import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/category.dart';
import '../models/prediction_result.dart';
import '../models/waste_report.dart';

class ApiService {
  final String? token;

  ApiService({this.token});

  Map<String, String> get _headers {
    final map = {
      'Accept': 'application/json',
    };
    if (token != null && token!.isNotEmpty) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }

  // 1. Fetch Categories
  Future<List<WasteCategory>> getCategories() async {
    try {
      final response = await http.get(
        Uri.parse('${AppConfig.baseUrl}/categories'),
        headers: _headers,
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        final list = body['data'] as List<dynamic>? ?? [];
        return list.map((c) => WasteCategory.fromJson(c)).toList();
      }
      return [];
    } catch (_) {
      // Fallback categories if server unreachable
      return [
        WasteCategory(id: 1, name: 'Organik', slug: 'organic', badgeColor: '#10B981', description: 'Sisa makanan, dedaunan, ranting'),
        WasteCategory(id: 2, name: 'Plastik', slug: 'plastic', badgeColor: '#3B82F6', description: 'Botol plastik, kantong, kemasan'),
        WasteCategory(id: 3, name: 'Kertas', slug: 'paper', badgeColor: '#F59E0B', description: 'Kardus, koran, buku bekas'),
      ];
    }
  }

  // 2. Classify image with MobileNetV2 AI (supports byte array for cross-platform Web & Mobile)
  Future<PredictionResult> predictImage(Uint8List imageBytes, String filename) async {
    final uri = Uri.parse('${AppConfig.baseUrl}/predict');
    final request = http.MultipartRequest('POST', uri);

    request.headers.addAll(_headers);
    request.files.add(
      http.MultipartFile.fromBytes('file', imageBytes, filename: filename),
    );

    final streamedResponse = await request.send().timeout(const Duration(seconds: 25));
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body);
      if (body['data'] != null) {
        return PredictionResult.fromJson(body['data']);
      }
      throw Exception('Format respons AI tidak valid');
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Gagal melakukan klasifikasi gambar');
    }
  }

  // 3. Submit Waste Report (cross-platform with byte array)
  Future<Map<String, dynamic>> submitReport({
    required Uint8List imageBytes,
    required String filename,
    required String title,
    String? description,
    required int categoryId,
    required double latitude,
    required double longitude,
    String? addressNote,
  }) async {
    final uri = Uri.parse('${AppConfig.baseUrl}/reports');
    final request = http.MultipartRequest('POST', uri);

    request.headers.addAll(_headers);
    request.files.add(
      http.MultipartFile.fromBytes('file', imageBytes, filename: filename),
    );

    request.fields['title'] = title;
    if (description != null && description.isNotEmpty) {
      request.fields['description'] = description;
    }
    request.fields['category_id'] = categoryId.toString();
    request.fields['latitude'] = latitude.toString();
    request.fields['longitude'] = longitude.toString();
    if (addressNote != null && addressNote.isNotEmpty) {
      request.fields['address_note'] = addressNote;
    }

    final streamedResponse = await request.send().timeout(const Duration(seconds: 30));
    final response = await http.Response.fromStream(streamedResponse);

    final body = jsonDecode(response.body);
    if (response.statusCode == 201 || response.statusCode == 200) {
      return {'success': true, 'data': body['data']};
    } else {
      throw Exception(body['detail'] ?? 'Gagal mengirimkan laporan sampah');
    }
  }

  // 4. Fetch Reports List
  Future<List<WasteReport>> getReports({
    String? status,
    int? categoryId,
    String? search,
    int page = 1,
    int limit = 50,
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
      'limit': limit.toString(),
    };
    if (status != null && status.isNotEmpty) {
      queryParams['status'] = status;
    }
    if (categoryId != null) {
      queryParams['category_id'] = categoryId.toString();
    }
    if (search != null && search.isNotEmpty) {
      queryParams['search'] = search;
    }

    final uri = Uri.parse('${AppConfig.baseUrl}/reports').replace(queryParameters: queryParams);
    final response = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body);
      final list = body['data'] as List<dynamic>? ?? [];
      return list.map((item) => WasteReport.fromJson(item)).toList();
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Gagal memuat daftar laporan');
    }
  }

  // 5. Fetch Report Detail
  Future<WasteReport> getReportDetail(String reportId) async {
    final uri = Uri.parse('${AppConfig.baseUrl}/reports/$reportId');
    final response = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body);
      return WasteReport.fromJson(body['data']);
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Gagal memuat detail laporan');
    }
  }

  // 6. Fetch Dashboard Stats
  Future<Map<String, dynamic>> getDashboardStats() async {
    try {
      final uri = Uri.parse('${AppConfig.baseUrl}/dashboard/stats');
      final response = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        return body['data'] as Map<String, dynamic>? ?? {};
      }
    } catch (_) {}
    return {
      'total_reports': 0,
      'pending_reports': 0,
      'in_progress_reports': 0,
      'completed_reports': 0,
    };
  }
}
