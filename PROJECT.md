# Project: Smart Waste Management System (SWMS) - Day 3 Web Dashboard

## Architecture
- Monorepo containing `backend/`, `ml_pipeline/`, `web/`, `mobile/`, and `docs/`.
- Day 3 implements the **Web Dashboard** in `web/` using **Next.js 14 (App Router)** and **Tailwind CSS**, adhering to the **Eco-Tech Resilience** design system in `docs/STYLING_GUIDE.md`.
- Integrates directly with the FastAPI backend REST API (`http://localhost:8000/api/v1`) built in Day 2:
  - JWT Authentication & RBAC (`/api/v1/auth/login`, `/api/v1/auth/me`)
  - Admin Analytics Dashboard (`/api/v1/dashboard/stats`)
  - Waste Reports CRUD & Audit Logs (`/api/v1/reports`, `/api/v1/reports/{id}`, `/api/v1/reports/{id}/status`)
  - Master Categories catalog (`/api/v1/categories`)
  - Static Media uploads serving (`http://localhost:8000/uploads/...`)

## Code Layout
- `web/`:
  - `package.json`: Project scripts & dependencies (Next.js 14, React 18, Tailwind 3.4, Lucide icons, Axios, clsx, tailwind-merge)
  - `tsconfig.json`: TypeScript configuration with path aliases (`@/*` -> `./src/*`)
  - `next.config.mjs`: Next.js config with image domains (`localhost`)
  - `tailwind.config.ts`: Eco-Tech color tokens, typography scales, semantic badges
  - `postcss.config.js`: PostCSS plugins configuration
  - `.env.local`: Environment variables (`NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`)
  - `src/`:
    - `app/`:
      - `layout.tsx`: Root HTML layout with Google Fonts (`Space Grotesk`, `Inter`, `JetBrains Mono`)
      - `globals.css`: Tailwind directives, CSS variables, typography utility classes
      - `page.tsx`: Root landing page / redirect to `/dashboard` or `/login`
      - `(auth)/`:
        - `login/page.tsx`: Login view with credentials form, quick evaluator presets, error alerts
      - `(dashboard)/`:
        - `layout.tsx`: Authenticated app shell with responsive Sidebar, Header, and Auth Guard
        - `dashboard/page.tsx`: Analytics metrics cards, category distribution, recent activities
        - `reports/page.tsx`: Reports table, search, filters, pagination, review modal
        - `users/page.tsx`: User management list view for administrators
    - `components/`:
      - `Sidebar.tsx`: Desktop fixed sidebar + mobile slide-out drawer navigation
      - `Header.tsx`: Breadcrumbs, backend health indicator, user profile summary & logout
      - `StatCard.tsx`: Metric card widget with icon, count, subtitle, accent styling
      - `StatusBadge.tsx`: Semantic badge (Pending: amber, In Progress: blue, Completed: emerald, Rejected: rose)
      - `CategoryBadge.tsx`: Category chip (Organic: green, Plastic: sky, Paper: amber)
      - `CategoryChart.tsx`: Waste category distribution breakdown & proportional progress bar
      - `ReportModal.tsx`: Comprehensive review modal with photo preview, AI badge, Google Maps link, status patch form, audit trail
    - `lib/`:
      - `api.ts`: Axios client configured with `NEXT_PUBLIC_API_URL`, Bearer interceptor, image URL resolver
      - `auth.tsx`: Auth Context Provider (`useAuth`), token persistence, login/logout functions
      - `utils.ts`: Class name merger (`cn`), date formatting, coordinate formatting
    - `types/`:
      - `api.ts`: TypeScript contracts for User, Report, DashboardStats, Category, ApiResponse

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Eco-Tech Typography & Layout | Space Grotesk (headings), Inter (body/tables), JetBrains Mono (GPS/IDs) | M1 | ORIGINAL_REQUEST R1, STYLING_GUIDE.md |
| 2 | Eco-Tech Color Palette | Emerald primary `#059669`, slate neutrals, subtle borders | M1 | ORIGINAL_REQUEST R1, STYLING_GUIDE.md |
| 3 | Semantic Status Badges | Amber (Pending), Blue (In Progress), Emerald (Completed), Rose (Rejected) | M1 | ORIGINAL_REQUEST R1, STYLING_GUIDE.md |
| 4 | Category Visual Badges | Green (Organic), Sky (Plastic), Amber (Paper) with specific hex accents | M1 | STYLING_GUIDE.md, API_SPECS.md |
| 5 | Responsive Navigation Shell | Collapsible sidebar, header with breadcrumbs and live backend health ping | M1 | TASKS.md 3.1, STYLING_GUIDE.md |
| 6 | Axios API Client & Interceptors | Base URL `NEXT_PUBLIC_API_URL`, automatic Bearer header, 401 handling | M2 | ORIGINAL_REQUEST R5, TASKS.md 3.2 |
| 7 | Authentication & Login Page | Email & password form, JWT storage, evaluator quick presets | M2 | ORIGINAL_REQUEST R2, TASKS.md 3.2 |
| 8 | RBAC & Route Protection | Protected routes redirect unauthenticated users to `/login`, admin-only guards | M2 | ORIGINAL_REQUEST R2, FLOWS.md |
| 9 | Current User Profile Display | Fetches and renders authenticated user profile from `GET /api/v1/auth/me` | M2 | ORIGINAL_REQUEST R5, API_SPECS.md |
| 10 | Primary Analytics Stat Cards | 4 top cards: Total Reports, Pending, In Progress, Completion Rate % | M3 | ORIGINAL_REQUEST R3, TASKS.md 3.3 |
| 11 | Category Distribution Breakdown | Organic, Plastic, Paper waste distribution visualization & percentages | M3 | ORIGINAL_REQUEST R3, TASKS.md 3.3 |
| 12 | Recent Activity Audit Stream | Feed of recent report creations and status updates from backend stats | M3 | ORIGINAL_REQUEST R3, API_SPECS.md |
| 13 | Interactive Reports Table | Paginated table with thumbnails, titles, categories, reporter, GPS, status | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.4 |
| 14 | Keyword Search & Filtering | Keyword search across title/note + Status dropdown + Category dropdown | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.4 |
| 15 | Table Pagination Controls | Previous/Next pagination with page counts and item bounds | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.4 |
| 16 | Review Modal Photo Preview | High-res photo preview with URL resolution against backend static mount | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.5 |
| 17 | Review Modal AI Badge | Detected category name + confidence percentage in JetBrains Mono | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.5 |
| 18 | Review Modal Geolocation Link | Latitude & Longitude with clickable `https://www.google.com/maps?q=lat,long` | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.5 |
| 19 | Review Modal Status Disposition | Form with allowed state transitions + admin notes via `PATCH /reports/{id}/status` | M4 | ORIGINAL_REQUEST R4, TASKS.md 3.5 |
| 20 | Review Modal Audit Trail View | Chronological list of historical status transitions and remarks | M4 | API_SPECS.md, ERD.md |
| 21 | User Management List View | Table of registered users with roles, statuses, and registration dates | M5 | ORIGINAL_REQUEST R5, TASKS.md 3.6 |
| 22 | Navigation Integration & Responsive Shell | Complete end-to-end user navigation, mobile/tablet/desktop responsive testing | M5 | ORIGINAL_REQUEST R6, TASKS.md 3.6 |
| 23 | E2E Testing Suite Pass (Tiers 1-4) | Requirement-driven test suite validating web client, auth, stats, reports | M6 | Project Pattern Final Milestone |
| 24 | Adversarial Hardening (Tier 5) | Edge case handling, empty states, zero-division, network drops, token expiry | M6 | Project Pattern Tier 5 |
| 25 | Production Build Verification | Zero errors on `npm run build`, linting, and TypeScript typechecking | M6 | ORIGINAL_REQUEST R6 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0| Survey & Scope Mapping | Spec mining, backend API mapping, frontend environment audit | none | DONE |
| M_TEST| E2E Testing Track | Requirement-driven opaque-box test suite (Tiers 1-4), TEST_INFRA.md, TEST_READY.md | M0 | DONE |
| M1| Next.js 14 Setup & Eco-Tech Design System | `npm install`, configs, typography, status badges, responsive shell layout | M0 | DONE |
| M2| API Client, Auth & Route Protection | Axios client, auth context, `/login` page, token persistence, RBAC guards | M1 | DONE |
| M3| Analytics Dashboard | `/dashboard` page, 4 stat cards, category distribution, recent activities | M2 | DONE |
| M4| Reports Table & Review Modal | `/reports` page, filters, search, pagination, modal with photo, AI badge, Google Maps, status PATCH form | M2 | IN_PROGRESS |
| M5| User Management & Full Navigation Integration | `/users` page, profile view, responsive audit across mobile/tablet/desktop | M3, M4 | PLANNED |
| M6| Final Milestone (E2E Pass & Adversarial Hardening) | Pass 100% E2E test suite + Tier 5 Adversarial hardening + `npm run build` | M1, M2, M3, M4, M5, TEST_READY | PLANNED |

