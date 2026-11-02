## 2026-11-02T08:57:38Z
You are worker_m1, a teamwork_worker subagent.
Your working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m1\
Project root: D:\Ngoding\interviewWeb\BillcodeTech

MANDATORY FIRST STEP:
Read:
1. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md (Day 2 requirements R1, R2)
2. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\orchestrator_2\PROJECT.md
3. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day2\handoff.md
4. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_db_test\handoff.md
5. docs/ERD.md, docs/RUNBOOK.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Milestone Scope (M1: Database Core, Relational Models, Seeding & Alembic):
You exclusively own and will implement the following files in `backend/`:

1. `backend/app/core/config.py`:
   - Pydantic Settings class loading from `.env` or defaults:
     - `PROJECT_NAME`: "Smart Waste Management System API"
     - `VERSION`: "1.0.0"
     - `API_V1_STR`: "/api/v1"
     - `DATABASE_URL`: `postgresql+psycopg2://postgres:postgres@localhost:5432/swms_db`
     - `SQLITE_FALLBACK_URL`: `sqlite:///./swms_dev.db`
     - `JWT_SECRET`: default secure key (e.g. "bilcode-swms-super-secret-jwt-key-2026")
     - `ALGORITHM`: "HS256"
     - `ACCESS_TOKEN_EXPIRE_MINUTES`: 60 * 24 (1440 mins)
     - `UPLOAD_DIR`: "backend/uploads/reports"

