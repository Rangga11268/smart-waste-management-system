# Specification Mining Report: SWMS Web Dashboard (Day 3)
**Author:** `spec_miner_day3_1`  
**Milestone:** Day 3 — Next.js 14 App Router & Tailwind CSS Web Dashboard  
**Date:** 2026-11-02  
**Target Repository:** `D:\Ngoding\interviewWeb\BillcodeTech`

---

## 1. Executive Summary & Authoritative Specification Sources

This report provides an exhaustive, ground-truth specification mining analysis for **Day 3** of the Smart Waste Management System (SWMS) technical test. All findings are derived directly from authoritative repository documentation, existing backend REST API implementations, Pydantic schemas, and database models.

### Authoritative Specification Sources Examined:
1. **`ORIGINAL_REQUEST.md`** (Day 3 section: Requirements R1–R6, Acceptance Criteria)
2. **`docs/STYLING_GUIDE.md`** (Eco-Tech design tokens, typography, semantic status badges, AI categories)
3. **`docs/TASKS.md`** (Day 3 task breakdown: 3.1 to 3.6)
4. **`docs/PRD.md`** (Functional requirements FR-WB-01 to FR-WB-06, User Personas, NFRs)
5. **`docs/SPEC.md`** (Technical architecture, code samples, boundaries, testing strategy)
6. **`docs/API_SPECS.md`** (Backend contract schemas, status codes, request/response models)
7. **`docs/FLOWS.md`** (State machine transition rules, sequence diagrams, edge case resolutions)
8. **`docs/ERD.md` & `backend/app/models/`** (Entity relational schema, field constraints)
9. **`docs/RUNBOOK.md`** (Default seed accounts, demo walk-through scripts)
10. **`backend/app/api/v1/` & `backend/app/schemas/`** (FastAPI live route logic, Pydantic models, error handlers)
11. **`web/package.json`** (Configured dependencies: Next.js 14.2.0, React 18.2.0, Tailwind 3.4.3, Lucide 0.363.0, Axios 1.6.8)

---

## 2. Eco-Tech Design System Requirements

The design system implements the **"Eco-Tech Resilience"** theme, characterized by modern emerald green accents, high contrast slate/zinc surfaces, strict anti-slop rules, and clear visual hierarchy.

### 2.1 Color Palette & Exact Tokens

| Token Name | Hex Code | Tailwind Class | Semantic Usage & Context |
| :--- | :--- | :--- | :--- |
| **Brand Primary** | | | |
| `primary-50` | `#ecfdf5` | `bg-emerald-50` / `text-emerald-50` | Subtle active navigation backgrounds, badge background |
| `primary-500` | `#10b981` | `bg-emerald-500` | Accents, floating badges, secondary green elements |
| `primary-600` | `#059669` | `bg-emerald-600` | **Core Brand Primary**: Primary CTA buttons, active sidebar state, focus rings |
| `primary-700` | `#047857` | `bg-emerald-700` | Hover states on primary action buttons |
| `primary-900` | `#064e3b` | `bg-emerald-900` | High-emphasis headings, dark green brand accents |
| **Neutral Base (Slate & Zinc)** | | | |
| `surface-ground` | `#f8fafc` | `bg-slate-50` | Main application background canvas (behind cards & tables) |
| `surface-card` | `#ffffff` | `bg-white` | Card container background, modal container, dropdown popover |
| `border-subtle` | `#e2e8f0` | `border-slate-200` | Card borders, table dividers, input borders, sidebar divider |
| `text-muted` | `#64748b` | `text-slate-500` | Field labels, timestamps, metadata captions, empty states |
| `text-body` | `#334155` | `text-slate-700` | Regular body paragraphs, table cell data, form values |
| `text-heading` | `#0f172a` | `text-slate-900` | Page titles, widget stat counts, modal headings |

### 2.2 Semantic Status Badges

Report status values have strict semantic color mappings across the application:

| Status Value | Badge Background | Badge Text | Border Color | Operational Definition & Rule |
| :--- | :--- | :--- | :--- | :--- |
| **`Pending`** | `bg-amber-50` | `text-amber-700` | `border-amber-200` | New report submitted by citizen; awaiting admin triage. |
| **`In Progress`** | `bg-blue-50` | `text-blue-700` | `border-blue-200` | Assigned; sanitation crew dispatched to location. |
| **`Completed`** | `bg-emerald-50` | `text-emerald-700` | `border-emerald-200` | Waste collected and site resolved. Terminal state. |
| **`Rejected`** | `bg-rose-50` | `text-rose-700` | `border-rose-200` | Invalid, duplicate, or unverified report. Terminal state. |

