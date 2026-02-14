# NeuralTrust Implementation Plan

## Overview

This plan outlines the implementation steps to complete the NeuralTrust Flutter app with Algorand integration, local storage, and new features.

## Implementation Phases

### Phase 1: Dependencies and Setup

#### 1.1 Update pubspec.yaml

Add the following dependencies to `NeuralTrust/pubspec.yaml`:

```yaml
dependencies:
  # Algorand Integration
  algorand_dart: ^1.0.3
  
  # Local Storage
  shared_preferences: ^2.2.2
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  
  # HTTP & API
  dio: ^5.4.0
  
  # WebSockets
  web_socket_channel: ^2.4.0
  
  # Biometrics
  local_auth: ^2.1.8
  
  # QR Codes
  qr_flutter: ^4.1.0
  mobile_scanner: ^4.0.1
  
  # Utilities
  intl: ^0.18.1
  uuid: ^4.2.2
  logger: ^2.0.2
  crypto: ^3.0.3
  encrypt: ^5.0.3

dev_dependencies:
  build_runner: ^2.4.8
  hive_generator: ^2.0.1
```

#### 1.2 Create Directory Structure

```
lib/
...
```

---

### Phase 2: Core Services Implementation

#### 2.1 Algorand Service

**File**: `lib/services/algorand/algorand_service.dart`

Key methods:
- `initialize()` - Setup Algorand client
- `createAccount()` - Generate new wallet
- `importAccount(mnemonic)` - Import from mnemonic
- `getBalance(address)` - Get account balance
- `getSuggestedParams()` - Get transaction params
- `sendTransaction()` - Submit transaction

#### 2.2 Wallet Service

**File**: `lib/services/algorand/wallet_service.dart`

Key methods:
- `createWallet(name, pin)` - Create and store new wallet
- `importWallet(name, mnemonic, pin)` - Import existing wallet
- `getAccount(address, pin)` - Retrieve account for signing
- `deleteWallet(address)` - Remove wallet
- `getWallets()` - List all wallets

#### 2.3 Transaction Service

**File**: `lib/services/algorand/transaction_service.dart`

Key methods:
- `sendAlgo(account, recipient, amount)` - Send ALGO
- `sendAsset(account, recipient, assetId, amount)` - Send ASA
- `optInToAsset(account, assetId)` - Opt-in to asset
- `getTransactionHistory(address)` - Get history from indexer
- `waitForConfirmation(txId)` - Wait for tx confirmation

#### 2.4 Multi-Signature Service

**File**: `lib/services/algorand/multisig_service.dart`

Key methods:
- `createMultisigAddress(signers, threshold)` - Create M-of-N address
- `signMultisigTransaction(multisig, signer, tx)` - Sign with one signer
- `mergeSignatures(signedTxs)` - Combine signatures
- `submitMultisig(mergedTx)` - Execute transaction

---

### Phase 3: Storage Services Implementation

#### 3.1 Secure Storage Service

**File**: `lib/services/storage/secure_storage_service.dart`

Key methods:
- `storeMnemonic(address, encryptedMnemonic)`
- `getMnemonic(address)`
- `deleteMnemonic(address)`
- `storePinHash(pinHash)`
- `getPinHash()`

#### 3.2 Hive Storage Service

**File**: `lib/services/storage/hive_service.dart`

Key methods:
- `initialize()` - Register adapters, open boxes
- `saveWallet(wallet)`
- `getWallets()`
- `saveTransaction(transaction)`
- `getTransactions(walletId)`

#### 3.3 Preferences Service

**File**: `lib/services/storage/preferences_service.dart`

Key methods:
- `setThemeMode(mode)`
- `getThemeMode()`
- `setRiskThreshold(threshold)`
- `getRiskThreshold()`
- `setOnboardingComplete(complete)`

---

### Phase 4: Data Models Implementation

#### 4.1 Create Hive Models

**Files**:
- `lib/models/wallet.dart`
- `lib/models/transaction.dart`
- `lib/models/asset.dart`
- `lib/models/alert.dart`
- `lib/models/portfolio_snapshot.dart`
- `lib/models/multisig_proposal.dart`

Each model needs:
- Hive type annotations
- Hive field annotations
- `part 'model.g.dart';` directive

#### 4.2 Generate Adapters

Run: `flutter packages pub run build_runner build`

