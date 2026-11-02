# Smart Waste Management System (SWMS) - Backend Test Infrastructure

## 1. Testing Philosophy & Architecture

The Day 2 SWMS backend automated test infrastructure is designed under a **Zero-Dependency, Requirement-Driven, Opaque-Box** philosophy. It guarantees that the entire test suite can execute reliably in local developer environments, CI pipelines, and take-home evaluation environments without requiring external services, live Docker daemons, or internet connectivity.

### Core Architectural Pillars
1. **Zero External Service Dependencies**: Automated connection probing attempts primary PostgreSQL database connectivity; upon unavailability or connection timeout, it transparently falls back to an isolated SQLite engine.
2. **In-Memory Concurrency & Isolation**: Tests run against `sqlite:///:memory:` configured with SQLAlchemy `StaticPool` and `check_same_thread=False`, ensuring fast, deterministic, non-interfering execution.
3. **Strict Relational Integrity**: SQLite does not enforce foreign keys by default. The test engine registers a connection listener (`PRAGMA foreign_keys=ON;`), guaranteeing strict foreign key constraint validation identical to PostgreSQL.
4. **Contract-Driven Specification**: Every test assertion is derived directly from authoritative system specifications (`docs/API_SPECS.md`, `docs/ERD.md`, `docs/RUNBOOK.md`, `docs/FLOWS.md`, and `ORIGINAL_REQUEST.md`).
5. **Backward Compatibility**: Fully preserves Day 1 test coverage across all 5 Day 1 tiers (99 tests) while adding 76 Day 2 backend tests (total 175 tests).

---

## 2. Four-Tier Test Architecture

