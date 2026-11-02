# Web Frontend Environment & Scaffolding Investigation Report

**Subagent**: `explorer_web_env_1`  
**Date**: 2026-11-02  
**Target Path**: `D:\Ngoding\interviewWeb\BillcodeTech\web`  
**Related Documents**: `docs/STYLING_GUIDE.md`, `docs/API_SPECS.md`, `docs/RUNBOOK.md`, `ORIGINAL_REQUEST.md` (Day 3)

---

## Executive Summary

The `web/` module is intended to serve as the **Smart Waste Management System (SWMS) Web Dashboard** for Admins and Operators, implemented using **Next.js 14 (App Router)** and **Tailwind CSS** under the **Eco-Tech Resilience** design system.

Currently, `web/` contains only `package.json` and a documentation `README.md`. No `node_modules`, configuration files (`tsconfig.json`, `next.config.mjs`, `tailwind.config.ts`, `postcss.config.js`), or source files (`src/`) exist yet.
An `npm install --dry-run` was executed against the local Node v24.12.0 / npm 11.5.1 runtime and successfully resolved all 432 dependencies in 28 seconds with zero peer dependency conflicts. Google Fonts endpoints for `Space Grotesk`, `Inter`, and `JetBrains Mono` were verified to be online and reachable (HTTP 200).

Below is the detailed technical assessment and architectural blueprint for Milestone 1 (M1) scaffolding and Milestone 3 (M3) implementation.

---

## 1. Environment & Package Assessment

### 1.1 Node.js & Toolchain Runtime
- **Node.js**: `v24.12.0` (Active LTS / Current)
- **npm**: `11.5.1`
- **npx**: `11.5.1`
- **Registry Connectivity**: `npm ping` responded in `408ms` to `https://registry.npmjs.org/`.

### 1.2 Existing Dependencies in `web/package.json`

```json
{
  "dependencies": {
    "axios": "^1.6.8",
    "clsx": "^2.1.0",
    "lucide-react": "^0.363.0",
    "next": "^14.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwind-merge": "^2.2.2"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "autoprefixer": "^10.4.19",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.0",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.0"
  }
}
```

### 1.3 Dependency Resolution Analysis
- Running `npm install --dry-run` in `web/` resolved:
  - `next`: `14.2.35`
  - `react`: `18.3.1`
  - `react-dom`: `18.3.1`
  - `tailwindcss`: `3.4.19`
  - `lucide-react`: `0.363.0`
  - `axios`: `1.21.0`
  - `clsx`: `2.1.1`
  - `tailwind-merge`: `2.6.1`
  - `typescript`: `5.9.3`
  - Total packages: `432 packages` added cleanly with zero peer dependency errors.

### 1.4 Missing / Optional Package Analysis (Charts & Visualization)
- **Chart Library (`recharts`)**:
  - `recharts` is currently **not** present in `package.json`.
  - Checking `recharts` peer dependencies confirmed compatibility with React 18 (`^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0`).
  - **Senior Dev / Anti-Slop Recommendation**:
    - The backend endpoint `GET /api/v1/dashboard/stats` pre-calculates both `count` and `percentage` for each category (`Organic Waste`, `Plastic Waste`, `Paper Waste`).
    - Building clean, responsive progress/distribution bars using native Tailwind CSS and lightweight SVG requires **zero additional dependencies**, eliminates Next.js 14 App Router SSR hydration mismatches, avoids canvas sizing issues on mobile, and adds 0 KB to the client bundle.
    - If interactive charts (such as donut or bar charts) are explicitly desired, `recharts` can be installed without conflicts; however, native Tailwind progress cards are faster, more reliable, and directly satisfy all Acceptance Criteria in `ORIGINAL_REQUEST.md`.

---

## 2. Build & Dev Script Execution Assessment

### 2.1 Existing Scripts in `web/package.json`
- `"dev": "next dev"`
- `"build": "next build"`
- `"start": "next start"`
- `"lint": "next lint"`

