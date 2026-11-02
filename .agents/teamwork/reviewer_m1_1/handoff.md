# Milestone 1 (M1) Quality & Adversarial Review Report

**Reviewer**: `reviewer_m1_1`  
**Roles**: Reviewer & Adversarial Critic  
**Reviewed Target**: Milestone 1 (Database Core, Relational Models, Seeding & Alembic Migrations) produced by `worker_m1`  
**Date**: 2026-11-02  
**Final Verdict**: **APPROVE**  

---

## 1. Observation

Direct code inspections, schema verifications, and execution commands yielded the following verified evidence:

### 1.1 Source Code Inspection
- `backend/app/core/config.py`: Correctly defines `Settings` using `pydantic_settings.BaseSettings` with `PROJECT_NAME`, `VERSION`, `API_V1_STR`, `DATABASE_URL` (defaulting to PostgreSQL `swms_db`), `SQLITE_FALLBACK_URL`, `JWT_SECRET`, `ALGORITHM` (HS256), `ACCESS_TOKEN_EXPIRE_MINUTES` (1440), and `UPLOAD_DIR`.
- `backend/app/core/database.py`: Implements `create_app_engine()` with active TCP probe (`connect_timeout=2`, `pool_pre_ping=True`) on PostgreSQL, catching `OperationalError` and gracefully falling back to SQLite (`configure_sqlite_engine()`). Sets `connect_args={"check_same_thread": False}` and hooks `@event.listens_for(engine, "connect")` executing `PRAGMA foreign_keys=ON;`.
- `backend/app/models/` (`base.py`, `user.py`, `category.py`, `report.py`, `log.py`):
  - Strictly adheres to SQLAlchemy 2.0 `DeclarativeBase` architecture.
  - Primary keys and foreign keys for UUIDs use `sa.Uuid(as_uuid=True)` with default `uuid.uuid4`.
  - Check constraints defined: `role IN ('admin', 'user')` on `users`, `status IN ('Pending', 'In Progress', 'Completed', 'Rejected')` on `waste_reports`.
  - Referential actions defined: `users.id` cascade delete on `waste_reports`, `waste_reports.id` cascade delete on `report_logs`, `categories.id` restrict delete, and `users.id` set null on `report_logs.actor_id`.
  - Indexes conform to `docs/ERD.md`: `idx_users_email`, `idx_users_role`, `idx_reports_user_id`, `idx_reports_category_id`, `idx_reports_status`, `idx_reports_created_at_desc`, `idx_logs_report_id`.
- `backend/app/core/seed.py`: Implements `seed_database()` using native `bcrypt` (`bcrypt.hashpw` with `bcrypt.gensalt()`, `bcrypt.checkpw`) without deprecated `passlib`. Correctly seeds 3 master categories (`organic`, `plastic`, `paper`) and 2 default accounts (`admin@bilcode.id` / `Admin123!` and `user@bilcode.id` / `User123!`) with 100% idempotency.
- `backend/seed.py`: Standalone CLI script successfully verifies tables and runs `seed_database()`.
- `backend/alembic/env.py`: Configured with `render_as_batch=True`, shared application engine, and `target_metadata = Base.metadata`.
- `backend/alembic/versions/6a3d4361fa05_create_initial_swms_tables.py`: Comprehensive initial migration creating all 4 tables, foreign keys, check constraints, and batch alterations.
- `backend/app/main.py`: Lifespan context manager ensures upload directory creation, table initialization, and idempotent database seeding. Health probes (`/`, `/health`, `/api/v1/health`) return HTTP 200 OK.

### 1.2 Verification Command Executions
1. `python backend/verify_m1.py`:
   - All 5 checks passed cleanly (PostgreSQL fallback probe, 4 ERD tables, seeding idempotency, native bcrypt verification, SQLite foreign keys & cascade delete).
2. `pytest tests/test_day2_db_fallback.py -v`:
   - 15 of 15 tests passed with 0 failures in 10.51s.
3. `alembic current`:
   - Confirmed current revision is `6a3d4361fa05 (head)`.
4. `pytest tests/test_tier1_structure.py tests/test_tier2_validation.py`:
   - 75 of 75 Day 1 tests passed with 0 regressions.
5. FastAPI TestClient probe on `app.main:app`:
   - `GET /` -> HTTP 200 `{'status': 'success', 'app': 'Smart Waste Management System API', 'version': '1.0.0', 'docs': '/docs'}`
   - `GET /health` -> HTTP 200 `{'status': 'healthy', 'service': 'backend', 'version': '1.0.0'}`
   - `GET /api/v1/health` -> HTTP 200 `{'status': 'healthy', 'service': 'backend', 'version': '1.0.0'}`
   - `GET /docs` -> HTTP 200 OK.

---

## 2. Logic Chain

