# Challenger Report: Database Fallback, Alembic Batch Migrations & Schema Stress Testing

**Challenger**: `challenger_m1_2` (Empirical Challenger)  
**Milestone**: M1 (Database Core, Relational Models, Seeding & Alembic Migrations)  
**Date**: 2026-11-02  
**Verdict**: **APPROVE**  

---

## 1. Observation

All adversarial challenges were empirically executed against the implementation in `D:\Ngoding\interviewWeb\BillcodeTech` using dedicated stress harnesses and test suites.

### 1.1 Database Fallback Adversarial Probe
Tested `create_app_engine(database_url=..., fallback_url=...)` across 11 adversarial and malformed inputs:
1. **Non-existent host**: `postgresql+psycopg2://postgres:postgres@invalid.host.domain.test:5432/swms_db`
   - Caught: `OperationalError: (psycopg2.OperationalError) could not translate host name "invalid.host.domain.test" to address: Name or service not known`
   - Result: Cleanly logged fallback warning and initialized functioning SQLite engine in 0.03s.
2. **Invalid port out-of-range**: `postgresql+psycopg2://postgres:postgres@localhost:999999/swms_db`
   - Caught: `OperationalError: (psycopg2.OperationalError) invalid port number: "999999"`
   - Result: Fell back to local SQLite without unhandled crash.
3. **Invalid negative port**: `postgresql+psycopg2://postgres:postgres@localhost:-1/swms_db`
   - Caught: `OperationalError: (psycopg2.OperationalError) invalid port number: "-1"`
   - Result: Fell back to local SQLite without unhandled crash.
4. **Non-numeric port**: `postgresql+psycopg2://postgres:postgres@localhost:abc/swms_db`
   - Caught: `ValueError: invalid literal for int() with base 10: 'abc'`
   - Result: Fell back to local SQLite without unhandled crash.
5. **Unreachable IP timeout bound**: `postgresql+psycopg2://postgres:postgres@192.0.2.1:5432/swms_db` (RFC 5737 TEST-NET-1)
   - Caught: `OperationalError: (psycopg2.OperationalError) connection to server at "192.0.2.1", port 5432 failed: timeout expired`
   - Elapsed Time: **2.01s** (strictly bounded by `connect_timeout=2` in `backend/app/core/database.py:55`).
   - Result: Prevented infinite thread blocking and fell back to local SQLite cleanly.
6. **Malformed connection strings**:
   - `"not_a_valid_url"`: Caught `ArgumentError: Could not parse SQLAlchemy URL from given URL string`.
   - `"postgresql://"`: Caught `OperationalError`, fell back cleanly.
   - `"postgresql+psycopg2://"`: Caught `OperationalError`, fell back cleanly.
   - `"unknown+dialect://user:pass@host:5432/db"`: Caught `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:unknown.dialect`.
   - `""` and `None`: Fell back to default `SQLITE_FALLBACK_URL`.
7. **Functional CRUD on Fallback Engine**:
   - Created tables via `Base.metadata.create_all()`, inserted records into `categories`, and queried back with 100% data integrity.

### 1.2 Alembic Batch Migration Validation
Tested full migration lifecycle using CLI in `backend/`:
- **`python -m alembic current`**: Verified starting head `6a3d4361fa05 (head)`.
- **`python -m alembic downgrade -1`**:
  ```text
  INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
  INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
  INFO  [alembic.runtime.migration] Running downgrade 6a3d4361fa05 -> , create_initial_swms_tables
  ```
  - Exit code: **0**.
  - Verified tables `users`, `categories`, `waste_reports`, and `report_logs` were cleanly dropped.
- **`python -m alembic upgrade head`**:
  ```text
  INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
  INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
  INFO  [alembic.runtime.migration] Running upgrade  -> 6a3d4361fa05, create_initial_swms_tables
  ```
  - Exit code: **0**.
  - Verified all 4 tables and their indexes were cleanly recreated without syntax errors.
- **Batch mode directives**:
  - `backend/alembic/env.py:55` defines `render_as_batch=True`.
  - `backend/alembic/versions/6a3d4361fa05_create_initial_swms_tables.py` uses `with op.batch_alter_table('users', ...)` and `with op.batch_alter_table('waste_reports', ...)` for index and constraint management, ensuring full SQLite DDL compatibility.

### 1.3 Schema Boundary Limits & Constraint Enforcement
1. **Status CHECK Constraint**:
   - Table `waste_reports` (`backend/app/models/report.py:62`):
     `sa.CheckConstraint("status IN ('Pending', 'In Progress', 'Completed', 'Rejected')", name="check_report_status")`
   - Inserting `"InvalidStatus"`, `"PendingApproval"`, `"UNKNOWN"`, `"in progress"`, or `""`:
     `sqlite3.IntegrityError: CHECK constraint failed: check_report_status` raised and caught.
   - Inserting all 4 valid statuses (`Pending`, `In Progress`, `Completed`, `Rejected`): Succeeded.
2. **User Role CHECK Constraint**:
   - Table `users` (`backend/app/models/user.py:30`):
     `sa.CheckConstraint("role IN ('admin', 'user')", name="check_user_role")`
   - Inserting `"superadmin"`, `"moderator"`, `"guest"`, `""`, or `"ADMIN"`:
     `sqlite3.IntegrityError: CHECK constraint failed: check_user_role` raised and caught.
