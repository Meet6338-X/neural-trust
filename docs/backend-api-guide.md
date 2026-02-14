# Backend API Guide

This document provides comprehensive documentation for the NeuralTrust FastAPI backend, including all endpoints, request/response formats, and integration examples.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [API Endpoints](#api-endpoints)
4. [WebSocket API](#websocket-api)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Overview

The NeuralTrust backend is a FastAPI-based REST API that provides:

- **AI Risk Analysis** - Transaction risk assessment using AI models
- **Smart Contract Auditing** - Vulnerability detection in TEAL/Python contracts
- **Address Reputation** - Trust scoring for Algorand addresses
- **Portfolio Analysis** - Risk assessment of asset holdings
- **Transaction Simulation** - Pre-execution transaction testing
- **Vault Management** - Guardian Vault smart contract interaction
- **Real-Time Alerts** - WebSocket-based notifications

### Base URL

```
Development: http://localhost:8000
Production: https://api.neuraltrust.app
```

### API Prefix

All API endpoints are prefixed with `/api`:

```
http://localhost:8000/api/analysis/risk
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip or poetry

### Installation

```bash
cd projects/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your configuration
```

### Running the Server

```bash
# Development mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

```env
# Algorand Network
ALGORAND_NETWORK=testnet
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud

# AI Configuration
OPENROUTER_API_KEY=your_api_key
AI_MODEL=anthropic/claude-3-haiku
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Guardian Vault
GUARDIAN_VAULT_APP_ID=0

# Database
DATABASE_URL=sqlite+aiosqlite:///./chainguardian.db
```

---

## API Endpoints

### Health Check

#### GET /health

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "ChainGuardian Backend",
  "network": "testnet"
}
```

#### GET /health/detailed

Detailed health check with dependency status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-14T08:00:00.000Z",
  "version": "0.1.0",
  "service": "ChainGuardian Backend",
  "checks": {
    "ai_service": {
      "status": "configured",
      "model": "anthropic/claude-3-haiku",
      "provider": "OpenRouter"
    },
    "blockchain": {
      "status": "connected",
      "network": "testnet",
      "last_round": 12345678
    },
    "database": {
      "status": "connected",
      "type": "SQLite"
    },
    "guardian_vault": {
      "status": "configured",
      "app_id": 12345
    }
  }
}
```

---

### Risk Analysis

#### POST /api/analysis/risk

Analyze a transaction for risk.

**Request Body:**
```json
{
  "type": "transfer",
  "amount": 100.5,
  "sender": "ALGORAND_ADDRESS_SENDER",
  "recipient": "ALGORAND_ADDRESS_RECIPIENT",
  "protocol": "Tinyman",
  "timestamp": "2026-02-14T08:00:00Z",
  "additional_context": {
    "asset_id": 0,
    "note": "Optional transaction note"
  }
}
```

**Response:**
```json
{
  "risk_score": 35,
  "recommendation": "WARN",
  "reasoning": "Transaction to new recipient address with moderate amount. No known issues with the protocol.",
  "model_used": "anthropic/claude-3-haiku",
  "confidence": 0.85
}
```

**Risk Score Guidelines:**
| Score | Risk Level | Recommendation |
|-------|------------|----------------|
| 0-30 | Low | ALLOW |
| 31-60 | Medium | WARN |
| 61-100 | High | BLOCK |

#### POST /api/analysis/batch

Analyze multiple transactions in batch.

**Request Body:**
```json
{
  "transactions": [
    {
      "type": "transfer",
      "amount": 100,
      "sender": "ADDRESS1",
      "recipient": "ADDRESS2"
    },
    {
      "type": "swap",
      "amount": 500,
      "sender": "ADDRESS1",
      "protocol": "Tinyman"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "risk_score": 25,
      "recommendation": "ALLOW",
      "reasoning": "Standard transfer to known address",
      "model_used": "anthropic/claude-3-haiku",
      "confidence": 0.92
    },
    {
      "risk_score": 45,
      "recommendation": "WARN",
      "reasoning": "Large swap amount, verify protocol",
      "model_used": "anthropic/claude-3-haiku",
      "confidence": 0.78
    }
  ]
}
```

#### GET /api/analysis/model-info

Get information about the AI model.

**Response:**
```json
{
  "model": "anthropic/claude-3-haiku",
  "provider": "OpenRouter",
  "api_base": "https://openrouter.ai/api/v1",
  "configured": true
}
```

---

### Smart Contract Audit

#### POST /api/audit/contract

Audit a smart contract for vulnerabilities.

**Request Body:**
```json
{
  "source_code": "# TEAL or Python contract code",
  "language": "teal",
  "contract_name": "MyContract"
}
```

**Response:**
```json
{
  "vulnerabilities": [
    {
      "type": "REENTRANCY",
      "severity": "HIGH",
      "line_number": 45,
      "description": "Potential reentrancy vulnerability detected",
      "recommendation": "Add reentrancy guard or use checks-effects-interactions pattern"
    },
    {
      "type": "ACCESS_CONTROL",
      "severity": "MEDIUM",
      "line_number": 23,
      "description": "Missing access control check",
      "recommendation": "Add sender verification before state changes"
    }
  ],
  "overall_risk": "HIGH",
  "score": 75,
  "summary": "Contract has 2 vulnerabilities requiring attention",
  "recommendations": [
    "Implement proper access control",
    "Add reentrancy protection",
    "Consider formal verification"
  ]
}
```

#### GET /api/audit/contract/patterns

List available vulnerability patterns.

**Response:**
```json
{
  "patterns": [
    {
      "name": "REENTRANCY",
      "description": "Detects potential reentrancy vulnerabilities",
      "severity": "HIGH"
    },
    {
      "name": "INTEGER_OVERFLOW",
      "description": "Detects integer overflow/underflow",
      "severity": "HIGH"
    },
    {
      "name": "ACCESS_CONTROL",
      "description": "Detects missing access control",
      "severity": "MEDIUM"
    }
  ]
}
```

---

### Address Reputation

#### GET /api/reputation/{address}

Get reputation score for an Algorand address.

**Response:**
```json
{
  "address": "ALGORAND_ADDRESS",
  "trust_score": 85,
  "risk_level": "LOW",
  "factors": {
    "account_age_days": 365,
    "total_transactions": 150,
    "flags": 0,
    "known_interactions": true
  },
  "history": {
    "first_seen": "2025-02-14T00:00:00Z",
    "last_active": "2026-02-14T08:00:00Z"
  },
  "recommendations": []
}
```

#### POST /api/reputation/batch

Get reputation scores for multiple addresses.

**Request Body:**
```json
{
  "addresses": ["ADDRESS1", "ADDRESS2", "ADDRESS3"]
}
```

---

### Portfolio Analysis

#### POST /api/portfolio/analyze

Analyze portfolio risk.

**Request Body:**
```json
{
  "address": "ALGORAND_ADDRESS",
  "include_assets": true,
  "include_protocols": true
}
```

**Response:**
```json
{
  "total_value_usd": 15000.00,
  "risk_score": 45,
  "risk_level": "MEDIUM",
  "assets": [
    {
      "asset_id": 0,
      "name": "Algo",
      "amount": 5000,
      "value_usd": 5000.00,
      "allocation_percent": 33.3,
      "risk_contribution": 10
    },
    {
      "asset_id": 12345,
      "name": "USDC",
      "amount": 10000,
      "value_usd": 10000.00,
      "allocation_percent": 66.7,
      "risk_contribution": 35
    }
  ],
  "protocol_exposure": [
    {
      "protocol": "Tinyman",
      "value_usd": 3000.00,
      "risk_level": "MEDIUM"
    }
  ],
  "recommendations": [
    "Consider diversifying across more protocols",
    "Reduce exposure to volatile assets"
  ]
}
```

---

### Transaction Simulation

#### POST /api/simulate/transaction

Simulate a transaction before execution.

**Request Body:**
```json
{
  "sender": "ALGORAND_ADDRESS",
  "receiver": "ALGORAND_ADDRESS",
  "amount": 1000000,
  "type": "payment"
}
```

**Response:**
```json
{
  "success": true,
  "fee": 1000,
  "min_fee": 1000,
  "estimated_round": 12345680,
  "warnings": []
}
```

#### GET /api/simulate/fees

Get current fee estimates.

**Response:**
```json
{
  "min_fee": 1000,
  "suggested_fee": 1000,
  "priority_fee": 2000,
  "network_congestion": "LOW"
}
```

---

### Vault Management

#### POST /api/vault/create

Create a new Guardian Vault.

**Request Body:**
```json
{
  "owner_address": "ALGORAND_ADDRESS",
  "risk_threshold": 50,
  "daily_limit": 10000000,
  "guardians": ["GUARDIAN_ADDRESS_1", "GUARDIAN_ADDRESS_2"]
}
```

**Response:**
```json
{
  "app_id": 12345,
  "app_address": "APP_ADDRESS",
  "status": "created",
  "transaction_id": "TX_ID"
}
```

#### GET /api/vault/{address}

Get vault status for an address.

**Response:**
```json
{
  "app_id": 12345,
  "owner": "ALGORAND_ADDRESS",
  "risk_threshold": 50,
  "daily_limit": 10000000,
  "is_frozen": false,
  "guardians": ["GUARDIAN_1", "GUARDIAN_2"],
  "total_protected": 50000000,
  "transactions_blocked": 5
}
```

#### POST /api/vault/freeze

Freeze a vault.

**Request Body:**
```json
{
  "app_id": 12345,
  "reason": "Suspicious activity detected"
}
```

#### POST /api/vault/unfreeze

Unfreeze a vault.

**Request Body:**
```json
{
  "app_id": 12345,
  "guardian_signature": "SIGNATURE"
}
```

---

## WebSocket API

### Connection

Connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts');
```

### Subscribe to Address Alerts

```json
{
  "type": "subscribe",
  "address": "ALGORAND_ADDRESS"
}
```

### Unsubscribe

```json
{
  "type": "unsubscribe",
  "address": "ALGORAND_ADDRESS"
}
```

### Alert Message Format

```json
{
  "type": "alert",
  "address": "ALGORAND_ADDRESS",
  "alert": {
    "id": "alert_123",
    "severity": "HIGH",
    "title": "High Risk Transaction Detected",
    "message": "Transaction to flagged address blocked",
    "timestamp": "2026-02-14T08:00:00Z",
    "data": {
      "transaction_id": "TX_ID",
      "risk_score": 85
    }
  }
}
```

---

## Data Models

### TransactionData

```python
class TransactionData(BaseModel):
    type: str                    # transfer, swap, stake, etc.
    amount: float                # Amount in ALGO
    sender: str                  # Sender address
    recipient: str               # Recipient address
    protocol: Optional[str]      # Protocol name
    timestamp: Optional[str]     # ISO timestamp
    additional_context: Optional[dict]
```

### RiskAnalysisResponse

```python
class RiskAnalysisResponse(BaseModel):
    risk_score: int              # 0-100
    recommendation: str          # ALLOW, WARN, BLOCK
    reasoning: str               # Explanation
    model_used: str              # AI model name
    confidence: float            # 0-1
```

### Vulnerability

```python
class Vulnerability(BaseModel):
    type: str                    # Vulnerability type
    severity: str                # LOW, MEDIUM, HIGH, CRITICAL
    line_number: Optional[int]   # Line in source code
    description: str             # Description
    recommendation: str          # How to fix
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Rate Limiting

Rate limits are applied per IP address:

| Endpoint Type | Limit |
|--------------|-------|
| Health checks | 60/minute |
| Analysis | 30/minute |
| Audit | 10/minute |
| Other | 60/minute |

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1707900000
```

---

## Examples

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Risk analysis
curl -X POST http://localhost:8000/api/analysis/risk \
  -H "Content-Type: application/json" \
  -d '{
    "type": "transfer",
    "amount": 100,
    "sender": "SENDER_ADDRESS",
    "recipient": "RECIPIENT_ADDRESS"
  }'

# Contract audit
curl -X POST http://localhost:8000/api/audit/contract \
  -H "Content-Type: application/json" \
  -d '{
    "source_code": "# Your contract code",
    "language": "teal"
  }'
```

### Python Example

```python
import httpx

async def analyze_transaction(tx_data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/analysis/risk",
            json=tx_data
        )
        return response.json()
```

### Dart/Flutter Example

```dart
Future<RiskAnalysis> analyzeTransaction(TransactionData data) async {
  final response = await _dio.post(
    '/api/analysis/risk',
    data: data.toJson(),
  );
  return RiskAnalysis.fromJson(response.data);
}
```

---

## API Documentation

Interactive API documentation is available when running the server:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

*Last Updated: February 2026*
