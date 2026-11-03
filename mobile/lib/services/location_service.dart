import 'package:geolocator/geolocator.dart';

class LocationResult {
  final double latitude;
  final double longitude;
  final double accuracy;
  final bool isSimulated;
  final String? errorMessage;

  LocationResult({
    required this.latitude,
    required this.longitude,
    this.accuracy = 0.0,
    this.isSimulated = false,
    this.errorMessage,
  });
}

class LocationService {
  // Default coordinates fallback: Jakarta center (Monas)
  static const double defaultLatitude = -6.175392;
  static const double defaultLongitude = 106.827153;

  static Future<LocationResult> getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    try {
      serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return LocationResult(
          latitude: defaultLatitude,
          longitude: defaultLongitude,
          isSimulated: true,
          errorMessage: 'Layanan lokasi dinonaktifkan. Menggunakan koordinat default.',
        );
      }

      permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return LocationResult(
            latitude: defaultLatitude,
            longitude: defaultLongitude,
            isSimulated: true,
            errorMessage: 'Izin lokasi ditolak. Menggunakan koordinat default.',
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return LocationResult(
          latitude: defaultLatitude,
          longitude: defaultLongitude,
          isSimulated: true,
          errorMessage: 'Izin lokasi ditolak permanen. Menggunakan koordinat default.',
        );
      }

      final position = await Geolocator.getCurrentPosition(
        timeLimit: const Duration(seconds: 10),
      );

      return LocationResult(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        isSimulated: false,
      );
    } catch (e) {
      return LocationResult(
        latitude: defaultLatitude,
        longitude: defaultLongitude,
        isSimulated: true,
        errorMessage: 'Gagal mengambil GPS ($e). Menggunakan koordinat default.',
      );
    }
  }
}
