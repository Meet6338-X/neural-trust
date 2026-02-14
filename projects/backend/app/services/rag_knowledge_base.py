"""
RAG Knowledge Base for ChainGuardian Chatbot.
Provides context-aware responses based on project documentation.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class RAGKnowledgeBase:
    """
    Knowledge base for RAG-style context injection.
    Contains project-specific information for the chatbot.
    """
    
    def __init__(self):
        self.knowledge_chunks = self._initialize_knowledge()
    
    def _initialize_knowledge(self) -> List[Dict[str, str]]:
        """Initialize knowledge chunks for RAG."""
        return [
            # Project Overview
            {
                "topic": "project_overview",
                "content": """ChainGuardian is an AI-Powered DeFi Risk & Compliance Assistant on Algorand blockchain. 
It combines off-chain AI intelligence with on-chain blockchain enforcement to protect users from risky or fraudulent financial actions.
The platform provides real-time risk analysis, transaction monitoring, and smart contract auditing capabilities."""
            },
            {
                "topic": "core_features",
                "content": """ChainGuardian Core Features:
1. AI Risk Analysis - Analyze transactions for potential risks using advanced AI
2. Smart Contract Audit - Audit TEAL and Python smart contracts for vulnerabilities
3. Address Reputation - Get trust scores for Algorand addresses
4. Portfolio Analysis - Analyze portfolio risk exposure
5. Transaction Simulation - Simulate transactions before execution
6. Real-Time Alerts - WebSocket-based real-time risk alerts
7. Guardian Vault - Smart contract-based fund protection"""
            },
            
            # Risk Analysis
            {
                "topic": "risk_scoring",
                "content": """Risk Scoring System:
- Risk scores range from 0-100
- 0-20: VERY_LOW risk - Account appears legitimate
- 21-40: LOW risk - Minor concerns
- 41-60: MEDIUM risk - Proceed with caution
- 61-80: HIGH risk - Manual review recommended
- 81-100: VERY_HIGH risk - Transaction blocked

Recommendations: ALLOW, WARN, or BLOCK based on risk score."""
            },
            {
                "topic": "risk_factors",
                "content": """Risk Factors Analyzed:
1. Account Age - Based on transaction history length
2. Transaction Frequency - Pattern analysis of transaction timing
3. Counterparty Diversity - Number of unique addresses interacted with
4. Value Patterns - Consistency of transaction amounts
5. Historical Risk - Previous risk analysis results
6. Time Patterns - Unusual timing of transactions
7. Blocked History - History of blocked transactions"""
            },
            {
                "topic": "dynamic_risk",
                "content": """Dynamic Risk Scoring:
The system uses cumulative risk scoring that considers:
- Current transaction risk (40% weight)
- Historical risk (25% weight)
- Address reputation (20% weight)
- Behavioral patterns (15% weight)

Risk factors are weighted:
- Historical risk: 25%
- Blocked history: 25%
- Transaction frequency: 15%
- Time patterns: 15%
- Recipient diversity: 10%
- Amount pattern: 10%"""
            },
            
            # Guardian Vault
            {
                "topic": "guardian_vault",
                "content": """Guardian Vault is a smart contract-based protection system on Algorand.
Features:
- Set maximum risk threshold for transactions
- Freeze/unfreeze funds instantly
- Multi-signature support for added security
- Automatic blocking of high-risk transactions
- Real-time monitoring and alerts

Users can configure vault rules to automatically protect their funds based on risk scores."""
            },
            {
                "topic": "vault_freeze",
                "content": """Vault Freeze Functionality:
- Instantly freeze all vault operations
- Prevents any withdrawals or transactions
- Useful when suspicious activity is detected
- Can only be unfrozen by authorized parties
- Provides emergency fund protection

To freeze: Use the vault freeze endpoint or smart contract call.
To unfreeze: Requires proper authorization through the vault contract."""
            },
            
            # Algorand Integration
            {
                "topic": "algorand_network",
                "content": """ChainGuardian operates on Algorand blockchain:
