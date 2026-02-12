"""
Transaction Simulator Service for Algorand.

Simulates transactions before execution to preview state changes,
estimate fees, and identify potential issues.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from algosdk.v2client.algod import AlgodClient
from algosdk import transaction, encoding

from app.config import settings

logger = logging.getLogger(__name__)


class SimulationStatus(str, Enum):
    """Status of a simulation."""
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"


@dataclass
class SimulationWarning:
    """Warning from a simulation."""
    type: str
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class StateChange:
    """Represents a state change from a transaction."""
    key: str
    old_value: Optional[str]
    new_value: str
    type: str  # "global", "local", "box"


@dataclass
class SimulationResult:
    """Result of a transaction simulation."""
    success: bool
    status: SimulationStatus
    estimated_fee: int
    estimated_rounds: int
    warnings: List[SimulationWarning]
    state_changes: List[StateChange]
    logs: List[str]
    error_message: Optional[str] = None
    budget_used: int = 0
    budget_remaining: int = 0


class TransactionSimulator:
    """
    Transaction simulator for Algorand.
    
    Simulates transactions to preview effects without actually
    executing them on the blockchain.
    """
    
    # Minimum balance requirements (in microALGOs)
    MIN_BALANCE_PER_ASSET = 100_000
    MIN_BALANCE_PER_APP = 100_000
    MIN_BALANCE_PER_BOX_BYTE = 400
    MIN_BALANCE_BASE = 1_000_000
    
    def __init__(self) -> None:
        """Initialize the transaction simulator."""
        self.algod_client = self._get_algod_client()
    
    def _get_algod_client(self) -> AlgodClient:
        """Get the Algorand algod client."""
        from algosdk.v2client.algod import AlgodClient as SDKAlgodClient
        node_url = settings.ALGORAND_NODE_URL or "https://testnet-api.algonode.cloud"
        return SDKAlgodClient(algod_address=node_url, algod_token="")
    
    async def simulate_payment(
        self,
        sender: str,
        receiver: str,
        amount: int,
        close_remainder_to: Optional[str] = None
    ) -> SimulationResult:
        """
        Simulate a payment transaction.
        
        Args:
            sender: Sender address
            receiver: Receiver address
            amount: Amount in microALGOs
            close_remainder_to: Optional address to close remainder to
        
        Returns:
            SimulationResult with simulation details
        """
        warnings = []
        state_changes = []
        logs = []
        
        try:
            # Get suggested params
            params = self.algod_client.suggested_params()
            
            # Create payment transaction
            txn = transaction.PaymentTxn(
                sender=sender,
                sp=params,
                receiver=receiver,
                amt=amount,
                close_remainder_to=close_remainder_to
            )
            
            # Simulate the transaction
            sim_response = self.algod_client.simulate_rawtxn(
                encoding.msgpack_encode(txn)
            )
            
            # Parse simulation response
            sim_result = sim_response.get("txn-groups", [{}])[0]
            success = not sim_result.get("failed-pc", False)
            
            # Check for warnings
            sender_info = self.algod_client.account_info(sender)
            sender_balance = sender_info.get("amount", 0)
            
            if sender_balance < amount + self.MIN_BALANCE_BASE:
                warnings.append(SimulationWarning(
                    type="insufficient_balance",
                    message="Sender may have insufficient balance after transaction",
                    details={
                        "current_balance": sender_balance,
                        "transaction_amount": amount,
                        "min_required": amount + self.MIN_BALANCE_BASE
                    }
                ))
            
            # Track state changes
            state_changes.append(StateChange(
                key="balance",
                old_value=str(sender_balance),
                new_value=str(sender_balance - amount - txn.fee),
                type="local"
            ))
            
            # Get logs from simulation
            if "txn-results" in sim_result:
                for result in sim_result["txn-results"]:
                    if "logs" in result:
                        logs.extend(result["logs"])
            
            return SimulationResult(
                success=success,
                status=SimulationStatus.SUCCESS if success else SimulationStatus.FAILURE,
                estimated_fee=txn.fee,
                estimated_rounds=params.lastRound + 1,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                budget_used=0,
                budget_remaining=700  # Default opcode budget
            )
            
        except Exception as e:
            logger.error(f"Payment simulation failed: {e}")
            return SimulationResult(
                success=False,
                status=SimulationStatus.FAILURE,
                estimated_fee=1000,
                estimated_rounds=0,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                error_message=str(e)
            )
    
    async def simulate_app_call(
        self,
        sender: str,
        app_id: int,
        app_args: Optional[List[bytes]] = None,
        accounts: Optional[List[str]] = None,
        foreign_apps: Optional[List[int]] = None,
        foreign_assets: Optional[List[int]] = None,
        boxes: Optional[List[tuple]] = None
    ) -> SimulationResult:
        """
        Simulate an application call transaction.
        
        Args:
            sender: Sender address
            app_id: Application ID to call
            app_args: Application arguments
            accounts: Foreign accounts
            foreign_apps: Foreign app IDs
            foreign_assets: Foreign asset IDs
            boxes: Box references
        
        Returns:
            SimulationResult with simulation details
        """
        warnings = []
        state_changes = []
        logs = []
        
        try:
            # Get suggested params
            params = self.algod_client.suggested_params()
            
            # Create application call transaction
            txn = transaction.ApplicationCallTxn(
                sender=sender,
                sp=params,
                index=app_id,
                app_args=app_args,
                accounts=accounts,
                foreign_apps=foreign_apps,
                foreign_assets=foreign_assets,
                boxes=boxes,
                on_complete=transaction.OnComplete.NoOpOC
            )
            
            # Simulate the transaction
            sim_response = self.algod_client.simulate_rawtxn(
                encoding.msgpack_encode(txn)
            )
            
            # Parse simulation response
            sim_result = sim_response.get("txn-groups", [{}])[0]
            success = not sim_result.get("failed-pc", False)
            
            # Get budget information
            budget_used = sim_result.get("budget-consumed", 0)
            budget_remaining = 700 - budget_used  # Default budget is 700
            
            # Check for budget warnings
            if budget_remaining < 100:
                warnings.append(SimulationWarning(
                    type="low_opcode_budget",
                    message="Low opcode budget remaining",
                    details={
                        "budget_used": budget_used,
                        "budget_remaining": budget_remaining
                    }
                ))
            
            # Parse logs
            if "txn-results" in sim_result:
                for result in sim_result["txn-results"]:
                    if "logs" in result:
                        for log in result["logs"]:
                            try:
                                logs.append(log.decode('utf-8', errors='replace'))
                            except:
                                logs.append(str(log))
            
            # Check app state changes
            try:
                app_info = self.algod_client.application_info(app_id)
                if "params" in app_info:
                    params_data = app_info["params"]
                    if "global-state" in params_data:
                        for state in params_data["global-state"]:
                            state_changes.append(StateChange(
                                key=state.get("key", ""),
                                old_value=state.get("value", {}).get("bytes", ""),
                                new_value="[potentially modified]",
                                type="global"
                            ))
            except Exception as e:
                logger.debug(f"Could not fetch app state: {e}")
            
            return SimulationResult(
                success=success,
                status=SimulationStatus.SUCCESS if success else SimulationStatus.FAILURE,
                estimated_fee=txn.fee,
                estimated_rounds=params.lastRound + 1,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                error_message=None if success else sim_result.get("fail-message", "Unknown error"),
                budget_used=budget_used,
                budget_remaining=budget_remaining
            )
            
        except Exception as e:
            logger.error(f"App call simulation failed: {e}")
            return SimulationResult(
                success=False,
                status=SimulationStatus.FAILURE,
                estimated_fee=1000,
                estimated_rounds=0,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                error_message=str(e)
            )
    
    async def simulate_asset_transfer(
        self,
        sender: str,
        receiver: str,
        asset_id: int,
        amount: int,
        close_remainder_to: Optional[str] = None
    ) -> SimulationResult:
        """
        Simulate an asset transfer transaction.
        
        Args:
            sender: Sender address
            receiver: Receiver address
            asset_id: Asset ID to transfer
            amount: Amount in asset units
            close_remainder_to: Optional address to close remainder to
        
        Returns:
            SimulationResult with simulation details
        """
        warnings = []
        state_changes = []
        logs = []
        
        try:
            # Get suggested params
            params = self.algod_client.suggested_params()
            
            # Create asset transfer transaction
            txn = transaction.AssetTransferTxn(
                sender=sender,
                sp=params,
                receiver=receiver,
                amt=amount,
                index=asset_id,
                close_assets_to=close_remainder_to
            )
            
            # Simulate the transaction
            sim_response = self.algod_client.simulate_rawtxn(
                encoding.msgpack_encode(txn)
            )
            
            # Parse simulation response
            sim_result = sim_response.get("txn-groups", [{}])[0]
            success = not sim_result.get("failed-pc", False)
            
            # Check if receiver is opted in
            try:
                receiver_info = self.algod_client.account_info(receiver)
                assets = receiver_info.get("assets", [])
                opted_in = any(a.get("asset-id") == asset_id for a in assets)
                
                if not opted_in:
                    warnings.append(SimulationWarning(
                        type="receiver_not_opted_in",
                        message="Receiver is not opted in to this asset",
                        details={
                            "asset_id": asset_id,
                            "receiver": receiver
                        }
                    ))
            except Exception:
                pass
            
            # Check sender balance
            try:
                sender_info = self.algod_client.account_info(sender)
                sender_assets = sender_info.get("assets", [])
                sender_asset = next(
                    (a for a in sender_assets if a.get("asset-id") == asset_id),
                    None
                )
                
                if sender_asset is None:
                    warnings.append(SimulationWarning(
                        type="sender_not_opted_in",
                        message="Sender is not opted in to this asset",
                        details={"asset_id": asset_id}
                    ))
                elif sender_asset.get("amount", 0) < amount:
                    warnings.append(SimulationWarning(
                        type="insufficient_asset_balance",
                        message="Sender has insufficient asset balance",
                        details={
                            "current_balance": sender_asset.get("amount", 0),
                            "transfer_amount": amount
                        }
                    ))
            except Exception:
                pass
            
            return SimulationResult(
                success=success,
                status=SimulationStatus.SUCCESS if success else SimulationStatus.FAILURE,
                estimated_fee=txn.fee,
                estimated_rounds=params.lastRound + 1,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                budget_used=0,
                budget_remaining=700
            )
            
        except Exception as e:
            logger.error(f"Asset transfer simulation failed: {e}")
            return SimulationResult(
                success=False,
                status=SimulationStatus.FAILURE,
                estimated_fee=1000,
                estimated_rounds=0,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                error_message=str(e)
            )
    
    async def simulate_group(
        self,
        transactions: List[Dict[str, Any]]
    ) -> SimulationResult:
        """
        Simulate a group of transactions.
        
        Args:
            transactions: List of transaction specifications
        
        Returns:
            SimulationResult for the group
        """
        warnings = []
        state_changes = []
        logs = []
        total_fee = 0
        
        try:
            # Build transaction group
            txn_group = []
            params = self.algod_client.suggested_params()
            
            for tx_spec in transactions:
                tx_type = tx_spec.get("type", "payment")
                
                if tx_type == "payment":
                    txn = transaction.PaymentTxn(
                        sender=tx_spec["sender"],
                        sp=params,
                        receiver=tx_spec["receiver"],
                        amt=tx_spec.get("amount", 0)
                    )
                elif tx_type == "app_call":
                    txn = transaction.ApplicationCallTxn(
                        sender=tx_spec["sender"],
                        sp=params,
                        index=tx_spec["app_id"],
                        app_args=tx_spec.get("app_args"),
                        on_complete=transaction.OnComplete.NoOpOC
                    )
                elif tx_type == "asset_transfer":
                    txn = transaction.AssetTransferTxn(
                        sender=tx_spec["sender"],
                        sp=params,
                        receiver=tx_spec["receiver"],
                        amt=tx_spec.get("amount", 0),
                        index=tx_spec["asset_id"]
                    )
                else:
                    continue
                
                txn_group.append(txn)
                total_fee += txn.fee
            
            # Assign group ID
            if len(txn_group) > 1:
                gid = transaction.calculate_group_id(txn_group)
                for txn in txn_group:
                    txn.group = gid
            
            # Encode and simulate
            encoded = [encoding.msgpack_encode(txn) for txn in txn_group]
            sim_response = self.algod_client.simulate_rawtxn(encoded)
            
            # Parse results
            sim_result = sim_response.get("txn-groups", [{}])[0]
            success = not sim_result.get("failed-pc", False)
            
            # Add group-specific warnings
            if len(txn_group) > 16:
                warnings.append(SimulationWarning(
                    type="large_group",
                    message="Transaction group exceeds recommended size",
                    details={"group_size": len(txn_group)}
                ))
            
            return SimulationResult(
                success=success,
                status=SimulationStatus.SUCCESS if success else SimulationStatus.FAILURE,
                estimated_fee=total_fee,
                estimated_rounds=params.lastRound + 1,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                error_message=None if success else sim_result.get("fail-message", "Unknown error"),
                budget_used=0,
                budget_remaining=700
            )
            
        except Exception as e:
            logger.error(f"Group simulation failed: {e}")
            return SimulationResult(
                success=False,
                status=SimulationStatus.FAILURE,
                estimated_fee=total_fee,
                estimated_rounds=0,
                warnings=warnings,
                state_changes=state_changes,
                logs=logs,
                error_message=str(e)
            )
    
    async def estimate_fees(
        self,
        transaction_type: str,
        priority: str = "normal"
    ) -> Dict[str, int]:
        """
        Estimate transaction fees.
        
        Args:
            transaction_type: Type of transaction
            priority: Fee priority (low, normal, high)
        
        Returns:
            Dictionary with fee estimates
        """
        try:
            params = self.algod_client.suggested_params()
            base_fee = params.min_fee  # Use min_fee (snake_case) for newer algosdk
            
            # Priority multipliers
            multipliers = {
                "low": 1.0,
                "normal": 1.5,
                "high": 3.0
            }
            
            multiplier = multipliers.get(priority, 1.5)
            
            # Additional fees for complex transactions
            additional_fees = {
                "payment": 0,
                "app_call": 1000,  # Apps typically need more fees
                "asset_transfer": 0,
                "asset_creation": 1000,
                "app_creation": 1000
            }
            
            estimated = int((base_fee + additional_fees.get(transaction_type, 0)) * multiplier)
            
            return {
                "base_fee": base_fee,
                "estimated_fee": estimated,
                "priority": priority,
                "transaction_type": transaction_type
            }
            
        except Exception as e:
            logger.error(f"Fee estimation failed: {e}")
            return {
                "base_fee": 1000,
                "estimated_fee": 1000,
                "priority": priority,
                "transaction_type": transaction_type,
                "error": str(e)
            }


# Singleton instance
_transaction_simulator: Optional[TransactionSimulator] = None


def get_transaction_simulator() -> TransactionSimulator:
    """Get or create the transaction simulator singleton instance."""
    global _transaction_simulator
    if _transaction_simulator is None:
        _transaction_simulator = TransactionSimulator()
    return _transaction_simulator
