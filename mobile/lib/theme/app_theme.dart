import 'package:flutter/material.dart';

class AppTheme {
  // Brand colors (Eco-Tech Emerald M3 Palette)
  static const Color primary = Color(0xFF059669);
  static const Color primaryDark = Color(0xFF047857);
  static const Color primaryLight = Color(0xFF10B981);
  static const Color primaryContainer = Color(0xFFD1FAE5);
  static const Color onPrimaryContainer = Color(0xFF065F46);

  // Surface & neutral colors (High contrast, anti-slop)
  static const Color background = Color(0xFFF8FAFC); // Slate 50
  static const Color surface = Colors.white;
  static const Color surfaceMuted = Color(0xFFF1F5F9); // Slate 100
  static const Color textPrimary = Color(0xFF0F172A); // Slate 900 (Contrast > 15:1)
  static const Color textSecondary = Color(0xFF475569); // Slate 600 (Contrast > 5.5:1, WCAG AA compliant)
  static const Color textTertiary = Color(0xFF94A3B8); // Slate 400
  static const Color border = Color(0xFFE2E8F0); // Slate 200
  static const Color borderActive = Color(0xFFCBD5E1); // Slate 300

  // Semantic Status Colors (Rigorous WCAG AA contrast against their light container backgrounds)
  // Pending: Amber
  static const Color statusPending = Color(0xFFB45309); // Amber 700
  static const Color statusPendingBg = Color(0xFFFEF3C7); // Amber 100
  static const Color statusPendingBorder = Color(0xFFFDE68A); // Amber 200

  // In Progress: Blue
  static const Color statusInProgress = Color(0xFF1D4ED8); // Blue 700
  static const Color statusInProgressBg = Color(0xFFDBEAFE); // Blue 100
  static const Color statusInProgressBorder = Color(0xFFBFDBFE); // Blue 200

  // Completed: Emerald
  static const Color statusCompleted = Color(0xFF047857); // Emerald 700
  static const Color statusCompletedBg = Color(0xFFD1FAE5); // Emerald 100
  static const Color statusCompletedBorder = Color(0xFFA7F3D0); // Emerald 200

  // Rejected: Rose
  static const Color statusRejected = Color(0xFFBE123C); // Rose 700
  static const Color statusRejectedBg = Color(0xFFFFE4E6); // Rose 100
  static const Color statusRejectedBorder = Color(0xFFFECDD3); // Rose 200

  static Color getStatusColor(String status) {
    switch (status.toUpperCase().replaceAll('_', ' ')) {
      case 'PENDING':
        return statusPending;
      case 'IN PROGRESS':
        return statusInProgress;
      case 'COMPLETED':
        return statusCompleted;
      case 'REJECTED':
        return statusRejected;
      default:
        return textSecondary;
    }
  }

  static Color getStatusBgColor(String status) {
    switch (status.toUpperCase().replaceAll('_', ' ')) {
      case 'PENDING':
        return statusPendingBg;
      case 'IN PROGRESS':
        return statusInProgressBg;
      case 'COMPLETED':
        return statusCompletedBg;
      case 'REJECTED':
        return statusRejectedBg;
      default:
        return surfaceMuted;
    }
  }

  static Color getStatusBorderColor(String status) {
    switch (status.toUpperCase().replaceAll('_', ' ')) {
      case 'PENDING':
        return statusPendingBorder;
      case 'IN PROGRESS':
        return statusInProgressBorder;
      case 'COMPLETED':
        return statusCompletedBorder;
      case 'REJECTED':
        return statusRejectedBorder;
      default:
        return border;
    }
  }

  /// Relative human-readable time formatter (e.g., "10 menit yang lalu")
  static String formatRelativeTime(DateTime dt) {
    final localDt = dt.isUtc ? dt.toLocal() : dt;
    final now = DateTime.now();
    final difference = now.difference(localDt);

    if (difference.isNegative || difference.inSeconds < 60) {
      return 'Baru saja';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} menit lalu';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} jam lalu';
    } else if (difference.inDays == 1) {
      return 'Kemarin';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} hari lalu';
    } else {
      return '${localDt.day}/${localDt.month}/${localDt.year}';
    }
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        onPrimary: Colors.white,
        primaryContainer: primaryContainer,
        onPrimaryContainer: onPrimaryContainer,
        surface: surface,
        surfaceContainerLowest: background,
        surfaceContainerLow: background,
        surfaceContainer: surfaceMuted,
        outline: border,
        outlineVariant: borderActive,
      ),
      scaffoldBackgroundColor: background,
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        foregroundColor: textPrimary,
        elevation: 0,
        scrolledUnderElevation: 1,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.3,
        ),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: border, width: 1),
        ),
        margin: EdgeInsets.zero,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: border, width: 1),
        ),
        titleTextStyle: const TextStyle(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w800,
          letterSpacing: -0.4,
        ),
        contentTextStyle: const TextStyle(
          color: textSecondary,
          fontSize: 14,
          height: 1.45,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: border, width: 1.2),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: border, width: 1.2),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: primary, width: 2.0),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: statusRejected, width: 1.2),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: statusRejected, width: 2.0),
        ),
        hintStyle: const TextStyle(color: textTertiary, fontSize: 14),
        labelStyle: const TextStyle(color: textSecondary, fontSize: 14, fontWeight: FontWeight.w500),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          elevation: 0,
          minimumSize: const Size(double.infinity, 52), // Ergonomic field target minimum 52dp
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          textStyle: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.2,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          side: const BorderSide(color: border, width: 1.2),
          minimumSize: const Size(0, 48),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        contentTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 14,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
