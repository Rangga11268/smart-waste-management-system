import 'package:flutter_test/flutter_test.dart';
import 'package:swms_mobile/models/prediction_result.dart';

void main() {
  group('PredictionResult Model Tests', () {
    test('parses API predict response with probabilities correctly', () {
      final json = {
        'category': 'Organic',
        'confidence': 0.945,
        'confidence_percentage': '94.50%',
        'category_id': 1,
        'probabilities': {
          'Organic': 0.945,
          'Plastic': 0.035,
          'Paper': 0.020,
        },
      };

      final result = PredictionResult.fromJson(json);

      expect(result.category, 'Organic');
      expect(result.confidence, 0.945);
      expect(result.confidencePercentage, '94.50%');
      expect(result.categoryId, 1);
      expect(result.probabilities['Organic'], 0.945);
      expect(result.probabilities['Plastic'], 0.035);
      expect(result.probabilities['Paper'], 0.020);
    });
  });
}
