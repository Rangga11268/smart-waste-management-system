# Test Infrastructure Specification: SWMS Day 3 Web Dashboard

> **Target Repository:** `D:\Ngoding\interviewWeb\BillcodeTech`  
> **Milestone:** Day 3 Web Dashboard (Next.js 14 App Router + Tailwind CSS)  
> **Test Suite Files:** `tests/test_day3_web_e2e.py`, `tests/day3_web_runner.py`  
> **Test Engine:** Pytest 9.1+ with FastAPI TestClient and isolated In-Memory SQLite  
> **Total Automated Tests:** **88 Tests** (100% Pass Rate across all 4 Tiers)

---

## 1. Testing Philosophy & 4-Tier Methodology

The testing infrastructure implements a **requirement-driven, opaque-box end-to-end (E2E)** methodology designed to validate the Next.js 14 Web Dashboard contracts, design system adherence, REST API integrations, and municipal operational workflows.

```
                  ▲
                 / \
                /   \     Tier 4: Real-World Scenarios (3 tests)
               /     \    Full Admin Triage, Citizen-to-Completion, RBAC
              /-------\
             /         \    Tier 3: Cross-Feature Combinations (6 tests)
            /           \   Compound Queries, State Machine Chains, Audit Trails
           /-------------\
          /               \   Tier 2: Boundary & Corner Cases (14 tests)
         /                 \  Zero-division, Terminal State Locks, 400/401/403/422
        /-------------------\
       /                     \  Tier 1: Feature Coverage (65 tests)
      /                       \ 13 core features × 5 tests each
     /-------------------------\
```

### Architectural Principles:
1. **Opaque-Box Contract Verification**: Evaluates system behavior strictly against public API endpoints, response envelopes, error codes, and documented specifications without mutating internal application logic.
2. **Progressive Testability & Isolation**: Tests run in an isolated in-memory SQLite database environment (`StaticPool` with `PRAGMA foreign_keys=ON`) so tests never corrupt developer databases or require external server processes.
3. **Dual Execution Mode**: Test suite can be executed natively via standard `pytest` or via the dedicated formatted console runner `python tests/day3_web_runner.py`.

---

## 2. Test Suite Architecture & Directory Layout

```text
BillcodeTech/
├── backend/                        # FastAPI REST API & Models (Day 2)
│   ├── app/
│   │   ├── api/v1/                 # Endpoints: auth, dashboard, reports, categories, predict
│   │   ├── core/                   # Config, Database engine, Seeder
│   │   └── models/                 # User, Category, WasteReport, ReportLog
├── web/                            # Next.js 14 Web Dashboard (Day 3)
│   ├── src/
│   │   ├── app/                    # App Router pages: (auth)/login, (dashboard)/...
│   │   ├── components/             # Reusable UI widgets, badges, modals
│   │   ├── lib/                    # api.ts (Axios client), auth.tsx (Context)
│   │   └── types/                  # TypeScript API contracts
├── tests/
│   ├── conftest.py                 # Pytest session fixtures, TestClient, In-Memory DB
│   ├── test_day3_web_e2e.py        # Core Day 3 E2E test suite (88 test cases)
│   └── day3_web_runner.py          # Formatted CLI test runner with per-tier reporting
├── TEST_INFRA.md                   # Testing infrastructure & methodology documentation
└── TEST_READY.md                   # Test suite readiness certification
```

---

## 3. Comprehensive Feature Coverage Matrix

### Tier 1: Feature Coverage (65 Tests — 13 Features × 5 Tests Each)

