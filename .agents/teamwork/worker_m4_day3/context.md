# worker_m4_day3 Context
Target: Execute Milestone 4 (M4) - Waste Reports Management Table & Review Modal:
- Create web/src/components/ReportModal.tsx:
  - Photo evidence preview with getFullImageUrl and error fallback.
  - AI classification category & confidence percentage in JetBrains Mono.
  - GPS coordinates with direct Google Maps link (https://www.google.com/maps?q=lat,long).
  - Admin status disposition form (PATCH /api/v1/reports/{id}/status) with state machine transitions:
    - Pending -> In Progress / Rejected
    - In Progress -> Completed / Rejected
    - Completed / Rejected -> Terminal locked (disabled form, terminal alert)
  - Admin notes (admin_notes) field.
  - Audit trail history timeline from report.logs.
- Create web/src/app/(dashboard)/reports/page.tsx:
  - Fetches from GET /api/v1/reports via reportsApi.getReports().
  - Debounced keyword search (title, description, address_note).
  - Status filter dropdown and category filter dropdown.
  - Pagination controls (Previous/Next, page bounds).
  - Table columns: ID (font-mono), thumbnail, title & address note, CategoryBadge, reporter, GPS (font-mono), date, StatusBadge, action "Tinjau".
  - Review Modal trigger with real-time table state update upon status patch.
- Verify npm run typecheck, npm run lint, npm run build, and python tests/day3_web_runner.py.
