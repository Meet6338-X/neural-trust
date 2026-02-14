"""
Simplified Risk Analysis Service - Single Address Input, Maximum Output.
"""

import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.config import settings
from app.services.transaction_history_service import get_transaction_history_service
from app.services.risk_calculator_service import get_risk_calculator_service

logger = logging.getLogger(__name__)


class SimplifiedAnalysisService:
    """
    Simplified risk analysis service.
    
    Input: Just an address
    Output: Comprehensive risk report with funds, transactions, and risk factors
    """
    
    def __init__(self):
        self.algorand_node_url = settings.ALGORAND_NODE_URL or "https://testnet-api.algonode.cloud"
        self.indexer_url = settings.ALGORAND_INDEXER_URL or "https://testnet-idx.algonode.cloud"
        self.history_service = get_transaction_history_service()
        self.risk_calculator = get_risk_calculator_service()
    
    async def analyze_address(
        self,
        address: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis with just an address.
        
        Args:
            address: Algorand address to analyze
            db: Optional database session
        
        Returns:
            Complete risk analysis report
        """
        logger.info(f"Starting simplified analysis for: {address}")
        
        # 1. Get account info (funds, assets)
        account_info = await self._get_account_info(address)
        
        # 2. Get transaction history
        tx_history = await self.history_service.get_address_transaction_history(
            address, limit=50, db=db
        )
        
        # 3. Get risk analysis history
        risk_history = await self.history_service.get_risk_analysis_history(
            address, limit=20, db=db
        )
        
        # 4. Calculate patterns
        patterns = await self.history_service.calculate_transaction_patterns(
            address, db=db
        )
        
        # 5. Calculate risk factors
        risk_factors = self.risk_calculator.calculate_risk_factors(
            tx_history, risk_history, patterns
        )
        
        # 6. Calculate overall risk score
        pattern_score = self.risk_calculator.calculate_pattern_score(risk_factors)
        
        # Get reputation from address stats
        address_stats = await self.history_service.get_address_statistics(address, db=db)
        reputation = address_stats.get("reputation", {})
        
        # Calculate final risk score
        risk_score = self._calculate_final_risk_score(
            account_info, tx_history, risk_factors, pattern_score, reputation
        )
        
        # 7. Generate recommendations
        recommendations = self._generate_recommendations(
            risk_score, account_info, tx_history, risk_factors
        )
        
        # 8. Check for flags
        flags = self._check_flags(account_info, tx_history, risk_factors)
        
        # 9. Build comprehensive response
        return {
            "address": address,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "recommendation": self.risk_calculator.get_risk_recommendation(risk_score),
            "funds": {
                "algo_balance": account_info.get("balance", 0),
                "balance_micro_algos": account_info.get("balance_micro_algos", 0),
                "assets_count": len(account_info.get("assets", [])),
                "assets": account_info.get("assets", [])[:5],  # Top 5 assets
                "min_balance": account_info.get("min_balance", 0),
                "status": account_info.get("status", "unknown")
            },
            "transaction_summary": {
                "total_transactions": tx_history.get("total_count", 0),
                "total_volume": tx_history.get("statistics", {}).get("total_volume", 0),
                "average_amount": tx_history.get("statistics", {}).get("average_amount", 0),
                "unique_counterparties": tx_history.get("statistics", {}).get("unique_recipients", 0) + 
                                        tx_history.get("statistics", {}).get("unique_senders", 0),
                "first_transaction": tx_history.get("statistics", {}).get("first_transaction"),
                "last_transaction": tx_history.get("statistics", {}).get("last_transaction")
            },
            "risk_factors": {
                "account_age": {
                    "score": self._calculate_age_score(tx_history),
                    "status": self._get_age_status(tx_history),
                    "details": f"Account has {tx_history.get('total_count', 0)} transactions"
                },
                "transaction_frequency": {
                    "score": risk_factors.get("transaction_frequency", {}).get("score", 50),
                    "status": risk_factors.get("transaction_frequency", {}).get("description", "Unknown"),
                    "details": risk_factors.get("transaction_frequency", {}).get("factors", {})
                },
                "counterparty_diversity": {
                    "score": risk_factors.get("recipient_diversity", {}).get("score", 50),
                    "status": risk_factors.get("recipient_diversity", {}).get("description", "Unknown"),
                    "details": risk_factors.get("recipient_diversity", {}).get("factors", {})
                },
                "value_patterns": {
                    "score": risk_factors.get("amount_pattern", {}).get("score", 50),
                    "status": risk_factors.get("amount_pattern", {}).get("description", "Unknown"),
                    "details": risk_factors.get("amount_pattern", {}).get("factors", {})
                },
                "historical_risk": {
                    "score": risk_factors.get("historical_risk", {}).get("score", 50),
                    "status": risk_factors.get("historical_risk", {}).get("description", "No history"),
                    "details": risk_factors.get("historical_risk", {}).get("factors", {})
                }
            },
            "flags": flags,
            "suggestions": recommendations,
            "reputation": reputation,
            "pattern_score": pattern_score,
            "analysis_timestamp": self._get_timestamp()
        }
    
    async def _get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information from Algorand."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.algorand_node_url}/v2/accounts/{address}"
                )
                
                if response.status_code != 200:
                    return {"balance": 0, "assets": [], "status": "not_found"}
                
                data = response.json()
                amount = data.get("amount", 0)
                
                return {
                    "balance": amount / 1_000_000,  # Convert to ALGO
                    "balance_micro_algos": amount,
                    "min_balance": data.get("min-balance", 0),
                    "status": data.get("status", "unknown"),
                    "assets": [
                        {
                            "asset_id": asset.get("asset-id"),
                            "amount": asset.get("amount", 0),
                            "is_frozen": asset.get("is-frozen", False)
                        }
                        for asset in data.get("assets", [])
                    ],
                    "created_at_round": data.get("created-at-round"),
                    "rewards": data.get("rewards", 0)
                }
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return {"balance": 0, "assets": [], "status": "error", "error": str(e)}
    
    def _calculate_final_risk_score(
        self,
        account_info: Dict,
        tx_history: Dict,
        risk_factors: Dict,
        pattern_score: int,
        reputation: Dict
    ) -> int:
        """Calculate final risk score from all factors."""
        # Base score from pattern analysis
        base_score = pattern_score
        
        # Adjust for account balance
        balance = account_info.get("balance", 0)
        if balance == 0:
            base_score += 10  # Empty account is slightly suspicious
        elif balance > 1000:
            base_score -= 5  # Well-funded account is more established
        
        # Adjust for transaction count
        tx_count = tx_history.get("total_count", 0)
        if tx_count == 0:
            base_score += 15  # New account with no history
        elif tx_count > 50:
            base_score -= 10  # Established account
        elif tx_count > 10:
            base_score -= 5
        
        # Adjust for reputation
        rep_score = reputation.get("score", 50)
        base_score = (base_score * 0.7) + (rep_score * 0.3)
        
        return min(100, max(0, int(base_score)))
    
    def _calculate_age_score(self, tx_history: Dict) -> int:
        """Calculate score based on account age/activity."""
        tx_count = tx_history.get("total_count", 0)
        
        if tx_count == 0:
            return 70  # New account - higher risk
        elif tx_count < 5:
            return 50  # Very new
        elif tx_count < 20:
            return 35  # Some history
        elif tx_count < 50:
            return 25  # Established
        else:
            return 15  # Very established
    
    def _get_age_status(self, tx_history: Dict) -> str:
        """Get status text for account age."""
        tx_count = tx_history.get("total_count", 0)
        
        if tx_count == 0:
            return "new_account"
        elif tx_count < 5:
            return "very_new"
        elif tx_count < 20:
            return "some_history"
        elif tx_count < 50:
            return "established"
        else:
            return "well_established"
    
    def _generate_recommendations(
        self,
        risk_score: int,
        account_info: Dict,
        tx_history: Dict,
        risk_factors: Dict
    ) -> list:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Based on risk score
        if risk_score > 70:
            recommendations.append("High risk detected - manual review recommended")
        elif risk_score > 50:
            recommendations.append("Moderate risk - proceed with caution")
        
        # Based on account status
        tx_count = tx_history.get("total_count", 0)
        if tx_count == 0:
            recommendations.append("New account - monitor initial transactions closely")
        
        balance = account_info.get("balance", 0)
        if balance == 0:
            recommendations.append("Account has zero balance - verify legitimacy")
        
        # Based on risk factors
        if risk_factors.get("recipient_diversity", {}).get("score", 50) > 60:
            recommendations.append("Limited counterparty diversity - investigate relationships")
        
        # Positive recommendations
        if risk_score < 30:
            recommendations.append("Low risk profile - account appears legitimate")
        
        # Vault suggestion
        recommendations.append("Consider setting up vault protection for enhanced security")
        
        return recommendations
    
    def _check_flags(
        self,
        account_info: Dict,
        tx_history: Dict,
        risk_factors: Dict
    ) -> list:
        """Check for warning flags."""
        flags = []
        
        # Check for zero balance
        if account_info.get("balance", 0) == 0:
            flags.append({
                "type": "warning",
                "message": "Account has zero balance",
                "severity": "medium"
            })
        
        # Check for new account
        if tx_history.get("total_count", 0) == 0:
            flags.append({
                "type": "info",
                "message": "New account with no transaction history",
                "severity": "low"
            })
        
        # Check for high-risk patterns
        if risk_factors.get("time_patterns", {}).get("score", 50) > 60:
            flags.append({
                "type": "warning",
                "message": "Unusual transaction timing detected",
                "severity": "medium"
            })
        
        # Check for frozen assets
        frozen_assets = [
            a for a in account_info.get("assets", [])
            if a.get("is_frozen", False)
        ]
        if frozen_assets:
            flags.append({
                "type": "warning",
                "message": f"{len(frozen_assets)} frozen assets found",
                "severity": "high"
            })
        
        return flags
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level from score."""
        if score <= 20:
            return "VERY_LOW"
        elif score <= 40:
            return "LOW"
        elif score <= 60:
            return "MEDIUM"
        elif score <= 80:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Singleton instance
_simplified_analysis_service: Optional[SimplifiedAnalysisService] = None


def get_simplified_analysis_service() -> SimplifiedAnalysisService:
    """Get or create the simplified analysis service singleton."""
    global _simplified_analysis_service
    if _simplified_analysis_service is None:
        _simplified_analysis_service = SimplifiedAnalysisService()
    return _simplified_analysis_service