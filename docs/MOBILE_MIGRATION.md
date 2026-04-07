# Sahakar Mandal - Mobile App Migration Guide

Complete guide to convert Sahakar Mandal web app to a hybrid mobile application using Flutter or Ionic/Cordova.

## Overview

The Sahakar Mandal web application is designed with **API-first architecture**, making it ideal for mobile app conversion. This guide explains how to create iOS and Android apps from the same REST API backend.

---

## Part 1: Flutter Migration

Flutter is recommended for best performance and native feel.

### Step 1: Project Setup

```bash
# Install Flutter SDK from https://flutter.dev/docs/get-started/install

# Create new Flutter project
flutter create sahakar_mandal_mobile

cd sahakar_mandal_mobile

# Get dependencies
flutter pub get
```

### Step 2: Project Structure

```
sahakar_mandal_mobile/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── config/
│   │   ├── api_config.dart         # API configuration
│   │   ├── firebase_config.dart    # Firebase setup
│   │   └── app_constants.dart      # Constants
│   ├── models/                      # Data models
│   │   ├── user_model.dart
│   │   ├── donation_model.dart
│   │   ├── event_model.dart
│   │   └── ...
│   ├── services/                    # API & business logic
│   │   ├── api_service.dart        # REST API client
│   │   ├── auth_service.dart       # Authentication
│   │   ├── donation_service.dart
│   │   └── ...
│   ├── providers/                   # State management (Provider)
│   │   ├── auth_provider.dart
│   │   ├── donation_provider.dart
│   │   └── ...
│   ├── screens/                     # UI Screens
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   └── signup_screen.dart
│   │   ├── main/
│   │   │   ├── home_screen.dart
│   │   │   ├── dashboard_screen.dart
│   │   │   └── ...
│   │   └── ...
│   ├── widgets/                     # Reusable widgets
│   │   ├── custom_button.dart
│   │   ├── donation_card.dart
│   │   └── ...
│   └── utils/                       # Utility functions
│       ├── validators.dart
│       ├── formatters.dart
│       └── ...
├── pubspec.yaml                     # Dependencies
└── README.md
```

### Step 3: Install Dependencies

Update `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Network & API
  http: ^1.1.0
  dio: ^5.3.0
  
  # State Management
  provider: ^6.0.0
  
  # Firebase
  firebase_core: ^2.24.0
  firebase_auth: ^4.10.0
  firebase_storage: ^11.2.0
  cloud_firestore: ^4.13.0
  
  # Authentication & JWT
  jwt_decoder: ^2.0.1
  
  # Payment
  razorpay_flutter: ^1.3.6
  
  # QR Code
  qr_code_scanner: ^1.0.1
  qr_flutter: ^4.1.0
  
  # Image & Gallery
  image_picker: ^1.0.4
  cached_network_image: ^3.3.0
  
  # Charts
  fl_chart: ^0.63.0
  
  # Notifications
  firebase_messaging: ^14.6.0
  
  # Local Storage
  shared_preferences: ^2.2.2
  hive: ^2.2.3
  
  # UI/UX
  flutter_screenutil: ^5.9.0
  get: ^4.6.5
  
  # Utilities
  intl: ^0.19.0
  connectivity_plus: ^5.0.0
  

dev_dependencies:
  flutter_test:
    sdk: flutter
  hive_generator: ^2.0.1
  build_runner: ^2.4.6
```

### Step 4: API Service Implementation

Create `lib/services/api_service.dart`:

```dart
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';

class ApiService {
  late Dio _dio;
  final String _tokenKey = 'auth_token';
  
  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
        },
      ),
    );
    
    // Add interceptors
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add token to requests
          final token = await _getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) {
          // Handle errors
          if (error.response?.statusCode == 401) {
            // Token expired, logout
            _logout();
          }
          return handler.next(error);
        },
      ),
    );
  }
  
  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }
  
  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }
  
  // Auth endpoints
  Future<Map<String, dynamic>> signup(Map<String, dynamic> data) async {
    final response = await _dio.post('/auth/signup', data: data);
    await _saveToken(response.data['token']);
    return response.data;
  }
  
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    await _saveToken(response.data['token']);
    return response.data;
  }
  
  Future<void> logout() async {
    await _dio.post('/auth/logout');
    await _logout();
  }
  
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/auth/me');
    return response.data;
  }
  
  // Donation endpoints
  Future<List<dynamic>> getDonations() async {
    final response = await _dio.get('/donations');
    return response.data['donations'] ?? [];
  }
  
  Future<Map<String, dynamic>> createDonation(Map<String, dynamic> data) async {
    final response = await _dio.post('/donations', data: data);
    return response.data;
  }
  
  // Receipt endpoints
  Future<Map<String, dynamic>> generateReceipt(String donationId) async {
    final response = await _dio.post('/receipts/$donationId/generate');
    return response.data;
  }
  
  Future<String> getReceiptQrCode(String receiptId) {
    return Future.value('${ApiConfig.baseUrl}/receipts/$receiptId/qrcode');
  }
  
  // Dashboard endpoints
  Future<Map<String, dynamic>> getDashboardSummary() async {
    final response = await _dio.get('/dashboard/summary');
    return response.data;
  }
  
  // Add more endpoints as needed...
  
  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }
}
```

