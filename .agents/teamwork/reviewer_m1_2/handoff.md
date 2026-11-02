# Milestone 1 Independent Review & Adversarial Audit Report

**Reviewer**: `reviewer_m1_2`  
**Milestone**: M1 (Database Core, Relational Models, Seeding & Alembic Migrations)  
**Target Artifact**: Codebase produced by `worker_m1`  
**Verdict**: **APPROVE**  
**Integrity Status**: PASS (Zero integrity violations)  

---

## 1. Observation

### 1.1 Direct Schema & Constraints Audit against `docs/ERD.md`
1. **`users` Table** (`backend/app/models/user.py:14-42`):
   - `id`: `sa.Column(sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)` matches UUID PK.
   - `email`: `sa.Column(sa.String(255), unique=True, nullable=False, index=True)` matches VARCHAR(255) UNIQUE NOT NULL.
   - `password_hash`: `sa.Column(sa.String(255), nullable=False)` matches VARCHAR(255) NOT NULL.
   - `full_name`: `sa.Column(sa.String(150), nullable=False)` matches VARCHAR(150) NOT NULL.
   - `role`: `sa.Column(sa.String(20), nullable=False, default="user", index=True)` with check constraint `sa.CheckConstraint("role IN ('admin', 'user')", name="check_user_role")`.
   - `phone_number`: `sa.Column(sa.String(30), nullable=True)`.
   - `is_active`: `sa.Column(sa.Boolean, default=True, nullable=False)`.
   - `created_at` / `updated_at`: `sa.DateTime(timezone=True)` with `server_default=func.now()`.
2. **`categories` Table** (`backend/app/models/category.py:13-30`):
   - `id`: `sa.Column(sa.Integer, primary_key=True, autoincrement=True)` matches SERIAL PK.
   - `slug`: `sa.Column(sa.String(50), unique=True, nullable=False)` matches VARCHAR(50) UNIQUE.
   - `name`: `sa.Column(sa.String(100), nullable=False)` matches VARCHAR(100) NOT NULL.
   - `description`: `sa.Column(sa.Text, nullable=True)`.
   - `badge_color`: `sa.Column(sa.String(20), default="#059669", nullable=False)`.
   - `created_at`: `sa.DateTime(timezone=True)` with `server_default=func.now()`.
3. **`waste_reports` Table** (`backend/app/models/report.py:14-78`):
   - `id`: UUID PK.
   - `user_id`: `sa.ForeignKey("users.id", ondelete="CASCADE")` (UUID FK CASCADE).
   - `category_id`: `sa.ForeignKey("categories.id", ondelete="RESTRICT")` (INT FK RESTRICT).
   - `title`: `sa.String(200)` NOT NULL.
   - `image_url`: `sa.String(500)` NOT NULL.
   - `latitude`, `longitude`: `sa.Float` NOT NULL (GPS coordinates).
   - `status`: `sa.String(30)` default 'Pending' with check constraint `status IN ('Pending', 'In Progress', 'Completed', 'Rejected')`.
   - `created_at` indexed descending: `sa.Index("idx_reports_created_at_desc", created_at.desc())`.
   - `logs` relationship ordered by `desc(ReportLog.created_at)`.
4. **`report_logs` Table** (`backend/app/models/log.py:14-43`):
   - `id`: UUID PK.
   - `report_id`: `sa.ForeignKey("waste_reports.id", ondelete="CASCADE")` (UUID FK CASCADE).
   - `actor_id`: `sa.ForeignKey("users.id", ondelete="SET NULL")` (UUID FK SET NULL, `nullable=True`).
   - `previous_status` (VARCHAR 30 NULLABLE), `new_status` (VARCHAR 30 NOT NULL), `remarks` (TEXT NULLABLE).
   - `created_at`: `sa.DateTime(timezone=True)` default `func.now()`.

### 1.2 Direct Seeding & Credentials Audit against `docs/RUNBOOK.md`
- Master categories defined in `backend/app/core/seed.py:17-39`:
  - `organic`: `"Organic Waste"`, color `"#16a34a"`.
  - `plastic`: `"Plastic Waste"`, color `"#0284c7"`.
  - `paper`: `"Paper Waste"`, color `"#d97706"`.
