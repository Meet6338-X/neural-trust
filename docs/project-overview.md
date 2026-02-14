# NeuralTrust Project Overview

## What is NeuralTrust?

NeuralTrust (formerly ChainGuardian) is an AI-powered blockchain security platform built specifically for the Algorand ecosystem. It combines advanced artificial intelligence with robust wallet management to provide comprehensive protection for digital assets.

## Mission

To make blockchain transactions safe and accessible for everyone by providing intelligent, real-time security analysis and user-friendly wallet management tools.

## Core Features

### 1. AI-Powered Transaction Analysis
- Real-time risk assessment for every transaction
- Detection of phishing attempts, scams, and malicious contracts
- Clear recommendations: ALLOW, WARN, or BLOCK
- Detailed explanations of identified risks

### 2. Smart Contract Auditing
- Automated vulnerability detection
- Pre-interaction safety verification
- Known vulnerability pattern matching
- Security scoring and recommendations

### 3. Multi-Signature Wallets
- M-of-N signature requirements
- Shared control for organizations
- Enhanced security for large holdings
- Proposal and approval workflow

### 4. Social Recovery
- Trusted guardian system
- Wallet recovery without seed phrase
- Configurable recovery thresholds
- Guardian management interface

### 5. Portfolio Management
- Real-time asset tracking
- Performance analytics
- Historical charts
- Multi-currency support

### 6. Security Alerts
- Real-time notifications
- Price alerts
- Security warnings
- Transaction confirmations

## Technology Stack

### Mobile App (Flutter)
- **Framework**: Flutter 3.10+
- **Language**: Dart
- **State Management**: Riverpod
- **Navigation**: GoRouter
- **Local Storage**: Hive, flutter_secure_storage
- **Blockchain**: algorand_dart ^1.0.3

### Backend (FastAPI)
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI Integration**: OpenRouter API
- **Database**: SQLite/PostgreSQL
- **API**: RESTful with OpenAPI docs

### Smart Contracts
- **Platform**: Algorand
- **Language**: PyTeal
- **Tools**: AlgoKit

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      NeuralTrust App                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Wallet    │  │ Transaction │  │  Portfolio  │        │
│  │  Management │  │   Service   │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    AI       │  │   Alert     │  │  Multi-Sig  │        │
│  │  Analysis   │  │   Service   │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                      Storage Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Secure    │  │    Hive     │  │Preferences  │        │
│  │   Storage   │  │   Database  │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    External Services                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Algorand   │  │   Backend   │  │ Price Feeds │        │
│  │    Node     │  │    API      │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Target Users

### Individual Users
- Crypto investors seeking security
- DeFi participants
- NFT collectors
- Everyday Algorand users

### Organizations
- DAOs managing treasury
- Companies holding crypto assets
- Investment funds
- Non-profits accepting donations

### Developers
- DApp developers
- Smart contract creators
- Integration partners
- Security researchers

## Roadmap

### Phase 1: Core Features (Current)
- ✅ Wallet creation and import
- ✅ Transaction sending with AI analysis
- ✅ Portfolio tracking
- ✅ Multi-signature support
- ✅ Local secure storage

### Phase 2: Enhanced Security
- ⏳ Hardware wallet integration
- ⏳ Advanced biometrics
- ⏳ Transaction simulation
- ⏳ Address book with verification

### Phase 3: DeFi Integration
- 📋 DEX integration
- 📋 Yield farming analysis
- 📋 Liquidity pool monitoring
- 📋 DeFi position tracking

### Phase 4: Cross-Chain
- 📋 Multi-chain support
- 📋 Cross-chain analysis
- 📋 Bridge security
- 📋 Unified portfolio view

## Security Model

### Local Security
- Private keys never leave device
- Encrypted storage using platform secure storage
- Biometric authentication
- PIN protection

### Transaction Security
- AI analysis before every transaction
- Risk scoring and recommendations
- User confirmation required
- Transaction simulation

### Recovery Security
- Multi-signature recovery
- Social recovery with guardians
- Encrypted backup options
- No centralized key storage

## Business Model

### Free Tier
- Basic wallet functionality
- Limited AI analysis
- Portfolio tracking
- Basic alerts

### Premium Tier
- Unlimited AI analysis
- Advanced security features
- Priority support
- Multi-signature wallets

### Enterprise Tier
- Custom integrations
- API access
- Dedicated support
- SLA guarantees

## Success Metrics

| Metric | Target |
|--------|--------|
| Active Users | 100,000+ |
| Transactions Analyzed | 1M+ |
| Funds Protected | $1B+ |
| Security Incidents Prevented | 10,000+ |
| User Satisfaction | 4.5+ stars |

## Team

NeuralTrust is developed by a team passionate about blockchain security and user experience. We believe that security shouldn't come at the cost of usability.

## Contact

- **Website**: [neuraltrust.io](https://neuraltrust.io)
- **GitHub**: [github.com/neuraltrust](https://github.com/neuraltrust)
- **Twitter**: [@neuraltrust](https://twitter.com/neuraltrust)
- **Discord**: [discord.gg/neuraltrust](https://discord.gg/neuraltrust)

## License

NeuralTrust is open source under the MIT License. See [LICENSE](../LICENSE) for details.