---

### Phase 5: State Management (Providers)

#### 5.1 Wallet Provider

**File**: `lib/providers/wallet_provider.dart`

State:
- `wallets` - List of wallets
- `selectedWallet` - Current active wallet
- `isLoading`
- `error`

Actions:
- `loadWallets()`
- `createWallet(name, pin)`
- `importWallet(name, mnemonic, pin)`
- `selectWallet(wallet)`
- `deleteWallet(address)`

#### 5.2 Portfolio Provider

**File**: `lib/providers/portfolio_provider.dart`

State:
- `portfolioValue`
- `assets`
- `performanceData`
- `isLoading`

Actions:
- `loadPortfolio(address)`
- `refreshPrices()`
- `getHistoricalData(period)`

#### 5.3 Settings Provider

**File**: `lib/providers/settings_provider.dart`

State:
- `themeMode`
- `riskThreshold`
- `notificationsEnabled`
- `biometricEnabled`

Actions:
- `loadSettings()`
- `updateSetting(key, value)`

---

### Phase 6: UI Screens Implementation

#### 6.1 Wallet Screens

**Create Wallet Screen**: `lib/screens/wallet/create_wallet_screen.dart`
- Wallet name input
- PIN setup
- PIN confirmation
- Mnemonic display
- Mnemonic verification
- Success confirmation

**Import Wallet Screen**: `lib/screens/wallet/import_wallet_screen.dart`
- Mnemonic input (25 words)
- Wallet name input
- PIN setup
- Import confirmation

**Wallet List Screen**: `lib/screens/wallet/wallet_screen.dart`
- List of wallets with balances
- Add wallet button
- Wallet selection

**Wallet Detail Screen**: `lib/screens/wallet/wallet_detail_screen.dart`
- Balance display
- Send/Receive buttons
- Transaction history
- Asset list

#### 6.2 Transaction Screens

**Send Screen**: `lib/screens/transaction/send_screen.dart`
- Recipient address input (manual or QR)
- Amount input
- Asset selection
- Fee display
- Risk analysis preview
- Confirmation dialog

**Transaction History Screen**: `lib/screens/transaction/transaction_history_screen.dart`
- Filterable transaction list
- Transaction details
- Risk score display

#### 6.3 Portfolio Screens

**Portfolio Screen**: `lib/screens/portfolio/portfolio_screen.dart`
- Total value display
- Asset allocation chart
- Performance chart
- Asset list with values

**Asset Detail Screen**: `lib/screens/portfolio/asset_detail_screen.dart`
- Asset information
- Price chart
- Holdings
- Send/Receive buttons

#### 6.4 Multi-Signature Screens

**Create Multi-Sig Screen**: `lib/screens/multisig/create_multisig_screen.dart`
- Signer address inputs
- Threshold selection
- Wallet name

**Multi-Sig Detail Screen**: `lib/screens/multisig/multisig_detail_screen.dart`
- Signer list
- Pending proposals
- Proposal approval

---

### Phase 7: Backend Integration

#### 7.1 API Service

**File**: `lib/services/api/backend_api_service.dart`

Methods:
- `analyzeTransaction(data)` - POST /api/analysis/risk
- `batchAnalyze(transactions)` - POST /api/analysis/batch
- `getReputation(address)` - GET /api/reputation/{address}
- `auditContract(source, language)` - POST /api/audit/contract
- `analyzePortfolio(addresses)` - POST /api/portfolio/analyze

#### 7.2 WebSocket Service

**File**: `lib/services/api/websocket_service.dart`

Methods:
- `connect()` - Establish connection
- `subscribe(address)` - Subscribe to address alerts
- `unsubscribe(address)` - Unsubscribe
- `disconnect()` - Close connection

---

### Phase 8: New Features

#### 8.1 Recurring Payments

**File**: `lib/services/recurring_payment_service.dart`

Features:
- Schedule recurring transfers
- Configurable intervals (daily, weekly, monthly)
- Automatic execution
- Cancellation option

#### 8.2 Social Recovery

**File**: `lib/services/social_recovery_service.dart`

Features:
- Designate recovery contacts
- Initiate recovery process
- Contact approval flow
- Time-locked execution

#### 8.3 Enhanced Alerts

**File**: `lib/services/alert_service.dart`

