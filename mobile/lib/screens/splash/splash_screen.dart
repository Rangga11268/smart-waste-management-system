import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../services/auth_service.dart';
import '../auth/login_screen.dart';
import '../home/home_screen.dart';
import '../onboarding/onboarding_screen.dart';

class SplashScreen extends StatefulWidget {
  final AuthService authService;

  const SplashScreen({super.key, required this.authService});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  // Assembly animation: 3 leaves fly in from separated outer points to center
  late final Animation<double> _assemblyAnimation;
  // Seed pop animation
  late final Animation<double> _seedAnimation;
  // Title & subtitle fade + slide up
  late final Animation<double> _textAnimation;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    );

    // Assembly curve: snappy arrival with a soft magnetic snap
    _assemblyAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 0.65, curve: Curves.easeOutBack),
    );

    // Center seed pop
    _seedAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.60, 0.82, curve: Curves.elasticOut),
    );

    // Text reveal
    _textAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.70, 1.0, curve: Curves.easeOutCubic),
    );

    _controller.forward();
    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _handleNavigation();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _handleNavigation() async {
    // Check if user has seen onboarding
    final prefs = await SharedPreferences.getInstance();
    final bool seenOnboarding = prefs.getBool('seen_onboarding') ?? false;

    if (!mounted) return;

    Widget nextScreen;
    if (!seenOnboarding) {
      nextScreen = OnboardingScreen(
        authService: widget.authService,
      );
    } else if (widget.authService.isAuthenticated) {
      nextScreen = HomeScreen(authService: widget.authService);
    } else {
      nextScreen = LoginScreen(
        authService: widget.authService,
      );
    }

    Navigator.pushReplacement(
      context,
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 500),
        pageBuilder: (_, animation, __) => nextScreen,
        transitionsBuilder: (_, animation, __, child) {
          return FadeTransition(opacity: animation, child: child);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Background subtle radial glow
          Center(
            child: Container(
              width: 320,
              height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    const Color(0xFF10B981).withValues(alpha: 0.08),
                    Colors.white.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),

          // Central Animated Assembling Logo & Brand
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Animated Assembling Mark
                AnimatedBuilder(
                  animation: _controller,
                  builder: (context, child) {
                    return SizedBox(
                      width: 140,
                      height: 140,
                      child: CustomPaint(
                        painter: _AssembleLogoPainter(
                          assemblyProgress: _assemblyAnimation.value,
                          seedProgress: _seedAnimation.value,
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 24),

                // Animated Brand Title & Tagline
                AnimatedBuilder(
                  animation: _textAnimation,
                  builder: (context, child) {
                    final opacity = _textAnimation.value;
                    final slide = (1.0 - _textAnimation.value) * 16.0;

                    return Transform.translate(
                      offset: Offset(0, slide),
                      child: Opacity(
                        opacity: opacity,
                        child: Column(
                          children: [
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Text(
                                  'SWMS',
                                  style: TextStyle(
                                    fontSize: 32,
                                    fontWeight: FontWeight.w900,
                                    color: Color(0xFF0F172A),
                                    letterSpacing: -1.0,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 7,
                                    vertical: 3,
                                  ),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFECFDF5),
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(
                                      color: const Color(0xFFA7F3D0),
                                    ),
                                  ),
                                  child: const Text(
                                    'ECO-TECH',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w800,
                                      color: Color(0xFF059669),
                                      letterSpacing: 0.5,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            const Text(
                              'Smart Waste Management System',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF64748B),
                                letterSpacing: 0.3,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),

          // Bottom Version Badge
          Positioned(
            bottom: 36,
            left: 0,
            right: 0,
            child: Center(
              child: Text(
                'v1.0 · Urban Sustainability',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: const Color(0xFF94A3B8).withValues(alpha: 0.8),
                  letterSpacing: 0.5,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Painter that animates the 3 leaves flying in from outer positions
/// and locking into place at the center
class _AssembleLogoPainter extends CustomPainter {
  final double assemblyProgress;
  final double seedProgress;

  _AssembleLogoPainter({
    required this.assemblyProgress,
    required this.seedProgress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final scale = size.width / 256.0;

    final leafGradients = [
      [const Color(0xFF4ADE80), const Color(0xFF16A34A)],
      [const Color(0xFF10B981), const Color(0xFF059669)],
      [const Color(0xFF059669), const Color(0xFF047857)],
    ];

    // Distance multiplier: 1.0 (start, separated 110dp outward) to 0.0 (docked in center)
    final separation = (1.0 - assemblyProgress).clamp(0.0, 1.0);
    final outwardDist = 140.0 * separation;
    final leafScale = (0.4 + (0.6 * assemblyProgress)).clamp(0.0, 1.0);

    for (int i = 0; i < 3; i++) {
      final baseAngleDeg = i * 120.0;
      final baseAngleRad = baseAngleDeg * math.pi / 180.0;

      // Calculate radial departure vector
      // Offset perpendicular/along angle so they fly inward from 3 distinct corners
      final dirX = math.sin(baseAngleRad);
      final dirY = -math.cos(baseAngleRad);
      final offset = Offset(dirX * outwardDist, dirY * outwardDist);

      canvas.save();
      canvas.translate(center.dx + offset.dx, center.dy + offset.dy);
      // Extra dynamic rotation twist while flying inward
      final twist = (1.0 - assemblyProgress) * 0.8 * (i.isEven ? 1 : -1);
      canvas.rotate(baseAngleRad + twist);
      canvas.scale(scale * leafScale);

      // The Leaf Path
      final path = Path();
      path.moveTo(0, -104);
      path.cubicTo(42, -104, 84, -72, 84, -24);
      path.cubicTo(84, 16, 54, 48, 16, 62);
      path.cubicTo(34, 36, 38, 10, 32, -16);
      path.cubicTo(26, -42, 12, -74, 0, -104);
      path.close();

      final paint = Paint()
        ..shader = LinearGradient(
          colors: leafGradients[i],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ).createShader(const Rect.fromLTWH(-100, -110, 200, 200));

      canvas.drawPath(path, paint);

      // Inner vein accent
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

    // Central Seed popping out when leaves settle
    if (seedProgress > 0.05) {
      final clampedSeed = seedProgress.clamp(0.0, 1.0);
      final seedPaint = Paint()..color = const Color(0xFF10B981);
      canvas.drawCircle(center, 9 * scale * clampedSeed, seedPaint);

      // Tiny white highlight dot
      final highlightPaint = Paint()..color = Colors.white.withValues(alpha: 0.8);
      canvas.drawCircle(
        Offset(center.dx - (2 * scale), center.dy - (2 * scale)),
        2.5 * scale * clampedSeed,
        highlightPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _AssembleLogoPainter oldDelegate) {
    return oldDelegate.assemblyProgress != assemblyProgress ||
        oldDelegate.seedProgress != seedProgress;
  }
}
