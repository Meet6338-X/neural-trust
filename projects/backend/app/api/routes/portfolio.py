"""
Portfolio Analysis API Routes.

Endpoints for portfolio risk analysis and recommendations.
"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse,
    AssetHolding,
    ProtocolExposure,
)
from app.services.portfolio_analyzer import get_portfolio_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolio", tags=["Portfolio Analysis"])


@router.post("/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """
    Analyze a portfolio for risk exposure.
    
    This endpoint analyzes the on-chain portfolio of an Algorand address
    and returns a comprehensive risk assessment with recommendations.
    
    - **address**: The Algorand address to analyze
    - **include_recommendations**: Whether to include AI recommendations
    """
    try:
        analyzer = get_portfolio_analyzer()
        result = await analyzer.analyze_portfolio(
            address=request.address,
            include_recommendations=request.include_recommendations
        )
        
        return PortfolioAnalysisResponse(
            address=result.address,
            total_value_usd=result.total_value_usd,
            risk_score=result.risk_score,
            risk_level=result.risk_level.value,
            asset_breakdown=[
                AssetHolding(
                    asset_id=a.asset_id,
                    asset_name=a.asset_name,
                    amount=a.amount,
                    value_usd=a.value_usd,
                    risk_score=a.risk_score
                )
                for a in result.asset_breakdown
            ],
            protocol_exposure=[
                ProtocolExposure(
                    protocol_name=p.protocol_name,
                    exposure_usd=p.exposure_usd,
                    risk_level=p.risk_level.value,
                    description=p.description
                )
                for p in result.protocol_exposure
            ],
            concentration_risks=result.concentration_risks,
            recommendations=result.recommendations,
            analysis_time_ms=result.analysis_time_ms
        )
        
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio analysis failed: {str(e)}"
        )


@router.get("/{address}/summary")
async def get_portfolio_summary(address: str):
    """
    Get a quick summary of a portfolio.
    
    Returns basic portfolio information without detailed analysis.
    
    - **address**: The Algorand address
    """
    try:
        analyzer = get_portfolio_analyzer()
        result = await analyzer.analyze_portfolio(
            address=address,
            include_recommendations=False
        )
        
        return {
            "address": address,
            "total_value_usd": result.total_value_usd,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "asset_count": len(result.asset_breakdown),
            "protocol_count": len(result.protocol_exposure),
            "has_concentration_risks": len(result.concentration_risks) > 0
        }
        
    except Exception as e:
        logger.error(f"Portfolio summary failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio summary failed: {str(e)}"
        )


@router.get("/{address}/assets")
async def get_portfolio_assets(address: str):
    """
    Get the list of assets in a portfolio.
    
    - **address**: The Algorand address
    """
    try:
        analyzer = get_portfolio_analyzer()
        result = await analyzer.analyze_portfolio(
            address=address,
            include_recommendations=False
        )
        
        return {
            "address": address,
            "assets": [
                {
                    "asset_id": a.asset_id,
                    "name": a.asset_name,
                    "amount": a.amount,
                    "value_usd": a.value_usd,
                    "risk_score": a.risk_score,
                    "type": a.asset_type
                }
                for a in result.asset_breakdown
            ],
            "total_assets": len(result.asset_breakdown)
        }
        
    except Exception as e:
        logger.error(f"Asset listing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Asset listing failed: {str(e)}"
        )


@router.get("/{address}/protocols")
async def get_protocol_exposure(address: str):
    """
    Get protocol exposure for a portfolio.
    
    - **address**: The Algorand address
    """
    try:
        analyzer = get_portfolio_analyzer()
        result = await analyzer.analyze_portfolio(
            address=address,
            include_recommendations=False
        )
        
        return {
            "address": address,
            "protocols": [
                {
                    "name": p.protocol_name,
                    "exposure_usd": p.exposure_usd,
                    "risk_level": p.risk_level.value,
                    "description": p.description
                }
                for p in result.protocol_exposure
            ],
            "total_protocols": len(result.protocol_exposure)
        }
        
    except Exception as e:
        logger.error(f"Protocol exposure analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Protocol exposure analysis failed: {str(e)}"
        )


@router.get("/{address}/risks")
async def get_portfolio_risks(address: str):
    """
    Get concentration and risk factors for a portfolio.
    
    - **address**: The Algorand address
    """
    try:
        analyzer = get_portfolio_analyzer()
        result = await analyzer.analyze_portfolio(
            address=address,
            include_recommendations=False
        )
        
        return {
            "address": address,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "concentration_risks": result.concentration_risks,
            "high_risk_assets": [
                {
                    "name": a.asset_name,
                    "risk_score": a.risk_score,
                    "value_usd": a.value_usd
                }
                for a in result.asset_breakdown
                if a.risk_score > 30
            ]
        }
        
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Risk analysis failed: {str(e)}"
        )
