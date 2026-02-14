"""
Risk Calculator Service for calculating risk factors and cumulative scores.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskCalculatorService:
    """
    Service for calculating risk factors and cumulative risk scores.
    
    Risk Factor Weights:
    - Previous Risk Scores: 25%
    - Blocked Transaction History: 25%
    - Transaction Frequency: 15%
    - Time-based Patterns: 15%
    - Recipient Diversity: 10%
    - Average Transaction Amount: 10%
    """
    
    # Risk factor weights
    WEIGHTS = {
        "historical_risk": 0.25,
        "blocked_history": 0.25,
        "transaction_frequency": 0.15,
        "time_patterns": 0.15,
        "recipient_diversity": 0.10,
        "amount_pattern": 0.10
    }
    
    def calculate_risk_factors(
        self,
        transaction_history: Dict[str, Any],
        risk_history: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate all risk factors for an address.
        
        Args:
            transaction_history: Transaction history data
            risk_history: Previous risk analysis data
            patterns: Transaction pattern analysis
        
        Returns:
            Dictionary with all risk factors
        """
        factors = {}
        
        # Historical risk factor
        factors["historical_risk"] = self._calculate_historical_risk_factor(risk_history)
        
        # Blocked history factor
        factors["blocked_history"] = self._calculate_blocked_history_factor(risk_history)
        
        # Transaction frequency factor
        factors["transaction_frequency"] = self._calculate_frequency_factor(
            transaction_history.get("statistics", {}),
            patterns.get("patterns", {}).get("frequency_pattern", {})
        )
        
        # Time pattern factor
        factors["time_patterns"] = self._calculate_time_pattern_factor(
            patterns.get("patterns", {}).get("time_pattern", {})
        )
        
        # Recipient diversity factor
        factors["recipient_diversity"] = self._calculate_recipient_diversity_factor(
            transaction_history.get("statistics", {}),
            patterns.get("patterns", {}).get("recipient_pattern", {})
        )
        
        # Amount pattern factor
        factors["amount_pattern"] = self._calculate_amount_pattern_factor(
            patterns.get("patterns", {}).get("amount_pattern", {})
        )
        
        return factors
    
    def calculate_cumulative_score(
        self,
        current_score: int,
        risk_factors: Dict[str, Any],
        reputation_score: int
    ) -> int:
        """
        Calculate cumulative risk score.
        
        Formula:
        cumulative = (
            current_score * 0.40 +
            historical_avg * 0.25 +
            reputation_score * 0.20 +
            pattern_score * 0.15
        )
        
        Args:
            current_score: Current transaction risk score
            risk_factors: Calculated risk factors
            reputation_score: Address reputation score
        
        Returns:
            Cumulative risk score (0-100)
        """
        # Get weighted factor scores
        historical_score = risk_factors.get("historical_risk", {}).get("weighted_score", 50)
        blocked_score = risk_factors.get("blocked_history", {}).get("weighted_score", 50)
        frequency_score = risk_factors.get("transaction_frequency", {}).get("weighted_score", 50)
        time_score = risk_factors.get("time_patterns", {}).get("weighted_score", 50)
        diversity_score = risk_factors.get("recipient_diversity", {}).get("weighted_score", 50)
        amount_score = risk_factors.get("amount_pattern", {}).get("weighted_score", 50)
        
        # Calculate pattern score (weighted average of pattern factors)
        pattern_score = (
            frequency_score * self.WEIGHTS["transaction_frequency"] +
            time_score * self.WEIGHTS["time_patterns"] +
            diversity_score * self.WEIGHTS["recipient_diversity"] +
            amount_score * self.WEIGHTS["amount_pattern"]
        ) / (self.WEIGHTS["transaction_frequency"] + self.WEIGHTS["time_patterns"] + 
            self.WEIGHTS["recipient_diversity"] + self.WEIGHTS["amount_pattern"])
        
        # Calculate historical component
        historical_component = (
            historical_score * self.WEIGHTS["historical_risk"] +
            blocked_score * self.WEIGHTS["blocked_history"]
        ) / (self.WEIGHTS["historical_risk"] + self.WEIGHTS["blocked_history"])
        
        # Calculate cumulative score
        cumulative = (
            current_score * 0.40 +
            historical_component * 0.25 +
            reputation_score * 0.20 +
            pattern_score * 0.15
        )
        
        return min(100, max(0, int(cumulative)))
    
    def calculate_pattern_score(self, risk_factors: Dict[str, Any]) -> int:
        """
        Calculate overall pattern score from risk factors.
        
        Args:
            risk_factors: Calculated risk factors
        
        Returns:
            Pattern score (0-100)
        """
        scores = []
        
        for factor_name, weight in self.WEIGHTS.items():
            factor_data = risk_factors.get(factor_name, {})
            score = factor_data.get("weighted_score", 50)
            scores.append(score * weight)
        
        return int(sum(scores))
    
    def _calculate_historical_risk_factor(
        self,
        risk_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate historical risk factor from previous analyses."""
        stats = risk_history.get("statistics", {})
        
        total_analyses = stats.get("total_analyses", 0)
        if total_analyses == 0:
            return {
                "score": 50,
                "weighted_score": 50,
                "weight": self.WEIGHTS["historical_risk"],
                "description": "No previous risk analyses",
                "factors": {}
            }
        
        avg_risk = stats.get("average_risk_score", 50)
        max_risk = stats.get("max_risk_score", 50)
        trend = stats.get("risk_trend", "stable")
        
        # Adjust score based on trend
        trend_adjustment = 0
        if trend == "declining":
            trend_adjustment = 10  # Risk increasing
        elif trend == "improving":
            trend_adjustment = -10  # Risk decreasing
        
        score = min(100, max(0, avg_risk + trend_adjustment))
        
        return {
            "score": score,
            "weighted_score": score,
            "weight": self.WEIGHTS["historical_risk"],
            "description": f"Average risk: {avg_risk:.1f}, Trend: {trend}",
            "factors": {
                "total_analyses": total_analyses,
                "average_risk": avg_risk,
                "max_risk": max_risk,
                "trend": trend
            }
        }
    
    def _calculate_blocked_history_factor(
        self,
        risk_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate blocked transaction history factor."""
        stats = risk_history.get("statistics", {})
        
        blocked_count = stats.get("blocked_count", 0)
        total_analyses = stats.get("total_analyses", 0)
        
        if total_analyses == 0:
            return {
                "score": 50,
                "weighted_score": 50,
                "weight": self.WEIGHTS["blocked_history"],
                "description": "No transaction history",
                "factors": {}
            }
        
        # Calculate blocked ratio
        blocked_ratio = blocked_count / total_analyses if total_analyses > 0 else 0
        
        # Score based on blocked ratio
        if blocked_ratio > 0.3:
            score = 85  # High risk
        elif blocked_ratio > 0.1:
            score = 65
        elif blocked_ratio > 0:
            score = 45
        else:
            score = 20  # No blocked transactions - good
        
        return {
            "score": score,
            "weighted_score": score,
            "weight": self.WEIGHTS["blocked_history"],
            "description": f"{blocked_count} blocked out of {total_analyses} transactions",
            "factors": {
                "blocked_count": blocked_count,
                "total_analyses": total_analyses,
                "blocked_ratio": blocked_ratio
            }
        }
    
    def _calculate_frequency_factor(
        self,
        tx_stats: Dict[str, Any],
        frequency_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate transaction frequency factor."""
        total_tx = tx_stats.get("total_transactions", 0)
        
        if total_tx == 0:
            return {
                "score": 50,
                "weighted_score": 50,
                "weight": self.WEIGHTS["transaction_frequency"],
                "description": "No transactions",
                "factors": {}
            }
        
        # Get pattern score from frequency analysis
        pattern_score = frequency_pattern.get("score", 50)
        pattern_type = frequency_pattern.get("pattern", "unknown")
        
        # Adjust based on total transactions
        if total_tx > 100:
            volume_adjustment = -10  # Established address
        elif total_tx > 50:
            volume_adjustment = -5
        elif total_tx < 5:
            volume_adjustment = 15  # New address
        else:
            volume_adjustment = 0
        
        score = min(100, max(0, pattern_score + volume_adjustment))
        
        return {
            "score": score,
            "weighted_score": score,
            "weight": self.WEIGHTS["transaction_frequency"],
            "description": f"Pattern: {pattern_type}, Total: {total_tx} transactions",
            "factors": {
                "total_transactions": total_tx,
                "pattern": pattern_type,
                "average_interval_hours": frequency_pattern.get("average_interval_hours")
            }
        }
    
    def _calculate_time_pattern_factor(
        self,
        time_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate time pattern factor."""
        pattern_score = time_pattern.get("score", 50)
        pattern_type = time_pattern.get("pattern", "unknown")
        night_ratio = time_pattern.get("night_transaction_ratio", 0)
        
        return {
            "score": pattern_score,
            "weighted_score": pattern_score,
            "weight": self.WEIGHTS["time_patterns"],
            "description": f"Pattern: {pattern_type}, Night ratio: {night_ratio:.1%}",
            "factors": {
                "pattern": pattern_type,
                "night_transaction_ratio": night_ratio
            }
        }
    
    def _calculate_recipient_diversity_factor(
        self,
        tx_stats: Dict[str, Any],
        recipient_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate recipient diversity factor."""
        unique_recipients = tx_stats.get("unique_recipients", 0)
        
        if unique_recipients == 0:
            return {
                "score": 50,
                "weighted_score": 50,
                "weight": self.WEIGHTS["recipient_diversity"],
                "description": "No recipients",
                "factors": {}
            }
        
        pattern_score = recipient_pattern.get("score", 50)
        pattern_type = recipient_pattern.get("pattern", "unknown")
        diversity_ratio = recipient_pattern.get("diversity_ratio", 0)
        
        return {
            "score": pattern_score,
            "weighted_score": pattern_score,
            "weight": self.WEIGHTS["recipient_diversity"],
            "description": f"Pattern: {pattern_type}, {unique_recipients} unique recipients",
            "factors": {
                "unique_recipients": unique_recipients,
                "pattern": pattern_type,
                "diversity_ratio": diversity_ratio
            }
        }
    
    def _calculate_amount_pattern_factor(
        self,
        amount_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate amount pattern factor."""
        pattern_score = amount_pattern.get("score", 50)
        pattern_type = amount_pattern.get("pattern", "unknown")
        avg_amount = amount_pattern.get("average", 0)
        
        return {
            "score": pattern_score,
            "weighted_score": pattern_score,
            "weight": self.WEIGHTS["amount_pattern"],
            "description": f"Pattern: {pattern_type}, Avg: {avg_amount:.2f} ALGO",
            "factors": {
                "pattern": pattern_type,
                "average": avg_amount,
                "max": amount_pattern.get("max"),
                "min": amount_pattern.get("min")
            }
        }
    
    def get_risk_recommendation(self, cumulative_score: int) -> str:
        """
        Get recommendation based on cumulative score.
        
        Args:
            cumulative_score: The cumulative risk score
        
        Returns:
            Recommendation string (ALLOW, WARN, BLOCK)
        """
        if cumulative_score <= 30:
            return "ALLOW"
        elif cumulative_score <= 60:
            return "WARN"
        else:
            return "BLOCK"
    
    def get_risk_level(self, score: int) -> str:
        """
        Get risk level description.
        
        Args:
            score: Risk score
        
        Returns:
            Risk level string
        """
        if score <= 20:
            return "very_low"
        elif score <= 40:
            return "low"
        elif score <= 60:
            return "medium"
        elif score <= 80:
            return "high"
        else:
            return "very_high"


# Singleton instance
_risk_calculator_service: Optional[RiskCalculatorService] = None


def get_risk_calculator_service() -> RiskCalculatorService:
    """Get or create the risk calculator service singleton."""
    global _risk_calculator_service
    if _risk_calculator_service is None:
        _risk_calculator_service = RiskCalculatorService()
    return _risk_calculator_service