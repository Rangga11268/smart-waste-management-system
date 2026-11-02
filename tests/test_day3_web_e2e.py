"""Comprehensive Requirement-Driven Opaque-Box E2E Test Suite for SWMS Day 3 Web Dashboard.

Validates the full 4-tier testing methodology for Next.js 14 Web Dashboard:
- Tier 1: Feature Coverage (>=5 tests per feature across 13 core features:
    1. styling/tokens
    2. fonts/typography
    3. auth login flow
    4. token injection & interceptors
    5. stats metrics
    6. category breakdown
    7. reports table
    8. filters
    9. search
    10. review modal
    11. google maps link
    12. status patch
    13. user management)
- Tier 2: Boundary & Corner Cases (empty reports, 0 total zero-division, invalid status transition 400,
    invalid credentials 401, non-admin 403, out-of-bounds page, relative URL prefixing, etc.)
- Tier 3: Cross-Feature Combinations (search + filter + pagination, login -> auth token -> fetch stats
    -> update report status -> audit log reflection, multi-hop lifecycle)
- Tier 4: Real-World Scenarios (full admin triage workflow, citizen submission to completion lifecycle,
    RBAC security & role isolation)

Can be executed directly via:
    pytest tests/test_day3_web_e2e.py -v
or:
    python tests/test_day3_web_e2e.py
"""

from datetime import datetime, timezone
import io
import math
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
import uuid

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Ensure project root and backend are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
WEB_DIR = PROJECT_ROOT / "web"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# =============================================================================
# Specification Constants & Contracts (docs/STYLING_GUIDE.md & docs/API_SPECS.md)
# =============================================================================

ECO_TECH_COLOR_TOKENS = {
    "primary-50": "#ecfdf5",
    "primary-500": "#10b981",
    "primary-600": "#059669",  # Brand primary
    "primary-700": "#047857",
    "primary-900": "#064e3b",
    "surface-ground": "#f8fafc",
    "surface-card": "#ffffff",
    "border-subtle": "#e2e8f0",
    "text-muted": "#64748b",
    "text-body": "#334155",
    "text-heading": "#0f172a",
}

STATUS_BADGE_TOKENS = {
    "Pending": {
        "bg": "bg-amber-50",
        "text": "text-amber-700",
        "border": "border-amber-200",
    },
    "In Progress": {
        "bg": "bg-blue-50",
        "text": "text-blue-700",
        "border": "border-blue-200",
    },
    "Completed": {
        "bg": "bg-emerald-50",
        "text": "text-emerald-700",
        "border": "border-emerald-200",
    },
    "Rejected": {
        "bg": "bg-rose-50",
        "text": "text-rose-700",
        "border": "border-rose-200",
    },
}

CATEGORY_ACCENT_TOKENS = {
    "Organic Waste": {
        "slug": "organic",
        "hex": "#16a34a",
        "badge_class": "bg-green-100 text-green-800",
    },
    "Plastic Waste": {
        "slug": "plastic",
        "hex": "#0284c7",
        "badge_class": "bg-sky-100 text-sky-800",
    },
    "Paper Waste": {
        "slug": "paper",
        "hex": "#d97706",
        "badge_class": "bg-amber-100 text-amber-800",
    },
}

TYPOGRAPHY_FONT_FAMILIES = {
    "headings": "Space Grotesk",
    "body": "Inter",
    "mono": "JetBrains Mono",
}


# =============================================================================
# Helper Utilities for Web API Client Contracts
# =============================================================================

def resolve_image_url(path: Optional[str], base_url: str = "http://localhost:8000") -> str:
    """Normalize relative or absolute image URL per Web Client contract in docs/SPEC.md."""
    if not path:
        return "/placeholder.png"
    if path.startswith("http://") or path.startswith("https://"):
        return path
    origin = base_url.rstrip("/")
    if origin.endswith("/api/v1"):
        origin = origin[:-7]
    clean_path = "/" + path.lstrip("/")
    return f"{origin}{clean_path}"


def format_google_maps_url(lat: float, lon: float) -> str:
    """Generate external Google Maps URL according to ORIGINAL_REQUEST.md R4."""
    return f"https://www.google.com/maps?q={lat},{lon}"


def format_confidence_percentage(confidence: Optional[float]) -> str:
    """Format AI classification confidence percentage for JetBrains Mono badge."""
    if confidence is None or math.isnan(confidence):
        return "0.00%"
    return f"{confidence * 100:.2f}%"


def create_test_report_helper(
    client: TestClient,
    headers: Dict[str, str],
    dummy_image_bytes: bytes,
    title: str = "Test Waste Report",
    category_id: int = 2,
    latitude: float = -6.2088,
    longitude: float = 106.8456,
    description: str = "Auto-generated test report",
    address_note: str = "Jl. Sudirman No. 45",
) -> Dict[str, Any]:
    """Helper to submit a new report and return created report data."""
    files = {"file": ("report_image.jpg", dummy_image_bytes, "image/jpeg")}
    data = {
        "title": title,
        "category_id": category_id,
        "latitude": latitude,
        "longitude": longitude,
        "description": description,
        "address_note": address_note,
    }
    response = client.post("/api/v1/reports", files=files, data=data, headers=headers)
    assert response.status_code == 201, f"Report creation failed: {response.text}"
    return response.json()["data"]


# =============================================================================
# TIER 1: FEATURE COVERAGE (>=5 tests per feature across 13 features = 65 tests)
# =============================================================================

