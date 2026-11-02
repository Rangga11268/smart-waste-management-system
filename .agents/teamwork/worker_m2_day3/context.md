# worker_m2_day3 Context
Target: Execute Milestone 2 (M2) - API Client, Authentication, Session Management & Route Protection:
- Implement web/src/lib/api.ts with Axios, NEXT_PUBLIC_API_URL, Bearer interceptor, 401 handling, image URL helper, typed API methods.
- Implement web/src/lib/auth.tsx with AuthProvider, useAuth hook, token persistence in localStorage, user profile hydration via GET /api/v1/auth/me.
- Implement web/src/app/(auth)/login/page.tsx with Eco-Tech styling, email/password form, quick evaluator presets (Admin: admin@bilcode.id / Admin123!, User: user@bilcode.id / User123!), error handling.
- Implement web/src/app/(dashboard)/layout.tsx with client-side Auth Guard: unauthenticated redirects to /login, citizen redirected away from admin-only routes.
- Verify npm run typecheck, npm run lint, and npm run build.
