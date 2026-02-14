"""
API routes for risk analysis endpoints with dynamic risk scoring.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from app.models.schemas import (
    TransactionData,
    RiskAnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ModelInfoResponse,
)
from app.models.database import get_db
from app.services.ai_engine import get_ai_engine, AIRiskEngine
from app.services.simplified_analysis_service import get_simplified_analysis_service, SimplifiedAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


# ==================== Simplified Analysis Models ====================

class SimplifiedAnalysisRequest(BaseModel):
    """Request for simplified analysis - just an address."""
    address: str = Field(..., description="Algorand address to analyze")


class SimplifiedAnalysisResponse(BaseModel):
    """Comprehensive analysis response from single address input."""
    address: str
    risk_score: int
    risk_level: str
    recommendation: str
    funds: dict
    transaction_summary: dict
    risk_factors: dict
    flags: List[dict]
    suggestions: List[str]
    reputation: dict
    pattern_score: int
    analysis_timestamp: str


# ==================== Enhanced Response Models ====================

class DynamicRiskAnalysisResponse(BaseModel):
    """Enhanced risk analysis response with historical context."""
    risk_score: int = Field(..., description="Current transaction risk score (0-100)")
    cumulative_risk_score: int = Field(..., description="Cumulative risk including history")
    recommendation: str = Field(..., description="ALLOW, WARN, or BLOCK")
    reasoning: str = Field(..., description="Explanation of the assessment")
    model_used: str = Field(..., description="AI model used")
    confidence: float = Field(..., description="Confidence level (0-1)")
    historical_context: Optional[dict] = Field(None, description="Historical data summary")
    risk_factors: Optional[dict] = Field(None, description="Risk factor breakdown")
    reputation: Optional[dict] = Field(None, description="Address reputation")


class RiskProfileResponse(BaseModel):
    """Response for address risk profile."""
    address: str
    reputation: dict
    transaction_statistics: dict
    risk_statistics: dict
    patterns: dict
    risk_factors: dict
    pattern_score: int
    recent_transactions: List[dict]
    recent_analyses: List[dict]


class RiskFactorsResponse(BaseModel):
    """Response for risk factors breakdown."""
    address: str
    risk_factors: dict
    pattern_score: int
    cumulative_score: int


# ==================== Endpoints ====================

@router.post("/risk", response_model=DynamicRiskAnalysisResponse)
async def analyze_risk(
    transaction_data: TransactionData,
    db: AsyncSession = Depends(get_db),
    ai_engine: AIRiskEngine = Depends(get_ai_engine)
) -> DynamicRiskAnalysisResponse:
    """
    Analyze a transaction for risk using AI with historical context.
    
    This endpoint now incorporates:
    - Transaction history for the sender address
    - Previous risk analysis scores
    - Behavioral pattern analysis
    - Cumulative risk scoring
    
    Args:
        transaction_data: Transaction details to analyze
        db: Database session for history lookup
        ai_engine: AI engine dependency
    
    Returns:
        Dynamic risk analysis with cumulative scoring
    """
    try:
        logger.info(f"Analyzing transaction: {transaction_data.type} - {transaction_data.amount} ALGO from {transaction_data.sender}")
        
        # Convert to dict for AI engine
        tx_dict = transaction_data.model_dump()
        
        # Get AI analysis with historical context
        result = await ai_engine.analyze_transaction(tx_dict, db=db)
        
        return DynamicRiskAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.post("/risk/simple", response_model=RiskAnalysisResponse)
async def analyze_risk_simple(
    transaction_data: TransactionData,
    ai_engine: AIRiskEngine = Depends(get_ai_engine)
) -> RiskAnalysisResponse:
    """
    Simple risk analysis without historical context (for backward compatibility).
    
    Args:
        transaction_data: Transaction details to analyze
        ai_engine: AI engine dependency
    
    Returns:
        Basic risk analysis result
    """
    try:
        logger.info(f"Simple analysis: {transaction_data.type} - {transaction_data.amount} ALGO")
        
        # Convert to dict for AI engine
        tx_dict = transaction_data.model_dump()
        
        # Get simple AI analysis
        result = await ai_engine.analyze_transaction_simple(tx_dict)
        
        return RiskAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.post("/simple", response_model=SimplifiedAnalysisResponse)
async def simplified_analysis(
    request: SimplifiedAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    service: SimplifiedAnalysisService = Depends(get_simplified_analysis_service)
) -> SimplifiedAnalysisResponse:
    """
    Simplified analysis endpoint - just provide an address.
    
    This endpoint takes a single Algorand address and returns a comprehensive
    risk analysis including:
    - Current funds (ALGO balance and assets)
    - Transaction summary
    - Risk factors and score
    - Flags and warnings
    - Actionable suggestions
    - Reputation data
    
    Minimum input, maximum output!
    """
    try:
        logger.info(f"Simplified analysis requested for: {request.address}")
        
        result = await service.analyze_address(request.address, db=db)
        
        return SimplifiedAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Simplified analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/batch", response_model=BatchAnalysisResponse)
async def batch_analyze(
    request: BatchAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    ai_engine: AIRiskEngine = Depends(get_ai_engine)
) -> BatchAnalysisResponse:
    """
    Analyze multiple transactions in batch with historical context.
    
    Args:
        request: Batch analysis request with transactions
        db: Database session for history lookup
        ai_engine: AI engine dependency
    
    Returns:
        Batch analysis results
    """
    try:
        logger.info(f"Batch analyzing {len(request.transactions)} transactions")
        
        # Convert to list of dicts
        transactions = [tx.model_dump() for tx in request.transactions]
        
        # Get batch analysis with history
        results = await ai_engine.batch_analyze(transactions, db=db)
        
        return BatchAnalysisResponse(results=results)
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/profile/{address}", response_model=RiskProfileResponse)
async def get_risk_profile(
    address: str,
    db: AsyncSession = Depends(get_db),
    ai_engine: AIRiskEngine = Depends(get_ai_engine)
) -> RiskProfileResponse:
    """
    Get comprehensive risk profile for an address.
    
    Returns:
    - Reputation score and tier
    - Transaction statistics
    - Risk analysis history
    - Behavioral patterns
    - Risk factor breakdown
    """
    try:
        logger.info(f"Getting risk profile for: {address}")
        
        profile = await ai_engine.get_address_risk_profile(address, db=db)
        
        if "error" in profile:
            raise HTTPException(status_code=404, detail=profile["error"])
        
        return RiskProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get risk profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk profile: {str(e)}")


@router.get("/history/{address}")
async def get_analysis_history(
    address: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get risk analysis history for an address.
    
    Args:
        address: The address to query
        limit: Maximum number of analyses to return
        db: Database session
    
    Returns:
        List of previous risk analyses with statistics
    """
    try:
        from app.services.transaction_history_service import get_transaction_history_service
        
        history_service = get_transaction_history_service()
        result = await history_service.get_risk_analysis_history(address, limit=limit, db=db)
        
        return result
    except Exception as e:
        logger.error(f"Failed to get analysis history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis history: {str(e)}")