**Badge UI Implementation Spec:**
```tsx
<span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full border border-[color] bg-[color] text-[color]">
  <span className="h-1.5 w-1.5 rounded-full bg-current" />
  {status}
</span>
```

### 2.3 AI Classification Category Colors

Categories identified by the MobileNetV2 inference engine or stored in the database catalog:

| Category Name | Slug | Accent Color Hex | Badge Styling |
| :--- | :--- | :--- | :--- |
| **Organic Waste** | `organic` | `#16a34a` (Forest Emerald) | `bg-green-100 text-green-800 border-green-200` |
| **Plastic Waste** | `plastic` | `#0284c7` (Ocean Cyan/Blue) | `bg-sky-100 text-sky-800 border-sky-200` |
| **Paper Waste** | `paper` | `#d97706` (Warm Amber/Wood) | `bg-amber-100 text-amber-800 border-amber-200` |

### 2.4 Typography Hierarchy

* **Heading & Display Font:** `Space Grotesk` (Geometric sans-serif for sharp, modern Smart City branding).
* **Body, UI & Table Font:** `Inter` (High legibility for numeric tables, labels, and forms).
* **Monospace Font:** `JetBrains Mono` (Dedicated for GPS coordinates `lat, long`, Report IDs `#RPT-XXXX` / UUID, and AI confidence percentages `94.21%`).

#### Font Scale Specification:
* **Display / Stat Counts:** `font-['Space_Grotesk'] text-3xl font-bold tracking-tight text-slate-900`
* **Page Title (H1):** `font-['Space_Grotesk'] text-2xl font-bold text-slate-900`
* **Section Title (H2):** `font-['Space_Grotesk'] text-lg font-semibold text-slate-800`
* **Card Title / Subheading:** `font-['Inter'] text-sm font-medium text-slate-600`
* **Body / Table Cell:** `font-['Inter'] text-sm font-normal text-slate-700`
* **GPS & IDs (Mono):** `font-mono text-xs font-medium text-slate-500`
* **Caption / Timestamp:** `text-xs font-medium text-slate-400`

### 2.5 Anti-Slop & UI Quality Standards
* ❌ **Forbidden:** Cheap glassmorphism, muddy low-contrast text, chaotic emojis in formal enterprise headings, unconstrained page overflow.
* ✅ **Required:** Crisp SVG icons (`lucide-react`), tactile micro-badges with smooth radii (`rounded-full` or `rounded-md`), structured loading skeletons (`animate-pulse bg-slate-200`), and accessible focus states.

---

## 3. Navigation Shell & Application Layout

### 3.1 Overall Layout Structure
* **Container:** Full-viewport dashboard layout (`min-h-screen bg-slate-50 flex flex-col md:flex-row`).
* **Sidebar:** Fixed width `w-64` on desktop (`hidden md:flex flex-col bg-white border-r border-slate-200`), with collapsible mobile slide-out drawer triggered by hamburger button.
* **Top Header:** Fixed or sticky height `h-16`, `bg-white border-b border-slate-200 px-6 flex items-center justify-between`.
* **Main Content Area:** Scrollable viewport container (`flex-1 p-6 md:p-8 overflow-y-auto max-w-7xl mx-auto w-full`).

### 3.2 Sidebar Elements
1. **Brand Header:**
   * SWMS Logo icon (e.g. `Recycle` or `Leaf` in emerald-600).
   * Title: **SWMS Admin** (`font-['Space_Grotesk'] font-bold text-slate-900`).
   * Version Badge: `v1.0.0` (`bg-emerald-50 text-emerald-700 text-[10px] px-1.5 py-0.5 rounded font-mono`).
2. **Navigation Menu Items:**
   * 📊 **Dashboard Overview** (`/dashboard`) — Lucide `LayoutDashboard` or `BarChart3`
   * 📋 **Laporan Sampah** (`/reports`) — Lucide `ClipboardList` or `FileText`
   * 👥 **Manajemen Pengguna** (`/users`) — Lucide `Users` (Admin only)
   * ⚙️ **API Documentation** (`http://localhost:8000/docs`) — Lucide `BookOpen` or `ExternalLink` (Opens backend Swagger UI in new tab)