### 2.2 Execution Test
- Invoking `npm run build` in `web/` resulted in:
  ```
  'next' is not recognized as an internal or external command, operable program or batch file.
  Exit code: 1
  ```
  *Reason*: `web/node_modules` does not exist yet. Running `npm install` inside `web/` is required before any Next.js commands can execute.

### 2.3 Script Recommendations for M1
Add the following convenience script to `package.json`:
- `"typecheck": "tsc --noEmit"` — Enables rapid TypeScript contract validation without generating build artifacts, ideal for CI and pre-commit checks.

---

## 3. Font Loading Capabilities in Next.js 14

### 3.1 Styling Guide Requirements (`docs/STYLING_GUIDE.md`)
- **Heading & Display Font**: `Space Grotesk` (Geometric sans-serif)
- **Body, UI & Table Font**: `Inter` (Neo-grotesque)
- **Monospace Font**: `JetBrains Mono` (GPS coordinates, Report IDs, confidence metrics)

### 3.2 Connectivity Test
Network requests directly from the current host to Google Fonts CDN:
- `Inter` (`https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap`): **HTTP 200 OK**
- `Space Grotesk` (`https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap`): **HTTP 200 OK**
- `JetBrains Mono` (`https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap`): **HTTP 200 OK**

### 3.3 Next.js 14 Implementation Pattern
Use `next/font/google` in `web/src/app/layout.tsx` to define CSS variables:
```tsx
import { Inter, Space_Grotesk, JetBrains_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});
```

### 3.4 Offline & Resilient Fallback Strategy
If Next.js builds run in air-gapped CI/CD environments or environments with flaky external DNS:
Configure Tailwind `fontFamily` with comprehensive system fallback stacks:
```ts
fontFamily: {
  heading: ['var(--font-space-grotesk)', 'Space Grotesk', 'system-ui', 'sans-serif'],
  sans: ['var(--font-inter)', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
  mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'Consolas', 'Courier New', 'monospace'],
}
```
This ensures zero typography breakage even if Google Fonts download is bypassed or blocked.

---

## 4. Configuration Gaps to Resolve in M1

| Missing Item | Impact | Required Remediation |
|:---|:---|:---|
| **`node_modules`** | Cannot run `npm run dev`, `build`, or `lint` | Run `npm install` inside `web/` |
| **`tsconfig.json`** | TypeScript compiler and Next.js path aliases (`@/*`) undefined | Create standard Next.js 14 `tsconfig.json` with `@/* -> ./src/*` |
| **`next.config.mjs`** | Missing image domain configuration for backend uploads | Create `next.config.mjs` configuring `images.remotePatterns` for `http://localhost:8000/uploads/**` (or `unoptimized: true`) |
| **`postcss.config.js`** | Tailwind CSS cannot compile without PostCSS plugins | Create standard `postcss.config.js` declaring `tailwindcss` and `autoprefixer` |
| **`tailwind.config.ts`** | Eco-Tech color tokens, custom fonts, and content scanning paths undefined | Create `tailwind.config.ts` mapped to `docs/STYLING_GUIDE.md` specifications |
| **`.env.local`** | Frontend cannot resolve backend API URL | Create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| **`src/` Directory** | No application scaffolding | Create `src/app/`, `src/components/`, `src/lib/` |

---

## 5. Recommended Architecture & Implementation Blueprint

### 5.1 Project Directory Structure

