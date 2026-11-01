# SWMS Mobile Application

Citizen reporting mobile application for the Smart Waste Management System (SWMS), built with Flutter for Android.

---

## Features

- **Smart Waste AI Scan**: Capture waste piles directly via mobile camera (`image_picker`) and submit to the backend `/predict` endpoint for automatic classification into *Organic*, *Plastic*, or *Paper* with real-time confidence scores.
- **Automated GPS Geotagging**: Locks high-accuracy GNSS device coordinates (`geolocator`) automatically upon capturing an evidence photo.
- **Citizen Report Submission**: Seamlessly packages evidence photo, AI prediction, GPS coordinates, and user notes into a single multipart payload.
- **Real-Time History & Status Tracking**: Live timeline showing report progress from `Pending` $\rightarrow$ `In Progress` $\rightarrow$ `Completed` with operator status notes.
- **Offline & Low-Bandwidth Resilience**: Caches user session credentials (`shared_preferences`) and validates image size prior to transmission.

---

## Directory Structure

```
mobile/
├── lib/
│   ├── models/           # Data models (User, WasteReport, PredictionResult)
│   ├── screens/          # Application views
│   │   ├── auth/         # Login & registration screens
│   │   ├── home/         # Home screen with quick report action
│   │   ├── report/       # Camera scan, AI classification preview & submit
│   │   └── history/      # Citizen report history & status timeline
│   ├── services/         # Hardware & API integration services
│   │   ├── api_service.dart      # REST HTTP client
│   │   ├── camera_service.dart   # Image capture & compression
│   │   └── location_service.dart # GPS acquisition & permissions
│   └── main.dart         # Flutter app entrypoint & theme setup
├── pubspec.yaml          # Flutter dependencies and assets configuration
└── README.md             # This guide
```

---

## Getting Started

### 1. Prerequisites
- Flutter SDK 3.19+ (Dart 3.x)
- Android Studio / Android SDK 33+ or VS Code with Flutter Extension
- Physical Android test device or Android Emulator

### 2. Install Dependencies
```bash
flutter pub get
```

### 3. Run on Connected Device / Emulator
Ensure local FastAPI backend is reachable (use `http://10.0.2.2:8000/api/v1` on Android Emulator or local network IP on physical device):
```bash
flutter run
```

### 4. Build Standalone Android Release APK
```bash
flutter build apk --release
```
The resulting `.apk` binary will be generated at:
`mobile/build/app/outputs/flutter-apk/app-release.apk`

---

## Day 4 Implementation Roadmap

- Initialize Flutter MaterialApp with brand color palette and typography.
- Implement camera capture interface and preview screen.
- Integrate GPS coordinate locking via `geolocator`.
- Send image to FastAPI `/predict` and render AI classification pill with confidence score.
- Submit full report to `POST /api/v1/reports` and show status confirmation.
- Build report history list with pull-to-refresh and semantic status badges.