2. `backend/app/core/database.py`:
   - Implement `create_app_engine()` with automatic SQLite fallback:
     - Check `DATABASE_URL`. If PostgreSQL or non-sqlite, attempt active TCP handshake probe with `connect_timeout=2` and `pool_pre_ping=True`.
     - If connection raises `OperationalError` or fails, log warning: `"Primary database connection failed. Falling back to local SQLite: ..."`, dispose failed engine, and return SQLite engine pointing to `SQLITE_FALLBACK_URL`.
     - SQLite engine MUST configure:
       - `connect_args={"check_same_thread": False}`
       - `@event.listens_for(engine, "connect")` executing `PRAGMA foreign_keys=ON;`
     - Declarative `Base = declarative_base()` (or `class Base(DeclarativeBase): pass` in SQLAlchemy 2.0).
     - `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
     - `get_db()` generator yielding `db` session and closing in `finally`.

3. Relational Models (`backend/app/models/`):
   - `backend/app/models/base.py`: Shared `Base`.
   - `backend/app/models/user.py`:
     - `User`: `id` (`sa.Uuid(as_uuid=True)`, pk, default `uuid.uuid4`), `email` (`sa.String(255)`, unique, not null, indexed), `password_hash` (`sa.String(255)`, not null), `full_name` (`sa.String(150)`, not null), `role` (`sa.String(20)`, not null, default `"user"`, indexed, check constraint in ('admin', 'user')), `phone_number` (`sa.String(30)`, nullable), `is_active` (`sa.Boolean`, default True), `created_at` (`sa.DateTime(timezone=True)`, server_default=func.now()), `updated_at` (`sa.DateTime(timezone=True)`, server_default=func.now(), onupdate=func.now()).
     - Relationship to `waste_reports` (`cascade="all, delete-orphan"`).
   - `backend/app/models/category.py`:
     - `Category`: `id` (`sa.Integer`, pk, autoincrement=True), `slug` (`sa.String(50)`, unique, not null), `name` (`sa.String(100)`, not null), `description` (`sa.Text`, nullable), `badge_color` (`sa.String(20)`, default="#059669"), `created_at` (`sa.DateTime(timezone=True)`, server_default=func.now()).
     - Relationship to `waste_reports`.
   - `backend/app/models/report.py`:
     - `WasteReport`: `id` (`sa.Uuid(as_uuid=True)`, pk, default `uuid.uuid4`), `user_id` (`sa.Uuid(as_uuid=True)`, ForeignKey("users.id", ondelete="CASCADE"), not null, indexed), `category_id` (`sa.Integer`, ForeignKey("categories.id", ondelete="RESTRICT"), not null, indexed), `title` (`sa.String(200)`, not null), `description` (`sa.Text`, nullable), `image_url` (`sa.String(500)`, not null), `detected_category` (`sa.String(100)`, nullable), `ai_confidence` (`sa.Float`, default=0.0), `latitude` (`sa.Float`, not null), `longitude` (`sa.Float`, not null), `address_note` (`sa.String(255)`, nullable), `status` (`sa.String(30)`, default="Pending", not null, indexed, check constraint in ('Pending', 'In Progress', 'Completed', 'Rejected')), `admin_notes` (`sa.Text`, nullable), `resolved_at` (`sa.DateTime(timezone=True)`, nullable), `created_at` (`sa.DateTime(timezone=True)`, server_default=func.now(), index=True), `updated_at` (`sa.DateTime(timezone=True)`, server_default=func.now(), onupdate=func.now()).
     - Relationships: `reporter` (`User`), `category` (`Category`), `logs` (`ReportLog`, `cascade="all, delete-orphan"`).
   - `backend/app/models/log.py`:
     - `ReportLog`: `id` (`sa.Uuid(as_uuid=True)`, pk, default `uuid.uuid4`), `report_id` (`sa.Uuid(as_uuid=True)`, ForeignKey("waste_reports.id", ondelete="CASCADE"), not null, indexed), `actor_id` (`sa.Uuid(as_uuid=True)`, ForeignKey("users.id", ondelete="SET NULL"), nullable), `previous_status` (`sa.String(30)`, nullable), `new_status` (`sa.String(30)`, not null), `remarks` (`sa.Text`, nullable), `created_at` (`sa.DateTime(timezone=True)`, server_default=func.now()).
     - Relationships: `report` (`WasteReport`), `actor` (`User`).
   - `backend/app/models/__init__.py`: Import all models (`User`, `Category`, `WasteReport`, `ReportLog`, `Base`) so they are exposed for Alembic metadata.

4. `backend/app/core/seed.py`:
   - Implement `seed_database(db: Session)`:
     - Initial categories:
       1. Organic Waste: `slug="organic"`, `name="Organic Waste"`, `description="Sisa makanan, dedaunan, sayuran, dan bahan mudah terurai"`, `badge_color="#16a34a"`
       2. Plastic Waste: `slug="plastic"`, `name="Plastic Waste"`, `description="Botol plastik, kantong kresek, kemasan sachet, sedotan"`, `badge_color="#0284c7"`
       3. Paper Waste: `slug="paper"`, `name="Paper Waste"`, `description="Kertas karton, kardus, koran bekas, dokumen kertas"`, `badge_color="#d97706"`
     - Default test credentials:
       1. Super Admin: `email="admin@bilcode.id"`, `password="Admin123!"`, `role="admin"`, `full_name="Super Admin"`, `phone_number="081234567890"`
       2. Citizen: `email="user@bilcode.id"`, `password="User123!"`, `role="user"`, `full_name="Warga Pelapor"`, `phone_number="08123456789"`
     - Password hashing MUST use native `bcrypt` (`bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')`) directly (do NOT use passlib due to Python 3.12 compatibility bug).
     - Must be completely idempotent (skip insert if category slug or user email already exists).

5. `backend/seed.py`:
   - Standalone CLI executable: initializes DB, seeds categories and users, prints status.

6. `backend/alembic/` & `backend/alembic.ini`:
   - Configure Alembic to use `backend.app.models.Base.metadata` and shared engine.
   - Configure `render_as_batch=True` in `env.py` for SQLite DDL compatibility.
   - Generate initial migration revision covering all 4 tables.

7. Update `backend/app/main.py`:
   - Add async `lifespan(app)` context manager:
     - Run `Base.metadata.create_all(bind=engine)`
     - With `SessionLocal()` as db: `seed_database(db)`
   - Ensure health routes (`/`, `/health`, `/api/v1/health`) return 200 OK.