The Day 2 backend test suite adheres to a structured 4-tier testing hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 4: Real-World Operational Scenarios (RUNBOOK.md)        │
│ Multi-city Jakarta/Bandung coordinates, multi-report triage │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Cross-Feature Pairwise Integrations                 │
│ Citizen Reg -> Login -> Report + AI -> Admin PATCH -> Stats │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Boundary, Corner Cases & RBAC Security Hardening    │
│ Out-of-bounds coords, terminal states, 403 checks, zero-div │
├─────────────────────────────────────────────────────────────┤
│ Tier 1: Isolated Feature & Contract Coverage (Happy Paths)  │
│ Auth, ML Predict, Reports CRUD, Dashboard Stats, Categories │
└─────────────────────────────────────────────────────────────┘
```

### Tier Breakdown
- **Tier 1: Feature Coverage (Isolation)**
  - Happy path verification for every functional endpoint and database operation.
  - Verifies exact HTTP status codes (`200 OK`, `201 Created`), response schemas, pagination metadata, and database state updates.
- **Tier 2: Boundary & Corner Cases (Negative & Edge Testing)**
  - Input validation bounds: coordinates (latitude $\notin [-90, 90]$, longitude $\notin [-180, 180]$), missing required fields (`422`), non-existent foreign keys (`400`/`404`).
  - File validation stress: unsupported extensions (`.txt`, `.pdf`), corrupted bytes, 0-byte empty payloads, extreme dimensions ($1\times1$, $1000\times1000$), grayscale mode conversion.
  - Role-Based Access Control (RBAC): citizen non-admin tokens receiving `403 Forbidden` on admin-restricted endpoints (`PATCH /reports/{id}/status`, `GET /dashboard/stats`).
  - State Machine Terminality: invalid direct transitions (`Pending` $\rightarrow$ `Completed`) and transitions from terminal states (`Completed`, `Rejected`) rejected with `400 Bad Request`.
  - Resilience: zero reports in database handled without `ZeroDivisionError` (completion rate returns `0.0%`).
- **Tier 3: Cross-Feature Integrations (Pairwise Verification)**
  - Tests interactions across system boundaries: Registration $\rightarrow$ Authentication $\rightarrow$ Image Upload $\rightarrow$ Machine Learning Inference $\rightarrow$ State Machine Progression $\rightarrow$ Audit Trail Recording $\rightarrow$ Dashboard Metric Aggregation.
- **Tier 4: Real-World Operational Scenarios**
  - Full end-to-end evaluation flow matching `docs/RUNBOOK.md`: evaluator login (`admin@bilcode.id` and `user@bilcode.id`), report creation at real coordinates (Monas, Bundaran HI, Gedung Sate), and complete lifecycle triage with admin audit notes.

---

## 3. Pytest Fixture Ecosystem (`tests/conftest.py`)

The fixture layer provides clean, modular, and reusable components across all test modules:

| Fixture | Scope | Description |
|---|---|---|
| `test_engine` | `session` | In-memory SQLite engine with `StaticPool` and `PRAGMA foreign_keys=ON;`. |
| `db_session` | `function` | Transactional session with automatic rollback upon test completion, preventing state leaks. |
| `seed_data` | `function` | Idempotently populates 3 master categories and 2 default accounts (`admin@bilcode.id`, `user@bilcode.id`). |
| `client` | `function` | FastAPI `TestClient` with `get_db` overridden to provide the test database session. |
| `admin_headers` | `function` | Bearer Authorization header for Super Admin (`role: admin`). |
| `user_headers` | `function` | Bearer Authorization header for Citizen (`role: user`). |
| `dummy_image_bytes` | `session` | Valid JPEG image dynamically generated in memory via Pillow. |
| `dummy_png_bytes` | `session` | Valid PNG image dynamically generated in memory via Pillow. |
| `dummy_webp_bytes` | `session` | Valid WebP image dynamically generated in memory via Pillow. |
| `corrupt_image_bytes` | `session` | Corrupted non-image binary stream with invalid JPEG headers. |
| `empty_file_bytes` | `session` | 0-byte empty binary payload for upload boundary testing. |

---

## 4. Test Suite Inventory

| File Path | Target Domain | Tests | Focus Areas |
|---|---|---|---|
| `tests/test_day2_db_fallback.py` | Database & Fallback | 14 | Automatic fallback from unreachable Postgres, foreign key enforcement, ERD schema validation, idempotent seeding, bcrypt security. |
| `tests/test_day2_auth.py` | Auth & RBAC | 14 | User registration, JWT login, profile retrieval, duplicate email prevention, malformed/expired token rejection, inactive user lock. |
| `tests/test_day2_predict.py` | ML Inference | 14 | MobileNetV2 image classification, JPEG/PNG/WebP formats, probabilities normalization, unsupported/corrupt file rejection, extreme dimensions. |
| `tests/test_day2_reports.py` | Reports CRUD & Triage | 23 | Report submission with GPS & photo, list with filters/search/pagination, single report detail, admin status updates, audit log records, RBAC 403 guard, coordinate boundary checks, Tier 3 & Tier 4 flows. |
| `tests/test_day2_dashboard.py` | Admin Stats & Master Data | 11 | Dashboard aggregate statistics, completion rate math, category distributions, active users, master categories catalog, health/root probes, empty DB zero-division prevention. |
| `tests/test_tier1_structure.py` | Day 1 Structure | 38 | Monorepo layout, dataset presence, citations, scripts existence. |
| `tests/test_tier2_validation.py` | Day 1 Validation | 36 | Image integrity, class balance, model checkpoint format, training arguments. |
| `tests/test_tier3_interaction.py` | Day 1 Integration | 8 | Dataset <-> Model <-> Predictor contracts, evaluate script integration. |
| `tests/test_tier4_scenarios.py` | Day 1 Scenarios | 6 | Per-class inference, aspect ratios, metrics parsing. |
| `tests/test_tier5_adversarial_empirical.py` | Day 1 Hardening | 11 | Numerical stability, repeatability, batch benchmark, color spaces. |
| **Total** | **Whole Project** | **175** | **Complete coverage across Day 1 ML pipeline and Day 2 Backend API** |

---

## 5. Execution Commands

### Run Day 2 Test Suite:
```bash
pytest tests/test_day2_db_fallback.py tests/test_day2_auth.py tests/test_day2_predict.py tests/test_day2_reports.py tests/test_day2_dashboard.py -v
```

### Run Entire Repository Suite (Day 1 + Day 2):
```bash
pytest tests/ -v
```

### Run Specific Tier or Category:
```bash
# Database connectivity & fallback tests:
pytest tests/test_day2_db_fallback.py -v

# Health and root probe tests:
pytest tests/test_day2_dashboard.py -k "root or health" -v
```
