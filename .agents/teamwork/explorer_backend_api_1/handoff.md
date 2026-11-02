# Handoff Report: FastAPI Backend API Contract & Data Schemas (Day 2 -> Day 3)

## 1. Observation

Direct observations from source inspection and execution in `BillcodeTech/backend`:

1. **Router Registration (`backend/app/main.py:105-116`)**:
   - `app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])`
   - `app.include_router(predict_router, prefix=f"{settings.API_V1_STR}/predict", tags=["Prediction"])`
   - `app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])`
   - `app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])`
   - `app.include_router(categories_router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categories"])`
   - Confirmed via route introspection:
     - `/api/v1/auth/register` [POST]
     - `/api/v1/auth/login` [POST]
     - `/api/v1/auth/me` [GET]
     - `/api/v1/predict` [POST]
     - `/api/v1/reports` [POST, GET]
     - `/api/v1/reports/{id}` [GET]
     - `/api/v1/reports/{id}/status` [PATCH]
     - `/api/v1/dashboard/stats` [GET]
     - `/api/v1/categories` [GET]
     - `/uploads` [StaticFiles mount at `backend/uploads`]
   - **No `/users` router or `GET /api/v1/users` route exists anywhere in the codebase.**

2. **Dashboard Stats Keys (`backend/app/schemas/dashboard.py:9-18` & `backend/app/api/v1/dashboard.py:44-63`)**:
   - The summary object contains:
     ```python
     total_reports: int
     pending_count: int
     in_progress_count: int
     completed_count: int
     rejected_count: int
     completion_rate_percent: float
     active_users: Optional[int] = None
     ```
   - The keys are named `pending_count` and `in_progress_count` (NOT `pending_reports` or `in_progress_reports`), and `completion_rate_percent` (NOT `completion_rate`).
   - The response wrapper is: `{"status": "success", "data": {"summary": {...}, "category_distribution": [...], "recent_activities": [...]}}`.

3. **Reports Listing & Filtering (`backend/app/api/v1/reports.py:195-280` & `backend/app/schemas/report.py:101-115`)**:
   - Query parameters supported:
     - `status: Optional[str] = Query(None)`
     - `category_id: Optional[int] = Query(None)`
     - `search: Optional[str] = Query(None)`
     - `page: int = Query(1, ge=1)`
     - `limit: int = Query(10, ge=1, le=100)`
   - Envelope keys:
     - `status`: `"success"`
     - `meta`: `{"total_items": int, "current_page": int, "total_pages": int, "limit": int}`
     - `data`: List of `ReportListItem` objects.

4. **Report Status Transition Rules (`backend/app/api/v1/reports.py:383-402`)**:
   - `allowed_transitions = {"Pending": {"In Progress", "Rejected"}, "In Progress": {"Completed", "Rejected"}}`.
   - `Completed` and `Rejected` are terminal states.
   - Requires `admin` role (`get_current_admin` dependency).
   - Status update payload: `{"status": str, "admin_notes": Optional[str]}`.

5. **Authentication & Credentials (`backend/app/core/seed.py:41-56` & `backend/app/api/v1/auth.py:93-191`)**:
   - Seed accounts:
     - Admin: `admin@bilcode.id` / `Admin123!` (role: `admin`)
     - User: `user@bilcode.id` / `User123!` (role: `user`)
   - `POST /api/v1/auth/login` accepts both `application/json` (`{"email": "...", "password": "..."}`) and `application/x-www-form-urlencoded` (`username=...&password=...`).
   - Returns token: `{"status": "success", "data": {"access_token": "...", "token_type": "bearer", "user": {...}}}`.
   - `GET /api/v1/auth/me` requires `Authorization: Bearer <access_token>`.

6. **CORS Configuration (`backend/app/main.py:59-69`)**:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "http://127.0.0.1:3000",
           "*",
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

7. **Static Image Uploads (`backend/app/main.py:98-102` & `backend/app/api/v1/reports.py:138`)**:
   - Upload URL format: `/uploads/reports/{unique_filename}`
   - Full URL from browser: `http://localhost:8000/uploads/reports/{unique_filename}`.

8. **Error Formats**:
   - HTTP 400, 401, 403, 404: `{"detail": "<message>"}`
   - HTTP 422: `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` or custom `{"detail": "<message>"}`.

---

## 2. Logic Chain

1. From Observation 1, the FastAPI app mounts 5 routers under `/api/v1`: `auth`, `predict`, `reports`, `dashboard`, `categories`. No `users` router exists in `backend/app/api/v1/` or `main.py`. Therefore, an admin user listing endpoint (`GET /api/v1/users`) was not implemented in Day 2. The Day 3 Web Dashboard implementers must be notified so they can handle User Management appropriately (either by adding the endpoint or providing fallback/mock data).
2. From Observation 2, the frontend metrics cards must not look for `data.total_reports` or `data.pending_reports`. Instead, they must access `data.summary.total_reports`, `data.summary.pending_count`, `data.summary.in_progress_count`, `data.summary.completed_count`, and `data.summary.completion_rate_percent`.
3. From Observation 3, the reports table in `web/` must pass query parameters `page`, `limit`, `status`, `category_id`, and `search`. The pagination component must read metadata from `meta.total_items`, `meta.current_page`, `meta.total_pages`, and `meta.limit`.
4. From Observation 4, the review modal disposition form must only offer valid transitions: `Pending` -> `In Progress` | `Rejected`, and `In Progress` -> `Completed` | `Rejected`. Terminal states must have status change controls disabled.
5. From Observation 5, 6, and 7, the Next.js API client in `web/src/lib/api.ts` must use `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`), submit JSON to `/api/v1/auth/login`, store the JWT token, and attach `Authorization: Bearer <token>` on all requests to protected routes. Image URLs returned by the backend (`/uploads/reports/...`) must be prefixed with `NEXT_PUBLIC_API_URL`.

---

## 3. Caveats

1. **User Management Endpoint Absence**: While `docs/TASKS.md` Task 3.6 mentions "Manajemen User list untuk admin", `docs/API_SPECS.md` and the actual Day 2 backend implementation do not include a `GET /api/v1/users` endpoint. This is documented with recommended TypeScript interfaces and mock fallback strategies.
2. **Database State**: The SQLite database file `backend/swms_dev.db` exists. When the FastAPI server starts, its lifespan context manager runs `seed_database(db)` idempotently, ensuring test users and master categories are present.

---

## 4. Conclusion

All actual FastAPI backend contracts, exact schema field names, query parameters, auth mechanisms, seed credentials, CORS configurations, error structures, and upload paths have been fully documented in `report.md`. The Day 3 Web Dashboard implementers now have the exact specifications to build the Next.js 14 web application without guesswork.

---

## 5. Verification Method

To independently verify these findings:
1. Inspect router declarations:
   ```powershell
   python -c "import sys, os; sys.path.insert(0, os.path.abspath('BillcodeTech/backend')); sys.path.insert(0, os.path.abspath('BillcodeTech')); from app.main import app; print([(r.path, list(r.methods)) for r in app.routes if hasattr(r, 'methods')])"
   ```
2. Verify automated test suite passing:
   ```powershell
   pytest tests/test_day2_auth.py tests/test_day2_dashboard.py tests/test_day2_reports.py
   ```
3. Inspect schema definitions directly:
   - `BillcodeTech/backend/app/schemas/dashboard.py`
   - `BillcodeTech/backend/app/schemas/report.py`
   - `BillcodeTech/backend/app/schemas/auth.py`
   - `BillcodeTech/backend/app/core/seed.py`