3. **Active Navigation State:**
   * Style: `bg-emerald-50 text-emerald-700 font-medium border-r-2 border-emerald-600` (or `bg-emerald-600 text-white rounded-lg`).
4. **User Profile Quick Footer:**
   * Current user avatar initials (e.g., "SA" for Super Admin).
   * User full name & role tag (`admin` or `user`).
   * Sign Out button (`LogOut` icon) triggering session clearance.

### 3.3 Top Header Elements
* **Breadcrumbs / Current Page Indicator:** Displays current hierarchy (e.g., `Beranda / Laporan Sampah`).
* **Backend Status Health Indicator:**
   * Live ping to `GET /api/v1/health` or `GET /health`.
   * Display: Green pulse dot with text `API Online` or red dot `API Offline`.
* **User Profile & Quick Actions:**
   * Current authenticated user pill.
   * Logout button with confirmation or instant token revocation.

---

## 4. Authentication, Session Management & RBAC

### 4.1 Login Screen (`/login`)
* **Layout:** Centered card on a clean `bg-slate-50` background.
* **Branding:** Eco-Tech logo, "Smart Waste Management System", and prompt "Masuk ke Dashboard Operasional".
* **Form Inputs:**
  1. `Email`: Input type `email`, placeholder `admin@bilcode.id`, required validation.
  2. `Password`: Input type `password`, required validation.
* **Quick Credential Fill Buttons (Developer / Evaluator Convenience):**
  * Admin Preset: Fills `admin@bilcode.id` / `Admin123!`
  * User Preset: Fills `user@bilcode.id` / `User123!`
* **Submission Handling:**
  * Dispatches `POST /api/v1/auth/login` with `{ email, password }`.
  * On `200 OK`:
    * Extracts `data.access_token` and `data.user` (`id, email, full_name, role`).
    * Persists `access_token` and user session to `localStorage` (and/or cookies for SSR compatibility).
    * Configures Axios default `Authorization` header.
    * Redirects to `/dashboard` (for admin) or `/reports`.
  * On Error:
    * `401 Unauthorized`: Displays "Email atau kata sandi tidak valid."
    * `422 Unprocessable Entity`: Displays "Format email atau sandi tidak lengkap."
    * Network Error: Displays "Gagal terhubung ke backend server di http://localhost:8000."

### 4.2 Role-Based Access Control (RBAC) Matrix

| Route / Resource | Citizen (`user`) | Administrator (`admin`) | Unauthenticated Guest |
| :--- | :--- | :--- | :--- |
| `/login` | Can view; if already logged in, redirects to app | Can view; if logged in, redirects to `/dashboard` | Allowed |
| `/dashboard` | **Forbidden** (Backend `GET /dashboard/stats` returns 403; UI shows access denied or redirects to `/reports`) | **Full Access** (View stats, charts, logs) | Redirects to `/login` |
| `/reports` | **Read Access** (Can view reports list & detail) | **Full Access** (View reports, open modal, update status) | Redirects to `/login` |
| `PATCH /reports/{id}/status` | **Forbidden** (HTTP 403) | **Allowed** (`Pending`->`In Progress`/`Rejected`, `In Progress`->`Completed`/`Rejected`) | HTTP 401 |
| `/users` | **Forbidden** (Hidden from menu, blocked) | **Full Access** (View registered users list) | Redirects to `/login` |

### 4.3 Route Guard Implementation
* Client-side auth wrapper / hook (`useAuth` or `AuthProvider`) checks token existence.
* If no token is present when visiting `/dashboard`, `/reports`, or `/users` $\rightarrow$ Redirect immediately to `/login`.
* Validates session freshness via `GET /api/v1/auth/me`. If `401 Unauthorized` is returned $\rightarrow$ Clear stored token and redirect to `/login`.

---

## 5. Dashboard Page Specification (`/dashboard`)

