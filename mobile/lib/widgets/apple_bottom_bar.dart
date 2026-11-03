import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class AppleBottomBarItem {
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const AppleBottomBarItem({
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}

class AppleBottomBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;
  final List<AppleBottomBarItem> items;

  const AppleBottomBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final bottomPadding = MediaQuery.paddingOf(context).bottom;

    return ClipRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          decoration: const BoxDecoration(
            color: Color(0xEBFFFFFF),
            border: Border(
              top: BorderSide(
                color: Color(0xFFE2E8F0),
                width: 0.8,
              ),
            ),
          ),
          padding: EdgeInsets.only(
            bottom: bottomPadding > 0 ? bottomPadding : 8,
            top: 8,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(items.length, (index) {
              final item = items[index];
              final isSelected = currentIndex == index;
              final color = isSelected ? AppTheme.primary : const Color(0xFF94A3B8);

              return Expanded(
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => onTap(index),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        isSelected ? item.activeIcon : item.icon,
                        size: 24,
                        color: color,
                      ),
                      const SizedBox(height: 3),
                      Text(
                        item.label,
                        style: TextStyle(
                          fontSize: 10.5,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                          color: color,
                          letterSpacing: -0.2,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}