### Step 5: Authentication Service

Create `lib/services/auth_service.dart`:

```dart
import 'package:firebase_auth/firebase_auth.dart';
import 'api_service.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiService apiService;
  final FirebaseAuth firebaseAuth = FirebaseAuth.instance;
  
  AuthService(this.apiService);
  
  Future<UserModel> signup({
    required String name,
    required String email,
    required String password,
    required String phone,
    String? area,
    String role = 'volunteer',
  }) async {
    final response = await apiService.signup({
      'name': name,
      'email': email,
      'password': password,
      'phone': phone,
      'area': area ?? '',
      'role': role,
    });
    
    return UserModel.fromJson(response);
  }
  
  Future<UserModel> login(String email, String password) async {
    final response = await apiService.login(email, password);
    return UserModel.fromJson(response);
  }
  
  Future<void> logout() async {
    await apiService.logout();
  }
  
  Future<UserModel> getCurrentUser() async {
    final response = await apiService.getCurrentUser();
    return UserModel.fromJson(response);
  }
  
  Future<bool> isAuthenticated() async {
    final token = await apiService._getToken();
    return token != null;
  }
}
```

### Step 6: Models

Create `lib/models/user_model.dart`:

```dart
class UserModel {
  final String userId;
  final String name;
  final String email;
  final String phone;
  final String role;
  final String area;
  final String status;
  
  UserModel({
    required this.userId,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    required this.area,
    required this.status,
  });
  
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      userId: json['user_id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      role: json['role'] ?? 'volunteer',
      area: json['area'] ?? '',
      status: json['status'] ?? 'active',
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'name': name,
      'email': email,
      'phone': phone,
      'role': role,
      'area': area,
      'status': status,
    };
  }
}
```

Create `lib/models/donation_model.dart`:

```dart
class DonationModel {
  final String id;
  final String donationId;
  final String donorName;
  final String? donorEmail;
  final String? donorPhone;
  final double amount;
  final String donationType;
  final String purpose;
  final String status;
  final DateTime date;
  
  DonationModel({
    required this.id,
    required this.donationId,
    required this.donorName,
    this.donorEmail,
    this.donorPhone,
    required this.amount,
    required this.donationType,
    required this.purpose,
    required this.status,
    required this.date,
  });
  
  factory DonationModel.fromJson(Map<String, dynamic> json) {
    return DonationModel(
      id: json['id'] ?? '',
      donationId: json['donation_id'] ?? '',
      donorName: json['donor_name'] ?? '',
      donorEmail: json['donor_email'],
      donorPhone: json['donor_mobile'],
      amount: (json['amount'] ?? 0).toDouble(),
      donationType: json['donation_type'] ?? 'cash',
      purpose: json['purpose'] ?? 'general',
      status: json['status'] ?? 'pending',
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'donation_id': donationId,
      'donor_name': donorName,
      'donor_email': donorEmail,
      'donor_mobile': donorPhone,
      'amount': amount,
      'donation_type': donationType,
      'purpose': purpose,
      'status': status,
      'date': date.toIso8601String(),
    };
  }
}
```

### Step 7: State Management (Provider)

Create `lib/providers/auth_provider.dart`:

```dart
import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService authService;
  
  UserModel? _currentUser;
  bool _isLoading = false;
  String? _error;
  
  AuthProvider(this.authService);
  
  UserModel? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _currentUser != null;
  
  Future<void> signup({
    required String name,
    required String email,
    required String password,
    required String phone,
    String? area,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final user = await authService.signup(
        name: name,
        email: email,
        password: password,
        phone: phone,
        area: area,
      );
      _currentUser = user;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final user = await authService.login(email, password);
      _currentUser = user;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      await authService.logout();
      _currentUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> getCurrentUser() async {
    try {
      _currentUser = await authService.getCurrentUser();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
    }
  }
}
```

### Step 8: Login Screen

Create `lib/screens/auth/login_screen.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);
  
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _emailController;
  late TextEditingController _passwordController;
  
  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController();
    _passwordController = TextEditingController();
  }
  
  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('सहकार मंडळ / Sahakar Mandal'),
        centerTitle: true,
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Email field
                  TextFormField(
                    controller: _emailController,
                    decoration: InputDecoration(
                      labelText: 'Email',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter email';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  // Password field
                  TextFormField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter password';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),
                  
                  // Error message
                  if (authProvider.error != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Text(
                        authProvider.error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  
                  // Login button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: authProvider.isLoading
                          ? null
                          : () {
                              if (_formKey.currentState!.validate()) {
                                authProvider.login(
                                  _emailController.text,
                                  _passwordController.text,
                                );
                              }
                            },
                      child: authProvider.isLoading
                          ? const CircularProgressIndicator()
                          : const Text('Login'),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
```

