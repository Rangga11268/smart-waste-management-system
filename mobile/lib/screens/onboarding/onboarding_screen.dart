import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../services/auth_service.dart';
import '../../theme/app_theme.dart';
import '../auth/login_screen.dart';
import '../home/home_screen.dart';

class OnboardingScreen extends StatefulWidget {
  final AuthService authService;
  final VoidCallback? onFinish;

  const OnboardingScreen({
    super.key,
    required this.authService,
    this.onFinish,
  });

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<OnboardingItem> _slides = const [
    OnboardingItem(
      title: 'Pindai Cerdas dengan AI',
      subtitle:
          'Foto tumpukan sampah dan biarkan model deep learning SWMS mengklasifikasikan jenis sampah secara instan & akurat.',
      badgeText: 'Vision AI 98%',
      accentColor: AppTheme.primary,
      iconData: Icons.document_scanner_rounded,
      secondaryIcon: Icons.auto_awesome_rounded,
      slideType: OnboardingType.aiScanner,
    ),
    OnboardingItem(
      title: 'Geotagging Presisi Otomatis',
      subtitle:
          'Koordinat GPS terkunci otomatis saat pengambilan foto agar armada kebersihan kota tiba langsung di titik sasaran.',
      badgeText: 'GPS Lock < 5m',
      accentColor: Color(0xFF0284C7),
      iconData: Icons.location_on_rounded,
      secondaryIcon: Icons.my_location_rounded,
      slideType: OnboardingType.gps,
    ),
    OnboardingItem(
      title: 'Kota Bersih & Berkelanjutan',
      subtitle:
          'Pantau proses penanganan laporan secara transparan dari status Menunggu, Diproses, hingga tumpukan sampah Selesai dibersihkan.',
      badgeText: 'Zero Waste Impact',
      accentColor: Color(0xFF059669),
      iconData: Icons.nature_people_rounded,
      secondaryIcon: Icons.eco_rounded,
      slideType: OnboardingType.eco,
    ),
  ];

  Future<void> _completeOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('seen_onboarding', true);

    if (!mounted) return;

    if (widget.onFinish != null) {
      widget.onFinish!();
      return;
    }

