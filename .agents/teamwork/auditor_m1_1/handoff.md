# Forensic Audit Report: Milestone 1 (Database Core, Models, Seeding & Alembic Migrations)

**Auditor**: `auditor_m1_1`  
**Milestone**: M1 (Database Core, Relational Models, Seeding & Alembic Migrations)  
**Profile**: General Project (Integrity Mode: `development` per `ORIGINAL_REQUEST.md`)  
**Verdict**: **`CLEAN`**  

---

## 1. Observation

### 1.1 Source Code Forensic Analysis
1. **Database Core Engine & Fallback (`backend/app/core/database.py`)**:
   - Lines 52–65: Attempts real TCP connection to PostgreSQL via SQLAlchemy `create_engine` with `connect_timeout=2` and executes `conn.execute(text("SELECT 1"))`.
   - Lines 65–74: Catches real `Exception` (e.g., `psycopg2.OperationalError`), cleans up connection pool via `temp_engine.dispose()`, logs a warning, and falls back to `configure_sqlite_engine(fallback)`.
   - Lines 20–35: Configures SQLite with `connect_args={"check_same_thread": False}` and attaches an event listener on `"connect"` executing `cursor.execute("PRAGMA foreign_keys=ON;")`.
   - Lines 81–87: `get_db()` generator provides real `SessionLocal()` sessions with a guaranteed `finally: db.close()` cleanup.
   - Observation: No hardcoded flags, mocks, or facade engines exist.

2. **Database Seeding & Hashing Authenticity (`backend/app/core/seed.py`)**:
   - Lines 59–63: `hash_password(password: str)` generates unique random salts via `salt = bcrypt.gensalt()` and computes hashes with native `bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")`.
   - Lines 65–73: `verify_password()` computes authentic password checks via `bcrypt.checkpw()`.
   - Lines 81–118: `seed_database()` queries `Category` by `slug` and `User` by `email` before inserting, ensuring genuine idempotency.
   - Observation: No static precomputed hash strings or password bypasses exist.

3. **Relational Models (`backend/app/models/`)**:
   - `User` (`backend/app/models/user.py`): UUID primary key (`sa.Uuid(as_uuid=True)`), unique indexed email, check constraint `sa.CheckConstraint("role IN ('admin', 'user')", name="check_user_role")`, and cascade relationship `cascade="all, delete-orphan"` to `waste_reports`.
   - `Category` (`backend/app/models/category.py`): Integer autoincrement primary key, unique slug, name, badge_color, and back-reference relationship to `waste_reports`.
   - `WasteReport` (`backend/app/models/report.py`): UUID primary key, foreign keys to `users.id` (ON DELETE CASCADE) and `categories.id` (ON DELETE RESTRICT), status check constraint `status IN ('Pending', 'In Progress', 'Completed', 'Rejected')`, compound desc index `idx_reports_created_at_desc`, and cascade relationship to `report_logs`.
   - `ReportLog` (`backend/app/models/log.py`): UUID primary key, foreign key to `waste_reports.id` (ON DELETE CASCADE) and `users.id` (ON DELETE SET NULL).
   - Observation: Complete SQLAlchemy 2.0 DeclarativeBase models with genuine constraints and relations.

4. **Alembic Migrations (`backend/alembic/`)**:
   - `backend/alembic/env.py` (lines 40, 56): Configured with `render_as_batch=True` to support SQLite table schema migrations.
   - `backend/alembic/versions/6a3d4361fa05_create_initial_swms_tables.py`: Complete initial migration DDL for `categories`, `users`, `waste_reports`, and `report_logs` with batch alter table operations.

### 1.2 Direct Binary SQLite3 Verification
Direct queries on `D:\Ngoding\interviewWeb\swms_dev.db`:
- **Binary Header Check**:
  ```python
  with open("swms_dev.db", "rb") as f:
      header = f.read(16)
  assert header == b"SQLite format 3\x00"
  ```
  Result: Binary header matches verbatim `b'SQLite format 3\x00'`.
- **Table Discovery (`sqlite_master`)**:
  ```python
  tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
  ```
  Result: `['users', 'categories', 'waste_reports', 'report_logs']`. All 4 required ERD tables exist.
- **Seeded Master Records**:
  - `categories`: 3 records present (`organic`, `plastic`, `paper`) with respective badge colors (`#16a34a`, `#0284c7`, `#d97706`).
  - `users`: 2 records present:
    - Admin: `admin@bilcode.id` | Hash: `$2b$12$VwsXqAQ2mU1hq/pGaLONJuJMhxQHC7184xtbgMnLs/XPmszQAuoom`
    - User: `user@bilcode.id` | Hash: `$2b$12$hKTlNLFxmjSUj7h2G8dcHuQnNsDoFaR6iOd1wnmWvkYqSfIlindia`
  - Password Verification:
    - `bcrypt.checkpw(b"Admin123!", admin_hash.encode())` -> `True`
    - `bcrypt.checkpw(b"WrongPass", admin_hash.encode())` -> `False`
    - `bcrypt.checkpw(b"User123!", user_hash.encode())` -> `True`
    - `bcrypt.checkpw(b"WrongPass", user_hash.encode())` -> `False`

### 1.3 Git History and Test Integrity Inspection
- `git diff tests/`: Completely empty (0 modified lines). No test fixtures, assertions, or runners were altered or monkey-patched.
- Pre-populated artifacts: Search for pre-existing log files (`*.log`, `*result*`, `*output*`) returned 0 artifacts.