* **Target URL:** `/dashboard`
* **Data Source:** `GET /api/v1/dashboard/stats` (Requires Admin Bearer token).
* **Expected Response Shape:**
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
        { "category": "Organic Waste", "count": 64, "percentage": 45.07 },
        { "category": "Plastic Waste", "count": 52, "percentage": 36.62 },
        { "category": "Paper Waste", "count": 26, "percentage": 18.31 }
      ],
      "recent_activities": [
        {
          "report_id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
          "action": "Status changed to In Progress",
          "timestamp": "2026-11-01T13:00:00Z"
        }
      ]
    }
  }
  ```

### 5.1 Primary Stat Cards (4 Top Widgets)
1. **Total Laporan Masuk:**
   * Metric: `summary.total_reports`
   * Icon: Lucide `FileText` or `Inbox`
   * Accent: Slate-800
   * Subtitle: "Semua laporan yang tercatat di sistem"
2. **Perlu Validasi (`Pending`):**
   * Metric: `summary.pending_count`
   * Icon: Lucide `Clock` or `AlertCircle`
   * Accent: Amber-600 (`bg-amber-50 text-amber-700 border-amber-200`)
   * Subtitle: "Menunggu peninjauan petugas"
3. **Sedang Ditangani (`In Progress`):**
   * Metric: `summary.in_progress_count`
   * Icon: Lucide `Truck` or `Activity`
   * Accent: Blue-600 (`bg-blue-50 text-blue-700 border-blue-200`)
   * Subtitle: "Armada kebersihan di lapangan"
4. **Tingkat Penyelesaian (`Completion Rate`):**
   * Metric: `${summary.completion_rate_percent}%`
   * Icon: Lucide `CheckCircle2`
   * Accent: Emerald-600 (`bg-emerald-50 text-emerald-700 border-emerald-200`)
   * Formula: `(completed_count / total_reports) * 100` (or `0.0%` if `total_reports == 0`)
   * Subtitle: `${summary.completed_count} dari ${summary.total_reports} laporan tuntas`

### 5.2 Waste Category Distribution Section
* **Breakdown Metrics:**
  * Organic Waste: Count, Percentage, bar meter in `#16a34a` (green)
  * Plastic Waste: Count, Percentage, bar meter in `#0284c7` (sky/blue)
  * Paper Waste: Count, Percentage, bar meter in `#d97706` (amber)
* **Visual Presentation:**
  * Segmented progress bar showing the proportional distribution of each category.
  * Category legend with count badges, percentages, and indicator chips.

### 5.3 Recent Activity Stream
* Renders items from `recent_activities`:
  * Action description (e.g., "Status changed to In Progress", "Report created (Pending)").
  * Report UUID (truncated with copy button).
  * Relative timestamp (e.g., "5 menit lalu", formatted with date-fns or native `Intl.RelativeTimeFormat`).

---

## 6. Reports Management & Review Modal (`/reports`)

* **Target URL:** `/reports`
* **Data Source:** `GET /api/v1/reports`
* **Query Parameters Supported:**
  * `status`: `Pending | In Progress | Completed | Rejected`
  * `category_id`: `1 | 2 | 3`
  * `search`: string keyword (searches across title, description, address_note)
  * `page`: integer (default: 1)
  * `limit`: integer (default: 10)

### 6.1 Interactive Table Specification
* **Columns:**
  1. **ID:** Short formatted ID (e.g., `#RPT-` + first 8 characters of UUID in `font-mono text-xs`).
  2. **Thumbnail:** Rounded image thumbnail (`w-12 h-12 object-cover rounded-lg border border-slate-200`). Prefixed with backend URL if relative path (`http://localhost:8000/uploads/...`).
  3. **Judul & Catatan:** Title in `font-medium text-slate-900` + optional landmark/address note in `text-xs text-slate-500`.
  4. **Kategori:** Category chip with category badge color (`#16a34a`, `#0284c7`, or `#d97706`).
  5. **Pelapor:** Full name of citizen reporter (`reporter.full_name`).
  6. **Lokasi GPS:** Latitude & Longitude in `font-mono text-xs text-slate-600`.
  7. **Tanggal:** Formatted creation date (e.g. `02 Nov 2026, 14:30`).
  8. **Status:** Semantic `StatusBadge` component (`Pending`, `In Progress`, `Completed`, `Rejected`).
  9. **Aksi:** Action button "Tinjau" / "Detail" (Lucide `Eye` icon).

### 6.2 Filter & Search Bar
* **Keyword Search:** Input with Lucide `Search` icon; debounced (300ms) to prevent query spamming. Searches across title, description, and address note.
* **Status Filter Dropdown:** Options: `Semua Status`, `Pending`, `In Progress`, `Completed`, `Rejected`.
* **Category Filter Dropdown:** Options: `Semua Kategori`, `Organic Waste (1)`, `Plastic Waste (2)`, `Paper Waste (3)`.
* **Reset Filters Button:** Resets all parameters to initial page 1.