- Currently on TestNet for development
- Can be deployed to MainNet
- Uses Algorand's fast, secure infrastructure
- Transaction finality in ~4.5 seconds
- Low transaction fees (~0.001 ALGO)

Algorand provides the perfect foundation for DeFi security with its high throughput and low latency."""
            },
            {
                "topic": "algorand_address",
                "content": """Algorand Address Format:
- 58 characters long
- Base32 encoded
- Example: FR3DXSMXLGF7QOEYMYSYN3RV3UNFEYEK2RF2P3PAXXTKFNRASPRFADPD34
- Addresses are case-sensitive
- Always verify the full address before transactions

The system can analyze any Algorand address for risk and reputation."""
            },
            
            # Quick Analysis
            {
                "topic": "quick_analysis",
                "content": """Quick Analysis Feature:
- Enter just an Algorand address to get comprehensive risk report
- Returns: Risk score, funds, transaction summary, risk factors, flags, suggestions
- Minimum input, maximum output approach
- Real-time blockchain data fetching
- Pattern analysis and reputation scoring

Access via /quick-analysis page or /api/analysis/simple endpoint."""
            },
            
            # Asset Protection
            {
                "topic": "asset_protection",
                "content": """Asset Protection Module (Coming Soon):
- Protect digital assets by registering on Algorand blockchain
- Support for certificates, documents, images, credit files
- URL-based asset registration
- Immutable proof of ownership
- Content hashing for verification

This feature allows users to create blockchain-based proof of their digital assets."""
            },
            
            # AI Model
            {
                "topic": "ai_model",
                "content": """ChainGuardian uses advanced AI for risk analysis:
- Model: Advanced AI Engine via OpenRouter API
- Capabilities: Natural language understanding, risk assessment, pattern recognition
- Response time: Typically 2-5 seconds
- Confidence scoring for all predictions

The AI is trained to identify potential fraud, scams, and risky transaction patterns."""
            },
            
            # API Endpoints
            {
                "topic": "api_endpoints",
                "content": """Key API Endpoints:
- POST /api/analysis/simple - Quick address analysis
- POST /api/analysis/risk - Full transaction risk analysis
- GET /api/analysis/profile/{address} - Address risk profile
- GET /api/analysis/history/{address} - Analysis history
- POST /api/chatbot/chat - Chat with AI assistant
- GET /api/vault/status - Vault status check
- POST /api/vault/freeze - Freeze vault
- POST /api/vault/unfreeze - Unfreeze vault
- WS /ws/alerts - Real-time WebSocket alerts"""
            },
            
            # Security Best Practices
            {
                "topic": "security_tips",
                "content": """Security Best Practices:
1. Always verify addresses before sending funds
2. Use vault protection for large holdings
3. Enable real-time alerts for your addresses
4. Review risk analysis before executing transactions
5. Keep your private keys secure and never share them
6. Be cautious of unsolicited investment opportunities
7. Verify all smart contract interactions
8. Use multi-signature for additional security"""
            },
            {
                "topic": "common_scams",
                "content": """Common Crypto Scams to Watch For:
1. Phishing attacks - Fake websites mimicking real services
2. Rug pulls - Developers abandoning projects after taking funds
3. Ponzi schemes - Promises of unrealistic returns
4. Impersonation - Fake social media accounts
5. Smart contract vulnerabilities - Exploiting code bugs
6. Flash loan attacks - Manipulating DeFi protocols
7. Private key theft - Social engineering to get keys

ChainGuardian helps identify these risks through AI analysis."""
            },
            
            # DeFi Concepts
            {
                "topic": "defi_basics",
                "content": """DeFi (Decentralized Finance) Basics:
- Financial services without traditional intermediaries
- Built on blockchain smart contracts
- Key activities: Trading, lending, borrowing, yield farming
- Risks: Smart contract bugs, impermanent loss, rug pulls
- Popular Algorand DeFi: Tinyman, Pact, Yieldly

