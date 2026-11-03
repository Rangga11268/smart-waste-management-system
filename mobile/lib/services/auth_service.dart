import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import '../models/user.dart';

class AuthService extends ChangeNotifier {
  static const String _keyToken = 'swms_auth_token';
  static const String _keyUser = 'swms_auth_user';

  String? _token;
  User? _currentUser;
  bool _isLoading = true;

  String? get token => _token;
  User? get currentUser => _currentUser;
  bool get isAuthenticated => _token != null && _currentUser != null;
  bool get isLoading => _isLoading;

  AuthService() {
    checkAuth();
  }

  Future<void> checkAuth() async {
    _isLoading = true;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString(_keyToken);
      final userStr = prefs.getString(_keyUser);

      if (_token != null && userStr != null) {
        _currentUser = User.fromJson(jsonDecode(userStr));
        // Verify with server in background
        _refreshUserProfile();
      } else {
        _token = null;
        _currentUser = null;
      }
    } catch (e) {
      debugPrint('Auth restore error: $e');
      _token = null;
      _currentUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> _refreshUserProfile() async {
    if (_token == null) return;
    try {
      final response = await http.get(
        Uri.parse('${AppConfig.baseUrl}/auth/me'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Accept': 'application/json',
        },
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        if (body['data'] != null) {
          _currentUser = User.fromJson(body['data']);
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(_keyUser, jsonEncode(_currentUser!.toJson()));
          notifyListeners();
        }
      } else if (response.statusCode == 401) {
        await logout();
      }
    } catch (_) {}
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/auth/login'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'email': email.trim(),
          'password': password,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['status'] == 'success') {
        final tokenData = data['data'];
        _token = tokenData['access_token'];
        _currentUser = User.fromJson(tokenData['user']);

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_keyToken, _token!);
        await prefs.setString(_keyUser, jsonEncode(_currentUser!.toJson()));

        notifyListeners();
        return {'success': true};
      } else {
        final errorMsg = data['detail'] ?? data['message'] ?? 'Email atau password salah';
        return {'success': false, 'error': errorMsg.toString()};
      }
    } catch (e) {
      return {'success': false, 'error': 'Gagal terhubung ke server: $e'};
    }
  }

  Future<Map<String, dynamic>> register({
    required String fullName,
    required String email,
    required String password,
    String? phoneNumber,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/auth/register'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'full_name': fullName.trim(),
          'email': email.trim(),
          'password': password,
          if (phoneNumber != null && phoneNumber.trim().isNotEmpty)
            'phone_number': phoneNumber.trim(),
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true};
      } else {
        final errorMsg = data['detail'] ?? data['message'] ?? 'Pendaftaran gagal';
        return {'success': false, 'error': errorMsg.toString()};
      }
    } catch (e) {
      return {'success': false, 'error': 'Gagal terhubung ke server: $e'};
    }
  }

  Future<void> logout() async {
    _token = null;
    _currentUser = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyToken);
    await prefs.remove(_keyUser);
    notifyListeners();
  }
}
