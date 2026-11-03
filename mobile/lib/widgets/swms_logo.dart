import 'dart:math' as math;
import 'package:flutter/material.dart';

class SwmsLogo extends StatelessWidget {
  final double size;
  final bool showText;
  final Color? textColor;

  const SwmsLogo({
    super.key,
    this.size = 48,
    this.showText = false,
    this.textColor,
  });

  @override
  Widget build(BuildContext context) {
    final mark = SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _SwmsLogoPainter(),
      ),
    );

    if (!showText) return mark;

    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        mark,
        const SizedBox(width: 12),
        Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'SWMS',
                  style: TextStyle(
                    fontSize: size * 0.42,
                    fontWeight: FontWeight.w900,
                    letterSpacing: -0.5,
                    color: textColor ?? const Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(width: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: const Color(0xFFA7F3D0)),
                  ),
                  child: const Text(
                    'ECO',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF059669),
                    ),
                  ),
                ),
              ],
            ),
            Text(
              'Smart Waste Management',
              style: TextStyle(
                fontSize: size * 0.22,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF64748B),
                letterSpacing: 0.2,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _SwmsLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final scale = size.width / 256.0;

    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.scale(scale);

    // 3 Leaf colors representing nature & recycling stages
    final colors = [
      [const Color(0xFF4ADE80), const Color(0xFF16A34A)],
      [const Color(0xFF10B981), const Color(0xFF059669)],
      [const Color(0xFF059669), const Color(0xFF047857)],
    ];

    for (int i = 0; i < 3; i++) {
      canvas.save();
      canvas.rotate(i * 120 * math.pi / 180);

      final path = Path();
      path.moveTo(0, -104);
      path.cubicTo(42, -104, 84, -72, 84, -24);
      path.cubicTo(84, 16, 54, 48, 16, 62);
      path.cubicTo(34, 36, 38, 10, 32, -16);
      path.cubicTo(26, -42, 12, -74, 0, -104);
      path.close();

      final paint = Paint()
        ..shader = LinearGradient(
          colors: colors[i],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ).createShader(const Rect.fromLTWH(-100, -110, 200, 200));

      canvas.drawPath(path, paint);

      // Delicate inner leaf contour
      final veinPath = Path();
      veinPath.moveTo(0, -104);
      veinPath.cubicTo(18, -70, 24, -40, 20, -10);
      veinPath.cubicTo(18, 12, 8, 34, -4, 50);
      veinPath.cubicTo(8, 36, 14, 18, 14, -4);
      veinPath.cubicTo(14, -28, 8, -66, 0, -104);
      veinPath.close();

      final veinPaint = Paint()
        ..color = const Color(0xFF064E3B).withValues(alpha: 0.25);
      canvas.drawPath(veinPath, veinPaint);

      canvas.restore();
    }

    // Centered sustainability seed node
    final seedPaint = Paint()..color = const Color(0xFF10B981);
    canvas.drawCircle(Offset.zero, 9, seedPaint);

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
