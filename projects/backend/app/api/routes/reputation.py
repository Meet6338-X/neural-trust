"""
Address Reputation API Routes.

Endpoints for address trust scoring and risk assessment.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    ReputationScore,
    AddressHistoryResponse,
    AddressHistoryEntry,
)
from app.services.reputation_service import get_reputation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reputation", tags=["Address Reputation"])


@router.get("/{address}", response_model=ReputationScore)
async def get_address_reputation(address: str):
    """
    Get reputation score for an Algorand address.
    
    This endpoint analyzes the on-chain behavior of an address
    and returns a trust score with risk assessment.
    
    - **address**: The Algorand address to analyze
    """
    try:
        service = get_reputation_service()
        reputation = await service.get_reputation(address)
        
        return ReputationScore(
            address=reputation.address,
            trust_score=reputation.trust_score,
            risk_level=reputation.risk_level.value,
            first_seen=str(reputation.first_seen) if reputation.first_seen else None,
            last_active=str(reputation.last_active) if reputation.last_active else None,
            total_transactions=reputation.total_transactions,
            total_volume_algo=reputation.total_volume_algo,
            flags=reputation.flags,
            labels=reputation.labels,
            risk_factors=reputation.risk_factors
        )
        
    except Exception as e:
        logger.error(f"Failed to get reputation for {address}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reputation analysis failed: {str(e)}"
        )


@router.get("/{address}/history", response_model=AddressHistoryResponse)
async def get_address_history(
    address: str,
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get transaction history with risk annotations for an address.
    
    - **address**: The Algorand address
    - **limit**: Maximum number of entries to return
    """
    try:
        service = get_reputation_service()
        reputation = await service.get_reputation(address)
        
        # Create history entries from reputation data
        entries = []
        
        # Add recent activity summary
        if reputation.total_transactions > 0:
            entries.append(AddressHistoryEntry(
                timestamp="recent",
                action="analysis_complete",
                risk_score=reputation.trust_score,
                details=f"Analyzed {reputation.total_transactions} transactions"
            ))
        
        # Add risk factor entries
        for factor in reputation.risk_factors[:5]:
            entries.append(AddressHistoryEntry(
                timestamp="analysis",
                action="risk_factor_detected",
                risk_score=0,
                details=factor
            ))
        
        return AddressHistoryResponse(
            address=address,
            entries=entries,
            total=len(entries)
        )
        
    except Exception as e:
        logger.error(f"Failed to get history for {address}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"History retrieval failed: {str(e)}"
        )


@router.post("/batch", response_model=dict)
async def batch_get_reputation(addresses: List[str]):
    """
    Get reputation scores for multiple addresses.
    
    - **addresses**: List of Algorand addresses to analyze
    """
    if len(addresses) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 addresses per batch request"
        )
    
    try:
        service = get_reputation_service()
        results = await service.batch_get_reputation(addresses)
        
        return {
            "results": {
                addr: ReputationScore(
                    address=rep.address,
                    trust_score=rep.trust_score,
                    risk_level=rep.risk_level.value,
                    first_seen=str(rep.first_seen) if rep.first_seen else None,
                    last_active=str(rep.last_active) if rep.last_active else None,
                    total_transactions=rep.total_transactions,
                    total_volume_algo=rep.total_volume_algo,
                    flags=rep.flags,
                    labels=rep.labels,
                    risk_factors=rep.risk_factors
                ).model_dump()
                for addr, rep in results.items()
            },
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Batch reputation check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )


@router.get("/{address}/quick-check")
async def quick_risk_check(
    address: str,
    threshold: int = Query(default=50, ge=0, le=100)
):
    """
    Quick risk check for an address.
    
    Returns a simple pass/fail assessment based on the threshold.
    
    - **address**: The Algorand address to check
    - **threshold**: Minimum trust score required (default: 50)
    """
    try:
        service = get_reputation_service()
        result = await service.check_address_risk(address, threshold)
        return result
        
    except Exception as e:
        logger.error(f"Quick risk check failed for {address}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Risk check failed: {str(e)}"
        )


@router.get("/{address}/patterns")
async def get_behavior_patterns(address: str):
    """
    Get identified behavior patterns for an address.
    
    - **address**: The Algorand address to analyze
    """
    try:
        service = get_reputation_service()
        reputation = await service.get_reputation(address)
        
        return {
            "address": address,
            "patterns": reputation.behavior_patterns,
            "labels": reputation.labels,
            "interpretation": _interpret_patterns(reputation.behavior_patterns)
        }
        
    except Exception as e:
        logger.error(f"Pattern analysis failed for {address}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pattern analysis failed: {str(e)}"
        )


def _interpret_patterns(patterns: List[str]) -> str:
    """Generate human-readable interpretation of behavior patterns."""
    if not patterns:
        return "No significant behavior patterns detected."
    
    interpretations = {
        "inactive": "This address has no recent activity.",
        "primarily_payments": "This address mainly sends and receives ALGO payments.",
        "app_user": "This address frequently interacts with smart contracts.",
        "asset_trader": "This address is active in asset trading.",
        "active": "This is an actively used address.",
        "moderate_activity": "This address has moderate activity levels.",
        "low_activity": "This address has low transaction activity.",
    }
    
    parts = [interpretations.get(p, f"Pattern: {p}") for p in patterns]
    return " ".join(parts)
