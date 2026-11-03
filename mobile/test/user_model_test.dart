import 'package:flutter_test/flutter_test.dart';
import 'package:swms_mobile/models/user.dart';

void main() {
  group('User Model Tests', () {
    test('parses JSON correctly into User instance', () {
      final json = {
        'id': 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d',
        'email': 'citizen@bilcode.id',
        'full_name': 'Budi Santoso',
        'role': 'citizen',
        'phone_number': '081234567890',
        'created_at': '2026-11-03T10:00:00Z',
      };

      final user = User.fromJson(json);

      expect(user.id, 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d');
      expect(user.email, 'citizen@bilcode.id');
      expect(user.fullName, 'Budi Santoso');
      expect(user.role, 'citizen');
      expect(user.phoneNumber, '081234567890');
      expect(user.createdAt, isNotNull);
    });

    test('serializes User instance back to JSON map', () {
      final user = User(
        id: 'user-123',
        email: 'test@bilcode.id',
        fullName: 'Test User',
        role: 'admin',
        phoneNumber: '081111111',
      );

      final map = user.toJson();
      expect(map['id'], 'user-123');
      expect(map['email'], 'test@bilcode.id');
      expect(map['full_name'], 'Test User');
      expect(map['role'], 'admin');
    });
  });
}
