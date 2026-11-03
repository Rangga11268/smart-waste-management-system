import 'package:flutter_test/flutter_test.dart';
import 'package:swms_mobile/models/category.dart';

void main() {
  group('WasteCategory Model Tests', () {
    test('parses JSON with numeric ID and default color fallback', () {
      final json = {
        'id': 1,
        'name': 'Organik',
        'slug': 'organic',
        'description': 'Sisa makanan dan daun',
        'badge_color': '#10B981',
      };

      final cat = WasteCategory.fromJson(json);

      expect(cat.id, 1);
      expect(cat.name, 'Organik');
      expect(cat.slug, 'organic');
      expect(cat.badgeColor, '#10B981');
    });

    test('serializes WasteCategory to JSON map', () {
      final cat = WasteCategory(
        id: 2,
        name: 'Plastik',
        slug: 'plastic',
        description: 'Botol dan gelas plastik',
        badgeColor: '#3B82F6',
      );

      final map = cat.toJson();
      expect(map['id'], 2);
      expect(map['name'], 'Plastik');
      expect(map['badge_color'], '#3B82F6');
    });
  });
}