- Default test accounts defined in `backend/app/core/seed.py:41-56`:
  - Super Admin: `"admin@bilcode.id"` / `"Admin123!"` (`role="admin"`, `full_name="Super Admin"`).
  - Warga Pelapor: `"user@bilcode.id"` / `"User123!"` (`role="user"`, `full_name="Warga Pelapor"`).
- Password hashing in `backend/app/core/seed.py:59-73`:
  - Uses native Python `bcrypt` (`bcrypt.hashpw` / `bcrypt.checkpw`) without deprecated `passlib` dependencies, ensuring 100% Python 3.12 compatibility.
- Idempotency in `backend/app/core/seed.py:76-118`:
  - Checks existence via `filter_by(slug=cat_data["slug"])` and `filter_by(email=user_data["email"])`.
  - Multiple executions add 0 new records and produce 0 errors.

### 1.3 Direct Execution and Independent Test Suite Results
1. **Milestone 1 Verification Script** (`python backend/verify_m1.py`):
   ```text
   ==================================================================
    [SWMS M1 VERIFICATION] Running Milestone 1 Validation Checks
   ==================================================================
   [Check 1/5] Verifying PostgreSQL probe & SQLite automatic fallback...
    -> PASS: PostgreSQL probe timed out safely and fell back to SQLite.
   [Check 2/5] Verifying all 4 ERD tables and schema structure...
    -> PASS: All 4 tables (users, categories, waste_reports, report_logs) exist with valid schema.
   [Check 3/5] Verifying seeding counts and idempotency...
    -> PASS: Seeding is 100% idempotent; 3 categories and 2 users created.
   [Check 4/5] Verifying native bcrypt password hashing & verification...
    -> PASS: Native bcrypt hashing and verification succeeded for all accounts.
   [Check 5/5] Verifying SQLite foreign keys (PRAGMA foreign_keys=ON) & cascade delete...
    -> PASS: SQLite PRAGMA foreign_keys=ON active and cascade delete functions correctly.
   ==================================================================
    [SWMS M1 VERIFICATION] ALL 5 CHECKS PASSED (100% SUCCESS)!
   ==================================================================
   ```
2. **Automated Database & Fallback Pytest Suite** (`pytest tests/test_day2_db_fallback.py -v`):
   - 15/15 tests passed cleanly in 9.29s (100% pass rate).
3. **Standalone Seeding CLI** (`python backend/seed.py`):
   - First run: seeded 3 categories, 2 users.
   - Second run: seeded 0 categories, 0 users; Status: `SUCCESS (Idempotent)`.
4. **Alembic Migration State** (`alembic current` in `backend/`):
   - Current revision: `6a3d4361fa05 (head)`.
5. **Day 1 Regression Check** (`pytest tests/test_tier1_structure.py tests/test_tier2_validation.py`):
   - 75/75 passed cleanly in 8.49s (0 regressions).
6. **FastAPI Lifespan and Health Endpoints** (`/`, `/health`, `/api/v1/health`):
   - Returned HTTP 200 OK with expected JSON payloads.

---

## 2. Logic Chain

1. **Schema & Referential Integrity**:
   - `docs/ERD.md` requires 4 tables with strict relations (`users`, `categories`, `waste_reports`, `report_logs`).
   - SQLite by default does not enforce foreign keys unless `PRAGMA foreign_keys=ON;` is executed per connection.
   - In `backend/app/core/database.py`, an `@event.listens_for(engine, "connect")` listener executes `PRAGMA foreign_keys=ON;` on every checkout.
   - We experimentally verified that violating foreign keys raises `IntegrityError`, deleting a `WasteReport` cascade-deletes associated `ReportLog` rows, deleting a `User` cascade-deletes associated `WasteReport` rows, deleting a `Category` referenced by a report raises `IntegrityError` (`ON DELETE RESTRICT`), and deleting an actor `User` sets `ReportLog.actor_id` to `NULL` while preserving the audit history.
