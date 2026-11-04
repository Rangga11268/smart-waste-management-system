import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class BackendStatusPill extends StatelessWidget {
  final bool isConnected;
  final VoidCallback? onTap;

  const BackendStatusPill({
    super.key,
    this.isConnected = true,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final statusColor = isConnected ? AppTheme.primary : AppTheme.statusPending;
    final text = isConnected ? 'Sistem Aktif' : 'Menghubungkan';

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.02),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: statusColor,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 5),
            Text(
              text,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
                letterSpacing: -0.2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
