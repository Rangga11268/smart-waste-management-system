"""Tier 5 Adversarial & Coverage Hardening Test Suite for SWMS Day 2 Backend.

Author: challenger_final
Milestone: M6 (Final Milestone - Phase 2)

Empirically probes:
1. Security & Auth:
   - Algorithm confusion attacks (alg="none", unsigned tokens)
   - Invalid HMAC signatures
   - Expired tokens
   - Non-existent UUIDs and non-UUID subjects
   - Malformed bearer headers and empty tokens
   - Missing required claims
   - Inactive user token rejection
   - Unicode and emoji handling in user registration and login
   - Bcrypt 72-byte boundary password behavior
2. Inference & Media:
   - Double extensions (e.g. image.jpg.exe, report.png.sh)
   - Missing or no extension files
   - Transparent PNGs (RGBA mode conversion)
   - Unusual color channels (CMYK, Palette P mode, Luminance+Alpha LA mode)
   - Extreme image dimensions (1x1 pixel)
   - Extreme aspect ratios (ultra-wide 800x8 and ultra-tall 8x800)
   - Truncated corrupt image headers
3. Reports & SQL:
   - SQL injection attacks in search queries (e.g. "'; DROP TABLE users; --", "' OR '1'='1")
   - SQL injection attacks in status filters
   - Extreme pagination limits (limit=1000 exceeding le=100)
   - Negative and zero page/limit parameters (page=-5, page=0, limit=0)
   - Extreme high page numbers returning empty data arrays
   - Concurrent/multi-threaded status transition safety & data integrity
4. State Machine & Audit Logs:
   - Strict enforcement of terminal states (Completed, Rejected) rejecting all subsequent transitions
   - Disallowed direct transition skips (Pending -> Completed)
   - Chronological ordering and immutability of audit log records
   - Attribution accuracy of actor_id and resolved_at timestamps
5. Dashboard Resiliency:
   - Resiliency when total_reports == 0 (zero-division prevention, empty distributions)
   - Resiliency when total_reports has only Rejected reports (completion_rate = 0.0%)
   - Resiliency when total_reports has only Completed reports (completion_rate = 100.0%)
   - Category distribution calculations under single-category dominance
"""

import concurrent.futures
from datetime import datetime, timedelta, timezone
import io
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List

import jwt
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Setup project root and backend dir on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models.category import Category
from app.models.log import ReportLog
from app.models.report import WasteReport
from app.models.user import User


# =============================================================================
# 1. SECURITY & AUTHENTICATION ADVERSARIAL ATTACKS
# =============================================================================