### 6.3 Pagination Controls
* Displays: `Menampilkan (page-1)*limit + 1 hingga min(page*limit, total_items) dari total_items laporan`.
* Buttons: "Sebelumnya" (`page - 1`, disabled if `current_page === 1`), "Selanjutnya" (`page + 1`, disabled if `current_page === total_pages`).
* Page number indicators with active styling on `current_page`.

### 6.4 Review Modal Component (`ReportModal`)
Triggered when an operator clicks "Tinjau" on any report record. Can optionally fetch detailed report data from `GET /api/v1/reports/{id}` to load the audit trail.

**Modal Sub-Components:**
1. **Header:** Title, report ID in `font-mono`, and close button (`X` icon).
2. **Photo Preview:** High-resolution image preview with full width/aspect ratio container, with fallback placeholder if image load fails.
3. **AI Classification Badge:**
   * Category Detected: e.g. "Terdeteksi: Plastic Waste".
   * AI Confidence: Formatted percentage (e.g. `ai_confidence * 100` -> `94.21%` in `font-mono font-semibold`).
4. **Geolocation & Map Link:**
   * Coordinates: `Latitude: {lat}, Longitude: {long}` in `font-mono`.
   * Address / Landmark Note: e.g. "Di sebelah warung mie ayam".
   * Clickable Button / Link: **Buka di Google Maps** (`https://www.google.com/maps?q={latitude},{longitude}` target="_blank" rel="noopener noreferrer").
5. **State Machine Disposition Form (Admin Only):**
   * **Current Status:** Displays existing status badge.
   * **Allowed Status Transitions:**
     * If `Pending`: Options to transition to `In Progress` or `Rejected`.
     * If `In Progress`: Options to transition to `Completed` or `Rejected`.
     * If `Completed` or `Rejected`: Shows notification "Laporan telah selesai/ditutup (Status Terminal). Tidak dapat diubah lagi." Form inputs are disabled.
   * **Admin Notes Field:** Textarea for disposition / field remarks (e.g. "Armada truk #3 dikerahkan ke lokasi").
   * **Action Submit Button:** Executes `PATCH /api/v1/reports/{id}/status` with payload:
     ```json
     {
       "status": "In Progress",
       "admin_notes": "Armada truk #3 dikerahkan"
     }
     ```
   * **Feedback & Live Update:**
     * Submitting shows loading spinner on button.
     * On success: Displays toast or alert, updates report status in parent table without requiring full page reload, and appends to audit log list.
     * On error (400, 403, 404): Displays backend error message.
6. **Audit Trail History Timeline:**
   * List of historical transitions from `report.logs`:
     * Previous Status $\rightarrow$ New Status
     * Remarks / Notes
     * Timestamp (formatted date/time)

---

## 7. User Management Specification (`/users`)

* **Target URL:** `/users`
* **Access Scope:** Admin role only (`role === 'admin'`).
* **Requirements:**
  1. Displays registered system users.
  2. Columns: Avatar/Initials, Full Name, Email, Phone Number, Role (`Admin` vs `User`), Status (`Aktif` vs `Nonaktif`), Created At.
  3. Role Indicators:
     * `Admin`: Emerald / Purple badge (`bg-emerald-100 text-emerald-800` or `bg-purple-100 text-purple-800`).
     * `User`: Slate / Blue badge (`bg-slate-100 text-slate-800`).
  4. Status Indicators:
     * Active (`is_active === true`): Green dot badge `Aktif`.
  5. Search / Filter: Filter by name or email.
  6. **Data Source Integration:**
     * Note from Backend Inspection: The Day 2 backend has `GET /api/v1/auth/me` and seed accounts (`admin@bilcode.id`, `user@bilcode.id`). If no generic `GET /api/v1/users` endpoint is added to backend, the web client should display the registered seed accounts and current session profile, with seamless support for a users endpoint if present.

---

## 8. Technical & Build Constraints

