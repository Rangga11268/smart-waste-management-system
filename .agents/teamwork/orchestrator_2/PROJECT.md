# Project: Smart Waste Management System (SWMS) - Day 2 Backend API & Database

## Architecture
- FastAPI REST API application (`backend/app/main.py`) running under Uvicorn with prefix `/api/v1`.
- Dual database support: Primary PostgreSQL (`psycopg2`) with automatic fallback to local SQLite (`sqlite:///./swms_dev.db`) on connection failure/timeout, ensuring zero-dependency local development and testing.
- Database ORM via SQLAlchemy 2.0 with Alembic batch migrations (`render_as_batch=True`).
- Authentication: Stateless JWT (HS256) via `pyjwt` with 24h expiration, native `bcrypt` password hashing (Python 3.12 compatible).
- Role-Based Access Control (RBAC): `admin` and `user` roles enforced via FastAPI dependency injection (`get_current_user`, `get_current_admin`).
- Machine Learning Integration: Singleton `WastePredictor` loading PyTorch MobileNetV2 (`waste_model.pth`, `class_to_idx.json`) for CPU inference (`< 200ms` target latency).
- Media Storage: Uploaded waste report evidence stored at `backend/uploads/reports/` and served statically at `/uploads/reports/`.
- Audit Logging: Immutable history in `report_logs` recording every status transition (`Pending` -> `In Progress` -> `Completed` | `Rejected`).
- Automated Test Suite: Isolated in-memory SQLite (`sqlite:///:memory:`) with `pytest` and `fastapi.testclient.TestClient`.