| # | Feature Area | Test Method Names | Coverage Description |
|---|--------------|-------------------|----------------------|
| **F01** | **Styling & Design Tokens** | `test_f01_01_primary_emerald_tokens_specification`<br>`test_f01_02_neutral_base_tokens_specification`<br>`test_f01_03_text_slate_tokens_specification`<br>`test_f01_04_semantic_status_badge_tokens_specification`<br>`test_f01_05_category_badge_tokens_specification` | Validates `#059669` emerald brand tokens (`primary-50` through `900`), neutral base canvas/card/border tokens, text slate hierarchy, semantic status badges (amber/blue/emerald/rose), and category accents. |
| **F02** | **Typography & Fonts** | `test_f02_01_heading_display_font_space_grotesk`<br>`test_f02_02_body_ui_font_inter`<br>`test_f02_03_monospace_font_jetbrains_mono`<br>`test_f02_04_typography_scale_hierarchy`<br>`test_f02_05_font_css_variables_and_fallback` | Validates Space Grotesk for display/headings, Inter for body/tables, JetBrains Mono for GPS/IDs, typography scale definitions, and CSS variable configurations. |
| **F03** | **Auth Login Flow** | `test_f03_01_admin_login_endpoint_success`<br>`test_f03_02_citizen_login_endpoint_success`<br>`test_f03_03_login_response_envelope_structure`<br>`test_f03_04_login_user_profile_payload_fields`<br>`test_f03_05_evaluator_quick_presets_authentication` | Validates admin and citizen login against `POST /api/v1/auth/login`, JWT access token issuance, response envelope, user profile payload, and evaluator quick-fill credentials. |
| **F04** | **Token Injection & Interceptors** | `test_f04_01_bearer_token_authorization_header_me`<br>`test_f04_02_missing_auth_header_returns_401`<br>`test_f04_03_malformed_auth_header_returns_401`<br>`test_f04_04_tampered_token_signature_returns_401`<br>`test_f04_05_auth_session_profile_fields_contract` | Validates `Authorization: Bearer <token>` injection on `/api/v1/auth/me`, rejection of missing/malformed/tampered tokens with 401, and profile field contracts. |
| **F05** | **Stats Metrics Cards** | `test_f05_01_admin_stats_total_reports_metric`<br>`test_f05_02_admin_stats_status_counters_presence`<br>`test_f05_03_admin_stats_completion_rate_calculation`<br>`test_f05_04_admin_stats_active_users_metric`<br>`test_f05_05_stat_cards_ui_metadata_contract` | Validates `GET /api/v1/dashboard/stats` summary counters (`total_reports`, `pending_count`, `in_progress_count`, `completed_count`, `rejected_count`), completion rate percentage, active users count, and UI card metadata. |
| **F06** | **Category Distribution** | `test_f06_01_category_distribution_presence`<br>`test_f06_02_category_distribution_item_fields`<br>`test_f06_03_category_distribution_count_sum`<br>`test_f06_04_category_distribution_percentage_sum`<br>`test_f06_05_category_accent_colors_mapping` | Validates presence of Organic, Plastic, and Paper categories in distribution, count and percentage consistency, sum matching total classified reports, and color mappings. |
| **F07** | **Reports Table** | `test_f07_01_reports_table_envelope_structure`<br>`test_f07_02_reports_table_meta_fields`<br>`test_f07_03_reports_table_item_fields`<br>`test_f07_04_reports_table_nested_category`<br>`test_f07_05_reports_table_nested_reporter` | Validates `GET /api/v1/reports` envelope structure, pagination meta (`total_items`, `current_page`, `total_pages`, `limit`), table record fields, and nested category & reporter objects. |
| **F08** | **Multi-Criteria Filters** | `test_f08_01_filter_by_pending_status`<br>`test_f08_02_filter_by_in_progress_status`<br>`test_f08_03_filter_by_completed_status`<br>`test_f08_04_filter_by_rejected_status`<br>`test_f08_05_filter_by_category_id` | Validates filtering reports by exact status (`Pending`, `In Progress`, `Completed`, `Rejected`) and master category ID (`category_id=1, 2, 3`). |
| **F09** | **Keyword Search** | `test_f09_01_search_by_title_keyword`<br>`test_f09_02_search_by_description_keyword`<br>`test_f09_03_search_by_address_note_keyword`<br>`test_f09_04_search_case_insensitivity`<br>`test_f09_05_search_no_match_returns_empty` | Validates search query matching against title, description, and landmark note, case-insensitivity, and clean empty state returns. |
| **F10** | **Review Modal** | `test_f10_01_review_modal_fetch_detail_by_id`<br>`test_f10_02_review_modal_ai_detection_badge`<br>`test_f10_03_review_modal_photo_preview_field`<br>`test_f10_04_review_modal_address_and_notes`<br>`test_f10_05_review_modal_audit_trail_history` | Validates `GET /api/v1/reports/{id}` for modal preview, AI confidence percentage badge, photo evidence URL, landmark notes, and audit log list. |
| **F11** | **Google Maps Geolocation** | `test_f11_01_google_maps_url_generation`<br>`test_f11_02_google_maps_latitude_range_validation`<br>`test_f11_03_google_maps_longitude_range_validation`<br>`test_f11_04_google_maps_coordinate_formatting_mono`<br>`test_f11_05_google_maps_link_target_security` | Validates external Google Maps URL format `https://www.google.com/maps?q={lat},{long}`, valid latitude/longitude ranges, precision display in monospace, and secure link attributes. |
| **F12** | **Status Patch & State Machine** | `test_f12_01_status_patch_pending_to_in_progress`<br>`test_f12_02_status_patch_in_progress_to_completed`<br>`test_f12_03_status_patch_pending_to_rejected`<br>`test_f12_04_status_patch_returns_updated_at`<br>`test_f12_05_status_patch_completed_sets_resolved_at` | Validates administrative status mutations via `PATCH /api/v1/reports/{id}/status`, admin notes attachment, updated timestamps, and `resolved_at` persistence on completion. |
| **F13** | **User Management & RBAC** | `test_f13_01_admin_user_profile_role`<br>`test_f13_02_citizen_user_profile_role`<br>`test_f13_03_user_profile_active_status`<br>`test_f13_04_seed_users_presence_and_roles`<br>`test_f13_05_rbac_admin_route_guard_enforcement` | Validates role distinctions (`admin` vs `user`), active account statuses, seed user presence (`admin@bilcode.id` / `user@bilcode.id`), and 403 route guard restrictions. |

