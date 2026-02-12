"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


# ============================================================================
# Vault Schemas
# ============================================================================

class VaultCreate(BaseModel):
    """Schema for creating a new vault."""
    risk_threshold: int = Field(
        ...,
        ge=0,
        le=100,
        description="Personal risk threshold (0-100)"
    )
    user_address: str = Field(
        ...,
        alias="wallet_address",  # <--- THIS IS THE FIX
        description="User's Algorand address"
    )


class VaultResponse(BaseModel):
    """Schema for vault response."""
    user_address: str
    risk_threshold: int
    current_risk_score: int
    is_frozen: bool
    created_at: Optional[datetime] = None


class VaultUpdate(BaseModel):
    """Schema for updating vault settings."""
    risk_threshold: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="New risk threshold"
    )


# ============================================================================
# Risk Analysis Schemas
# ============================================================================

class TransactionData(BaseModel):
    """Schema for transaction data to analyze."""
    type: str = Field(
        ...,
        description="Transaction type (e.g., transfer, swap, stake)"
    )
    amount: float = Field(
        ...,
        ge=0,
        description="Amount in ALGO"
    )
    sender: str = Field(
        ...,
        description="Sender's Algorand address"
    )
    recipient: str = Field(
        ...,
        description="Recipient's Algorand address"
    )
    timestamp: Optional[str] = Field(
        None,
        description="Transaction timestamp"
    )
    protocol: Optional[str] = Field(
        None,
        description="Protocol name if applicable"
    )
    additional_context: Optional[dict] = Field(
        None,
        description="Additional context for analysis"
    )


class RiskAnalysisResponse(BaseModel):
    """Schema for risk analysis response."""
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score (0-100)"
    )
    recommendation: Literal["ALLOW", "WARN", "BLOCK"] = Field(
        ...,
        description="AI recommendation"
    )
    reasoning: str = Field(
        ...,
        description="Explanation of the risk assessment"
    )
    model_used: str = Field(
        ...,
        description="AI model used for analysis"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level (0-1)"
    )


class BatchAnalysisRequest(BaseModel):
    """Schema for batch transaction analysis."""
    transactions: list[TransactionData] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of transactions to analyze"
    )


class BatchAnalysisResponse(BaseModel):
    """Schema for batch analysis response."""
    results: list[RiskAnalysisResponse]


# ============================================================================
# Freeze/Unfreeze Schemas
# ============================================================================

class FreezeRequest(BaseModel):
    """Schema for freezing a vault."""
    user_address: str = Field(
        ...,
        description="User's Algorand address to freeze"
    )
    reason: Optional[str] = Field(
        None,
        description="Reason for freezing"
    )


class UnfreezeRequest(BaseModel):
    """Schema for unfreezing a vault."""
    user_address: str = Field(
        ...,
        description="User's Algorand address to unfreeze"
    )


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditEntry(BaseModel):
    """Schema for audit log entry."""
    id: int
    user_address: str
    risk_score: int
    decision: int = Field(
        ...,
        description="0=BLOCKED, 1=ALLOWED, 2=FROZEN"
    )
    timestamp: int


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    entries: list[AuditEntry]
    total: int


# ============================================================================
# Health Check Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    blockchain_connected: bool
    ai_configured: bool
    database_connected: bool


class ModelInfoResponse(BaseModel):
    """Schema for AI model information."""
    model: str
    provider: str
    api_base: str
    configured: bool


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ============================================================================
# Transaction Execution Schemas
# ============================================================================

class ExecuteTransactionRequest(BaseModel):
    """Schema for executing a transaction with risk check."""
    user_address: str
    action_type: str
    transaction_data: Optional[TransactionData] = None


class ExecuteTransactionResponse(BaseModel):
    """Schema for transaction execution response."""
    allowed: bool
    risk_score: Optional[int] = None
    recommendation: Optional[str] = None
    audit_entry_id: Optional[int] = None


# ============================================================================
# Contract Audit Schemas
# ============================================================================

class ContractAuditRequest(BaseModel):
    """Schema for contract audit request."""
    code: str = Field(
        ...,
        description="The smart contract source code to audit"
    )
    language: str = Field(
        default="teal",
        description="Contract language (teal, python, pyteal)"
    )
    check_types: list[str] = Field(
        default=["security", "optimization", "best_practice"],
        description="Types of checks to perform"
    )


class AuditFindingResponse(BaseModel):
    """Schema for a single audit finding."""
    type: str = Field(
        ...,
        description="Type of finding (security, optimization, best_practice)"
    )
    severity: str = Field(
        ...,
        description="Severity level (critical, high, medium, low, info)"
    )
    title: str = Field(..., description="Brief title of the finding")
    description: str = Field(..., description="Detailed description")
    line_number: Optional[int] = Field(None, description="Line number if applicable")
    code_snippet: Optional[str] = Field(None, description="Related code snippet")
    recommendation: str = Field(..., description="How to fix the issue")
    references: list[str] = Field(
        default_factory=list,
        description="Reference links for more information"
    )