### Step 9: Main App Setup

Create `lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'providers/auth_provider.dart';
import 'screens/auth/login_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider(create: (_) => ApiService()),
        ProxyProvider<ApiService, AuthService>(
          create: (_, apiService) => AuthService(apiService),
          update: (_, apiService, __) => AuthService(apiService),
        ),
        ChangeNotifierProxyProvider<AuthService, AuthProvider>(
          create: (_, authService) => AuthProvider(authService),
          update: (_, authService, authProvider) =>
              authProvider ?? AuthProvider(authService),
        ),
      ],
      child: MaterialApp(
        title: 'Sahakar Mandal',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const LoginScreen(),
      ),
    );
  }
}
```

### Step 10: Build & Test

```bash
# Run on emulator
flutter run

# Build APK (Android)
flutter build apk --release

# Build iOS
flutter build ios --release

# Build web (bonus)
flutter build web
```

---

## Part 2: Ionic/Cordova Migration

Alternative using web technologies (HTML/CSS/JavaScript).

### Step 1: Setup Ionic

```bash
# Install Ionic CLI
npm install -g @ionic/cli

# Create project
ionic start sahakar-mandal-mobile blank --type=react

cd sahakar-mandal-mobile
```

### Step 2: Install Capacitor Plugins

```bash
npm install @capacitor/core @capacitor/cli
npx cap init

# Install necessary plugins
npm install @capacitor/geolocation
npm install @capacitor/camera
npm install @capacitor/filesystem
npm install cordova-plugin-qrscanner
npm install firebase
```

### Step 3: Project Structure

```
sahakar-mandal-mobile/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx
│   │   ├── DonationCard.tsx
│   │   └── ...
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   └── ...
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── ...
│   ├── App.tsx
│   └── index.tsx
├── android/
├── ios/
└── package.json
```

### Step 4: API Service (React)

Create `src/services/api.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';
import { Storage } from '@ionic/storage';

class ApiService {
  private api: AxiosInstance;
  private storage: Storage;
  
  constructor() {
    this.api = axios.create({
      baseURL: 'https://sahakar-mandal-api.onrender.com/api',
      timeout: 30000,
    });
    
    this.api.interceptors.request.use(async (config) => {
      const token = await localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    this.storage = new Storage();
  }
  
  async login(email: string, password: string) {
    const response = await this.api.post('/auth/login', {
      email,
      password,
    });
    
    await localStorage.setItem('auth_token', response.data.token);
    await localStorage.setItem('user', JSON.stringify(response.data));
    
    return response.data;
  }
  
  async getDonations() {
    const response = await this.api.get('/donations');
    return response.data.donations;
  }
  
  async createDonation(data: any) {
    const response = await this.api.post('/donations', data);
    return response.data;
  }
  
  // Add more methods...
}

export default new ApiService();
```

### Step 5: Push Notifications Setup

```bash
npm install @capacitor/push-notifications
npx cap plugin add @capacitor/push-notifications
```

---

## Part 3: Cross-Platform Features

### QR Code Scanning

**Flutter:**
```dart
import 'package:qr_code_scanner/qr_code_scanner.dart';

class QRScannerScreen extends StatefulWidget {
  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  late QRViewController controller;
  
  @override
  Widget build(BuildContext context) {
    return QRView(
      key: qrKey,
      onQRViewCreated: _onQRViewCreated,
    );
  }
  
  void _onQRViewCreated(QRViewController controller) {
    this.controller = controller;
    controller.scannedDataStream.listen((scanData) {
      // Handle scanned QR code
      print('QR Code: ${scanData.code}');
    });
  }
}
```

### Camera Access

**Flutter:**
```dart
import 'package:image_picker/image_picker.dart';

final ImagePicker picker = ImagePicker();
final XFile? image = await picker.pickImage(source: ImageSource.camera);
```

**Ionic/Cordova:**
```typescript
import { Camera, CameraResultType } from '@capacitor/camera';

const takePhoto = async () => {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: true,
    resultType: CameraResultType.Uri
  });
};
```

### Offline Support

**Flutter with Hive:**
```dart
import 'package:hive/hive.dart';

class OfflineService {
  late Box donationBox;
  
  Future<void> init() async {
    donationBox = await Hive.openBox('donations');
  }
  
  Future<void> saveDonationOffline(DonationModel donation) async {
    await donationBox.put(donation.id, donation.toJson());
  }
  
  Future<void> syncOfflineDonations(ApiService apiService) async {
    for (var key in donationBox.keys) {
      final donationJson = donationBox.get(key);
      await apiService.createDonation(donationJson);
      await donationBox.delete(key);
    }
  }
}
```

