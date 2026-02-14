"""
AI Risk Engine using OpenRouter API with dynamic risk analysis.
Incorporates transaction history for cumulative risk profiles.
"""

import json
import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.config import settings
from app.services.transaction_history_service import get_transaction_history_service, TransactionHistoryService
from app.services.risk_calculator_service import get_risk_calculator_service, RiskCalculatorService

logger = logging.getLogger(__name__)


class AIRiskEngine:
    """
    AI-powered risk analysis engine using OpenRouter API.
    
    This service analyzes DeFi transactions and returns risk scores
    and recommendations, incorporating historical transaction data
    for cumulative risk profiles.
    """
    
    def __init__(self) -> None:
        """Initialize the AI Risk Engine."""
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.AI_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.history_service = get_transaction_history_service()
        self.risk_calculator = get_risk_calculator_service()
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
    
    async def analyze_transaction(
        self,
        transaction_data: Dict[str, Any],
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Analyze a transaction and return risk assessment.
        
        Args:
            transaction_data: Dictionary containing transaction details
                - type: Transaction type (e.g., "transfer", "swap", "stake")
                - amount: Amount in ALGO
                - recipient: Recipient address
                - sender: Sender address
                - timestamp: Transaction timestamp
                - protocol: Optional protocol name
                - additional_context: Any additional context
            db: Optional database session for history lookup
        
        Returns:
            Dictionary containing:
                - risk_score: Current transaction risk score (0-100)
                - cumulative_risk_score: Cumulative risk including history
                - recommendation: "ALLOW", "WARN", or "BLOCK"
                - reasoning: Explanation of the risk assessment
                - model_used: Model name used for analysis
                - confidence: Confidence level (0-1)
                - historical_context: Historical data summary
                - risk_factors: Breakdown of risk factors
        """
        sender = transaction_data.get("sender", "")
        
        # Fetch historical data
        historical_context = {}
        risk_factors = {}
        reputation = {}
        
        if sender and db:
            try:
                # Get transaction history
                tx_history = await self.history_service.get_address_transaction_history(
                    sender, limit=20, db=db
                )
                
                # Get risk analysis history
                risk_history = await self.history_service.get_risk_analysis_history(
                    sender, limit=20, db=db
                )
                
                # Get transaction patterns
                patterns = await self.history_service.calculate_transaction_patterns(
                    sender, db=db
                )
                
                # Get address statistics
                address_stats = await self.history_service.get_address_statistics(
                    sender, db=db
                )
                
                # Calculate risk factors
                risk_factors = self.risk_calculator.calculate_risk_factors(
                    tx_history, risk_history, patterns
                )
                
                # Get reputation
                reputation = address_stats.get("reputation", {})
                
                # Build historical context for AI prompt
                historical_context = {
                    "total_previous_transactions": tx_history.get("total_count", 0),
                    "average_previous_risk_score": risk_history.get("statistics", {}).get("average_risk_score", 50),
                    "risk_trend": risk_history.get("statistics", {}).get("risk_trend", "unknown"),
                    "reputation_tier": reputation.get("tier", "unknown"),
                    "blocked_count": risk_history.get("statistics", {}).get("blocked_count", 0),
                    "warned_count": risk_history.get("statistics", {}).get("warned_count", 0),
                    "account_age_days": self._calculate_account_age(tx_history),
                    "unique_recipients": tx_history.get("statistics", {}).get("unique_recipients", 0)
                }
                
            except Exception as e:
                logger.error(f"Failed to fetch historical data: {e}")
                historical_context = {"error": str(e)}
        
        # Build enhanced prompt with history
        prompt = self._build_analysis_prompt(transaction_data, historical_context, risk_factors)
        
        try:
            result = await self._call_openrouter(prompt)
            ai_response = self._parse_ai_response(result)
            
            # Calculate cumulative risk score
            current_score = ai_response.get("risk_score", 50)
            reputation_score = reputation.get("score", 50) if reputation else 50
            
            cumulative_score = self.risk_calculator.calculate_cumulative_score(
                current_score, risk_factors, reputation_score
            )
            
            # Build enhanced response
            response = {
                **ai_response,
                "cumulative_risk_score": cumulative_score,
                "historical_context": historical_context,
                "risk_factors": risk_factors if risk_factors else None,
                "reputation": reputation if reputation else None
            }
            
            return response
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._get_default_response(historical_context)
    
    async def analyze_transaction_simple(
        self,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simple analysis without historical data (for backward compatibility).
        
        Args:
            transaction_data: Transaction details
        
        Returns:
            Risk analysis result
        """
        prompt = self._build_analysis_prompt(transaction_data, {}, {})
        
        try:
            result = await self._call_openrouter(prompt)
            return self._parse_ai_response(result)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._get_default_response()
    
    async def batch_analyze(
        self,
        transactions: list[Dict[str, Any]],
        db: Optional[AsyncSession] = None
    ) -> list[Dict[str, Any]]:
        """
        Analyze multiple transactions in batch.
        
        Args:
            transactions: List of transaction data dictionaries
            db: Optional database session
        
        Returns:
            List of risk analysis results
        """
        results = []
        for tx in transactions:
            result = await self.analyze_transaction(tx, db=db)
            results.append(result)
        return results
    
    def _build_analysis_prompt(
        self,
        transaction_data: Dict[str, Any],
        historical_context: Dict[str, Any],
        risk_factors: Dict[str, Any]
    ) -> str:
        """Build the analysis prompt for the AI model."""
        tx_type = transaction_data.get("type", "unknown")
        amount = transaction_data.get("amount", "0")
        recipient = transaction_data.get("recipient", "unknown")
        sender = transaction_data.get("sender", "unknown")
        protocol = transaction_data.get("protocol", "unknown")
        
        # Base prompt
        prompt = f"""You are a DeFi security analyst specializing in Algorand blockchain transactions. Analyze the following transaction for potential risks.

Transaction Details:
- Type: {tx_type}
- Amount: {amount} ALGO
- Sender: {sender}
- Recipient: {recipient}
- Protocol: {protocol}
- Timestamp: {transaction_data.get('timestamp', 'unknown')}
"""
        
        # Add historical context if available
        if historical_context and "error" not in historical_context:
            prompt += f"""
Historical Context for Sender:
- Previous Transactions: {historical_context.get('total_previous_transactions', 0)}
- Average Previous Risk Score: {historical_context.get('average_previous_risk_score', 'N/A')}
- Risk Trend: {historical_context.get('risk_trend', 'unknown')}
- Reputation Tier: {historical_context.get('reputation_tier', 'unknown')}
- Blocked Transactions: {historical_context.get('blocked_count', 0)}
- Warning Transactions: {historical_context.get('warned_count', 0)}
- Account Age: {historical_context.get('account_age_days', 'unknown')} days
- Unique Recipients: {historical_context.get('unique_recipients', 0)}
"""
        
        # Add risk factor summary if available
        if risk_factors:
            prompt += "\nRisk Factor Summary:\n"
            for factor_name, factor_data in risk_factors.items():
                if isinstance(factor_data, dict):
                    score = factor_data.get("score", "N/A")
                    description = factor_data.get("description", "")
                    prompt += f"- {factor_name}: {score}/100 ({description})\n"
        
        prompt += f"""
Risk Factors to Consider:
1. Is this a suspicious transaction pattern?
2. Could this be a scam or phishing attempt?
3. Is the amount unusually large for this type of transaction?
4. Is the recipient address new or unknown?
5. Are there any red flags in the transaction metadata?
6. Is this a known high-risk protocol?
7. Does this transaction fit the sender's historical pattern?
8. Is there a sudden change in transaction behavior?

Provide your analysis in the following JSON format:
{{
    "risk_score": <number from 0 to 100>,
    "recommendation": "ALLOW" | "WARN" | "BLOCK",
    "reasoning": "<brief explanation of your assessment>",
    "confidence": <number from 0 to 1>
}}

Risk Score Guidelines:
- 0-30: Low risk - Safe to proceed
- 31-60: Medium risk - Proceed with caution
- 61-100: High risk - Block or require additional verification

Return ONLY the JSON object, no additional text."""
        
        return prompt
    
    async def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        """
        Call the OpenRouter API with the given prompt.
        
        Args:
            prompt: The prompt to send to the AI model
        
        Returns:
            The API response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://chainguardian.app",
            "X-Title": "ChainGuardian",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a DeFi security analyst. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_ai_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the AI response and extract risk analysis.
        
        Args:
            response: The raw API response
        
        Returns:
            Parsed risk analysis dictionary
        """
        try:
            content = response["choices"][0]["message"]["content"]
            analysis = json.loads(content)
            
            # Validate and sanitize the response
            risk_score = min(100, max(0, int(analysis.get("risk_score", 50))))
            recommendation = analysis.get("recommendation", "WARN")
            reasoning = analysis.get("reasoning", "Analysis complete")
            confidence = min(1.0, max(0.0, float(analysis.get("confidence", 0.5))))
            
            # Validate recommendation
            if recommendation not in ["ALLOW", "WARN", "BLOCK"]:
                recommendation = "WARN"
            
            return {
                "risk_score": risk_score,
                "recommendation": recommendation,
                "reasoning": reasoning,
                "model_used": "Advanced AI Engine",
                "confidence": confidence,
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._get_default_response()
    
    def _get_default_response(
        self,
        historical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Return a safe default response when AI analysis fails."""
        return {
            "risk_score": 50,
            "cumulative_risk_score": 50,
            "recommendation": "WARN",
            "reasoning": "AI analysis unavailable - manual review recommended",
            "model_used": "fallback",
            "confidence": 0.0,
            "historical_context": historical_context or {},
            "risk_factors": None,
            "reputation": None
        }
    
    def _calculate_account_age(self, tx_history: Dict[str, Any]) -> int:
        """Calculate account age in days from transaction history."""
        stats = tx_history.get("statistics", {})
        first_tx = stats.get("first_transaction")
        
        if not first_tx:
            return 0
        
        try:
            from datetime import datetime
            first_date = datetime.fromisoformat(first_tx.replace("Z", "+00:00"))
            now = datetime.utcnow()
            age = (now - first_date.replace(tzinfo=None)).days
            return max(0, age)
        except:
            return 0
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the AI model being used.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "provider": "OpenRouter",
            "api_base": self.base_url,
            "configured": bool(self.api_key),
            "features": [
                "dynamic_risk_analysis",
                "transaction_history",
                "cumulative_scoring",
                "risk_factors"
            ]
        }
    
    async def get_address_risk_profile(
        self,
        address: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive risk profile for an address.
        
        Args:
            address: The address to profile
            db: Database session
        
        Returns:
            Complete risk profile
        """
        if not db:
            return {"error": "Database session required"}
        
        try:
            # Get all historical data
            tx_history = await self.history_service.get_address_transaction_history(
                address, limit=50, db=db
            )
            risk_history = await self.history_service.get_risk_analysis_history(
                address, limit=50, db=db
            )
            patterns = await self.history_service.calculate_transaction_patterns(
                address, db=db
            )
            stats = await self.history_service.get_address_statistics(
                address, db=db
            )
            
            # Calculate risk factors
            risk_factors = self.risk_calculator.calculate_risk_factors(
                tx_history, risk_history, patterns
            )
            
            # Calculate pattern score
            pattern_score = self.risk_calculator.calculate_pattern_score(risk_factors)
            
            return {
                "address": address,
                "reputation": stats.get("reputation", {}),
                "transaction_statistics": tx_history.get("statistics", {}),
                "risk_statistics": risk_history.get("statistics", {}),
                "patterns": patterns,
                "risk_factors": risk_factors,
                "pattern_score": pattern_score,
                "recent_transactions": tx_history.get("transactions", [])[:10],
                "recent_analyses": risk_history.get("analyses", [])[:10]
            }
        except Exception as e:
            logger.error(f"Failed to get risk profile: {e}")
            return {"error": str(e)}


# Singleton instance
_ai_engine: Optional[AIRiskEngine] = None


def get_ai_engine() -> AIRiskEngine:
    """Get or create the AI engine singleton instance."""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIRiskEngine()
    return _ai_engine
