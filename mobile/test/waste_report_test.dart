import 'package:flutter_test/flutter_test.dart';
import 'package:swms_mobile/models/waste_report.dart';

void main() {
  group('WasteReport & ReportLog Model Tests', () {
    test('parses full WasteReport with embedded reporter and logs', () {
      final json = {
        'id': 'b1c2d3e4-1111-2222-3333-444455556666',
        'title': 'Tumpukan Sampah Dekat Pasar',
        'description': 'Banyak kantong plastik liar',
        'image_url': '/uploads/evidence1.jpg',
        'detected_category': 'Plastic',
        'ai_confidence': 0.92,
        'latitude': -6.2088,
        'longitude': 106.8456,
        'address_note': 'Pintu timur pasar',
        'status': 'In Progress',
        'admin_notes': 'Tim armada kebersihan sedang meluncur',
        'created_at': '2026-11-03T11:00:00Z',
        'category': {
          'id': 2,
          'name': 'Plastik',
          'badge_color': '#3B82F6',
        },
        'reporter': {
          'id': 'u-1',
          'full_name': 'Warga Peduli',
          'email': 'peduli@bilcode.id',
        },
        'logs': [
          {
            'id': 'log-1',
            'previous_status': 'Pending',
            'new_status': 'In Progress',
            'remarks': 'Diverifikasi oleh admin',
            'created_at': '2026-11-03T11:30:00Z',
          }
        ],
      };

      final report = WasteReport.fromJson(json);

      expect(report.id, 'b1c2d3e4-1111-2222-3333-444455556666');
      expect(report.title, 'Tumpukan Sampah Dekat Pasar');
      expect(report.detectedCategory, 'Plastic');
      expect(report.aiConfidence, 0.92);
      expect(report.latitude, -6.2088);
      expect(report.longitude, 106.8456);
      expect(report.status, 'In Progress');
      expect(report.category.name, 'Plastik');
      expect(report.reporter.fullName, 'Warga Peduli');
      expect(report.logs.length, 1);
      expect(report.logs.first.newStatus, 'In Progress');
    });
  });
}