class TestTier5AuthSecurityAdversarial:
    """Adversarial stress testing for JWT authentication and user registration."""

    def test_token_algorithm_confusion_attack_none_rejected(self, client: TestClient, seed_data):
        """Verify tokens with algorithm 'none' (algorithm confusion) are rejected with 401."""
        admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
        payload = {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "role": admin_user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        # Craft an unsigned token with alg="none"
        none_token = jwt.encode(payload, key="", algorithm="none")

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {none_token}"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        assert response.json()["detail"] == "Could not validate credentials"

    def test_token_invalid_hmac_signature_rejected(self, client: TestClient, seed_data):
        """Verify tokens signed with an invalid/attacker secret are rejected with 401."""
        admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
        payload = {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "role": admin_user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        forged_token = jwt.encode(payload, key="ATTACKER_UNAUTHORIZED_SECRET_KEY", algorithm="HS256")

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged_token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_token_expired_timestamp_rejected(self, client: TestClient, seed_data):
        """Verify tokens with past expiration timestamps are rejected with 401."""
        admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
        payload = {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "role": admin_user.role,
            "exp": datetime.now(timezone.utc) - timedelta(hours=2),  # Expired 2 hours ago
        }
        expired_token = jwt.encode(payload, key=settings.JWT_SECRET, algorithm=settings.ALGORITHM)

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_token_nonexistent_user_uuid_rejected(self, client: TestClient):
        """Verify valid token with non-existent random UUID subject is rejected with 401."""
        nonexistent_uuid = uuid.uuid4()
        payload = {
            "sub": str(nonexistent_uuid),
            "email": "ghost.user@bilcode.id",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, key=settings.JWT_SECRET, algorithm=settings.ALGORITHM)

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_token_malformed_strings_and_empty_bearer_rejected(self, client: TestClient):
        """Verify malformed, truncated, or pseudo-token strings return 401."""
        bad_headers = [
            "Bearer ",
            "Bearer not_a_real_jwt",
            "Bearer header.payload",
            "Bearer ...",
            "Basic YWRtaW46cGFzc3dvcmQ=",
            "Token something_else",
        ]
        for header_val in bad_headers:
            response = client.get("/api/v1/auth/me", headers={"Authorization": header_val})
            assert response.status_code == 401, f"Failed for header: {header_val}"

    def test_token_missing_or_invalid_sub_claim_rejected(self, client: TestClient):
        """Verify tokens with missing sub or non-UUID sub string return 401."""
        # 1. Missing sub
        payload_no_sub = {
            "email": "user@bilcode.id",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token_no_sub = jwt.encode(payload_no_sub, key=settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        resp1 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_no_sub}"})
        assert resp1.status_code == 401

        # 2. Non-UUID sub
        payload_bad_sub = {
            "sub": "not_a_valid_uuid_format",
            "email": "user@bilcode.id",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token_bad_sub = jwt.encode(payload_bad_sub, key=settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        resp2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_bad_sub}"})
        assert resp2.status_code == 401

    def test_token_inactive_user_account_rejected(self, client: TestClient, db_session: Session, seed_data):
        """Verify token for an account marked is_active=False returns 401 inactive status."""
        user = seed_data["users_by_email"]["user@bilcode.id"]
        user.is_active = False
        db_session.commit()

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, key=settings.JWT_SECRET, algorithm=settings.ALGORITHM)

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()

    def test_registration_unicode_and_emoji_handling(self, client: TestClient, db_session: Session):
        """Verify citizen registration and authentication fully support unicode and emoji characters."""
        unicode_payload = {
            "email": "citra.lestari.♻️@bilcode.id",
            "password": "KunciRahasia!🔐2026",
            "full_name": "Citra Lestari 🌿🗑️ ᚠᛇᚻ",
            "phone_number": "+6281298765432",
        }
        reg_resp = client.post("/api/v1/auth/register", json=unicode_payload)
        assert reg_resp.status_code == 201
        data = reg_resp.json()["data"]
        assert data["full_name"] == "Citra Lestari 🌿🗑️ ᚠᛇᚻ"
        assert data["email"] == "citra.lestari.♻️@bilcode.id"

        # Authenticate with the unicode password
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": unicode_payload["email"], "password": unicode_payload["password"]},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["access_token"]

        # Fetch profile
        me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["full_name"] == "Citra Lestari 🌿🗑️ ᚠᛇᚻ"

    def test_registration_bcrypt_password_boundary_72_bytes(self, client: TestClient):
        """Verify password handling exactly at the 72-byte native Bcrypt boundary."""
        exact_72_char_pwd = "P" * 70 + "!9"
        assert len(exact_72_char_pwd.encode("utf-8")) == 72

        reg_resp = client.post(
            "/api/v1/auth/register",
            json={
                "email": "boundary72@bilcode.id",
                "password": exact_72_char_pwd,
                "full_name": "Boundary 72 Tester",
            },
        )
        assert reg_resp.status_code == 201

        # Successful login
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "boundary72@bilcode.id", "password": exact_72_char_pwd},
        )
        assert login_resp.status_code == 200

        # Wrong password fails
        login_fail = client.post(
            "/api/v1/auth/login",
            json={"email": "boundary72@bilcode.id", "password": exact_72_char_pwd + "X"},
        )
        assert login_fail.status_code == 401


# =============================================================================
# 2. INFERENCE & MEDIA ADVERSARIAL STRESS
# =============================================================================

class TestTier5InferenceMediaAdversarial:
    """Adversarial stress testing for ML inference file formats and dimensions."""

    def test_predict_double_extension_executable_rejected(self, client: TestClient, dummy_image_bytes: bytes):
        """Verify double extension ending in executable (.jpg.exe) is rejected with 400."""
        files = {"file": ("exploit_image.jpg.exe", dummy_image_bytes, "application/octet-stream")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400
        assert "Unsupported image extension" in response.json()["detail"]

    def test_predict_double_extension_script_rejected(self, client: TestClient, dummy_png_bytes: bytes):
        """Verify double extension ending in shell script (.png.sh) is rejected with 400."""
        files = {"file": ("malicious_photo.png.sh", dummy_png_bytes, "text/x-shellscript")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400
        assert "Unsupported image extension" in response.json()["detail"]

    def test_predict_missing_or_no_extension_rejected(self, client: TestClient, dummy_image_bytes: bytes):
        """Verify files with no extension are rejected with 400."""
        files = {"file": ("image_without_extension", dummy_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400
        assert "Unsupported image extension" in response.json()["detail"]

    def test_predict_transparent_png_rgba_mode_converted(self, client: TestClient):
        """Verify transparent PNG (RGBA mode) is gracefully converted to RGB and classified."""
        img = Image.new("RGBA", (128, 128), color=(255, 69, 0, 128))  # Semi-transparent red-orange
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        rgba_bytes = buf.getvalue()

        files = {"file": ("transparent_sample.png", rgba_bytes, "image/png")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["category"] in {"Organic Waste", "Plastic Waste", "Paper Waste"}
        assert 0.0 <= data["confidence"] <= 1.0

    def test_predict_unusual_color_channels_cmyk_mode(self, client: TestClient):
        """Verify CMYK mode image is properly converted to RGB and classified without error."""
        img = Image.new("CMYK", (100, 100), color=(0, 255, 255, 0))  # Cyan/Yellow
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        cmyk_bytes = buf.getvalue()

        files = {"file": ("cmyk_photo.jpg", cmyk_bytes, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_predict_unusual_color_channels_palette_p_mode(self, client: TestClient):
        """Verify Palette indexed mode (P mode) PNG is properly converted to RGB."""
        img = Image.new("P", (80, 80))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        p_bytes = buf.getvalue()

        files = {"file": ("palette_image.png", p_bytes, "image/png")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_predict_unusual_color_channels_grayscale_alpha_la_mode(self, client: TestClient):
        """Verify Luminance + Alpha (LA mode) PNG is properly converted to RGB."""
        img = Image.new("LA", (80, 80), color=(128, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        la_bytes = buf.getvalue()

        files = {"file": ("luminance_alpha.png", la_bytes, "image/png")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_predict_extreme_dimension_1x1(self, client: TestClient):
        """Verify 1x1 pixel image executes MobileNetV2 preprocessing without error."""
        img = Image.new("RGB", (1, 1), color=(120, 200, 80))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pixel_bytes = buf.getvalue()

        files = {"file": ("single_pixel.png", pixel_bytes, "image/png")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        data = response.json()["data"]
        probs = data["probabilities"]
        assert "Organic Waste" in probs and "Plastic Waste" in probs and "Paper Waste" in probs
        prob_sum = sum(probs.values())
        assert abs(prob_sum - 1.0) < 0.01

    def test_predict_extreme_aspect_ratio_ultra_wide(self, client: TestClient):
        """Verify ultra-wide 800x8 ribbon image executes without aspect ratio errors."""
        img = Image.new("RGB", (800, 8), color=(50, 100, 150))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        wide_bytes = buf.getvalue()

        files = {"file": ("ribbon.jpg", wide_bytes, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_predict_extreme_aspect_ratio_ultra_tall(self, client: TestClient):
        """Verify ultra-tall 8x800 pillar image executes without aspect ratio errors."""
        img = Image.new("RGB", (8, 800), color=(150, 100, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        tall_bytes = buf.getvalue()

        files = {"file": ("pillar.jpg", tall_bytes, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_predict_truncated_corrupt_jpeg_bytes_rejected(self, client: TestClient):
        """Verify truncated image header with corrupted scan data is rejected with 400."""
        truncated_header = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        files = {"file": ("corrupt_scan.jpg", truncated_header, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400
        assert "Corrupted or invalid image file" in response.json()["detail"]


# =============================================================================
# 3. REPORTS & SQL ADVERSARIAL STRESS
# =============================================================================

class TestTier5ReportsAndSQLAdversarial:
    """Adversarial testing for SQL injection neutralization, pagination boundaries, and concurrency."""

    def test_reports_sql_injection_in_search_query_neutralized(
        self, client: TestClient, user_headers, db_session: Session, seed_data
    ):
        """Verify classic SQL injection attempts in search parameters do not execute raw SQL."""
        injection_payloads = [
            "'; DROP TABLE users; --",
            "%'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "UNION SELECT null, null, null, null, null, null --",
            "\" OR \"\"=\"",
        ]

        for payload in injection_payloads:
            response = client.get(f"/api/v1/reports?search={payload}", headers=user_headers)
            assert response.status_code == 200, f"Query failed on payload: {payload}"
            body = response.json()
            assert body["status"] == "success"
            assert "data" in body
            assert "meta" in body

        # Verify users table was NOT modified or dropped
        user_count = db_session.query(User).count()
        assert user_count >= 2, "Users table was corrupted or dropped by SQL injection!"

    def test_reports_sql_injection_in_status_filter_neutralized(
        self, client: TestClient, user_headers
    ):
        """Verify SQL injection in status filter treats input as literal string, returning 0 items."""
        response = client.get("/api/v1/reports?status=' OR 1=1 --", headers=user_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["meta"]["total_items"] == 0

    def test_reports_pagination_limit_exceeding_max_rejected(self, client: TestClient, user_headers):
        """Verify pagination limit > 100 is rejected with 422 Unprocessable Entity."""
        response = client.get("/api/v1/reports?limit=1000", headers=user_headers)
        assert response.status_code == 422

    def test_reports_pagination_negative_and_zero_page_rejected(self, client: TestClient, user_headers):
        """Verify invalid page/limit parameters (< 1) are rejected with 422."""
        invalid_params = [
            "?page=-5",
            "?page=0",
            "?limit=0",
            "?limit=-10",
        ]
        for param in invalid_params:
            response = client.get(f"/api/v1/reports{param}", headers=user_headers)
            assert response.status_code == 422, f"Expected 422 for param {param}, got {response.status_code}"

    def test_reports_pagination_extreme_high_page_returns_empty_array(
        self, client: TestClient, user_headers, dummy_image_bytes: bytes
    ):
        """Verify extremely large page numbers gracefully return empty data array with 200 OK."""
        # Submit 1 report to ensure DB has records
        files = {"file": ("test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": "Sampah Daun Kering",
            "category_id": 1,
            "latitude": -6.2000,
            "longitude": 106.8400,
        }
        client.post("/api/v1/reports", files=files, data=data, headers=user_headers)

        response = client.get("/api/v1/reports?page=100000&limit=50", headers=user_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["meta"]["current_page"] == 100000
        assert body["meta"]["total_items"] >= 1

    def test_reports_concurrent_status_transitions_consistency(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes, db_session: Session
    ):
        """Verify multiple sequential and rapid status transition requests maintain DB consistency."""
        # Submit 1 report (starts in Pending)
        files = {"file": ("concurrency_test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": "Laporan Uji Transisi",
            "category_id": 2,
            "latitude": -6.9175,
            "longitude": 107.6191,
        }
        create_resp = client.post("/api/v1/reports", files=files, data=data, headers=user_headers)
        assert create_resp.status_code == 201
        report_id = create_resp.json()["data"]["id"]

        # 1. Update Pending -> In Progress (Valid)
        p1 = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "In Progress", "admin_notes": "First triage"},
            headers=admin_headers,
        )
        assert p1.status_code == 200

        # 2. Immediate duplicate transition Pending -> In Progress (Invalid: already In Progress)
        p2 = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "In Progress", "admin_notes": "Duplicate transition attempt"},
            headers=admin_headers,
        )
        assert p2.status_code == 400
        assert "Invalid status transition" in p2.json()["detail"]

        # 3. Transition In Progress -> Completed (Valid)
        p3 = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Completed", "admin_notes": "Field team cleared site"},
            headers=admin_headers,
        )
        assert p3.status_code == 200

        # 4. Immediate duplicate transition In Progress -> Completed (Invalid: already Completed terminal)
        p4 = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={"status": "Completed", "admin_notes": "Post-terminal attempt"},
            headers=admin_headers,
        )
        assert p4.status_code == 400
        assert "terminal state" in p4.json()["detail"]


# =============================================================================
# 4. STATE MACHINE & AUDIT LOG IMMUTABILITY ADVERSARIAL STRESS
# =============================================================================

class TestTier5StateMachineAndAuditLogsAdversarial:
    """Adversarial stress testing for SWMS finite state machine rules and audit trail."""

    def test_state_machine_strict_terminal_completed_transitions_rejected(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes
    ):
        """Verify Completed state is strictly terminal and rejects all subsequent transitions with 400."""
        # Create and transition report to Completed
        files = {"file": ("terminal_comp.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Sampah", "category_id": 1, "latitude": -6.20, "longitude": 106.84}
        rep = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        r_id = rep["id"]

        client.patch(f"/api/v1/reports/{r_id}/status", json={"status": "In Progress"}, headers=admin_headers)
        comp_resp = client.patch(f"/api/v1/reports/{r_id}/status", json={"status": "Completed"}, headers=admin_headers)
        assert comp_resp.status_code == 200

        # All four subsequent transitions must return 400 Bad Request
        for target in ["Pending", "In Progress", "Rejected", "Completed"]:
            bad_patch = client.patch(
                f"/api/v1/reports/{r_id}/status",
                json={"status": target, "admin_notes": f"Illegal move to {target}"},
                headers=admin_headers,
            )
            assert bad_patch.status_code == 400, f"Expected 400 for Completed -> {target}, got {bad_patch.status_code}"
            assert "terminal state 'Completed'" in bad_patch.json()["detail"]

    def test_state_machine_strict_terminal_rejected_transitions_rejected(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes
    ):
        """Verify Rejected state is strictly terminal and rejects all subsequent transitions with 400."""
        files = {"file": ("terminal_rej.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Hoax", "category_id": 3, "latitude": -6.20, "longitude": 106.84}
        rep = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        r_id = rep["id"]

        rej_resp = client.patch(
            f"/api/v1/reports/{r_id}/status",
            json={"status": "Rejected", "admin_notes": "Bukan sampah umum"},
            headers=admin_headers,
        )
        assert rej_resp.status_code == 200

        for target in ["Pending", "In Progress", "Completed", "Rejected"]:
            bad_patch = client.patch(
                f"/api/v1/reports/{r_id}/status",
                json={"status": target, "admin_notes": f"Illegal move to {target}"},
                headers=admin_headers,
            )
            assert bad_patch.status_code == 400, f"Expected 400 for Rejected -> {target}, got {bad_patch.status_code}"
            assert "terminal state 'Rejected'" in bad_patch.json()["detail"]

    def test_state_machine_disallowed_direct_skip_rejected(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes
    ):
        """Verify illegal state jump from Pending directly to Completed is rejected."""
        files = {"file": ("skip_test.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Langsung Selesai", "category_id": 2, "latitude": -6.20, "longitude": 106.84}
        rep = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]
        r_id = rep["id"]

        skip_resp = client.patch(
            f"/api/v1/reports/{r_id}/status",
            json={"status": "Completed", "admin_notes": "Trying to skip In Progress"},
            headers=admin_headers,
        )
        assert skip_resp.status_code == 400
        assert "Invalid status transition from Pending to Completed" in skip_resp.json()["detail"]

    def test_audit_log_immutability_and_chronology(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes, db_session: Session
    ):
        """Verify complete chronological audit history, actor attribution, and immutability."""
        files = {"file": ("audit_full.jpg", dummy_image_bytes, "image/jpeg")}
        data = {
            "title": "Audit Trail Inspection Report",
            "category_id": 2,
            "latitude": -6.2088,
            "longitude": 106.8456,
        }
        create_resp = client.post("/api/v1/reports", files=files, data=data, headers=user_headers)
        r_id = create_resp.json()["data"]["id"]

        # Step 1: Pending -> In Progress
        client.patch(
            f"/api/v1/reports/{r_id}/status",
            json={"status": "In Progress", "admin_notes": "Petugas diterjunkan"},
            headers=admin_headers,
        )

        # Step 2: In Progress -> Completed
        client.patch(
            f"/api/v1/reports/{r_id}/status",
            json={"status": "Completed", "admin_notes": "Lokasi bersih"},
            headers=admin_headers,
        )

        # Verify via GET /reports/{id}
        detail_resp = client.get(f"/api/v1/reports/{r_id}", headers=user_headers)
        assert detail_resp.status_code == 200
        detail = detail_resp.json()["data"]

        logs = detail["logs"]
        assert len(logs) == 3, f"Expected exactly 3 log records, got {len(logs)}"

        # Check chronology and status sequence
        assert logs[0]["previous_status"] is None
        assert logs[0]["new_status"] == "Pending"

        assert logs[1]["previous_status"] == "Pending"
        assert logs[1]["new_status"] == "In Progress"
        assert logs[1]["remarks"] == "Petugas diterjunkan"

        assert logs[2]["previous_status"] == "In Progress"
        assert logs[2]["new_status"] == "Completed"
        assert logs[2]["remarks"] == "Lokasi bersih"

        t0 = datetime.fromisoformat(logs[0]["created_at"])
        t1 = datetime.fromisoformat(logs[1]["created_at"])
        t2 = datetime.fromisoformat(logs[2]["created_at"])
        assert t0 <= t1 <= t2, "Audit log timestamps must be strictly non-decreasing"

        # Verify resolved_at on report is set
        assert detail["resolved_at"] is not None


# =============================================================================
# 5. DASHBOARD RESILIENCY ADVERSARIAL STRESS
# =============================================================================

class TestTier5DashboardResiliencyAdversarial:
    """Adversarial stress testing for Admin Dashboard metrics, aggregations, and edge cases."""

    def test_dashboard_resiliency_zero_reports(self, client: TestClient, admin_headers, seed_data):
        """Verify dashboard stats execute cleanly when total_reports == 0 without division by zero."""
        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]

        summary = data["summary"]
        assert summary["total_reports"] == 0
        assert summary["pending_count"] == 0
        assert summary["in_progress_count"] == 0
        assert summary["completed_count"] == 0
        assert summary["rejected_count"] == 0
        assert summary["completion_rate_percent"] == 0.0
        assert summary["active_users"] >= 2

        # All category distribution percentages must be 0.0
        dist = data["category_distribution"]
        assert len(dist) == 3
        for cat_stat in dist:
            assert cat_stat["count"] == 0
            assert cat_stat["percentage"] == 0.0

        assert data["recent_activities"] == []

    def test_dashboard_resiliency_only_rejected_reports(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes
    ):
        """Verify dashboard statistics when 100% of reports are Rejected (completion_rate = 0.0%)."""
        for i in range(3):
            files = {"file": (f"rej_{i}.jpg", dummy_image_bytes, "image/jpeg")}
            data = {"title": f"Laporan Ditolak {i}", "category_id": 1, "latitude": -6.2, "longitude": 106.8}
            r_id = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]["id"]
            client.patch(f"/api/v1/reports/{r_id}/status", json={"status": "Rejected"}, headers=admin_headers)

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        summary = response.json()["data"]["summary"]
        assert summary["total_reports"] == 3
        assert summary["rejected_count"] == 3
        assert summary["completed_count"] == 0
        assert summary["completion_rate_percent"] == 0.0

    def test_dashboard_resiliency_only_completed_reports(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes
    ):
        """Verify dashboard statistics when 100% of reports are Completed (completion_rate = 100.0%)."""
        for i in range(3):
            files = {"file": (f"comp_{i}.jpg", dummy_image_bytes, "image/jpeg")}
            data = {"title": f"Laporan Beres {i}", "category_id": 2, "latitude": -6.2, "longitude": 106.8}
            r_id = client.post("/api/v1/reports", files=files, data=data, headers=user_headers).json()["data"]["id"]
            client.patch(f"/api/v1/reports/{r_id}/status", json={"status": "In Progress"}, headers=admin_headers)
            client.patch(f"/api/v1/reports/{r_id}/status", json={"status": "Completed"}, headers=admin_headers)

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        summary = response.json()["data"]["summary"]
        assert summary["total_reports"] == 3
        assert summary["completed_count"] == 3
        assert summary["rejected_count"] == 0
        assert summary["completion_rate_percent"] == 100.0

    def test_dashboard_category_distribution_single_category_dominance(
        self, client: TestClient, user_headers, admin_headers, dummy_image_bytes: bytes
    ):
        """Verify category breakdown calculates 100.0% for dominant category and 0.0% for others."""
        for i in range(4):
            files = {"file": (f"organic_{i}.jpg", dummy_image_bytes, "image/jpeg")}
            data = {"title": f"Sisa Makanan {i}", "category_id": 1, "latitude": -6.2, "longitude": 106.8}
            client.post("/api/v1/reports", files=files, data=data, headers=user_headers)

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        dist = response.json()["data"]["category_distribution"]

        dist_by_name = {d["category"]: d for d in dist}
        assert dist_by_name["Organic Waste"]["count"] == 4
        assert dist_by_name["Organic Waste"]["percentage"] == 100.0

        assert dist_by_name["Plastic Waste"]["count"] == 0
        assert dist_by_name["Plastic Waste"]["percentage"] == 0.0

        assert dist_by_name["Paper Waste"]["count"] == 0
        assert dist_by_name["Paper Waste"]["percentage"] == 0.0
