#!/usr/bin/env python3
"""E2E Test Runner for Smart Waste Management System (SWMS) - Day 3 Web Dashboard.

Executes the requirement-driven, opaque-box test suite across Tiers 1-4:
- Tier 1: Feature Coverage (>=5 tests per feature across 13 core features = 65 tests)
- Tier 2: Boundary & Corner Cases (14 tests)
- Tier 3: Cross-Feature Combinations (6 tests)
- Tier 4: Real-World Scenarios (3 tests)

Total: 88 Automated Tests

Usage:
    python tests/day3_web_runner.py [--tier 1|2|3|4] [-v|--verbose]
"""

import argparse
from pathlib import Path
import sys
import time
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEST_FILE = str(PROJECT_ROOT / "tests" / "test_day3_web_e2e.py")


class TierCollectorPlugin:
    """Pytest plugin to track granular execution per tier."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.records = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            test_name = report.nodeid.split("::")[-1]
            if report.passed:
                self.passed += 1
                self.records.append((test_name, "PASS", report.duration, ""))
            elif report.failed:
                self.failed += 1
                longrepr = str(report.longrepr)
                self.records.append((test_name, "FAIL", report.duration, longrepr.splitlines()[-1] if longrepr else ""))
            elif report.skipped:
                self.skipped += 1
                self.records.append((test_name, "SKIP", report.duration, ""))


def run_tier(tier_num: int, verbose: bool = False):
    """Run tests for a single tier using pytest keyword filter."""
    tier_info = {
        1: ("Tier 1: Feature Coverage", "TestTier1FeatureCoverage"),
        2: ("Tier 2: Boundary & Corner Cases", "TestTier2BoundaryCases"),
        3: ("Tier 3: Cross-Feature Combinations", "TestTier3CrossFeatureCombinations"),
        4: ("Tier 4: Real-World Scenarios", "TestTier4RealWorldScenarios"),
    }
    tier_name, class_filter = tier_info[tier_num]
    print(f"\n{'='*75}\n  RUNNING {tier_name.upper()}\n{'='*75}")

    collector = TierCollectorPlugin()
    args = [TEST_FILE, "-k", class_filter, "-q"]
    if verbose:
        args.append("-v")

    start_time = time.perf_counter()
    exit_code = pytest.main(args, plugins=[collector])
    elapsed = time.perf_counter() - start_time

    total = collector.passed + collector.failed + collector.skipped
    pass_rate = (collector.passed / total * 100) if total > 0 else 0.0

    print(f"\nResults for {tier_name}:")
    print(f"  Total Tests: {total} | Passed: {collector.passed} | Failed: {collector.failed} | Skipped: {collector.skipped}")
    print(f"  Pass Rate:   {pass_rate:.1f}% | Duration: {elapsed:.2f}s")

    if collector.failed > 0:
        print("\n  Failures in this Tier:")
        for name, status, duration, err_msg in collector.records:
            if status == "FAIL":
                print(f"    - [{status}] {name} ({duration:.2f}s): {err_msg}")

    return {
        "tier": tier_num,
        "name": tier_name,
        "total": total,
        "passed": collector.passed,
        "failed": collector.failed,
        "skipped": collector.skipped,
        "pass_rate": pass_rate,
        "elapsed": elapsed,
        "exit_code": exit_code,
    }


def main():
    parser = argparse.ArgumentParser(description="SWMS Day 3 Web Dashboard E2E Test Runner")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run a specific tier (1, 2, 3, or 4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose test execution details")
    args = parser.parse_args()

    tiers_to_run = [args.tier] if args.tier else [1, 2, 3, 4]

    print("\n" + "#" * 75)
    print("  SMART WASTE MANAGEMENT SYSTEM (SWMS) - DAY 3 WEB E2E TEST SUITE")
    print(f"  Project Root: {PROJECT_ROOT}")
    print(f"  Test File:    {TEST_FILE}")
    print("#" * 75)

    all_tier_results = []
    overall_start = time.perf_counter()

    for t in tiers_to_run:
        res = run_tier(t, verbose=args.verbose)
        all_tier_results.append(res)

    overall_elapsed = time.perf_counter() - overall_start

    # Summary table
    print("\n" + "=" * 75)
    print("                         FINAL TEST SUITE SUMMARY")
    print("=" * 75)
    header = f"{'Tier':<36} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Pass %':<8}"
    print(header)
    print("-" * len(header))

    grand_total = 0
    grand_passed = 0
    grand_failed = 0
    grand_skipped = 0

    for res in all_tier_results:
        grand_total += res["total"]
        grand_passed += res["passed"]
        grand_failed += res["failed"]
        grand_skipped += res["skipped"]
        row = f"{res['name']:<36} | {res['total']:<6} | {res['passed']:<6} | {res['failed']:<6} | {res['pass_rate']:.1f}%"
        print(row)

    print("-" * len(header))
    grand_pass_rate = (grand_passed / grand_total * 100) if grand_total > 0 else 0.0
    summary_row = f"{'OVERALL TOTALS':<36} | {grand_total:<6} | {grand_passed:<6} | {grand_failed:<6} | {grand_pass_rate:.1f}%"
    print(summary_row)
    print("=" * 75)
    print(f"Total Suite Execution Time: {overall_elapsed:.2f} seconds\n")

    if grand_failed == 0 and grand_total > 0:
        print(">>> ALL TESTS PASSED SUCCESSFULLY! Day 3 Web Dashboard criteria fully satisfied. <<<")
        return 0
    else:
        print(f">>> {grand_failed} test(s) failed. Please review error reports above. <<<")
        return 1


if __name__ == "__main__":
    sys.exit(main())