@router.get("/factors/{address}", response_model=RiskFactorsResponse)
async def get_risk_factors(
    address: str,
    db: AsyncSession = Depends(get_db)
) -> RiskFactorsResponse:
    """
    Get detailed risk factor breakdown for an address.
    
    Returns:
    - Individual risk factor scores
    - Pattern analysis score
    - Cumulative risk score
    """
    try:
        from app.services.transaction_history_service import get_transaction_history_service
        from app.services.risk_calculator_service import get_risk_calculator_service
        
        logger.info(f"Calculating risk factors for: {address}")
        
        history_service = get_transaction_history_service()
        risk_calculator = get_risk_calculator_service()
        
        # Get data
        tx_history = await history_service.get_address_transaction_history(address, limit=50, db=db)
        risk_history = await history_service.get_risk_analysis_history(address, limit=50, db=db)
        patterns = await history_service.calculate_transaction_patterns(address, db=db)
        stats = await history_service.get_address_statistics(address, db=db)
        
        # Calculate factors
        risk_factors = risk_calculator.calculate_risk_factors(tx_history, risk_history, patterns)
        pattern_score = risk_calculator.calculate_pattern_score(risk_factors)
        
        # Calculate cumulative score
        reputation = stats.get("reputation", {})
        cumulative = risk_calculator.calculate_cumulative_score(
            pattern_score, risk_factors, reputation.get("score", 50)
        )
        
        return RiskFactorsResponse(
            address=address,
            risk_factors=risk_factors,
            pattern_score=pattern_score,
            cumulative_score=cumulative
        )
    except Exception as e:
        logger.error(f"Failed to get risk factors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk factors: {str(e)}")


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(
    ai_engine: AIRiskEngine = Depends(get_ai_engine)
) -> ModelInfoResponse:
    """
    Get information about the AI model being used.
    
    Args:
        ai_engine: AI engine dependency
    
    Returns:
        Model information
    """
    try:
        info = await ai_engine.get_model_info()
        return ModelInfoResponse(**info)
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.get("/transactions/{address}")
async def get_transaction_history(
    address: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get transaction history for an address.
    
    Args:
        address: The address to query
        limit: Maximum number of transactions to return
        db: Database session
    
    Returns:
        Transaction history with statistics
    """
    try:
        from app.services.transaction_history_service import get_transaction_history_service
        
        history_service = get_transaction_history_service()
        result = await history_service.get_address_transaction_history(address, limit=limit, db=db)
        
        return result
    except Exception as e:
        logger.error(f"Failed to get transaction history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transaction history: {str(e)}")
