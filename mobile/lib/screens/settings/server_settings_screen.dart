import 'package:flutter/material.dart';
import '../../config/app_config.dart';
import '../../theme/app_theme.dart';

class ServerSettingsScreen extends StatefulWidget {
  const ServerSettingsScreen({super.key});

  @override
  State<ServerSettingsScreen> createState() => _ServerSettingsScreenState();
}

class _ServerSettingsScreenState extends State<ServerSettingsScreen> {
  late final TextEditingController _urlController;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: AppConfig.baseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _saveUrl(String url) async {
    await AppConfig.setBaseUrl(url);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Alamat server berhasil diperbarui'),
          backgroundColor: AppTheme.primary,
        ),
      );
      Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Konfigurasi Server API'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Server Endpoint URL',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Tentukan alamat backend FastAPI yang akan diakses oleh aplikasi mobile ini.',
              style: TextStyle(fontSize: 14, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'Base URL API',
                hintText: 'http://10.0.2.2:8000/api/v1',
                prefixIcon: Icon(Icons.dns_outlined, color: AppTheme.primary),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _saveUrl(_urlController.text),
                icon: const Icon(Icons.check),
                label: const Text('Simpan Perubahan'),
              ),
            ),
            const SizedBox(height: 32),
            const Text(
              'Pilihan Preset URL Cepat:',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 12),
            _buildPresetTile(
              title: 'Android Emulator (Default)',
              subtitle: 'http://10.0.2.2:8000/api/v1',
              url: 'http://10.0.2.2:8000/api/v1',
            ),
            const SizedBox(height: 8),
            _buildPresetTile(
              title: 'Localhost / Windows Desktop',
              subtitle: 'http://127.0.0.1:8000/api/v1',
              url: 'http://127.0.0.1:8000/api/v1',
            ),
            const SizedBox(height: 8),
            _buildPresetTile(
              title: 'Perangkat Fisik (IP LAN)',
              subtitle: 'Contoh: http://192.168.1.10:8000/api/v1',
              url: 'http://192.168.1.10:8000/api/v1',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPresetTile({
    required String title,
    required String subtitle,
    required String url,
  }) {
    return Card(
      child: ListTile(
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
        trailing: const Icon(Icons.arrow_forward_ios, size: 14),
        onTap: () {
          _urlController.text = url;
          _saveUrl(url);
        },
      ),
    );
  }
}
