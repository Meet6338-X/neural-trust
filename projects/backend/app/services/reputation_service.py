"""
Address Reputation Service for Algorand.

Calculates trust scores and risk assessments for Algorand addresses
based on transaction history, behavior patterns, and known risk factors.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from app.config import settings

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AddressReputation:
    """Reputation data for an Algorand address."""
    address: str
    trust_score: int  # 0-100
    risk_level: RiskLevel
    first_seen: Optional[str] = None
    last_active: Optional[str] = None
    total_transactions: int = 0
    total_volume_algo: float = 0.0
    total_assets: int = 0
    created_apps: int = 0
    opted_in_apps: int = 0
    flags: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    behavior_patterns: List[str] = field(default_factory=list)


class ReputationService:
    """
    Service for calculating and managing address reputation scores.
    
    Analyzes on-chain behavior to determine trust scores and identify
    potentially risky addresses.
    """
    
    # Known high-risk patterns
    RISK_PATTERNS = {
        "high_frequency_trading": {
            "threshold": 100,  # transactions per day
            "risk_weight": 10,
            "description": "High frequency trading pattern detected"
        },
        "large_single_transaction": {
            "threshold": 100000,  # ALGO
            "risk_weight": 15,
            "description": "Large single transaction detected"
        },
        "new_account": {
            "threshold": 7,  # days
            "risk_weight": 20,
            "description": "Recently created account"
        },
        "dust_transactions": {
            "threshold": 50,  # count of tiny transactions
            "risk_weight": 25,
            "description": "Multiple dust transactions (potential mixing)"
        },
        "failed_transactions": {
            "threshold": 10,  # failed transactions
            "risk_weight": 15,
            "description": "Multiple failed transactions"
        },
    }
    
    # Positive behavior patterns
    POSITIVE_PATTERNS = {
        "long_history": {
            "threshold": 365,  # days
            "trust_weight": 10,
            "description": "Long account history"
        },
        "consistent_activity": {
            "threshold": 30,  # days of activity
            "trust_weight": 5,
            "description": "Consistent account activity"
        },
        "app_creator": {
            "threshold": 1,  # apps created
            "trust_weight": 5,
            "description": "Smart contract developer"
        },
        "asset_creator": {
            "threshold": 1,  # assets created
            "trust_weight": 3,
            "description": "Asset creator"
        },
    }
    
    # Known blacklist (would typically come from external source)
    BLACKLIST: List[str] = []
    
    # Known whitelist (verified addresses)
    WHITELIST: Dict[str, List[str]] = {
        "verified_projects": [],
        "exchanges": [],
        "known_good": []
    }
    
    def __init__(self) -> None:
        """Initialize the reputation service."""
        self.algod_client = self._get_algod_client()
        self.indexer_client = self._get_indexer_client()
    
    def _get_algod_client(self) -> AlgodClient:
        """Get the Algorand algod client."""
        from algosdk.v2client.algod import AlgodClient as SDKAlgodClient
        node_url = settings.ALGORAND_NODE_URL or "https://testnet-api.algonode.cloud"
        return SDKAlgodClient(algod_address=node_url, algod_token="")
    
    def _get_indexer_client(self) -> IndexerClient:
        """Get the Algorand indexer client."""
        from algosdk.v2client.indexer import IndexerClient as SDKIndexerClient
        indexer_url = settings.ALGORAND_INDEXER_URL or "https://testnet-idx.algonode.cloud"
        return SDKIndexerClient(indexer_address=indexer_url, indexer_token="")
    
    async def get_reputation(self, address: str) -> AddressReputation:
        """
        Calculate reputation score for an Algorand address.
        
        Args:
            address: The Algorand address to analyze
        
        Returns:
            AddressReputation with trust score and risk assessment
        """
        import time
        start_time = time.time()
        
        # Initialize reputation object
        reputation = AddressReputation(
            address=address,
            trust_score=50,  # Start neutral
            risk_level=RiskLevel.MEDIUM
        )
        
        try:
            # Get account information
            account_info = await self._get_account_info(address)
            if account_info is None:
                reputation.flags.append("account_not_found")
                reputation.trust_score = 0
                reputation.risk_level = RiskLevel.CRITICAL
                return reputation
            
            # Get transaction history
            tx_history = await self._get_transaction_history(address)
            
            # Calculate metrics
            reputation.total_transactions = len(tx_history)
            reputation.total_volume_algo = self._calculate_volume(tx_history)
            reputation.total_assets = len(account_info.get("assets", []))
            reputation.created_apps = account_info.get("created-apps", 0) if isinstance(account_info.get("created-apps"), int) else len(account_info.get("created-apps", []))
            reputation.opted_in_apps = len(account_info.get("apps-local-state", []))
            
            # Calculate first seen and last active
            if tx_history:
                reputation.first_seen = tx_history[0].get("round-time")
                reputation.last_active = tx_history[-1].get("round-time")
            
            # Check blacklist/whitelist
            if address in self.BLACKLIST:
                reputation.flags.append("blacklisted")
                reputation.trust_score = 0
                reputation.risk_level = RiskLevel.CRITICAL
                return reputation
            
            for category, addresses in self.WHITELIST.items():
                if address in addresses:
                    reputation.labels.append(category)
                    reputation.trust_score = min(100, reputation.trust_score + 30)
            
            # Analyze risk patterns
            risk_score = self._analyze_risk_patterns(
                account_info, tx_history, reputation
            )
            
            # Analyze positive patterns
            trust_bonus = self._analyze_positive_patterns(
                account_info, tx_history, reputation
            )
            
            # Calculate final score
            reputation.trust_score = max(0, min(100, 
                50 - risk_score + trust_bonus
            ))
            
            # Determine risk level
            reputation.risk_level = self._calculate_risk_level(reputation.trust_score)
            
            # Add behavior patterns
            reputation.behavior_patterns = self._identify_behavior_patterns(
                tx_history, account_info
            )
            
        except Exception as e:
            logger.error(f"Error calculating reputation for {address}: {e}")
            reputation.flags.append("analysis_error")
            reputation.risk_factors.append(str(e)[:100])
        
        return reputation
    
    async def _get_account_info(self, address: str) -> Optional[Dict[str, Any]]:
        """Get account information from the blockchain."""
        try:
            # Use synchronous client in async context
            import asyncio
            loop = asyncio.get_event_loop()
            account_info = await loop.run_in_executor(
                None,
                self.algod_client.account_info,
                address
            )
            return account_info
        except Exception as e:
            logger.error(f"Failed to get account info for {address}: {e}")
            return None
    
    async def _get_transaction_history(
        self,
        address: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get transaction history for an address."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Search transactions for this address
            response = await loop.run_in_executor(
                None,
                lambda: self.indexer_client.search_transactions(
                    address=address,
                    limit=limit
                )
            )
            
            return response.get("transactions", [])
        except Exception as e:
            logger.error(f"Failed to get transaction history for {address}: {e}")
            return []
    
    def _calculate_volume(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate total transaction volume in ALGO."""
        total = 0.0
        for tx in transactions:
            if "payment-transaction" in tx:
                amount = tx["payment-transaction"].get("amount", 0)
                total += amount / 1_000_000  # Convert microALGO to ALGO
        return total
    
    def _analyze_risk_patterns(
        self,
        account_info: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        reputation: AddressReputation
    ) -> int:
        """Analyze risk patterns and return risk score."""
        risk_score = 0
        
        # Check for new account
        if reputation.first_seen:
            first_seen_date = datetime.fromtimestamp(reputation.first_seen)
            days_since_creation = (datetime.utcnow() - first_seen_date).days
            if days_since_creation < self.RISK_PATTERNS["new_account"]["threshold"]:
                risk_score += self.RISK_PATTERNS["new_account"]["risk_weight"]
                reputation.risk_factors.append("new_account")
        
        # Check for high frequency trading
        if len(transactions) > self.RISK_PATTERNS["high_frequency_trading"]["threshold"]:
            risk_score += self.RISK_PATTERNS["high_frequency_trading"]["risk_weight"]
            reputation.risk_factors.append("high_frequency_trading")
        
        # Check for large single transactions
        for tx in transactions[:20]:  # Check recent transactions
            if "payment-transaction" in tx:
                amount = tx["payment-transaction"].get("amount", 0) / 1_000_000
                if amount > self.RISK_PATTERNS["large_single_transaction"]["threshold"]:
                    risk_score += self.RISK_PATTERNS["large_single_transaction"]["risk_weight"]
                    reputation.risk_factors.append("large_single_transaction")
                    break
        
        # Check for dust transactions
        dust_count = 0
        for tx in transactions:
            if "payment-transaction" in tx:
                amount = tx["payment-transaction"].get("amount", 0)
                if amount < 1000:  # Less than 0.001 ALGO
                    dust_count += 1
        if dust_count > self.RISK_PATTERNS["dust_transactions"]["threshold"]:
            risk_score += self.RISK_PATTERNS["dust_transactions"]["risk_weight"]
            reputation.risk_factors.append("dust_transactions")
        
        # Check for failed transactions
        failed_count = sum(1 for tx in transactions if tx.get("tx-type") == "fail")
        if failed_count > self.RISK_PATTERNS["failed_transactions"]["threshold"]:
            risk_score += self.RISK_PATTERNS["failed_transactions"]["risk_weight"]
            reputation.risk_factors.append("failed_transactions")
        
        return risk_score
    
    def _analyze_positive_patterns(
        self,
        account_info: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        reputation: AddressReputation
    ) -> int:
        """Analyze positive patterns and return trust bonus."""
        trust_bonus = 0
        
        # Check for long history
        if reputation.first_seen:
            first_seen_date = datetime.fromtimestamp(reputation.first_seen)
            days_since_creation = (datetime.utcnow() - first_seen_date).days
            if days_since_creation > self.POSITIVE_PATTERNS["long_history"]["threshold"]:
                trust_bonus += self.POSITIVE_PATTERNS["long_history"]["trust_weight"]
                reputation.labels.append("long_history")
        
        # Check for app creation
        if reputation.created_apps >= self.POSITIVE_PATTERNS["app_creator"]["threshold"]:
            trust_bonus += self.POSITIVE_PATTERNS["app_creator"]["trust_weight"]
            reputation.labels.append("developer")
        
        # Check for asset creation
        created_assets = account_info.get("created-assets", [])
        if len(created_assets) >= self.POSITIVE_PATTERNS["asset_creator"]["threshold"]:
            trust_bonus += self.POSITIVE_PATTERNS["asset_creator"]["trust_weight"]
            reputation.labels.append("asset_creator")
        
        return trust_bonus
    
    def _calculate_risk_level(self, trust_score: int) -> RiskLevel:
        """Calculate risk level from trust score."""
        if trust_score >= 70:
            return RiskLevel.LOW
        elif trust_score >= 50:
            return RiskLevel.MEDIUM
        elif trust_score >= 30:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _identify_behavior_patterns(
        self,
        transactions: List[Dict[str, Any]],
        account_info: Dict[str, Any]
    ) -> List[str]:
        """Identify behavior patterns from transaction history."""
        patterns = []
        
        if not transactions:
            patterns.append("inactive")
            return patterns
        
        # Analyze transaction types
        tx_types = {}
        for tx in transactions:
            tx_type = tx.get("tx-type", "unknown")
            tx_types[tx_type] = tx_types.get(tx_type, 0) + 1
        
        if tx_types.get("pay", 0) > len(transactions) * 0.8:
            patterns.append("primarily_payments")
        
        if tx_types.get("appl", 0) > len(transactions) * 0.5:
            patterns.append("app_user")
        
        if tx_types.get("axfer", 0) > len(transactions) * 0.3:
            patterns.append("asset_trader")
        
        # Analyze activity frequency
        if len(transactions) > 50:
            patterns.append("active")
        elif len(transactions) > 10:
            patterns.append("moderate_activity")
        else:
            patterns.append("low_activity")
        
        return patterns
    
    async def batch_get_reputation(
        self,
        addresses: List[str]
    ) -> Dict[str, AddressReputation]:
        """
        Get reputation scores for multiple addresses.
        
        Args:
            addresses: List of Algorand addresses
        
        Returns:
            Dictionary mapping addresses to their reputation
        """
        results = {}
        for address in addresses:
            results[address] = await self.get_reputation(address)
        return results
    
    async def check_address_risk(
        self,
        address: str,
        threshold: int = 50
    ) -> Dict[str, Any]:
        """
        Quick risk check for an address.
        
        Args:
            address: The address to check
            threshold: Risk threshold (lower = stricter)
        
        Returns:
            Risk assessment summary
        """
        reputation = await self.get_reputation(address)
        
        return {
            "address": address,
            "is_safe": reputation.trust_score >= threshold,
            "trust_score": reputation.trust_score,
            "risk_level": reputation.risk_level.value,
            "flags": reputation.flags,
            "risk_factors": reputation.risk_factors[:3],  # Top 3 risk factors
        }


# Singleton instance
_reputation_service: Optional[ReputationService] = None


def get_reputation_service() -> ReputationService:
    """Get or create the reputation service singleton instance."""
    global _reputation_service
    if _reputation_service is None:
        _reputation_service = ReputationService()
    return _reputation_service