---

## Part 4: Firebase Setup for Mobile

### Step 1: Add Firebase to Flutter

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Configure Firebase for Flutter
flutterfire configure
```

### Step 2: Android Setup

Edit `android/build.gradle`:

```gradle
buildscript {
  dependencies {
    classpath 'com.google.gms:google-services:4.3.15'
  }
}
```

Edit `android/app/build.gradle`:

```gradle
apply plugin: 'com.google.gms.google-services'

dependencies {
  implementation 'com.google.firebase:firebase-analytics'
}
```

### Step 3: iOS Setup

```bash
cd ios
pod install
cd ..
```

---

## Part 5: Payment Integration

### Razorpay for Flutter

```bash
flutter pub add razorpay_flutter
```

```dart
import 'package:razorpay_flutter/razorpay_flutter.dart';

class PaymentService {
  late Razorpay _razorpay;
  
  PaymentService() {
    _razorpay = Razorpay();
    _razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, handlePaymentSuccess);
    _razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, handlePaymentError);
  }
  
  void initiatePayment(double amount) {
    var options = {
      'key': 'YOUR_RAZORPAY_KEY',
      'amount': (amount * 100).toInt(),
      'name': 'Sahakar Mandal',
      'description': 'Donation',
      'prefill': {
        'contact': '9876543210',
        'email': 'user@example.com'
      }
    };
    
    try {
      _razorpay.open(options);
    } catch (e) {
      print(e);
    }
  }
  
  void handlePaymentSuccess(PaymentSuccessResponse response) {
    print('Payment Success: ${response.paymentId}');
    // Verify and save payment
  }
  
  void handlePaymentError(PaymentFailureResponse response) {
    print('Payment Error: ${response.message}');
  }
}
```

---

## Part 6: App Icons & Splash Screen

### Flutter

```bash
# Generate icons
flutter pub get
flutter pub run flutter_launcher_icons:main

# Generate splash
flutter pub run flutter_native_splash:create
```

Configure `pubspec.yaml`:

```yaml
flutter_icons:
  android: "launcher_icon"
  ios: true
  image_path: "assets/icon.png"

flutter_native_splash:
  image: assets/splash.png
  color: "FF6B35"
```

---

## Part 7: Testing

### Unit Tests

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahakar_mandal/models/donation_model.dart';

void main() {
  group('DonationModel', () {
    test('converts JSON to DonationModel', () {
      final json = {
        'id': 'donation_1',
        'donation_id': 'DONATION_001',
        'donor_name': 'John Doe',
        'amount': 5000,
        'donation_type': 'cash',
        'purpose': 'general',
        'status': 'completed',
        'date': '2024-01-01T10:00:00Z',
      };
      
      final donation = DonationModel.fromJson(json);
      
      expect(donation.donorName, 'John Doe');
      expect(donation.amount, 5000);
    });
  });
}
```

### Widget Tests

```dart
testWidgets('Login form validation', (WidgetTester tester) async {
  await tester.pumpWidget(const MyApp());
  
  // Find login button
  final loginButton = find.byType(ElevatedButton);
  
  // Tap it
  await tester.tap(loginButton);
  await tester.pumpWidget(const MyApp());
  
  // Verify validation
  expect(find.text('Please enter email'), findsOneWidget);
});
```

---

## Part 8: App Store Deployment

### Android (Google Play Store)

```bash
# Build release APK
flutter build apk --release

# Build App Bundle
flutter build appbundle --release

# Upload to Google Play Console
```

### iOS (Apple App Store)

```bash
# Build release
flutter build ios --release

# Archive and upload via Xcode or TestFlight
```

---

## Part 9: Versioning & Updates

```yaml
# pubspec.yaml
version: 1.0.0+1
```

Increment version for updates:
- Major: New features
- Minor: Bug fixes
- Patch: Hotfixes
- Build number: Every release

---

## Part 10: Migration Checklist

- [ ] Project setup complete
- [ ] API integration working
- [ ] Authentication implemented
- [ ] Main screens built
- [ ] Payment integration complete
- [ ] Firebase configured
- [ ] Offline support added
- [ ] Push notifications setup
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] Images optimized
- [ ] Icons/splash configured
- [ ] Tests written
- [ ] Performance optimized
- [ ] App signed (iOS/Android)
- [ ] Deployed to stores
- [ ] Analytics configured

---

## Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Ionic Documentation](https://ionicframework.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Razorpay Mobile](https://razorpay.com/integrations/)

---

Last Updated: 2024
Version: 1.0.0
