"""
Transaction Simulation API Routes.

Endpoints for simulating transactions before execution.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.models.schemas import (
    SimulationRequest,
    SimulationResult as SimulationResultSchema,
)
from app.services.transaction_simulator import get_transaction_simulator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulate", tags=["Transaction Simulation"])


@router.post("/payment", response_model=SimulationResultSchema)
async def simulate_payment(
    sender: str,
    receiver: str,
    amount: int = Query(..., description="Amount in microALGOs"),
    close_remainder_to: Optional[str] = None
):
    """
    Simulate a payment transaction.
    
    - **sender**: Sender address
    - **receiver**: Receiver address
    - **amount**: Amount in microALGOs
    - **close_remainder_to**: Optional address to close remainder to
    """
    try:
        simulator = get_transaction_simulator()
        result = await simulator.simulate_payment(
            sender=sender,
            receiver=receiver,
            amount=amount,
            close_remainder_to=close_remainder_to
        )
        
        return SimulationResultSchema(
            success=result.success,
            estimated_fee=result.estimated_fee,
            estimated_rounds=result.estimated_rounds,
            warnings=[w.message for w in result.warnings],
            state_changes=[
                {
                    "key": s.key,
                    "old_value": s.old_value,
                    "new_value": s.new_value,
                    "type": s.type
                }
                for s in result.state_changes
            ],
            logs=result.logs
        )
        
    except Exception as e:
        logger.error(f"Payment simulation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@router.post("/app-call", response_model=SimulationResultSchema)
async def simulate_app_call(
    sender: str,
    app_id: int,
    app_args: Optional[List[str]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None
):
    """
    Simulate an application call transaction.
    
    - **sender**: Sender address
    - **app_id**: Application ID to call
    - **app_args**: Application arguments (base64 encoded strings)
    - **accounts**: Foreign accounts
    - **foreign_apps**: Foreign app IDs
    - **foreign_assets**: Foreign asset IDs
    """
    try:
        simulator = get_transaction_simulator()
        
        # Convert app_args to bytes
        args_bytes = None
        if app_args:
            import base64
            args_bytes = [base64.b64decode(arg) for arg in app_args]
        
        result = await simulator.simulate_app_call(
            sender=sender,
            app_id=app_id,
            app_args=args_bytes,
            accounts=accounts,
            foreign_apps=foreign_apps,
            foreign_assets=foreign_assets
        )
        
        return SimulationResultSchema(
            success=result.success,
            estimated_fee=result.estimated_fee,
            estimated_rounds=result.estimated_rounds,
            warnings=[w.message for w in result.warnings],
            state_changes=[
                {
                    "key": s.key,
                    "old_value": s.old_value,
                    "new_value": s.new_value,
                    "type": s.type
                }
                for s in result.state_changes
            ],
            logs=result.logs
        )
        
    except Exception as e:
        logger.error(f"App call simulation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@router.post("/asset-transfer", response_model=SimulationResultSchema)
async def simulate_asset_transfer(
    sender: str,
    receiver: str,
    asset_id: int,
    amount: int = Query(..., description="Amount in asset units"),
    close_remainder_to: Optional[str] = None
):
    """
    Simulate an asset transfer transaction.
    
    - **sender**: Sender address
    - **receiver**: Receiver address
    - **asset_id**: Asset ID to transfer
    - **amount**: Amount in asset units
    - **close_remainder_to**: Optional address to close remainder to
    """
    try:
        simulator = get_transaction_simulator()
        result = await simulator.simulate_asset_transfer(
            sender=sender,
            receiver=receiver,
            asset_id=asset_id,
            amount=amount,
            close_remainder_to=close_remainder_to
        )
        
        return SimulationResultSchema(
            success=result.success,
            estimated_fee=result.estimated_fee,
            estimated_rounds=result.estimated_rounds,
            warnings=[w.message for w in result.warnings],
            state_changes=[
                {
                    "key": s.key,
                    "old_value": s.old_value,
                    "new_value": s.new_value,
                    "type": s.type
                }
                for s in result.state_changes
            ],
            logs=result.logs
        )
        
    except Exception as e:
        logger.error(f"Asset transfer simulation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@router.post("/group")
async def simulate_transaction_group(transactions: List[dict]):
    """
    Simulate a group of transactions.
    
    - **transactions**: List of transaction specifications
      - type: Transaction type (payment, app_call, asset_transfer)
      - sender: Sender address
      - receiver: Receiver address (for payment/asset_transfer)
      - amount: Amount (for payment/asset_transfer)
      - app_id: Application ID (for app_call)
      - asset_id: Asset ID (for asset_transfer)
    """
    if len(transactions) > 16:
        raise HTTPException(
            status_code=400,
            detail="Maximum 16 transactions per group"
        )
    
    try:
        simulator = get_transaction_simulator()
        result = await simulator.simulate_group(transactions)
        
        return {
            "success": result.success,
            "status": result.status.value,
            "estimated_fee": result.estimated_fee,
            "estimated_rounds": result.estimated_rounds,
            "warnings": [
                {
                    "type": w.type,
                    "message": w.message,
                    "details": w.details
                }
                for w in result.warnings
            ],
            "state_changes": [
                {
                    "key": s.key,
                    "old_value": s.old_value,
                    "new_value": s.new_value,
                    "type": s.type
                }
                for s in result.state_changes
            ],
            "logs": result.logs,
            "error_message": result.error_message
        }
        
    except Exception as e:
        logger.error(f"Group simulation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@router.get("/fees")
async def estimate_fees(
    transaction_type: str = Query(
        default="payment",
        description="Type of transaction"
    ),
    priority: str = Query(
        default="normal",
        description="Fee priority (low, normal, high)"
    )
):
    """
    Estimate transaction fees.
    
    - **transaction_type**: Type of transaction (payment, app_call, asset_transfer)
    - **priority**: Fee priority (low, normal, high)
    """
    try:
        simulator = get_transaction_simulator()
        result = await simulator.estimate_fees(transaction_type, priority)
        return result
        
    except Exception as e:
        logger.error(f"Fee estimation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Fee estimation failed: {str(e)}"
        )


@router.get("/dry-run/{address}")
async def dry_run_account_transactions(address: str):
    """
    Perform a dry-run analysis of pending transactions for an account.
    
    - **address**: The Algorand address to analyze
    """
    try:
        from algosdk.v2client.algod import AlgodClient as SDKAlgodClient
        
        node_url = settings.ALGORAND_NODE_URL or "https://testnet-api.algonode.cloud"
        algod = SDKAlgodClient(algod_address=node_url, algod_token="")
        
        account_info = algod.account_info(address)
        
        return {
            "address": address,
            "balance": account_info.get("amount", 0),
            "min_balance": account_info.get("min-balance", 0),
            "pending_transactions": account_info.get("pending-rewards", 0),
            "assets_count": len(account_info.get("assets", [])),
            "apps_count": len(account_info.get("apps-local-state", [])),
            "status": "ready",
            "recommendations": [
                "Ensure sufficient balance for transaction fees",
                "Check asset opt-ins before transfers",
                "Verify app state before calling"
            ]
        }
        
    except Exception as e:
        logger.error(f"Dry-run analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Dry-run analysis failed: {str(e)}"
        )