### 8.1 Next.js 14 App Router Directory Conventions
The web application must be structured in `web/`:
```text
web/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx        # Client login form
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx          # Authenticated shell layout (Sidebar + Header)
│   │   │   ├── page.tsx            # Redirects to /dashboard
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx        # Stats cards, charts, recent activities
│   │   │   ├── reports/
│   │   │   │   └── page.tsx        # Reports master table, search, filters, review modal
│   │   │   └── users/
│   │   │       └── page.tsx        # User management list view
│   │   ├── layout.tsx              # Root HTML & body layout with font imports
│   │   ├── globals.css             # Tailwind base styles, font-family declarations
│   │   └── not-found.tsx           # 404 page
│   ├── components/
│   │   ├── Sidebar.tsx             # Collapsible navigation sidebar
│   │   ├── Header.tsx              # Top bar with user profile & status
│   │   ├── StatCard.tsx            # Reusable metric card
│   │   ├── StatusBadge.tsx         # Semantic status indicator
│   │   ├── ReportModal.tsx         # Review modal with photo preview & disposition
│   │   └── CategoryChart.tsx       # Waste category distribution visualization
│   └── lib/
│       ├── api.ts                  # Axios client with interceptors
│       ├── auth.ts                 # Auth context / token management
│       └── utils.ts                # Date formatting, class merge (clsx + twMerge)
├── tailwind.config.ts              # Eco-Tech design tokens & custom colors
├── tsconfig.json                   # Strict TypeScript compiler options
├── package.json                    # Dependencies & scripts
└── .env.local                      # NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
```

### 8.2 API Client Configuration (`web/src/lib/api.ts`)
* Configured using `NEXT_PUBLIC_API_URL` (default fallback: `http://localhost:8000/api/v1`).
* Request Interceptor: Automatically inspects `localStorage.getItem('token')` or cookies and attaches:
  `Authorization: Bearer <token>`
* Response Interceptor: Catches `401 Unauthorized` responses and triggers redirect to `/login` after clearing expired token.
* Handles image URL normalization:
  ```ts
  export const getFullImageUrl = (path: string): string => {
    if (!path) return '/placeholder.png';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    const backendOrigin = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1').replace(/\/api\/v1\/?$/, '');
    return `${backendOrigin}${path.startsWith('/') ? '' : '/'}${path}`;
  };
  ```

### 8.3 Tailwind CSS Theme Configuration (`tailwind.config.ts`)
Must register custom font families and colors:
```ts
theme: {
  extend: {
    fontFamily: {
      sans: ['var(--font-inter)', 'Inter', 'sans-serif'],
      display: ['var(--font-space-grotesk)', 'Space Grotesk', 'sans-serif'],
      mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'monospace'],
    },
    colors: {
      primary: {
        50: '#ecfdf5',
        500: '#10b981',
        600: '#059669',
        700: '#047857',
        900: '#064e3b',
      },
    },
  },
}
```

### 8.4 Quality Gates & Production Build
* **TypeScript:** Strict type checking (`tsc --noEmit`).
* **ESLint:** Passing clean with Next.js standard config (`next lint`).
* **Production Build:** `npm run build` must complete with zero errors and generate static/server route manifests.

---

