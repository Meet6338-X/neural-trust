"""
Portfolio Risk Analyzer Service for Algorand.

Analyzes user portfolios for risk exposure, concentration risks,
and provides AI-driven recommendations for risk mitigation.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
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
class AssetHolding:
    """Represents an asset holding in a portfolio."""
    asset_id: int
    asset_name: str
    amount: float
    value_usd: Optional[float] = None
    risk_score: int = 0
    asset_type: str = "asa"  # asa, nft, lp


@dataclass
class ProtocolExposure:
    """Represents exposure to a DeFi protocol."""
    protocol_name: str
    exposure_usd: float
    risk_level: RiskLevel
    description: Optional[str] = None
    contracts: List[str] = field(default_factory=list)


@dataclass
class PortfolioAnalysis:
    """Result of portfolio risk analysis."""
    address: str
    total_value_usd: float
    risk_score: int
    risk_level: RiskLevel
    asset_breakdown: List[AssetHolding]
    protocol_exposure: List[ProtocolExposure]
    concentration_risks: List[str]
    recommendations: List[str]
    analysis_time_ms: float


class PortfolioAnalyzer:
    """
    AI-powered portfolio risk analyzer for Algorand.
    
    Analyzes asset composition, protocol exposure, and concentration
    risks to provide comprehensive risk assessment.
    """
    
    # Known DeFi protocols on Algorand
    KNOWN_PROTOCOLS = {
        "tinyman": {
            "name": "Tinyman",
            "risk_level": RiskLevel.LOW,
            "description": "Decentralized exchange",
            "app_ids": [350338509, 552655436]  # Example app IDs
        },
        "pact": {
            "name": "Pact",
            "risk_level": RiskLevel.LOW,
            "description": "AMM DEX",
            "app_ids": [766495262]
        },
        "algofi": {
            "name": "AlgoFi",
            "risk_level": RiskLevel.MEDIUM,
            "description": "Lending protocol",
            "app_ids": [465818543]
        },
        "folks": {
            "name": "Folks Finance",
            "risk_level": RiskLevel.LOW,
            "description": "Lending protocol",
            "app_ids": [655540327]
        },
        "vestige": {
            "name": "Vestige",
            "risk_level": RiskLevel.LOW,
            "description": "Token analytics",
            "app_ids": []
        },
        "yieldly": {
            "name": "Yieldly",
            "risk_level": RiskLevel.MEDIUM,
            "description": "Yield aggregator",
            "app_ids": [233725848]
        },
    }
    
    # Risk weights for different asset types
    ASSET_RISK_WEIGHTS = {
        "native": 0,  # ALGO
        "stablecoin": 5,  # USDC, USDT
        "major_asa": 15,  # USDC, goBTC, goETH
        "defi_token": 30,  # Governance tokens
        "meme_token": 60,  # High volatility
        "nft": 40,  # NFTs
        "lp_token": 35,  # LP tokens
        "unknown": 50,  # Unknown assets
    }
    
    # Known stablecoins
    STABLECOINS = [312769, 465818830, 841143952]  # USDC, USDT, etc.
    
    # Major ASAs
    MAJOR_ASAS = [312769, 386192725, 386195940, 31566704]  # USDC, goBTC, goETH, etc.
    
    def __init__(self) -> None:
        """Initialize the portfolio analyzer."""
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
    
    async def analyze_portfolio(
        self,
        address: str,
        include_recommendations: bool = True
    ) -> PortfolioAnalysis:
        """
        Analyze a portfolio for risk exposure.
        
        Args:
            address: The Algorand address to analyze
            include_recommendations: Whether to include AI recommendations
        
        Returns:
            PortfolioAnalysis with risk assessment
        """
        import time
        start_time = time.time()
        
        # Initialize result
        result = PortfolioAnalysis(
            address=address,
            total_value_usd=0.0,
            risk_score=0,
            risk_level=RiskLevel.MEDIUM,
            asset_breakdown=[],
            protocol_exposure=[],
            concentration_risks=[],
            recommendations=[]
        )
        
        try:
            # Get account information
            account_info = await self._get_account_info(address)
            if account_info is None:
                result.concentration_risks.append("Account not found")
                return result
            
            # Analyze ALGO balance
            algo_balance = account_info.get("amount", 0) / 1_000_000
            result.asset_breakdown.append(AssetHolding(
                asset_id=0,
                asset_name="ALGO",
                amount=algo_balance,
                value_usd=algo_balance * 0.20,  # Approximate ALGO price
                risk_score=0,
                asset_type="native"
            ))
            
            # Analyze asset holdings
            assets = account_info.get("assets", [])
            for asset in assets:
                holding = await self._analyze_asset(asset)
                if holding:
                    result.asset_breakdown.append(holding)
            
            # Calculate total value
            result.total_value_usd = sum(
                h.value_usd or h.amount for h in result.asset_breakdown
            )
            
            # Analyze protocol exposure
            result.protocol_exposure = await self._analyze_protocol_exposure(
                address, account_info
            )
            
            # Calculate concentration risks
            result.concentration_risks = self._calculate_concentration_risks(
                result.asset_breakdown, result.total_value_usd
            )
            
            # Calculate overall risk score
            result.risk_score = self._calculate_risk_score(
                result.asset_breakdown,
                result.protocol_exposure,
                result.concentration_risks
            )
            
            # Determine risk level
            result.risk_level = self._determine_risk_level(result.risk_score)
            
            # Generate recommendations
            if include_recommendations:
                result.recommendations = await self._generate_recommendations(
                    result, address
                )
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed for {address}: {e}")
            result.concentration_risks.append(f"Analysis error: {str(e)[:100]}")
        
        result.analysis_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _get_account_info(self, address: str) -> Optional[Dict[str, Any]]:
        """Get account information from the blockchain."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            account_info = await loop.run_in_executor(
                None,
                self.algod_client.account_info,
                address
            )
            return account_info
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return None
    
    async def _analyze_asset(self, asset_data: Dict[str, Any]) -> Optional[AssetHolding]:
        """Analyze a single asset holding."""
        try:
            asset_id = asset_data.get("asset-id", 0)
            amount = asset_data.get("amount", 0)
            
            # Get asset info
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                asset_info = await loop.run_in_executor(
                    None,
                    self.algod_client.asset_info,
                    asset_id
                )
                params = asset_info.get("params", {})
                name = params.get("name", f"Asset {asset_id}")
                decimals = params.get("decimals", 0)
                total_amount = amount / (10 ** decimals)
            except Exception:
                name = f"Asset {asset_id}"
                total_amount = amount / 1_000_000  # Assume 6 decimals
            
            # Determine asset type and risk
            asset_type, risk_score = self._classify_asset(asset_id, name)
            
            # Estimate value (simplified)
            value_usd = self._estimate_asset_value(asset_id, total_amount, name)
            
            return AssetHolding(
                asset_id=asset_id,
                asset_name=name,
                amount=total_amount,
                value_usd=value_usd,
                risk_score=risk_score,
                asset_type=asset_type
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze asset: {e}")
            return None
    
    def _classify_asset(self, asset_id: int, name: str) -> tuple:
        """Classify asset type and determine risk score."""
        name_lower = name.lower()
        
        # Check for stablecoins
        if asset_id in self.STABLECOINS or "usd" in name_lower:
            return "stablecoin", self.ASSET_RISK_WEIGHTS["stablecoin"]
        
        # Check for major ASAs
        if asset_id in self.MAJOR_ASAS:
            return "major_asa", self.ASSET_RISK_WEIGHTS["major_asa"]
        
        # Check for LP tokens
        if "lp" in name_lower or "pool" in name_lower:
            return "lp_token", self.ASSET_RISK_WEIGHTS["lp_token"]
        
        # Check for NFTs
        if "nft" in name_lower or len(name) > 30:
            return "nft", self.ASSET_RISK_WEIGHTS["nft"]
        
        # Check for meme tokens
        meme_keywords = ["meme", "doge", "shib", "pepe", "wojak"]
        if any(kw in name_lower for kw in meme_keywords):
            return "meme_token", self.ASSET_RISK_WEIGHTS["meme_token"]
        
        # Check for DeFi tokens
        defi_keywords = ["gov", "dao", "token", "swap", "finance"]
        if any(kw in name_lower for kw in defi_keywords):
            return "defi_token", self.ASSET_RISK_WEIGHTS["defi_token"]
        
        return "unknown", self.ASSET_RISK_WEIGHTS["unknown"]
    
    def _estimate_asset_value(
        self,
        asset_id: int,
        amount: float,
        name: str
    ) -> float:
        """Estimate USD value of an asset holding."""
        # Simplified estimation - in production would use price oracle
        if asset_id in self.STABLECOINS:
            return amount  # 1:1 for stablecoins
        
        if asset_id in self.MAJOR_ASAS:
            # Approximate values
            if "btc" in name.lower():
                return amount * 40000  # Approximate BTC price
            elif "eth" in name.lower():
                return amount * 2500  # Approximate ETH price
            return amount  # Default 1:1
        
        # For unknown assets, assume low value
        return amount * 0.01
    
    async def _analyze_protocol_exposure(
        self,
        address: str,
        account_info: Dict[str, Any]
    ) -> List[ProtocolExposure]:
        """Analyze exposure to DeFi protocols."""
        exposures = []
        
        # Check opted-in apps
        apps = account_info.get("apps-local-state", [])
        for app in apps:
            app_id = app.get("id", 0)
            
            # Check if this is a known protocol
            for protocol_key, protocol_info in self.KNOWN_PROTOCOLS.items():
                if app_id in protocol_info.get("app_ids", []):
                    exposures.append(ProtocolExposure(
                        protocol_name=protocol_info["name"],
                        exposure_usd=0,  # Would need deeper analysis
                        risk_level=protocol_info["risk_level"],
                        description=protocol_info["description"],
                        contracts=[str(app_id)]
                    ))
        
        # If no protocol exposure found, add a note
        if not exposures and apps:
            exposures.append(ProtocolExposure(
                protocol_name="Unknown Apps",
                exposure_usd=0,
                risk_level=RiskLevel.MEDIUM,
                description=f"Opted into {len(apps)} unknown applications"
            ))
        
        return exposures
    
    def _calculate_concentration_risks(
        self,
        assets: List[AssetHolding],
        total_value: float
    ) -> List[str]:
        """Calculate concentration risks in the portfolio."""
        risks = []
        
        if total_value <= 0:
            risks.append("Portfolio has no measurable value")
            return risks
        
        # Check single asset concentration
        for asset in assets:
            if asset.value_usd:
                concentration = (asset.value_usd / total_value) * 100
                if concentration > 70:
                    risks.append(
                        f"High concentration in {asset.asset_name}: {concentration:.1f}%"
                    )
                elif concentration > 50:
                    risks.append(
                        f"Moderate concentration in {asset.asset_name}: {concentration:.1f}%"
                    )
        
        # Check number of assets
        if len(assets) < 3:
            risks.append("Limited diversification - consider adding more assets")
        
        # Check for high-risk assets
        high_risk_assets = [a for a in assets if a.risk_score > 40]
        if high_risk_assets:
            total_risk_exposure = sum(a.value_usd or 0 for a in high_risk_assets)
            if total_value > 0:
                risk_pct = (total_risk_exposure / total_value) * 100
                if risk_pct > 30:
                    risks.append(
                        f"High exposure to risky assets: {risk_pct:.1f}%"
                    )
        
        return risks
    
    def _calculate_risk_score(
        self,
        assets: List[AssetHolding],
        protocols: List[ProtocolExposure],
        concentration_risks: List[str]
    ) -> int:
        """Calculate overall portfolio risk score."""
        score = 0
        
        # Asset risk contribution
        for asset in assets:
            weight = asset.risk_score / 100
            score += weight * 20  # Max 20 points per asset type
        
        # Protocol risk contribution
        for protocol in protocols:
            if protocol.risk_level == RiskLevel.HIGH:
                score += 15
            elif protocol.risk_level == RiskLevel.MEDIUM:
                score += 10
            elif protocol.risk_level == RiskLevel.LOW:
                score += 5
        
        # Concentration risk contribution
        score += len(concentration_risks) * 5
        
        return min(100, int(score))
    
    def _determine_risk_level(self, risk_score: int) -> RiskLevel:
        """Determine risk level from score."""
        if risk_score >= 70:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _generate_recommendations(
        self,
        analysis: PortfolioAnalysis,
        address: str
    ) -> List[str]:
        """Generate AI-powered recommendations."""
        recommendations = []
        
        # Basic recommendations based on analysis
        if analysis.risk_score > 60:
            recommendations.append(
                "Consider reducing exposure to high-risk assets"
            )
        
        if len(analysis.concentration_risks) > 2:
            recommendations.append(
                "Diversify your portfolio across more asset types"
            )
        
        # Check for stablecoin allocation
        stablecoin_value = sum(
            a.value_usd or 0 for a in analysis.asset_breakdown
            if a.asset_type == "stablecoin"
        )
        if analysis.total_value_usd > 0:
            stable_pct = (stablecoin_value / analysis.total_value_usd) * 100
            if stable_pct < 10:
                recommendations.append(
                    "Consider adding stablecoins for stability (target 10-20%)"
                )
        
        # Check for ALGO allocation
        algo_value = sum(
            a.value_usd or 0 for a in analysis.asset_breakdown
            if a.asset_name == "ALGO"
        )
        if analysis.total_value_usd > 0:
            algo_pct = (algo_value / analysis.total_value_usd) * 100
            if algo_pct < 20:
                recommendations.append(
                    "Consider increasing ALGO holdings for staking rewards"
                )
        
        # Add AI-powered recommendations if configured
        if settings.OPENROUTER_API_KEY:
            ai_recs = await self._get_ai_recommendations(analysis)
            recommendations.extend(ai_recs)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def _get_ai_recommendations(
        self,
        analysis: PortfolioAnalysis
    ) -> List[str]:
        """Get AI-powered recommendations using OpenRouter."""
        try:
            import httpx
            import json
            
            prompt = f"""You are a DeFi portfolio advisor. Analyze this Algorand portfolio and provide 2-3 specific recommendations.

Portfolio Summary:
- Total Value: ${analysis.total_value_usd:.2f}
- Risk Score: {analysis.risk_score}/100
- Risk Level: {analysis.risk_level.value}
- Number of Assets: {len(analysis.asset_breakdown)}
- Concentration Risks: {', '.join(analysis.concentration_risks[:3])}

Provide recommendations as a JSON array of strings:
["recommendation 1", "recommendation 2", "recommendation 3"]

Return ONLY the JSON array."""

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7,
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI recommendations failed: {e}")
            return []


# Singleton instance
_portfolio_analyzer: Optional[PortfolioAnalyzer] = None


def get_portfolio_analyzer() -> PortfolioAnalyzer:
    """Get or create the portfolio analyzer singleton instance."""
    global _portfolio_analyzer
    if _portfolio_analyzer is None:
        _portfolio_analyzer = PortfolioAnalyzer()
    return _portfolio_analyzer
