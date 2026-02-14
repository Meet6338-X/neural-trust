"""
Transaction History Service for fetching and aggregating transaction data.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import httpx

from app.config import settings
from app.models.database import RiskAnalysis, Transaction, Vault

logger = logging.getLogger(__name__)


class TransactionHistoryService:
    """
    Service for fetching and aggregating transaction history from multiple sources.
    
    Sources:
    - Local database (RiskAnalysis, Transaction tables)
    - Algorand Indexer (on-chain transactions)
    - Local blockchain (in-memory transactions)
    """
    
    def __init__(self):
        self.algorand_node_url = settings.ALGORAND_NODE_URL or "https://testnet-api.algonode.cloud"
        self.indexer_url = settings.ALGORAND_INDEXER_URL or "https://testnet-idx.algonode.cloud"
    
    async def get_address_transaction_history(
        self,
        address: str,
        limit: int = 20,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive transaction history for an address.
        
        Args:
            address: The Algorand address to query
            limit: Maximum number of transactions to return
            db: Optional database session
        
        Returns:
            Dictionary with transaction history and statistics
        """
        # Get from multiple sources
        db_transactions = await self._get_db_transactions(address, limit, db)
        algorand_transactions = await self._get_algorand_transactions(address, limit)
        
        # Merge and deduplicate
        all_transactions = self._merge_transactions(db_transactions, algorand_transactions)
        
        # Calculate statistics
        stats = self._calculate_statistics(all_transactions)
        
        return {
            "address": address,
            "transactions": all_transactions[:limit],
            "total_count": len(all_transactions),
            "statistics": stats
        }
    
    async def get_risk_analysis_history(
        self,
        address: str,
        limit: int = 20,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get previous risk analyses for an address.
        
        Args:
            address: The address to query
            limit: Maximum number of analyses to return
            db: Database session
        
        Returns:
            Dictionary with risk analysis history
        """
        if not db:
            return {"analyses": [], "statistics": {}}
        
        try:
            # Get vault for this address
            vault_result = await db.execute(
                select(Vault).where(Vault.user_address == address)
            )
            vault = vault_result.scalar_one_or_none()
            
            if not vault:
                return {"analyses": [], "statistics": {}}
            
            # Get risk analyses
            result = await db.execute(
                select(RiskAnalysis)
                .where(RiskAnalysis.vault_id == vault.id)
                .order_by(RiskAnalysis.created_at.desc())
                .limit(limit)
            )
            analyses = result.scalars().all()
            
            # Calculate statistics
            if analyses:
                scores = [a.risk_score for a in analyses]
                recommendations = [a.recommendation for a in analyses]
                
                stats = {
                    "total_analyses": len(analyses),
                    "average_risk_score": sum(scores) / len(scores),
                    "max_risk_score": max(scores),
                    "min_risk_score": min(scores),
                    "risk_trend": self._calculate_trend(scores),
                    "blocked_count": recommendations.count("BLOCK"),
                    "warned_count": recommendations.count("WARN"),
                    "allowed_count": recommendations.count("ALLOW"),
                    "last_analysis": analyses[0].created_at.isoformat() if analyses else None
                }
            else:
                stats = {"total_analyses": 0}
            
            return {
                "address": address,
                "analyses": [
                    {
                        "id": a.id,
                        "transaction_type": a.transaction_type,
                        "amount": a.amount,
                        "sender": a.sender,
                        "recipient": a.recipient,
                        "risk_score": a.risk_score,
                        "recommendation": a.recommendation,
                        "reasoning": a.reasoning,
                        "confidence": a.confidence,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in analyses
                ],
                "statistics": stats
            }
        except Exception as e:
            logger.error(f"Failed to get risk analysis history: {e}")
            return {"analyses": [], "statistics": {}}
    
    async def calculate_transaction_patterns(
        self,
        address: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Analyze transaction patterns for an address.
        
        Args:
            address: The address to analyze
            db: Database session
        
        Returns:
            Dictionary with pattern analysis
        """
        history = await self.get_address_transaction_history(address, limit=50, db=db)
        transactions = history.get("transactions", [])
        
        if not transactions:
            return {
                "has_patterns": False,
                "patterns": {},
                "anomaly_score": 0
            }
        
        patterns = {
            "frequency_pattern": self._analyze_frequency(transactions),
            "amount_pattern": self._analyze_amounts(transactions),
            "time_pattern": self._analyze_timing(transactions),
            "recipient_pattern": self._analyze_recipients(transactions, address)
        }
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(patterns)
        
        return {
            "has_patterns": True,
            "patterns": patterns,
            "anomaly_score": anomaly_score
        }
    
    async def get_address_statistics(
        self,
        address: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics for an address.
        
        Args:
            address: The address to query
            db: Database session
        
        Returns:
            Dictionary with comprehensive statistics
        """
        history = await self.get_address_transaction_history(address, limit=100, db=db)
        risk_history = await self.get_risk_analysis_history(address, limit=50, db=db)
        
        stats = history.get("statistics", {})
        risk_stats = risk_history.get("statistics", {})
        
        # Calculate reputation score
        reputation = self._calculate_reputation(stats, risk_stats)
        
        return {
            "address": address,
            "transaction_stats": stats,
            "risk_stats": risk_stats,
            "reputation": reputation,
            "profile_created": datetime.utcnow().isoformat()
        }
    
    async def _get_db_transactions(
        self,
        address: str,
        limit: int,
        db: Optional[AsyncSession]
    ) -> List[Dict[str, Any]]:
        """Get transactions from local database."""
        if not db:
            return []
        
        try:
            # Get transactions where address is sender or recipient
            result = await db.execute(
                select(Transaction)
                .where(
                    (Transaction.sender == address) | (Transaction.recipient == address)
                )
                .order_by(Transaction.created_at.desc())
                .limit(limit)
            )
            transactions = result.scalars().all()
            
            return [
                {
                    "tx_id": tx.tx_id,
                    "sender": tx.sender,
                    "recipient": tx.recipient,
                    "amount": tx.amount,
                    "type": tx.type,
                    "status": tx.status,
                    "risk_score": tx.risk_score,
                    "timestamp": tx.created_at.isoformat(),
                    "source": "database"
                }
                for tx in transactions
            ]
        except Exception as e:
            logger.error(f"Failed to get DB transactions: {e}")
            return []
    
    async def _get_algorand_transactions(
        self,
        address: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get transactions from Algorand indexer."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.indexer_url}/v2/accounts/{address}/transactions",
                    params={"limit": limit}
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                transactions = data.get("transactions", [])
                
                return [
                    {
                        "tx_id": tx.get("id"),
                        "sender": tx.get("sender"),
                        "recipient": tx.get("payment-transaction", {}).get("receiver", "unknown"),
                        "amount": tx.get("payment-transaction", {}).get("amount", 0) / 1_000_000,
                        "type": tx.get("tx-type", "unknown").replace("pay", "transfer"),
                        "timestamp": datetime.fromtimestamp(tx.get("round-time", 0)).isoformat() if tx.get("round-time") else None,
                        "source": "algorand_indexer",
                        "round": tx.get("confirmed-round")
                    }
                    for tx in transactions
                    if tx.get("tx-type") == "pay"  # Only payment transactions
                ]
        except Exception as e:
            logger.error(f"Failed to get Algorand transactions: {e}")
            return []
    
    def _merge_transactions(
        self,
        db_transactions: List[Dict],
        algorand_transactions: List[Dict]
    ) -> List[Dict]:
        """Merge and deduplicate transactions from multiple sources."""
        # Use tx_id as unique key
        seen_ids = set()
        merged = []
        
        # Add DB transactions first (they have risk scores)
        for tx in db_transactions:
            tx_id = tx.get("tx_id")
            if tx_id and tx_id not in seen_ids:
                seen_ids.add(tx_id)
                merged.append(tx)
        
        # Add Algorand transactions
        for tx in algorand_transactions:
            tx_id = tx.get("tx_id")
            if tx_id and tx_id not in seen_ids:
                seen_ids.add(tx_id)
                merged.append(tx)
        
        # Sort by timestamp descending
        merged.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return merged
    
    def _calculate_statistics(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from transaction list."""
        if not transactions:
            return {
                "total_transactions": 0,
                "total_volume": 0,
                "average_amount": 0,
                "unique_recipients": 0,
                "unique_senders": 0
            }
        
        amounts = [tx.get("amount", 0) for tx in transactions]
        recipients = set(tx.get("recipient") for tx in transactions if tx.get("recipient"))
        senders = set(tx.get("sender") for tx in transactions if tx.get("sender"))
        
        return {
            "total_transactions": len(transactions),
            "total_volume": sum(amounts),
            "average_amount": sum(amounts) / len(amounts) if amounts else 0,
            "max_amount": max(amounts) if amounts else 0,
            "min_amount": min(amounts) if amounts else 0,
            "unique_recipients": len(recipients),
            "unique_senders": len(senders),
            "first_transaction": transactions[-1].get("timestamp") if transactions else None,
            "last_transaction": transactions[0].get("timestamp") if transactions else None
        }
    
    def _calculate_trend(self, scores: List[int]) -> str:
        """Calculate risk score trend."""
        if len(scores) < 2:
            return "insufficient_data"
        
        # Compare recent scores to older scores
        recent = scores[:len(scores)//2]
        older = scores[len(scores)//2:]
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        diff = recent_avg - older_avg
        
        if diff > 10:
            return "declining"  # Risk increasing
        elif diff < -10:
            return "improving"  # Risk decreasing
        else:
            return "stable"
    
    def _analyze_frequency(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze transaction frequency patterns."""
        if len(transactions) < 2:
            return {"pattern": "insufficient_data", "score": 50}
        
        # Calculate time between transactions
        timestamps = []
        for tx in transactions:
            ts = tx.get("timestamp")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    timestamps.append(dt)
                except:
                    pass
        
        if len(timestamps) < 2:
            return {"pattern": "insufficient_data", "score": 50}
        
        # Calculate average time between transactions
        timestamps.sort(reverse=True)
        intervals = []
        for i in range(len(timestamps) - 1):
            interval = (timestamps[i] - timestamps[i + 1]).total_seconds()
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        # Score based on frequency (more frequent = lower risk generally)
        if avg_interval < 3600:  # Less than 1 hour
            score = 30  # Very active
            pattern = "high_frequency"
        elif avg_interval < 86400:  # Less than 1 day
            score = 25
            pattern = "daily"
        elif avg_interval < 604800:  # Less than 1 week
            score = 35
            pattern = "weekly"
        else:
            score = 50
            pattern = "infrequent"
        
        return {
            "pattern": pattern,
            "average_interval_hours": avg_interval / 3600,
            "score": score
        }
    
    def _analyze_amounts(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze transaction amount patterns."""
        amounts = [tx.get("amount", 0) for tx in transactions if tx.get("amount", 0) > 0]
        
        if not amounts:
            return {"pattern": "no_amounts", "score": 50}
        
        avg = sum(amounts) / len(amounts)
        max_amt = max(amounts)
        min_amt = min(amounts)
        
        # Check for consistent amounts (potential automation)
        variance = sum((a - avg) ** 2 for a in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        if std_dev < avg * 0.1:  # Very consistent amounts
            pattern = "consistent"
            score = 40  # Slightly suspicious
        elif max_amt > avg * 10:  # Large outliers
            pattern = "outliers"
            score = 55
        else:
            pattern = "varied"
            score = 25  # Normal varied amounts
        
        return {
            "pattern": pattern,
            "average": avg,
            "max": max_amt,
            "min": min_amt,
            "std_deviation": std_dev,
            "score": score
        }
    
    def _analyze_timing(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze timing patterns for anomalies."""
        timestamps = []
        for tx in transactions:
            ts = tx.get("timestamp")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    timestamps.append(dt)
                except:
                    pass
        
        if len(timestamps) < 3:
            return {"pattern": "insufficient_data", "score": 50}
        
        # Check for unusual timing (late night, weekends, etc.)
        hours = [ts.hour for ts in timestamps]
        
        # Check for clustering
        night_txs = sum(1 for h in hours if h < 6)  # 0-6 AM
        night_ratio = night_txs / len(hours)
        
        if night_ratio > 0.5:
            pattern = "night_heavy"
            score = 60  # Suspicious
        elif night_ratio > 0.3:
            pattern = "night_moderate"
            score = 45
        else:
            pattern = "normal_hours"
            score = 20
        
        return {
            "pattern": pattern,
            "night_transaction_ratio": night_ratio,
            "score": score
        }
    
    def _analyze_recipients(self, transactions: List[Dict], address: str) -> Dict[str, Any]:
        """Analyze recipient diversity."""
        recipients = [tx.get("recipient") for tx in transactions if tx.get("recipient") and tx.get("recipient") != address]
        unique_recipients = set(recipients)
        
        if not unique_recipients:
            return {"pattern": "no_recipients", "score": 50}
        
        # Calculate diversity score
        diversity = len(unique_recipients) / len(recipients) if recipients else 0
        
        if diversity > 0.8:  # High diversity
            pattern = "diverse"
            score = 20  # Good
        elif diversity > 0.5:
            pattern = "moderate"
            score = 35
        else:
            pattern = "concentrated"
            score = 55  # Suspicious - always sending to same addresses
        
        return {
            "pattern": pattern,
            "unique_recipients": len(unique_recipients),
            "total_recipient_transactions": len(recipients),
            "diversity_ratio": diversity,
            "score": score
        }
    
    def _calculate_anomaly_score(self, patterns: Dict) -> int:
        """Calculate overall anomaly score from patterns."""
        scores = []
        weights = {
            "frequency_pattern": 0.20,
            "amount_pattern": 0.25,
            "time_pattern": 0.25,
            "recipient_pattern": 0.30
        }
        
        for pattern_name, weight in weights.items():
            pattern_data = patterns.get(pattern_name, {})
            score = pattern_data.get("score", 50)
            scores.append(score * weight)
        
        return int(sum(scores))
    
    def _calculate_reputation(
        self,
        tx_stats: Dict,
        risk_stats: Dict
    ) -> Dict[str, Any]:
        """Calculate address reputation."""
        # Base reputation score
        base_score = 50
        
        # Adjust based on transaction history
        total_tx = tx_stats.get("total_transactions", 0)
        if total_tx > 50:
            base_score -= 10  # Established address
        elif total_tx > 20:
            base_score -= 5
        elif total_tx < 5:
            base_score += 15  # New address - higher risk
        
        # Adjust based on risk history
        avg_risk = risk_stats.get("average_risk_score", 50)
        blocked_count = risk_stats.get("blocked_count", 0)
        
        if blocked_count > 0:
            base_score += blocked_count * 5  # Each blocked tx increases risk
        
        if avg_risk > 60:
            base_score += 10
        elif avg_risk < 30:
            base_score -= 10
        
        # Determine tier
        if base_score < 30:
            tier = "trusted"
        elif base_score < 50:
            tier = "moderate"
        elif base_score < 70:
            tier = "caution"
        else:
            tier = "high_risk"
        
        return {
            "score": min(100, max(0, base_score)),
            "tier": tier,
            "factors": {
                "transaction_count": total_tx,
                "average_risk": avg_risk,
                "blocked_transactions": blocked_count
            }
        }


# Singleton instance
_transaction_history_service: Optional[TransactionHistoryService] = None


def get_transaction_history_service() -> TransactionHistoryService:
    """Get or create the transaction history service singleton."""
    global _transaction_history_service
    if _transaction_history_service is None:
        _transaction_history_service = TransactionHistoryService()
    return _transaction_history_service