## 9. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Design System | Eco-Tech Color Palette | Semantic colors: Emerald `#059669`, Neutral Slate `#f8fafc`, Borders `#e2e8f0` | Tailwind classes | CSS variables & styles | Fallback to Tailwind default colors | `docs/STYLING_GUIDE.md` |
| 2 | Design System | Typography Hierarchy | Space Grotesk (headings), Inter (body/tables), JetBrains Mono (GPS/IDs) | Text elements | Styled typography | Default system fonts if unlinked | `docs/STYLING_GUIDE.md` |
| 3 | Design System | Semantic Status Badges | Color-coded badges: Amber (Pending), Blue (In Progress), Emerald (Completed), Rose (Rejected) | `status: string` | Styled pill badge with status dot | Fallback neutral badge | `docs/STYLING_GUIDE.md`, `docs/SPEC.md` |
| 4 | Design System | Category Accent Badges | Color-coded chips for Organic (`#16a34a`), Plastic (`#0284c7`), Paper (`#d97706`) | `category_name` or `category_id` | Styled category tag | Fallback gray tag | `docs/STYLING_GUIDE.md` |
| 5 | Navigation | Responsive Shell & Sidebar | Fixed desktop sidebar (`w-64`), hamburger drawer for mobile/tablet | Viewport size, toggle state | Responsive navigation layout | Overflow prevented | `docs/STYLING_GUIDE.md`, `docs/SPEC.md` |
| 6 | Navigation | Header with User & Health | Displays page breadcrumb, API online indicator, user avatar and logout | User session, `/health` ping | Interactive header | Shows "API Offline" if ping fails | `docs/STYLING_GUIDE.md`, `backend/app/main.py` |
| 7 | Authentication | User Login Screen | Centered card form accepting email & password with test presets | `email`, `password` | JWT token, user object | 401 on invalid credentials, 422 on empty | `docs/API_SPECS.md`, `backend/app/api/v1/auth.py` |
| 8 | Authentication | Token Storage & Persistence | Store JWT access token in `localStorage` and attach Bearer header | `access_token` string | Persistent session across refreshes | Session cleared on 401 | `docs/SPEC.md`, `docs/TASKS.md` |
| 9 | Authentication | User Profile Display | Fetches and displays current user metadata from `GET /api/v1/auth/me` | Bearer token | User ID, email, name, role | 401 redirects to `/login` | `docs/API_SPECS.md`, `backend/app/api/v1/auth.py` |
| 10 | RBAC | Route Protection Guard | Protects admin-only routes (`/dashboard`, `/reports`, `/users`) | User role from token / `/me` | Allowed route or redirect | Non-admin blocked from admin-only pages | `docs/FLOWS.md`, `docs/TASKS.md` |
| 11 | Dashboard | Primary Metric Cards | 4 top cards: Total Reports, Pending, In Progress, Completion Rate % | `GET /api/v1/dashboard/stats` | 4 summary metric widgets | Shows 0 or skeleton on load failure | `docs/API_SPECS.md`, `backend/app/api/v1/dashboard.py` |
| 12 | Dashboard | Category Distribution Chart | Breakdown visualization of Organic, Plastic, and Paper waste | `category_distribution` array | Progress meters, counts, % | Displays 0% if total is 0 | `docs/API_SPECS.md`, `backend/app/api/v1/dashboard.py` |
| 13 | Dashboard | Recent Activity Audit Stream | Audit log feed showing latest status updates and created reports | `recent_activities` array | Activity list with timestamps | Shows empty state if no activity | `docs/API_SPECS.md`, `backend/app/api/v1/dashboard.py` |
| 14 | Reports Table | Paginated Master Table | Displays reports with thumbnails, title, category, reporter, GPS, date, status | `GET /api/v1/reports?page=&limit=` | Rendered table rows & pagination | Empty table if no records | `docs/API_SPECS.md`, `backend/app/api/v1/reports.py` |
| 15 | Reports Filter | Multi-Criteria Filtering | Filter reports by status dropdown and category dropdown | `status`, `category_id` params | Filtered reports query | Resets to page 1 on filter change | `docs/API_SPECS.md`, `backend/app/api/v1/reports.py` |
| 16 | Reports Search | Debounced Keyword Search | Searches keywords across report title, description, and address note | `search` query string | Live filtered results matching term | Returns 0 items if no match | `docs/API_SPECS.md`, `backend/app/api/v1/reports.py` |
| 17 | Review Modal | Photo Evidence Preview | High-resolution photo preview of reported waste with image fallback | `image_url` | Rendered image container | Placeholder if image not found | `docs/PRD.md`, `docs/FLOWS.md` |
| 18 | Review Modal | AI Detection Confidence Badge | Displays auto-detected category and confidence percentage | `detected_category`, `ai_confidence` | Styled badge with % in JetBrains Mono | Shows 0.0% if confidence missing | `docs/PRD.md`, `docs/API_SPECS.md` |
| 19 | Review Modal | Geolocation & Google Maps Link | Displays lat/long and direct link `https://www.google.com/maps?q=lat,long` | `latitude`, `longitude` | Coordinates + clickable external button | Button opens new tab | `ORIGINAL_REQUEST.md`, `docs/FLOWS.md` |
| 20 | Review Modal | Status Transition Form | Allows Admin to transition report status (`Pending` -> `In Progress`/`Rejected`, etc.) | `status`, `admin_notes` | Updated status & audit log entry | 400 if invalid transition or terminal | `docs/FLOWS.md`, `backend/app/api/v1/reports.py` |
| 21 | Review Modal | Audit Trail History View | Chronological list of status changes with previous/new status and notes | `report.logs` array | Visual audit timeline | Shows initial submission if no changes | `docs/ERD.md`, `backend/app/api/v1/reports.py` |
| 22 | User Management | Registered Users List | Administrative view of system users with roles and active status | Seed data / `/auth/me` | Table of users with badges | Access restricted to Admin role | `docs/PRD.md`, `ORIGINAL_REQUEST.md` |
| 23 | Build System | Next.js 14 Production Build | Optimized production compilation (`npm run build`) | Source code in `web/` | Production bundle in `web/.next` | 0 errors required | `web/package.json`, `docs/SPEC.md` |

---

## 10. Edge Cases & Boundary Behaviors

