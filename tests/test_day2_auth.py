"""Tier 1 and Tier 2 Authentication and RBAC Test Suite for SWMS - Day 2.

Covers:
- Tier 1 (Feature Coverage):
  1. User registration happy path (POST /api/v1/auth/register)
  2. Citizen login returning valid JWT and user payload (POST /api/v1/auth/login)
  3. Admin login returning valid JWT with admin role (POST /api/v1/auth/login)
  4. Authenticated citizen user profile retrieval (GET /api/v1/auth/me)
  5. Authenticated admin user profile retrieval (GET /api/v1/auth/me)
  6. Login compatibility with application/x-www-form-urlencoded credentials
- Tier 2 (Boundary & Corner Cases):
  1. Duplicate email registration rejection (HTTP 400 Bad Request)
  2. Registration payload missing required fields (HTTP 422 Unprocessable Entity)
  3. Login failure on invalid password (HTTP 401 Unauthorized)
  4. Login failure on non-existent email account (HTTP 401 Unauthorized)
  5. Unauthenticated request to protected endpoint without Authorization header (HTTP 401)
  6. Request with malformed / non-JWT Authorization header (HTTP 401)
  7. Request with expired JWT token (HTTP 401)
  8. Login rejection for deactivated user account (is_active = False)
"""

from datetime import datetime, timedelta, timezone
import uuid
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.seed import verify_password
from app.models.user import User


