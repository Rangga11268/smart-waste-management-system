import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'config/app_config.dart';
import 'screens/splash/splash_screen.dart';
import 'services/auth_service.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Set system navigation & status bar colors (mobile native only)
  if (!kIsWeb) {
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
      ),
    );
  }

  // Catch unhandled asynchronous errors to prevent unhandled promise rejections on web
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('SWMS Handled Exception: $error');
    return true;
  };

  // Initialize dynamic server base URL
  await AppConfig.init();

  runApp(const SwmsApp());
}

class SwmsApp extends StatefulWidget {
  const SwmsApp({super.key});

  @override
  State<SwmsApp> createState() => _SwmsAppState();
}

class _SwmsAppState extends State<SwmsApp> {
  late final AuthService _authService;

  @override
  void initState() {
    super.initState();
    _authService = AuthService();
  }

  @override
  void dispose() {
    _authService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SWMS Citizen',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: SplashScreen(authService: _authService),
    );
  }
}