| # | Feature | Input / Scenario | Observed / Required Behavior |
|---|---------|------------------|------------------------------|
| 1 | Dashboard Stats | `total_reports == 0` (Empty database) | `completion_rate_percent` returns `0.0` (zero-division guarded in backend). UI displays `0.0%` without crashing or NaN. |
| 2 | Dashboard Stats | Non-admin (`user@bilcode.id`) attempts to fetch `/dashboard/stats` | Backend responds with `403 Forbidden`. Frontend catches error and redirects citizen to `/reports` or shows access denied banner. |
| 3 | Dashboard Stats | Unauthenticated visitor accesses `/dashboard` | Backend returns `401 Unauthorized`. Frontend auth guard redirects immediately to `/login`. |
| 4 | Status Transition | Admin attempts direct transition `Pending` $\rightarrow$ `Completed` | Backend rejects with HTTP 400 (`Invalid status transition from Pending to Completed`). UI restricts select options to `In Progress` and `Rejected`. |
| 5 | Status Transition | Admin attempts to transition a `Completed` or `Rejected` report | Backend rejects with HTTP 400 (`Report is already in terminal state`). UI disables update form and renders "Status Terminal" notice. |
| 6 | Status Transition | Admin updates status to `Completed` | Backend sets `resolved_at` to current UTC timestamp and records `ReportLog`. UI updates badge to emerald `Completed`. |
| 7 | Reports Search | Search query with special characters or no matches | Backend executes parameterized ILIKE query and returns `total_items: 0, data: []`. UI renders empty state card: "Tidak ada laporan yang cocok". |
| 8 | Reports Pagination | Out-of-bounds page request (e.g. `page: 999` with 10 total items) | Backend returns `total_items: 10, data: []`. UI shows empty page with option to return to page 1. |
| 9 | Reports Table | Relative `image_url` returned from backend (e.g. `/uploads/reports/abc.jpg`) | Frontend utility prepends `http://localhost:8000` so image renders correctly instead of 404ing against Next.js host. |
| 10 | Review Modal | Report has missing or null `admin_notes` | UI displays "Tidak ada catatan disposisi" or placeholder text without throwing undefined errors. |
| 11 | Review Modal | Report has `ai_confidence: null` or `0.0` | UI displays `0.00%` or "Manual Tagged" badge in JetBrains Mono. |
| 12 | Navigation Shell | Screen resized to mobile width (< 768px) | Sidebar automatically collapses into off-canvas drawer; hamburger toggle appears in header; table enables horizontal scroll container. |
| 13 | Token Persistence | User closes and reopens browser tab | Token retrieved from `localStorage`; `GET /api/v1/auth/me` validates session; user stays logged in without re-authenticating. |
| 14 | Session Expiry | Stored JWT token expires (after 24 hours) | Backend returns `401 Unauthorized`. Axios interceptor catches 401, clears `localStorage`, and redirects to `/login` with notification. |

---

## 11. Day 3 Verification & Acceptance Matrix

| Item | Requirement | Verification Method |
| :--- | :--- | :--- |
| **V1** | Eco-Tech Typography configured | Check `tailwind.config.ts` and `globals.css` for `Space Grotesk`, `Inter`, `JetBrains Mono`. |
| **V2** | Exact color hex codes implemented | Verify `#059669` primary and semantic status badge classes (`bg-amber-50`, `bg-blue-50`, `bg-emerald-50`, `bg-rose-50`). |
| **V3** | Auth & Session Flow | Test login with `admin@bilcode.id` / `Admin123!` and `user@bilcode.id` / `User123!`. Check token in `localStorage`. |
| **V4** | RBAC Route Protection | Verify unauthenticated redirect to `/login` and non-admin restriction on `/dashboard` and `/users`. |
| **V5** | Dashboard Stats Rendering | Confirm 4 metric cards, category distribution meters, and recent activity logs match `GET /api/v1/dashboard/stats`. |
| **V6** | Reports Table CRUD & Filter | Test keyword search debounce, status dropdown, category dropdown, and pagination against backend `/api/v1/reports`. |
| **V7** | Review Modal & Status Transition | Open modal, verify evidence photo, AI confidence %, Google Maps link (`maps.google.com/?q=lat,long`), execute `PATCH` to update status. |
| **V8** | Production Build Quality Gate | Run `npm run build` inside `web/` to confirm zero compilation, TypeScript, or lint errors. |

---
*Report generated and verified by `spec_miner_day3_1`.*
