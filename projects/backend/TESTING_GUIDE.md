# ChainGuardian Backend - Testing Guide

## Quick Start

### 1. Start the Server

```bash
cd projects/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 2. Run Automated Tests

```bash
cd projects/backend
python test_api.py
```

## API Endpoints

### Health Check Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Basic health check |
| `/health/detailed` | GET | Detailed health with all service statuses |

**Example:**
```bash
curl http://localhost:8002/health
curl http://localhost:8002/health/detailed
```

### AI Risk Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analysis/risk` | POST | Analyze transaction risk |
| `/api/analysis/batch` | POST | Batch analyze multiple transactions |
| `/api/analysis/model-info` | GET | Get AI model information |

**Example - Risk Analysis:**
```bash
curl -X POST http://localhost:8002/api/analysis/risk \
  -H "Content-Type: application/json" \
  -d '{
    "type": "transfer",
    "amount": 100.0,
    "sender": "YOUR_ADDRESS",
    "recipient": "RECIPIENT_ADDRESS",
    "protocol": "tinyman"
  }'
```

### Smart Contract Audit

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audit/contract` | POST | Audit smart contract code |
| `/api/audit/contract/patterns` | GET | List vulnerability patterns |

**Example - Contract Audit:**
```bash
curl -X POST http://localhost:8002/api/audit/contract \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#pragma version 8\ntxn Sender\napp_global_put\nint 1\nreturn",
    "language": "teal",
    "check_types": ["security", "optimization", "best_practice"]
  }'
```

**Example - Get Patterns:**
```bash
curl http://localhost:8002/api/audit/contract/patterns
```

### Address Reputation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/reputation/{address}` | GET | Get address reputation |
| `/api/reputation/{address}/history` | GET | Get reputation history |
| `/api/reputation/{address}/patterns` | GET | Get risk patterns |
| `/api/reputation/batch` | POST | Batch check addresses |

**Example:**
```bash
curl http://localhost:8002/api/reputation/ALGORAND_ADDRESS
```

### Portfolio Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portfolio/analyze` | POST | Analyze portfolio risk |
| `/api/portfolio/{address}/summary` | GET | Get portfolio summary |
| `/api/portfolio/{address}/assets` | GET | List portfolio assets |
| `/api/portfolio/{address}/protocols` | GET | Get protocol exposure |
| `/api/portfolio/{address}/risks` | GET | Get portfolio risks |

**Example:**
```bash
curl -X POST http://localhost:8002/api/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "address": "YOUR_ADDRESS",
    "assets": [
      {"asset_id": 0, "amount": 1000000, "symbol": "ALGO"},
      {"asset_id": 12345, "amount": 500, "symbol": "USDC"}
    ]
  }'
```

### Transaction Simulation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulate/payment` | POST | Simulate payment transaction |
| `/api/simulate/app-call` | POST | Simulate app call |
| `/api/simulate/asset-transfer` | POST | Simulate asset transfer |
| `/api/simulate/group` | POST | Simulate transaction group |
| `/api/simulate/fees` | GET | Estimate transaction fees |
| `/api/simulate/dry-run/{address}` | GET | Dry-run account analysis |

**Example - Fee Estimation:**
```bash
curl "http://localhost:8002/api/simulate/fees?transaction_type=payment&priority=normal"
```

**Example - Payment Simulation:**
```bash
curl -X POST "http://localhost:8002/api/simulate/payment?sender=SENDER&receiver=RECEIVER&amount=1000000"
```

### WebSocket Real-Time Alerts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws/alerts` | WebSocket | Real-time risk alerts |
| `/ws/status` | GET | WebSocket connection status |

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8002/ws/alerts');

ws.onopen = () => {
  console.log('Connected to alerts');
  
  // Subscribe to address alerts
  ws.send(JSON.stringify({
    type: 'subscribe',
    address: 'YOUR_ALGORAND_ADDRESS'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Alert:', data);
};
```

### Vault Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vault/create` | POST | Create a new vault |
| `/api/vault/{address}` | GET | Get vault status |
| `/api/vault/{address}` | PUT | Update vault settings |
| `/api/vault/freeze` | POST | Freeze a vault |
| `/api/vault/unfreeze` | POST | Unfreeze a vault |

### Audit Log

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audit/{address}` | GET | Get audit logs for address |
| `/api/audit/onchain/{index}` | GET | Get on-chain audit entry |
| `/api/audit/onchain/count` | GET | Get audit entry count |

## Web Interface

Access the web dashboard at:
- Home: http://localhost:8002/
- Dashboard: http://localhost:8002/dashboard
- Vault: http://localhost:8002/vault
- Analysis: http://localhost:8002/analysis
- Audit: http://localhost:8002/audit

## API Documentation

- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Environment Configuration

Create a `.env` file in `projects/backend/` with:

```env
# Algorand Network
ALGORAND_NETWORK=testnet
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud

# AI Configuration (OpenRouter)
OPENROUTER_API_KEY=your_api_key_here
AI_MODEL=neuralbase/nemotron-3-nano-30b-a3b:free

# API Settings
API_HOST=0.0.0.0
API_PORT=8002
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Guardian Vault (optional)
GUARDIAN_VAULT_APP_ID=0
```

## Troubleshooting

### Server Won't Start
1. Check if port is already in use: `netstat -ano | findstr :8002`
2. Kill existing processes: `taskkill /f /im python.exe`
3. Restart the server

### Blockchain Connection Issues
1. Verify network connectivity
2. Check Algorand node status at https://testnet-api.algonode.cloud/health
3. Try alternative node URLs

### AI Analysis Errors
1. Verify OPENROUTER_API_KEY is set correctly
2. Check API quota and validity
3. The system will fall back to rule-based analysis if AI fails

### Database Issues
1. Delete `chainguardian.db` to reset the database
2. The database will be recreated on next startup
