import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../models/category.dart';
import '../../models/prediction_result.dart';
import '../../services/api_service.dart';
import '../../services/location_service.dart';
import '../../theme/app_theme.dart';

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
            title: const Row(
              children: [
                Icon(Icons.check_circle, color: AppTheme.primary, size: 28),
                SizedBox(width: 8),
                Text('Laporan Berhasil'),
              ],
            ),
            content: Text(
              'Laporan Anda #$reportId telah berhasil dikirim ke sistem. Petugas kebersihan akan segera menindaklanjuti lokasi ini.',
            ),
            actions: [
              TextButton(
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
        title: const Text('Laporkan Sampah'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Photo Capture Section
              _buildPhotoCard(),
              const SizedBox(height: 16),

              // 2. AI Classification Result
              if (_isAnalyzingAI || _aiResult != null || _aiError != null)
                _buildAiResultCard(),
              const SizedBox(height: 16),

              // 3. GPS Geotagging Card
              _buildGpsCard(),
              const SizedBox(height: 16),

              // 4. Form Fields
              _buildFormFields(),
              const SizedBox(height: 24),

              // Submit Action
              ElevatedButton.icon(
                onPressed: _isSubmitting ? null : _handleSubmit,
                icon: _isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.send_rounded),
                label: Text(
                  _isSubmitting ? 'Mengirim Laporan...' : 'Kirim Laporan Sampah',
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPhotoCard() {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          if (_imageBytes != null)
            Stack(
              children: [
                Image.memory(
                  _imageBytes!,
                  height: 220,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
                Positioned(
                  top: 8,
                  right: 8,
                  child: CircleAvatar(
                    backgroundColor: Colors.black54,
                    child: IconButton(
                      icon: const Icon(Icons.close, color: Colors.white, size: 20),
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
              ],
            )
          else
            Container(
              height: 180,
              color: AppTheme.background,
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.camera_alt_outlined, size: 52, color: AppTheme.primary),
                    SizedBox(height: 8),
                    Text(
                      'Ambil foto bukti sampah',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimary,
                        fontSize: 15,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'AI akan mengenali jenis sampah secara otomatis',
                      style: TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.photo_camera, size: 18),
                    label: const Text('Kamera', style: TextStyle(fontSize: 13)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library_outlined, size: 18),
                    label: const Text('Galeri', style: TextStyle(fontSize: 13)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAiResultCard() {
    if (_isAnalyzingAI) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.primaryContainer.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
        ),
        child: const Row(
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primary),
            ),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                'AI MobileNetV2 sedang memindai citra sampah...',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.primaryDark,
                ),
              ),
            ),
          ],
        ),
      );
    }

    if (_aiError != null) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppTheme.statusPendingBg,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.statusPending.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            const Icon(Icons.info_outline, color: AppTheme.statusPending, size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                'Pemberitahuan AI: $_aiError. Anda dapat memilih kategori manual.',
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
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.primaryContainer.withValues(alpha: 0.6),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.primary),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.auto_awesome, color: AppTheme.primary, size: 20),
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
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppTheme.primary,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    res.category,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: res.confidence,
                      minHeight: 8,
                      backgroundColor: Colors.white,
                      color: AppTheme.primary,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  res.confidencePercentage,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.onPrimaryContainer,
                  ),
                ),
              ],
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
                const Icon(Icons.location_on, color: AppTheme.statusInProgress, size: 20),
                const SizedBox(width: 8),
                const Text(
                  'Geotagging Lokasi GPS',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const Spacer(),
                if (_isLoadingGps)
                  const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                else
                  IconButton(
                    icon: const Icon(Icons.refresh, size: 18),
                    tooltip: 'Perbarui Koordinat GPS',
                    visualDensity: VisualDensity.compact,
                    onPressed: _fetchGpsLocation,
                  ),
              ],
            ),
            const SizedBox(height: 6),
            if (_location != null) ...[
              Text(
                'Lat: ${_location!.latitude.toStringAsFixed(6)}, Lng: ${_location!.longitude.toStringAsFixed(6)}',
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimary,
                ),
              ),
              if (_location!.isSimulated)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    _location!.errorMessage ?? 'Mode simulasi / default Jakarta',
                    style: const TextStyle(fontSize: 11, color: AppTheme.statusPending),
                  ),
                ),
            ] else
              const Text(
                'Mencari sinyal GPS...',
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
            prefixIcon: Icon(Icons.title),
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
            prefixIcon: Icon(Icons.category_outlined),
          ),
          items: _categories.map((c) {
            return DropdownMenuItem<int>(
              value: c.id,
              child: Text(c.name),
            );
          }).toList(),
          onChanged: (val) {
            setState(() {
              _selectedCategoryId = val;
            });
          },
          validator: (val) => val == null ? 'Pilih kategori sampah' : null,
        ),
        const SizedBox(height: 16),

        // Catatan Alamat / Patokan
        TextFormField(
          controller: _addressController,
          decoration: const InputDecoration(
            labelText: 'Catatan Alamat / Patokan (Opsional)',
            hintText: 'Contoh: Samping pos satpam RT 04, Jl. Merpati',
            prefixIcon: Icon(Icons.map_outlined),
          ),
        ),
        const SizedBox(height: 16),

        // Deskripsi Tambahan
        TextFormField(
          controller: _descController,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: 'Keterangan Tambahan (Opsional)',
            hintText: 'Jelaskan kondisi tumpukan, aroma bau, atau potensi sumbatan selokan...',
            prefixIcon: Padding(
              padding: EdgeInsets.only(bottom: 40),
              child: Icon(Icons.notes_rounded),
            ),
          ),
        ),
      ],
    );
  }
}