Features:
- Price alerts
- Transaction alerts
- Risk threshold alerts
- Custom alert rules

---

### Phase 9: Testing

#### 9.1 Unit Tests

- Test all services
- Test providers
- Test utility functions

#### 9.2 Widget Tests

- Test all screens
- Test common widgets

#### 9.3 Integration Tests

- Test wallet creation flow
- Test transaction flow
- Test multi-sig flow

---

## File Creation Checklist

### Services Layer
- [ ] `lib/services/algorand/algorand_service.dart`
- [ ] `lib/services/algorand/wallet_service.dart`
- [ ] `lib/services/algorand/transaction_service.dart`
- [ ] `lib/services/algorand/multisig_service.dart`
- [ ] `lib/services/algorand/asset_service.dart`
- [ ] `lib/services/storage/secure_storage_service.dart`
- [ ] `lib/services/storage/hive_service.dart`
- [ ] `lib/services/storage/preferences_service.dart`
- [ ] `lib/services/api/backend_api_service.dart`
- [ ] `lib/services/api/websocket_service.dart`
- [ ] `lib/services/portfolio/portfolio_service.dart`
- [ ] `lib/services/portfolio/price_service.dart`
- [ ] `lib/services/auth/biometric_service.dart`

### Models
- [ ] `lib/models/wallet.dart`
- [ ] `lib/models/transaction.dart`
- [ ] `lib/models/asset.dart`
- [ ] `lib/models/alert.dart`
- [ ] `lib/models/portfolio_snapshot.dart`
- [ ] `lib/models/multisig_proposal.dart`
- [ ] `lib/models/risk_analysis.dart`

### Providers
- [ ] `lib/providers/wallet_provider.dart`
- [ ] `lib/providers/portfolio_provider.dart`
- [ ] `lib/providers/settings_provider.dart`
- [ ] `lib/providers/alerts_provider.dart`
- [ ] `lib/providers/auth_provider.dart`

### Screens
- [ ] `lib/screens/wallet/create_wallet_screen.dart`
- [ ] `lib/screens/wallet/import_wallet_screen.dart`
- [ ] `lib/screens/wallet/wallet_screen.dart`
- [ ] `lib/screens/wallet/wallet_detail_screen.dart`
- [ ] `lib/screens/transaction/send_screen.dart`
- [ ] `lib/screens/transaction/transaction_history_screen.dart`
- [ ] `lib/screens/portfolio/portfolio_screen.dart`
- [ ] `lib/screens/portfolio/asset_detail_screen.dart`
- [ ] `lib/screens/multisig/create_multisig_screen.dart`
- [ ] `lib/screens/multisig/multisig_detail_screen.dart`

### Widgets
- [ ] `lib/widgets/wallet/wallet_card.dart`
- [ ] `lib/widgets/wallet/transaction_item.dart`
- [ ] `lib/widgets/wallet/balance_display.dart`
- [ ] `lib/widgets/portfolio/portfolio_chart.dart`
- [ ] `lib/widgets/portfolio/asset_list_tile.dart`
- [ ] `lib/widgets/portfolio/allocation_chart.dart`
- [ ] `lib/widgets/multisig/signer_list.dart`
- [ ] `lib/widgets/multisig/approval_status.dart`

### Configuration
- [ ] `lib/config/app_config.dart`
- [ ] `lib/config/constants.dart`

---

## Execution Order

1. **Update pubspec.yaml** with new dependencies
2. **Run `flutter pub get`** to install dependencies
3. **Create config files** (app_config.dart, constants.dart)
4. **Create data models** with Hive annotations
5. **Run build_runner** to generate adapters
6. **Implement storage services** (secure, hive, preferences)
7. **Implement Algorand services** (algorand, wallet, transaction, multisig)
8. **Implement API services** (backend_api, websocket)
9. **Implement providers** (state management)
10. **Create UI screens** (wallet, transaction, portfolio, multisig)
11. **Create widgets** (reusable components)
12. **Update routing** in app.dart
13. **Write tests**
14. **Test on device/emulator**

---

## Notes

- All sensitive data (mnemonics, private keys) must be stored using `flutter_secure_storage`
- Use Hive for structured data that needs queries
- Use SharedPreferences for simple settings
- All network calls should have proper error handling
- Implement loading states for all async operations
- Add proper logging for debugging

---

*Created: February 2026*