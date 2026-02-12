"""
WebSocket Manager for Real-Time Alerts.

Provides WebSocket connections for real-time risk alerts and notifications.
"""

import logging
import json
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of real-time alerts."""
    RISK_CHANGE = "risk_change"
    TRANSACTION = "transaction"
    PORTFOLIO = "portfolio"
    SYSTEM = "system"
    VAULT = "vault"


@dataclass
class Alert:
    """Represents a real-time alert."""
    alert_id: str
    alert_type: AlertType
    address: str
    risk_score: int
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None


class ConnectionManager:
    """
    Manages WebSocket connections for real-time alerts.
    
    Supports:
    - Multiple concurrent connections
    - Address-based subscriptions
    - Alert broadcasting
    - Connection health monitoring
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Address subscriptions: address -> set of connection IDs
        self.address_subscriptions: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Alert history for replay
        self.alert_history: List[Alert] = []
        self.max_history = 100
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            connection_id: Unique identifier for this connection
        """
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "subscriptions": set(),
            "last_ping": datetime.utcnow().isoformat()
        }
        logger.info(f"WebSocket connected: {connection_id}")
        
        # Send welcome message
        await self.send_personal_message(connection_id, {
            "type": "connected",
            "connection_id": connection_id,
            "message": "Connected to ChainGuardian real-time alerts",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, connection_id: str):
        """
        Handle WebSocket disconnection.
        
        Args:
            connection_id: The connection to remove
        """
        # Remove from active connections
        self.active_connections.pop(connection_id, None)
        
        # Remove from address subscriptions
        metadata = self.connection_metadata.get(connection_id, {})
        for address in metadata.get("subscriptions", set()):
            if address in self.address_subscriptions:
                self.address_subscriptions[address].discard(connection_id)
        
        # Remove metadata
        self.connection_metadata.pop(connection_id, None)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific connection.
        
        Args:
            connection_id: Target connection ID
            message: Message to send
        """
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(connection_id, message)
    
    async def broadcast_to_address(self, address: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connections subscribed to an address.
        
        Args:
            address: The address to broadcast to
            message: Message to send
        """
        connection_ids = self.address_subscriptions.get(address, set())
        for connection_id in list(connection_ids):
            await self.send_personal_message(connection_id, message)
    
    async def subscribe_to_address(self, connection_id: str, address: str):
        """
        Subscribe a connection to alerts for an address.
        
        Args:
            connection_id: The connection to subscribe
            address: The address to subscribe to
        """
        # Add to address subscriptions
        if address not in self.address_subscriptions:
            self.address_subscriptions[address] = set()
        self.address_subscriptions[address].add(connection_id)
        
        # Update connection metadata
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["subscriptions"].add(address)
        
        logger.info(f"Connection {connection_id} subscribed to {address}")
        
        # Confirm subscription
        await self.send_personal_message(connection_id, {
            "type": "subscribed",
            "address": address,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def unsubscribe_from_address(self, connection_id: str, address: str):
        """
        Unsubscribe a connection from an address.
        
        Args:
            connection_id: The connection to unsubscribe
            address: The address to unsubscribe from
        """
        if address in self.address_subscriptions:
            self.address_subscriptions[address].discard(connection_id)
        
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["subscriptions"].discard(address)
        
        await self.send_personal_message(connection_id, {
            "type": "unsubscribed",
            "address": address,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_alert(self, alert: Alert):
        """
        Send an alert to relevant subscribers.
        
        Args:
            alert: The alert to send
        """
        # Store in history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Broadcast to address subscribers
        message = {
            "type": "alert",
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type.value,
            "address": alert.address,
            "risk_score": alert.risk_score,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "details": alert.details
        }
        
        await self.broadcast_to_address(alert.address, message)
        
        # Also broadcast system alerts to all
        if alert.alert_type == AlertType.SYSTEM:
            await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    def get_subscription_count(self, address: str) -> int:
        """Get the number of subscriptions for an address."""
        return len(self.address_subscriptions.get(address, set()))
    
    async def ping_all(self):
        """Send ping to all connections to check health."""
        for connection_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(connection_id, {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception:
                # Connection is dead, remove it
                self.disconnect(connection_id)


# Global connection manager
manager = ConnectionManager()


async def websocket_handler(websocket: WebSocket, connection_id: str):
    """
    Handle WebSocket messages from a client.
    
    Args:
        websocket: The WebSocket connection
        connection_id: Unique identifier for this connection
    """
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive and process messages
            data = await websocket.receive_json()
            
            message_type = data.get("type", "unknown")
            
            if message_type == "subscribe":
                # Subscribe to address alerts
                address = data.get("address")
                if address:
                    await manager.subscribe_to_address(connection_id, address)
            
            elif message_type == "unsubscribe":
                # Unsubscribe from address alerts
                address = data.get("address")
                if address:
                    await manager.unsubscribe_from_address(connection_id, address)
            
            elif message_type == "pong":
                # Update last ping time
                if connection_id in manager.connection_metadata:
                    manager.connection_metadata[connection_id]["last_ping"] = datetime.utcnow().isoformat()
            
            elif message_type == "get_history":
                # Send alert history
                address = data.get("address")
                history = [
                    {
                        "alert_id": a.alert_id,
                        "alert_type": a.alert_type.value,
                        "address": a.address,
                        "risk_score": a.risk_score,
                        "message": a.message,
                        "timestamp": a.timestamp
                    }
                    for a in manager.alert_history
                    if not address or a.address == address
                ]
                await manager.send_personal_message(connection_id, {
                    "type": "history",
                    "alerts": history[-20:],  # Last 20 alerts
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "get_status":
                # Send connection status
                await manager.send_personal_message(connection_id, {
                    "type": "status",
                    "connection_id": connection_id,
                    "subscriptions": list(
                        manager.connection_metadata.get(connection_id, {}).get("subscriptions", set())
                    ),
                    "connected_at": manager.connection_metadata.get(connection_id, {}).get("connected_at"),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            else:
                # Unknown message type
                await manager.send_personal_message(connection_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)


async def broadcast_risk_alert(
    address: str,
    risk_score: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Broadcast a risk alert to subscribers.
    
    Args:
        address: The affected address
        risk_score: The risk score
        message: Alert message
        details: Additional details
    """
    import uuid
    
    alert = Alert(
        alert_id=str(uuid.uuid4()),
        alert_type=AlertType.RISK_CHANGE,
        address=address,
        risk_score=risk_score,
        message=message,
        timestamp=datetime.utcnow().isoformat(),
        details=details
    )
    
    await manager.send_alert(alert)


async def broadcast_transaction_alert(
    address: str,
    tx_type: str,
    risk_score: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Broadcast a transaction alert to subscribers.
    
    Args:
        address: The affected address
        tx_type: Transaction type
        risk_score: The risk score
        message: Alert message
        details: Additional details
    """
    import uuid
    
    alert = Alert(
        alert_id=str(uuid.uuid4()),
        alert_type=AlertType.TRANSACTION,
        address=address,
        risk_score=risk_score,
        message=message,
        timestamp=datetime.utcnow().isoformat(),
        details={"tx_type": tx_type, **(details or {})}
    )
    
    await manager.send_alert(alert)


async def broadcast_system_alert(
    message: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Broadcast a system-wide alert to all connections.
    
    Args:
        message: Alert message
        details: Additional details
    """
    import uuid
    
    alert = Alert(
        alert_id=str(uuid.uuid4()),
        alert_type=AlertType.SYSTEM,
        address="system",
        risk_score=0,
        message=message,
        timestamp=datetime.utcnow().isoformat(),
        details=details
    )
    
    await manager.send_alert(alert)
