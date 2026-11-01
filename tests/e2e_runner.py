#!/usr/bin/env python3
"""
E2E Test Runner for Smart Waste Management System (SWMS) - Day 1.

Executes the requirement-driven, opaque-box test suite across Tiers 1-4:
- Tier 1: Feature Coverage (Directory structure, dataset files, model export)
- Tier 2: Boundary & Corner Cases (80/20 balance, thresholds, decodability)
- Tier 3: Cross-Feature Interactions (ImageFolder compatibility, model loading, contract)
- Tier 4: Real-World Scenarios (End-to-end inference, aspect ratios, metrics audit)

Usage:
    python tests/e2e_runner.py [--tier 1|2|3|4] [--verbose]
"""

import argparse
import os
from pathlib import Path
import sys
import time
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class DetailedTestResult(unittest.TestResult):
    """Custom TestResult collecting granular status and diagnostics."""

    def __init__(self, verbosity=1):
        super().__init__()
        self.verbosity = verbosity
        self.test_records = []  # list of (test_name, doc, status, err_msg, duration)
        self._start_time = None

    def startTest(self, test):
        super().startTest(test)
        self._start_time = time.perf_counter()

    def addSuccess(self, test):
        super().addSuccess(test)
        duration = time.perf_counter() - self._start_time
        doc = (test.shortDescription() or "").strip()
        self.test_records.append((test.id().split(".")[-1], doc, "PASS", "", duration))
        if self.verbosity > 1:
            print(f"  [PASS] {test.id().split('.')[-1]} - {doc} ({duration:.3f}s)")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        duration = time.perf_counter() - self._start_time
        doc = (test.shortDescription() or "").strip()
        msg = self._exc_info_to_string(err, test).splitlines()[-1]
        self.test_records.append((test.id().split(".")[-1], doc, "FAIL", msg, duration))
        if self.verbosity > 1:
            print(f"  [FAIL] {test.id().split('.')[-1]} - {doc} ({duration:.3f}s)\n         -> {msg}")

    def addError(self, test, err):
        super().addError(test, err)
        duration = time.perf_counter() - self._start_time
        doc = (test.shortDescription() or "").strip()
        msg = self._exc_info_to_string(err, test).splitlines()[-1]
        self.test_records.append((test.id().split(".")[-1], doc, "ERROR", msg, duration))
        if self.verbosity > 1:
            print(f"  [ERROR] {test.id().split('.')[-1]} - {doc} ({duration:.3f}s)\n         -> {msg}")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        duration = time.perf_counter() - self._start_time
        doc = (test.shortDescription() or "").strip()
        self.test_records.append((test.id().split(".")[-1], doc, "SKIP", reason, duration))
        if self.verbosity > 1:
            print(f"  [SKIP] {test.id().split('.')[-1]} - {doc} (Reason: {reason})")


def run_tier(tier_num: int, suite: unittest.TestSuite, verbosity: int = 1):
    """Execute a single tier test suite and return stats dictionary."""
    tier_names = {
        1: "Tier 1: Feature Coverage",
        2: "Tier 2: Boundary & Corner Cases",
        3: "Tier 3: Cross-Feature Interactions",
        4: "Tier 4: Real-World Scenarios",
    }
    tier_title = tier_names.get(tier_num, f"Tier {tier_num}")
    print(f"\n{'='*75}\n  RUNNING {tier_title.upper()}\n{'='*75}")

    runner_result = DetailedTestResult(verbosity=verbosity)
    start = time.perf_counter()
    suite.run(runner_result)
    elapsed = time.perf_counter() - start

    total = runner_result.testsRun
    passed = len([r for r in runner_result.test_records if r[2] == "PASS"])
    failed = len([r for r in runner_result.test_records if r[2] == "FAIL"])
    errors = len([r for r in runner_result.test_records if r[2] == "ERROR"])
    skipped = len([r for r in runner_result.test_records if r[2] == "SKIP"])
    pass_rate = (passed / total * 100) if total > 0 else 0.0

    print(f"\nResults for {tier_title}:")
    print(f"  Total Tests: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors} | Skipped: {skipped}")
    print(f"  Pass Rate:   {pass_rate:.1f}% | Duration: {elapsed:.2f}s")

    if (failed + errors) > 0:
        print("\n  Failures / Missing Artifacts in this Tier:")
        for name, doc, status, err_msg, _ in runner_result.test_records:
            if status in ("FAIL", "ERROR"):
                print(f"    - [{status}] {name}: {err_msg}")

    return {
        "tier": tier_num,
        "name": tier_title,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": pass_rate,
        "elapsed": elapsed,
        "records": runner_result.test_records,
    }


