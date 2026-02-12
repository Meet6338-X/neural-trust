# ChainGuardian

AI-Powered DeFi Risk & Compliance Assistant built on Algorand blockchain with Firebase backend.

## 🚀 Features

- **Real-time Risk Assessment**: AI-powered risk scoring for DeFi transactions
- **Smart Contract Enforcement**: On-chain validation with Algorand
- **Firebase Integration**: Serverless backend with Firestore and Authentication
- **Cross-Platform**: Flutter app for iOS, Android, Web, and Desktop
- **Free Tier Optimized**: Minimal database operations for cost efficiency

## 📋 Prerequisites

- Flutter SDK 3.10+
- Dart 3.0+
- Firebase account (free tier)
- Git

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd neuraltrust
```

### 2. Install Dependencies

```bash
flutter pub get
```

### 3. Firebase Configuration

The project is already configured with Firebase project `chainguardian-ai`. The configuration is in `lib/firebase_options.dart`.

If you need to use your own Firebase project:

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable Authentication (Anonymous auth for testing)
3. Enable Firestore Database
4. Copy your Firebase config and update `lib/firebase_options.dart`

### 4. Firestore Security Rules

The project includes minimal security rules in `firestore.rules`:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Risk scores - users can read their own, system can write
    match /risk_scores/{scoreId} {
      allow read: if request.auth != null && resource.data.user_id == request.auth.uid;
      allow write: if request.auth != null;
    }
    
    // Alerts - users can read/write their own
    match /alerts/{alertId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
  }
}
```

### 5. Run the Application

#### Android (Primary Platform)
```bash
# Connect your Android device via USB or start an emulator
flutter devices

# Run on Android
flutter run -d android
```

#### Web
```bash
flutter run -d chrome
```

#### iOS
```bash
flutter run -d ios
```

#### Desktop (Windows/macOS/Linux)
```bash
flutter run -d windows
# or
flutter run -d macos
# or
flutter run -d linux
```

### Android Setup Notes

The Android app is configured with:
- Package name: `com.example.neuraltrust`
- Firebase configuration: `android/app/google-services.json`
- Google Services plugin: Added to `android/app/build.gradle.kts`

If you need to use a different package name:
1. Update `android/app/build.gradle.kts` with your package name
2. Create a new Android app in Firebase Console
3. Download the new `google-services.json`
4. Update `lib/firebase_options.dart` with the new configuration

## 📁 Project Structure

```
neuraltrust/
├── lib/
│   ├── main.dart              # App entry point
│   ├── app.dart               # Main app with auth and dashboard
│   └── firebase_options.dart  # Firebase configuration
├── plans/
│   └── chainguardian-project-plan.md  # Comprehensive project plan
├── firebase.json              # Firebase configuration
├── firestore.rules            # Firestore security rules
└── pubspec.yaml               # Flutter dependencies
```

## 🔥 Firebase Services Used

### Firestore Database
- **Users Collection**: Stores user profiles and preferences
- **Risk Scores Collection**: Time-series risk assessment data
- **Alerts Collection**: Real-time alerts and notifications

### Firebase Authentication
- Anonymous authentication for quick onboarding
- Extensible for email/password, Google, Apple, etc.

### Free Tier Limits
- Firestore: 50K reads, 20K writes/day
- Authentication: 10K verifications/month
- Storage: 5GB
- Hosting: 10GB/month

## 🎨 UI Features

### Auth Screen
- Anonymous sign-in for quick access
- Clean, modern design with gradient logo

### Dashboard Screen
- Portfolio risk score visualization
- Real-time risk level indicator
- Feature grid for navigation
- User profile management

## 🚧 Current Implementation Status

- ✅ Firebase project setup
- ✅ Firestore database with security rules
- ✅ Firebase Authentication (anonymous)
- ✅ Flutter app with Firebase SDK integration
- ✅ Basic UI framework (Auth & Dashboard screens)
- ✅ Riverpod state management
- ✅ Real-time Firestore listeners

## 📝 Next Steps

1. **Wallet Integration**: Add Algorand wallet connection
2. **Risk Assessment Engine**: Implement AI-powered risk scoring
3. **Data Ingestion**: Connect to DEX price feeds
4. **Smart Contracts**: Deploy Algorand smart contracts
5. **Alert System**: Implement push notifications
6. **Backend API**: Add Python FastAPI for AI/ML processing

## 📚 Documentation

- [Project Plan](plans/chainguardian-project-plan.md) - Comprehensive technical documentation
- [Firebase Documentation](https://firebase.google.com/docs)
- [Flutter Documentation](https://flutter.dev/docs)
- [Algorand Documentation](https://developer.algorand.org/docs)

## 🤝 Contributing

This is a proof-of-concept implementation. Contributions are welcome!

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

For issues or questions, please refer to the project plan documentation.

---

**Built with ❤️ using Flutter, Firebase, and Algorand**
