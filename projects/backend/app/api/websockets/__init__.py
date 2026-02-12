"""
WebSocket module for real-time alerts.
"""

from app.api.websockets.alerts import (
    manager,
    websocket_handler,
    broadcast_risk_alert,
    broadcast_transaction_alert,
    broadcast_system_alert,
    AlertType,
    Alert,
)

__all__ = [
    "manager",
    "websocket_handler",
    "broadcast_risk_alert",
    "broadcast_transaction_alert",
    "broadcast_system_alert",
    "AlertType",
    "Alert",
]