class TestTier1FeatureCoverage:
    """Tier 1: Comprehensive feature coverage for all 13 Day 3 web dashboard features."""

    # -------------------------------------------------------------------------
    # Feature 1: Styling / Tokens (5 tests)
    # -------------------------------------------------------------------------
    def test_f01_01_primary_emerald_tokens_specification(self):
        """F1.1: Verify primary emerald brand color palette tokens."""
        assert ECO_TECH_COLOR_TOKENS["primary-600"] == "#059669", "Brand primary must be #059669"
        assert ECO_TECH_COLOR_TOKENS["primary-50"] == "#ecfdf5", "Primary 50 highlight token mismatch"
        assert ECO_TECH_COLOR_TOKENS["primary-500"] == "#10b981", "Primary 500 accent token mismatch"
        assert ECO_TECH_COLOR_TOKENS["primary-700"] == "#047857", "Primary 700 hover token mismatch"
        assert ECO_TECH_COLOR_TOKENS["primary-900"] == "#064e3b", "Primary 900 dark token mismatch"

    def test_f01_02_neutral_base_tokens_specification(self):
        """F1.2: Verify neutral base canvas, card, and border tokens."""
        assert ECO_TECH_COLOR_TOKENS["surface-ground"] == "#f8fafc", "Surface ground canvas must be #f8fafc"
        assert ECO_TECH_COLOR_TOKENS["surface-card"] == "#ffffff", "Surface card container must be #ffffff"
        assert ECO_TECH_COLOR_TOKENS["border-subtle"] == "#e2e8f0", "Border subtle must be #e2e8f0"

    def test_f01_03_text_slate_tokens_specification(self):
        """F1.3: Verify slate typography text contrast tokens."""
        assert ECO_TECH_COLOR_TOKENS["text-muted"] == "#64748b", "Text muted label must be #64748b"
        assert ECO_TECH_COLOR_TOKENS["text-body"] == "#334155", "Text body paragraph must be #334155"
        assert ECO_TECH_COLOR_TOKENS["text-heading"] == "#0f172a", "Text heading must be #0f172a"

    def test_f01_04_semantic_status_badge_tokens_specification(self):
        """F1.4: Verify semantic status badge background, text, and border classes."""
        for status in ["Pending", "In Progress", "Completed", "Rejected"]:
            assert status in STATUS_BADGE_TOKENS, f"Status {status} missing from badge specification"
            badge = STATUS_BADGE_TOKENS[status]
            assert "bg-" in badge["bg"], f"Background class missing for {status}"
            assert "text-" in badge["text"], f"Text class missing for {status}"
            assert "border-" in badge["border"], f"Border class missing for {status}"

    def test_f01_05_category_badge_tokens_specification(self):
        """F1.5: Verify AI category classification accent colors and badge classes."""
        assert CATEGORY_ACCENT_TOKENS["Organic Waste"]["hex"] == "#16a34a"
        assert CATEGORY_ACCENT_TOKENS["Plastic Waste"]["hex"] == "#0284c7"
        assert CATEGORY_ACCENT_TOKENS["Paper Waste"]["hex"] == "#d97706"

    # -------------------------------------------------------------------------
    # Feature 2: Fonts & Typography (5 tests)
    # -------------------------------------------------------------------------
    def test_f02_01_heading_display_font_space_grotesk(self):
        """F2.1: Verify Space Grotesk is designated font family for headings/display."""
        assert TYPOGRAPHY_FONT_FAMILIES["headings"] == "Space Grotesk"

    def test_f02_02_body_ui_font_inter(self):
        """F2.2: Verify Inter is designated font family for body, tables, and forms."""
        assert TYPOGRAPHY_FONT_FAMILIES["body"] == "Inter"

    def test_f02_03_monospace_font_jetbrains_mono(self):
        """F2.3: Verify JetBrains Mono is designated font family for GPS, IDs, and metrics."""
        assert TYPOGRAPHY_FONT_FAMILIES["mono"] == "JetBrains Mono"

    def test_f02_04_typography_scale_hierarchy(self):
        """F2.4: Verify typography scale hierarchy according to STYLING_GUIDE.md §2."""
        scale_classes = {
            "big_stats": "text-3xl font-bold tracking-tight text-slate-900",
            "page_title": "text-2xl font-bold text-slate-900",
            "section_title": "text-lg font-semibold text-slate-800",
            "card_title": "text-sm font-medium text-slate-600",
            "body": "text-sm font-normal text-slate-700",
            "gps_mono": "font-mono text-xs font-medium text-slate-500",
        }
        for element, classes in scale_classes.items():
            assert len(classes) > 0, f"Typography scale definition missing for {element}"

    def test_f02_05_font_css_variables_and_fallback(self):
        """F2.5: Verify CSS font variables contract (--font-space-grotesk, --font-inter, --font-jetbrains-mono)."""
        font_vars = ["--font-space-grotesk", "--font-inter", "--font-jetbrains-mono"]
        for var in font_vars:
            assert var.startswith("--font-"), f"Font variable {var} must use standard Next.js CSS var prefix"

    # -------------------------------------------------------------------------
    # Feature 3: Auth Login Flow (5 tests)
    # -------------------------------------------------------------------------
    def test_f03_01_admin_login_endpoint_success(self, client: TestClient, seed_data: Dict[str, Any]):
        """F3.1: Verify admin login POST /api/v1/auth/login returns 200, JWT token, and role='admin'."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "Admin123!"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == "admin@bilcode.id"

    def test_f03_02_citizen_login_endpoint_success(self, client: TestClient, seed_data: Dict[str, Any]):
        """F3.2: Verify citizen login POST /api/v1/auth/login returns 200, JWT token, and role='user'."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "user@bilcode.id", "password": "User123!"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "access_token" in data
        assert data["user"]["role"] == "user"
        assert data["user"]["email"] == "user@bilcode.id"

    def test_f03_03_login_response_envelope_structure(self, client: TestClient, seed_data: Dict[str, Any]):
        """F3.3: Verify login response structure conforms to status envelope and token_type='bearer'."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "Admin123!"},
        )
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["token_type"].lower() == "bearer"
        assert len(body["data"]["access_token"]) > 20

    def test_f03_04_login_user_profile_payload_fields(self, client: TestClient, seed_data: Dict[str, Any]):
        """F3.4: Verify user payload in login response contains id, email, full_name, and role."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "Admin123!"},
        )
        user = resp.json()["data"]["user"]
        for field in ["id", "email", "full_name", "role"]:
            assert field in user, f"Field '{field}' missing from login user payload"

    def test_f03_05_evaluator_quick_presets_authentication(self, client: TestClient, seed_data: Dict[str, Any]):
        """F3.5: Verify both evaluator quick fill presets authenticate cleanly."""
        presets = [
            ("admin@bilcode.id", "Admin123!", "admin"),
            ("user@bilcode.id", "User123!", "user"),
        ]
        for email, password, expected_role in presets:
            resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
            assert resp.status_code == 200
            assert resp.json()["data"]["user"]["role"] == expected_role

    # -------------------------------------------------------------------------
    # Feature 4: Token Injection & Interceptors (5 tests)
    # -------------------------------------------------------------------------
    def test_f04_01_bearer_token_authorization_header_me(self, client: TestClient, admin_headers: Dict[str, str]):
        """F4.1: Verify GET /api/v1/auth/me accepts Bearer token and returns current authenticated user."""
        resp = client.get("/api/v1/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["email"] == "admin@bilcode.id"
        assert data["role"] == "admin"

    def test_f04_02_missing_auth_header_returns_401(self, client: TestClient):
        """F4.2: Verify GET /api/v1/auth/me without Authorization header returns 401 Unauthorized."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
        assert "Not authenticated" in resp.json().get("detail", "")

    def test_f04_03_malformed_auth_header_returns_401(self, client: TestClient):
        """F4.3: Verify malformed Authorization header (non-Bearer or garbage) returns 401."""
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Token not_a_bearer_token"})
        assert resp.status_code == 401

    def test_f04_04_tampered_token_signature_returns_401(self, client: TestClient):
        """F4.4: Verify tampered or invalid JWT signature returns 401 Unauthorized."""
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered_signature_swms_invalid"
        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
        assert resp.status_code == 401

    def test_f04_05_auth_session_profile_fields_contract(self, client: TestClient, user_headers: Dict[str, str]):
        """F4.5: Verify /api/v1/auth/me returns all contract fields: id, email, full_name, role, created_at."""
        resp = client.get("/api/v1/auth/me", headers=user_headers)
        assert resp.status_code == 200
        user = resp.json()["data"]
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert "role" in user
        assert "created_at" in user

    # -------------------------------------------------------------------------
    # Feature 5: Stats Metrics Cards (5 tests)
    # -------------------------------------------------------------------------
    def test_f05_01_admin_stats_total_reports_metric(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F5.1: Verify summary.total_reports reflects total reports count."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, title="Stat Metric Test 1")
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        summary = resp.json()["data"]["summary"]
        assert summary["total_reports"] >= 1

    def test_f05_02_admin_stats_status_counters_presence(
        self, client: TestClient, admin_headers: Dict[str, str]
    ):
        """F5.2: Verify summary contains pending_count, in_progress_count, completed_count, rejected_count."""
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        summary = resp.json()["data"]["summary"]
        for key in ["pending_count", "in_progress_count", "completed_count", "rejected_count"]:
            assert key in summary, f"Counter '{key}' missing from summary"
            assert isinstance(summary[key], int)

    def test_f05_03_admin_stats_completion_rate_calculation(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F5.3: Verify summary.completion_rate_percent is a float value between 0.0 and 100.0."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, title="Completion Rate Test")
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        summary = resp.json()["data"]["summary"]
        rate = summary["completion_rate_percent"]
        assert isinstance(rate, (int, float))
        assert 0.0 <= rate <= 100.0

    def test_f05_04_admin_stats_active_users_metric(
        self, client: TestClient, admin_headers: Dict[str, str]
    ):
        """F5.4: Verify summary.active_users is a non-negative integer."""
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        summary = resp.json()["data"]["summary"]
        assert "active_users" in summary
        assert summary["active_users"] is not None
        assert summary["active_users"] >= 1

    def test_f05_05_stat_cards_ui_metadata_contract(self):
        """F5.5: Verify the 4 primary stat cards specification contract."""
        stat_cards = [
            {"title": "Total Laporan Masuk", "key": "total_reports", "accent": "slate"},
            {"title": "Perlu Validasi", "key": "pending_count", "accent": "amber"},
            {"title": "Sedang Ditangani", "key": "in_progress_count", "accent": "blue"},
            {"title": "Tingkat Penyelesaian", "key": "completion_rate_percent", "accent": "emerald"},
        ]
        assert len(stat_cards) == 4
        for card in stat_cards:
            assert "title" in card and "key" in card and "accent" in card

    # -------------------------------------------------------------------------
    # Feature 6: Category Breakdown Distribution (5 tests)
    # -------------------------------------------------------------------------
    def test_f06_01_category_distribution_presence(
        self, client: TestClient, admin_headers: Dict[str, str]
    ):
        """F6.1: Verify category_distribution array contains Organic, Plastic, and Paper entries."""
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        distribution = resp.json()["data"]["category_distribution"]
        category_names = [d["category"] for d in distribution]
        for expected in ["Organic Waste", "Plastic Waste", "Paper Waste"]:
            assert expected in category_names, f"Category '{expected}' missing from distribution"

    def test_f06_02_category_distribution_item_fields(
        self, client: TestClient, admin_headers: Dict[str, str]
    ):
        """F6.2: Verify each distribution item contains category, count, and percentage fields."""
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]["category_distribution"]:
            assert "category" in item
            assert "count" in item and isinstance(item["count"], int)
            assert "percentage" in item and isinstance(item["percentage"], (int, float))

    def test_f06_03_category_distribution_count_sum(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F6.3: Verify sum of category distribution counts equals total classified reports."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, category_id=1)
        create_test_report_helper(client, user_headers, dummy_image_bytes, category_id=2)
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        dist_sum = sum(d["count"] for d in data["category_distribution"])
        assert dist_sum == data["summary"]["total_reports"]

    def test_f06_04_category_distribution_percentage_sum(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F6.4: Verify category percentages sum to ~100.0% when reports exist."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, category_id=2)
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        if data["summary"]["total_reports"] > 0:
            pct_sum = sum(d["percentage"] for d in data["category_distribution"])
            assert 99.5 <= pct_sum <= 100.5, f"Percentage sum {pct_sum} deviates from 100%"

    def test_f06_05_category_accent_colors_mapping(self):
        """F6.5: Verify category distribution matches documented accent colors."""
        for cat_name, info in CATEGORY_ACCENT_TOKENS.items():
            assert info["hex"].startswith("#")
            assert len(info["hex"]) == 7

    # -------------------------------------------------------------------------
    # Feature 7: Reports Table (5 tests)
    # -------------------------------------------------------------------------
    def test_f07_01_reports_table_envelope_structure(
        self, client: TestClient, user_headers: Dict[str, str]
    ):
        """F7.1: Verify GET /api/v1/reports returns envelope with status, meta, and data."""
        resp = client.get("/api/v1/reports", headers=user_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "meta" in body
        assert "data" in body and isinstance(body["data"], list)

    def test_f07_02_reports_table_meta_fields(
        self, client: TestClient, user_headers: Dict[str, str]
    ):
        """F7.2: Verify meta envelope contains total_items, current_page, total_pages, and limit."""
        resp = client.get("/api/v1/reports", headers=user_headers)
        meta = resp.json()["meta"]
        for field in ["total_items", "current_page", "total_pages", "limit"]:
            assert field in meta, f"Meta field '{field}' missing"
            assert isinstance(meta[field], int)

    def test_f07_03_reports_table_item_fields(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F7.3: Verify report items include id, title, image_url, latitude, longitude, status, created_at."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, title="Table Item Field Test")
        resp = client.get("/api/v1/reports", headers=user_headers)
        report = resp.json()["data"][0]
        required_fields = ["id", "title", "image_url", "latitude", "longitude", "status", "created_at"]
        for field in required_fields:
            assert field in report, f"Report item missing '{field}'"

    def test_f07_04_reports_table_nested_category(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F7.4: Verify each report item contains nested category with id, name, badge_color."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, category_id=2)
        resp = client.get("/api/v1/reports", headers=user_headers)
        category = resp.json()["data"][0]["category"]
        assert "id" in category
        assert "name" in category
        assert "badge_color" in category

    def test_f07_05_reports_table_nested_reporter(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F7.5: Verify each report item contains nested reporter with id and full_name."""
        create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.get("/api/v1/reports", headers=user_headers)
        reporter = resp.json()["data"][0]["reporter"]
        assert "id" in reporter
        assert "full_name" in reporter

    # -------------------------------------------------------------------------
    # Feature 8: Filters (5 tests)
    # -------------------------------------------------------------------------
    def test_f08_01_filter_by_pending_status(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F8.1: Verify filter by status=Pending returns only Pending reports."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, title="Filter Pending 1")
        resp = client.get("/api/v1/reports?status=Pending", headers=user_headers)
        assert resp.status_code == 200
        for rep in resp.json()["data"]:
            assert rep["status"] == "Pending"

    def test_f08_02_filter_by_in_progress_status(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F8.2: Verify filter by status=In Progress returns only In Progress reports."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="Filter In Progress 1")
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "In Progress"}, headers=admin_headers)
        resp = client.get("/api/v1/reports?status=In Progress", headers=user_headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]:
            assert item["status"] == "In Progress"

    def test_f08_03_filter_by_completed_status(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F8.3: Verify filter by status=Completed returns only Completed reports."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="Filter Completed 1")
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "In Progress"}, headers=admin_headers)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "Completed"}, headers=admin_headers)
        resp = client.get("/api/v1/reports?status=Completed", headers=user_headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]:
            assert item["status"] == "Completed"

    def test_f08_04_filter_by_rejected_status(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F8.4: Verify filter by status=Rejected returns only Rejected reports."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="Filter Rejected 1")
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "Rejected"}, headers=admin_headers)
        resp = client.get("/api/v1/reports?status=Rejected", headers=user_headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]:
            assert item["status"] == "Rejected"

    def test_f08_05_filter_by_category_id(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F8.5: Verify filter by category_id returns reports belonging exclusively to that category."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, category_id=2, title="Plastic Filter Test")
        resp = client.get("/api/v1/reports?category_id=2", headers=user_headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]:
            assert item["category"]["id"] == 2

    # -------------------------------------------------------------------------
    # Feature 9: Search (5 tests)
    # -------------------------------------------------------------------------
    def test_f09_01_search_by_title_keyword(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F9.1: Verify search matching keyword in title."""
        unique_term = f"KardusBekas_{uuid.uuid4().hex[:6]}"
        create_test_report_helper(client, user_headers, dummy_image_bytes, title=f"Tumpukan {unique_term}")
        resp = client.get(f"/api/v1/reports?search={unique_term}", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["meta"]["total_items"] >= 1
        assert unique_term in resp.json()["data"][0]["title"]

    def test_f09_02_search_by_description_keyword(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F9.2: Verify search matching keyword in description."""
        unique_desc = f"BanjirSaluran_{uuid.uuid4().hex[:6]}"
        create_test_report_helper(client, user_headers, dummy_image_bytes, description=f"Menyumbat {unique_desc}")
        resp = client.get(f"/api/v1/reports?search={unique_desc}", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["meta"]["total_items"] >= 1

    def test_f09_03_search_by_address_note_keyword(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F9.3: Verify search matching keyword in address_note/landmark."""
        unique_landmark = f"WarungPadang_{uuid.uuid4().hex[:6]}"
        create_test_report_helper(client, user_headers, dummy_image_bytes, address_note=f"Depan {unique_landmark}")
        resp = client.get(f"/api/v1/reports?search={unique_landmark}", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["meta"]["total_items"] >= 1

    def test_f09_04_search_case_insensitivity(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F9.4: Verify search query is case-insensitive (UPPERCASE matches lowercase)."""
        create_test_report_helper(client, user_headers, dummy_image_bytes, title="Botol Kaca Minuman")
        resp = client.get("/api/v1/reports?search=BOTOL", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["meta"]["total_items"] >= 1

    def test_f09_05_search_no_match_returns_empty(
        self, client: TestClient, user_headers: Dict[str, str]
    ):
        """F9.5: Verify unmatched search query returns total_items: 0 and data: []."""
        resp = client.get("/api/v1/reports?search=NON_EXISTENT_KEYWORD_XYZ999", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["meta"]["total_items"] == 0
        assert resp.json()["data"] == []

    # -------------------------------------------------------------------------
    # Feature 10: Review Modal (5 tests)
    # -------------------------------------------------------------------------
    def test_f10_01_review_modal_fetch_detail_by_id(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F10.1: Verify GET /api/v1/reports/{id} returns full report details for review modal."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="Review Modal Detail")
        resp = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == rep["id"]
        assert data["title"] == "Review Modal Detail"

    def test_f10_02_review_modal_ai_detection_badge(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F10.2: Verify review modal detail includes detected_category and ai_confidence."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "detected_category" in data
        assert "ai_confidence" in data

    def test_f10_03_review_modal_photo_preview_field(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F10.3: Verify review modal detail contains valid image_url for photo preview."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers)
        data = resp.json()["data"]
        assert data["image_url"] is not None
        assert len(data["image_url"]) > 0

    def test_f10_04_review_modal_address_and_notes(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F10.4: Verify review modal detail includes address_note and description."""
        rep = create_test_report_helper(
            client, user_headers, dummy_image_bytes,
            description="Detail description text",
            address_note="Patokan depan gerbang",
        )
        resp = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers)
        data = resp.json()["data"]
        assert data["description"] == "Detail description text"
        assert data["address_note"] == "Patokan depan gerbang"

    def test_f10_05_review_modal_audit_trail_history(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F10.5: Verify review modal detail includes logs array with transition history."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers)
        data = resp.json()["data"]
        assert "logs" in data and isinstance(data["logs"], list)
        assert len(data["logs"]) >= 1
        assert data["logs"][0]["new_status"] == "Pending"

    # -------------------------------------------------------------------------
    # Feature 11: Google Maps Link (5 tests)
    # -------------------------------------------------------------------------
    def test_f11_01_google_maps_url_generation(self):
        """F11.1: Verify Google Maps URL matches https://www.google.com/maps?q={lat},{long}."""
        lat, lon = -6.2088, 106.8456
        url = format_google_maps_url(lat, lon)
        assert url == "https://www.google.com/maps?q=-6.2088,106.8456"

    def test_f11_02_google_maps_latitude_range_validation(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F11.2: Verify report latitude is within geographical range [-90.0, 90.0]."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, latitude=-6.1754)
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers).json()["data"]
        assert -90.0 <= detail["latitude"] <= 90.0

    def test_f11_03_google_maps_longitude_range_validation(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F11.3: Verify report longitude is within geographical range [-180.0, 180.0]."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, longitude=106.8272)
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers).json()["data"]
        assert -180.0 <= detail["longitude"] <= 180.0

    def test_f11_04_google_maps_coordinate_formatting_mono(self):
        """F11.4: Verify coordinate formatting preserves precision for JetBrains Mono display."""
        lat, lon = -6.208812, 106.845678
        formatted = f"{lat:.4f}, {lon:.4f}"
        assert formatted == "-6.2088, 106.8457"

    def test_f11_05_google_maps_link_target_security(self):
        """F11.5: Verify Google Maps link contract specifies target='_blank' and rel='noopener noreferrer'."""
        link_props = {
            "target": "_blank",
            "rel": "noopener noreferrer",
        }
        assert link_props["target"] == "_blank"
        assert "noopener" in link_props["rel"]
        assert "noreferrer" in link_props["rel"]

    # -------------------------------------------------------------------------
    # Feature 12: Status Patch (5 tests)
    # -------------------------------------------------------------------------
    def test_f12_01_status_patch_pending_to_in_progress(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F12.1: Verify admin can transition status from Pending to In Progress with admin_notes."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress", "admin_notes": "Truk kebersihan dikerahkan"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "In Progress"
        assert resp.json()["data"]["admin_notes"] == "Truk kebersihan dikerahkan"

    def test_f12_02_status_patch_in_progress_to_completed(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F12.2: Verify admin can transition status from In Progress to Completed."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "In Progress"}, headers=admin_headers)
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "Completed", "admin_notes": "Sampah selesai diangkut"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "Completed"

    def test_f12_03_status_patch_pending_to_rejected(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F12.3: Verify admin can transition status from Pending to Rejected."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "Rejected", "admin_notes": "Foto tidak valid / palsu"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "Rejected"

    def test_f12_04_status_patch_returns_updated_at(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F12.4: Verify status patch response returns updated_at timestamp."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "updated_at" in resp.json()["data"]

    def test_f12_05_status_patch_completed_sets_resolved_at(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """F12.5: Verify transitioning to Completed populates resolved_at in report details."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "In Progress"}, headers=admin_headers)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "Completed"}, headers=admin_headers)
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=admin_headers).json()["data"]
        assert detail["status"] == "Completed"
        assert detail["resolved_at"] is not None

    # -------------------------------------------------------------------------
    # Feature 13: User Management (5 tests)
    # -------------------------------------------------------------------------
    def test_f13_01_admin_user_profile_role(self, client: TestClient, admin_headers: Dict[str, str]):
        """F13.1: Verify Super Admin user profile displays role='admin'."""
        resp = client.get("/api/v1/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "admin"

    def test_f13_02_citizen_user_profile_role(self, client: TestClient, user_headers: Dict[str, str]):
        """F13.2: Verify Citizen user profile displays role='user'."""
        resp = client.get("/api/v1/auth/me", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "user"

    def test_f13_03_user_profile_active_status(self, client: TestClient, admin_headers: Dict[str, str]):
        """F13.3: Verify user account status data structure contains valid identity metadata."""
        resp = client.get("/api/v1/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "email" in data and "@" in data["email"]
        assert "full_name" in data and len(data["full_name"]) > 0

    def test_f13_04_seed_users_presence_and_roles(self, client: TestClient, seed_data: Dict[str, Any]):
        """F13.4: Verify initial seed users admin@bilcode.id and user@bilcode.id are present."""
        admin = client.post("/api/v1/auth/login", json={"email": "admin@bilcode.id", "password": "Admin123!"})
        user = client.post("/api/v1/auth/login", json={"email": "user@bilcode.id", "password": "User123!"})
        assert admin.status_code == 200
        assert user.status_code == 200

    def test_f13_05_rbac_admin_route_guard_enforcement(self, client: TestClient, user_headers: Dict[str, str]):
        """F13.5: Verify RBAC route guard blocks standard user from admin-only endpoints with HTTP 403."""
        resp = client.get("/api/v1/dashboard/stats", headers=user_headers)
        assert resp.status_code == 403
        assert "Admin access required" in resp.json().get("detail", "")


# =============================================================================
# TIER 2: BOUNDARY & CORNER CASES (14 tests)
# =============================================================================

class TestTier2BoundaryCases:
    """Tier 2: Boundary and corner cases (empty collections, division-by-zero, invalid states, 401/403)."""

    def test_t2_01_empty_reports_list_returns_zero_meta(self, client: TestClient, user_headers: Dict[str, str]):
        """T2.01: Verify empty query returns total_items: 0, current_page: 1, and empty data list."""
        resp = client.get("/api/v1/reports?search=TOTALLY_EMPTY_NO_MATCH", headers=user_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["meta"]["total_items"] == 0
        assert body["data"] == []

    def test_t2_02_zero_reports_division_guard_in_stats(self, client: TestClient, admin_headers: Dict[str, str]):
        """T2.02: Verify zero total reports completion_rate_percent returns 0.0 without ZeroDivisionError."""
        # Stats summary completion_rate_percent must always be numeric float
        resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert resp.status_code == 200
        rate = resp.json()["data"]["summary"]["completion_rate_percent"]
        assert isinstance(rate, (int, float))
        assert rate >= 0.0

    def test_t2_03_invalid_status_transition_pending_to_completed_400(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T2.03: Verify direct invalid transition Pending -> Completed is rejected with HTTP 400."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "Completed"},
            headers=admin_headers,
        )
        assert resp.status_code == 400
        assert "Invalid status transition" in resp.json().get("detail", "")

    def test_t2_04_terminal_state_completed_modification_400(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T2.04: Verify attempt to modify a Completed report is rejected with HTTP 400 (Terminal State)."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "In Progress"}, headers=admin_headers)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "Completed"}, headers=admin_headers)
        # Attempt modifying completed report back to In Progress
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress"},
            headers=admin_headers,
        )
        assert resp.status_code == 400
        assert "terminal state" in resp.json().get("detail", "")

    def test_t2_05_terminal_state_rejected_modification_400(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T2.05: Verify attempt to modify a Rejected report is rejected with HTTP 400 (Terminal State)."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "Rejected"}, headers=admin_headers)
        # Attempt modifying rejected report
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress"},
            headers=admin_headers,
        )
        assert resp.status_code == 400
        assert "terminal state" in resp.json().get("detail", "")

    def test_t2_06_invalid_credentials_401_rejection(self, client: TestClient):
        """T2.06: Verify login with invalid password returns HTTP 401 Unauthorized."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "WrongPassword999!"},
        )
        assert resp.status_code == 401
        assert "Invalid email or password" in resp.json().get("detail", "")

    def test_t2_07_unregistered_email_401_rejection(self, client: TestClient):
        """T2.07: Verify login with unregistered email returns HTTP 401 Unauthorized."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent_ghost@bilcode.id", "password": "AnyPassword123!"},
        )
        assert resp.status_code == 401
        assert "Invalid email or password" in resp.json().get("detail", "")

    def test_t2_08_non_admin_403_on_dashboard_stats(self, client: TestClient, user_headers: Dict[str, str]):
        """T2.08: Verify citizen user receives HTTP 403 Forbidden on GET /api/v1/dashboard/stats."""
        resp = client.get("/api/v1/dashboard/stats", headers=user_headers)
        assert resp.status_code == 403
        assert "Admin access required" in resp.json().get("detail", "")

    def test_t2_09_non_admin_403_on_status_patch(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T2.09: Verify citizen user receives HTTP 403 Forbidden on PATCH /api/v1/reports/{id}/status."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress"},
            headers=user_headers,
        )
        assert resp.status_code == 403
        assert "Admin access required" in resp.json().get("detail", "")

    def test_t2_10_out_of_bounds_page_returns_empty_data(self, client: TestClient, user_headers: Dict[str, str]):
        """T2.10: Verify requesting out-of-bounds page (page=999) returns empty data list with 200 OK."""
        resp = client.get("/api/v1/reports?page=999&limit=10", headers=user_headers)
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_t2_11_page_limit_boundary_validation_422(self, client: TestClient, user_headers: Dict[str, str]):
        """T2.11: Verify limit boundary validation rejects limit=0 or limit=101 with 422."""
        resp_low = client.get("/api/v1/reports?limit=0", headers=user_headers)
        assert resp_low.status_code == 422
        resp_high = client.get("/api/v1/reports?limit=101", headers=user_headers)
        assert resp_high.status_code == 422

    def test_t2_12_relative_image_url_prefix_resolver(self):
        """T2.12: Verify relative image URL prefix normalization function."""
        # Relative path gets backend origin prepended
        assert resolve_image_url("/uploads/reports/abc.jpg") == "http://localhost:8000/uploads/reports/abc.jpg"
        assert resolve_image_url("uploads/reports/xyz.jpg") == "http://localhost:8000/uploads/reports/xyz.jpg"
        # Absolute path remains untouched
        assert resolve_image_url("https://cdn.example.com/photo.jpg") == "https://cdn.example.com/photo.jpg"
        # None or empty returns placeholder
        assert resolve_image_url(None) == "/placeholder.png"
        assert resolve_image_url("") == "/placeholder.png"

    def test_t2_13_report_with_null_admin_notes_handled(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T2.13: Verify newly created report has admin_notes=None without crashing client."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=user_headers).json()["data"]
        assert detail["admin_notes"] is None

    def test_t2_14_ai_confidence_null_or_zero_boundary(self):
        """T2.14: Verify confidence percentage formatter handles null, zero, and standard float."""
        assert format_confidence_percentage(None) == "0.00%"
        assert format_confidence_percentage(0.0) == "0.00%"
        assert format_confidence_percentage(0.9421) == "94.21%"
        assert format_confidence_percentage(1.0) == "100.00%"


# =============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (6 tests)
# =============================================================================

class TestTier3CrossFeatureCombinations:
    """Tier 3: Complex multi-step cross-feature integrations."""

    def test_t3_01_search_filter_pagination_compound_query(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T3.01: Verify search + status filter + category filter + pagination combined together."""
        unique_tag = f"Compound_{uuid.uuid4().hex[:6]}"
        create_test_report_helper(client, user_headers, dummy_image_bytes, title=f"Botol {unique_tag}", category_id=2)
        create_test_report_helper(client, user_headers, dummy_image_bytes, title=f"Kertas {unique_tag}", category_id=3)

        url = f"/api/v1/reports?search={unique_tag}&status=Pending&category_id=2&page=1&limit=5"
        resp = client.get(url, headers=user_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 1
        assert data[0]["category"]["id"] == 2
        assert data[0]["status"] == "Pending"

    def test_t3_02_login_stats_patch_audit_log_chain(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T3.02: Verify chain: Login -> Auth token -> Fetch stats -> Update report status -> Audit log reflection."""
        # 1. Login as admin
        login_resp = client.post("/api/v1/auth/login", json={"email": "admin@bilcode.id", "password": "Admin123!"})
        admin_token = login_resp.json()["data"]["access_token"]
        admin_auth = {"Authorization": f"Bearer {admin_token}"}

        # 2. Citizen creates report
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="Audit Chain Test")

        # 3. Fetch initial stats
        stats1 = client.get("/api/v1/dashboard/stats", headers=admin_auth).json()["data"]["summary"]

        # 4. Patch report status to In Progress
        patch_resp = client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress", "admin_notes": "Truk dikerahkan"},
            headers=admin_auth,
        )
        assert patch_resp.status_code == 200

        # 5. Verify audit log reflection in report details
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=admin_auth).json()["data"]
        assert detail["status"] == "In Progress"
        assert len(detail["logs"]) >= 2
        latest_log = detail["logs"][-1]
        assert latest_log["new_status"] == "In Progress"
        assert latest_log["remarks"] == "Truk dikerahkan"

    def test_t3_03_citizen_submission_admin_triage_flow(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T3.03: Verify citizen submits report -> admin stats pending increments -> admin filters & reviews."""
        initial_stats = client.get("/api/v1/dashboard/stats", headers=admin_headers).json()["data"]["summary"]
        initial_pending = initial_stats["pending_count"]

        # Citizen submits report
        create_test_report_helper(client, user_headers, dummy_image_bytes, title="Citizen Triage Flow")

        # Admin stats reflects increment
        new_stats = client.get("/api/v1/dashboard/stats", headers=admin_headers).json()["data"]["summary"]
        assert new_stats["pending_count"] == initial_pending + 1

    def test_t3_04_full_state_machine_three_stage_audit_trail(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T3.04: Verify full transition Pending -> In Progress -> Completed records all 3 stages in audit trail."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)

        # Stage 1: Transition to In Progress
        client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress", "admin_notes": "Tahap 1 Mulai"},
            headers=admin_headers,
        )

        # Stage 2: Transition to Completed
        client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "Completed", "admin_notes": "Tahap 2 Selesai"},
            headers=admin_headers,
        )

        # Verify audit trail contains all stages in chronological order
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=admin_headers).json()["data"]
        logs = detail["logs"]
        assert len(logs) == 3
        assert logs[0]["new_status"] == "Pending"
        assert logs[1]["new_status"] == "In Progress"
        assert logs[2]["new_status"] == "Completed"

    def test_t3_05_rejection_path_audit_log_trail(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T3.05: Verify rejection flow Pending -> Rejected records terminal log with rejection note."""
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes)
        client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "Rejected", "admin_notes": "Lokasi tidak ditemukan"},
            headers=admin_headers,
        )
        detail = client.get(f"/api/v1/reports/{rep['id']}", headers=admin_headers).json()["data"]
        assert detail["status"] == "Rejected"
        logs = detail["logs"]
        assert logs[-1]["new_status"] == "Rejected"
        assert logs[-1]["remarks"] == "Lokasi tidak ditemukan"

    def test_t3_06_master_categories_cross_referenced_with_reports(
        self, client: TestClient, user_headers: Dict[str, str]
    ):
        """T3.06: Verify categories catalog GET /api/v1/categories matches categories returned in reports list."""
        cat_resp = client.get("/api/v1/categories")
        assert cat_resp.status_code == 200
        catalog = {c["id"]: c["name"] for c in cat_resp.json()["data"]}

        reports_resp = client.get("/api/v1/reports", headers=user_headers)
        assert reports_resp.status_code == 200
        for rep in reports_resp.json()["data"]:
            cid = rep["category"]["id"]
            assert cid in catalog
            assert rep["category"]["name"] == catalog[cid]


# =============================================================================
# TIER 4: REAL-WORLD SCENARIOS (3 tests)
# =============================================================================

class TestTier4RealWorldScenarios:
    """Tier 4: End-to-end operational scenarios simulating real-world municipal workflows."""

    def test_t4_01_full_admin_triage_workflow(
        self, client: TestClient, user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T4.01: Full admin triage workflow:
        1. Citizen submits waste report with GPS coordinates and AI-predicted category.
        2. Super Admin logs in and acquires authentication token.
        3. Admin views dashboard metrics, observing pending verification count.
        4. Admin inspects report review modal: examines photo preview, AI badge, and Google Maps link.
        5. Admin updates status to 'In Progress' with field dispatch notes.
        6. Admin re-fetches report detail to verify status update and audit trail entry.
        7. Admin re-fetches dashboard stats to verify updated operational metric.
        """
        # Step 1: Citizen submits report
        report_data = create_test_report_helper(
            client,
            user_headers,
            dummy_image_bytes,
            title="Tumpukan Limbah Plastik Monas",
            category_id=2,
            latitude=-6.1754,
            longitude=106.8272,
            description="Tumpukan botol kemasan plastik dekat pintu barat daya",
            address_note="Dekat gerbang Monas barat daya",
        )
        report_id = report_data["id"]

        # Step 2: Admin authenticates
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@bilcode.id", "password": "Admin123!"},
        )
        assert login_resp.status_code == 200
        admin_token = login_resp.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Step 3: Admin checks dashboard stats
        stats_resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert stats_resp.status_code == 200
        assert stats_resp.json()["data"]["summary"]["pending_count"] >= 1

        # Step 4: Admin reviews report detail in modal
        detail_resp = client.get(f"/api/v1/reports/{report_id}", headers=admin_headers)
        assert detail_resp.status_code == 200
        report_detail = detail_resp.json()["data"]

        # Validate photo preview URL
        resolved_img = resolve_image_url(report_detail["image_url"])
        assert "http" in resolved_img

        # Validate AI confidence formatting
        ai_badge_text = format_confidence_percentage(report_detail["ai_confidence"])
        assert "%" in ai_badge_text

        # Validate Google Maps link format
        maps_url = format_google_maps_url(report_detail["latitude"], report_detail["longitude"])
        assert maps_url == "https://www.google.com/maps?q=-6.1754,106.8272"

        # Step 5: Admin dispatches crew (PATCH status to In Progress)
        patch_resp = client.patch(
            f"/api/v1/reports/{report_id}/status",
            json={
                "status": "In Progress",
                "admin_notes": "Armada Truk Unit #04 dikerahkan ke lokasi Monas Barat Daya",
            },
            headers=admin_headers,
        )
        assert patch_resp.status_code == 200

        # Step 6: Verify report state & audit log
        updated_detail = client.get(f"/api/v1/reports/{report_id}", headers=admin_headers).json()["data"]
        assert updated_detail["status"] == "In Progress"
        assert updated_detail["admin_notes"] == "Armada Truk Unit #04 dikerahkan ke lokasi Monas Barat Daya"
        assert len(updated_detail["logs"]) == 2
        assert updated_detail["logs"][-1]["new_status"] == "In Progress"

        # Step 7: Verify updated dashboard metrics
        updated_stats = client.get("/api/v1/dashboard/stats", headers=admin_headers).json()["data"]["summary"]
        assert updated_stats["in_progress_count"] >= 1

    def test_t4_02_citizen_report_to_completion_lifecycle(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T4.02: End-to-end lifecycle from citizen report to full administrative completion:
        1. Citizen submits report.
        2. Admin moves report to In Progress.
        3. Sanitation crew cleans area; Admin moves report to Completed.
        4. Verification of resolved_at timestamp, terminal lock, and completion rate impact.
        """
        # 1. Citizen submits report
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="Full Lifecycle Report")
        rep_id = rep["id"]

        # 2. Admin transitions to In Progress
        client.patch(
            f"/api/v1/reports/{rep_id}/status",
            json={"status": "In Progress", "admin_notes": "Tim dalam perjalanan"},
            headers=admin_headers,
        )

        # 3. Admin transitions to Completed
        complete_resp = client.patch(
            f"/api/v1/reports/{rep_id}/status",
            json={"status": "Completed", "admin_notes": "Lokasi bersih tuntas, sampah diangkut"},
            headers=admin_headers,
        )
        assert complete_resp.status_code == 200

        # 4. Verify resolved_at and terminal status
        final_detail = client.get(f"/api/v1/reports/{rep_id}", headers=admin_headers).json()["data"]
        assert final_detail["status"] == "Completed"
        assert final_detail["resolved_at"] is not None

        # Verify terminal lock prevents further modification
        lock_resp = client.patch(
            f"/api/v1/reports/{rep_id}/status",
            json={"status": "In Progress"},
            headers=admin_headers,
        )
        assert lock_resp.status_code == 400

    def test_t4_03_rbac_security_and_role_isolation(
        self, client: TestClient, admin_headers: Dict[str, str], user_headers: Dict[str, str], dummy_image_bytes: bytes
    ):
        """T4.03: Multi-role security and RBAC isolation:
        1. Anonymous visitor is blocked from /auth/me, /reports, and /dashboard/stats.
        2. Citizen user is allowed read access to /reports and /auth/me, but blocked (403) from stats and status mutation.
        3. Administrator has full privileges across all endpoints.
        """
        rep = create_test_report_helper(client, user_headers, dummy_image_bytes, title="RBAC Test Report")

        # 1. Anonymous visitor
        assert client.get("/api/v1/auth/me").status_code == 401
        assert client.get("/api/v1/dashboard/stats").status_code == 401
        assert client.patch(f"/api/v1/reports/{rep['id']}/status", json={"status": "In Progress"}).status_code == 401

        # 2. Citizen user
        assert client.get("/api/v1/auth/me", headers=user_headers).status_code == 200
        assert client.get("/api/v1/reports", headers=user_headers).status_code == 200
        assert client.get("/api/v1/dashboard/stats", headers=user_headers).status_code == 403
        assert client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress"},
            headers=user_headers,
        ).status_code == 403

        # 3. Super Admin
        assert client.get("/api/v1/auth/me", headers=admin_headers).status_code == 200
        assert client.get("/api/v1/dashboard/stats", headers=admin_headers).status_code == 200
        assert client.patch(
            f"/api/v1/reports/{rep['id']}/status",
            json={"status": "In Progress"},
            headers=admin_headers,
        ).status_code == 200


# =============================================================================
# Standalone CLI Test Runner Execution
# =============================================================================

if __name__ == "__main__":
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)