2. **Check Constraint Enforcement**:
   - We stress-tested inserting invalid roles (e.g. `'hacker'`) and invalid statuses (e.g. `'InvalidStatus'`).
   - Both were rejected by the SQLite database engine with `sqlalchemy.exc.IntegrityError: CHECK constraint failed`.
3. **Database Fallback Resilience**:
   - In `backend/app/core/database.py`, `create_app_engine()` configures a 2-second connection timeout (`connect_args={"connect_timeout": 2}`) for PostgreSQL.
   - If PostgreSQL is offline, `create_engine` raises `OperationalError`, the temporary engine is safely disposed of (`temp_engine.dispose()`), and the local SQLite engine is activated transparently.
4. **Python 3.12 Native Bcrypt Security**:
   - Deprecated `passlib` causes `AttributeError` on Python 3.12 with modern bcrypt versions.
   - The implementation uses native `bcrypt.hashpw` and `bcrypt.checkpw`, generating valid `$2b$` salted hashes. We verified that valid credentials (`Admin123!`, `User123!`) authenticate successfully while incorrect credentials fail.
5. **Zero Integrity Violations**:
   - Audited codebase for hardcoded outputs, fake mocks, bypassed logic, or fabricated logs.
   - All models, seed routines, migrations, and checks are fully implemented with real database calls and verified live.

---

## 3. Caveats

- **SQLite Database Path Relative Resolution**:
  - `SQLITE_FALLBACK_URL: str = "sqlite:///./swms_dev.db"` resolves `./swms_dev.db` relative to the current working directory of the invoking process.
  - If a script is executed from `backend/`, it touches `backend/swms_dev.db`; if executed from project root, it touches `BillcodeTech/swms_dev.db`.
  - Both databases are properly migrated/seeded via application lifespan or CLI, but evaluators should consistently run commands from the project root (`D:\Ngoding\interviewWeb\BillcodeTech`) as documented in `docs/RUNBOOK.md`.
- **Production PostgreSQL Switch**:
  - In production, when `DATABASE_URL` points to a reachable PostgreSQL instance, `create_app_engine()` connects to PostgreSQL directly without falling back to SQLite.

---

## 4. Conclusion

**Verdict: APPROVE**

Milestone 1 satisfies all functional, architectural, and security requirements:
- Schema, column types, UUIDs, indexes, check constraints, and foreign key cascades match `docs/ERD.md` 100%.
- Initial master categories and default credentials strictly adhere to `docs/RUNBOOK.md` and seed idempotently.
- PostgreSQL probe with graceful SQLite fallback functions reliably with zero hang.
- Alembic batch migration `6a3d4361fa05` is clean and up-to-date.
- All 15 unit/integration tests in `tests/test_day2_db_fallback.py` and 5 checks in `backend/verify_m1.py` pass with 0 failures.
- No integrity violations or shortcuts detected.

Worker `worker_m1` is cleared to proceed, or downstream milestones (M3 Auth, M4 ML Inference, M5 Reports CRUD) may build directly on this foundation.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Schema & Fallback Suite**:
   ```powershell
   Set-Location D:\Ngoding\interviewWeb\BillcodeTech
   pytest tests/test_day2_db_fallback.py -v
   ```
   *Expected*: `15 passed in ~9-15s`.

2. **Verify Milestone 1 Checks**:
   ```powershell
   Set-Location D:\Ngoding\interviewWeb\BillcodeTech
   python backend/verify_m1.py
   ```
   *Expected*: `ALL 5 CHECKS PASSED (100% SUCCESS)!`.

3. **Verify Database Seeding & Idempotency**:
   ```powershell
   Set-Location D:\Ngoding\interviewWeb\BillcodeTech
   python backend/seed.py
   ```
   *Expected*: `Status: SUCCESS (Idempotent)`.

4. **Verify Alembic Migration Current Head**:
   ```powershell
   Set-Location D:\Ngoding\interviewWeb\BillcodeTech\backend
   alembic current
   ```
   *Expected*: `6a3d4361fa05 (head)`.