1. **Integrity & Anti-Cheat Assessment**:
   - The code contains zero hardcoded test outputs, zero facade stubs, and no bypassed logic.
   - The fallback probe actively executes `SELECT 1` on PostgreSQL and catches connection refusal/timeout within 2 seconds.
   - The password hashing is genuine bcrypt with distinct random salts per execution.
   - Referential integrity and check constraints are genuinely enforced at the database level.

2. **Standards & Conformance**:
   - Conforms strictly to requirements R1 and R2 of `ORIGINAL_REQUEST.md` (Day 2).
   - Relational schema exactly matches `docs/ERD.md` SQL DDL specification.
   - Seed data exact match with credentials in `docs/RUNBOOK.md` (`admin@bilcode.id` / `Admin123!` and `user@bilcode.id` / `User123!`).

3. **Adversarial Stress-Testing**:
   - **Hypothesis 1 (Check Constraints on SQLite)**: Tested inserting an invalid role (`role='hacker'`). SQLite raised `IntegrityError` and aborted transaction. (PASS)
   - **Hypothesis 2 (Foreign Key Cascade on SQLite)**: Tested deleting a `WasteReport` with an attached `ReportLog`. Deleting the report cascaded to the log, leaving zero orphans. (PASS)
   - **Hypothesis 3 (UUID String Querying Pitfall)**: Tested querying with raw string ID `filter(User.id == str(u_id))` vs `filter(User.id == uuid.UUID(str(u_id)))`. Discovered that SQLAlchemy 2.0 with `sa.Uuid(as_uuid=True)` under SQLite crashes with `AttributeError: 'str' object has no attribute 'hex'` when passed a raw string. When coerced to `uuid.UUID`, queries succeed. (CRITICAL ADVISORY for M3 & M5).
   - **Hypothesis 4 (Working Directory Sensitivity)**: Discovered that `SQLITE_FALLBACK_URL: str = "sqlite:///./swms_dev.db"` resolves relative to current working directory (`D:\Ngoding\interviewWeb\BillcodeTech` vs `D:\Ngoding\interviewWeb\BillcodeTech\backend`). (MINOR ADVISORY).

---

## 3. Caveats & Advisories for Downstream Milestones

1. **CRITICAL ADVISORY for Milestone 3 (Auth) & Milestone 5 (Reports) — UUID Query Parameter Casting**:
   - **Symptom**: When querying models using `sa.Uuid(as_uuid=True)` on SQLite, executing `session.query(Model).filter(Model.id == param)` where `param` is a `str` (e.g. from JWT `sub` or URL path `/reports/{id}`) will raise `sqlalchemy.exc.StatementError: (builtins.AttributeError) 'str' object has no attribute 'hex'`.
   - **Requirement**: Downstream engineers implementing FastAPI route dependencies (`get_current_user`) and route handlers (`GET /reports/{id}`) MUST type-hint IDs as `uuid.UUID` or explicitly coerce string inputs with `uuid.UUID(id_str)` before passing them into SQLAlchemy queries.
2. **ADVISORY — SQLite Fallback Database File Path**:
   - Running scripts from different working directories creates separate `swms_dev.db` files. For production or consistent local execution, ensuring paths are anchored or setting `DATABASE_URL` prevents divergence.
3. **No PostgreSQL Instance Running Locally**:
   - Verified that the system operates seamlessly in offline SQLite fallback mode without external Docker/PostgreSQL containers.

---

## 4. Conclusion

**Verdict: APPROVE**

The work delivered for Milestone 1 by `worker_m1` meets and exceeds all quality, architectural, and security standards:
- Dual-database connectivity with 2s PostgreSQL TCP handshake timeout and automatic local SQLite fallback is robust and reliable.
- All 4 models (`User`, `Category`, `WasteReport`, `ReportLog`) precisely conform to `docs/ERD.md`.
- Seeding logic is 100% idempotent and uses native Python 3.12 bcrypt.
- Initial Alembic migration `6a3d4361fa05` is applied and verified.
- 100% test pass rate across 15 database fallback tests, 5 verification checks, and 75 Day 1 tests.
- Zero integrity violations detected.

---

## 5. Verification Method

To independently reproduce and verify this assessment:

1. **Milestone 1 Verification Script**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python backend/verify_m1.py
   ```
   *Expected*: `[SWMS M1 VERIFICATION] ALL 5 CHECKS PASSED (100% SUCCESS)!`

2. **Pytest Database Fallback & ERD Test Suite**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   pytest tests/test_day2_db_fallback.py -v
   ```
   *Expected*: `15 passed` with 0 failures.

3. **Check Alembic Migration State**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech\backend
   alembic current
   ```
   *Expected*: Displays `6a3d4361fa05 (head)`.

4. **Verify Lifespan & Health Endpoints via TestClient**:
   ```powershell
   python -c "from fastapi.testclient import TestClient; from backend.app.main import app; c = TestClient(app); print(c.get('/health').json())"
   ```
   *Expected*: `{'status': 'healthy', 'service': 'backend', 'version': '1.0.0'}`.
