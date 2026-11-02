# SWMS Backend API Contract & Schema Specification (Day 2 Analysis)

> **Generated for:** Day 3 Web Dashboard Engineering Team (Next.js 14 App Router + Tailwind CSS)  
> **Backend Source:** `backend/app/` (FastAPI 0.110+, SQLAlchemy 2.0+, Pydantic v2, SQLite / PostgreSQL)  
> **Base URL (Local API):** `http://localhost:8000/api/v1`  
> **Static Media URL:** `http://localhost:8000/uploads/reports/<filename>`  
> **Interactive OpenAPI Docs:** `http://localhost:8000/docs`  

---

## Executive Summary & Critical Findings

1. **Authentication Token Format**: Bearer JWT passed in header `Authorization: Bearer <access_token>`. The token is signed using HS256 (`settings.JWT_SECRET`) and contains claims `{ "sub": "<uuid_str>", "email": "...", "role": "admin"|"user", "exp": <unix_ts> }`.
2. **Dashboard Stats Keys**: Inside `data.summary`, the keys use the suffix `_count` rather than `_reports` (e.g. `pending_count`, `in_progress_count`, `completed_count`, `rejected_count`) and `completion_rate_percent` (NOT `completion_rate`). Top-level data contains `summary`, `category_distribution`, and `recent_activities`.
3. **Reports Filtering & Pagination**: Query parameters are `status`, `category_id` (integer ID, not category slug/name), `search` (keyword across title/description/address_note), `page` (default 1, ge=1), and `limit` (default 10, 1-100). The pagination envelope has key `meta` (`total_items`, `current_page`, `total_pages`, `limit`) and `data` (list of report items).
4. **Missing Users Listing Route (`/api/v1/users`)**: **Day 2 backend DOES NOT have a `/users` router or `GET /api/v1/users` endpoint.** The only user endpoint implemented in Day 2 is `GET /api/v1/auth/me`. Recommendations are provided below for Day 3 Web User Management.
5. **CORS Configuration**: Permissive for `http://localhost:3000`, `http://127.0.0.1:3000`, and `*` with `allow_credentials=True`, all methods, and all headers.
6. **Error Response Format**: FastAPI standard `{"detail": "<message>"}` for HTTP 400, 401, 403, 404, and standard Pydantic array `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` for HTTP 422.

---

## 1. Authentication & Session Management

### 1.1 POST `/api/v1/auth/login`
- **Method:** `POST`
- **URL Path:** `/api/v1/auth/login`
- **Auth:** Public
- **Supported Content-Types:**
  - `application/json`
  - `application/x-www-form-urlencoded`
  - `multipart/form-data`
- **Request Body Parameters:**
  - `email` (string, required): User email address (or `username` when using form-urlencoded)
  - `password` (string, required): Plaintext password

#### Request Body (`application/json`):
```json
{
  "email": "admin@bilcode.id",
  "password": "Admin123!"
}
```

#### Response `200 OK`:
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "993a401c-3b09-4bf9-8ebf-cfce48375422",
      "email": "admin@bilcode.id",
      "full_name": "Super Admin",
      "role": "admin",
      "phone_number": "081234567890",
      "created_at": "2026-11-01T10:00:00Z"
    }
  }
}
```

#### Error Responses:
- `401 Unauthorized`:
  ```json
  { "detail": "Invalid email or password" }
  ```
  or if account is inactive:
  ```json
  { "detail": "User account is inactive" }
  ```
- `422 Unprocessable Entity`:
  ```json
  { "detail": "Email and password are required" }
  ```
  or
  ```json
  { "detail": "Invalid JSON payload" }
  ```

---

### 1.2 GET `/api/v1/auth/me`
- **Method:** `GET`
- **URL Path:** `/api/v1/auth/me`
- **Auth:** `Bearer <access_token>` (required)
- **Request Headers:**
  - `Authorization: Bearer <access_token>`

#### Response `200 OK`:
```json
{
  "status": "success",
  "data": {
    "id": "993a401c-3b09-4bf9-8ebf-cfce48375422",
    "email": "admin@bilcode.id",
    "full_name": "Super Admin",
    "role": "admin",
    "phone_number": "081234567890",
    "created_at": "2026-11-01T10:00:00Z"
  }
}
```

#### Error Responses:
- `401 Unauthorized` (Missing token):
  ```json
  { "detail": "Not authenticated" }
  ```
- `401 Unauthorized` (Expired or invalid token):
  ```json
  { "detail": "Could not validate credentials" }
  ```

---

### 1.3 POST `/api/v1/auth/register`
- **Method:** `POST`
- **URL Path:** `/api/v1/auth/register`
- **Auth:** Public
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "full_name": "Budi Santoso",
    "email": "budi.santoso@example.com",
    "password": "Password123!",
    "phone_number": "081298765432"
  }
  ```
  - `full_name`: string (1-150 characters)
  - `email`: string (valid email format)
  - `password`: string (minimum 6 characters)
  - `phone_number`: string (optional, max 30 characters)