def main():
    parser = argparse.ArgumentParser(description="SWMS Day 1 Opaque-Box E2E Test Runner")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Execute only a specific tier (1, 2, 3, or 4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose test execution details")
    args = parser.parse_args()

    verbosity = 2 if args.verbose else 1

    # Import test cases dynamically
    from tests.test_tier1_structure import TestTier1FeatureCoverage
    from tests.test_tier2_validation import TestTier2BoundaryValidation
    from tests.test_tier3_interaction import TestTier3CrossFeatureInteractions
    from tests.test_tier4_scenarios import TestTier4RealWorldScenarios

    loader = unittest.TestLoader()
    suites = {
        1: loader.loadTestsFromTestCase(TestTier1FeatureCoverage),
        2: loader.loadTestsFromTestCase(TestTier2BoundaryValidation),
        3: loader.loadTestsFromTestCase(TestTier3CrossFeatureInteractions),
        4: loader.loadTestsFromTestCase(TestTier4RealWorldScenarios),
    }

    tiers_to_run = [args.tier] if args.tier else [1, 2, 3, 4]

    print("\n" + "#"*75)
    print("  SMART WASTE MANAGEMENT SYSTEM (SWMS) - DAY 1 E2E TEST SUITE")
    print(f"  Project Root: {PROJECT_ROOT}")
    print("#"*75)

    all_tier_results = []
    overall_start = time.perf_counter()

    for t in tiers_to_run:
        res = run_tier(t, suites[t], verbosity=verbosity)
        all_tier_results.append(res)

    overall_elapsed = time.perf_counter() - overall_start

    # Print summary table
    print("\n" + "="*75)
    print("                         FINAL TEST SUITE SUMMARY")
    print("="*75)
    header = f"{'Tier':<35} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Pass %':<8}"
    print(header)
    print("-" * len(header))

    grand_total = 0
    grand_passed = 0
    grand_failed = 0
    grand_errors = 0
    grand_skipped = 0

    for res in all_tier_results:
        grand_total += res["total"]
        grand_passed += res["passed"]
        grand_failed += res["failed"] + res["errors"]
        grand_skipped += res["skipped"]
        row = f"{res['name']:<35} | {res['total']:<6} | {res['passed']:<6} | {res['failed'] + res['errors']:<6} | {res['pass_rate']:.1f}%"
        print(row)

    print("-" * len(header))
    grand_pass_rate = (grand_passed / grand_total * 100) if grand_total > 0 else 0.0
    summary_row = f"{'OVERALL TOTALS':<35} | {grand_total:<6} | {grand_passed:<6} | {grand_failed:<6} | {grand_pass_rate:.1f}%"
    print(summary_row)
    print("="*75)
    print(f"Total Suite Execution Time: {overall_elapsed:.2f} seconds\n")

    if grand_failed == 0 and grand_total > 0:
        print(">>> ALL TESTS PASSED SUCCESSFULLY! Model & deliverables satisfy Day 1 criteria. <<<")
        return 0
    else:
        print(f">>> {grand_failed} test(s) failed or artifacts missing for incomplete implementation milestones. <<<")
        return 1


if __name__ == "__main__":
    sys.exit(main())