class ContractAuditResponse(BaseModel):
    """Schema for contract audit response."""
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk score (0-100)"
    )
    findings: list[AuditFindingResponse] = Field(
        ...,
        description="List of audit findings"
    )
    summary: str = Field(..., description="Human-readable summary")
    total_issues: int = Field(..., description="Total number of issues found")
    critical_count: int = Field(..., description="Number of critical issues")
    high_count: int = Field(..., description="Number of high severity issues")
    medium_count: int = Field(..., description="Number of medium severity issues")
    low_count: int = Field(..., description="Number of low severity issues")
    lines_analyzed: int = Field(..., description="Number of lines analyzed")
    analysis_time_ms: float = Field(..., description="Analysis time in milliseconds")


# ============================================================================
# Address Reputation Schemas
# ============================================================================

class ReputationScore(BaseModel):
    """Schema for address reputation score."""
    address: str = Field(..., description="Algorand address")
    trust_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Trust score (0-100)"
    )
    risk_level: str = Field(
        ...,
        description="Risk level (low, medium, high, critical)"
    )
    first_seen: Optional[str] = Field(None, description="First seen timestamp")
    last_active: Optional[str] = Field(None, description="Last active timestamp")
    total_transactions: int = Field(0, description="Total transaction count")
    total_volume_algo: float = Field(0, description="Total volume in ALGO")
    flags: list[str] = Field(default_factory=list, description="Risk flags")
    labels: list[str] = Field(default_factory=list, description="Address labels")
    risk_factors: list[str] = Field(default_factory=list, description="Risk factors")


class AddressHistoryEntry(BaseModel):
    """Schema for address history entry."""
    timestamp: str
    action: str
    risk_score: int
    details: Optional[str] = None


class AddressHistoryResponse(BaseModel):
    """Schema for address history response."""
    address: str
    entries: list[AddressHistoryEntry]
    total: int


# ============================================================================
# Portfolio Analysis Schemas
# ============================================================================

class AssetHolding(BaseModel):
    """Schema for asset holding."""
    asset_id: int
    asset_name: str
    amount: float
    value_usd: Optional[float] = None
    risk_score: int = 0


class ProtocolExposure(BaseModel):
    """Schema for protocol exposure."""
    protocol_name: str
    exposure_usd: float
    risk_level: str
    description: Optional[str] = None


class PortfolioAnalysisRequest(BaseModel):
    """Schema for portfolio analysis request."""
    address: str = Field(..., description="Algorand address to analyze")
    include_recommendations: bool = Field(
        default=True,
        description="Include AI recommendations"
    )


class PortfolioAnalysisResponse(BaseModel):
    """Schema for portfolio analysis response."""
    address: str
    total_value_usd: float
    risk_score: int
    risk_level: str
    asset_breakdown: list[AssetHolding]
    protocol_exposure: list[ProtocolExposure]
    concentration_risks: list[str]
    recommendations: list[str]
    analysis_time_ms: float


# ============================================================================
# Transaction Simulation Schemas
# ============================================================================

class SimulationRequest(BaseModel):
    """Schema for transaction simulation request."""
    sender: str = Field(..., description="Sender address")
    receiver: Optional[str] = Field(None, description="Receiver address")
    amount: Optional[float] = Field(None, description="Amount in ALGO")
    app_id: Optional[int] = Field(None, description="Application ID for app calls")
    app_args: Optional[list[str]] = Field(None, description="Application arguments")
    simulation_type: str = Field(
        default="payment",
        description="Type of simulation (payment, app_call, asset_transfer)"
    )


class SimulationResult(BaseModel):
    """Schema for transaction simulation result."""
    success: bool
    estimated_fee: int
    estimated_rounds: int
    warnings: list[str]
    state_changes: list[dict]
    logs: list[str]


# ============================================================================
# Alert Schemas
# ============================================================================

class AlertSubscription(BaseModel):
    """Schema for alert subscription."""
    address: str
    alert_types: list[str] = Field(
        default_factory=lambda: ["risk_change", "transaction", "portfolio"],
        description="Types of alerts to subscribe to"
    )
    threshold: Optional[int] = Field(
        None,
        description="Risk score threshold for alerts"
    )


class RiskAlert(BaseModel):
    """Schema for a risk alert."""
    alert_id: str
    alert_type: str
    address: str
    risk_score: int
    message: str
    timestamp: str
    details: Optional[dict] = None
