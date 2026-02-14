"""
Chatbot Service for Transaction Alerts and AI-powered Chat.
Uses OpenRouter API with nvidia/nemotron-3-nano-30b-a3b model.
Includes RAG-style context injection for project-specific knowledge.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx

from app.config import settings
from app.services.rag_knowledge_base import get_rag_knowledge_base

logger = logging.getLogger(__name__)


class ChatMessage:
    """Represents a chat message."""
    
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.timestamp = timestamp or datetime.utcnow().timestamp()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class TransactionAlert:
    """Represents a transaction alert."""
    
    def __init__(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        transaction_data: Dict[str, Any],
        timestamp: Optional[float] = None,
        read: bool = False
    ):
        self.alert_id = alert_id
        self.alert_type = alert_type  # "risk", "suspicious", "info", "warning"
        self.severity = severity  # "low", "medium", "high", "critical"
        self.title = title
        self.message = message
        self.transaction_data = transaction_data
        self.timestamp = timestamp or datetime.utcnow().timestamp()
        self.read = read
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "transaction_data": self.transaction_data,
            "timestamp": self.timestamp,
            "read": self.read
        }


class ChatbotService:
    """
    AI-powered chatbot service for transaction assistance and alerts.
    """
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.AI_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.conversation_history: List[ChatMessage] = []
        self.alerts: List[TransactionAlert] = []
        self.max_history = 20
        self.rag_knowledge = get_rag_knowledge_base()
        
        # Initialize system prompt
        self.system_prompt = """You are ChainGuardian, an AI assistant specialized in blockchain security, DeFi transactions, and cryptocurrency analysis. You help users:

1. Analyze transactions for potential risks
2. Understand blockchain concepts and DeFi protocols
3. Get alerts about suspicious activities
4. Manage their crypto portfolio safely
5. Navigate Algorand and other blockchain networks

You have access to real-time transaction data and can provide risk assessments. Always be helpful, accurate, and security-focused.

When discussing transactions:
- Highlight potential security risks
- Explain complex DeFi concepts simply
- Provide actionable recommendations
- Warn about common scams and phishing attempts

Respond in a friendly but professional tone. If you're unsure about something, admit it and suggest verification methods."""

    async def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            user_message: The user's message
            context: Optional context data (e.g., current transaction, wallet info)
        
        Returns:
            Dictionary with response and metadata
        """
        # Add user message to history
        self.conversation_history.append(ChatMessage(
            role="user",
            content=user_message,
            metadata={"context": context} if context else {}
        ))
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        try:
            # Build messages for API
            messages = self._build_messages(user_message, context)
            
            # Call OpenRouter API
            response = await self._call_openrouter(messages)
            
            # Extract assistant response
            assistant_content = response["choices"][0]["message"]["content"]
            
            # Add to history
            self.conversation_history.append(ChatMessage(
                role="assistant",
                content=assistant_content
            ))
            
            return {
                "success": True,
                "response": assistant_content,
                "model": self.model,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error. Please try again.",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_messages(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Build messages array for API call with RAG context."""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Get RAG context for the user message
        rag_context = self.rag_knowledge.get_relevant_context(user_message)
        if rag_context:
            messages.append({
                "role": "system",
                "content": f"Relevant Knowledge Base:\n{rag_context}"
            })
        
        # Add conversation history
        for msg in self.conversation_history[:-1]:  # Exclude current message
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add context if provided
        if context:
            context_message = self._format_context(context)
            messages.append({
                "role": "system",
                "content": f"Current context:\n{context_message}"
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data for the AI."""
        parts = []
        
        if "wallet_address" in context:
            parts.append(f"Wallet: {context['wallet_address']}")
        
        if "current_transaction" in context:
            tx = context["current_transaction"]
            parts.append(f"Current Transaction: {json.dumps(tx, indent=2)}")
        
        if "portfolio" in context:
            parts.append(f"Portfolio: {json.dumps(context['portfolio'], indent=2)}")
        
        if "network" in context:
            parts.append(f"Network: {context['network']}")
        
        return "\n".join(parts)
    
    async def _call_openrouter(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://chainguardian.app",
            "X-Title": "ChainGuardian Chatbot",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def analyze_transaction_chat(
        self,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a transaction and provide chat-based insights.
        
        Args:
            transaction_data: Transaction details to analyze
        
        Returns:
            Analysis result with chat response
        """
        prompt = f"""Please analyze this transaction and provide your assessment:

Transaction Details:
{json.dumps(transaction_data, indent=2)}

Provide:
1. Risk Assessment (Low/Medium/High)
2. Potential Concerns
3. Recommendations
4. Any red flags to watch for"""

        return await self.chat(prompt, {"current_transaction": transaction_data})
    
    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        transaction_data: Dict[str, Any]
    ) -> TransactionAlert:
        """Create a new transaction alert."""
        import hashlib
        
        alert_id = hashlib.sha256(
            f"{alert_type}{title}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        alert = TransactionAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            transaction_data=transaction_data
        )
        
        self.alerts.append(alert)
        logger.info(f"Created alert: {alert_id} - {title}")
        
        return alert
    
    async def get_alerts(
        self,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all alerts."""
        alerts = self.alerts
        
        if unread_only:
            alerts = [a for a in alerts if not a.read]
        
        # Sort by timestamp (newest first)
        alerts = sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        
        return [a.to_dict() for a in alerts[:limit]]
    
    async def mark_alert_read(self, alert_id: str) -> bool:
        """Mark an alert as read."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.read = True
                return True
        return False
    
    async def clear_alerts(self) -> int:
        """Clear all alerts."""
        count = len(self.alerts)
        self.alerts = []
        return count
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return [msg.to_dict() for msg in self.conversation_history]
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    async def get_quick_replies(self, context: str = "general") -> List[str]:
        """Get suggested quick replies based on context."""
        quick_replies = {
            "general": [
                "What is my portfolio risk level?",
                "Analyze my recent transactions",
                "Show me security tips",
                "What are the current network conditions?"
            ],
            "transaction": [
                "Is this transaction safe?",
                "What are the risks?",
                "Should I proceed?",
                "Explain this transaction"
            ],
            "alert": [
                "Tell me more about this alert",
                "What should I do?",
                "Is this a false positive?",
                "How to prevent this?"
            ],
            "portfolio": [
                "What's my total balance?",
                "Show risk analysis",
                "Recommend rebalancing",
                "Check asset allocation"
            ]
        }
        
        return quick_replies.get(context, quick_replies["general"])
    
    async def process_natural_language_command(
        self,
        command: str
    ) -> Dict[str, Any]:
        """
        Process natural language commands for blockchain operations.
        
        Args:
            command: Natural language command
        
        Returns:
            Parsed command and parameters
        """
        prompt = f"""Parse this natural language command and extract the intent and parameters:

Command: "{command}"

Respond in JSON format:
{{
    "intent": "send|check_balance|get_history|analyze|create_alert|other",
    "parameters": {{
        "amount": <number or null>,
        "recipient": "<address or null>",
        "asset": "<asset name or null>",
        "timeframe": "<timeframe or null>"
    }},
    "confidence": <0-1>
}}

Only respond with the JSON object."""

        try:
            messages = [
                {"role": "system", "content": "You are a command parser. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._call_openrouter(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Parse JSON response
            parsed = json.loads(content)
            
            return {
                "success": True,
                "parsed_command": parsed,
                "original_command": command
            }
        
        except Exception as e:
            logger.error(f"Failed to parse command: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_command": command
            }


# Singleton instance
_chatbot_service: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """Get or create the chatbot service singleton instance."""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
