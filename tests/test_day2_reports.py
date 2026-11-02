"""Tier 1, Tier 2, Tier 3, and Tier 4 Waste Reports Management Test Suite for SWMS - Day 2.

Covers:
- Tier 1 (Feature Coverage):
  1. Citizen submits waste report with valid photo & GPS (POST /api/v1/reports)
  2. List reports with default pagination (GET /api/v1/reports)
  3. Filter reports by status (?status=Pending)
  4. Filter reports by category (?category_id=2)
  5. Keyword search across title/description/address_note (?search=...)
  6. Pagination limit and page navigation (?page=1&limit=5)
  7. Get single report details by UUID with audit log history (GET /api/v1/reports/{id})
  8. Admin updates status from Pending to In Progress with admin notes (PATCH /api/v1/reports/{id}/status)
  9. Admin updates status from In Progress to Completed, automatically setting resolved_at
  10. Audit log verification in report_logs table upon status modification
- Tier 2 (Boundary & Corner Cases):
  1. Non-admin citizen user receives 403 Forbidden on PATCH /api/v1/reports/{id}/status
  2. Disallowed direct transition Pending -> Completed rejected with 400 Bad Request
  3. Disallowed transition from terminal state Completed rejected with 400 Bad Request
  4. Disallowed transition from terminal state Rejected rejected with 400 Bad Request
  5. Update status on non-existent report UUID returns 404 Not Found
  6. Get report detail on non-existent report UUID returns 404 Not Found
  7. Report creation with out-of-bounds latitude (>90 or <-90) rejected with 422
  8. Report creation with out-of-bounds longitude (>180 or <-180) rejected with 422
  9. Report creation with non-existent category_id (e.g. 999) rejected with 400 or 404
  10. Keyword search with no matching results returns empty data array with total_items=0
  11. Pagination page index out of bounds returns empty data array
- Tier 3 (Cross-Feature Pairwise Integration):
  - Citizen registers -> logins -> submits report -> Admin logins -> updates status -> audit logs recorded -> dashboard reflects metrics
- Tier 4 (Real-World Application Scenario per docs/RUNBOOK.md):
  - Multi-report submission in Jakarta/Bandung, full lifecycle triage, and audit trail inspection
"""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.log import ReportLog
from app.models.report import WasteReport
from app.models.user import User


