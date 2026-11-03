import 'dart:convert';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

class LocationResult {
  final double latitude;
  final double longitude;
  final double accuracy;
  final bool isSimulated;
  final String? errorMessage;
  final String? address;

  LocationResult({
    required this.latitude,
    required this.longitude,
    this.accuracy = 0.0,
    this.isSimulated = false,
    this.errorMessage,
    this.address,
  });
}

class LocationService {
  // Default coordinates fallback: Jakarta center (Monas)
  static const double defaultLatitude = -6.175392;
  static const double defaultLongitude = 106.827153;

  /// Reverse geocode latitude and longitude to human-readable address via OSM Nominatim
  static Future<String?> reverseGeocode(double lat, double lon) async {
    try {
      final uri = Uri.parse(
        'https://nominatim.openstreetmap.org/reverse?format=json&lat=$lat&lon=$lon&zoom=18&addressdetails=1',
      );
      final response = await http.get(uri, headers: {
        'User-Agent': 'SWMS-Mobile/1.0 (bilcode-assessment)',
      }).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        final displayName = data['display_name'] as String?;
        return displayName;
      }
    } catch (_) {
      // Graceful degradation when offline or network fails
    }
    return null;
  }

  static Future<LocationResult> getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    try {
      serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        final addr = await reverseGeocode(defaultLatitude, defaultLongitude);
        return LocationResult(
          latitude: defaultLatitude,
          longitude: defaultLongitude,
          isSimulated: true,
          errorMessage: 'Layanan lokasi dinonaktifkan. Menggunakan koordinat default.',
          address: addr,
        );
      }

      permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          final addr = await reverseGeocode(defaultLatitude, defaultLongitude);
          return LocationResult(
            latitude: defaultLatitude,
            longitude: defaultLongitude,
            isSimulated: true,
            errorMessage: 'Izin lokasi ditolak. Menggunakan koordinat default.',
            address: addr,
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        final addr = await reverseGeocode(defaultLatitude, defaultLongitude);
        return LocationResult(
          latitude: defaultLatitude,
          longitude: defaultLongitude,
          isSimulated: true,
          errorMessage: 'Izin lokasi ditolak permanen. Menggunakan koordinat default.',
          address: addr,
        );
      }

      final position = await Geolocator.getCurrentPosition(
        timeLimit: const Duration(seconds: 10),
      );

      final addr = await reverseGeocode(position.latitude, position.longitude);

      return LocationResult(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        isSimulated: false,
        address: addr,
      );
    } catch (e) {
      final addr = await reverseGeocode(defaultLatitude, defaultLongitude);
      return LocationResult(
        latitude: defaultLatitude,
        longitude: defaultLongitude,
        isSimulated: true,
        errorMessage: 'Gagal mengambil GPS ($e). Menggunakan koordinat default.',
        address: addr,
      );
    }
  }
}
