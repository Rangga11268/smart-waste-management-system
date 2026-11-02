# Handoff Report: Specification Mining for Day 3 (SWMS Web Dashboard)

**Agent ID:** `spec_miner_day3_1`  
**Milestone:** Day 3 — Web Dashboard (Next.js 14 App Router & Tailwind CSS)  
**Parent Orchestrator:** `43d63726-8e7d-4ce8-9507-d98d72d21885`  
**Target Path:** `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day3_1\handoff.md`  

---

## 1. Observation

Direct observations extracted from the authoritative codebase and documentation:

1. **Approved Task Prompt & Acceptance Criteria:**
   * In `ORIGINAL_REQUEST.md` (lines 108–166): Day 3 requirements mandate:
     - R1: Next.js 14 App Router, Tailwind CSS, Lucide icons, Eco-Tech styling (`Space Grotesk`, `Inter`, `JetBrains Mono`, `#059669` primary emerald, semantic badges: amber for Pending, blue for In Progress, emerald for Completed, rose for Rejected).
     - R2: Login page, JWT session persistence, RBAC route protection (Admin vs User).
     - R3: `/dashboard` with 4 metric cards, category distribution (Organic, Plastic, Paper), recent activities.
     - R4: `/reports` table with keyword search, status & category filters, pagination, review modal with photo preview, AI confidence %, GPS with Google Maps link (`https://www.google.com/maps?q=lat,long`), and admin status update form with `admin_notes` via `PATCH /api/v1/reports/{id}/status`.
     - R5: `web/src/lib/api.ts` connecting via `NEXT_PUBLIC_API_URL` with Bearer injection, user profile from `GET /api/v1/auth/me`, and user management list view for admins.
     - R6: Responsive layout and clean `npm run build` with zero errors.

2. **Eco-Tech Design System & Tokens:**
   * In `docs/STYLING_GUIDE.md` (lines 13–47):
     - Primary: `primary-50` (`#ecfdf5`), `primary-500` (`#10b981`), `primary-600` (`#059669` Brand Primary), `primary-700` (`#047857`), `primary-900` (`#064e3b`).
     - Neutrals: `surface-ground` (`#f8fafc`), `surface-card` (`#ffffff`), `border-subtle` (`#e2e8f0`), `text-muted` (`#64748b`), `text-body` (`#334155`), `text-heading` (`#0f172a`).
     - Status Badges:
       - Pending: `bg-amber-50 text-amber-700 border-amber-200`
       - In Progress: `bg-blue-50 text-blue-700 border-blue-200`
       - Completed: `bg-emerald-50 text-emerald-700 border-emerald-200`
       - Rejected: `bg-rose-50 text-rose-700 border-rose-200`
     - AI Categories:
       - Organic Waste: `#16a34a` (`bg-green-100 text-green-800`)
       - Plastic Waste: `#0284c7` (`bg-sky-100 text-sky-800`)
       - Paper Waste: `#d97706` (`bg-amber-100 text-amber-800`)

3. **Backend API Endpoints & Contract Schemas:**
   * `POST /api/v1/auth/login` (`backend/app/api/v1/auth.py:94-192`): Accepts JSON or form data, returns `{ status: "success", data: { access_token, token_type: "bearer", user: { id, email, full_name, role } } }`.
   * `GET /api/v1/auth/me` (`backend/app/api/v1/auth.py:194-207`): Returns `{ status: "success", data: UserSummary }`.
   * `GET /api/v1/dashboard/stats` (`backend/app/api/v1/dashboard.py:37-109`): Admin-only (403 for non-admin). Returns `summary` (`total_reports`, `pending_count`, `in_progress_count`, `completed_count`, `rejected_count`, `completion_rate_percent`, `active_users`), `category_distribution` array, and `recent_activities` array.
   * `GET /api/v1/reports` (`backend/app/api/v1/reports.py:195-280`): Accepts `status`, `category_id`, `search`, `page`, `limit`. Returns `meta` (`total_items`, `current_page`, `total_pages`, `limit`) and `data` array with nested `category` and `reporter`.
   * `GET /api/v1/reports/{id}` (`backend/app/api/v1/reports.py:283-360`): Returns single report detail with chronological `logs` audit trail.
   * `PATCH /api/v1/reports/{id}/status` (`backend/app/api/v1/reports.py:363-436`): Admin-only. Accepts `{ status, admin_notes }`. Allowed transitions: `Pending` -> `In Progress` or `Rejected`; `In Progress` -> `Completed` or `Rejected`. Terminal states `Completed` and `Rejected` reject transitions with 400.

