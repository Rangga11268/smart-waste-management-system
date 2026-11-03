class PredictionResult {
  final String category;
  final double confidence;
  final String confidencePercentage;
  final int categoryId;
  final Map<String, double> probabilities;

  PredictionResult({
    required this.category,
    required this.confidence,
    required this.confidencePercentage,
    required this.categoryId,
    required this.probabilities,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    Map<String, double> probs = {};
    if (json['probabilities'] is Map) {
      json['probabilities'].forEach((k, v) {
        probs[k.toString()] = (v is num) ? v.toDouble() : 0.0;
      });
    }

    return PredictionResult(
      category: json['category']?.toString() ?? '',
      confidence: (json['confidence'] is num) ? (json['confidence'] as num).toDouble() : 0.0,
      confidencePercentage: json['confidence_percentage']?.toString() ?? '0%',
      categoryId: json['category_id'] is int ? json['category_id'] : int.tryParse(json['category_id'].toString()) ?? 1,
      probabilities: probs,
    );
  }
}
