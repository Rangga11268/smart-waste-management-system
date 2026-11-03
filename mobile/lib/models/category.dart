class WasteCategory {
  final int id;
  final String name;
  final String? slug;
  final String? description;
  final String badgeColor;

  WasteCategory({
    required this.id,
    required this.name,
    this.slug,
    this.description,
    required this.badgeColor,
  });

  factory WasteCategory.fromJson(Map<String, dynamic> json) {
    return WasteCategory(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id'].toString()) ?? 0,
      name: json['name']?.toString() ?? '',
      slug: json['slug']?.toString(),
      description: json['description']?.toString(),
      badgeColor: json['badge_color']?.toString() ?? '#059669',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'description': description,
      'badge_color': badgeColor,
    };
  }
}