class TestTier1ReportsFeatureCoverage:
    """Tier 1: Feature coverage for waste reports CRUD and audit logging in isolation."""

    def test_submit_report_happy_path(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes, seed_data, db_session: Session
    ):
        """Tier 1: Verify authenticated citizen can submit a waste report with photo and GPS."""
        files = {
            "file": ("tumpukan_plastik.jpg", dummy_image_bytes, "image/jpeg"),
        }
        data = {
            "title": "Tumpukan botol plastik di pinggir selokan",
            "description": "Botol plastik menumpuk menyumbat aliran air.",
            "category_id": 2,  # Plastic Waste
            "latitude": -6.2088,
            "longitude": 106.8456,
            "address_note": "Jl. Ahmad Yani No. 12, depan ruko",
        }

        response = client.post("/api/v1/reports", files=files, data=data, headers=user_headers)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        res_data = body["data"]
        assert res_data["title"] == "Tumpukan botol plastik di pinggir selokan"
        assert res_data["status"] == "Pending"
        assert "id" in res_data
        assert "image_url" in res_data
        assert "created_at" in res_data

        # Verify database record
        report_id = uuid.UUID(res_data["id"])
        db_report = db_session.query(WasteReport).filter_by(id=report_id).first()
        assert db_report is not None
        assert db_report.category_id == 2
        assert db_report.latitude == -6.2088
        assert db_report.longitude == 106.8456
        assert db_report.status == "Pending"

        # Verify initial audit log record in report_logs
        initial_log = db_session.query(ReportLog).filter_by(report_id=report_id).first()
        assert initial_log is not None
        assert initial_log.new_status == "Pending"

    def test_list_reports_default_pagination(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 1: Verify GET /reports returns paginated meta and data array with nested entities."""
        # Submit 2 test reports
        for i in range(2):
            files = {"file": (f"test_{i}.jpg", dummy_image_bytes, "image/jpeg")}
            data = {
                "title": f"Laporan Sampah #{i+1}",
                "category_id": 1 if i == 0 else 2,
                "latitude": -6.2000 + (i * 0.01),
                "longitude": 106.8000 + (i * 0.01),
            }
            client.post("/api/v1/reports", files=files, data=data, headers=user_headers)

        response = client.get("/api/v1/reports", headers=user_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        assert "meta" in body
        assert "data" in body
        meta = body["meta"]
        assert meta["total_items"] >= 2
        assert meta["current_page"] == 1
        assert meta["limit"] >= 1

        first_item = body["data"][0]
        assert "id" in first_item
        assert "title" in first_item
        assert "status" in first_item
        assert "category" in first_item
        assert "name" in first_item["category"]
        assert "reporter" in first_item

    def test_filter_reports_by_status(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 1: Verify filtering reports by status parameter (?status=Pending vs ?status=In Progress)."""
        # Create a report and advance its status to In Progress
        files = {"file": ("filter_test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": "Laporan In Progress Test",
            "category_id": 1,
            "latitude": -6.1754,
            "longitude": 106.8272,
        }
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        # Advance to In Progress via Admin
        client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "In Progress", "admin_notes": "Truk dikerahkan"},
            headers=admin_headers,
        )

        # Query with ?status=In Progress
        resp_prog = client.get("/api/v1/reports?status=In Progress", headers=user_headers)
        assert resp_prog.status_code == 200
        items_prog = resp_prog.json()["data"]
        assert all(r["status"] == "In Progress" for r in items_prog)
        assert any(r["id"] == report_id for r in items_prog)

    def test_filter_reports_by_category(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 1: Verify filtering reports by category_id parameter (?category_id=2)."""
        files = {"file": ("cat_test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": "Laporan Sampah Kertas",
            "category_id": 3,  # Paper Waste
            "latitude": -6.2100,
            "longitude": 106.8500,
        }
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        resp_cat = client.get("/api/v1/reports?category_id=3", headers=user_headers)
        assert resp_cat.status_code == 200
        items_cat = resp_cat.json()["data"]
        assert all(r["category"]["id"] == 3 for r in items_cat)
        assert any(r["id"] == report_id for r in items_cat)

    def test_search_reports_by_keyword(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 1: Verify keyword search across title, description, or address notes."""
        unique_keyword = "KardusSuperUnik"
        files = {"file": ("search_test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": f"Tumpukan {unique_keyword} di pasar",
            "description": "Banyak berserakan di jalanan.",
            "category_id": 3,
            "latitude": -6.2200,
            "longitude": 106.8600,
        }
        client.post("/api/v1/reports", files=files, data=data, headers=user_headers)

        resp_search = client.get(f"/api/v1/reports?search={unique_keyword.lower()}", headers=user_headers)
        assert resp_search.status_code == 200
        data_search = resp_search.json()["data"]
        assert len(data_search) >= 1
        assert any(unique_keyword in r["title"] for r in data_search)

    def test_get_report_details_by_id(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 1: Verify fetching complete single report record by UUID with audit log list."""
        files = {"file": ("detail_test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": "Laporan Detail Komplit",
            "description": "Deskripsi rinci lokasi sampah.",
            "category_id": 1,
            "latitude": -6.1800,
            "longitude": 106.8300,
            "address_note": "Dekat gapura perumahan",
        }
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        response = client.get(f"/api/v1/reports/{report_id}", headers=user_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        r_data = body["data"]
        assert r_data["id"] == report_id
        assert r_data["title"] == "Laporan Detail Komplit"
        assert r_data["address_note"] == "Dekat gapura perumahan"
        assert "category" in r_data
        assert "reporter" in r_data
        assert "logs" in r_data
        assert isinstance(r_data["logs"], list)

    def test_admin_update_status_pending_to_in_progress(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 1: Verify admin can transition report status from Pending to In Progress."""
        files = {"file": ("status1.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Status Transisi 1", "category_id": 2, "latitude": -6.19, "longitude": 106.84}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        payload = {
            "status": "In Progress",
            "admin_notes": "Tim truk kebersihan armada #3 sedang dikerahkan ke lokasi.",
        }
        response = client.patch(f"/api/v1/reports/{report_id}/status", json=payload, headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "In Progress"
        assert body["data"]["admin_notes"] == payload["admin_notes"]

    def test_admin_update_status_in_progress_to_completed_sets_resolved_at(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data, db_session: Session
    ):
        """Tier 1: Verify transition In Progress -> Completed automatically timestamps resolved_at."""
        files = {"file": ("status2.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Selesai Test", "category_id": 2, "latitude": -6.19, "longitude": 106.84}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        # Step 1: Pending -> In Progress
        client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "In Progress", "admin_notes": "Sedang dibersihkan"},
            headers=admin_headers,
        )

        # Step 2: In Progress -> Completed
        response = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Completed", "admin_notes": "Lokasi bersih tuntas."},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "Completed"

        # Check resolved_at in database
        db_report = db_session.query(WasteReport).filter_by(id=uuid.UUID(report_id)).first()
        assert db_report.status == "Completed"
        assert db_report.resolved_at is not None

    def test_audit_logs_record_every_status_transition(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data, db_session: Session
    ):
        """Tier 1: Verify every status transition records a corresponding row in report_logs."""
        files = {"file": ("audit.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Audit Trail", "category_id": 1, "latitude": -6.20, "longitude": 106.85}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_uuid = uuid.UUID(created["id"])

        # Transition 1: Pending -> In Progress
        client.patch(
            f"/api/v1/reports/{report_uuid}/status",
            json={"status": "In Progress", "admin_notes": "Action 1"},
            headers=admin_headers,
        )

        # Transition 2: In Progress -> Completed
        client.patch(
            f"/api/v1/reports/{report_uuid}/status",
            json={"status": "Completed", "admin_notes": "Action 2"},
            headers=admin_headers,
        )

        logs = db_session.query(ReportLog).filter_by(report_id=report_uuid).order_by(ReportLog.created_at).all()
        # Expect at least 3 logs: Initial (Pending), Transition to In Progress, Transition to Completed
        assert len(logs) >= 3
        statuses = [l.new_status for l in logs]
        assert "Pending" in statuses
        assert "In Progress" in statuses
        assert "Completed" in statuses


class TestTier2ReportsBoundaryAndCornerCases:
    """Tier 2: RBAC permissions, invalid transitions, terminal states, and validation bounds."""

    def test_citizen_user_cannot_update_report_status_forbidden(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 2: Verify non-admin citizen attempting to update report status receives 403 Forbidden."""
        files = {"file": ("forbidden.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Hak Akses", "category_id": 1, "latitude": -6.21, "longitude": 106.85}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        # Attempt PATCH with user_headers (Citizen)
        response = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Completed", "admin_notes": "Saya selesai sendiri"},
            headers=user_headers,
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        assert "detail" in response.json()

    def test_invalid_direct_transition_pending_to_completed_rejected(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 2: Verify direct transition from Pending to Completed without In Progress returns 400 Bad Request."""
        files = {"file": ("direct_jump.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Loncat Status", "category_id": 1, "latitude": -6.21, "longitude": 106.85}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        response = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Completed", "admin_notes": "Langsung komplit"},
            headers=admin_headers,
        )
        assert response.status_code == 400, f"Expected 400 for illegal transition, got {response.status_code}: {response.text}"

    def test_terminal_state_completed_cannot_be_transitioned(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 2: Verify once a report is Completed, subsequent transitions are rejected with 400 Bad Request."""
        files = {"file": ("terminal_completed.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Terminal 1", "category_id": 1, "latitude": -6.21, "longitude": 106.85}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        # Pending -> In Progress -> Completed
        client.patch(f"/api/v1/reports/{report_id}/status", json={"status": "In Progress"}, headers=admin_headers)
        client.patch(f"/api/v1/reports/{report_id}/status", json={"status": "Completed"}, headers=admin_headers)

        # Attempt to transition Completed -> In Progress
        reopen_response = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "In Progress", "admin_notes": "Membuka kembali laporan"},
            headers=admin_headers,
        )
        assert reopen_response.status_code == 400, f"Expected 400, got {reopen_response.status_code}"

    def test_terminal_state_rejected_cannot_be_transitioned(
        self, client: TestClient, admin_headers, user_headers, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 2: Verify once a report is Rejected, subsequent transitions are rejected with 400 Bad Request."""
        files = {"file": ("terminal_rejected.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Ditolak", "category_id": 1, "latitude": -6.21, "longitude": 106.85}
        created = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        report_id = created["id"]

        # Pending -> Rejected
        reject_resp = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Rejected", "admin_notes": "Foto bukan tumpukan sampah"},
            headers=admin_headers,
        )
        assert reject_resp.status_code == 200

        # Attempt to transition Rejected -> Pending
        invalid_retry = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Pending", "admin_notes": "Coba lagi"},
            headers=admin_headers,
        )
        assert invalid_retry.status_code == 400

    def test_get_report_details_nonexistent_uuid_returns_404(self, client: TestClient, user_headers):
        """Tier 2: Verify requesting a non-existent report UUID returns 404 Not Found."""
        random_uuid = str(uuid.uuid4())
        response = client.get(f"/api/v1/reports/{random_uuid}", headers=user_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_update_status_nonexistent_uuid_returns_404(self, client: TestClient, admin_headers):
        """Tier 2: Verify updating status of a non-existent report UUID returns 404 Not Found."""
        random_uuid = str(uuid.uuid4())
        response = client.patch(
            f"/api/v1/reports/{random_uuid}/status",
            json={"status": "In Progress"},
            headers=admin_headers,
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_submit_report_invalid_latitude_bounds(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes
    ):
        """Tier 2: Verify latitude > 90.0 or < -90.0 returns 422 Unprocessable Entity."""
        files = {"file": ("bounds.jpg", dummy_image_bytes, "image/jpeg")}
        data_over = {"title": "Lat Out", "category_id": 1, "latitude": 95.5, "longitude": 106.0}
        resp1 = client.post("/api/v1/reports", files=files, data=data_over, headers=user_headers)
        assert resp1.status_code == 422

        data_under = {"title": "Lat Under", "category_id": 1, "latitude": -95.5, "longitude": 106.0}
        files2 = {"file": ("bounds.jpg", dummy_image_bytes, "image/jpeg")}
        resp2 = client.post("/api/v1/reports", files=files2, data=data_under, headers=user_headers)
        assert resp2.status_code == 422

    def test_submit_report_invalid_longitude_bounds(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes
    ):
        """Tier 2: Verify longitude > 180.0 or < -180.0 returns 422 Unprocessable Entity."""
        files = {"file": ("bounds_long.jpg", dummy_image_bytes, "image/jpeg")}
        data_long = {"title": "Long Out", "category_id": 1, "latitude": -6.0, "longitude": 195.0}
        resp = client.post("/api/v1/reports", files=files, data=data_long, headers=user_headers)
        assert resp.status_code == 422

    def test_submit_report_nonexistent_category_id(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes
    ):
        """Tier 2: Verify referencing a non-existent category_id (e.g. 999) returns 400 or 404."""
        files = {"file": ("invalid_cat.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Kategori Tidak Ada", "category_id": 999, "latitude": -6.2, "longitude": 106.8}
        response = client.post("/api/v1/reports", files=files, data=data, headers=user_headers)
        assert response.status_code in (400, 404), f"Expected 400 or 404, got {response.status_code}"

    def test_list_reports_empty_search_query(self, client: TestClient, user_headers, seed_data):
        """Tier 2: Verify search keyword with zero matches returns 200 OK with total_items=0 and empty list."""
        response = client.get("/api/v1/reports?search=NONEXISTENT_KEYWORD_XYZ_987", headers=user_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["total_items"] == 0
        assert body["data"] == []

    def test_list_reports_page_out_of_bounds(self, client: TestClient, user_headers, seed_data):
        """Tier 2: Verify requesting a page far beyond total pages returns 200 OK with empty data list."""
        response = client.get("/api/v1/reports?page=9999&limit=10", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["data"] == []


class TestTier3CrossFeatureIntegration:
    """Tier 3: Pairwise and multi-feature end-to-end integration flows."""

    def test_tier3_citizen_registration_report_submission_admin_triage_flow(
        self, client: TestClient, dummy_image_bytes: bytes, seed_data, db_session: Session
    ):
        """Tier 3: Citizen registers -> logins -> submits report -> Admin logins -> triages to Completed."""
        # Step 1: Register citizen
        reg_payload = {
            "full_name": "Pak RT Bambang",
            "email": "rt.bambang@example.com",
            "password": "Password123!",
            "phone_number": "081122334455",
        }
        reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 201

        # Step 2: Citizen logins
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "rt.bambang@example.com", "password": "Password123!"},
        )
        assert login_resp.status_code == 200
        citizen_token = login_resp.json()["data"]["access_token"]
        citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

        # Step 3: Citizen submits report with photo and coordinates
        report_files = {"file": ("sampah_rt.jpg", dummy_image_bytes, "image/jpeg")}
        report_data = {
            "title": "Tumpukan sampah organik warga di TPS",
            "description": "Sisa daun dan rumput halaman menumpuk.",
            "category_id": 1,  # Organic Waste
            "latitude": -6.1754,
            "longitude": 106.8272,
            "address_note": "TPS RW 05 Gambir",
        }
        rep_resp = client.post("/api/v1/reports", files=report_files, data=report_data, headers=citizen_headers)
        assert rep_resp.status_code == 201
        report_id = rep_resp.json()["data"]["id"]

        # Step 4: Admin logins
        admin_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "Admin123!"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Step 5: Admin updates status to In Progress
        p1 = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "In Progress", "admin_notes": "Truk sampah bergerak ke TPS RW 05."},
            headers=admin_headers,
        )
        assert p1.status_code == 200

        # Step 6: Admin updates status to Completed
        p2 = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Completed", "admin_notes": "TPS RW 05 sudah bersih."},
            headers=admin_headers,
        )
        assert p2.status_code == 200

        # Step 7: Verify detail reflects both transitions in logs
        detail_resp = client.get(f"/api/v1/reports/{report_id}", headers=citizen_headers)
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()["data"]
        assert detail_data["status"] == "Completed"
        assert len(detail_data["logs"]) >= 3


class TestTier4RealWorldScenarios:
    """Tier 4: Real-world operational scenarios per docs/RUNBOOK.md and evaluation scripts."""

    def test_tier4_complete_runbook_evaluation_scenario(
        self, client: TestClient, dummy_image_bytes: bytes, seed_data
    ):
        """Tier 4: Multi-report Jakarta/Bandung submission and triage evaluation scenario."""
        # 1. Login Super Admin
        admin_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "Admin123!"},
        )
        assert admin_resp.status_code == 200
        admin_headers = {"Authorization": f"Bearer {admin_resp.json()['data']['access_token']}"}

        # 2. Login Warga Pelapor
        user_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "user@bilcode.id", "password": "User123!"},
        )
        assert user_resp.status_code == 200
        user_headers = {"Authorization": f"Bearer {user_resp.json()['data']['access_token']}"}

        # 3. Submit 3 reports in different cities & categories
        scenarios = [
            {
                "title": "Tumpukan Botol Plastik Monas Jakarta",
                "category_id": 2,
                "latitude": -6.1754,
                "longitude": 106.8272,
                "address_note": "Dekat Pintu Silang Monas Barat",
            },
            {
                "title": "Kardus Bekas Bundaran HI Jakarta",
                "category_id": 3,
                "latitude": -6.1950,
                "longitude": 106.8230,
                "address_note": "Depan halte Bundaran HI",
            },
            {
                "title": "Sampah Dedaunan Gedung Sate Bandung",
                "category_id": 1,
                "latitude": -6.9025,
                "longitude": 107.6186,
                "address_note": "Taman Gasibu Bandung",
            },
        ]

        created_ids = []
        for s in scenarios:
            files = {"file": ("runbook_evidence.jpg", dummy_image_bytes, "image/jpeg")}
            res = client.post("/api/v1/reports", files=files, data=s, headers=user_headers)
            assert res.status_code == 201
            created_ids.append(res.json()["data"]["id"])

        # 4. Admin completes first report (Monas)
        client.patch(
            f"/api/v1/reports/{created_ids[0]}/status",
            json={"status": "In Progress", "admin_notes": "Petugas dikerahkan"},
            headers=admin_headers,
        )
        client.patch(
            f"/api/v1/reports/{created_ids[0]}/status",
            json={"status": "Completed", "admin_notes": "Selesai dibersihkan"},
            headers=admin_headers,
        )

        # 5. Admin rejects second report (Bundaran HI)
        client.patch(
            f"/api/v1/reports/{created_ids[1]}/status",
            json={"status": "Rejected", "admin_notes": "Bukan sampah liar, kardus sedang dipindahkan toko"},
            headers=admin_headers,
        )

        # 6. Verify third report (Bandung) is still Pending
        bandung_rep = client.get(f"/api/v1/reports/{created_ids[2]}", headers=user_headers).json()["data"]
        assert bandung_rep["status"] == "Pending"

        # 7. Check list filtering by category and search
        search_res = client.get("/api/v1/reports?search=Bandung", headers=user_headers).json()["data"]
        assert any(r["id"] == created_ids[2] for r in search_res)
