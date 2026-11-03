"""Unit tests for User Management endpoints (GET /api/v1/users)."""

import pytest


def test_list_users_unauthenticated(client):
    """Unauthenticated request must return 401 Unauthorized."""
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_list_users_as_citizen_forbidden(client, user_headers):
    """Citizen user request must return 403 Forbidden."""
    response = client.get("/api/v1/users", headers=user_headers)
    assert response.status_code == 403


def test_list_users_as_admin_success(client, admin_headers):
    """Admin request must return 200 OK with list of users."""
    response = client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 2  # Seed admin and citizen exist

    # Verify structure of user item
    user = data["data"][0]
    assert "id" in user
    assert "email" in user
    assert "full_name" in user
    assert "role" in user
    assert "total_reports" in user


def test_list_users_filter_by_role(client, admin_headers):
    """Filtering by role=admin should only return admin users."""
    response = client.get("/api/v1/users?role=admin", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    for u in data["data"]:
        assert u["role"] == "admin"


def test_list_users_search(client, admin_headers):
    """Searching by 'bilcode' should return seed accounts."""
    response = client.get("/api/v1/users?search=bilcode", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 1
