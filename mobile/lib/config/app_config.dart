import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static const String _keyBaseUrl = 'swms_base_url';
  
  // Default URL: 10.0.2.2 for Android emulator pointing to host machine
  static const String defaultEmulatorUrl = 'http://10.0.2.2:8000/api/v1';
  static const String defaultLocalhostUrl = 'http://localhost:8000/api/v1';
  
  static String getDefaultUrl() {
    if (kIsWeb) {
      return defaultLocalhostUrl;
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      return defaultEmulatorUrl;
    }
    return defaultLocalhostUrl;
  }

  static String _currentBaseUrl = defaultLocalhostUrl;

  static String get baseUrl => _currentBaseUrl;

  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final savedUrl = prefs.getString(_keyBaseUrl);

    if (savedUrl != null) {
      // Auto-migrate if running on Web/Desktop but saved URL is 10.0.2.2
      if (kIsWeb && savedUrl.contains('10.0.2.2')) {
        _currentBaseUrl = defaultLocalhostUrl;
        await prefs.setString(_keyBaseUrl, defaultLocalhostUrl);
      } else {
        _currentBaseUrl = savedUrl;
      }
    } else {
      _currentBaseUrl = getDefaultUrl();
    }
  }

  static Future<void> setBaseUrl(String newUrl) async {
    String cleanUrl = newUrl.trim();
    if (cleanUrl.endsWith('/')) {
      cleanUrl = cleanUrl.substring(0, cleanUrl.length - 1);
    }
    if (!cleanUrl.endsWith('/api/v1')) {
      cleanUrl = '$cleanUrl/api/v1';
    }
    _currentBaseUrl = cleanUrl;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyBaseUrl, cleanUrl);
  }
}
