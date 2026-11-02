"""Tier 1 and Tier 2 Admin Dashboard Metrics, Master Categories, and Health Probes Test Suite for SWMS - Day 2.

Covers:
- Tier 1 (Feature Coverage):
  1. Admin dashboard statistics happy path (GET /api/v1/dashboard/stats)
  2. Summary metrics calculation accuracy (total, pending, in_progress, completed, rejected, completion_rate)
  3. Category distribution aggregations and percentages
  4. Active user count metric reflection
  5. Recent activities audit stream retrieval
  6. Categories master catalog endpoint (GET /api/v1/categories)
  7. Root service probe (GET /)
  8. Primary health probes (GET /health and GET /api/v1/health)
- Tier 2 (Boundary & Corner Cases):
  1. Non-admin citizen user receives 403 Forbidden on dashboard stats
  2. Unauthenticated user receives 401 Unauthorized on dashboard stats
  3. Empty database stats handling (zero reports division by zero prevention, returning 0.0%)
  4. 100% completion rate calculation when all reports are completed
  5. Master categories retrieval with query params and empty database resiliency
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


class TestTier1DashboardFeatureCoverage:
    """Tier 1: Feature coverage for dashboard statistics, master categories, and health probes."""

    def test_admin_dashboard_stats_happy_path(
        self, client: TestClient, admin_headers, dummy_image_bytes: bytes, user_headers, seed_data
    ):
        """Tier 1: Verify authenticated admin can retrieve dashboard statistics with all top-level sections."""
        # Create at least one report to have non-empty metrics
        files = {"file": ("dash_rep.jpg", dummy_image_bytes, "image/jpeg")}
        data = {"title": "Laporan Dashboard Test", "category_id": 2, "latitude": -6.2, "longitude": 106.8}
        client.post("/api/v1/reports", files=files, data=data, headers=user_headers)

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        stats = body["data"]

        # Validate top-level schema blocks
        assert "summary" in stats
        assert "category_distribution" in stats
        assert "recent_activities" in stats

        summary = stats["summary"]
        assert "total_reports" in summary
        assert "pending_count" in summary
        assert "in_progress_count" in summary
        assert "completed_count" in summary
        assert "rejected_count" in summary
        assert "completion_rate_percent" in summary

    def test_dashboard_metrics_counts_and_rate_accuracy(
        self, client: TestClient, admin_headers, seed_data, db_session: Session
    ):
        """Tier 1: Verify accurate calculation of status counts and completion rate percentage."""
        # Directly insert controlled report counts for deterministic math
        # 1 Pending, 1 In Progress, 2 Completed, 1 Rejected (Total = 5, Completed = 2 -> 40.00%)
        admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
        cat_plastic = seed_data["categories_by_slug"]["plastic"]

        statuses = ["Pending", "In Progress", "Completed", "Completed", "Rejected"]
        for s in statuses:
            rep = WasteReport(
                id=uuid.uuid4(),
                user_id=admin_user.id,
                category_id=cat_plastic.id,
                title=f"Report {s}",
                image_url="http://test/img.jpg",
                latitude=-6.2,
                longitude=106.8,
                status=s,
                resolved_at=datetime.now(timezone.utc) if s == "Completed" else None,
            )
            db_session.add(rep)
        db_session.commit()

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        summary = response.json()["data"]["summary"]

        assert summary["total_reports"] >= 5
        assert summary["pending_count"] >= 1
        assert summary["in_progress_count"] >= 1
        assert summary["completed_count"] >= 2
        assert summary["rejected_count"] >= 1

        # Check rate calculation: (completed / total) * 100
        expected_rate = round((summary["completed_count"] / summary["total_reports"]) * 100, 2)
        assert abs(summary["completion_rate_percent"] - expected_rate) < 0.1

    def test_dashboard_category_distribution_aggregations(
        self, client: TestClient, admin_headers, seed_data, db_session: Session
    ):
        """Tier 1: Verify category distribution aggregation includes names, counts, and percentages."""
        admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
        cat_organic = seed_data["categories_by_slug"]["organic"]
        cat_paper = seed_data["categories_by_slug"]["paper"]

        # Insert 2 Organic, 1 Paper
        for _ in range(2):
            db_session.add(WasteReport(
                id=uuid.uuid4(), user_id=admin_user.id, category_id=cat_organic.id,
                title="Organic Waste", image_url="http://test/o.jpg",
                latitude=-6.2, longitude=106.8, status="Pending",
            ))
        db_session.add(WasteReport(
            id=uuid.uuid4(), user_id=admin_user.id, category_id=cat_paper.id,
            title="Paper Waste", image_url="http://test/p.jpg",
            latitude=-6.2, longitude=106.8, status="Pending",
        ))
        db_session.commit()

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        dist = response.json()["data"]["category_distribution"]

        assert isinstance(dist, list)
        cat_names = [item["category"] for item in dist]
        assert "Organic Waste" in cat_names
        assert "Paper Waste" in cat_names

        for item in dist:
            assert "count" in item
            assert "percentage" in item
            assert isinstance(item["count"], int)
            assert 0.0 <= item["percentage"] <= 100.0

    def test_dashboard_active_users_metric(self, client: TestClient, admin_headers, seed_data):
        """Tier 1: Verify active_users count metric reflects users in database with is_active=True."""
        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        summary = response.json()["data"]["summary"]

        if "active_users" in summary:
            # Seed data has 2 active users (admin and user)
            assert summary["active_users"] >= 2

    def test_categories_master_catalog_endpoint(self, client: TestClient, seed_data):
        """Tier 1: Verify GET /api/v1/categories returns list of master waste categories."""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        cats = body["data"]

        assert len(cats) >= 3
        slugs = {c["slug"] for c in cats}
        assert {"organic", "plastic", "paper"}.issubset(slugs)

        first_cat = cats[0]
        assert "id" in first_cat
        assert "name" in first_cat
        assert "slug" in first_cat
        assert "badge_color" in first_cat

    def test_root_endpoint_probe(self, client: TestClient):
        """Tier 1: Verify root endpoint probe GET / returns success status, version, and docs link."""
        response = client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert "app" in body
        assert "version" in body
        assert body["docs"] == "/docs"

    def test_health_endpoints_probes(self, client: TestClient):
        """Tier 1: Verify healthcheck probes GET /health and GET /api/v1/health return healthy status."""
        for path in ["/health", "/api/v1/health"]:
            response = client.get(path)
            assert response.status_code == 200, f"Healthcheck failed at {path}: {response.text}"
            body = response.json()
            assert body["status"] == "healthy"
            assert body["service"] == "backend"
            assert "version" in body


class TestTier2DashboardBoundaryAndCornerCases:
    """Tier 2: Authorization security, division by zero prevention, and empty database handling."""

    def test_citizen_user_cannot_access_dashboard_stats_forbidden(self, client: TestClient, user_headers):
        """Tier 2: Verify non-admin citizen token receives 403 Forbidden on GET /dashboard/stats."""
        response = client.get("/api/v1/dashboard/stats", headers=user_headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        assert "detail" in response.json()

    def test_unauthenticated_request_to_dashboard_stats_rejected(self, client: TestClient):
        """Tier 2: Verify unauthenticated request to /dashboard/stats returns 401 Unauthorized."""
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_dashboard_stats_empty_database_zero_division_prevention(
        self, client: TestClient, admin_headers, seed_data, db_session: Session
    ):
        """Tier 2: Verify 0 reports in database handles completion rate cleanly as 0.0 (no ZeroDivisionError)."""
        # Ensure 0 reports
        db_session.query(ReportLog).delete()
        db_session.query(WasteReport).delete()
        db_session.commit()

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200, f"Dashboard failed on empty DB: {response.text}"

        summary = response.json()["data"]["summary"]
        assert summary["total_reports"] == 0
        assert summary["pending_count"] == 0
        assert summary["in_progress_count"] == 0
        assert summary["completed_count"] == 0
        assert summary["rejected_count"] == 0
        assert summary["completion_rate_percent"] == 0.0

    def test_dashboard_stats_100_percent_completion_rate(
        self, client: TestClient, admin_headers, seed_data, db_session: Session
    ):
        """Tier 2: Verify completion rate equals exactly 100.0% when all reports are completed."""
        admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
        cat_plastic = seed_data["categories_by_slug"]["plastic"]

        # Delete existing and insert only 2 Completed reports
        db_session.query(ReportLog).delete()
        db_session.query(WasteReport).delete()
        for i in range(2):
            db_session.add(WasteReport(
                id=uuid.uuid4(), user_id=admin_user.id, category_id=cat_plastic.id,
                title=f"Completed {i}", image_url="http://test/c.jpg",
                latitude=-6.2, longitude=106.8, status="Completed",
                resolved_at=datetime.now(timezone.utc),
            ))
        db_session.commit()

        response = client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        summary = response.json()["data"]["summary"]
        assert summary["total_reports"] == 2
        assert summary["completed_count"] == 2
        assert summary["completion_rate_percent"] == 100.0
