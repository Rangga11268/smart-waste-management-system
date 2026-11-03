import 'category.dart';

DateTime parseUtcDateTime(dynamic raw) {
  if (raw == null) return DateTime.now();
  String s = raw.toString().trim();
  if (s.isEmpty) return DateTime.now();
  if (!s.endsWith('Z') && !s.contains('+') && !(s.length > 10 && s.substring(10).contains('-'))) {
    s = '${s}Z';
  }
  final dt = DateTime.tryParse(s) ?? DateTime.now();
  return dt.isUtc ? dt.toLocal() : dt;
}

class Reporter {
  final String id;
  final String fullName;
  final String? email;

  Reporter({
    required this.id,
    required this.fullName,
    this.email,
  });

  factory Reporter.fromJson(Map<String, dynamic> json) {
    return Reporter(
      id: json['id']?.toString() ?? '',
      fullName: json['full_name']?.toString() ?? 'Citizen',
      email: json['email']?.toString(),
    );
  }
}

class ReportLog {
  final String id;
  final String? previousStatus;
  final String newStatus;
  final String? remarks;
  final DateTime createdAt;

  ReportLog({
    required this.id,
    this.previousStatus,
    required this.newStatus,
    this.remarks,
    required this.createdAt,
  });

  factory ReportLog.fromJson(Map<String, dynamic> json) {
    return ReportLog(
      id: json['id']?.toString() ?? '',
      previousStatus: json['previous_status']?.toString(),
      newStatus: json['new_status']?.toString() ?? '',
      remarks: json['remarks']?.toString(),
      createdAt: parseUtcDateTime(json['created_at']),
    );
  }
}

class WasteReport {
  final String id;
  final String title;
  final String? description;
  final String imageUrl;
  final String? detectedCategory;
  final double? aiConfidence;
  final double latitude;
  final double longitude;
  final String? addressNote;
  final String status;
  final String? adminNotes;
  final DateTime createdAt;
  final WasteCategory category;
  final Reporter reporter;
  final List<ReportLog> logs;

  WasteReport({
    required this.id,
    required this.title,
    this.description,
    required this.imageUrl,
    this.detectedCategory,
    this.aiConfidence,
    required this.latitude,
    required this.longitude,
    this.addressNote,
    required this.status,
    this.adminNotes,
    required this.createdAt,
    required this.category,
    required this.reporter,
    this.logs = const [],
  });

  factory WasteReport.fromJson(Map<String, dynamic> json) {
    var rawLogs = json['logs'] as List<dynamic>? ?? [];
    List<ReportLog> parsedLogs = rawLogs
        .map((log) => ReportLog.fromJson(log as Map<String, dynamic>))
        .toList();

    return WasteReport(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Laporan Sampah',
      description: json['description']?.toString(),
      imageUrl: json['image_url']?.toString() ?? '',
      detectedCategory: json['detected_category']?.toString(),
      aiConfidence: (json['ai_confidence'] is num)
          ? (json['ai_confidence'] as num).toDouble()
          : null,
      latitude: (json['latitude'] is num)
          ? (json['latitude'] as num).toDouble()
          : 0.0,
      longitude: (json['longitude'] is num)
          ? (json['longitude'] as num).toDouble()
          : 0.0,
      addressNote: json['address_note']?.toString(),
      status: json['status']?.toString() ?? 'Pending',
      adminNotes: json['admin_notes']?.toString(),
      createdAt: parseUtcDateTime(json['created_at']),
      category: json['category'] is Map<String, dynamic>
          ? WasteCategory.fromJson(json['category'])
          : WasteCategory(id: 0, name: 'Umum', badgeColor: '#059669'),
      reporter: json['reporter'] is Map<String, dynamic>
          ? Reporter.fromJson(json['reporter'])
          : Reporter(id: '', fullName: 'Citizen'),
      logs: parsedLogs,
    );
  }
}
