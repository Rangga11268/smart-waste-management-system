import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../models/category.dart';
import '../../models/prediction_result.dart';
import '../../services/api_service.dart';
import '../../services/location_service.dart';
import '../../theme/app_theme.dart';
import '../../widgets/dashed_border.dart';

class CreateReportScreen extends StatefulWidget {
  final ApiService apiService;
  final VoidCallback? onReportCreated;

  const CreateReportScreen({
    super.key,
    required this.apiService,
    this.onReportCreated,
  });

  @override
  State<CreateReportScreen> createState() => _CreateReportScreenState();
}

class _CreateReportScreenState extends State<CreateReportScreen> {
  final _formKey = GlobalKey<FormState>();
  final _imagePicker = ImagePicker();

  Uint8List? _imageBytes;
  String? _imageName;
  bool _isAnalyzingAI = false;
  PredictionResult? _aiResult;
  String? _aiError;

  bool _isLoadingGps = false;
  LocationResult? _location;

  List<WasteCategory> _categories = [];
  int? _selectedCategoryId;

  final _titleController = TextEditingController();
  final _descController = TextEditingController();
  final _addressController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _loadCategories();
    _fetchGpsLocation();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  Future<void> _loadCategories() async {
    try {
      final list = await widget.apiService.getCategories();
      if (mounted) {
        setState(() {
          _categories = list;
          if (_categories.isNotEmpty && _selectedCategoryId == null) {
            _selectedCategoryId = _categories.first.id;
          }
        });
      }
    } catch (_) {}
  }

