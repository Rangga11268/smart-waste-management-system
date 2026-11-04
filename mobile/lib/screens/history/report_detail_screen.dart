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
    if (url.isEmpty) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    final base = AppConfig.baseUrl.replaceAll('/api/v1', '');
    if (url.startsWith('/')) {
      return '$base$url';
    }
    return '$base/$url';
  }

  String _formatStatusLabel(String raw) {
    switch (raw.toUpperCase().replaceAll('_', ' ')) {
      case 'PENDING':
        return 'Menunggu Validasi';
      case 'IN PROGRESS':
        return 'Sedang Ditangani';
      case 'COMPLETED':
        return 'Selesai Ditangani';
      case 'REJECTED':
        return 'Laporan Ditolak';
      default:
        return raw;
    }
  }

  @override
  Widget build(BuildContext context) {
    final report = _report;
    final reportCode = widget.reportId.length >= 8
        ? widget.reportId.substring(0, 8).toUpperCase()
        : widget.reportId.toUpperCase();

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: AppTheme.textPrimary,
        centerTitle: false,
        title: const Text(
          'Detail Laporan',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            letterSpacing: -0.3,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Segarkan data',
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
                      padding: const EdgeInsets.fromLTRB(18, 16, 18, 32),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // 1. Report Reference Bar (Clean Header, No Capsules)
                          _buildReportReferenceHeader(report, reportCode),
                          const SizedBox(height: 16),

                          // 2. Linear Workflow Stepper
                          _buildLinearProgressTracker(report.status),
                          const SizedBox(height: 20),

                          // 3. Report Title & Photo
                          Text(
                            report.title,
                            style: const TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.textPrimary,
                              letterSpacing: -0.5,
                              height: 1.25,
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Evidence Photo
                          _buildEvidencePhoto(report.imageUrl),
                          const SizedBox(height: 20),

                          // 4. AI Vision MobileNetV2 Intel Card
                          _buildAiIntelligenceCard(report),
                          const SizedBox(height: 14),

                          // 5. GPS & Reverse Geocoding Address Card
                          _buildLocationCard(report),
                          const SizedBox(height: 14),

                          // 6. Citizen Description & Notes
                          _buildDescriptionCard(report),
                          const SizedBox(height: 14),

                          // 7. Field Operator Notes (If available)
                          if (report.adminNotes != null && report.adminNotes!.isNotEmpty) ...[
                            _buildAdminNotesCard(report.adminNotes!),
                            const SizedBox(height: 14),
                          ],

                          // 8. Audit Trail Timeline
                          _buildAuditTrailTimeline(report.logs),
                        ],
                      ),
                    ),
    );
  }

  // 1. Clean Report Reference Header
  Widget _buildReportReferenceHeader(WasteReport report, String reportCode) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Text(
                    'ID:',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF64748B),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'SWMS-$reportCode',
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.5,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                ],
              ),
              Text(
                _formatDate(report.createdAt),
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Divider(height: 1, color: Color(0xFFF1F5F9)),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: AppTheme.getStatusColor(report.status),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _formatStatusLabel(report.status),
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.getStatusColor(report.status),
                    ),
                  ),
                ],
              ),
              Text(
                'Kategori: ${report.category.name}',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF334155),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // 2. Linear Progress Tracker (Clean, No Toy Bubbles)
  Widget _buildLinearProgressTracker(String status) {
    final s = status.toUpperCase().replaceAll('_', ' ');
    final isPending = s == 'PENDING';
    final isInProgress = s == 'IN PROGRESS';
    final isCompleted = s == 'COMPLETED';
    final isRejected = s == 'REJECTED';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'PROGRES PENANGANAN LAPORAN',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.8,
              color: Color(0xFF64748B),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildLinearStep(
                title: 'Diajukan',
                isDone: true,
                isActive: isPending,
              ),
              Expanded(
                child: Container(
                  height: 2,
                  color: (isInProgress || isCompleted)
                      ? AppTheme.primary
                      : const Color(0xFFE2E8F0),
                ),
              ),
              _buildLinearStep(
                title: 'Diproses',
                isDone: isInProgress || isCompleted,
                isActive: isInProgress,
              ),
              Expanded(
                child: Container(
                  height: 2,
                  color: isCompleted
                      ? AppTheme.primary
                      : (isRejected ? AppTheme.statusRejected : const Color(0xFFE2E8F0)),
                ),
              ),
              _buildLinearStep(
                title: isRejected ? 'Ditolak' : 'Selesai',
                isDone: isCompleted,
                isActive: isCompleted || isRejected,
                isRejected: isRejected,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLinearStep({
    required String title,
    required bool isDone,
    required bool isActive,
    bool isRejected = false,
  }) {
    Color iconColor;
    if (isRejected) {
      iconColor = AppTheme.statusRejected;
    } else if (isDone || isActive) {
      iconColor = AppTheme.primary;
    } else {
      iconColor = const Color(0xFF94A3B8);
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          isRejected
              ? Icons.cancel_rounded
              : (isDone ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded),
          size: 18,
          color: iconColor,
        ),
        const SizedBox(height: 4),
        Text(
          title,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isActive || isDone ? FontWeight.w700 : FontWeight.w500,
            color: isRejected
                ? AppTheme.statusRejected
                : (isActive || isDone ? const Color(0xFF0F172A) : const Color(0xFF64748B)),
          ),
        ),
      ],
    );
  }

  // 3. Evidence Photo
  Widget _buildEvidencePhoto(String imageUrl) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.network(
        _normalizeImageUrl(imageUrl),
        height: 230,
        width: double.infinity,
        fit: BoxFit.cover,
        errorBuilder: (ctx, err, stack) {
          return Container(
            height: 180,
            color: const Color(0xFFF1F5F9),
            child: const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF94A3B8)),
                  SizedBox(height: 6),
                  Text(
                    'Foto bukti tersimpan di server',
                    style: TextStyle(color: Color(0xFF64748B), fontSize: 12),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // 4. AI Vision MobileNetV2 Intel Card
  Widget _buildAiIntelligenceCard(WasteReport report) {
    final detectedCategory = report.detectedCategory ?? report.category.name;
    final confidencePercent = ((report.aiConfidence ?? 0.0) * 100).toStringAsFixed(1);
    final confidenceNum = report.aiConfidence ?? 0.0;
    final confidenceLabel = confidenceNum >= 0.8
        ? 'Tinggi'
        : (confidenceNum >= 0.6 ? 'Moderat' : 'Perlu Verifikasi');

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.smart_toy_outlined, size: 16, color: Color(0xFF0F172A)),
              SizedBox(width: 8),
              Text(
                'HASIL INFERENSI AI VISION (MOBILENETV2)',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _buildDetailRow(
            label: 'Kategori Terdeteksi',
            value: detectedCategory,
            isStrong: true,
          ),
          const SizedBox(height: 8),
          _buildDetailRow(
            label: 'Skor Akurasi / Keyakinan',
            value: '$confidencePercent% ($confidenceLabel)',
          ),
          const SizedBox(height: 8),
          _buildDetailRow(
            label: 'Model Arsitektur',
            value: 'PyTorch MobileNetV2 (<100ms)',
          ),
          const SizedBox(height: 8),
          _buildDetailRow(
            label: 'Status Klasifikasi',
            value: 'Tervalidasi Otomatis saat Pengiriman',
          ),
        ],
      ),
    );
  }

  // 5. GPS & Location Information Card
  Widget _buildLocationCard(WasteReport report) {
    final coords = '${report.latitude.toStringAsFixed(6)}, ${report.longitude.toStringAsFixed(6)}';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.location_on_outlined, size: 16, color: Color(0xFF0F172A)),
                  SizedBox(width: 8),
                  Text(
                    'KOORDINAT GEOSPASIAL & ALAMAT',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                      color: Color(0xFF64748B),
                    ),
                  ),
                ],
              ),
              InkWell(
                onTap: () {
                  Clipboard.setData(ClipboardData(text: coords));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Koordinat GPS berhasil disalin ke clipboard'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
                borderRadius: BorderRadius.circular(4),
                child: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  child: Row(
                    children: [
                      Icon(Icons.copy_rounded, size: 13, color: Color(0xFF0F172A)),
                      SizedBox(width: 4),
                      Text(
                        'Salin GPS',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildDetailRow(
            label: 'Titik Koordinat',
            value: coords,
            isMonospace: true,
          ),
          if (report.addressNote != null && report.addressNote!.isNotEmpty) ...[
            const SizedBox(height: 8),
            _buildDetailRow(
              label: 'Patokan / Alamat Lengkap',
              value: report.addressNote!,
            ),
          ],
          const SizedBox(height: 8),
          _buildDetailRow(
            label: 'Metode Penguncian',
            value: 'GPS Satelit Kamera Ponsel (WIB)',
          ),
        ],
      ),
    );
  }

  // 6. Citizen Description Card
  Widget _buildDescriptionCard(WasteReport report) {
    final desc = (report.description != null && report.description!.trim().isNotEmpty)
        ? report.description!
        : 'Tidak ada deskripsi tambahan dari pelapor.';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.notes_rounded, size: 16, color: Color(0xFF0F172A)),
              SizedBox(width: 8),
              Text(
                'DESKRIPSI & KETERANGAN PELAPOR',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            desc,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xFF334155),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  // 7. Field Operator Notes Card
  Widget _buildAdminNotesCard(String notes) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFCBD5E1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.assignment_ind_outlined, size: 16, color: Color(0xFF0F172A)),
              SizedBox(width: 8),
              Text(
                'DISPOSISI / CATATAN PETUGAS LAPANGAN',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: Color(0xFF0F172A),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            notes,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: Color(0xFF1E293B),
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }

  // 8. Audit Trail Timeline
  Widget _buildAuditTrailTimeline(List<ReportLog> logs) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.history_rounded, size: 16, color: Color(0xFF0F172A)),
                  SizedBox(width: 8),
                  Text(
                    'AUDIT TRAIL & RIWAYAT DISPOSISI',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                      color: Color(0xFF64748B),
                    ),
                  ),
                ],
              ),
              Text(
                '${logs.length} Log Terverifikasi',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          if (logs.isEmpty)
            const Text(
              'Belum ada riwayat status tercatat.',
              style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
            )
          else
            ...logs.asMap().entries.map((entry) {
              final idx = entry.key;
              final log = entry.value;
              final isLast = idx == logs.length - 1;

              return IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Vertical Timeline Line & Point
                    SizedBox(
                      width: 16,
                      child: Column(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            margin: const EdgeInsets.only(top: 4),
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                          if (!isLast)
                            Expanded(
                              child: Container(
                                width: 1.5,
                                color: const Color(0xFFE2E8F0),
                              ),
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(bottom: isLast ? 0 : 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Status: ${_formatStatusLabel(log.newStatus)}',
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            if (log.remarks != null && log.remarks!.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(top: 2),
                                child: Text(
                                  log.remarks!,
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF475569),
                                  ),
                                ),
                              ),
                            const SizedBox(height: 2),
                            Text(
                              _formatDate(log.createdAt),
                              style: const TextStyle(
                                fontSize: 11,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildDetailRow({
    required String label,
    required String value,
    bool isStrong = false,
    bool isMonospace = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: Color(0xFF64748B),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            fontWeight: isStrong ? FontWeight.w800 : FontWeight.w600,
            fontFamily: isMonospace ? 'monospace' : null,
            color: const Color(0xFF0F172A),
          ),
        ),
      ],
    );
  }
}