#### Response `201 Created`:
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": "7c8e9b81-64d4-482a-bc91-2489e24f4692",
    "email": "budi.santoso@example.com",
    "full_name": "Budi Santoso",
    "role": "user",
    "phone_number": "081298765432",
    "created_at": "2026-11-02T12:00:00Z"
  }
}
```

#### Error Responses:
- `400 Bad Request` (Duplicate email):
  ```json
  { "detail": "Email already registered" }
  ```
- `422 Unprocessable Entity` (Validation failure):
  ```json
  {
    "detail": [
      {
        "loc": ["body", "password"],
        "msg": "String should have at least 6 characters",
        "type": "string_too_short"
      }
    ]
  }
  ```

---

## 2. Dashboard Statistics & Analytics

### 2.1 GET `/api/v1/dashboard/stats`
- **Method:** `GET`
- **URL Path:** `/api/v1/dashboard/stats`
- **Auth:** `Bearer <access_token>` (Admin Only — role must be `admin`)
- **Query Parameters:** None

#### Response `200 OK`:
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_reports": 142,
      "pending_count": 18,
      "in_progress_count": 12,
      "completed_count": 105,
      "rejected_count": 7,
      "completion_rate_percent": 73.94,
      "active_users": 2
    },
    "category_distribution": [
      {
        "category": "Organic Waste",
        "count": 64,
        "percentage": 45.07
      },
      {
        "category": "Plastic Waste",
        "count": 52,
        "percentage": 36.62
      },
      {
        "category": "Paper Waste",
        "count": 26,
        "percentage": 18.31
      }
    ],
    "recent_activities": [
      {
        "report_id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
        "action": "Status changed to In Progress",
        "timestamp": "2026-11-02T11:45:00Z"
      },
      {
        "report_id": "4a12cb34-dce5-4122-8991-34fa98bb0192",
        "action": "Report created (Pending)",
        "timestamp": "2026-11-02T11:30:00Z"
      }
    ]
  }
}
```

#### TypeScript Types for Dashboard:
```typescript
export interface DashboardSummary {
  total_reports: number;
  pending_count: number;
  in_progress_count: number;
  completed_count: number;
  rejected_count: number;
  completion_rate_percent: number;
  active_users?: number | null;
}

export interface CategoryDistribution {
  category: string;
  count: number;
  percentage: number;
}

export interface RecentActivity {
  report_id: string; // UUID
  action: string;
  timestamp: string; // ISO datetime
}

export interface DashboardStatsData {
  summary: DashboardSummary;
  category_distribution: CategoryDistribution[];
  recent_activities: RecentActivity[];
}

export interface DashboardStatsResponse {
  status: "success";
  data: DashboardStatsData;
}
```

#### Error Responses:
- `401 Unauthorized`: `{ "detail": "Not authenticated" }`
- `403 Forbidden` (Citizen user): `{ "detail": "Admin access required" }`

---

## 3. Waste Reports Management

### 3.1 GET `/api/v1/reports`
- **Method:** `GET`
- **URL Path:** `/api/v1/reports` (also works with trailing slash `/api/v1/reports/`)
- **Auth:** `Bearer <access_token>`
- **Query Parameters:**
  - `status` (string, optional): Filter by exact status (`Pending`, `In Progress`, `Completed`, `Rejected`)
  - `category_id` (integer, optional): Filter by Category ID (`1` for Organic, `2` for Plastic, `3` for Paper)
  - `search` (string, optional): Case-insensitive keyword search matching `title`, `description`, or `address_note`
  - `page` (integer, optional, default: `1`, min: `1`): Current page number
  - `limit` (integer, optional, default: `10`, min: `1`, max: `100`): Items per page