---

### Tier 2: Boundary & Corner Cases (14 Tests)

| # | Test Method Name | Scenario & Boundary Condition Verified |
|---|------------------|----------------------------------------|
| **T2.01** | `test_t2_01_empty_reports_list_returns_zero_meta` | Empty report query returns `total_items: 0, current_page: 1, data: []` without errors. |
| **T2.02** | `test_t2_02_zero_reports_division_guard_in_stats` | Zero total reports handles division-by-zero safely, returning `completion_rate_percent: 0.0`. |
| **T2.03** | `test_t2_03_invalid_status_transition_pending_to_completed_400` | Skipping `In Progress` (`Pending` -> `Completed`) is rejected with HTTP 400. |
| **T2.04** | `test_t2_04_terminal_state_completed_modification_400` | Attempting to modify a `Completed` report is rejected with HTTP 400 (Terminal State). |
| **T2.05** | `test_t2_05_terminal_state_rejected_modification_400` | Attempting to modify a `Rejected` report is rejected with HTTP 400 (Terminal State). |
| **T2.06** | `test_t2_06_invalid_credentials_401_rejection` | Invalid password returns HTTP 401 Unauthorized with descriptive detail. |
| **T2.07** | `test_t2_07_unregistered_email_401_rejection` | Unregistered email returns HTTP 401 Unauthorized. |
| **T2.08** | `test_t2_08_non_admin_403_on_dashboard_stats` | Non-admin token requesting `/api/v1/dashboard/stats` receives HTTP 403 Forbidden. |
| **T2.09** | `test_t2_09_non_admin_403_on_status_patch` | Non-admin token executing `PATCH /api/v1/reports/{id}/status` receives HTTP 403 Forbidden. |
| **T2.10** | `test_t2_10_out_of_bounds_page_returns_empty_data` | Requesting out-of-bounds page (`page=999`) returns `data: []` with 200 OK. |
| **T2.11** | `test_t2_11_page_limit_boundary_validation_422` | Boundary validation rejects `limit=0` or `limit=101` with HTTP 422 Unprocessable Entity. |
| **T2.12** | `test_t2_12_relative_image_url_prefix_resolver` | Normalizes relative URL `/uploads/...` to `http://localhost:8000/...`, leaves absolute untouched, and handles null/empty with placeholder. |
| **T2.13** | `test_t2_13_report_with_null_admin_notes_handled` | Newly created report with `admin_notes=None` handles null safely without runtime crash. |
| **T2.14** | `test_t2_14_ai_confidence_null_or_zero_boundary` | Confidence percentage formatter handles `None`, `0.0`, and precision floats cleanly (`0.00%` vs `94.21%`). |

---

### Tier 3: Cross-Feature Combinations (6 Tests)

