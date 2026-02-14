# NeuralTrust Documentation

Welcome to the NeuralTrust (ChainGuardian) documentation. This folder contains comprehensive documentation for the entire project.

## Overview

NeuralTrust is an AI-powered blockchain security platform for Algorand that provides:
- **AI Transaction Analysis**: Real-time risk assessment for transactions
- **Smart Contract Auditing**: Automated vulnerability detection
- **Multi-Signature Wallets**: Enhanced security with shared control
- **Portfolio Tracking**: Real-time asset valuation and analytics
- **Social Recovery**: Guardian-based wallet recovery

## Documentation Index

### Project Documentation
- [Project Overview](./project-overview.md) - High-level project description and goals
- [Architecture](./architecture.md) - System architecture and design decisions
- [Problems We Solve](./problems-we-solve.md) - Real-world problems addressed by NeuralTrust

### Technical Documentation
- [Flutter App](./flutter-app.md) - Mobile app implementation details
- [Backend API](./backend-api.md) - FastAPI backend documentation
- [Smart Contracts](./smart-contracts.md) - PyTeal smart contract documentation
- [AI Engine](./ai-engine.md) - AI analysis and risk assessment

### User Guides
- [Getting Started](./getting-started.md) - Installation and setup guide
- [Wallet Management](./wallet-management.md) - Creating and managing wallets
- [Transaction Security](./transaction-security.md) - Understanding AI analysis

### Development
- [Contributing](./contributing.md) - How to contribute to the project
- [API Reference](./api-reference.md) - Complete API documentation

## Quick Links

| Component | Technology | Status |
|-----------|------------|--------|
| Flutter App | Flutter 3.10+, Dart | ✅ Active |
| Backend | FastAPI, Python 3.11+ | ✅ Active |
| Smart Contracts | PyTeal, Algorand | ✅ Active |
| AI Engine | OpenRouter, LLM | ✅ Active |
| Database | Hive, SQLite | ✅ Active |

## Project Structure

```
neural-trust/
├── NeuralTrust/           # Flutter mobile app
│   ├── lib/
│   │   ├── app/          # App configuration
│   │   ├── config/       # App constants and config
│   │   ├── models/       # Data models
│   │   ├── providers/    # Riverpod providers
│   │   ├── screens/      # UI screens
│   │   ├── services/     # Business logic
│   │   └── theme/        # App theming
│   └── ...
├── projects/
│   ├── backend/          # FastAPI backend
│   └── contracts/        # PyTeal smart contracts
├── docs/                 # Documentation
└── plans/               # Project plans
```

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Browse this folder for detailed guides
- **API Status**: Check `/health` endpoint for backend status

## License

This project is licensed under the MIT License.
