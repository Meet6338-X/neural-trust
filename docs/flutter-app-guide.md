# Flutter App Development Guide

This guide covers the development, architecture, and implementation details of the NeuralTrust Flutter mobile application.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Dependencies](#dependencies)
3. [Project Structure](#project-structure)
4. [Core Services](#core-services)
5. [State Management](#state-management)
6. [Navigation](#navigation)
7. [UI Components](#ui-components)
8. [Algorand Integration](#algorand-integration)
9. [Local Storage](#local-storage)
10. [Testing](#testing)

---

## Project Setup

### Prerequisites

- Flutter SDK 3.10+
- Dart SDK 3.0+
- Android Studio / Xcode (for platform-specific builds)
- VS Code with Flutter extension (recommended)

### Initial Setup

```bash
# Navigate to Flutter project
cd NeuralTrust

# Install dependencies
flutter pub get

# Run on connected device
flutter run

# Build for specific platform
flutter build apk        # Android
flutter build ios        # iOS
flutter build web        # Web
```

### Environment Configuration

Create environment-specific configurations:

```dart
// lib/config/app_config.dart
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  static const String algorandNetwork = String.fromEnvironment(
    'ALGORAND_NETWORK',
    defaultValue: 'testnet',
  );
}
```

---

## Dependencies

### Current Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # UI
  cupertino_icons: ^1.0.8
  go_router: ^14.6.2
  fl_chart: ^0.68.0
  shimmer: ^3.0.0
  
  # State Management
  flutter_riverpod: ^2.6.1
  
  # Firebase
  firebase_core: ^3.6.0
  firebase_auth: ^5.3.1
  cloud_firestore: ^5.4.4
  
  # Storage & Connectivity
  connectivity_plus: ^6.1.0
  flutter_secure_storage: ^9.2.4
```

### Required New Dependencies

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
```

---

## Project Structure

```
lib/
├── main.dart                    # App entry point
├── app.dart                     # App configuration and routing
│
├── config/
│   ├── app_config.dart          # Environment configuration
│   └── constants.dart           # App constants
│
├── models/
│   ├── wallet.dart              # Wallet data model
│   ├── transaction.dart         # Transaction model
│   ├── portfolio.dart           # Portfolio model
│   ├── risk_analysis.dart       # Risk analysis result
│   ├── alert.dart               # Alert notification
│   └── multisig_wallet.dart     # Multi-sig wallet model
│
├── services/
│   ├── algorand/
│   │   ├── algorand_service.dart
│   │   ├── wallet_service.dart
│   │   ├── transaction_service.dart
│   │   ├── multisig_service.dart
│   │   └── asset_service.dart
│   ├── storage/
│   │   ├── local_storage_service.dart
│   │   ├── secure_storage_service.dart
│   │   └── cache_service.dart
│   ├── api/
│   │   ├── backend_api_service.dart
│   │   └── websocket_service.dart
│   ├── portfolio/
│   │   ├── portfolio_service.dart
│   │   └── price_service.dart
│   └── auth/
│       ├── biometric_service.dart
│       └── auth_service.dart
│
├── providers/
│   ├── wallet_provider.dart
│   ├── portfolio_provider.dart
│   ├── settings_provider.dart
│   ├── alerts_provider.dart
│   └── auth_provider.dart
│
├── screens/
│   ├── onboarding/
│   │   ├── get_started_screen.dart
│   │   ├── create_wallet_screen.dart
│   │   └── import_wallet_screen.dart
│   ├── dashboard/
│   │   └── dashboard_screen.dart
│   ├── wallet/
│   │   ├── wallet_screen.dart
│   │   ├── wallet_detail_screen.dart
│   │   └── transaction_history_screen.dart
│   ├── portfolio/
│   │   ├── portfolio_screen.dart
│   │   └── asset_detail_screen.dart
│   ├── risk/
│   │   └── risk_screen.dart
│   ├── alerts/
│   │   └── alerts_screen.dart
│   ├── settings/
│   │   └── settings_screen.dart
│   ├── profile/
│   │   └── profile_screen.dart
│   └── multisig/
│       ├── create_multisig_screen.dart
│       └── multisig_detail_screen.dart
│
├── widgets/
│   ├── common/
│   │   ├── bottom_nav_bar.dart
│   │   ├── feature_card.dart
│   │   ├── risk_score_card.dart
│   │   ├── stats_card.dart
│   │   ├── loading_indicator.dart
│   │   └── error_display.dart
│   ├── wallet/
│   │   ├── wallet_card.dart
│   │   ├── transaction_item.dart
│   │   └── balance_display.dart
│   ├── portfolio/
│   │   ├── portfolio_chart.dart
│   │   ├── asset_list_tile.dart
│   │   └── allocation_chart.dart
│   └── multisig/
│       ├── signer_list.dart
│       └── approval_status.dart
│
└── theme/
    ├── app_theme.dart
    ├── colors.dart
    └── text_styles.dart
```

---

## Core Services

### 1. Algorand Service

Main service for blockchain interactions:

```dart
// lib/services/algorand/algorand_service.dart
import 'package:algorand_dart/algorand_dart.dart';

class AlgorandService {
  late Algorand _algorand;
  late AlgodClient _algodClient;
  late IndexerClient _indexerClient;
  
  static const String testnetAlgodUrl = 'https://testnet-api.algonode.cloud';
  static const String testnetIndexerUrl = 'https://testnet-idx.algonode.cloud';
  
  Future<void> initialize() async {
    _algodClient = AlgodClient(apiUrl: testnetAlgodUrl);
    _indexerClient = IndexerClient(apiUrl: testnetIndexerUrl);
    _algorand = Algorand(
      algodClient: _algodClient,
      indexerClient: _indexerClient,
    );
  }
  
  Future<Account> createAccount() async {
    return await Account.random();
  }
  
  Future<Account> importAccount(String mnemonic) async {
    return await Account.fromMnemonic(mnemonic);
  }
  
  Future<int> getBalance(String address) async {
    final accountInfo = await _algodClient.getAccount(address);
    return accountInfo.amount;
  }
  
  Future<String> sendTransaction({
    required Account account,
    required String recipient,
    required int amount,
    String? note,
  }) async {
    final params = await _algodClient.getTransactionParams();
    
    final transaction = PaymentTransaction.builder()
      .sender(account.address)
      .receiver(Address.fromAlgorandAddress(recipient))
      .amount(amount)
      .suggestedParams(params)
      .note(note != null ? utf8.encode(note) : null)
      .build();
    
    final signedTx = await transaction.sign(account);
    final txId = await _algorand.sendTransaction(signedTx);
    
    return txId;
  }
}
```

### 2. Wallet Service

Manages wallet creation, import, and storage:

```dart
// lib/services/algorand/wallet_service.dart
class WalletService {
  final SecureStorageService _secureStorage;
  final AlgorandService _algorandService;
  
  Future<Wallet> createWallet(String name, String pin) async {
    final account = await _algorandService.createAccount();
    final mnemonic = await account.getMnemonic();
    
    final wallet = Wallet(
      id: uuid.v4(),
      name: name,
      address: account.address.toString(),
      createdAt: DateTime.now(),
    );
    
    // Encrypt and store mnemonic
    await _secureStorage.write(
      key: 'wallet_${wallet.id}',
      value: _encryptMnemonic(mnemonic, pin),
    );
    
    return wallet;
  }
  
  Future<Wallet?> importWallet(String name, String mnemonic, String pin) async {
    final account = await _algorandService.importAccount(mnemonic);
    
    final wallet = Wallet(
      id: uuid.v4(),
      name: name,
      address: account.address.toString(),
      createdAt: DateTime.now(),
      isImported: true,
    );
    
    await _secureStorage.write(
      key: 'wallet_${wallet.id}',
      value: _encryptMnemonic(mnemonic, pin),
    );
    
    return wallet;
  }
  
  Future<Account?> getAccount(String walletId, String pin) async {
    final encrypted = await _secureStorage.read(key: 'wallet_$walletId');
    if (encrypted == null) return null;
    
    final mnemonic = _decryptMnemonic(encrypted, pin);
    return await _algorandService.importAccount(mnemonic);
  }
}
```

### 3. Local Storage Service

Handles persistent data storage:

```dart
// lib/services/storage/local_storage_service.dart
class LocalStorageService {
  late HiveInterface _hive;
  
  Future<void> initialize() async {
    await Hive.initFlutter();
    
    // Register adapters
    Hive.registerAdapter(WalletAdapter());
    Hive.registerAdapter(TransactionAdapter());
    Hive.registerAdapter(PortfolioAdapter());
    
    // Open boxes
    await Hive.openBox<Wallet>('wallets');
    await Hive.openBox<Transaction>('transactions');
    await Hive.openBox('settings');
  }
  
  // Wallet operations
  Future<void> saveWallet(Wallet wallet) async {
    final box = Hive.box<Wallet>('wallets');
    await box.put(wallet.id, wallet);
  }
  
  List<Wallet> getWallets() {
    return Hive.box<Wallet>('wallets').values.toList();
  }
  
  // Settings operations
  Future<void> setSetting(String key, dynamic value) async {
    final box = Hive.box('settings');
    await box.put(key, value);
  }
  
  T? getSetting<T>(String key, {T? defaultValue}) {
    final box = Hive.box('settings');
    return box.get(key, defaultValue: defaultValue) as T?;
  }
}
```

### 4. Backend API Service

Communicates with the FastAPI backend:

```dart
// lib/services/api/backend_api_service.dart
class BackendApiService {
  final Dio _dio;
  final String baseUrl;
  
  BackendApiService({
    required this.baseUrl,
  }) : _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: Duration(seconds: 30),
    receiveTimeout: Duration(seconds: 30),
  ));
  
  // Risk Analysis
  Future<RiskAnalysis> analyzeTransaction(TransactionData data) async {
    final response = await _dio.post('/api/analysis/risk', data: data.toJson());
    return RiskAnalysis.fromJson(response.data);
  }
  
  // Portfolio Analysis
  Future<PortfolioAnalysis> analyzePortfolio(List<String> addresses) async {
    final response = await _dio.post('/api/portfolio/analyze', data: {
      'addresses': addresses,
    });
    return PortfolioAnalysis.fromJson(response.data);
  }
  
  // Address Reputation
  Future<AddressReputation> getReputation(String address) async {
    final response = await _dio.get('/api/reputation/$address');
    return AddressReputation.fromJson(response.data);
  }
  
  // Contract Audit
  Future<ContractAudit> auditContract(String sourceCode, String language) async {
    final response = await _dio.post('/api/audit/contract', data: {
      'source_code': sourceCode,
      'language': language,
    });
    return ContractAudit.fromJson(response.data);
  }
}
```

---

## State Management

Using Riverpod for state management:

### Provider Structure

```dart
// lib/providers/wallet_provider.dart
final walletProvider = StateNotifierProvider<WalletNotifier, WalletState>((ref) {
  return WalletNotifier(
    walletService: ref.watch(walletServiceProvider),
    storageService: ref.watch(storageServiceProvider),
  );
});

class WalletState {
  final List<Wallet> wallets;
  final Wallet? selectedWallet;
  final bool isLoading;
  final String? error;
  
  WalletState({
    this.wallets = const [],
    this.selectedWallet,
    this.isLoading = false,
    this.error,
  });
}

class WalletNotifier extends StateNotifier<WalletState> {
  final WalletService _walletService;
  final LocalStorageService _storageService;
  
  WalletNotifier({
    required WalletService walletService,
    required LocalStorageService storageService,
  }) : _walletService = walletService,
       _storageService = storageService,
       super(WalletState()) {
    loadWallets();
  }
  
  Future<void> loadWallets() async {
    state = state.copyWith(isLoading: true);
    try {
      final wallets = _storageService.getWallets();
      state = state.copyWith(wallets: wallets, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }
  
  Future<void> createWallet(String name, String pin) async {
    state = state.copyWith(isLoading: true);
    try {
      final wallet = await _walletService.createWallet(name, pin);
      await _storageService.saveWallet(wallet);
      state = state.copyWith(
        wallets: [...state.wallets, wallet],
        selectedWallet: wallet,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }
}
```

---

## Navigation

Using go_router for declarative routing:

```dart
// lib/app.dart
final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/onboarding',
    routes: [
      // Onboarding
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const GetStartedScreen(),
      ),
      GoRoute(
        path: '/create-wallet',
        builder: (context, state) => const CreateWalletScreen(),
      ),
      GoRoute(
        path: '/import-wallet',
        builder: (context, state) => const ImportWalletScreen(),
      ),
      
      // Main App (with bottom nav)
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/wallet',
            builder: (context, state) => const WalletScreen(),
          ),
          GoRoute(
            path: '/portfolio',
            builder: (context, state) => const PortfolioScreen(),
          ),
          GoRoute(
            path: '/risk',
            builder: (context, state) => const RiskScreen(),
          ),
          GoRoute(
            path: '/alerts',
            builder: (context, state) => const AlertsScreen(),
          ),
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),
      
      // Detail screens
      GoRoute(
        path: '/wallet/:id',
        builder: (context, state) => WalletDetailScreen(
          walletId: state.pathParameters['id']!,
        ),
      ),
      GoRoute(
        path: '/asset/:id',
        builder: (context, state) => AssetDetailScreen(
          assetId: state.pathParameters['id']!,
        ),
      ),
    ],
  );
});
```

---

## UI Components

### Theme

```dart
// lib/theme/app_theme.dart
class AppTheme {
  static const Color primaryColor = Color(0xFF6C63FF);
  static const Color secondaryColor = Color(0xFF4ECDC4);
  static const Color accentColor = Color(0xFFFF6B6B);
  static const Color successColor = Color(0xFF4CAF50);
  static const Color warningColor = Color(0xFFFFC107);
  static const Color dangerColor = Color(0xFFF44336);
  static const Color backgroundColor = Color(0xFF1A1A2E);
  
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: backgroundColor,
      colorScheme: ColorScheme.dark(
        primary: primaryColor,
        secondary: secondaryColor,
        error: dangerColor,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: backgroundColor,
        elevation: 0,
      ),
      cardTheme: CardTheme(
        color: Color(0xFF16213E),
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
    );
  }
}
```

### Common Widgets

```dart
// lib/widgets/common/risk_score_card.dart
class RiskScoreCard extends StatelessWidget {
  final int riskScore;
  final String recommendation;
  final String reasoning;
  
  const RiskScoreCard({
    required this.riskScore,
    required this.recommendation,
    required this.reasoning,
  });
  
  Color get _scoreColor {
    if (riskScore <= 30) return AppTheme.successColor;
    if (riskScore <= 60) return AppTheme.warningColor;
    return AppTheme.dangerColor;
  }
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Risk Score', style: AppTheme.heading3),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _scoreColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '$riskScore',
                    style: TextStyle(
                      color: _scoreColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            LinearProgressIndicator(
              value: riskScore / 100,
              backgroundColor: Colors.grey[800],
              valueColor: AlwaysStoppedAnimation(_scoreColor),
            ),
            SizedBox(height: 16),
            Text(reasoning, style: AppTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}
```

---

## Algorand Integration

### Transaction Building

```dart
// lib/services/algorand/transaction_service.dart
class TransactionService {
  final AlgorandService _algorandService;
  
  Future<PendingTransaction> sendAlgo({
    required Account account,
    required String recipient,
    required double amount,
    String? note,
  }) async {
    final params = await _algorandService.getSuggestedParams();
    
    final transaction = PaymentTransaction.builder()
      .sender(account.address)
      .receiver(Address.fromAlgorandAddress(recipient))
      .amount((amount * 1e6).toInt()) // Convert to microAlgos
      .suggestedParams(params)
      .note(note != null ? utf8.encode(note) : null)
      .build();
    
    final signedTx = await transaction.sign(account);
    return await _algorandService.sendTransaction(signedTx);
  }
  
  Future<PendingTransaction> sendAsset({
    required Account account,
    required String recipient,
    required int assetId,
    required int amount,
  }) async {
    final params = await _algorandService.getSuggestedParams();
    
    final transaction = AssetTransferTransaction.builder()
      .sender(account.address)
      .receiver(Address.fromAlgorandAddress(recipient))
      .assetId(assetId)
      .amount(amount)
      .suggestedParams(params)
      .build();
    
    final signedTx = await transaction.sign(account);
    return await _algorandService.sendTransaction(signedTx);
  }
}
```

### Multi-Signature Support

```dart
// lib/services/algorand/multisig_service.dart
class MultisigService {
  Future<MultisigAddress> createMultisig({
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
  
  Future<SignedTransaction> signMultisigTransaction({
    required MultisigAddress multisig,
    required Account signer,
    required Transaction transaction,
  }) async {
    final signedTx = await transaction.sign(signer);
    
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
  
  Future<String> submitMultisig({
    required List<SignedTransaction> signedTransactions,
  }) async {
    // Merge signatures and submit
    final mergedTx = _mergeSignatures(signedTransactions);
    return await _algorandService.sendTransaction(mergedTx);
  }
}
```

---

## Local Storage

### Secure Storage (Keys/Mnemonics)

```dart
// lib/services/storage/secure_storage_service.dart
class SecureStorageService {
  final FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );
  
  Future<void> write({required String key, required String value}) async {
    await _storage.write(key: key, value: value);
  }
  
  Future<String?> read({required String key}) async {
    return await _storage.read(key: key);
  }
  
  Future<void> delete({required String key}) async {
    await _storage.delete(key: key);
  }
  
  Future<void> deleteAll() async {
    await _storage.deleteAll();
  }
}
```

### Hive Storage (Models)

```dart
// lib/models/wallet.dart
@HiveType(typeId: 0)
class Wallet extends HiveObject {
  @HiveField(0)
  String id;
  
  @HiveField(1)
  String name;
  
  @HiveField(2)
  String address;
  
  @HiveField(3)
  DateTime createdAt;
  
  @HiveField(4)
  bool isImported;
  
  @HiveField(5)
  bool isMultisig;
  
  @HiveField(6)
  int? threshold;
  
  @HiveField(7)
  List<String>? signers;
}
```

---

## Testing

### Unit Tests

```dart
// test/services/wallet_service_test.dart
void main() {
  late WalletService walletService;
  late MockSecureStorage mockStorage;
  late MockAlgorandService mockAlgorand;
  
  setUp(() {
    mockStorage = MockSecureStorage();
    mockAlgorand = MockAlgorandService();
    walletService = WalletService(mockStorage, mockAlgorand);
  });
  
  test('createWallet creates and stores wallet', () async {
    // Arrange
    when(mockAlgorand.createAccount()).thenReturn(mockAccount);
    
    // Act
    final wallet = await walletService.createWallet('Test Wallet', '1234');
    
    // Assert
    expect(wallet.name, 'Test Wallet');
    verify(mockStorage.write(key: anyNamed('key'), value: anyNamed('value')));
  });
}
```

### Widget Tests

```dart
// test/widgets/risk_score_card_test.dart
void main() {
  testWidgets('RiskScoreCard displays correct score', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: RiskScoreCard(
          riskScore: 45,
          recommendation: 'WARN',
          reasoning: 'Test reasoning',
        ),
      ),
    ));
    
    expect(find.text('45'), findsOneWidget);
    expect(find.text('Test reasoning'), findsOneWidget);
  });
}
```

---

## Build Commands

```bash
# Development
flutter run

# Build APK
flutter build apk --release

# Build iOS
flutter build ios --release

# Build Web
flutter build web --release

# Analyze code
flutter analyze

# Run tests
flutter test

# Generate code (Hive adapters, etc.)
flutter packages pub run build_runner build
```

---

*Last Updated: February 2026*
