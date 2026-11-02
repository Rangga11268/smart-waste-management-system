## 2026-11-02T12:32:37Z
Smart Waste Management System (SWMS) Web Dashboard (Admin & User) for the Bilcode Technology Fullstack Developer Technical Coding Test take-home assessment, implementing Day 3 of the roadmap in Next.js 14 App Router and Tailwind CSS.

Working directory: D:\Ngoding\interviewWeb\BillcodeTech
Integrity mode: development

## Requirements

### R1. Next.js 14 App Router Setup & Eco-Tech Design System
Setup the Next.js 14 web application in `web/` configured with Tailwind CSS and Lucide icons, adhering to the Eco-Tech styling guide in `docs/STYLING_GUIDE.md`: Space Grotesk for headings/display, Inter for body/forms/tables, JetBrains Mono for GPS coordinates and report IDs, and emerald primary `#059669` with semantic status badges (amber for Pending, blue for In Progress, emerald for Completed, rose for Rejected).

### R2. Authentication, Session Management & Route Protection
Implement the login page and session management integrated with backend `POST /api/v1/auth/login`, storing JWT access tokens, handling auth state, and enforcing role-based route protection where users with the Admin role are granted access to Dashboard, Reports Management, and User Management.

### R3. Analytics Dashboard
Implement the `/dashboard` page displaying key statistics fetched from `GET /api/v1/dashboard/stats`, including 4 primary metric cards (Total Reports, Pending Verification, In Progress, Completion Rate %), waste category distribution visualization (Organic, Plastic, Paper), and recent activity logs.

### R4. Waste Reports Management Table & Review Modal
Implement the `/reports` page with keyword text search (title, description, location benchmark), status and category filter dropdowns, pagination, and colored semantic status badges. Implement a report review modal featuring uploaded photo preview, AI detection badge (detected category and confidence score), GPS coordinates with a direct Google Maps link (`https://www.google.com/maps?q=lat,long`), and an admin status update action form (`PATCH /api/v1/reports/{id}/status`) with disposition notes (`admin_notes`).

### R5. User Management & API Client
Implement the API client in `web/src/lib/api.ts` configured with `NEXT_PUBLIC_API_URL` (connecting to `http://localhost:8000`) and automatic Bearer token injection, current user profile display from `GET /api/v1/auth/me`, and user management list view for administrators.

### R6. Verification & Responsive Build
Ensure all pages and components have responsive layouts across mobile, tablet, and desktop viewports, with a successful Next.js production build (`npm run build`), TypeScript type checking, and linting passing with zero errors in `web/`.
