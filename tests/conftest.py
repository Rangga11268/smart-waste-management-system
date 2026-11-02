"""Pytest test infrastructure and fixtures for Smart Waste Management System (SWMS) - Day 2.

Provides isolated in-memory SQLite database fixtures, foreign key enforcement,
FastAPI TestClient with dependency overrides, master seed data, authentication
headers, and synthetic image fixtures.
"""

import io
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Generator
import uuid

import pytest
from fastapi.testclient import TestClient
from PIL import Image
import jwt
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend and project root are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Backend application and model imports
from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.seed import seed_database
from app.models.category import Category
from app.models.log import ReportLog
from app.models.report import WasteReport
from app.models.user import User


@pytest.fixture(scope="session")
def test_engine() -> Engine:
    """Create an isolated in-memory SQLite engine with StaticPool and foreign key enforcement."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    # Create tables once for session or ensure Base metadata is ready
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Provide a transactional in-memory database session for each test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = session_factory()

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def seed_data(db_session: Session) -> Dict[str, Any]:
    """Seed master waste categories and initial default users into the test session."""
    seed_result = seed_database(db_session)
    categories = db_session.query(Category).order_by(Category.id).all()
    users = db_session.query(User).all()

    return {
        "summary": seed_result,
        "categories": categories,
        "categories_by_slug": {c.slug: c for c in categories},
        "categories_by_id": {c.id: c for c in categories},
        "users": users,
        "users_by_email": {u.email: u for u in users},
    }


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with the get_db dependency overridden to the test session."""
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, base_url="http://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_headers(client: TestClient, seed_data: Dict[str, Any]) -> Dict[str, str]:
    """Return Authorization Bearer header for the Super Admin test user."""
    # Attempt login via API endpoint first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@bilcode.id", "password": "Admin123!"},
    )
    if login_resp.status_code == 200:
        token = login_resp.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # Fallback to direct JWT token generation for test isolation
    admin_user = seed_data["users_by_email"]["admin@bilcode.id"]
    payload = {
        "sub": str(admin_user.id),
        "email": admin_user.email,
        "role": admin_user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def user_headers(client: TestClient, seed_data: Dict[str, Any]) -> Dict[str, str]:
    """Return Authorization Bearer header for the standard Citizen test user."""
    # Attempt login via API endpoint first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "user@bilcode.id", "password": "User123!"},
    )
    if login_resp.status_code == 200:
        token = login_resp.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # Fallback to direct JWT token generation for test isolation
    user = seed_data["users_by_email"]["user@bilcode.id"]
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def dummy_image_bytes() -> bytes:
    """Return valid JPEG image bytes dynamically generated via Pillow."""
    image = Image.new("RGB", (128, 128), color=(34, 139, 34))  # Forest green
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


@pytest.fixture(scope="session")
def dummy_png_bytes() -> bytes:
    """Return valid PNG image bytes dynamically generated via Pillow."""
    image = Image.new("RGB", (128, 128), color=(2, 132, 199))  # Sky blue
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture(scope="session")
def dummy_webp_bytes() -> bytes:
    """Return valid WebP image bytes dynamically generated via Pillow."""
    image = Image.new("RGB", (128, 128), color=(217, 119, 6))  # Amber
    buffer = io.BytesIO()
    image.save(buffer, format="WEBP")
    return buffer.getvalue()


@pytest.fixture(scope="session")
def corrupt_image_bytes() -> bytes:
    """Return corrupted non-image binary bytes with pseudo-JPEG header."""
    return b"\xff\xd8\xff\xe0CORRUPT_BYTES_SWMS_GARBAGE_PAYLOAD\x00\x01\x02\x03"


@pytest.fixture(scope="session")
def empty_file_bytes() -> bytes:
    """Return 0-byte empty binary payload."""
    return b""
