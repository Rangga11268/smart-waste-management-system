import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../../config/app_config.dart';
import '../../models/waste_report.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import '../../widgets/skeleton_loader.dart';

class ReportDetailScreen extends StatefulWidget {
  final String reportId;
  final ApiService apiService;
  final WasteReport? initialReport;

  const ReportDetailScreen({
    super.key,
    required this.reportId,
    required this.apiService,
    this.initialReport,
  });

  @override
  State<ReportDetailScreen> createState() => _ReportDetailScreenState();
}

class _ReportDetailScreenState extends State<ReportDetailScreen> {
  late WasteReport? _report;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _report = widget.initialReport;
    _fetchDetail();
  }

  Future<void> _fetchDetail() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final res = await widget.apiService.getReportDetail(widget.reportId);
      if (mounted) {
        setState(() {
          _report = res;
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
    // Relative upload url from backend
    final base = AppConfig.baseUrl.replaceAll('/api/v1', '');
    if (url.startsWith('/')) {
      return '$base$url';
    }
    return '$base/$url';
  }

  Widget _buildStepItem({
    required String stepNum,
    required String label,
    required bool isActive,
    required bool isDone,
    bool isRejected = false,
  }) {
    Color bg = Colors.grey.shade200;
    Color fg = Colors.grey.shade600;
    if (isRejected) {
      bg = AppTheme.statusRejected.withValues(alpha: 0.15);
      fg = AppTheme.statusRejected;
    } else if (isActive || isDone) {
      bg = AppTheme.primary;
      fg = Colors.white;
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: bg,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: isDone && !isRejected
                ? const Icon(Icons.check, size: 14, color: Colors.white)
                : Text(
                    stepNum,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: fg,
                    ),
                  ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
            color: isRejected
                ? AppTheme.statusRejected
                : (isActive ? AppTheme.textPrimary : AppTheme.textSecondary),
          ),
        ),
      ],
    );
  }

  Widget _buildStepDivider({required bool isDone}) {
    return Expanded(
      child: Container(
        height: 2,
        margin: const EdgeInsets.only(bottom: 14, left: 4, right: 4),
        color: isDone ? AppTheme.primary : Colors.grey.shade300,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final report = _report;

    return Scaffold(
      appBar: AppBar(
        title: Text(report != null ? '#${report.id.substring(0, 8)}' : 'Detail Laporan'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Segarkan',
            onPressed: _fetchDetail,
          ),
        ],
      ),
      body: _isLoading && report == null
          ? const ReportDetailSkeleton()
          : _error != null && report == null
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
                          onPressed: _fetchDetail,
                          child: const Text('Coba Lagi'),
                        ),
                      ],
                    ),
                  ),
                )
              : report == null
                  ? const Center(child: Text('Laporan tidak ditemukan'))
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // 1. Status & Category Header
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppTheme.getStatusBgColor(report.status),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: AppTheme.getStatusBorderColor(report.status)),
                                ),
                                child: Text(
                                  report.status.toUpperCase(),
                                  style: TextStyle(
                                    color: AppTheme.getStatusColor(report.status),
                                    fontWeight: FontWeight.w700,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppTheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  report.category.name,
                                  style: const TextStyle(
                                    color: AppTheme.onPrimaryContainer,
                                    fontWeight: FontWeight.w700,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                              const Spacer(),
                              Text(
                                _formatDate(report.createdAt),
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: AppTheme.textSecondary,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),

                          // Visual Status Stepper Tracker
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: AppTheme.border),
                            ),
                            child: Row(
                              children: [
                                _buildStepItem(
                                  stepNum: '1',
                                  label: 'Diajukan',
                                  isActive: true,
                                  isDone: true,
                                ),
                                _buildStepDivider(
                                  isDone: report.status == 'IN_PROGRESS' || report.status == 'COMPLETED',
                                ),
                                _buildStepItem(
                                  stepNum: '2',
                                  label: 'Diproses',
                                  isActive: report.status == 'IN_PROGRESS' || report.status == 'COMPLETED',
                                  isDone: report.status == 'IN_PROGRESS' || report.status == 'COMPLETED',
                                ),
                                _buildStepDivider(
                                  isDone: report.status == 'COMPLETED',
                                ),
                                _buildStepItem(
                                  stepNum: report.status == 'REJECTED' ? '✕' : '3',
                                  label: report.status == 'REJECTED' ? 'Ditolak' : 'Selesai',
                                  isActive: report.status == 'COMPLETED' || report.status == 'REJECTED',
                                  isDone: report.status == 'COMPLETED',
                                  isRejected: report.status == 'REJECTED',
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 14),

                          // 2. Title
                          Text(
                            report.title,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.textPrimary,
                              letterSpacing: -0.5,
                            ),
                          ),
                          const SizedBox(height: 16),

                          // 3. Evidence Image
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.network(
                              _normalizeImageUrl(report.imageUrl),
                              height: 240,
                              width: double.infinity,
                              fit: BoxFit.cover,
                              errorBuilder: (ctx, err, stack) {
                                return Container(
                                  height: 200,
                                  color: const Color(0xFFF1F5F9),
                                  child: const Center(
                                    child: Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        Icon(Icons.broken_image_outlined, size: 48, color: AppTheme.textSecondary),
                                        SizedBox(height: 8),
                                        Text('Gambar tersimpan di server', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                                      ],
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                          const SizedBox(height: 16),

                          // 4. AI Prediction Badge
                          if (report.detectedCategory != null || (report.aiConfidence != null && report.aiConfidence! > 0)) ...[
                            Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: AppTheme.primaryContainer.withValues(alpha: 0.5),
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: AppTheme.primary.withValues(alpha: 0.4)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.auto_awesome, color: AppTheme.primary, size: 20),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'Klasifikasi Citra AI MobileNetV2',
                                          style: TextStyle(
                                            fontSize: 12,
                                            fontWeight: FontWeight.w700,
                                            color: AppTheme.onPrimaryContainer,
                                          ),
                                        ),
                                        const SizedBox(height: 2),
                                        Text(
                                          'Kategori: ${report.detectedCategory ?? report.category.name} • Akurasi: ${((report.aiConfidence ?? 0.0) * 100).toStringAsFixed(1)}%',
                                          style: const TextStyle(
                                            fontSize: 13,
                                            fontWeight: FontWeight.w600,
                                            color: AppTheme.textPrimary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // 5. GPS & Location Information
                          Card(
                            child: Padding(
                              padding: const EdgeInsets.all(14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      const Icon(Icons.location_on, color: AppTheme.statusInProgress, size: 18),
                                      const SizedBox(width: 8),
                                      const Text(
                                        'Lokasi & Koordinat GPS',
                                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                                      ),
                                      const Spacer(),
                                      IconButton(
                                        icon: const Icon(Icons.copy, size: 16),
                                        tooltip: 'Salin Koordinat',
                                        visualDensity: VisualDensity.compact,
                                        onPressed: () {
                                          Clipboard.setData(ClipboardData(
                                            text: '${report.latitude}, ${report.longitude}',
                                          ));
                                          ScaffoldMessenger.of(context).showSnackBar(
                                            const SnackBar(
                                              content: Text('Koordinat berhasil disalin'),
                                              duration: Duration(seconds: 2),
                                            ),
                                          );
                                        },
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    '${report.latitude.toStringAsFixed(6)}, ${report.longitude.toStringAsFixed(6)}',
                                    style: const TextStyle(
                                      fontFamily: 'monospace',
                                      fontSize: 13,
                                      fontWeight: FontWeight.w600,
                                      color: AppTheme.textPrimary,
                                    ),
                                  ),
                                  if (report.addressNote != null && report.addressNote!.isNotEmpty) ...[
                                    const SizedBox(height: 6),
                                    Text(
                                      'Patokan: ${report.addressNote}',
                                      style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // 6. Description
                          if (report.description != null && report.description!.isNotEmpty) ...[
                            const Text(
                              'Deskripsi Pelapor:',
                              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              report.description!,
                              style: const TextStyle(fontSize: 14, height: 1.4, color: AppTheme.textPrimary),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // 7. Admin / Operator Notes
                          if (report.adminNotes != null && report.adminNotes!.isNotEmpty) ...[
                            Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: const Color(0xFFEFF6FF),
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: const Color(0xFFBFDBFE)),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Row(
                                    children: [
                                      Icon(Icons.support_agent, color: Color(0xFF1D4ED8), size: 18),
                                      SizedBox(width: 8),
                                      Text(
                                        'Catatan Petugas / Admin:',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 13,
                                          color: Color(0xFF1E3A8A),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    report.adminNotes!,
                                    style: const TextStyle(fontSize: 13, color: Color(0xFF1E3A8A)),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // 8. Status History Logs
                          if (report.logs.isNotEmpty) ...[
                            const Text(
                              'Riwayat Penanganan (Audit Logs):',
                              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                            ),
                            const SizedBox(height: 10),
                            ...report.logs.map((log) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 10),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Container(
                                      margin: const EdgeInsets.only(top: 2),
                                      width: 8,
                                      height: 8,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: AppTheme.getStatusColor(log.newStatus),
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            'Status diubah menjadi ${log.newStatus}',
                                            style: const TextStyle(
                                              fontWeight: FontWeight.w600,
                                              fontSize: 13,
                                              color: AppTheme.textPrimary,
                                            ),
                                          ),
                                          if (log.remarks != null && log.remarks!.isNotEmpty)
                                            Text(
                                              log.remarks!,
                                              style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                                            ),
                                          Text(
                                            _formatDate(log.createdAt),
                                            style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }),
                          ],
                        ],
                      ),
                    ),
    );
  }
}
