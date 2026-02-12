# NeuralTrust - AI-Powered DeFi Risk & Compliance Platform

<div align="center">

![NeuralTrust Banner](https://img.shields.io/badge/NeuralTrust-AI%20Powered%20DeFi%20Protection-blue?style=for-the-badge)

**AI-Powered Risk Analysis • Smart Contract Auditing • Real-Time Protection**

[![Algorand](https://img.shields.io/badge/Algorand-Blockchain-orange)](https://algorand.com)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Flutter](https://img.shields.io/badge/Flutter-Mobile-blue)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🚀 Overview

NeuralTrust (ChainGuardian) is a comprehensive DeFi risk management platform that combines **off-chain AI intelligence** with **on-chain blockchain enforcement** to protect users from risky or fraudulent financial actions on the Algorand blockchain.

### Key Features

- 🤖 **AI Risk Analysis** - Advanced AI models analyze transactions for potential risks
- 📝 **Smart Contract Auditing** - Automated vulnerability detection for TEAL and Python contracts
- 🛡️ **Guardian Vault** - On-chain risk threshold enforcement
- 📊 **Portfolio Analysis** - Comprehensive risk assessment of your holdings
- 🔔 **Real-Time Alerts** - WebSocket-based instant notifications
- 📱 **Mobile App** - Cross-platform Flutter app for iOS, Android, and Web
- 🌐 **Web Dashboard** - Python-based web interface with Jinja2 templates

---

## 📸 Screenshots

### Python Web Application

| Home Page | Dashboard |
|-----------|-----------|
| [![Home Page](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222312.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222312.png) | [![Dashboard](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222357.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222357.png) |

| Vault Management | Risk Analysis |
|------------------|---------------|
| [![Vault](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222414.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222414.png) | [![Analysis](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222515.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222515.png) |

| Audit Log | API Documentation |
|-----------|-------------------|
| [![Audit](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222530.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222530.png) | [![API Docs](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222544.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222544.png) |

| Health Check | Connected Wallet |
|--------------|------------------|
| [![Health](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20222621.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20222621.png) | [![Connected](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/python/Screenshot%202026-02-12%20223941.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/python/Screenshot%202026-02-12%20223941.png) |

### Flutter Mobile Application

| Dashboard | Risk Analysis |
|-----------|---------------|
| [![Mobile Dashboard](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164036.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164036.png) | [![Mobile Risk](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164054.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164054.png) |

| Alerts | Profile |
|--------|---------|
| [![Mobile Alerts](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164115.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164115.png) | [![Mobile Profile](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164142.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164142.png) |

| Settings | More Screens |
|----------|--------------|
| [![Mobile Settings](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164214.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164214.png) | [![More](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164237.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164237.png) |

| Additional Screen |
|-------------------|
| [![Additional](https://github.com/Meet6338-X/neural-trust/raw/main/Screenshot/mobile/Screenshot%202026-02-10%20164925.png)](https://github.com/Meet6338-X/neural-trust/blob/main/Screenshot/mobile/Screenshot%202026-02-10%20164925.png) |

---

## 📁 Project Structure

```
neural-trust/
├── projects/
│   ├── backend/           # FastAPI Python Backend
│   │   ├── app/
│   │   │   ├── api/       # API Routes
│   │   │   │   ├── routes/        # REST API endpoints
│   │   │   │   │   ├── analysis.py      # Risk analysis endpoints
│   │   │   │   │   ├── audit.py         # Audit log endpoints
│   │   │   │   │   ├── audit_contract.py # Contract auditing
│   │   │   │   │   ├── vault.py         # Vault management
│   │   │   │   │   ├── reputation.py    # Address reputation
│   │   │   │   │   ├── portfolio.py     # Portfolio analysis
│   │   │   │   │   └── simulate.py      # Transaction simulation
│   │   │   │   └── websockets/   # WebSocket handlers
│   │   │   ├── models/    # Database Models
│   │   │   │   ├── database.py     # SQLAlchemy models
│   │   │   │   └── schemas.py      # Pydantic schemas
│   │   │   ├── services/  # Business Logic
│   │   │   │   ├── ai_engine.py           # AI risk analysis
│   │   │   │   ├── blockchain_service.py  # Algorand integration
│   │   │   │   ├── contract_auditor.py    # Contract auditing
│   │   │   │   ├── reputation_service.py  # Address reputation
│   │   │   │   ├── portfolio_analyzer.py  # Portfolio analysis
│   │   │   │   └── transaction_simulator.py # Transaction simulation
│   │   │   ├── templates/ # Web Templates (Jinja2)
│   │   │   │   ├── base.html       # Base template
│   │   │   │   ├── index.html      # Home page
│   │   │   │   ├── dashboard.html  # Dashboard page
│   │   │   │   ├── vault.html      # Vault management
│   │   │   │   ├── analysis.html   # Risk analysis
│   │   │   │   └── audit.html      # Audit log
│   │   │   ├── static/    # Static Assets
│   │   │   │   └── js/main.js      # JavaScript utilities
│   │   │   ├── config.py   # Configuration
│   │   │   └── main.py     # FastAPI application
│   │   ├── test_api.py     # API tests
│   │   ├── requirements.txt
│   │   └── .env.template
│   │
│   └── contracts/         # Algorand Smart Contracts
│       └── smart_contracts/
│           ├── guardian_vault/  # Main Vault Contract
│           │   ├── contract.py      # Vault contract logic
│           │   ├── deploy_config.py # Deployment config
│           │   └── README.md
│           ├── bank/            # Bank Demo Contract
│           │   ├── contract.py
│           │   └── deploy_config.py
│           └── counter/         # Counter Demo Contract
│               ├── contract.py
│               └── deploy_config.py
│
├── NeuralTrust/           # Flutter Mobile App
│   ├── lib/
│   │   ├── main.dart           # App entry point
│   │   ├── app.dart            # App configuration
│   │   ├── screens/            # App Screens
│   │   │   ├── dashboard/         # Main Dashboard
│   │   │   │   └── dashboard_screen.dart
│   │   │   ├── risk/              # Risk Analysis
│   │   │   │   └── risk_screen.dart
│   │   │   ├── alerts/            # Notifications
│   │   │   │   └── alerts_screen.dart
│   │   │   ├── profile/           # User Profile
│   │   │   │   └── profile_screen.dart
│   │   │   ├── settings/          # App Settings
│   │   │   │   └── settings_screen.dart
│   │   │   └── onboarding/        # Get Started
│   │   │       └── get_started_screen.dart
│   │   ├── widgets/            # Reusable Widgets
│   │   │   └── common/
│   │   │       ├── bottom_nav_bar.dart
│   │   │       ├── feature_card.dart
│   │   │       ├── risk_score_card.dart
│   │   │       └── stats_card.dart
│   │   └── theme/              # App Theme
│   │       └── app_theme.dart
│   ├── pubspec.yaml            # Dependencies
│   ├── android/                # Android specific
│   ├── ios/                    # iOS specific
│   ├── web/                    # Web specific
│   ├── macos/                  # macOS specific
│   ├── windows/                # Windows specific
│   └── linux/                  # Linux specific
│
├── Screenshot/            # App Screenshots
│   ├── python/            # Web app screenshots
│   └── mobile/            # Mobile app screenshots
│
└── plans/                 # Project Documentation
    └── chainguardian-plan.md
```

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Mobile App
        FL[Flutter App - iOS/Android/Web]
    end
    
    subgraph Web Interface
        WF[Python Web Templates - Jinja2]
    end
    
    subgraph Backend
        API[FastAPI Server]
        AI[AI Risk Engine]
        WS[WebSocket Server]
    end
    
    subgraph Blockchain
        ALG[Algorand Network]
        GV[Guardian Vault Contract]
    end
    
    subgraph External
        OR[OpenRouter AI]
        IPFS[IPFS/Pinata]
    end
    
    FL --> API
    WF --> API
    API --> AI
    API --> WS
    API --> ALG
    AI --> OR
    ALG --> GV
    API --> IPFS
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Pydantic |
| **AI Engine** | OpenRouter API, Custom Rule Engine |
| **Blockchain** | Algorand, PyTeal, AlgoKit |
| **Web Interface** | Jinja2 Templates, TailwindCSS |
| **Mobile App** | Flutter, Dart |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Real-Time** | WebSocket |
| **Storage** | IPFS/Pinata |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Flutter SDK 3.0+
- AlgoKit CLI (optional, for smart contracts)

### 1. Clone the Repository

```bash
git clone https://github.com/Meet6338-X/neural-trust.git
cd neural-trust
```

### 2. Start the Backend

```bash
cd projects/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.template .env
# Edit .env with your API keys

# Run the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the Web Dashboard

Open your browser and navigate to:
- Home: `http://localhost:8000/`
- Dashboard: `http://localhost:8000/dashboard`
- Vault: `http://localhost:8000/vault`
- Analysis: `http://localhost:8000/analysis`
- Audit: `http://localhost:8000/audit`
- API Docs: `http://localhost:8000/docs`

### 4. Start the Mobile App

```bash
cd NeuralTrust

# Get dependencies
flutter pub get

# Run on device
flutter run

# Or build for specific platform
flutter build apk        # Android
flutter build ios        # iOS
flutter build web        # Web
```

---

## 📱 Mobile App Features

The Flutter mobile app provides a complete mobile experience:

### Screens

| Screen | Description |
|--------|-------------|
| **Dashboard** | Overview of vault status, risk scores, and quick actions |
| **Risk Analysis** | Detailed risk breakdown and transaction analysis |
| **Alerts** | Real-time notifications and risk warnings |
| **Profile** | Wallet management and account settings |
| **Settings** | App preferences and notification controls |

### Platform Support

- ✅ Android (API 21+)
- ✅ iOS (iOS 12+)
- ✅ Web (Chrome, Safari, Firefox)
- ✅ macOS
- ✅ Windows
- ✅ Linux

---

## 🌐 Web Dashboard Features

The Python-based web interface provides:

| Page | Description |
|------|-------------|
| **Home** | Landing page with project overview |
| **Dashboard** | Vault status, risk scores, quick actions |
| **Vault** | Create and manage Guardian Vaults |
| **Analysis** | AI-powered transaction risk analysis |
| **Audit** | Smart contract auditing tools |

---

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Basic health check |
| `/health/detailed` | GET | Detailed service status |
| `/api/analysis/risk` | POST | Analyze transaction risk |
| `/api/audit/contract` | POST | Audit smart contract |
| `/api/audit/contract/patterns` | GET | List vulnerability patterns |
| `/api/reputation/{address}` | GET | Get address reputation |
| `/api/portfolio/analyze` | POST | Analyze portfolio risk |
| `/api/simulate/fees` | GET | Estimate transaction fees |
| `/ws/alerts` | WebSocket | Real-time alerts |

### Vault Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vault/create` | POST | Create new vault |
| `/api/vault/status` | GET/POST | Get vault status |
| `/api/vault/{address}` | GET/PUT | Get/Update vault |
| `/api/vault/freeze` | POST | Freeze vault |
| `/api/vault/unfreeze` | POST | Unfreeze vault |

### Full API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## ⚙️ Configuration

### Backend Environment Variables

Create `projects/backend/.env`:

```env
# Algorand Network
ALGORAND_NETWORK=testnet
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud

# AI Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
AI_MODEL=anthropic/claude-3-haiku

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Guardian Vault Contract
GUARDIAN_VAULT_APP_ID=0
```

---

## 🧪 Testing

### Backend Tests

```bash
cd projects/backend
python test_api.py
```

### Smart Contract Tests

```bash
cd projects/contracts
pytest tests/
```

### Mobile App Tests

```bash
cd NeuralTrust
flutter test
```

---

## 📊 Features Deep Dive

### AI Risk Analysis

The AI engine analyzes transactions using:
- Pattern matching for known attack vectors
- Historical transaction analysis
- Protocol-specific risk assessment
- Real-time threat intelligence

### Smart Contract Auditor

Detects vulnerabilities including:
- Reentrancy attacks
- Integer overflow/underflow
- Unprotected access control
- Front-running vulnerabilities
- Unbounded loops
- Missing error handling

### Guardian Vault

On-chain protection mechanism:
- User-defined risk thresholds
- Automatic transaction blocking
- Emergency freeze capability
- Immutable audit logging

---

## 🔐 Security

- All sensitive data encrypted at rest
- API keys stored securely in environment variables
- WebSocket connections authenticated
- Rate limiting on all endpoints
- Input validation with Pydantic

---

## 📈 Roadmap

- [ ] Multi-chain support (Ethereum, Polygon)
- [ ] Advanced AI models integration
- [ ] Social recovery for vaults
- [ ] DAO governance
- [ ] Mobile push notifications
- [ ] Hardware wallet support

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Algorand Foundation](https://algorand.foundation) for blockchain infrastructure
- [AlgoKit](https://github.com/algorandfoundation/algokit-cli) for development tools
- [OpenRouter](https://openrouter.ai) for AI model access
- [Pinata](https://pinata.cloud) for IPFS storage

---

## 📞 Support

- Documentation: [docs.neuraltrust.io](https://docs.neuraltrust.io)
- Discord: [discord.gg/neuraltrust](https://discord.gg/neuraltrust)
- Twitter: [@NeuralTrust](https://twitter.com/NeuralTrust)
- Email: support@neuraltrust.io

---

<div align="center">

**Built with ❤️ by the NeuralTrust Team**

© 2026 NeuralTrust. All rights reserved.

</div>
