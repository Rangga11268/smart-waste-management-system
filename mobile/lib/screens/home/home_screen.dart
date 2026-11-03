import 'package:flutter/material.dart';
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
      final reportsData = await _apiService.getReports(limit: 5);

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

  @override
  Widget build(BuildContext context) {
    final user = widget.authService.currentUser;

    final List<Widget> pages = [
      _buildHomeTab(user),
      const SizedBox.shrink(), // Placeholder for center CTA action
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
            selectedIcon: Icon(Icons.home, color: AppTheme.primary),
            label: 'Beranda',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_circle, color: AppTheme.primary, size: 30),
            selectedIcon: Icon(Icons.add_circle, color: AppTheme.primary, size: 30),
            label: 'Laporkan',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history, color: AppTheme.primary),
            label: 'Riwayat',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: AppTheme.primary),
            label: 'Akun',
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
        padding: const EdgeInsets.fromLTRB(18, 54, 18, 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Bar
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Halo, ${user?.fullName ?? 'Citizen'} 👋',
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.textPrimary,
                          letterSpacing: -0.5,
                        ),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Jaga kebersihan lingkungan bersama SWMS',
                        style: TextStyle(
                          fontSize: 13,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.settings_outlined),
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

            // Hero CTA Card
            _buildHeroCtaCard(),
            const SizedBox(height: 24),

            // KPI Summary Stats
            const Text(
              'Statistik Pengelolaan Sampah',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 12),
            _buildStatsGrid(),
            const SizedBox(height: 28),

            // Recent Reports Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Laporan Terbaru',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                  ),
                ),
                TextButton(
                  onPressed: () {
                    setState(() {
                      _currentIndex = 2; // Switch to History tab
                    });
                  },
                  child: const Text('Lihat Semua'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (_isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (_recentReports.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(Icons.check_circle_outline, size: 40, color: AppTheme.primary),
                        SizedBox(height: 8),
                        Text(
                          'Belum ada laporan sampah aktif',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Gunakan tombol "Laporkan Sampah" untuk memulai.',
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
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF059669), Color(0xFF047857)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF059669).withValues(alpha: 0.25),
            blurRadius: 16,
            offset: const Offset(0, 6),
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
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.auto_awesome, color: Colors.white, size: 22),
              ),
              const SizedBox(width: 10),
              const Text(
                'AI Smart Waste Scanner',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 15,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Temukan tumpukan sampah? Foto langsung dengan kamera untuk klasifikasi otomatis (Organik, Plastik, Kertas) & kunci koordinat GPS.',
            style: TextStyle(
              color: Colors.white,
              fontSize: 13,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: AppTheme.primaryDark,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: _openCreateReport,
              icon: const Icon(Icons.photo_camera_rounded),
              label: const Text(
                'Ambil Foto & Lapor Sekarang',
                style: TextStyle(fontWeight: FontWeight.w700),
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
          child: _buildStatCard('Total Laporan', total.toString(), Icons.layers_outlined, AppTheme.textPrimary),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard('Menunggu', pending.toString(), Icons.hourglass_top, AppTheme.statusPending),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard('Diproses', inProgress.toString(), Icons.build_circle_outlined, AppTheme.statusInProgress),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard('Selesai', completed.toString(), Icons.task_alt, AppTheme.statusCompleted),
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String count, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
        child: Column(
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(height: 6),
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
              style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentItem(WasteReport r) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
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
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.getStatusBgColor(r.status),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            Icons.delete_outline_rounded,
            color: AppTheme.getStatusColor(r.status),
            size: 22,
          ),
        ),
        title: Text(
          r.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
        ),
        subtitle: Text(
          '${r.category.name} • ${r.status}',
          style: TextStyle(
            fontSize: 12,
            color: AppTheme.getStatusColor(r.status),
            fontWeight: FontWeight.w600,
          ),
        ),
        trailing: const Icon(Icons.chevron_right, size: 18, color: AppTheme.textSecondary),
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
                    radius: 30,
                    backgroundColor: AppTheme.primaryContainer,
                    child: Text(
                      user?.fullName.isNotEmpty == true ? user!.fullName[0].toUpperCase() : 'U',
                      style: const TextStyle(
                        fontSize: 24,
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
            child: OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                foregroundColor: AppTheme.statusRejected,
                side: const BorderSide(color: AppTheme.statusRejected),
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