  Future<void> _fetchGpsLocation() async {
    setState(() {
      _isLoadingGps = true;
    });

    final loc = await LocationService.getCurrentLocation();
    if (mounted) {
      setState(() {
        _location = loc;
        _isLoadingGps = false;
        if (loc.address != null && _addressController.text.isEmpty) {
          _addressController.text = loc.address!;
        }
      });
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1200,
        maxHeight: 1200,
        imageQuality: 85,
      );

      if (picked != null) {
        final bytes = await picked.readAsBytes();
        setState(() {
          _imageBytes = bytes;
          _imageName = picked.name;
          _aiResult = null;
          _aiError = null;
        });

        // Trigger automatic AI analysis
        _runAiInference(bytes, picked.name);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal memilih gambar: $e'),
            backgroundColor: AppTheme.statusRejected,
          ),
        );
      }
    }
  }

  Future<void> _runAiInference(Uint8List bytes, String filename) async {
    setState(() {
      _isAnalyzingAI = true;
      _aiError = null;
    });

    try {
      final result = await widget.apiService.predictImage(bytes, filename);
      if (mounted) {
        setState(() {
          _aiResult = result;
          _isAnalyzingAI = false;
          _selectedCategoryId = result.categoryId;

          // Auto-fill suggested title if still empty
          if (_titleController.text.isEmpty) {
            _titleController.text = 'Tumpukan Sampah ${result.category}';
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _aiError = e.toString().replaceAll('Exception: ', '');
          _isAnalyzingAI = false;
        });
      }
    }
  }

  void _onCategoryChanged(int? newId) {
    if (newId == null) return;
    setState(() {
      _selectedCategoryId = newId;
      final selectedCat = _categories.firstWhere(
        (c) => c.id == newId,
        orElse: () => _categories.first,
      );
      _titleController.text = 'Tumpukan Sampah ${selectedCat.name}';
    });
  }

  Future<void> _handleSubmit() async {
    if (_imageBytes == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Harap ambil foto sampah terlebih dahulu'),
          backgroundColor: AppTheme.statusRejected,
        ),
      );
      return;
    }

    if (!_formKey.currentState!.validate()) return;
    if (_selectedCategoryId == null) return;

    setState(() {
      _isSubmitting = true;
    });

    final lat = _location?.latitude ?? LocationService.defaultLatitude;
    final lng = _location?.longitude ?? LocationService.defaultLongitude;

    try {
      final res = await widget.apiService.submitReport(
        imageBytes: _imageBytes!,
        filename: _imageName ?? 'evidence.jpg',
        title: _titleController.text.trim(),
        description: _descController.text.trim().isNotEmpty
            ? _descController.text.trim()
            : null,
        categoryId: _selectedCategoryId!,
        latitude: lat,
        longitude: lng,
        addressNote: _addressController.text.trim().isNotEmpty
            ? _addressController.text.trim()
            : null,
      );

      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });

        final reportData = res['data'];
        final reportId = reportData?['id']?.toString().substring(0, 8) ?? 'Tersimpan';

        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            title: const Row(
              children: [
                Icon(Icons.check_circle_rounded, color: AppTheme.primary, size: 28),
                SizedBox(width: 10),
                Text('Laporan Terkirim!'),
              ],
            ),
            content: Text(
              'Laporan Anda #$reportId telah masuk ke sistem antrean dinas kebersihan dan akan segera ditindaklanjuti oleh armada lapangan.',
              style: const TextStyle(fontSize: 14, height: 1.45),
            ),
            actions: [
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(120, 44),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  Navigator.pop(ctx);
                  widget.onReportCreated?.call();
                  Navigator.pop(context, true);
                },
                child: const Text('OK, Lihat Riwayat'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: AppTheme.statusRejected,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Form Laporan Sampah'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(18, 12, 18, 100), // Extra bottom padding for floating submit bar
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Photo Capture Section (Dashed Border when empty, 16dp rounded when filled)
              _buildPhotoCard(),
              const SizedBox(height: 16),

              // 2. AI Detection Banner (Progress bar + percentage badge)
              if (_isAnalyzingAI || _aiResult != null || _aiError != null)
                _buildAiResultCard(),
              const SizedBox(height: 16),

              // 3. Compact GPS Geotagging Card
              _buildGpsCard(),
              const SizedBox(height: 16),

              // 4. Form Fields
              _buildFormFields(),
            ],
          ),
        ),
      ),
      // 5. Floating Ergonomic Thumb-Friendly Bottom Button (Height 54dp)
      bottomNavigationBar: Container(
        padding: EdgeInsets.fromLTRB(
          18,
          12,
          18,
          MediaQuery.of(context).padding.bottom + 12,
        ),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              offset: const Offset(0, -4),
              blurRadius: 14,
            ),
          ],
        ),
        child: SizedBox(
          height: 52,
          child: ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primary,
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
            onPressed: _isSubmitting ? null : _handleSubmit,
            icon: _isSubmitting
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.send_rounded, size: 20),
            label: Text(
              _isSubmitting ? 'Mengirim Laporan...' : 'Kirim Laporan Sampah',
              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPhotoCard() {
    if (_imageBytes != null) {
      return Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.border, width: 1.2),
        ),
        clipBehavior: Clip.antiAlias,
        child: Stack(
          children: [
            Image.memory(
              _imageBytes!,
              height: 230,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
            Positioned(
              top: 10,
              right: 10,
              child: CircleAvatar(
                radius: 18,
                backgroundColor: Colors.black.withValues(alpha: 0.6),
                child: IconButton(
                  icon: const Icon(Icons.close_rounded, color: Colors.white, size: 18),
                  padding: EdgeInsets.zero,
                  onPressed: () {
                    setState(() {
                      _imageBytes = null;
                      _imageName = null;
                      _aiResult = null;
                      _aiError = null;
                    });
                  },
                ),
              ),
            ),
            Positioned(
              bottom: 10,
              right: 10,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.7),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle, color: Color(0xFF4ADE80), size: 14),
                    SizedBox(width: 5),
                    Text(
                      'Foto Terpilih',
                      style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      );
    }

    // Clean Dashed Border Camera Placeholder
    return DashedBorderContainer(
      radius: 16,
      strokeWidth: 1.5,
      color: AppTheme.primaryLight.withValues(alpha: 0.5),
      backgroundColor: const Color(0xFFF0FDF4), // Subtle Emerald 50 tint
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: const BoxDecoration(
                color: AppTheme.primaryContainer,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.photo_camera_rounded,
                size: 34,
                color: AppTheme.primaryDark,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Ambil Foto Bukti Sampah',
              style: TextStyle(
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
                fontSize: 15,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'AI MobileNetV2 akan mendeteksi otomatis kategori sampah',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primary,
                      foregroundColor: Colors.white,
                      minimumSize: const Size(0, 46),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.photo_camera, size: 18),
                    label: const Text('Buka Kamera', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      backgroundColor: Colors.white,
                      minimumSize: const Size(0, 46),
                      side: const BorderSide(color: AppTheme.border, width: 1.2),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library_outlined, size: 18, color: AppTheme.textPrimary),
                    label: const Text('Pilih Galeri', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textPrimary)),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAiResultCard() {
    if (_isAnalyzingAI) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: AppTheme.primaryContainer.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.primaryLight.withValues(alpha: 0.5)),
        ),
        child: const Row(
          children: [
            SizedBox(
              width: 22,
              height: 22,
              child: CircularProgressIndicator(
                strokeWidth: 2.2,
                color: AppTheme.primaryDark,
              ),
            ),
            SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'AI MobileNetV2 Memindai...',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.primaryDark,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Mengklasifikasikan jenis sampah secara real-time',
                    style: TextStyle(fontSize: 11, color: AppTheme.onPrimaryContainer),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    if (_aiError != null) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.statusPendingBg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.statusPendingBorder),
        ),
        child: Row(
          children: [
            const Icon(Icons.info_outline, color: AppTheme.statusPending, size: 20),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                'Info AI: $_aiError. Anda dapat memilih kategori secara manual.',
                style: const TextStyle(fontSize: 12, color: AppTheme.textPrimary),
              ),
            ),
          ],
        ),
      );
    }

    if (_aiResult != null) {
      final res = _aiResult!;
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFECFDF5), Color(0xFFF0FDF4)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.primaryLight, width: 1.5),
          boxShadow: [
            BoxShadow(
              color: AppTheme.primary.withValues(alpha: 0.08),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: AppTheme.primary,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.auto_awesome, color: Colors.white, size: 16),
                ),
                const SizedBox(width: 8),
                const Text(
                  'Deteksi AI MobileNetV2',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.onPrimaryContainer,
                  ),
                ),
                const Spacer(),
                // Highlighted Category & Confidence Badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: res.confidence >= 0.85
                        ? AppTheme.primary
                        : const Color(0xFFD97706),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    res.confidence >= 0.85
                        ? res.category.toUpperCase()
                        : '${res.category.toUpperCase()} (SARAN)',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                      fontSize: 11,
                      letterSpacing: 0.3,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Progress Bar & Percentage
            Row(
              children: [
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: res.confidence,
                      minHeight: 10,
                      backgroundColor: Colors.white,
                      color: res.confidence >= 0.85
                          ? AppTheme.primary
                          : const Color(0xFFD97706),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  res.confidencePercentage,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: res.confidence >= 0.85
                        ? AppTheme.primaryDark
                        : const Color(0xFFB45309),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // 1-Tap Category Quick Chips
            const Row(
              children: [
                Icon(Icons.touch_app_rounded, size: 15, color: AppTheme.primaryDark),
                SizedBox(width: 6),
                Text(
                  'Koreksi Kategori (1-Ketuk jika AI meleset):',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: _categories.map((cat) {
                final isSelected = _selectedCategoryId == cat.id;
                return InkWell(
                  onTap: () => _onCategoryChanged(cat.id),
                  borderRadius: BorderRadius.circular(10),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                    decoration: BoxDecoration(
                      color: isSelected ? AppTheme.primary : Colors.white,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: isSelected ? AppTheme.primaryDark : const Color(0xFFCBD5E1),
                        width: isSelected ? 1.5 : 1.0,
                      ),
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: AppTheme.primary.withValues(alpha: 0.25),
                                blurRadius: 6,
                                offset: const Offset(0, 2),
                              )
                            ]
                          : null,
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (isSelected) ...[
                          const Icon(Icons.check_circle_rounded, size: 14, color: Colors.white),
                          const SizedBox(width: 5),
                        ],
                        Text(
                          cat.name,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                            color: isSelected ? Colors.white : AppTheme.textPrimary,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.7),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.primaryLight.withValues(alpha: 0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, size: 15, color: AppTheme.primaryDark),
                  SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'AI memberikan rekomendasi awal. Sentuh salah satu chip di atas untuk mengoreksi kategori seketika.',
                      style: TextStyle(
                        fontSize: 11,
                        color: AppTheme.textSecondary,
                        fontWeight: FontWeight.w500,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _buildGpsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: AppTheme.statusInProgressBg,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.location_on, color: AppTheme.statusInProgress, size: 18),
                ),
                const SizedBox(width: 10),
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Geotagging Lokasi GPS',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    Text(
                      'Koordinat bukti laporan lapangan',
                      style: TextStyle(fontSize: 11, color: AppTheme.textTertiary),
                    ),
                  ],
                ),
                const Spacer(),
                if (_isLoadingGps)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.statusInProgress),
                  )
                else
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      minimumSize: const Size(0, 36),
                      side: const BorderSide(color: AppTheme.border),
                    ),
                    onPressed: _fetchGpsLocation,
                    icon: const Icon(Icons.refresh, size: 15, color: AppTheme.textPrimary),
                    label: const Text('Refresh', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            if (_location != null) ...[
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceMuted,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Lat: ${_location!.latitude.toStringAsFixed(6)} | Lng: ${_location!.longitude.toStringAsFixed(6)}',
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textPrimary,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: _location!.isSimulated ? AppTheme.statusPendingBg : AppTheme.statusCompletedBg,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        _location!.isSimulated ? 'Simulasi' : 'Akurat',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          color: _location!.isSimulated ? AppTheme.statusPending : AppTheme.statusCompleted,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              if (_location!.address != null) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.primaryLight.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.place_rounded, size: 15, color: AppTheme.primaryDark),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          _location!.address!,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.textPrimary,
                            height: 1.3,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              if (_location!.isSimulated)
                Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(
                    _location!.errorMessage ?? 'Mode default koordinat Jakarta Pusat',
                    style: const TextStyle(fontSize: 11, color: AppTheme.statusPending),
                  ),
                ),
            ] else
              const Text(
                'Sedang mengunci sinyal GPS...',
                style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildFormFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Judul Laporan
        TextFormField(
          controller: _titleController,
          decoration: const InputDecoration(
            labelText: 'Judul Laporan *',
            hintText: 'Contoh: Tumpukan Sampah Plastik Liar',
            prefixIcon: Icon(Icons.title, color: AppTheme.textSecondary),
          ),
          validator: (val) {
            if (val == null || val.trim().isEmpty) {
              return 'Judul laporan wajib diisi';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Kategori Sampah
        DropdownButtonFormField<int>(
          key: ValueKey(_selectedCategoryId),
          initialValue: _selectedCategoryId,
          decoration: const InputDecoration(
            labelText: 'Kategori Sampah *',
            prefixIcon: Icon(Icons.category_outlined, color: AppTheme.textSecondary),
          ),
          items: _categories.map((c) {
            return DropdownMenuItem<int>(
              value: c.id,
              child: Text(c.name, style: const TextStyle(fontWeight: FontWeight.w600)),
            );
          }).toList(),
          onChanged: _onCategoryChanged,
          validator: (val) => val == null ? 'Pilih kategori sampah' : null,
        ),
        const SizedBox(height: 16),

        // Catatan Alamat / Patokan
        TextFormField(
          controller: _addressController,
          decoration: const InputDecoration(
            labelText: 'Patokan Alamat (Opsional)',
            hintText: 'Contoh: Samping pos satpam RT 04, Jl. Merpati',
            prefixIcon: Icon(Icons.map_outlined, color: AppTheme.textSecondary),
          ),
        ),
        const SizedBox(height: 16),

        // Deskripsi Tambahan
        TextFormField(
          controller: _descController,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: 'Keterangan Lapangan (Opsional)',
            hintText: 'Jelaskan kondisi tumpukan, aroma bau, atau potensi sumbatan selokan...',
            prefixIcon: Padding(
              padding: EdgeInsets.only(bottom: 40),
              child: Icon(Icons.notes_rounded, color: AppTheme.textSecondary),
            ),
          ),
        ),
      ],
    );
  }
}