## Interface Contracts
### Web Client ↔ Backend Auth Contract
- `POST /api/v1/auth/login`: `{ email, password }` -> `{ status: "success", data: { access_token, token_type: "bearer", user: { id, email, full_name, role } } }`
- `GET /api/v1/auth/me`: Header `Authorization: Bearer <token>` -> `{ status: "success", data: UserSummary }`

### Web Client ↔ Backend Dashboard Contract
- `GET /api/v1/dashboard/stats`: Header `Authorization: Bearer <admin_token>` -> `{ status: "success", data: { summary: { total_reports, pending_count, in_progress_count, completed_count, rejected_count, completion_rate_percent, active_users }, category_distribution: [...], recent_activities: [...] } }`

### Web Client ↔ Backend Reports Contract
- `GET /api/v1/reports?page=1&limit=10&status=Pending&category_id=1&search=xyz`: Header `Authorization: Bearer <token>` -> `{ status: "success", meta: { total_items, current_page, total_pages, limit }, data: [ReportItem, ...] }`
- `GET /api/v1/reports/{id}`: Header `Authorization: Bearer <token>` -> `{ status: "success", data: ReportDetailWithLogs }`
- `PATCH /api/v1/reports/{id}/status`: Header `Authorization: Bearer <admin_token>`, Body `{ status: "In Progress", admin_notes: "..." }` -> `{ status: "success", data: { id, status, admin_notes, updated_at } }`
- State Machine Transitions:
  - `Pending` -> `In Progress` | `Rejected`
  - `In Progress` -> `Completed` | `Rejected`
  - `Completed` / `Rejected` -> Terminal (no further transitions allowed)

### Web Client ↔ Static Media Contract
- Base backend origin: `http://localhost:8000`
- Image URL resolution: `${NEXT_PUBLIC_API_URL.replace('/api/v1', '')}${image_url}` -> `http://localhost:8000/uploads/reports/<filename>`
