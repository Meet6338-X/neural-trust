"""
Chatbot API Routes.
Provides endpoints for AI-powered chat and transaction alerts.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.chatbot_service import get_chatbot_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chatbot", tags=["chatbot"])


# ==================== Request Models ====================

class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context data")


class AnalyzeTransactionChatRequest(BaseModel):
    """Request model for transaction analysis via chat."""
    transaction_data: Dict[str, Any] = Field(..., description="Transaction details to analyze")


class CreateAlertRequest(BaseModel):
    """Request model for creating alerts."""
    alert_type: str = Field(..., description="Type of alert (risk, suspicious, info, warning)")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    transaction_data: Dict[str, Any] = Field(..., description="Related transaction data")


class ParseCommandRequest(BaseModel):
    """Request model for parsing natural language commands."""
    command: str = Field(..., description="Natural language command")


# ==================== Chat Endpoints ====================

@router.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Send a message to the AI chatbot and get a response.
    
    The chatbot can help with:
    - Transaction analysis
    - Blockchain security questions
    - DeFi protocol explanations
    - Risk assessments
    - Portfolio management advice
    """
    service = get_chatbot_service()
    
    result = await service.chat(request.message, request.context)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Chat failed"))
    
    return result


@router.post("/analyze-transaction")
async def analyze_transaction_chat(request: AnalyzeTransactionChatRequest) -> Dict[str, Any]:
    """
    Analyze a transaction using the AI chatbot.
    
    Provides detailed analysis including:
    - Risk assessment
    - Potential concerns
    - Recommendations
    - Red flags to watch for
    """
    service = get_chatbot_service()
    
    result = await service.analyze_transaction_chat(request.transaction_data)
    
    return result


@router.get("/history")
async def get_conversation_history() -> List[Dict[str, Any]]:
    """Get the conversation history."""
    service = get_chatbot_service()
    return service.get_conversation_history()


@router.delete("/history")
async def clear_conversation() -> Dict[str, str]:
    """Clear the conversation history."""
    service = get_chatbot_service()
    service.clear_conversation()
    return {"message": "Conversation history cleared"}


@router.get("/quick-replies")
async def get_quick_replies(context: str = Query(default="general")) -> List[str]:
    """
    Get suggested quick replies based on context.
    
    Contexts: general, transaction, alert, portfolio
    """
    service = get_chatbot_service()
    return await service.get_quick_replies(context)


# ==================== Alert Endpoints ====================

@router.post("/alerts")
async def create_alert(request: CreateAlertRequest) -> Dict[str, Any]:
    """
    Create a new transaction alert.
    
    Alert types: risk, suspicious, info, warning
    Severity levels: low, medium, high, critical
    """
    service = get_chatbot_service()
    
    # Validate alert type
    valid_types = ["risk", "suspicious", "info", "warning"]
    if request.alert_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid alert type. Must be one of: {valid_types}"
        )
    
    # Validate severity
    valid_severities = ["low", "medium", "high", "critical"]
    if request.severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity. Must be one of: {valid_severities}"
        )
    
    alert = await service.create_alert(
        alert_type=request.alert_type,
        severity=request.severity,
        title=request.title,
        message=request.message,
        transaction_data=request.transaction_data
    )
    
    return alert.to_dict()


@router.get("/alerts")
async def get_alerts(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100)
) -> List[Dict[str, Any]]:
    """
    Get all alerts.
    
    Set unread_only=true to get only unread alerts.
    """
    service = get_chatbot_service()
    return await service.get_alerts(unread_only=unread_only, limit=limit)


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str) -> Dict[str, Any]:
    """Mark an alert as read."""
    service = get_chatbot_service()
    
    success = await service.mark_alert_read(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert marked as read", "alert_id": alert_id}


@router.delete("/alerts")
async def clear_alerts() -> Dict[str, Any]:
    """Clear all alerts."""
    service = get_chatbot_service()
    count = await service.clear_alerts()
    return {"message": f"Cleared {count} alerts"}


# ==================== Command Parsing Endpoints ====================

@router.post("/parse-command")
async def parse_command(request: ParseCommandRequest) -> Dict[str, Any]:
    """
    Parse a natural language command.
    
    Supported intents:
    - send: Send a transaction
    - check_balance: Check account balance
    - get_history: Get transaction history
    - analyze: Analyze a transaction
    - create_alert: Create an alert
    """
    service = get_chatbot_service()
    
    result = await service.process_natural_language_command(request.command)
    
    return result