    Widget nextScreen;
    if (widget.authService.isAuthenticated) {
      nextScreen = HomeScreen(authService: widget.authService);
    } else {
      nextScreen = LoginScreen(
        authService: widget.authService,
        onLoginSuccess: () {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (_) => HomeScreen(authService: widget.authService),
            ),
          );
        },
      );
    }

    Navigator.pushReplacement(
      context,
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 400),
        pageBuilder: (_, animation, __) => nextScreen,
        transitionsBuilder: (_, animation, __, child) {
          return FadeTransition(opacity: animation, child: child);
        },
      ),
    );
  }

  void _nextPage() {
    if (_currentPage < _slides.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeInOutCubic,
      );
    } else {
      _completeOnboarding();
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currentItem = _slides[_currentPage];

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          TextButton(
            onPressed: _completeOnboarding,
            child: const Text(
              'Lewati',
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // PageView Slider
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                itemCount: _slides.length,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                },
                itemBuilder: (context, index) {
                  return _buildSlideContent(_slides[index]);
                },
              ),
            ),

            // Bottom Navigation Area (Indicators + Apple styled Primary Button)
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
              child: Column(
                children: [
                  // Smooth Animated Indicator Dots
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      _slides.length,
                      (index) => AnimatedContainer(
                        duration: const Duration(milliseconds: 250),
                        margin: const EdgeInsets.symmetric(horizontal: 4),
                        height: 7,
                        width: _currentPage == index ? 24 : 7,
                        decoration: BoxDecoration(
                          color: _currentPage == index
                              ? currentItem.accentColor
                              : const Color(0xFFE2E8F0),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 28),

                  // Large Apple Style Action Button
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: currentItem.accentColor,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shadowColor: Colors.transparent,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      onPressed: _nextPage,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            _currentPage == _slides.length - 1
                                ? 'Mulai Sekarang'
                                : 'Lanjut',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              letterSpacing: -0.2,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Icon(
                            _currentPage == _slides.length - 1
                                ? Icons.arrow_forward_rounded
                                : Icons.arrow_forward_ios_rounded,
                            size: _currentPage == _slides.length - 1 ? 20 : 16,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSlideContent(OnboardingItem item) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Illustration Graphics
          Center(
            child: _buildGraphicIllustration(item),
          ),
          const SizedBox(height: 36),

          // Micro Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: item.accentColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: item.accentColor.withValues(alpha: 0.25),
                width: 1,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(item.secondaryIcon, size: 14, color: item.accentColor),
                const SizedBox(width: 6),
                Text(
                  item.badgeText,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: item.accentColor,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Headline
          Text(
            item.title,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w800,
              color: AppTheme.textPrimary,
              letterSpacing: -0.6,
              height: 1.25,
            ),
          ),
          const SizedBox(height: 12),

          // Subtitle
          Text(
            item.subtitle,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 14,
              color: AppTheme.textSecondary,
              height: 1.5,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGraphicIllustration(OnboardingItem item) {
    return SizedBox(
      width: 240,
      height: 240,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Ambient blurred aura
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: item.accentColor.withValues(alpha: 0.08),
            ),
          ),
          // Subtle concentric ring
          Container(
            width: 220,
            height: 220,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: item.accentColor.withValues(alpha: 0.15),
                width: 1.5,
              ),
            ),
          ),
          // Inner core container with soft shadow
          Container(
            width: 140,
            height: 140,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: item.accentColor.withValues(alpha: 0.2),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
              border: Border.all(
                color: item.accentColor.withValues(alpha: 0.12),
                width: 1,
              ),
            ),
            child: Center(
              child: Icon(
                item.iconData,
                size: 64,
                color: item.accentColor,
              ),
            ),
          ),
          // Custom contextual badges
          if (item.slideType == OnboardingType.aiScanner) ...[
            _buildFloatingPill(
              top: 20,
              left: 10,
              label: 'Organik',
              color: const Color(0xFF059669),
            ),
            _buildFloatingPill(
              bottom: 24,
              right: 8,
              label: 'Plastik',
              color: const Color(0xFF0284C7),
            ),
          ] else if (item.slideType == OnboardingType.gps) ...[
            _buildFloatingPill(
              top: 24,
              right: 12,
              label: '-6.2088° S',
              color: const Color(0xFF0284C7),
              isMono: true,
            ),
            _buildFloatingPill(
              bottom: 24,
              left: 10,
              label: '106.8456° E',
              color: const Color(0xFF0284C7),
              isMono: true,
            ),
          ] else ...[
            _buildFloatingPill(
              top: 20,
              right: 12,
              label: 'Selesai 100%',
              color: const Color(0xFF059669),
            ),
            _buildFloatingPill(
              bottom: 22,
              left: 10,
              label: 'Eco-Citizen',
              color: const Color(0xFF10B981),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFloatingPill({
    double? top,
    double? bottom,
    double? left,
    double? right,
    required String label,
    required Color color,
    bool isMono = false,
  }) {
    return Positioned(
      top: top,
      bottom: bottom,
      left: left,
      right: right,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.3)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            color: color,
            fontFamily: isMono ? 'monospace' : null,
          ),
        ),
      ),
    );
  }
}

enum OnboardingType {
  aiScanner,
  gps,
  eco,
}

class OnboardingItem {
  final String title;
  final String subtitle;
  final String badgeText;
  final Color accentColor;
  final IconData iconData;
  final IconData secondaryIcon;
  final OnboardingType slideType;

  const OnboardingItem({
    required this.title,
    required this.subtitle,
    required this.badgeText,
    required this.accentColor,
    required this.iconData,
    required this.secondaryIcon,
    required this.slideType,
  });
}