```
web/
├── .env.local                    # Environment configuration
├── .gitignore
├── next.config.mjs               # Image remote patterns & Next.js settings
├── package.json
├── postcss.config.js             # PostCSS with tailwindcss & autoprefixer
├── tailwind.config.ts            # Eco-Tech design tokens & typography
├── tsconfig.json                 # TypeScript path aliases (@/*)
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx      # Admin & Operator login screen
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx        # Authenticated shell layout (Sidebar + Header)
│   │   │   ├── page.tsx          # Default redirect to /dashboard
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx      # Executive Metrics & Category Distribution
│   │   │   ├── reports/
│   │   │   │   └── page.tsx      # Filterable Reports Table & Review Modal
│   │   │   └── users/
│   │   │       └── page.tsx      # Registered Users list (Admin view)
│   │   ├── favicon.ico
│   │   ├── globals.css           # Tailwind directives & CSS base styling
│   │   └── layout.tsx            # Root layout with fonts & metadata
│   ├── components/
│   │   ├── CategoryBadge.tsx     # Organic, Plastic, Paper colored badges
│   │   ├── CategoryDistribution.tsx # Visual progress breakdown
│   │   ├── Header.tsx            # Top bar with API status & user profile
│   │   ├── LoadingSkeleton.tsx   # Loading placeholder states
│   │   ├── Pagination.tsx        # Next/Prev table pagination
│   │   ├── ReportModal.tsx       # Photo zoom, AI tag, GPS map link, status update
│   │   ├── ReportsTable.tsx      # Paginated, filterable table
│   │   ├── Sidebar.tsx           # Eco-Tech navigation sidebar
│   │   ├── StatCard.tsx          # 4 summary metric cards
│   │   └── StatusBadge.tsx       # Pending, In Progress, Completed, Rejected
│   └── lib/
│       ├── api.ts                # Axios instance with Bearer interceptors & API helpers
│       ├── types.ts              # TypeScript interfaces matching backend models
│       └── utils.ts              # cn() merge utility, date formatting, badge mappers
```

### 5.2 Exact Configuration Code Specs

#### `web/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

#### `web/postcss.config.js`
```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

#### `web/next.config.mjs`
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true, // Guarantees local / backend image preview without external domain rejection
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
```

#### `web/tailwind.config.ts`
```ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfdf5',
          500: '#10b981',
          600: '#059669', // Eco-Tech Brand Primary
          700: '#047857',
          900: '#064e3b',
        },
      },
      fontFamily: {
        heading: ['var(--font-space-grotesk)', 'Space Grotesk', 'system-ui', 'sans-serif'],
        sans: ['var(--font-inter)', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};
export default config;
```

#### `web/src/lib/utils.ts`
```ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatGpsCoordinates(lat: number, lng: number): string {
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
}

export function getGoogleMapsUrl(lat: number, lng: number): string {
  return `https://www.google.com/maps?q=${lat},${lng}`;
}
```

#### `web/src/lib/api.ts` Architecture
- **Base URL**: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'` (prefix with `/api/v1`).
- **Token Management**: Stores JWT in `localStorage` under key `swms_token`.
- **Request Interceptor**: Adds `Authorization: Bearer <token>` if present.
- **Response Interceptor**: Intercepts `401 Unauthorized` responses and cleans up token, redirecting client to `/login`.
- **Typed Endpoints**:
  - `authApi.login({ email, password })`
  - `authApi.getMe()`
  - `dashboardApi.getStats()`
  - `reportsApi.list({ page, limit, status, category_id, search })`
  - `reportsApi.getById(id)`
  - `reportsApi.updateStatus(id, { status, admin_notes })`

---

## 6. Verification Plan for Implementer
1. Execute `npm install` inside `web/` and verify that `package-lock.json` and `node_modules` are created cleanly.
2. Place the recommended configuration files (`tsconfig.json`, `next.config.mjs`, `postcss.config.js`, `tailwind.config.ts`, `.env.local`).
3. Create minimal root layout `src/app/layout.tsx` and smoke test page `src/app/page.tsx`.
4. Run `npm run build` in `web/` to confirm that TypeScript compilation and Next.js production build pass with **zero errors**.
5. Verify responsive styling and font variables in Chrome/browser at 375px (mobile), 768px (tablet), and 1280px (desktop).
