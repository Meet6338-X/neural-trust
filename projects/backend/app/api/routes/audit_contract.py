"""
Contract Audit API Routes.

Endpoints for smart contract security analysis.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ContractAuditRequest,
    ContractAuditResponse,
    AuditFindingResponse,
)
from app.services.contract_auditor import get_contract_auditor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit/contract", tags=["Contract Audit"])


@router.post("", response_model=ContractAuditResponse)
async def audit_contract(request: ContractAuditRequest):
    """
    Audit a smart contract for security vulnerabilities and issues.
    
    This endpoint analyzes TEAL or Python/PyTeal smart contract code
    for security vulnerabilities, optimization opportunities, and
    best practice violations.
    
    - **code**: The smart contract source code
    - **language**: Contract language (teal, python, pyteal)
    - **check_types**: Types of checks to perform (security, optimization, best_practice)
    """
    try:
        auditor = get_contract_auditor()
        result = await auditor.audit_contract(
            code=request.code,
            language=request.language,
            check_types=request.check_types
        )
        
        findings = [
            AuditFindingResponse(
                type=f.type.value,
                severity=f.severity.value,
                title=f.title,
                description=f.description,
                line_number=f.line_number,
                code_snippet=f.code_snippet,
                recommendation=f.recommendation,
                references=f.references
            )
            for f in result.findings
        ]
        
        return ContractAuditResponse(
            risk_score=result.risk_score,
            findings=findings,
            summary=result.summary,
            total_issues=result.total_issues,
            critical_count=result.critical_count,
            high_count=result.high_count,
            medium_count=result.medium_count,
            low_count=result.low_count,
            lines_analyzed=result.lines_analyzed,
            analysis_time_ms=result.analysis_time_ms
        )
        
    except Exception as e:
        logger.error(f"Contract audit failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Contract audit failed: {str(e)}"
        )


@router.get("/patterns", response_model=List[dict])
async def get_vulnerability_patterns():
    """
    Get a list of vulnerability patterns that the auditor checks for.
    
    Returns information about the types of vulnerabilities and issues
    that the contract auditor can detect.
    """
    return [
        {
            "name": "reentrancy",
            "severity": "critical",
            "description": "State changes after external calls may allow reentrancy attacks",
            "detection": "Pattern matching for callsub/pop sequences"
        },
        {
            "name": "integer_overflow",
            "severity": "high",
            "description": "Arithmetic operations without bounds checking",
            "detection": "Pattern matching for arithmetic operations"
        },
        {
            "name": "unprotected_access",
            "severity": "high",
            "description": "State can be modified without proper access control",
            "detection": "Missing sender verification before state changes"
        },
        {
            "name": "front_running",
            "severity": "medium",
            "description": "Transaction ordering may be exploitable",
            "detection": "Analysis of group size and application ID checks"
        },
        {
            "name": "unbounded_loop",
            "severity": "high",
            "description": "Loop without clear exit condition may cause out-of-gas",
            "detection": "Pattern matching for loop constructs"
        },
        {
            "name": "missing_version",
            "severity": "medium",
            "description": "Contract does not specify TEAL version pragma",
            "detection": "Missing #pragma version directive"
        },
        {
            "name": "missing_error_handling",
            "severity": "medium",
            "description": "No error handling or assertions found",
            "detection": "Missing err or assert opcodes"
        },
        {
            "name": "hardcoded_secrets",
            "severity": "medium",
            "description": "Found what appears to be hardcoded secrets or addresses",
            "detection": "Pattern matching for long string literals"
        },
        {
            "name": "unsafe_randomness",
            "severity": "high",
            "description": "Random function without VRF may be predictable",
            "detection": "Use of random without VRF verification"
        }
    ]