class TestTier1AuthFeatureCoverage:
    """Tier 1: Comprehensive feature coverage for auth endpoints in isolation."""

    def test_register_citizen_happy_path(self, client: TestClient, db_session: Session):
        """Tier 1: Verify citizen user registration creates account with Bcrypt password."""
        payload = {
            "full_name": "Darell Rangga",
            "email": "darell.new@example.com",
            "password": "Password123!",
            "phone_number": "081234567890",
        }

        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        assert "message" in body
        data = body["data"]
        assert data["email"] == "darell.new@example.com"
        assert data["full_name"] == "Darell Rangga"
        assert data["role"] == "user"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

        # Verify database record and password hashing
        db_user = db_session.query(User).filter_by(email="darell.new@example.com").first()
        assert db_user is not None
        assert db_user.password_hash != "Password123!"
        assert verify_password("Password123!", db_user.password_hash) is True
        assert db_user.role == "user"
        assert db_user.is_active is True

    def test_login_citizen_happy_path(self, client: TestClient, seed_data):
        """Tier 1: Verify citizen login returns access token and user profile."""
        payload = {
            "email": "user@bilcode.id",
            "password": "User123!",
        }

        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert "access_token" in data
        assert data["token_type"].lower() == "bearer"
        assert data["user"]["email"] == "user@bilcode.id"
        assert data["user"]["role"] == "user"
        assert data["user"]["full_name"] == "Warga Pelapor"

        # Verify token decoding and claims
        token = data["access_token"]
        claims = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        assert claims["email"] == "user@bilcode.id"
        assert claims["role"] == "user"
        assert "sub" in claims
        assert "exp" in claims

    def test_login_admin_happy_path(self, client: TestClient, seed_data):
        """Tier 1: Verify admin login returns access token with admin role."""
        payload = {
            "email": "admin@bilcode.id",
            "password": "Admin123!",
        }

        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == "admin@bilcode.id"

        token = data["access_token"]
        claims = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        assert claims["role"] == "admin"

    def test_get_me_citizen_profile(self, client: TestClient, user_headers):
        """Tier 1: Verify authenticated citizen can retrieve their own profile."""
        response = client.get("/api/v1/auth/me", headers=user_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["email"] == "user@bilcode.id"
        assert data["role"] == "user"
        assert data["full_name"] == "Warga Pelapor"
        assert "id" in data
        assert "created_at" in data

    def test_get_me_admin_profile(self, client: TestClient, admin_headers):
        """Tier 1: Verify authenticated admin can retrieve their own profile."""
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["email"] == "admin@bilcode.id"
        assert data["role"] == "admin"
        assert data["full_name"] == "Super Admin"

    def test_login_form_urlencoded_compatibility(self, client: TestClient, seed_data):
        """Tier 1: Verify login supports standard x-www-form-urlencoded form data."""
        form_data = {
            "username": "user@bilcode.id",
            "password": "User123!",
        }
        response = client.post(
            "/api/v1/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # Accepts form urlencoded or JSON
        if response.status_code != 200:
            # Also test with email key in form
            form_data_email = {"email": "user@bilcode.id", "password": "User123!"}
            response = client.post(
                "/api/v1/auth/login",
                data=form_data_email,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == 200, f"Form login failed: {response.text}"
        assert "access_token" in response.json()["data"]


class TestTier2AuthBoundaryAndCornerCases:
    """Tier 2: Boundary conditions, failure cascades, and security hardening for auth."""

    def test_register_duplicate_email_rejected(self, client: TestClient, seed_data):
        """Tier 2: Verify registration with already registered email returns 400 Bad Request."""
        payload = {
            "full_name": "Duplicated User",
            "email": "user@bilcode.id",  # Already in seed_data
            "password": "Password123!",
        }

        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "detail" in response.json()

    def test_register_missing_required_fields(self, client: TestClient):
        """Tier 2: Verify registration with missing required fields returns 422 Unprocessable Entity."""
        # Missing password
        response1 = client.post("/api/v1/auth/register", json={"email": "incomplete@example.com", "full_name": "Incomplete"})
        assert response1.status_code == 422

        # Missing email
        response2 = client.post("/api/v1/auth/register", json={"password": "Password123!", "full_name": "Incomplete"})
        assert response2.status_code == 422

        # Missing full_name
        response3 = client.post("/api/v1/auth/register", json={"email": "incomplete@example.com", "password": "Password123!"})
        assert response3.status_code == 422

    def test_login_invalid_password_returns_401(self, client: TestClient, seed_data):
        """Tier 2: Verify login with incorrect password returns 401 Unauthorized."""
        payload = {
            "email": "user@bilcode.id",
            "password": "WrongPassword123!",
        }

        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        assert "detail" in response.json()

    def test_login_nonexistent_email_returns_401(self, client: TestClient, seed_data):
        """Tier 2: Verify login with non-existent email returns 401 Unauthorized."""
        payload = {
            "email": "ghost.account@bilcode.id",
            "password": "AnyPassword123!",
        }

        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_me_unauthenticated_missing_header(self, client: TestClient):
        """Tier 2: Verify GET /auth/me without Authorization header returns 401 Unauthorized."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_me_malformed_token_returns_401(self, client: TestClient):
        """Tier 2: Verify GET /auth/me with garbage bearer token returns 401 Unauthorized."""
        headers = {"Authorization": "Bearer not_a_valid_jwt_token_garbage"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_me_expired_token_returns_401(self, client: TestClient, seed_data):
        """Tier 2: Verify GET /auth/me with an expired JWT token returns 401 Unauthorized."""
        user = seed_data["users_by_email"]["user@bilcode.id"]
        expired_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": datetime.now(timezone.utc) - timedelta(hours=2),  # Expired 2 hours ago
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_login_deactivated_user_rejected(self, client: TestClient, db_session: Session, seed_data):
        """Tier 2: Verify login attempts by inactive user account (is_active=False) are rejected."""
        # Deactivate user account
        user = db_session.query(User).filter_by(email="user@bilcode.id").first()
        user.is_active = False
        db_session.commit()

        payload = {
            "email": "user@bilcode.id",
            "password": "User123!",
        }
        response = client.post("/api/v1/auth/login", json=payload)
        # Expect 401 or 403 for inactive user
        assert response.status_code in (401, 403), f"Expected 401 or 403, got {response.status_code}: {response.text}"

    def test_get_current_admin_rbac_guard(self, client: TestClient, user_headers, admin_headers):
        """Tier 2: Verify get_current_admin permits admin and rejects citizen with HTTP 403."""
        from fastapi import Depends
        from app.api.deps import get_current_admin
        from app.main import app

        # Dynamically attach a test endpoint protected by get_current_admin if not already present
        route_path = "/api/v1/auth/test-admin-guard"
        existing_routes = [r.path for r in app.routes]
        if route_path not in existing_routes:
            @app.get(route_path, tags=["Auth"])
            def protected_admin_endpoint(admin: User = Depends(get_current_admin)):
                return {"status": "success", "admin_email": admin.email}

        # Citizen user must receive 403 Forbidden
        resp_user = client.get(route_path, headers=user_headers)
        assert resp_user.status_code == 403, f"Expected 403, got {resp_user.status_code}: {resp_user.text}"
        assert "Admin access required" in resp_user.json()["detail"]

        # Admin user must receive 200 OK
        resp_admin = client.get(route_path, headers=admin_headers)
        assert resp_admin.status_code == 200, f"Expected 200, got {resp_admin.status_code}: {resp_admin.text}"
        assert resp_admin.json()["admin_email"] == "admin@bilcode.id"