#### Response `200 OK`:
```json
{
  "status": "success",
  "meta": {
    "total_items": 45,
    "current_page": 1,
    "total_pages": 5,
    "limit": 10
  },
  "data": [
    {
      "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
      "title": "Tumpukan botol plastik di pinggir selokan",
      "image_url": "/uploads/reports/00b7494eb65843e8bcf6fc9472bd8ce7.jpg",
      "latitude": -6.2088,
      "longitude": 106.8456,
      "status": "Pending",
      "created_at": "2026-11-02T10:15:30Z",
      "category": {
        "id": 2,
        "name": "Plastic Waste",
        "badge_color": "#0284c7",
        "slug": "plastic"
      },
      "reporter": {
        "id": "7c8e9b81-64d4-482a-bc91-2489e24f4692",
        "full_name": "Darell Rangga",
        "email": "user@bilcode.id"
      }
    }
  ]
}
```

---

### 3.2 GET `/api/v1/reports/{id}`
- **Method:** `GET`
- **URL Path:** `/api/v1/reports/{id}`
- **Auth:** `Bearer <access_token>`
- **Path Parameter:**
  - `id`: UUID string of the report

#### Response `200 OK`:
```json
{
  "status": "success",
  "data": {
    "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
    "title": "Tumpukan botol plastik di pinggir selokan",
    "description": "Botol plastik menumpuk menyumbat aliran air.",
    "image_url": "/uploads/reports/00b7494eb65843e8bcf6fc9472bd8ce7.jpg",
    "detected_category": "Plastic Waste",
    "ai_confidence": 0.9421,
    "latitude": -6.2088,
    "longitude": 106.8456,
    "address_note": "Jl. Ahmad Yani No. 12, depan ruko",
    "status": "Pending",
    "admin_notes": null,
    "resolved_at": null,
    "created_at": "2026-11-02T10:15:30Z",
    "updated_at": "2026-11-02T10:15:30Z",
    "category": {
      "id": 2,
      "name": "Plastic Waste",
      "badge_color": "#0284c7",
      "slug": "plastic"
    },
    "reporter": {
      "id": "7c8e9b81-64d4-482a-bc91-2489e24f4692",
      "full_name": "Darell Rangga",
      "email": "user@bilcode.id"
    },
    "logs": [
      {
        "id": "55f5c3aa-608b-4a57-8273-0aa8398b1001",
        "previous_status": null,
        "new_status": "Pending",
        "actor_id": "7c8e9b81-64d4-482a-bc91-2489e24f4692",
        "remarks": "Initial report submission",
        "created_at": "2026-11-02T10:15:30Z"
      }
    ]
  }
}
```

#### Error Responses:
- `404 Not Found` (Invalid UUID or report does not exist):
  ```json
  { "detail": "Report not found" }
  ```

---

### 3.3 PATCH `/api/v1/reports/{id}/status`
- **Method:** `PATCH`
- **URL Path:** `/api/v1/reports/{id}/status`
- **Auth:** `Bearer <access_token>` (Admin Only — role must be `admin`)
- **Content-Type:** `application/json`
- **Path Parameter:** `id` (UUID string)
- **Request Body:**
  ```json
  {
    "status": "In Progress",
    "admin_notes": "Tim kebersihan armada #3 sedang meluncur ke lokasi."
  }
  ```

#### State Machine Transition Rules:
| Current Status | Allowed Next Statuses | Notes |
|:---|:---|:---|
| `Pending` | `In Progress`, `Rejected` | Direct skip to `Completed` is rejected |
| `In Progress` | `Completed`, `Rejected` | Setting `Completed` automatically sets `resolved_at` |
| `Completed` | *None (Terminal State)* | Any update rejected with HTTP 400 |
| `Rejected` | *None (Terminal State)* | Any update rejected with HTTP 400 |

#### Response `200 OK`:
```json
{
  "status": "success",
  "message": "Report status updated to In Progress",
  "data": {
    "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
    "status": "In Progress",
    "admin_notes": "Tim kebersihan armada #3 sedang meluncur ke lokasi.",
    "updated_at": "2026-11-02T11:00:00Z"
  }
}
```

#### Error Responses:
- `400 Bad Request` (Invalid status transition):
  ```json
  { "detail": "Invalid status transition from Pending to Completed" }
  ```
