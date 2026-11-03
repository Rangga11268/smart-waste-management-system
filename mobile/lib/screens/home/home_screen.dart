import 'package:flutter/material.dart';
import '../../config/app_config.dart';
import '../../models/user.dart';
import '../../models/waste_report.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../theme/app_theme.dart';
import '../history/history_screen.dart';
import '../history/report_detail_screen.dart';
import '../report/create_report_screen.dart';
import '../settings/server_settings_screen.dart';

class HomeScreen extends StatefulWidget {
  final AuthService authService;

  const HomeScreen({super.key, required this.authService});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  late ApiService _apiService;

  Map<String, dynamic> _stats = {
    'total_reports': 0,
    'pending_reports': 0,
    'in_progress_reports': 0,
    'completed_reports': 0,
  };
  List<WasteReport> _recentReports = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService(token: widget.authService.token);
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final statsData = await _apiService.getDashboardStats();
      final reportsData = await _apiService.getReports(limit: 6);

      if (mounted) {
        setState(() {
          _stats = statsData;
          _recentReports = reportsData;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _openCreateReport() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CreateReportScreen(
          apiService: _apiService,
          onReportCreated: _loadDashboardData,
        ),
      ),
    ).then((_) => _loadDashboardData());
  }

  String _normalizeImageUrl(String url) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    final base = AppConfig.baseUrl.replaceAll('/api/v1', '');
    if (url.startsWith('/')) {
      return '$base$url';
    }
    return '$base/$url';
  }

  @override
  Widget build(BuildContext context) {
    final user = widget.authService.currentUser;

    final List<Widget> pages = [
      _buildHomeTab(user),
      const SizedBox.shrink(), // Placeholder for central report action
      HistoryScreen(
        apiService: _apiService,
        currentUserId: user?.id,
      ),
      _buildProfileTab(user),
    ];

    return Scaffold(
      body: pages[_currentIndex == 1 ? 0 : _currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        height: 72,
        backgroundColor: Colors.white,
        elevation: 2,
        indicatorColor: AppTheme.primaryContainer,
        onDestinationSelected: (idx) {
          if (idx == 1) {
            _openCreateReport();
          } else {
            setState(() {
              _currentIndex = idx;
            });
          }
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: AppTheme.primaryDark),
            label: 'Beranda',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_circle, color: AppTheme.primary, size: 28),
            selectedIcon: Icon(Icons.add_circle, color: AppTheme.primaryDark, size: 28),
            label: 'Lapor',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history, color: AppTheme.primaryDark),
            label: 'Riwayat',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: AppTheme.primaryDark),
            label: 'Profil',
          ),
        ],
      ),
    );
  }

  Widget _buildHomeTab(User? user) {
    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      color: AppTheme.primary,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(18, 52, 18, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Top Header with User Greeting & Live Backend Indicator
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Halo, ${user?.fullName.split(' ').first ?? 'Citizen'} 👋',
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.textPrimary,
                          letterSpacing: -0.5,
                        ),
                      ),
                      const SizedBox(height: 3),
                      const Text(
                        'Jaga kebersihan lingkungan bersama SWMS',
                        style: TextStyle(
                          fontSize: 13,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      // Live backend connection pill
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryContainer.withValues(alpha: 0.7),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppTheme.primaryLight.withValues(alpha: 0.4)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 7,
                              height: 7,
                              decoration: const BoxDecoration(
                                color: AppTheme.primary,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 6),
                            const Text(
                              'Backend Terhubung',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: AppTheme.onPrimaryContainer,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.settings_outlined, color: AppTheme.textSecondary),
                  tooltip: 'Server Settings',
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ServerSettingsScreen()),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 20),

            // 2. Hero CTA Card (AI Smart Waste Scanner)
            _buildHeroCtaCard(),
            const SizedBox(height: 24),

            // 3. Compact KPI Metrics Summary
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Ringkasan Laporan',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
                Text(
                  'Update Realtime',
                  style: TextStyle(fontSize: 12, color: AppTheme.textTertiary),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildStatsGrid(),
            const SizedBox(height: 28),

            // 4. Recent Reports Feed Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Feed Laporan Terbaru',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
                TextButton(
                  onPressed: () {
                    setState(() {
                      _currentIndex = 2; // Switch to History tab
                    });
                  },
                  child: const Text(
                    'Lihat Semua',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            if (_isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(color: AppTheme.primary),
                ),
              )
            else if (_recentReports.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20, vertical: 32),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(Icons.check_circle_outline_rounded, size: 44, color: AppTheme.primary),
                        SizedBox(height: 12),
                        Text(
                          'Lingkungan Anda Bersih!',
                          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Belum ada laporan sampah aktif. Laporkan tumpukan baru untuk ditindaklanjuti.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ),
              )
            else
              ..._recentReports.map((r) => _buildRecentItem(r)),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroCtaCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF059669), Color(0xFF047857)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF059669).withValues(alpha: 0.28),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.22),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.auto_awesome, color: Colors.white, size: 22),
              ),
              const SizedBox(width: 10),
              const Text(
                'AI Smart Waste Scanner',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Temukan tumpukan sampah? Foto langsung untuk klasifikasi otomatis (Organik, Plastik, Kertas) & kunci koordinat GPS.',
            style: TextStyle(
              color: Colors.white,
              fontSize: 13,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: AppTheme.primaryDark,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              onPressed: _openCreateReport,
              icon: const Icon(Icons.photo_camera_rounded, size: 20),
              label: const Text(
                'Ambil Foto & Lapor Sekarang',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsGrid() {
    final total = _stats['total_reports'] ?? 0;
    final pending = _stats['pending_reports'] ?? 0;
    final inProgress = _stats['in_progress_reports'] ?? 0;
    final completed = _stats['completed_reports'] ?? 0;

    return Row(
      children: [
        Expanded(
          child: _buildStatCard('Total', total.toString(), Icons.layers_outlined, AppTheme.textPrimary, Colors.white),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard('Menunggu', pending.toString(), Icons.hourglass_top, AppTheme.statusPending, AppTheme.statusPendingBg),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard('Diproses', inProgress.toString(), Icons.build_circle_outlined, AppTheme.statusInProgress, AppTheme.statusInProgressBg),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard('Selesai', completed.toString(), Icons.task_alt, AppTheme.statusCompleted, AppTheme.statusCompletedBg),
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String count, IconData icon, Color color, Color bg) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border, width: 1),
      ),
      child: Column(
        children: [
          Icon(icon, size: 18, color: color),
          const SizedBox(height: 4),
          Text(
            count,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentItem(WasteReport r) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ReportDetailScreen(
                reportId: r.id,
                apiService: _apiService,
                initialReport: r,
              ),
            ),
          ).then((_) => _loadDashboardData());
        },
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. Photo Thumbnail with 12dp Radius
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  _normalizeImageUrl(r.imageUrl),
                  width: 74,
                  height: 74,
                  fit: BoxFit.cover,
                  errorBuilder: (ctx, err, stack) {
                    return Container(
                      width: 74,
                      height: 74,
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceMuted,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.image_not_supported_outlined,
                        color: AppTheme.textTertiary,
                        size: 26,
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(width: 14),

              // 2. Report Information & Top-Right Status Chip
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Status Chip at top-right & Category Badge
                    Row(
                      children: [
                        // Category Pill with Accent Dot
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: AppTheme.surfaceMuted,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 6,
                                height: 6,
                                decoration: const BoxDecoration(
                                  color: AppTheme.primary,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 5),
                              Text(
                                r.category.name,
                                style: const TextStyle(
                                  color: AppTheme.textPrimary,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 10,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Spacer(),
                        // Modern Status Chip in Top Right
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: AppTheme.getStatusBgColor(r.status),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: AppTheme.getStatusBorderColor(r.status),
                              width: 1,
                            ),
                          ),
                          child: Text(
                            r.status.toUpperCase(),
                            style: TextStyle(
                              color: AppTheme.getStatusColor(r.status),
                              fontWeight: FontWeight.w700,
                              fontSize: 10,
                              letterSpacing: 0.2,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),

                    // Title
                    Text(
                      r.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                        letterSpacing: -0.2,
                      ),
                    ),
                    const SizedBox(height: 4),

                    // Location / Address note & Relative Time
                    Row(
                      children: [
                        const Icon(Icons.location_on_outlined, size: 13, color: AppTheme.textTertiary),
                        const SizedBox(width: 3),
                        Expanded(
                          child: Text(
                            r.addressNote?.isNotEmpty == true
                                ? r.addressNote!
                                : '${r.latitude.toStringAsFixed(4)}, ${r.longitude.toStringAsFixed(4)}',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary),
                          ),
                        ),
                        const SizedBox(width: 6),
                        // Relative time format
                        Text(
                          AppTheme.formatRelativeTime(r.createdAt),
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                            color: AppTheme.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileTab(User? user) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profil & Pengaturan'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // User Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppTheme.primaryContainer,
                    child: Text(
                      user?.fullName.isNotEmpty == true ? user!.fullName[0].toUpperCase() : 'U',
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.primaryDark,
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user?.fullName ?? 'Citizen User',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            color: AppTheme.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          user?.email ?? '-',
                          style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                        ),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryContainer,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            (user?.role ?? 'citizen').toUpperCase(),
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: AppTheme.onPrimaryContainer,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Menu items
          const Text(
            'Pengaturan Aplikasi',
            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: AppTheme.textPrimary),
          ),
          const SizedBox(height: 10),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.dns_outlined, color: AppTheme.primary),
                  title: const Text('Konfigurasi Endpoint API Server'),
                  subtitle: const Text('Atur Base URL FastAPI backend'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ServerSettingsScreen()),
                    );
                  },
                ),
                const Divider(height: 1, color: AppTheme.border),
                ListTile(
                  leading: const Icon(Icons.info_outline, color: AppTheme.primary),
                  title: const Text('Tentang SWMS Mobile'),
                  subtitle: const Text('Versi 1.0.0 (Bilcode Tech Assessment)'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                  onTap: () {
                    showAboutDialog(
                      context: context,
                      applicationName: 'Smart Waste Management System (SWMS)',
                      applicationVersion: '1.0.0',
                      applicationLegalese: 'Dikembangkan untuk Bilcode Technology Technical Test',
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Logout Button
          SizedBox(
            width: double.infinity,
            height: 50,
            child: OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                foregroundColor: AppTheme.statusRejected,
                side: const BorderSide(color: AppTheme.statusRejectedBorder, width: 1.2),
              ),
              onPressed: () async {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Konfirmasi Keluar'),
                    content: const Text('Apakah Anda yakin ingin keluar dari akun ini?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Batal'),
                      ),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: AppTheme.statusRejected),
                        onPressed: () => Navigator.pop(ctx, true),
                        child: const Text('Keluar'),
                      ),
                    ],
                  ),
                );

                if (confirm == true) {
                  widget.authService.logout();
                }
              },
              icon: const Icon(Icons.logout),
              label: const Text('Keluar dari Akun'),
            ),
          ),
        ],
      ),
    );
  }
}
