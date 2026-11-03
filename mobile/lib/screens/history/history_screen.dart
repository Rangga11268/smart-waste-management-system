import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../config/app_config.dart';
import '../../models/waste_report.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import 'report_detail_screen.dart';

class HistoryScreen extends StatefulWidget {
  final ApiService apiService;
  final String? currentUserId;

  const HistoryScreen({
    super.key,
    required this.apiService,
    this.currentUserId,
  });

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<WasteReport> _reports = [];
  bool _isLoading = true;
  String? _error;
  String _selectedFilter = 'ALL';
  bool _onlyMyReports = false;

  final List<String> _filters = ['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'REJECTED'];

  @override
  void initState() {
    super.initState();
    _fetchReports();
  }

  Future<void> _fetchReports() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final statusParam = _selectedFilter == 'ALL' ? null : _selectedFilter;
      final list = await widget.apiService.getReports(status: statusParam, limit: 50);
      if (mounted) {
        setState(() {
          _reports = list;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceAll('Exception: ', '');
          _isLoading = false;
        });
      }
    }
  }

  String _formatDate(DateTime dt) {
    return DateFormat('dd MMM yyyy, HH:mm').format(dt);
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

  List<WasteReport> get _filteredReports {
    if (_onlyMyReports && widget.currentUserId != null) {
      return _reports.where((r) => r.reporter.id == widget.currentUserId).toList();
    }
    return _reports;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Riwayat Laporan Sampah'),
        actions: [
          IconButton(
            icon: Icon(
              _onlyMyReports ? Icons.person : Icons.public,
              color: _onlyMyReports ? AppTheme.primary : AppTheme.textSecondary,
            ),
            tooltip: _onlyMyReports ? 'Laporan Saya' : 'Semua Laporan Komunitas',
            onPressed: () {
              setState(() {
                _onlyMyReports = !_onlyMyReports;
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Segarkan',
            onPressed: _fetchReports,
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: _filters.map((filter) {
                final isSelected = _selectedFilter == filter;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(
                      filter == 'ALL' ? 'Semua' : filter.replaceAll('_', ' '),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                        color: isSelected ? Colors.white : AppTheme.textPrimary,
                      ),
                    ),
                    selected: isSelected,
                    selectedColor: AppTheme.primary,
                    checkmarkColor: Colors.white,
                    backgroundColor: Colors.white,
                    side: BorderSide(
                      color: isSelected ? AppTheme.primary : AppTheme.border,
                    ),
                    onSelected: (val) {
                      setState(() {
                        _selectedFilter = filter;
                      });
                      _fetchReports();
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          // Main List
          Expanded(
            child: RefreshIndicator(
              onRefresh: _fetchReports,
              color: AppTheme.primary,
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _error != null
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.error_outline, size: 48, color: AppTheme.statusRejected),
                                const SizedBox(height: 12),
                                Text(_error!, textAlign: TextAlign.center),
                                const SizedBox(height: 16),
                                ElevatedButton(
                                  onPressed: _fetchReports,
                                  child: const Text('Coba Lagi'),
                                ),
                              ],
                            ),
                          ),
                        )
                      : _filteredReports.isEmpty
                          ? const Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.inbox_outlined, size: 60, color: AppTheme.textSecondary),
                                  SizedBox(height: 12),
                                  Text(
                                    'Belum ada laporan sampah',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                      color: AppTheme.textPrimary,
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    'Laporan yang Anda kirimkan akan tampil di sini',
                                    style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                                  ),
                                ],
                              ),
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.all(16),
                              itemCount: _filteredReports.length,
                              separatorBuilder: (_, __) => const SizedBox(height: 12),
                              itemBuilder: (context, index) {
                                final report = _filteredReports[index];
                                return _buildReportCard(report);
                              },
                            ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReportCard(WasteReport report) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ReportDetailScreen(
                reportId: report.id,
                apiService: widget.apiService,
                initialReport: report,
              ),
            ),
          ).then((_) => _fetchReports());
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Thumbnail
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.network(
                  _normalizeImageUrl(report.imageUrl),
                  width: 72,
                  height: 72,
                  fit: BoxFit.cover,
                  errorBuilder: (ctx, err, stack) {
                    return Container(
                      width: 72,
                      height: 72,
                      color: const Color(0xFFF1F5F9),
                      child: const Icon(Icons.image_not_supported_outlined, color: AppTheme.textSecondary),
                    );
                  },
                ),
              ),
              const SizedBox(width: 14),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.getStatusBgColor(report.status),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            report.status.toUpperCase(),
                            style: TextStyle(
                              color: AppTheme.getStatusColor(report.status),
                              fontWeight: FontWeight.w700,
                              fontSize: 10,
                            ),
                          ),
                        ),
                        const SizedBox(width: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryContainer,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            report.category.name,
                            style: const TextStyle(
                              color: AppTheme.onPrimaryContainer,
                              fontWeight: FontWeight.w700,
                              fontSize: 10,
                            ),
                          ),
                        ),
                        const Spacer(),
                        Text(
                          _formatDate(report.createdAt),
                          style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      report.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    if (report.addressNote != null && report.addressNote!.isNotEmpty) ...[
                      const SizedBox(height: 3),
                      Row(
                        children: [
                          const Icon(Icons.location_on_outlined, size: 14, color: AppTheme.textSecondary),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              report.addressNote!,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