4. **Web Module State:**
   * `web/package.json` contains:
     - Next.js 14.2.0, React 18.2.0, Lucide-react 0.363.0, Axios 1.6.8, Tailwind CSS 3.4.3, TypeScript 5.4.0.
   * Directory `web/` currently contains only `package.json` and `README.md`. No `src/` directory exists yet.
   * Node version: `v24.12.0`, npm version: `11.5.1`.

---

## 2. Logic Chain

1. **From Acceptance Criteria to Architecture:** Day 3 requires building the web dashboard in `web/` from scratch using Next.js 14 App Router, Tailwind CSS, and Lucide icons.
2. **From API Contract to State Management:**
   - The backend is already operational and seeded with `admin@bilcode.id` (`Admin123!`) and `user@bilcode.id` (`User123!`).
   - The frontend Axios instance in `web/src/lib/api.ts` must use `NEXT_PUBLIC_API_URL` and attach the Bearer token from `localStorage` to all authenticated requests.
3. **From State Machine to UI Component Design:**
   - The report status transitions have strict rules enforced by backend (`backend/app/api/v1/reports.py:390-402`). The UI review modal (`ReportModal.tsx`) must dynamically adjust the available status options based on the current report status:
     - `Pending` $\rightarrow$ show options for `In Progress` and `Rejected`.
     - `In Progress` $\rightarrow$ show options for `Completed` and `Rejected`.
     - `Completed` / `Rejected` $\rightarrow$ lock the form and display a read-only terminal status badge.
4. **From Image Storage to Asset Display:**
   - The backend stores `image_url` as relative paths like `/uploads/reports/{filename}.jpg`.
   - The frontend must normalize relative paths to absolute URLs by prepending the backend host (e.g. `http://localhost:8000`), ensuring evidence photos render properly in the table and modal.
5. **From RBAC to Navigation & Views:**
   - Non-admin users (`role === 'user'`) will receive 403 Forbidden from `GET /api/v1/dashboard/stats`.
   - Therefore, the application navigation and routing must either hide/restrict the `/dashboard` and `/users` routes for non-admin accounts or redirect them to `/reports`.

---

## 3. Caveats

1. **User Management API:** The Day 2 backend does not currently have a dedicated `GET /api/v1/users` endpoint (only `GET /api/v1/auth/me`). For the `/users` page, the implementer can display the registered seed accounts (`admin@bilcode.id`, `user@bilcode.id`) and current session user, or implement a lightweight `GET /api/v1/users` endpoint in backend if permitted by workflow scope.
2. **Offline Font Assets:** Next.js font loading via Google Fonts (`next/font/google`) might attempt network access during build time. Using CSS variable fallbacks or standard local font declarations in `globals.css` and `tailwind.config.ts` prevents build errors if internet access is restricted or slow.

---

## 4. Conclusion

The specifications, design requirements, and backend contracts for Day 3 are completely defined, verified, and ready for scaffolding and implementation:
- Full specifications, color tokens, typography scales, formulas, component contracts, and edge cases have been compiled into `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day3_1\report.md`.
- Next steps for worker subagents:
  1. Initialize Next.js project files in `web/` (`tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`, `.env.local`).
  2. Implement `web/src/lib/api.ts` and auth session management.
  3. Implement layout shell (`Sidebar.tsx`, `Header.tsx`).
  4. Implement `/login`, `/dashboard`, `/reports` (with `ReportModal`), and `/users`.
  5. Validate production build via `npm run build`.

---

## 5. Verification Method

To independently verify all findings in this report:
1. **Inspect Documentation Files:**
   - `view_file D:\Ngoding\interviewWeb\BillcodeTech\docs\STYLING_GUIDE.md` (verify exact hex codes and typography rules).
   - `view_file D:\Ngoding\interviewWeb\BillcodeTech\docs\API_SPECS.md` (verify request/response JSON schemas).
   - `view_file D:\Ngoding\interviewWeb\BillcodeTech\docs\FLOWS.md` (verify state machine transition rules).
2. **Inspect Backend Implementation:**
   - `view_file D:\Ngoding\interviewWeb\BillcodeTech\backend\app\api\v1\dashboard.py` (verify `/dashboard/stats` calculation and fields).
   - `view_file D:\Ngoding\interviewWeb\BillcodeTech\backend\app\api\v1\reports.py` (verify `/reports` and `/reports/{id}/status` transition rules).
3. **Inspect Specification Mining Output:**
   - `view_file D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day3_1\report.md`.