ChainGuardian helps users navigate DeFi safely with risk analysis."""
            },
            {
                "topic": "yield_farming",
                "content": """Yield Farming on Algorand:
- Provide liquidity to earn rewards
- Popular on Tinyman, Pact, Yieldly
- Risks: Impermanent loss, smart contract vulnerabilities
- Always analyze pools before providing liquidity
- Consider risk score of pool tokens

Use ChainGuardian to analyze yield farming opportunities for risk."""
            },
            
            # Transaction Types
            {
                "topic": "transaction_types",
                "content": """Supported Transaction Types for Analysis:
1. Transfer - Simple ALGO or asset transfers
2. Swap - Token exchanges on DEXs
3. Liquidity - Adding/removing liquidity from pools
4. Staking - Staking tokens for rewards
5. Lending/Borrowing - DeFi lending protocols
6. Yield Farming - Complex yield strategies
7. NFT - Non-fungible token transactions
8. Other - Custom transaction types"""
            },
            
            # Troubleshooting
            {
                "topic": "troubleshooting",
                "content": """Common Issues and Solutions:
1. "Address not found" - Address may be new or invalid
2. "Analysis failed" - Check network connectivity
3. "High risk score" - Review risk factors for details
4. "Vault not found" - Create a vault for your address first
5. "API key error" - Contact support for API issues

For support, visit /docs for API documentation or use the chatbot."""
            }
        ]
    
    def get_relevant_context(
        self,
        query: str,
        max_chunks: int = 3
    ) -> str:
        """
        Get relevant context chunks based on the query.
        
        Uses simple keyword matching to find relevant knowledge.
        Can be enhanced with embedding-based similarity search.
        
        Args:
            query: The user's query
            max_chunks: Maximum number of chunks to return
            
        Returns:
            Combined context string
        """
        query_lower = query.lower()
        relevant_chunks = []
        
        # Score each chunk based on keyword matches
        for chunk in self.knowledge_chunks:
            score = 0
            topic = chunk["topic"]
            content = chunk["content"].lower()
            
            # Check for topic match
            if topic.replace("_", " ") in query_lower:
                score += 10
            
            # Check for keyword matches
            keywords = self._extract_keywords(query_lower)
            for keyword in keywords:
                if keyword in content:
                    score += 1
            
            if score > 0:
                relevant_chunks.append((score, chunk))
        
        # Sort by score and take top chunks
        relevant_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = relevant_chunks[:max_chunks]
        
        if not top_chunks:
            # Return general project info if no specific match
            return self._get_general_context()
        
        # Combine chunks into context string
        context_parts = []
        for score, chunk in top_chunks:
            context_parts.append(f"[{chunk['topic'].upper()}]\n{chunk['content']}")
        
        return "\n\n".join(context_parts)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "and", "but", "if", "or", "because",
            "until", "while", "what", "which", "who", "whom", "this",
            "that", "these", "those", "am", "i", "me", "my", "we",
            "our", "you", "your", "he", "him", "his", "she", "her",
            "it", "its", "they", "them", "their"
        }
        
        words = query.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _get_general_context(self) -> str:
        """Get general project context when no specific match."""
        return """[PROJECT OVERVIEW]
ChainGuardian is an AI-Powered DeFi Risk & Compliance Assistant on Algorand blockchain.
It provides real-time risk analysis, transaction monitoring, and smart contract auditing.

[CORE FEATURES]
- AI Risk Analysis for transactions
- Smart Contract Auditing
- Address Reputation Scoring
- Guardian Vault for fund protection
- Real-time Alerts via WebSocket

For specific topics, ask about: risk scoring, vault, freeze, algorand, analysis, security, or DeFi."""


# Singleton instance
_rag_knowledge_base: Optional[RAGKnowledgeBase] = None


def get_rag_knowledge_base() -> RAGKnowledgeBase:
    """Get or create the RAG knowledge base singleton."""
    global _rag_knowledge_base
    if _rag_knowledge_base is None:
        _rag_knowledge_base = RAGKnowledgeBase()
    return _rag_knowledge_base
