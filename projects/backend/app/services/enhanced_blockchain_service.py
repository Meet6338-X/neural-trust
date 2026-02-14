"""
Enhanced Blockchain Service with Block Creation and Multi-Network Support.
Supports Algorand, LoRa networks, and custom block creation.
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class Block:
    """Represents a single block in the blockchain."""
    
    def __init__(
        self,
        index: int,
        transactions: List[Dict[str, Any]],
        timestamp: float,
        previous_hash: str,
        nonce: int = 0
    ):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the hash of this block."""
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4) -> None:
        """Mine the block with proof of work."""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class Blockchain:
    """Simple blockchain implementation for transaction tracking."""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = 4
        self.mining_reward = 10
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block in the chain."""
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0"
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block."""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict[str, Any]) -> int:
        """Add a transaction to pending transactions."""
        transaction["timestamp"] = time.time()
        transaction["id"] = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()[:16]
        self.pending_transactions.append(transaction)
        return len(self.pending_transactions)
    
    def mine_pending_transactions(self, miner_address: str) -> Block:
        """Mine pending transactions into a new block."""
        # Add mining reward
        reward_transaction = {
            "type": "mining_reward",
            "miner": miner_address,
            "amount": self.mining_reward,
            "timestamp": time.time()
        }
        
        transactions = self.pending_transactions + [reward_transaction]
        
        new_block = Block(
            index=len(self.chain),
            transactions=transactions,
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block
    
    def get_balance(self, address: str) -> float:
        """Calculate balance for an address."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("sender") == address:
                    balance -= tx.get("amount", 0)
                if tx.get("recipient") == address:
                    balance += tx.get("amount", 0)
        return balance
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_transaction_history(self, address: str) -> List[Dict[str, Any]]:
        """Get all transactions for an address."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("sender") == address or tx.get("recipient") == address:
                    transactions.append({
                        **tx,
                        "block_index": block.index,
                        "block_hash": block.hash
                    })
        return transactions


class LoRaNetworkService:
    """Service for interacting with LoRa networks."""
    
    def __init__(self):
        self.enabled = settings.LORA_ENABLED
        self.api_url = settings.LORA_API_URL
        self.api_key = settings.LORA_API_KEY
    
    async def check_network_status(self) -> Dict[str, Any]:
        """Check LoRa network status."""
        if not self.enabled:
            return {"status": "disabled", "message": "LoRa network checking is disabled"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Simulated LoRa network check
                return {
                    "status": "online",
                    "networks": {
                        "the_things_network": {"status": "operational", "gateways": 15000},
                        "helium": {"status": "operational", "hotspots": 500000},
                        "chirpstack": {"status": "operational", "servers": 100}
                    },
                    "coverage": "global",
                    "last_checked": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"LoRa network check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_device_data(self, device_id: str) -> Dict[str, Any]:
        """Get data from a LoRa device."""
        if not self.enabled:
            return {"status": "disabled"}
        
        try:
            # Simulated device data
            return {
                "device_id": device_id,
                "status": "online",
                "last_seen": datetime.utcnow().isoformat(),
                "data": {
                    "temperature": 25.5,
                    "humidity": 60,
                    "battery": 85,
                    "signal_strength": -67
                }
            }
        except Exception as e:
            logger.error(f"Failed to get LoRa device data: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_transaction_alert(
        self,
        device_id: str,
        transaction_data: Dict[str, Any]
    ) -> bool:
        """Send transaction alert to LoRa device."""
        if not self.enabled:
            return False
        
        try:
            # Simulated alert sending
            logger.info(f"Sending alert to LoRa device {device_id}: {transaction_data}")
            return True
        except Exception as e:
            logger.error(f"Failed to send LoRa alert: {e}")
            return False


class EnhancedBlockchainService:
    """
    Enhanced blockchain service with multi-network support.
    Combines Algorand, local blockchain, and LoRa networks.
    """
    
    def __init__(self):
        self.local_blockchain = Blockchain()
        self.lora_service = LoRaNetworkService()
        self.algorand_node_url = settings.ALGORAND_NODE_URL or "https://testnet-api.algonode.cloud"
        self.indexer_url = settings.ALGORAND_INDEXER_URL or "https://testnet-idx.algonode.cloud"
    
    # ==================== Local Blockchain Operations ====================
    
    async def create_block(
        self,
        transactions: List[Dict[str, Any]],
        miner_address: str = "network"
    ) -> Dict[str, Any]:
        """Create a new block with the given transactions."""
        # Add transactions to pending
        for tx in transactions:
            self.local_blockchain.add_transaction(tx)
        
        # Mine the block
        block = self.local_blockchain.mine_pending_transactions(miner_address)
        
        logger.info(f"Created block {block.index} with {len(transactions)} transactions")
        
        return {
            "success": True,
            "block": block.to_dict(),
            "message": f"Block {block.index} created successfully"
        }
    
    async def get_blockchain_status(self) -> Dict[str, Any]:
        """Get the current status of the local blockchain."""
        return {
            "chain_length": len(self.local_blockchain.chain),
            "pending_transactions": len(self.local_blockchain.pending_transactions),
            "is_valid": self.local_blockchain.is_chain_valid(),
            "difficulty": self.local_blockchain.difficulty,
            "last_block": self.local_blockchain.get_latest_block().to_dict()
        }
    
    async def get_block_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a block by its index."""
        if 0 <= index < len(self.local_blockchain.chain):
            return self.local_blockchain.chain[index].to_dict()
        return None
    
    async def get_all_blocks(self) -> List[Dict[str, Any]]:
        """Get all blocks in the chain."""
        return [block.to_dict() for block in self.local_blockchain.chain]
    
    async def add_transaction(
        self,
        sender: str,
        recipient: str,
        amount: float,
        tx_type: str = "transfer",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a new transaction to pending transactions."""
        transaction = {
            "type": tx_type,
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "metadata": metadata or {}
        }
        
        tx_count = self.local_blockchain.add_transaction(transaction)
        
        return {
            "success": True,
            "transaction_id": transaction["id"],
            "pending_count": tx_count,
            "message": "Transaction added to pending pool"
        }
    
    async def get_pending_transactions(self) -> List[Dict[str, Any]]:
        """Get all pending transactions."""
        return self.local_blockchain.pending_transactions
    
    async def get_address_transactions(self, address: str) -> List[Dict[str, Any]]:
        """Get all transactions for an address."""
        return self.local_blockchain.get_transaction_history(address)
    
    async def get_address_balance(self, address: str) -> Dict[str, Any]:
        """Get balance for an address."""
        balance = self.local_blockchain.get_balance(address)
        return {
            "address": address,
            "balance": balance,
            "pending_transactions": len([
                tx for tx in self.local_blockchain.pending_transactions
                if tx.get("sender") == address or tx.get("recipient") == address
            ])
        }
    
    # ==================== LoRa Network Operations ====================
    
    async def check_lora_network(self) -> Dict[str, Any]:
        """Check LoRa network status."""
        return await self.lora_service.check_network_status()
    
    async def get_lora_device(self, device_id: str) -> Dict[str, Any]:
        """Get LoRa device data."""
        return await self.lora_service.get_device_data(device_id)
    
    async def send_lora_alert(
        self,
        device_id: str,
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send alert to LoRa device."""
        success = await self.lora_service.send_transaction_alert(device_id, alert_data)
        return {
            "success": success,
            "device_id": device_id,
            "message": "Alert sent successfully" if success else "Failed to send alert"
        }
    
    # ==================== Algorand Operations ====================
    
    async def get_algorand_status(self) -> Dict[str, Any]:
        """Get Algorand network status."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.algorand_node_url}/v2/status")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "online",
                        "network": settings.ALGORAND_NETWORK,
                        "last_round": data.get("last-round"),
                        "time_since_last_round": data.get("time-since-last-round"),
                        "catchup_time": data.get("catchup-time", 0)
                    }
                return {"status": "error", "message": "Failed to connect to Algorand"}
        except Exception as e:
            logger.error(f"Algorand status check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_algorand_account(self, address: str) -> Dict[str, Any]:
        """Get Algorand account information."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.algorand_node_url}/v2/accounts/{address}"
                )
                if response.status_code == 200:
                    data = response.json()
                    # The API returns account data directly, not wrapped in "account"
                    amount = data.get("amount", 0)
                    return {
                        "address": address,
                        "balance": amount / 1_000_000,  # Convert microAlgos to Algos
                        "balance_micro_algos": amount,
                        "min_balance": data.get("min-balance", 0),
                        "status": data.get("status", "unknown"),
                        "assets": data.get("assets", []),
                        "created_at_round": data.get("created-at-round"),
                        "rewards": data.get("rewards", 0),
                        "round": data.get("round"),
                        "amount_without_pending_rewards": data.get("amount-without-pending-rewards", 0)
                    }
                return {"error": "Account not found", "address": address}
        except Exception as e:
            logger.error(f"Failed to get Algorand account: {e}")
            return {"error": str(e), "address": address}
    
    async def get_algorand_transactions(
        self,
        address: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get transactions for an Algorand address."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.indexer_url}/v2/accounts/{address}/transactions",
                    params={"limit": limit}
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "address": address,
                        "transactions": data.get("transactions", []),
                        "next_token": data.get("next-token")
                    }
                return {"error": "Failed to fetch transactions", "address": address}
        except Exception as e:
            logger.error(f"Failed to get Algorand transactions: {e}")
            return {"error": str(e), "address": address}
    
    # ==================== Combined Operations ====================
    
    async def get_all_networks_status(self) -> Dict[str, Any]:
        """Get status of all supported networks."""
        algorand_status = await self.get_algorand_status()
        lora_status = await self.check_lora_network()
        local_status = await self.get_blockchain_status()
        
        return {
            "algorand": algorand_status,
            "lora": lora_status,
            "local_blockchain": local_status,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
_enhanced_blockchain_service: Optional[EnhancedBlockchainService] = None


def get_enhanced_blockchain_service() -> EnhancedBlockchainService:
    """Get or create the enhanced blockchain service singleton instance."""
    global _enhanced_blockchain_service
    if _enhanced_blockchain_service is None:
        _enhanced_blockchain_service = EnhancedBlockchainService()
    return _enhanced_blockchain_service