### 1.4 Independent Test Suite Execution
1. **`python backend/verify_m1.py`**:
   - Check 1: PostgreSQL probe timed out safely and fell back to SQLite -> `PASS`
   - Check 2: All 4 tables (users, categories, waste_reports, report_logs) exist with valid schema -> `PASS`
   - Check 3: Seeding is 100% idempotent; 3 categories and 2 users created -> `PASS`
   - Check 4: Native bcrypt hashing and verification succeeded for all accounts -> `PASS`
   - Check 5: SQLite PRAGMA foreign_keys=ON active and cascade delete functions correctly -> `PASS`
   - Output: `ALL 5 CHECKS PASSED (100% SUCCESS)!`
2. **`pytest tests/test_day2_db_fallback.py -v`**:
   - Result: `15 passed in 8.94s` (100% pass rate).
3. **`pytest tests/test_tier1_structure.py tests/test_tier2_validation.py`**:
   - Result: `75 passed in 8.24s` (zero Day 1 regressions).
4. **`alembic current`**:
   - Output: `6a3d4361fa05 (head)` (database schema is at latest Alembic revision).

### 1.5 Adversarial Review & Stress Testing
- **Test 1 (Role Check Constraint)**: Inserting user with role `'superhero'` failed with `IntegrityError` (`PASS`).
- **Test 2 (Category Slug Uniqueness)**: Inserting duplicate slug `'dup'` failed with `IntegrityError` (`PASS`).
- **Test 3 (Status Check Constraint)**: Inserting report with status `'BlahBlah'` failed with `IntegrityError` (`PASS`).
- **Test 4 (Complex/Unicode Passwords)**: Hashing and verifying complex unicode password `'P@sswørd—🚀—123!_éàç'` succeeded without errors (`PASS`).

---

## 2. Logic Chain

1. **Anti-Cheating & Integrity Verification**:
   - Observation 1.1 reveals that `database.py` performs authentic TCP connection attempts and error catches using standard SQLAlchemy and `psycopg2`, while `seed.py` dynamically invokes `bcrypt.gensalt()` and `bcrypt.hashpw()`.
   - Observation 1.2 confirms through direct inspection of `swms_dev.db` that the database is a valid SQLite3 binary file with distinct bcrypt salts on the seeded records, and passwords verify authentically with standard bcrypt routines.
   - Observation 1.3 shows that no test assertions or fixtures were tampered with in `tests/`.
   - Inference: The implementation is 100% authentic with zero shortcuts, mock facade bypasses, or hardcoded strings.

2. **Requirements R1 & R2 Compliance**:
   - R1 (Backend Architecture & Database Connectivity) demands PostgreSQL connectivity with automatic local SQLite fallback. Observation 1.1 and 1.4 confirm this behavior is active, tested, and operational.
   - R2 (Relational Models & Seeding) demands models conforming to `docs/ERD.md` and default seed data for categories and users. Observation 1.1, 1.2, and 1.5 demonstrate full schema compliance, constraint enforcement, and idempotent seeding.

3. **Verdict Determination**:
   - All Phase 1 and Phase 2 checks pass under Development Mode criteria.
   - Zero integrity violations were found.
   - Conclusion: The work product is **CLEAN**.

---

## 3. Caveats

- **PostgreSQL Connectivity in Development**: The local environment runs without a live PostgreSQL Docker daemon, which intentionally exercises the automatic SQLite fallback mechanism specified in R1. When deployed to production, configuring `DATABASE_URL` will transparently connect to PostgreSQL.
- **SQLite Concurrency**: SQLite fallback uses `check_same_thread=False` and `StaticPool` (in-memory) or write-ahead logging in multi-threaded environments, which is fully sufficient for local development and test execution.

---

## 4. Conclusion

Milestone 1 satisfies all integrity criteria and technical specifications:
- **Verdict**: **`CLEAN`**
- All 4 ERD tables (`users`, `categories`, `waste_reports`, `report_logs`) exist with active foreign keys, indexes, and check constraints.
- Database fallback from unreachable PostgreSQL to local SQLite works reliably without hangs or mocks.
- Passwords for `admin@bilcode.id` and `user@bilcode.id` are hashed using native bcrypt with random salts and verify successfully.
- Alembic batch migration is applied at head revision `6a3d4361fa05`.
- 15/15 database fallback tests, 5/5 standalone verification checks, and 75/75 Day 1 regression tests pass with 0 failures.

---

## 5. Verification Method

To independently reproduce this forensic audit:

1. **Verify Binary SQLite3 Database & Tables**:
   ```powershell
   python -c "import sqlite3; c=sqlite3.connect('swms_dev.db'); print([r[0] for r in c.execute('SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()])"
   ```
   *Expected Output*: `['users', 'categories', 'waste_reports', 'report_logs']`

2. **Verify Password Hashes with Bcrypt**:
   ```powershell
   python -c "import sqlite3, bcrypt; c=sqlite3.connect('swms_dev.db'); h=c.execute('SELECT password_hash FROM users WHERE email=\'admin@bilcode.id\'').fetchone()[0]; print('Verified:', bcrypt.checkpw(b'Admin123!', h.encode()))"
   ```
   *Expected Output*: `Verified: True`

3. **Run Standalone M1 Verification Suite**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python backend/verify_m1.py
   ```
   *Expected Output*: `[SWMS M1 VERIFICATION] ALL 5 CHECKS PASSED (100% SUCCESS)!`

4. **Run Pytest Fallback & Schema Tests**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   pytest tests/test_day2_db_fallback.py -v
   ```
   *Expected Output*: `15 passed`
