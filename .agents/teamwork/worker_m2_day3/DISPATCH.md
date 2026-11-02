## 2026-11-02T13:24:50Z

You are worker_m2_day3, a teamwork_worker subagent.
Working Directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_day3/
Parent Orchestrator ID: 43d63726-8e7d-4ce8-9507-d98d72d21885

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MANDATORY INPUT:
Read D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md.
Also inspect:
- D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md
- D:\Ngoding\interviewWeb\BillcodeTech\docs\STYLING_GUIDE.md
- D:\Ngoding\interviewWeb\BillcodeTech\docs\API_SPECS.md
- D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_backend_api_1\report.md
- D:\Ngoding\interviewWeb\BillcodeTech\web\src\types\api.ts
- D:\Ngoding\interviewWeb\BillcodeTech\web\src\components\Sidebar.tsx
- D:\Ngoding\interviewWeb\BillcodeTech\web\src\components\Header.tsx

OBJECTIVE:
Implement Milestone 2 (M2): API Client, Authentication, Session Management & Route Protection:
1. API Client (`web/src/lib/api.ts`):
   - Configure Axios instance with `baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`, timeout 15000ms, and `Content-Type: application/json`.
   - Request Interceptor: Read access token from `localStorage.getItem('token')` and attach `Authorization: Bearer <token>` to requests if present.
   - Response Interceptor: If error response status is 401, remove token and user from `localStorage` and redirect to `/login` (when in browser).
   - Implement `getFullImageUrl(path: string)` helper: resolves `/uploads/reports/...` to `${NEXT_PUBLIC_API_URL.replace('/api/v1', '')}${path}` (`http://localhost:8000/uploads/reports/...`).
   - Export typed API modules:
     - `authApi`: `login({ email, password })`, `getMe()`, `register(data)`
     - `dashboardApi`: `getStats()` -> `GET /api/v1/dashboard/stats`
     - `reportsApi`: `getReports(params)`, `getReport(id)`, `updateStatus(id, { status, admin_notes })`
     - `categoriesApi`: `getCategories()` -> `GET /api/v1/categories`
2. Authentication Context (`web/src/lib/auth.tsx`):
   - Create `AuthContext` and `AuthProvider` export with `useAuth()` hook.
   - Manage state: `user: UserProfile | null`, `token: string | null`, `isLoading: boolean`, `isAuthenticated: boolean`, `isAdmin: boolean`.
   - Implement `login(email, password)`: calls `authApi.login`, stores `token` and `user` in `localStorage`, updates state, returns user.
   - Implement `logout()`: clears `token` and `user` from `localStorage`, resets state, navigates to `/login`.
   - Implement initial hydration on mount: checks `localStorage` for token, verifies/refreshes user profile via `authApi.getMe()`.
3. Login Screen (`web/src/app/(auth)/login/page.tsx`):
   - Eco-Tech styling matching `docs/STYLING_GUIDE.md`: Brand Primary `#059669`, emerald accents, high-contrast inputs, Space Grotesk title.
   - Form fields: Email input and Password input with client-side validation.
   - Submit button with loading spinner state.
   - Error display card showing error messages on invalid credentials (401) or network failures.
   - Evaluator quick presets:
     - Button "Masuk sebagai Admin" -> fills `admin@bilcode.id` / `Admin123!`
     - Button "Masuk sebagai Warga" -> fills `user@bilcode.id` / `User123!`
   - On successful login: redirect admin to `/dashboard` and citizen to `/reports`.
4. Route Protection & App Shell (`web/src/app/(dashboard)/layout.tsx`):
   - Client layout wrapped with `AuthProvider`.
   - Protect routes: if user is not authenticated and not loading, redirect to `/login`.
   - RBAC protection: if user is logged in as `role: 'user'` and navigates to `/dashboard` or `/users`, redirect to `/reports` with an access notification.
   - Pass authenticated user profile into `Sidebar` and `Header` components.
   - Update `web/src/app/page.tsx` to handle root redirection to `/dashboard` or `/login`.
5. Verification:
   - Run `npm run typecheck` (`tsc --noEmit`), `npm run lint`, and `npm run build` in `web/` to confirm zero compilation, lint, or type errors.
   - Run `python tests/day3_web_runner.py` to confirm all 88 E2E test cases pass.

WRITE OWNERSHIP:
You own `web/src/lib/api.ts`, `web/src/lib/auth.tsx`, `web/src/app/(auth)/login/page.tsx`, `web/src/app/(dashboard)/layout.tsx`, and `web/src/app/page.tsx`. DO NOT modify `backend/` or `tests/`.

OUTPUT REQUIREMENTS:
Write implementation details, verification results, and handoff to:
`D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_day3\report.md` and `handoff.md`.

COMPLETION CRITERIA:
When finished, send a message back to parent orchestrator with summary of changes and build outputs.