- `400 Bad Request` (Attempting to modify terminal state):
  ```json
  { "detail": "Report is already in terminal state 'Completed'" }
  ```
- `403 Forbidden` (Citizen user):
  ```json
  { "detail": "Admin access required" }
  ```
- `404 Not Found`:
  ```json
  { "detail": "Report not found" }
  ```

---

### 3.4 POST `/api/v1/reports` (Submission)
- **Method:** `POST`
- **URL Path:** `/api/v1/reports`
- **Auth:** `Bearer <access_token>`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Binary image file (JPEG, PNG, WebP, BMP)
  - `title`: string (1-200 chars)
  - `description`: string (optional)
  - `category_id`: integer (1, 2, or 3)
  - `latitude`: float (-90.0 to 90.0)
  - `longitude`: float (-180.0 to 180.0)
  - `address_note`: string (optional, max 255 chars)

#### Response `201 Created`:
```json
{
  "status": "success",
  "message": "Report submitted successfully",
  "data": {
    "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
    "title": "Tumpukan botol plastik di pinggir selokan",
    "image_url": "/uploads/reports/00b7494eb65843e8bcf6fc9472bd8ce7.jpg",
    "detected_category": "Plastic Waste",
    "ai_confidence": 0.9421,
    "status": "Pending",
    "created_at": "2026-11-02T10:15:30Z"
  }
}
```

---

## 4. Master Waste Categories

### 4.1 GET `/api/v1/categories`
- **Method:** `GET`
- **URL Path:** `/api/v1/categories` (or `/api/v1/categories/`)
- **Auth:** Public (no auth token required)

#### Response `200 OK`:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "slug": "organic",
      "name": "Organic Waste",
      "description": "Sisa makanan, dedaunan, sayuran, dan bahan mudah terurai",
      "badge_color": "#16a34a"
    },
    {
      "id": 2,
      "slug": "plastic",
      "name": "Plastic Waste",
      "description": "Botol plastik, kantong kresek, kemasan sachet, sedotan",
      "badge_color": "#0284c7"
    },
    {
      "id": 3,
      "slug": "paper",
      "name": "Paper Waste",
      "description": "Kertas karton, kardus, koran bekas, dokumen kertas",
      "badge_color": "#d97706"
    }
  ]
}
```

---

## 5. Machine Learning Prediction Endpoint

### 5.1 POST `/api/v1/predict`
- **Method:** `POST`
- **URL Path:** `/api/v1/predict`
- **Auth:** Public
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Binary image file (JPEG, PNG, WebP, BMP)

#### Response `200 OK`:
```json
{
  "status": "success",
  "data": {
    "category": "Plastic Waste",
    "confidence": 0.9421,
    "confidence_percentage": "94.21%",
    "category_id": 2,
    "probabilities": {
      "Organic Waste": 0.0312,
      "Plastic Waste": 0.9421,
      "Paper Waste": 0.0267
    }
  }
}
```

---

## 6. Static Uploads & Media Serving

- **Mount Point:** `/uploads` mapped to `backend/uploads/`
- **URL Structure:** Relative path returned by backend is `/uploads/reports/<hash>.<ext>`
- **Full Browser Image URL:**
  ```
  ${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${report.image_url}
  ```
  Example: `http://localhost:8000/uploads/reports/00b7494eb65843e8bcf6fc9472bd8ce7.jpg`

---

## 7. Seed Users & Default Credentials

Seeded via `backend/app/core/seed.py` (idempotent, automatic on FastAPI startup or via `python backend/seed.py`):

| Role | Email | Password | Full Name | Phone Number |
|:---|:---|:---|:---|:---|
| **Admin** | `admin@bilcode.id` | `Admin123!` | Super Admin | `081234567890` |
| **User (Citizen)** | `user@bilcode.id` | `User123!` | Warga Pelapor | `08123456789` |

---

## 8. CORS Configuration

Configured in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js local dev
        "http://127.0.0.1:3000",   # Alternate local loopback
        "*",                       # Permissive for mobile clients
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- Frontend requests originating from Next.js (`http://localhost:3000`) will pass preflight OPTIONS checks without CORS errors.
- Pass Authorization header: `Authorization: Bearer <token>`.

---

## 9. Investigation of User Management Endpoints (`/api/v1/users`)

### Finding
Inspection of `backend/app/main.py` and `backend/app/api/v1/` shows that **no `/users` router or `GET /api/v1/users` route exists in the Day 2 codebase**.
The only user-related endpoints are:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Recommendations for Day 3 Web Dashboard (Task 3.6 / R5)
For the User Management view in Next.js:
1. **Current User Display:** The dashboard header / profile widget reliably uses `GET /api/v1/auth/me` to get the logged-in admin's identity (`id`, `email`, `full_name`, `role`).
2. **User Management List View:**
   - If extending the backend is allowed or if a users router is added, the standard contract should be:
     `GET /api/v1/users` (Admin only) returning:
     ```json
     {
       "status": "success",
       "data": [
         {
           "id": "uuid",
           "email": "user@bilcode.id",
           "full_name": "Warga Pelapor",
           "role": "user",
           "phone_number": "08123456789",
           "is_active": true,
           "created_at": "2026-11-01T10:00:00Z"
         }
       ]
     }
     ```
   - If the backend must remain strictly untouched as per Day 2 boundaries, the Next.js frontend client in `web/src/lib/api.ts` should either:
     a) Implement `getUsers()` with fallback mock data showing the seeded users (`admin@bilcode.id` and `user@bilcode.id`), or
     b) If an endpoint is created in Day 3, follow the standard enveloped format above.

