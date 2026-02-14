"""
Enhanced Blockchain API Routes.
Provides endpoints for block creation, transactions, and multi-network support.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.enhanced_blockchain_service import get_enhanced_blockchain_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blockchain", tags=["blockchain"])


# ==================== Request Models ====================

class CreateTransactionRequest(BaseModel):
    """Request model for creating a transaction."""
    sender: str = Field(..., description="Sender address")
    recipient: str = Field(..., description="Recipient address")
    amount: float = Field(..., gt=0, description="Transaction amount")
    type: str = Field(default="transfer", description="Transaction type")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CreateBlockRequest(BaseModel):
    """Request model for creating a block."""
    transactions: List[CreateTransactionRequest] = Field(..., description="List of transactions")
    miner_address: str = Field(default="network", description="Miner address for reward")


class SendLoraAlertRequest(BaseModel):
    """Request model for sending LoRa alert."""
    device_id: str = Field(..., description="LoRa device ID")
    alert_type: str = Field(..., description="Type of alert")
    message: str = Field(..., description="Alert message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional alert data")


# ==================== Local Blockchain Endpoints ====================

@router.get("/status")
async def get_blockchain_status() -> Dict[str, Any]:
    """Get the current status of the local blockchain."""
    service = get_enhanced_blockchain_service()
    return await service.get_blockchain_status()


@router.get("/blocks")
async def get_all_blocks() -> List[Dict[str, Any]]:
    """Get all blocks in the chain."""
    service = get_enhanced_blockchain_service()
    return await service.get_all_blocks()


@router.get("/blocks/{block_index}")
async def get_block(block_index: int) -> Dict[str, Any]:
    """Get a specific block by index."""
    service = get_enhanced_blockchain_service()
    block = await service.get_block_by_index(block_index)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


@router.post("/blocks/create")
async def create_block(request: CreateBlockRequest) -> Dict[str, Any]:
    """Create a new block with transactions."""
    service = get_enhanced_blockchain_service()
    
    transactions = [tx.model_dump() for tx in request.transactions]
    
    result = await service.create_block(transactions, request.miner_address)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail="Failed to create block")
    
    return result


@router.post("/transactions")
async def add_transaction(request: CreateTransactionRequest) -> Dict[str, Any]:
    """Add a transaction to the pending pool."""
    service = get_enhanced_blockchain_service()
    
    result = await service.add_transaction(
        sender=request.sender,
        recipient=request.recipient,
        amount=request.amount,
        tx_type=request.type,
        metadata=request.metadata
    )
    
    return result


@router.get("/transactions/pending")
async def get_pending_transactions() -> List[Dict[str, Any]]:
    """Get all pending transactions."""
    service = get_enhanced_blockchain_service()
    return await service.get_pending_transactions()


@router.get("/transactions/address/{address}")
async def get_address_transactions(address: str) -> List[Dict[str, Any]]:
    """Get all transactions for an address."""
    service = get_enhanced_blockchain_service()
    return await service.get_address_transactions(address)


@router.get("/balance/{address}")
async def get_address_balance(address: str) -> Dict[str, Any]:
    """Get balance for an address."""
    service = get_enhanced_blockchain_service()
    return await service.get_address_balance(address)


# ==================== LoRa Network Endpoints ====================

@router.get("/lora/status")
async def get_lora_status() -> Dict[str, Any]:
    """Check LoRa network status."""
    service = get_enhanced_blockchain_service()
    return await service.check_lora_network()


@router.get("/lora/devices/{device_id}")
async def get_lora_device(device_id: str) -> Dict[str, Any]:
    """Get LoRa device data."""
    service = get_enhanced_blockchain_service()
    return await service.get_lora_device(device_id)


@router.post("/lora/alerts")
async def send_lora_alert(request: SendLoraAlertRequest) -> Dict[str, Any]:
    """Send alert to LoRa device."""
    service = get_enhanced_blockchain_service()
    
    alert_data = {
        "alert_type": request.alert_type,
        "message": request.message,
        "data": request.data
    }
    
    return await service.send_lora_alert(request.device_id, alert_data)


# ==================== Algorand Network Endpoints ====================

@router.get("/algorand/status")
async def get_algorand_status() -> Dict[str, Any]:
    """Get Algorand network status."""
    service = get_enhanced_blockchain_service()
    return await service.get_algorand_status()


@router.get("/algorand/accounts/{address}")
async def get_algorand_account(address: str) -> Dict[str, Any]:
    """Get Algorand account information."""
    service = get_enhanced_blockchain_service()
    return await service.get_algorand_account(address)


@router.get("/algorand/transactions/{address}")
async def get_algorand_transactions(
    address: str,
    limit: int = Query(default=10, ge=1, le=100)
) -> Dict[str, Any]:
    """Get transactions for an Algorand address."""
    service = get_enhanced_blockchain_service()
    return await service.get_algorand_transactions(address, limit)


# ==================== Multi-Network Endpoints ====================

@router.get("/networks/status")
async def get_all_networks_status() -> Dict[str, Any]:
    """Get status of all supported networks."""
    service = get_enhanced_blockchain_service()
    return await service.get_all_networks_status()