## Code Layout
```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py             # get_db, get_current_user, get_current_admin
│   │   └── v1/
│   │       ├── auth.py         # POST /register, POST /login, GET /me
│   │       ├── predict.py      # POST /predict
│   │       ├── reports.py      # POST /reports, GET /reports, GET /reports/{id}, PATCH /reports/{id}/status
│   │       ├── dashboard.py    # GET /dashboard/stats
│   │       └── categories.py   # GET /categories
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (DATABASE_URL, JWT_SECRET, etc.)
│   │   ├── database.py         # Engine with automatic SQLite fallback & sessionmaker
│   │   ├── security.py         # Native bcrypt hashing & PyJWT token utilities
│   │   └── seed.py             # Idempotent master data & default test accounts
│   ├── models/
│   │   ├── __init__.py         # Export all models for Alembic discovery
│   │   ├── base.py             # DeclarativeBase
│   │   ├── user.py             # User (UUID pk, email, password_hash, role, etc.)
│   │   ├── category.py         # Category (int pk, slug, name, badge_color)
│   │   ├── report.py           # WasteReport (UUID pk, image_url, status, coords, etc.)
│   │   └── log.py              # ReportLog (UUID pk, report_id, actor_id, transitions)
│   ├── schemas/
│   │   ├── auth.py             # RegisterRequest, LoginRequest, TokenResponse, UserResponse
│   │   ├── predict.py          # PredictResponse, ProbabilitiesSchema
│   │   ├── report.py           # ReportCreate, ReportResponse, ReportListResponse, StatusUpdate
│   │   ├── dashboard.py        # DashboardStatsResponse, SummaryMetrics, CategoryDist
│   │   └── category.py         # CategoryResponse
│   ├── uploads/
│   │   └── reports/            # Saved uploaded report images
│   └── main.py                 # FastAPI application with lifespan, CORS, and static mount
├── alembic/
│   ├── env.py                  # Configured with batch mode & shared database engine
│   ├── script.py.mako
│   └── versions/               # Initial schema migration
├── alembic.ini
├── requirements.txt
└── seed.py                     # Standalone CLI entrypoint for database seeding
tests/
├── conftest.py                 # Pytest fixtures: test_engine, db_session, client, tokens
├── test_day2_auth.py           # Auth & RBAC test suite (15 tests)
├── test_day2_predict.py        # ML inference endpoint test suite (14 tests)
├── test_day2_reports.py        # Reports CRUD & audit logs test suite (22 tests)
├── test_day2_dashboard.py      # Admin dashboard statistics test suite (11 tests)
├── test_day2_db_fallback.py    # Database fallback & SQLite compatibility test suite (15 tests)
├── test_tier5_day2_adversarial.py # Tier 5 White-box adversarial hardening (34 tests)
├── test_adversarial_m1.py      # Concurrency & cascade adversarial tests (17 tests)
├── test_day2_m1_adversarial.py # Connection & batch limits adversarial tests (24 tests)
└── e2e_runner.py               # E2E test verification runner (89 tests)
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Health & Root Endpoints | `GET /`, `GET /health`, `GET /api/v1/health` probes | M1 | `main.py`, RUNBOOK |
| 2 | DB Engine & Automatic Fallback | PostgreSQL primary with SQLite automatic fallback | M1 | ORIGINAL_REQUEST R1 |
| 3 | Alembic Batch Migrations | Schema versioning supporting SQLite batch mode | M1 | ORIGINAL_REQUEST R1 |
| 4 | Relational Models | `User`, `Category`, `WasteReport`, `ReportLog` models | M1 | ORIGINAL_REQUEST R2, ERD.md |
| 5 | Master Category Seeding | Organic, Plastic, Paper default categories | M1 | ORIGINAL_REQUEST R2, RUNBOOK |
| 6 | Default Accounts Seeding | `admin@bilcode.id` and `user@bilcode.id` credentials | M1 | ORIGINAL_REQUEST R2, RUNBOOK |
| 7 | Bcrypt Password Security | Native Python 3.12 compatible bcrypt hashing | M2 | ORIGINAL_REQUEST R3, ADR.md |
| 8 | JWT Token Management | Sign & decode HS256 JWT tokens with 24h lifetime | M2 | ORIGINAL_REQUEST R3, API_SPECS |
| 9 | User Registration | `POST /api/v1/auth/register` endpoint | M2 | ORIGINAL_REQUEST R3, API_SPECS |
| 10 | User Login | `POST /api/v1/auth/login` endpoint returning token | M2 | ORIGINAL_REQUEST R3, API_SPECS |
| 11 | Current User Profile | `GET /api/v1/auth/me` endpoint | M2 | ORIGINAL_REQUEST R3, API_SPECS |
| 12 | Role-Based Access Control | Guard dependencies enforcing admin vs user permissions | M2 | ORIGINAL_REQUEST R3, API_SPECS |
| 13 | PyTorch ML Predict Endpoint | `POST /api/v1/predict` multipart image classification | M3 | ORIGINAL_REQUEST R4, API_SPECS |
| 14 | Evidence Photo Storage | `backend/uploads/reports/` with `/uploads` static mount | M3 | ARCHITECTURE.md, PRD.md |
| 15 | Waste Report Submission | `POST /api/v1/reports` with image upload, GPS, category | M4 | ORIGINAL_REQUEST R5, API_SPECS |
| 16 | Waste Report Listing | `GET /api/v1/reports` with status/cat filter, search, paging | M4 | ORIGINAL_REQUEST R5, API_SPECS |
| 17 | Waste Report Detail | `GET /api/v1/reports/{id}` with full details & audit logs | M4 | ORIGINAL_REQUEST R5, API_SPECS |
| 18 | Admin Status Update | `PATCH /api/v1/reports/{id}/status` restricted to Admin | M4 | ORIGINAL_REQUEST R5, API_SPECS |
| 19 | Audit Log Automation | Automatic insertion in `report_logs` on every transition | M4 | ORIGINAL_REQUEST R5, ERD.md |
| 20 | Admin Dashboard Stats | `GET /api/v1/dashboard/stats` summary, distributions | M5 | ORIGINAL_REQUEST R6, API_SPECS |
| 21 | Categories Master List | `GET /api/v1/categories` public dropdown endpoint | M5 | ERD.md, STYLING_GUIDE |
| 22 | E2E Requirement Tests | 4-Tier opaque-box test suite published in TEST_READY | M_TEST | Dual Track E2E |
| 23 | 100% E2E Pass Verification | Pass all Day 2 E2E and integration tests | M6 | Final Milestone Phase 1 |
| 24 | Adversarial Hardening | Tier 5 adversarial edge cases & coverage hardening | M6 | Final Milestone Phase 2 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M_TEST | E2E Testing Track | Design 4-tier requirement test suite & publish `TEST_READY.md` | none | DONE |
| M1 | Core Backend & DB Engine & Models | Config, DB engine + fallback, Alembic batch, models & seeding | none | DONE |
| M2 | JWT Auth & RBAC | Native bcrypt, PyJWT, `register`, `login`, `me`, auth dependencies | M1 | DONE |
| M3 | ML Inference & File Serving | `POST /api/v1/predict`, `WastePredictor` singleton, static upload mount | M1 | DONE |
| M4 | Waste Reports CRUD & Audit Logs | `POST /reports`, `GET /reports`, `GET /reports/{id}`, `PATCH /status`, `report_logs` auto-logging | M1, M2, M3 | DONE |
| M5 | Dashboard Stats & Categories Master | `GET /dashboard/stats`, `GET /categories` | M4 | DONE |
| M6 | Final Milestone (E2E Pass & Hardening) | Phase 1: 100% E2E pass; Phase 2: Tier 5 Adversarial Coverage Hardening | M1..M5, TEST_READY | DONE |
