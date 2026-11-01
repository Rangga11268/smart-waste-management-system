# SWMS Web Management Dashboard

Admin and operator web portal for the Smart Waste Management System (SWMS), built with Next.js 14 (App Router) and Tailwind CSS.

---

## Features

- **Next.js 14 App Router**: Hybrid server and client components architecture.
- **Tailwind CSS & Design Tokens**: Clean, responsive layout adhering to enterprise UI standards (`Space Grotesk` headings + `Inter` body).
- **Executive Statistics & Analytics**: Live stat cards (Total Reports, Verified, Resolved, Clean Rate) and waste category breakdown charts.
- **Filterable Triage Table**: Search by report ID or citizen name, filter by status (`Pending`, `In Progress`, `Completed`, `Rejected`), and paginate through reports.
- **Interactive Review Modal**: High-resolution evidence photo preview, GPS coordinate display with mapping integration, and one-click status transitions with audit notes.
- **Role-Guarded Authentication**: Secure administrative session management with automatic redirection.

---

## Directory Structure

```
web/
├── src/
│   ├── app/                  # Next.js 14 App Router
│   │   ├── (auth)/login/     # Admin login screen
│   │   ├── (dashboard)/      # Authenticated dashboard views
│   │   │   ├── reports/      # Reports table & triage
│   │   │   ├── users/        # User management
│   │   │   └── page.tsx      # Dashboard summary & metrics
│   │   ├── layout.tsx        # Root layout with sidebar navigation
│   │   └── globals.css       # Tailwind base styles and CSS variables
│   ├── components/           # Reusable UI components
│   │   ├── StatCard.tsx      # Summary metric display cards
│   │   ├── StatusBadge.tsx   # Semantic status badges
│   │   ├── ReportModal.tsx   # Detail inspection & status update modal
│   │   └── Sidebar.tsx       # Collapsible navigation sidebar
│   └── lib/                  # Utilities & API client
│       ├── api.ts            # Axios instance with auth interceptors
│       └── utils.ts          # Formatting & styling helpers
├── package.json              # Project dependencies & scripts
├── tailwind.config.ts        # Design tokens & color palette
├── tsconfig.json             # TypeScript configuration
└── README.md                 # This guide
```

---

## Local Development

### 1. Prerequisites
- Node.js 18.17+ or 20+
- npm (or pnpm / yarn)

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Variables
Create `.env.local` in the `web/` directory:
```env
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"
```

### 4. Run Development Server
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

### 5. Build for Production
```bash
npm run build
npm run start
```

---

## Day 3 Implementation Roadmap

- Implement App Router layout with navigation sidebar.
- Connect authenticated Axios client to Backend `POST /api/v1/auth/login`.
- Render real-time dashboard cards connected to `GET /api/v1/stats`.
- Implement responsive report management table with server-side pagination and status filter.
- Build report detail drawer/modal with photo zoom and `PATCH /api/v1/reports/{id}/status`.
