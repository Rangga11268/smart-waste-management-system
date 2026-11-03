import 'package:flutter/material.dart';

/// A reusable shimmering skeleton box for loading states
class SkeletonBox extends StatefulWidget {
  final double? width;
  final double height;
  final double borderRadius;
  final EdgeInsetsGeometry? margin;

  const SkeletonBox({
    super.key,
    this.width,
    required this.height,
    this.borderRadius = 8,
    this.margin,
  });

  @override
  State<SkeletonBox> createState() => _SkeletonBoxState();
}

class _SkeletonBoxState extends State<SkeletonBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final val = _controller.value;
        return Container(
          width: widget.width,
          height: widget.height,
          margin: widget.margin,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            gradient: LinearGradient(
              begin: Alignment(-1.5 + (val * 3), 0),
              end: Alignment(-0.5 + (val * 3), 0),
              colors: const [
                Color(0xFFE2E8F0),
                Color(0xFFF8FAFC),
                Color(0xFFE2E8F0),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Skeleton placeholder for Home Screen Feed
class HomeFeedSkeleton extends StatelessWidget {
  const HomeFeedSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        3,
        (index) => Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SkeletonBox(width: 80, height: 80, borderRadius: 12),
              SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        SkeletonBox(width: 70, height: 18, borderRadius: 6),
                        SkeletonBox(width: 50, height: 18, borderRadius: 10),
                      ],
                    ),
                    SizedBox(height: 8),
                    SkeletonBox(width: double.infinity, height: 16, borderRadius: 4),
                    SizedBox(height: 6),
                    SkeletonBox(width: 120, height: 14, borderRadius: 4),
                    SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        SkeletonBox(width: 90, height: 12, borderRadius: 4),
                        SkeletonBox(width: 60, height: 12, borderRadius: 4),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Skeleton placeholder for History Screen
class HistoryListSkeleton extends StatelessWidget {
  const HistoryListSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      itemCount: 4,
      itemBuilder: (context, index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SkeletonBox(width: 84, height: 84, borderRadius: 12),
              SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        SkeletonBox(width: 80, height: 20, borderRadius: 6),
                        SkeletonBox(width: 65, height: 20, borderRadius: 12),
                      ],
                    ),
                    SizedBox(height: 8),
                    SkeletonBox(width: double.infinity, height: 16, borderRadius: 4),
                    SizedBox(height: 6),
                    SkeletonBox(width: 140, height: 12, borderRadius: 4),
                    SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        SkeletonBox(width: 100, height: 12, borderRadius: 4),
                        SkeletonBox(width: 50, height: 12, borderRadius: 4),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// Skeleton placeholder for Report Detail Screen
class ReportDetailSkeleton extends StatelessWidget {
  const ReportDetailSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return const SingleChildScrollView(
      padding: EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SkeletonBox(width: double.infinity, height: 240, borderRadius: 20),
          SizedBox(height: 18),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SkeletonBox(width: 100, height: 24, borderRadius: 8),
              SkeletonBox(width: 80, height: 24, borderRadius: 12),
            ],
          ),
          SizedBox(height: 12),
          SkeletonBox(width: double.infinity, height: 28, borderRadius: 6),
          SizedBox(height: 8),
          SkeletonBox(width: 160, height: 16, borderRadius: 4),
          SizedBox(height: 20),
          SkeletonBox(width: double.infinity, height: 80, borderRadius: 16),
          SizedBox(height: 16),
          SkeletonBox(width: double.infinity, height: 100, borderRadius: 16),
          SizedBox(height: 16),
          SkeletonBox(width: double.infinity, height: 120, borderRadius: 16),
        ],
      ),
    );
  }
}
