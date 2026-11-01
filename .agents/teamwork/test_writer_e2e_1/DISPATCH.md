# Dispatch: E2E Test Suite Writer (Dual Track)

## Objective
Author the opaque-box, requirement-driven E2E test suite for Day 1 according to `TEST_INFRA.md` and `PROJECT.md`. Implement the test cases across Tiers 1-4 and the standalone test runner `tests/e2e_runner.py`. Once the test suite is fully authored and self-tested, publish `TEST_READY.md`.

## Working Directory
`D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_e2e_1`

## Inputs
- `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\TEST_INFRA.md`

## File Ownership
- Exclusively owns: `D:\Ngoding\interviewWeb\BillcodeTech\tests/**` and `D:\Ngoding\interviewWeb\BillcodeTech\TEST_READY.md`.
- Read-only on all other directories.

## Instructions
1. Read `ORIGINAL_REQUEST.md`, `PROJECT.md`, and `TEST_INFRA.md`.
2. Implement `tests/e2e_runner.py` and modular test suites under `tests/`:
   - Tier 1: Feature Coverage (Directory structure existence, dataset folder existence, model weight file format, image counts >= 50/class, citation file existence).
   - Tier 2: Boundary & Corner Cases (Dataset 80/20 train/val ratio balance, classification report precision/recall/F1 >= 0.75, overall test accuracy >= 80%, confusion matrix shape 3x3, corrupted/empty file detection).
   - Tier 3: Cross-Feature Interactions (PyTorch model loading into MobileNetV2 architecture, inference on sample image returns expected dictionary keys per API contract).
   - Tier 4: Real-World Scenarios (End-to-end execution of `predict.py` on real images from each class, metrics verification).
3. Ensure `python tests/e2e_runner.py` can be executed cleanly. The runner should report passing tests cleanly and clearly indicate what fails when files have not yet been produced.
4. When the test suite is authored, write `TEST_READY.md` at project root `D:\Ngoding\interviewWeb\BillcodeTech\TEST_READY.md` using the template from `TEST_INFRA.md`.
5. Write your report to `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_e2e_1\handoff.md` and send a message to orchestrator (`2fb3c008-4b2b-4b9e-88d9-91a9473b651c`).

## 2026-11-01T12:22:20Z
You are teamwork_test_writer_1.
Working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_e2e_1
Read D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md and the dispatch instructions at D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_e2e_1\DISPATCH.md.
Also read D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md and D:\Ngoding\interviewWeb\BillcodeTech\TEST_INFRA.md.
Implement the Day 1 opaque-box test suite across Tiers 1-4 and test runner tests/e2e_runner.py.
Publish TEST_READY.md when complete.
Write your completion handoff to D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_e2e_1\handoff.md.
When finished, send a message to orchestrator (conversation ID: 2fb3c008-4b2b-4b9e-88d9-91a9473b651c) with a summary.
