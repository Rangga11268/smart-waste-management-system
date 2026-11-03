import 'package:flutter_test/flutter_test.dart';
import 'package:swms_mobile/theme/app_theme.dart';

void main() {
  group('AppTheme Tests', () {
    test('returns correct semantic color for each status string', () {
      expect(AppTheme.getStatusColor('Pending'), AppTheme.statusPending);
      expect(AppTheme.getStatusColor('PENDING'), AppTheme.statusPending);
      expect(AppTheme.getStatusColor('In Progress'), AppTheme.statusInProgress);
      expect(AppTheme.getStatusColor('IN_PROGRESS'), AppTheme.statusInProgress);
      expect(AppTheme.getStatusColor('Completed'), AppTheme.statusCompleted);
      expect(AppTheme.getStatusColor('Rejected'), AppTheme.statusRejected);
    });

    test('returns correct background tint for status chips', () {
      expect(AppTheme.getStatusBgColor('Pending'), AppTheme.statusPendingBg);
      expect(AppTheme.getStatusBgColor('In Progress'), AppTheme.statusInProgressBg);
      expect(AppTheme.getStatusBgColor('Completed'), AppTheme.statusCompletedBg);
      expect(AppTheme.getStatusBgColor('Rejected'), AppTheme.statusRejectedBg);
    });

    test('formats relative time accurately', () {
      final now = DateTime.now();
      expect(AppTheme.formatRelativeTime(now), 'Baru saja');
      expect(
        AppTheme.formatRelativeTime(now.subtract(const Duration(minutes: 10))),
        '10 menit lalu',
      );
      expect(
        AppTheme.formatRelativeTime(now.subtract(const Duration(hours: 3))),
        '3 jam lalu',
      );
    });
  });
}