| # | Test Method Name | Combination Description |
|---|------------------|-------------------------|
| **T3.01** | `test_t3_01_search_filter_pagination_compound_query` | Combines text keyword search + status filter + category filter + pagination (`limit` & `page`) in a single query. |
| **T3.02** | `test_t3_02_login_stats_patch_audit_log_chain` | Multi-step integration: Admin login -> Bearer token -> Fetch stats -> Submit status patch -> Verify audit log reflection. |
| **T3.03** | `test_t3_03_citizen_submission_admin_triage_flow` | Citizen submits report -> Admin dashboard stats pending count increments -> Admin filters by Pending and locates record. |
| **T3.04** | `test_t3_04_full_state_machine_three_stage_audit_trail` | Transitions through full lifecycle: `Pending` -> `In Progress` -> `Completed`, verifying audit trail accumulates all 3 stages in order. |
| **T3.05** | `test_t3_05_rejection_path_audit_log_trail` | Transitions `Pending` -> `Rejected` with disposition remarks, verifying terminal state lock and audit log history. |
| **T3.06** | `test_t3_06_master_categories_cross_referenced_with_reports` | Fetches category catalog from `/api/v1/categories` and cross-references against report category metadata. |

---

### Tier 4: Real-World Scenarios (3 Tests)

| # | Test Method Name | Scenario Description |
|---|------------------|----------------------|
| **T4.01** | `test_t4_01_full_admin_triage_workflow` | **Full Admin Triage Flow**:<br>1. Citizen submits waste report with GPS coordinates and AI-predicted category.<br>2. Super Admin logs in and acquires authentication token.<br>3. Admin views dashboard metrics, observing pending verification count.<br>4. Admin inspects review modal: photo preview, AI badge, and Google Maps link.<br>5. Admin dispatches sanitation crew, patching status to `In Progress` with notes.<br>6. Admin verifies updated status and audit trail entry in report details.<br>7. Admin re-fetches dashboard metrics, verifying `in_progress_count` incremented. |
| **T4.02** | `test_t4_02_citizen_report_to_completion_lifecycle` | **Full Waste Resolution Lifecycle**:<br>1. Citizen submits report with photo and coordinates.<br>2. Admin transitions report to `In Progress`.<br>3. Crew completes cleanup; Admin transitions to `Completed`.<br>4. System populates `resolved_at`, enforces terminal state, and recalculates dashboard completion rate %. |
| **T4.03** | `test_t4_03_rbac_security_and_role_isolation` | **RBAC Security & Role Isolation**:<br>1. Anonymous user blocked (401) from `/auth/me`, `/reports`, `/dashboard/stats`, and mutations.<br>2. Citizen user permitted read-only access to `/reports` and `/auth/me`, but blocked (403) from stats and status mutation.<br>3. Super Admin granted full privileges across all endpoints. |

---

## 4. Test Execution Instructions

### Running via Pytest:
```bash
# From repository root (D:\Ngoding\interviewWeb\BillcodeTech)
pytest tests/test_day3_web_e2e.py -v

# Run specific tier
pytest tests/test_day3_web_e2e.py -k "TestTier1FeatureCoverage" -v
pytest tests/test_day3_web_e2e.py -k "TestTier2BoundaryCases" -v
pytest tests/test_day3_web_e2e.py -k "TestTier3CrossFeatureCombinations" -v
pytest tests/test_day3_web_e2e.py -k "TestTier4RealWorldScenarios" -v
```

### Running via Dedicated E2E Runner:
```bash
# Execute entire 4-tier suite with summary table
python tests/day3_web_runner.py

# Execute specific tier
python tests/day3_web_runner.py --tier 1
python tests/day3_web_runner.py --tier 2
python tests/day3_web_runner.py --tier 3
python tests/day3_web_runner.py --tier 4

# Run with verbose output
python tests/day3_web_runner.py -v
```

---

## 5. Verification & Test Suite Summary

```
===========================================================================
                         FINAL TEST SUITE SUMMARY
===========================================================================
Tier                                 | Total  | Pass   | Fail   | Pass %  
--------------------------------------------------------------------------
Tier 1: Feature Coverage             | 65     | 65     | 0      | 100.0%
Tier 2: Boundary & Corner Cases      | 14     | 14     | 0      | 100.0%
Tier 3: Cross-Feature Combinations   | 6      | 6      | 0      | 100.0%
Tier 4: Real-World Scenarios         | 3      | 3      | 0      | 100.0%
--------------------------------------------------------------------------
OVERALL TOTALS                       | 88     | 88     | 0      | 100.0%
===========================================================================
Total Suite Execution Time: ~130 seconds
>>> ALL TESTS PASSED SUCCESSFULLY! Day 3 Web Dashboard criteria fully satisfied. <<<
```