3. **GPS Float Precision (8+ Decimals)**:
   - Stored: `latitude = -6.20876345`, `longitude = 106.84559812` (8 decimal places, ~1.1mm resolution).
   - Retrieved: `latitude = -6.20876345`, `longitude = 106.84559812`.
   - Measured drift: `abs(stored - retrieved) = 0.0` (zero drift / no floating-point truncation).
   - Boundary coordinates tested: `(-90.0, -180.0)`, `(90.0, 180.0)`, `(0.0, 0.0)`, and 12-decimal coordinates (`-6.208763456789, 106.845598123456`) all retained exact equality.
4. **VARCHAR Exact Boundary Limits**:
   - `User.email` at exactly 255 chars: Successfully inserted and retrieved without truncation.
   - `WasteReport.title` at exactly 200 chars: Successfully inserted and retrieved without truncation.
   - `WasteReport.address_note` at exactly 255 chars: Successfully inserted and retrieved without truncation.
5. **Referential Integrity & Cascading Rules**:
   - Deleting a `Category` with associated reports failed with `IntegrityError` due to `ON DELETE RESTRICT` (`backend/app/models/report.py:28`).
   - Deleting a `User` with associated reports and logs cascaded cleanly due to `ON DELETE CASCADE` (`backend/app/models/user.py:37`).
   - Inserting duplicate `User.email` or `Category.slug` raised `IntegrityError` (UNIQUE constraints).

### 1.4 Automated Test Suite Execution
- **`pytest tests/test_day2_m1_adversarial.py -v`**:
  ```text
  ============================= 24 passed in 19.71s =============================
  ```
- **Combined Test Run (`pytest tests/test_day2_db_fallback.py tests/test_day2_m1_adversarial.py`)**:
  ```text
  ============================= 39 passed in 27.27s =============================
  ```
- **Standalone Verification (`python backend/verify_m1.py`)**:
  ```text
  [SWMS M1 VERIFICATION] ALL 5 CHECKS PASSED (100% SUCCESS)!
  ```
- **Day 1 Regression Check (`pytest tests/test_tier1_structure.py tests/test_tier2_validation.py`)**:
  ```text
  ============================= 75 passed in 6.25s ==============================
  ```

---

## 2. Logic Chain

1. **Fallback Robustness**:
   - `create_app_engine()` in `backend/app/core/database.py` wraps the primary database connection probe in a try/except catching all `Exception` types.
   - For PostgreSQL URIs, `connect_args["connect_timeout"] = 2` is injected. When pointing to non-existent hosts, invalid ports, unreachable IPs, or corrupt URLs, the driver throws `OperationalError`, `ValueError`, or `ArgumentError`.
   - The handler cleanly disposes of any incomplete engine pool and returns `configure_sqlite_engine(fallback)`, ensuring that the application will never crash or hang indefinitely on startup due to missing external databases.
2. **Alembic Reversibility & SQLite Batch Compatibility**:
   - SQLite does not support standard ALTER TABLE operations for adding/dropping constraints and certain index modifications.
   - Configuring `render_as_batch=True` causes Alembic to recreate tables behind the scenes (`batch_alter_table`).
   - Because `6a3d4361fa05_create_initial_swms_tables.py` wraps users, reports, and logs in batch operations, downgrade and upgrade executed without SQL syntax errors or orphaned locks.
3. **Schema Constraint Verification**:
   - Attaching `@event.listens_for(engine, "connect")` executing `PRAGMA foreign_keys=ON;` enforces referential integrity on SQLite.
   - Both table-level CHECK constraints (`check_report_status` and `check_user_role`) are properly embedded in the DDL and enforced by the engine on every INSERT/UPDATE.
   - Standard 64-bit IEEE 754 float representation in SQLite REAL and Python float natively preserves 8 decimal places (which requires ~27 bits of precision, well within 53-bit mantissa limits).

---

## 3. Caveats

1. **SQLite VARCHAR Length Enforcement**: SQLite uses dynamic typing type affinity (`TEXT` for `VARCHAR(N)`). The database engine does not reject strings longer than N characters unless a CHECK constraint or STRICT table is defined. String length limits must be enforced at the API schema layer using Pydantic (to be verified in M2/M3).
2. **Relative Database Path in Local Runs**: `SQLITE_FALLBACK_URL = "sqlite:///./swms_dev.db"` creates `swms_dev.db` relative to the current working directory of the process. Running commands from subdirectories (`backend/` vs project root) creates separate local database files if not invoked with an absolute path or matching CWD.

---

## 4. Conclusion

**Verdict**: **APPROVE**

Milestone 1 satisfies all requirements (R1, R2) with zero empirical failures:
- The database fallback mechanism is resilient against non-existent hosts, invalid ports, network drops, and malformed connection strings with bounded 2-second timeout.
- Alembic batch migrations support full upgrade and downgrade cycles with 0 errors.
- Database CHECK constraints, foreign key cascades, unique indexes, and 8-decimal GPS precision operate correctly.
- All 39 database test cases and 75 Day 1 regression test cases pass cleanly.

---

## 5. Verification Method

To independently reproduce this verification:

1. **Run Full Adversarial & Fallback Pytest Suite**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python -m pytest tests/test_day2_db_fallback.py tests/test_day2_m1_adversarial.py -v
   ```
   *Expected Output*: `39 passed in ~27s` with 0 failures.

2. **Verify Alembic CLI Migration Cycle**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech\backend
   python -m alembic downgrade -1
   python -m alembic upgrade head
   python -m alembic current
   ```
   *Expected Output*: Displays revision `6a3d4361fa05 (head)` with exit code 0.

3. **Verify Standalone Milestone 1 Script**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python backend/verify_m1.py
   ```
   *Expected Output*: `[SWMS M1 VERIFICATION] ALL 5 CHECKS PASSED (100% SUCCESS)!`