---

## 10. Complete TypeScript API Contracts for Next.js (`web/src/types/api.ts`)

```typescript
// ==========================================
// Generic API Envelope
// ==========================================
export interface ApiResponse<T> {
  status: "success" | "error";
  message?: string;
  data: T;
}

export interface ApiErrorResponse {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>;
}

// ==========================================
// Authentication Types
// ==========================================
export interface UserProfile {
  id: string; // UUID
  email: string;
  full_name: string;
  role: "admin" | "user";
  phone_number?: string | null;
  created_at?: string | null;
}

export interface LoginResponseData {
  access_token: string;
  token_type: "bearer";
  user: UserProfile;
}

// ==========================================
// Master Category Types
// ==========================================
export interface WasteCategory {
  id: number;
  slug: string;
  name: string;
  description?: string | null;
  badge_color: string;
}

export interface CategoryBrief {
  id: number;
  name: string;
  badge_color: string;
  slug?: string | null;
}

export interface ReporterBrief {
  id: string;
  full_name: string;
  email?: string | null;
}

// ==========================================
// Waste Report Types
// ==========================================
export type ReportStatus = "Pending" | "In Progress" | "Completed" | "Rejected";

export interface ReportListItem {
  id: string; // UUID
  title: string;
  image_url: string;
  latitude: number;
  longitude: number;
  status: ReportStatus;
  created_at: string;
  category: CategoryBrief;
  reporter: ReporterBrief;
}

export interface ReportLogItem {
  id: string; // UUID
  previous_status?: string | null;
  new_status: string;
  actor_id?: string | null;
  remarks?: string | null;
  created_at: string;
}

export interface ReportDetailData {
  id: string; // UUID
  title: string;
  description?: string | null;
  image_url: string;
  detected_category?: string | null;
  ai_confidence?: number;
  latitude: number;
  longitude: number;
  address_note?: string | null;
  status: ReportStatus;
  admin_notes?: string | null;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
  category: CategoryBrief;
  reporter: ReporterBrief;
  logs: ReportLogItem[];
}

export interface PaginationMeta {
  total_items: number;
  current_page: number;
  total_pages: number;
  limit: number;
}

export interface ReportListResponse {
  status: "success";
  meta: PaginationMeta;
  data: ReportListItem[];
}

// ==========================================
// Dashboard Stats Types
// ==========================================
export interface DashboardSummary {
  total_reports: number;
  pending_count: number;
  in_progress_count: number;
  completed_count: number;
  rejected_count: number;
  completion_rate_percent: number;
  active_users?: number | null;
}

export interface CategoryDistributionItem {
  category: string;
  count: number;
  percentage: number;
}

export interface RecentActivityItem {
  report_id: string;
  action: string;
  timestamp: string;
}

export interface DashboardStatsData {
  summary: DashboardSummary;
  category_distribution: CategoryDistributionItem[];
  recent_activities: RecentActivityItem[];
}
```
