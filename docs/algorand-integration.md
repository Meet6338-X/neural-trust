# Algorand Integration Guide

This document provides detailed guidance on integrating Algorand blockchain functionality into the NeuralTrust Flutter application using the `algorand_dart` SDK.

## Table of Contents

1. [Overview](#overview)
2. [SDK Setup](#sdk-setup)
3. [Network Configuration](#network-configuration)
4. [Wallet Management](#wallet-management)
5. [Transaction Operations](#transaction-operations)
6. [Asset Operations](#asset-operations)
7. [Multi-Signature Support](#multi-signature-support)
8. [Indexer Queries](#indexer-queries)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)

---

## Overview

### What is algorand_dart?

`algorand_dart` is a Dart SDK for interacting with the Algorand blockchain. It provides:

- Account management (creation, import, export)
- Transaction building and signing
- Asset (ASA) operations
- Smart contract interactions
- Indexer queries
- Multi-signature support

### Package Information

```yaml
dependencies:
  algorand_dart: ^1.0.3
```

### Supported Platforms

| Platform | Support |
|----------|---------|
| Android | ✅ Full |
| iOS | ✅ Full |
| Web | ✅ Full |
| macOS | ✅ Full |
| Windows | ✅ Full |
| Linux | ✅ Full |

---

## SDK Setup

### 1. Add Dependency

```yaml
# pubspec.yaml
dependencies:
  algorand_dart: ^1.0.3
```

### 2. Initialize Algorand Client

```dart
// lib/services/algorand/algorand_service.dart
import 'package:algorand_dart/algorand_dart.dart';

class AlgorandService {
  static final AlgorandService _instance = AlgorandService._internal();
  factory AlgorandService() => _instance;
  AlgorandService._internal();
  
  late Algorand _algorand;
  late AlgodClient _algodClient;
  late IndexerClient _indexerClient;
  
  Future<void> initialize({String network = 'testnet'}) async {
    final urls = _getNetworkUrls(network);
    
    _algodClient = AlgodClient(
      apiUrl: urls['algod']!,
      apiKey: urls['apiKey'], // Optional for Algonode
    );
    
    _indexerClient = IndexerClient(
      apiUrl: urls['indexer']!,
      apiKey: urls['apiKey'],
    );
    
    _algorand = Algorand(
      algodClient: _algodClient,
      indexerClient: _indexerClient,
    );
  }
  
  Map<String, String> _getNetworkUrls(String network) {
    switch (network) {
      case 'mainnet':
        return {
          'algod': 'https://mainnet-api.algonode.cloud',
          'indexer': 'https://mainnet-idx.algonode.cloud',
          'apiKey': '', // Not required for Algonode
        };
      case 'testnet':
      default:
        return {
          'algod': 'https://testnet-api.algonode.cloud',
          'indexer': 'https://testnet-idx.algonode.cloud',
          'apiKey': '',
        };
    }
  }
  
  Algorand get algorand => _algorand;
  AlgodClient get algodClient => _algodClient;
  IndexerClient get indexerClient => _indexerClient;
}
```

### 3. Provider Setup

```dart
// lib/providers/algorand_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

final algorandServiceProvider = Provider<AlgorandService>((ref) {
  final service = AlgorandService();
  service.initialize(network: 'testnet');
  return service;
});
```

---

## Network Configuration

### Algonode Endpoints (Free, No API Key Required)

| Network | Algod URL | Indexer URL |
|---------|-----------|-------------|
| Mainnet | `https://mainnet-api.algonode.cloud` | `https://mainnet-idx.algonode.cloud` |
| Testnet | `https://testnet-api.algonode.cloud` | `https://testnet-idx.algonode.cloud` |
| Betanet | `https://betanet-api.algonode.cloud` | `https://betanet-idx.algonode.cloud` |

### PureStake Endpoints (API Key Required)

```dart
final algodClient = AlgodClient(
  apiUrl: 'https://testnet-algorand.api.purestake.io/ps2',
  apiKey: 'YOUR_API_KEY',
);
```

### Custom Node Configuration

```dart
final algodClient = AlgodClient(
  apiUrl: 'http://localhost:4001',
  apiKey: 'your_api_key',
  tokenHeader: 'X-Algo-API-Token',
);
```

---

## Wallet Management

### Create New Wallet

```dart
// lib/services/algorand/wallet_service.dart
class WalletService {
  final AlgorandService _algorandService;
  final SecureStorageService _secureStorage;
  
  Future<WalletInfo> createWallet({
    required String name,
    required String pin,
  }) async {
    // Generate new account
    final account = await Account.random();
    final address = account.address.toString();
    final mnemonic = await account.getMnemonic();
    
    // Encrypt and store mnemonic
    final encryptedMnemonic = _encryptMnemonic(mnemonic, pin);
    await _secureStorage.write(
      key: 'mnemonic_$address',
      value: encryptedMnemonic,
    );
    
    // Store wallet metadata
    final wallet = WalletInfo(
      id: const Uuid().v4(),
      name: name,
      address: address,
      createdAt: DateTime.now(),
      isImported: false,
    );
    
    await _saveWalletMetadata(wallet);
    
    return wallet;
  }
}
```

### Import Wallet from Mnemonic

```dart
Future<WalletInfo> importWallet({
  required String name,
  required String mnemonic,
  required String pin,
}) async {
  try {
    // Validate mnemonic
    if (!_validateMnemonic(mnemonic)) {
      throw WalletException('Invalid mnemonic phrase');
    }
    
    // Create account from mnemonic
    final account = await Account.fromMnemonic(mnemonic);
    final address = account.address.toString();
    
    // Check if wallet already exists
    if (await _walletExists(address)) {
      throw WalletException('Wallet already imported');
    }
    
    // Encrypt and store
    final encryptedMnemonic = _encryptMnemonic(mnemonic, pin);
    await _secureStorage.write(
      key: 'mnemonic_$address',
      value: encryptedMnemonic,
    );
    
    final wallet = WalletInfo(
      id: const Uuid().v4(),
      name: name,
      address: address,
      createdAt: DateTime.now(),
      isImported: true,
    );
    
    await _saveWalletMetadata(wallet);
    
    return wallet;
  } catch (e) {
    throw WalletException('Failed to import wallet: $e');
  }
}
```

### Get Account from Storage

```dart
Future<Account?> getAccount(String address, String pin) async {
  final encryptedMnemonic = await _secureStorage.read(
    key: 'mnemonic_$address',
  );
  
  if (encryptedMnemonic == null) return null;
  
  final mnemonic = _decryptMnemonic(encryptedMnemonic, pin);
  return await Account.fromMnemonic(mnemonic);
}
```

### Mnemonic Validation

```dart
bool _validateMnemonic(String mnemonic) {
  final words = mnemonic.trim().split(' ');
  
  // Must be 25 words
  if (words.length != 25) return false;
  
  // Validate each word is in the BIP39 wordlist
  for (final word in words) {
    if (!bip39Wordlist.contains(word.toLowerCase())) {
      return false;
    }
  }
  
  return true;
}
```

### Mnemonic Encryption

```dart
import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart';

String _encryptMnemonic(String mnemonic, String pin) {
  // Derive key from PIN
  final key = Key.fromUtf8(
    sha256.convert(utf8.encode(pin)).toString().substring(0, 32),
  );
  
  final iv = IV.fromLength(16);
  final encrypter = Encrypter(AES(key));
  
  return encrypter.encrypt(mnemonic, iv: iv).base64;
}

String _decryptMnemonic(String encrypted, String pin) {
  final key = Key.fromUtf8(
    sha256.convert(utf8.encode(pin)).toString().substring(0, 32),
  );
  
  final iv = IV.fromLength(16);
  final encrypter = Encrypter(AES(key));
  
  return encrypter.decrypt64(encrypted, iv: iv);
}
```

---

## Transaction Operations

### Get Suggested Transaction Parameters

```dart
Future<SuggestedParams> getSuggestedParams() async {
  return await _algorandService.algodClient.transactionParams();
}
```

### Send ALGO Payment

```dart
Future<String> sendAlgo({
  required Account account,
  required String recipient,
  required double amount,
  String? note,
}) async {
  // Get suggested params
  final params = await getSuggestedParams();
  
  // Build transaction
  final transaction = PaymentTransaction.builder()
    .sender(account.address)
    .receiver(Address.fromAlgorandAddress(recipient))
    .amount((amount * 1e6).toInt()) // Convert to microAlgos
    .suggestedParams(params)
    .note(note != null ? utf8.encode(note) : null)
    .build();
  
  // Sign transaction
  final signedTx = await transaction.sign(account);
  
  // Send transaction
  final txId = await _algorandService.algorand.sendTransaction(signedTx);
  
  return txId;
}
```

### Send with Fee Override

```dart
Future<String> sendWithCustomFee({
  required Account account,
  required String recipient,
  required int amount,
  int? fee,
}) async {
  final params = await getSuggestedParams();
  
  if (fee != null) {
    params.fee = fee;
  }
  
  final transaction = PaymentTransaction.builder()
    .sender(account.address)
    .receiver(Address.fromAlgorandAddress(recipient))
    .amount(amount)
    .suggestedParams(params)
    .build();
  
  final signedTx = await transaction.sign(account);
  return await _algorandService.algorand.sendTransaction(signedTx);
}
```

### Wait for Transaction Confirmation

```dart
Future<PendingTransaction> waitForConfirmation(String txId) async {
  final response = await _algorandService.algorand.waitForConfirmation(
    txId,
    timeout: 60, // seconds
  );
  return response;
}
```

### Get Transaction Status

```dart
Future<TransactionStatus> getTransactionStatus(String txId) async {
  try {
    final pendingTx = await _algorandService.algodClient.pendingTransaction(txId);
    
    if (pendingTx.confirmedRound != null && pendingTx.confirmedRound! > 0) {
      return TransactionStatus.confirmed;
    } else if (pendingTx.poolError != null && pendingTx.poolError!.isNotEmpty) {
      return TransactionStatus.rejected;
    } else {
      return TransactionStatus.pending;
    }
  } catch (e) {
    return TransactionStatus.unknown;
  }
}
```

### Get Account Balance

```dart
Future<AccountBalance> getBalance(String address) async {
  final accountInfo = await _algorandService.algodClient.account(address);
  
  return AccountBalance(
    address: address,
    algoBalance: accountInfo.amount / 1e6,
    microAlgoBalance: accountInfo.amount,
    assets: accountInfo.assets?.map((asset) => AssetHolding(
      assetId: asset.assetId,
      amount: asset.amount,
      isFrozen: asset.isFrozen,
    )).toList() ?? [],
    minBalance: accountInfo.minBalance,
  );
}
```

---

## Asset Operations

### Opt-In to Asset

```dart
Future<String> optInToAsset({
  required Account account,
  required int assetId,
}) async {
  final params = await getSuggestedParams();
  
  final transaction = AssetOptInTransaction.builder()
    .sender(account.address)
    .assetId(assetId)
    .suggestedParams(params)
    .build();
  
  final signedTx = await transaction.sign(account);
  return await _algorandService.algorand.sendTransaction(signedTx);
}
```

### Send Asset (ASA)

```dart
Future<String> sendAsset({
  required Account account,
  required String recipient,
  required int assetId,
  required int amount,
}) async {
  // Check if recipient is opted in
  final recipientAccount = await _algorandService.algodClient.account(recipient);
  final isOptedIn = recipientAccount.assets?.any((a) => a.assetId == assetId) ?? false;
  
  if (!isOptedIn) {
    throw AssetException('Recipient is not opted in to this asset');
  }
  
  final params = await getSuggestedParams();
  
  final transaction = AssetTransferTransaction.builder()
    .sender(account.address)
    .receiver(Address.fromAlgorandAddress(recipient))
    .assetId(assetId)
    .amount(amount)
    .suggestedParams(params)
    .build();
  
  final signedTx = await transaction.sign(account);
  return await _algorandService.algorand.sendTransaction(signedTx);
}
```

### Get Asset Information

```dart
Future<AssetInfo> getAssetInfo(int assetId) async {
  final asset = await _algorandService.algodClient.asset(assetId);
  
  return AssetInfo(
    assetId: assetId,
    name: asset.params.name,
    unitName: asset.params.unitName,
    total: asset.params.total,
    decimals: asset.params.decimals,
    creator: asset.params.creator,
    url: asset.params.url,
    isFrozen: asset.params.defaultFrozen,
  );
}
```

---

## Multi-Signature Support

### Create Multi-Signature Address

```dart
Future<MultisigAddress> createMultisigAddress({
  required List<String> signerAddresses,
  required int threshold,
  int version = 1,
}) async {
  final addresses = signerAddresses
      .map((addr) => Address.fromAlgorandAddress(addr))
      .toList();
  
  return MultisigAddress(
    version: version,
    threshold: threshold,
    addresses: addresses,
  );
}
```

### Sign Multi-Signature Transaction

```dart
Future<SignedTransaction> signMultisigTransaction({
  required MultisigAddress multisig,
  required Account signer,
  required Transaction transaction,
}) async {
  // Sign the transaction with the account
  final signedTx = await transaction.sign(signer);
  
  // Create multisig signature
  return SignedTransaction(
    transaction: transaction,
    multisigSignature: MultisigSignature(
      version: multisig.version,
      threshold: multisig.threshold,
      subsignatures: [
        MultisigSubsig(
          publicKey: signer.publicKey,
          signature: signedTx.signature,
        ),
      ],
    ),
  );
}
```

### Merge Multi-Signature Signatures

```dart
SignedTransaction mergeMultisigSignatures({
  required Transaction transaction,
  required List<SignedTransaction> signedTransactions,
}) {
  final allSubsigs = <MultisigSubsig>[];
  
  for (final signedTx in signedTransactions) {
    if (signedTx.multisigSignature != null) {
      allSubsigs.addAll(signedTx.multisigSignature!.subsignatures);
    }
  }
  
  return SignedTransaction(
    transaction: transaction,
    multisigSignature: MultisigSignature(
      version: signedTransactions.first.multisigSignature!.version,
      threshold: signedTransactions.first.multisigSignature!.threshold,
      subsignatures: allSubsigs,
    ),
  );
}
```

### Submit Multi-Signature Transaction

```dart
Future<String> submitMultisigTransaction({
  required List<SignedTransaction> signedTransactions,
}) async {
  // Merge all signatures
  final mergedTx = mergeMultisigSignatures(
    transaction: signedTransactions.first.transaction,
    signedTransactions: signedTransactions,
  );
  
  // Submit to network
  return await _algorandService.algorand.sendTransaction(mergedTx);
}
```

---

## Indexer Queries

### Get Transaction History

```dart
Future<List<TransactionInfo>> getTransactionHistory(
  String address, {
  int? limit,
  DateTime? afterDate,
  String? nextToken,
}) async {
  final response = await _algorandService.indexerClient.transactions(
    address: address,
    limit: limit ?? 100,
    afterTime: afterDate?.toUtc().toIso8601String(),
    next: nextToken,
  );
  
  return response.transactions.map((tx) => TransactionInfo(
    txId: tx.id,
    sender: tx.sender,
    receiver: tx.paymentTransaction?.receiver,
    amount: tx.paymentTransaction?.amount ?? 0,
    fee: tx.fee,
    round: tx.confirmedRound,
    timestamp: DateTime.fromMillisecondsSinceEpoch(
      tx.roundTime * 1000,
    ),
    type: tx.txType,
  )).toList();
}
```

### Get Asset Holders

```dart
Future<List<AssetHolder>> getAssetHolders(int assetId) async {
  final response = await _algorandService.indexerClient.assetBalances(
    assetId: assetId,
  );
  
  return response.balances.map((balance) => AssetHolder(
    address: balance.address,
    amount: balance.amount,
    isFrozen: balance.isFrozen,
  )).toList();
}
```

### Search Transactions

```dart
Future<List<TransactionInfo>> searchTransactions({
  String? address,
  int? assetId,
  int? minAmount,
  int? maxAmount,
  String? txType,
}) async {
  final response = await _algorandService.indexerClient.searchTransactions(
    address: address,
    assetId: assetId,
    currencyGreaterThan: minAmount,
    currencyLessThan: maxAmount,
    txType: txType,
  );
  
  return response.transactions.map(_mapTransaction).toList();
}
```

---

## Error Handling

### Common Errors

```dart
enum AlgorandError {
  networkError,
  insufficientBalance,
  invalidAddress,
  invalidMnemonic,
  transactionRejected,
  assetNotOptedIn,
  frozenAsset,
  unknown,
}

class AlgorandException implements Exception {
  final AlgorandError error;
  final String message;
  
  AlgorandException(this.error, this.message);
  
  factory AlgorandException.fromError(dynamic error) {
    if (error is AlgorandApiException) {
      switch (error.statusCode) {
        case 400:
          return AlgorandException(
            AlgorandError.transactionRejected,
            error.message,
          );
        case 404:
          return AlgorandException(
            AlgorandError.invalidAddress,
            'Address or resource not found',
          );
        default:
          return AlgorandException(
            AlgorandError.networkError,
            error.message,
          );
      }
    }
    
    return AlgorandException(
      AlgorandError.unknown,
      error.toString(),
    );
  }
}
```

### Error Handling Example

```dart
Future<String?> sendTransactionSafely({
  required Account account,
  required String recipient,
  required int amount,
}) async {
  try {
    return await sendAlgo(
      account: account,
      recipient: recipient,
      amount: amount,
    );
  } on AlgorandApiException catch (e) {
    if (e.message.contains('overspend')) {
      throw AlgorandException(
        AlgorandError.insufficientBalance,
        'Insufficient balance for transaction',
      );
    }
    rethrow;
  } catch (e) {
    throw AlgorandException.fromError(e);
  }
}
```

---

## Best Practices

### 1. Secure Key Storage

```dart
// Always use secure storage for private keys
await FlutterSecureStorage().write(
  key: 'mnemonic_$address',
  value: encryptedMnemonic,
);
```

### 2. Transaction Validation

```dart
// Always validate before sending
Future<void> validateTransaction({
  required String sender,
  required String recipient,
  required int amount,
}) async {
  // Validate addresses
  if (!Address.isValid(sender)) {
    throw ValidationException('Invalid sender address');
  }
  if (!Address.isValid(recipient)) {
    throw ValidationException('Invalid recipient address');
  }
  
  // Validate amount
  if (amount <= 0) {
    throw ValidationException('Amount must be positive');
  }
  
  // Check balance
  final balance = await getBalance(sender);
  if (balance.microAlgoBalance < amount + 1000) { // Include fee
    throw ValidationException('Insufficient balance');
  }
}
```

### 3. Fee Management

```dart
// Use suggested fee with fallback
Future<int> getSuggestedFee() async {
  try {
    final params = await getSuggestedParams();
    return params.fee;
  } catch (e) {
    return 1000; // Minimum fee fallback
  }
}
```

### 4. Retry Logic

```dart
Future<T> withRetry<T>(
  Future<T> Function() operation, {
  int maxRetries = 3,
  Duration delay = const Duration(seconds: 1),
}) async {
  for (int i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (e) {
      if (i == maxRetries - 1) rethrow;
      await Future.delayed(delay * (i + 1));
    }
  }
  throw Exception('Max retries exceeded');
}
```

### 5. Caching

```dart
class CachedBalanceService {
  final Map<String, CachedBalance> _cache = {};
  
  Future<AccountBalance> getBalance(String address) async {
    final cached = _cache[address];
    if (cached != null && !cached.isExpired) {
      return cached.balance;
    }
    
    final balance = await _fetchBalance(address);
    _cache[address] = CachedBalance(
      balance: balance,
      timestamp: DateTime.now(),
    );
    
    return balance;
  }
}
```

---

## Testing

### Unit Testing with Mocks

```dart
// test/services/algorand_service_test.dart
void main() {
  late AlgorandService service;
  late MockAlgodClient mockAlgod;
  
  setUp(() {
    mockAlgod = MockAlgodClient();
    service = AlgorandService();
  });
  
  test('getBalance returns correct balance', () async {
    // Arrange
    when(() => mockAlgod.account(any()))
        .thenAnswer((_) async => AccountInfo(amount: 1000000));
    
    // Act
    final balance = await service.getBalance('TEST_ADDRESS');
    
    // Assert
    expect(balance.algoBalance, equals(1.0));
  });
}
```

### Integration Testing on Testnet

```dart
test('sendTransaction on testnet', () async {
  // Use funded testnet account
  final account = await Account.fromMnemonic(testMnemonic);
  
  final txId = await service.sendAlgo(
    account: account,
    recipient: testRecipient,
    amount: 0.001,
  );
  
  expect(txId, isNotEmpty);
  
  // Wait for confirmation
  final confirmed = await service.waitForConfirmation(txId);
  expect(confirmed.confirmedRound, greaterThan(0));
}, timeout: Timeout(Duration(minutes: 1)));
```

---

*Last Updated: February 2026*
