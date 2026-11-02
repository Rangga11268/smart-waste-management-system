## 2026-11-02T08:57:15Z
[Message] timestamp=2026-11-02T08:57:15Z sender=82c4b731-bdc8-49c5-a2ec-d29359fafec8 priority=MESSAGE_PRIORITY_HIGH content=You are test_writer_day2, a teamwork_test_writer subagent.
Your working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_day2\
Project root: D:\Ngoding\interviewWeb\BillcodeTech

MANDATORY FIRST STEP:
Read:
1. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md (Approved Task Prompt Day 2, R1-R7)
2. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\orchestrator_2\PROJECT.md
3. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day2\handoff.md
4. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_db_test\handoff.md
5. docs/API_SPECS.md, docs/ERD.md, docs/RUNBOOK.md, docs/FLOWS.md

Your scope:
As the E2E Testing Track author, you are responsible for designing and implementing the comprehensive requirement-driven, opaque-box test suite for Day 2 SWMS backend in `tests/`:

1. Design Methodology: 4-Tier Test Architecture:
   - Tier 1: Feature Coverage (>=5 test cases per feature covering happy paths in isolation)
     - Auth: Register, Login, Me (Admin & User)
     - Predict: Valid JPEG, PNG, WebP image classification, response structure & probabilities
     - Reports: Submit report with photo & GPS, List reports, Filter by status, Filter by category, Search keyword, Pagination
     - Status Update: Admin transition Pending -> In Progress, In Progress -> Completed, audit log record verification
     - Dashboard: Stats counts, status breakdown, category distribution, active users count
     - Categories: List master categories
     - Health: Root, /health, /api/v1/health
   - Tier 2: Boundary & Corner Cases (>=5 test cases per feature)
     - Auth: Duplicate email registration, invalid login password, nonexistent user, unauthenticated requests, malformed token
     - Predict: Unsupported extension (.txt, .pdf), corrupted image bytes, small/large dimensions, empty file
     - Reports: Invalid latitude (>90 or <-90), invalid longitude (>180 or <-180), non-existent category_id (e.g. 999), empty search result, page out of bounds, report not found UUID
     - Status Update: Non-admin citizen user attempting status update (403 Forbidden), invalid transition (Pending -> Completed directly), transition from completed/rejected (terminal states)
     - Dashboard: Non-admin citizen attempting stats (403 Forbidden), empty database stats handling (0 division prevention)
     - Database: Automatic SQLite fallback probe
   - Tier 3: Cross-Feature Combinations (Pairwise coverage)
     - Register citizen -> Login -> Submit report with photo -> Admin logs in -> Admin updates status -> Audit logs verified -> Dashboard stats reflects updated counts
     - Report submission triggers AI inference and saves detected_category + ai_confidence
     - User cannot update report status (403) but can view their own and public reports
   - Tier 4: Real-World Application Scenarios
     - Complete workflow per docs/RUNBOOK.md evaluation scenario: Super Admin login, Warga Pelapor login, multi-report submissions with real coordinates in Jakarta/Bandung, status lifecycle progression to Completed with admin notes.

2. Files to write in `tests/`:
   - `tests/conftest.py`:
     - Test engine with `sqlite:///:memory:` (or test db) and `StaticPool`
     - SQLite foreign keys enabled event listener (`PRAGMA foreign_keys=ON;`)
     - Fixtures: `test_engine`, `db_session`, `client` (FastAPI TestClient with `get_db` dependency override), `seed_data` (populates 3 categories and 2 seed users), `admin_headers`, `user_headers`, `dummy_image_bytes` (valid JPEG using Pillow), `corrupt_image_bytes`.
   - `tests/test_day2_auth.py`
   - `tests/test_day2_predict.py`
   - `tests/test_day2_reports.py`
   - `tests/test_day2_dashboard.py`
   - `tests/test_day2_db_fallback.py`
   - Also ensure existing Day 1 tests (`tests/test_tier1_structure.py` through `test_tier5_adversarial_empirical.py`) remain completely untouched and compatible.

3. Coordination Artifacts:
   - Create `TEST_INFRA.md` at `D:\Ngoding\interviewWeb\BillcodeTech\TEST_INFRA.md` describing philosophy, tiers, and inventory.
   - Create `TEST_READY.md` at `D:\Ngoding\interviewWeb\BillcodeTech\TEST_READY.md` listing runner command, coverage table, and feature checklist.

Write your report to `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\test_writer_day2\handoff.md`.
Follow Handoff Protocol. Send message to caller when complete.
