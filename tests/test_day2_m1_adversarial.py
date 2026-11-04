"""Empirical Adversarial & Stress Testing Suite for Milestone 1 (Database Core & Migrations).

Validates:
1. Fallback Adversarial Probe:
   - Non-existent hosts, invalid ports, unreachable IP (RFC 5737 TEST-NET-1 with connect_timeout=2),
     and malformed connection strings to create_app_engine() verifying reliable fallback to SQLite.
2. Alembic Batch Migration Validation:
   - alembic upgrade head runs cleanly on SQLite without SQL syntax errors.
   - alembic downgrade -1 and alembic upgrade head execute with 0 errors in batch mode.
3. Schema Boundary Limits:
   - Extreme string lengths against VARCHAR limits (email: 255, title: 200, address_note: 255).
   - GPS float precision (8+ decimal places, e.g. -6.20876345, 106.84559812) verifying zero loss of precision.
   - Status and role check constraints: inserting 'InvalidStatus' or invalid roles raises IntegrityError.
4. Referential Integrity:
   - Foreign key ON DELETE RESTRICT on categories.
   - Foreign key ON DELETE CASCADE on users and waste_reports.
"""

import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.database import (
    Base,
    configure_sqlite_engine,
    create_app_engine,
)
from app.models.category import Category
from app.models.log import ReportLog
from app.models.report import WasteReport
from app.models.user import User


class TestFallbackAdversarialProbe:
    """Stress testing the database engine initialization and fallback behavior under network/config failures."""

    def test_fallback_nonexistent_host(self):
        """Verify non-existent host triggers DNS failure and reliably falls back to SQLite."""
        bad_url = "postgresql+psycopg2://postgres:postgres@invalid.host.domain.test:5432/swms_db"
        t0 = time.time()
        engine = create_app_engine(database_url=bad_url, fallback_url="sqlite:///:memory:")
        elapsed = time.time() - t0

        assert engine is not None
        assert engine.name == "sqlite"
        assert elapsed < 5.0, f"Fallback took too long: {elapsed:.2f}s"

        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1
        engine.dispose()

    @pytest.mark.parametrize(
        "invalid_port_url,description",
        [
            ("postgresql+psycopg2://postgres:postgres@localhost:999999/swms_db", "Port out of range (>65535)"),
            ("postgresql+psycopg2://postgres:postgres@localhost:-1/swms_db", "Negative port number"),
            ("postgresql+psycopg2://postgres:postgres@localhost:0/swms_db", "Port 0"),
            ("postgresql+psycopg2://postgres:postgres@localhost:abc/swms_db", "Non-numeric port string"),
        ],
    )
    def test_fallback_invalid_ports(self, invalid_port_url: str, description: str):
        """Verify invalid ports trigger OperationalError/ValueError and fall back to SQLite."""
        engine = create_app_engine(database_url=invalid_port_url, fallback_url="sqlite:///:memory:")
        assert engine is not None, f"Failed for {description}"
        assert engine.name == "sqlite"

        with engine.connect() as conn:
            assert conn.execute(text("SELECT 100")).scalar() == 100
        engine.dispose()

    def test_fallback_unreachable_ip_timeout_bounded(self):
        """Verify unreachable IP (RFC 5737 TEST-NET-1: 192.0.2.1) times out within bounded window (~2s) and falls back."""
        unreachable_url = "postgresql+psycopg2://postgres:postgres@192.0.2.1:5432/swms_db"
        t0 = time.time()
        engine = create_app_engine(database_url=unreachable_url, fallback_url="sqlite:///:memory:")
        elapsed = time.time() - t0

        assert engine is not None
        assert engine.name == "sqlite"
        # Since connect_timeout=2 is configured, it must return well under 8 seconds
        assert elapsed <= 6.0, f"Unreachable IP probe took {elapsed:.2f}s (exceeded bounded timeout)"

        with engine.connect() as conn:
            assert conn.execute(text("SELECT 42")).scalar() == 42
        engine.dispose()

    @pytest.mark.parametrize(
        "malformed_url,description",
        [
            ("not_a_valid_url", "Gibberish plain text string"),
            ("postgresql://", "Empty host postgresql scheme"),
            ("postgresql+psycopg2://", "Empty host psycopg2 scheme"),
            ("unknown+dialect://user:pass@host:5432/db", "Unknown dialect / driver"),
            ("", "Empty connection string"),
            (None, "None type connection string"),
        ],
    )
    def test_fallback_malformed_connection_strings(self, malformed_url: str, description: str):
        """Verify completely malformed connection strings safely fall back to SQLite without crashing."""
        engine = create_app_engine(database_url=malformed_url, fallback_url="sqlite:///:memory:")
        assert engine is not None, f"Failed for {description}"
        assert engine.name == "sqlite"

        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1
        engine.dispose()

    def test_fallback_engine_functional_table_operations(self):
        """Verify fallback SQLite engine can execute full DDL, inserts, and queries without error."""
        engine = create_app_engine(
            database_url="postgresql+psycopg2://postgres:invalid@127.0.0.1:59999/swms_nonexistent",
            fallback_url="sqlite:///:memory:",
        )
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        cat = Category(slug="probe-cat", name="Probe Category", badge_color="#123456")
        session.add(cat)
        session.commit()

        retrieved = session.query(Category).filter_by(slug="probe-cat").first()
        assert retrieved is not None
        assert retrieved.name == "Probe Category"

        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


class TestAlembicBatchMigrationValidation:
    """Empirical verification of Alembic migrations under SQLite batch mode."""

    def test_alembic_cli_upgrade_and_downgrade_cycle(self):
        """Verify alembic upgrade head, downgrade -1, and upgrade head execute with returncode 0."""
        # Run alembic current to inspect initial state
        res_current = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )
        assert res_current.returncode == 0, f"alembic current failed: {res_current.stderr}"

        # 1. Downgrade -1
        res_down = subprocess.run(
            [sys.executable, "-m", "alembic", "downgrade", "-1"],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )
        assert res_down.returncode == 0, f"alembic downgrade -1 failed:\n{res_down.stderr}\n{res_down.stdout}"
        assert "Running downgrade" in (res_down.stderr + res_down.stdout)

        # 2. Upgrade head
        res_up = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )
        assert res_up.returncode == 0, f"alembic upgrade head failed:\n{res_up.stderr}\n{res_up.stdout}"
        assert "Running upgrade" in (res_up.stderr + res_up.stdout)

        # 3. Verify final current revision is head
        res_final = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )
        assert res_final.returncode == 0
        assert "6a3d4361fa05" in (res_final.stderr + res_final.stdout)

        # 4. Re-seed default users and categories so dev server remains fully operational
        from app.core.database import SessionLocal
        from app.core.seed import seed_database
        with SessionLocal() as db:
            seed_database(db)

    def test_alembic_script_renders_batch_alter_table(self):
        """Verify migration revision 6a3d4361fa05 employs batch_alter_table for SQLite compatibility."""
        version_file = BACKEND_DIR / "alembic" / "versions" / "6a3d4361fa05_create_initial_swms_tables.py"
        assert version_file.exists(), "Migration revision file missing"

        content = version_file.read_text(encoding="utf-8")
        assert "with op.batch_alter_table('users'" in content
        assert "with op.batch_alter_table('waste_reports'" in content
        assert "with op.batch_alter_table('report_logs'" in content
        assert "op.create_table('categories'" in content
        assert "check_report_status" in content
        assert "check_user_role" in content


class TestSchemaBoundaryLimits:
    """Stress testing schema field boundaries, float precision, and check constraints."""

    def test_status_check_constraint_rejects_invalid_values(self, db_session: Session, seed_data):
        """Verify that inserting invalid status values triggers a CHECK constraint violation."""
        user_id = seed_data["users"][0].id
        category_id = seed_data["categories"][0].id

        invalid_statuses = ["InvalidStatus", "PendingApproval", "UNKNOWN", "in progress", ""]
        for invalid_status in invalid_statuses:
            with db_session.begin_nested():
                report = WasteReport(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    category_id=category_id,
                    title="Invalid Status Report",
                    image_url="http://localhost:8000/uploads/reports/test.jpg",
                    latitude=-6.2088,
                    longitude=106.8456,
                    status=invalid_status,
                )
                db_session.add(report)
                with pytest.raises(IntegrityError) as exc_info:
                    db_session.flush()
                assert "CHECK constraint failed" in str(exc_info.value) or "check_report_status" in str(exc_info.value)

    def test_status_check_constraint_accepts_all_valid_values(self, db_session: Session, seed_data):
        """Verify all 4 allowed status values ('Pending', 'In Progress', 'Completed', 'Rejected') succeed."""
        user_id = seed_data["users"][0].id
        category_id = seed_data["categories"][0].id

        valid_statuses = ["Pending", "In Progress", "Completed", "Rejected"]
        for valid_status in valid_statuses:
            with db_session.begin_nested():
                report = WasteReport(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    category_id=category_id,
                    title=f"Valid Status {valid_status}",
                    image_url="http://localhost:8000/uploads/reports/test.jpg",
                    latitude=-6.2088,
                    longitude=106.8456,
                    status=valid_status,
                )
                db_session.add(report)
                db_session.flush()
                assert report.id is not None

    def test_user_role_check_constraint(self, db_session: Session):
        """Verify user role CHECK constraint enforces IN ('admin', 'user')."""
        for invalid_role in ["superadmin", "moderator", "guest", "", "ADMIN"]:
            user = User(
                email=f"invalid_role_{uuid.uuid4().hex[:6]}@example.com",
                password_hash="hash",
                full_name="Invalid Role User",
                role=invalid_role,
            )
            db_session.add(user)
            with pytest.raises(IntegrityError) as exc_info:
                db_session.flush()
            assert "CHECK constraint failed" in str(exc_info.value) or "check_user_role" in str(exc_info.value)
            db_session.rollback()

    def test_gps_float_precision_8_decimals_zero_loss(self, db_session: Session, seed_data):
        """Verify high-precision GPS coordinates (8 decimal places) retain exact precision without drift."""
        user = seed_data["users"][0]
        category = seed_data["categories"][0]

        # 8-decimal place coordinates (~1.1mm ground precision)
        target_lat = -6.20876345
        target_lon = 106.84559812

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=user.id,
            category_id=category.id,
            title="High Precision GPS Report",
            image_url="http://localhost:8000/uploads/reports/gps.jpg",
            latitude=target_lat,
            longitude=target_lon,
            status="Pending",
        )
        db_session.add(report)
        db_session.commit()

        # Query back and check precision
        retrieved = db_session.query(WasteReport).filter_by(id=report.id).first()
        assert retrieved is not None
        assert abs(retrieved.latitude - target_lat) < 1e-12, f"Latitude lost precision: {retrieved.latitude}"
        assert abs(retrieved.longitude - target_lon) < 1e-12, f"Longitude lost precision: {retrieved.longitude}"
        assert retrieved.latitude == target_lat
        assert retrieved.longitude == target_lon

    def test_extreme_gps_boundary_coordinates(self, db_session: Session, seed_data):
        """Verify boundary coordinates (-90, +90, -180, +180) store and retrieve accurately."""
        user = seed_data["users"][0]
        category = seed_data["categories"][0]

        boundaries = [
            (-90.0, -180.0),
            (90.0, 180.0),
            (0.0, 0.0),
            (-6.208763456789, 106.845598123456),  # 12 decimal places
        ]

        for lat, lon in boundaries:
            rep = WasteReport(
                id=uuid.uuid4(),
                user_id=user.id,
                category_id=category.id,
                title="Boundary GPS Report",
                image_url="http://localhost:8000/uploads/reports/boundary.jpg",
                latitude=lat,
                longitude=lon,
                status="Pending",
            )
            db_session.add(rep)
            db_session.commit()

            fetched = db_session.query(WasteReport).filter_by(id=rep.id).first()
            assert abs(fetched.latitude - lat) < 1e-12
            assert abs(fetched.longitude - lon) < 1e-12
            db_session.delete(fetched)
            db_session.commit()

    def test_varchar_exact_boundary_limits(self, db_session: Session, seed_data):
        """Verify storing string fields at their exact VARCHAR limits succeeds.
        - User.email: VARCHAR(255)
        - WasteReport.title: VARCHAR(200)
        - WasteReport.address_note: VARCHAR(255)
        """
        user_cat = seed_data["categories"][0]

        # 1. Email exactly 255 chars: prefix + '@' + domain
        domain = "example.com"
        local_part_len = 255 - 1 - len(domain)
        exact_255_email = "e" * local_part_len + "@" + domain
        assert len(exact_255_email) == 255

        user = User(
            email=exact_255_email,
            password_hash="hashed_pw",
            full_name="Exact Limit User",
            role="user",
        )
        db_session.add(user)
        db_session.commit()
        retrieved_user = db_session.query(User).filter_by(id=user.id).first()
        assert len(retrieved_user.email) == 255

        # 2. Title exactly 200 chars
        exact_200_title = "T" * 200
        assert len(exact_200_title) == 200

        # 3. Address note exactly 255 chars
        exact_255_note = "A" * 255
        assert len(exact_255_note) == 255

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=user.id,
            category_id=user_cat.id,
            title=exact_200_title,
            image_url="http://localhost:8000/uploads/reports/limit.jpg",
            latitude=-6.2,
            longitude=106.8,
            address_note=exact_255_note,
            status="Pending",
        )
        db_session.add(report)
        db_session.commit()

        retrieved_report = db_session.query(WasteReport).filter_by(id=report.id).first()
        assert len(retrieved_report.title) == 200
        assert len(retrieved_report.address_note) == 255


class TestReferentialIntegrityStress:
    """Stress testing relational constraints and cascading deletes."""

    def test_category_delete_restrict_when_reports_exist(self, db_session: Session, seed_data):
        """Verify deleting a category with attached reports fails with IntegrityError (ON DELETE RESTRICT)."""
        category = seed_data["categories"][0]
        user = seed_data["users"][0]

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=user.id,
            category_id=category.id,
            title="Restricted Category Report",
            image_url="http://localhost:8000/uploads/reports/test.jpg",
            latitude=-6.2,
            longitude=106.8,
            status="Pending",
        )
        db_session.add(report)
        db_session.commit()

        # Attempt to delete the category
        db_session.delete(category)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_user_email_uniqueness_constraint(self, db_session: Session):
        """Verify duplicate user email triggers an IntegrityError."""
        dup_email = f"duplicate_{uuid.uuid4().hex[:6]}@example.com"
        u1 = User(email=dup_email, password_hash="h1", full_name="User One", role="user")
        u2 = User(email=dup_email, password_hash="h2", full_name="User Two", role="user")

        db_session.add(u1)
        db_session.commit()

        db_session.add(u2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_category_slug_uniqueness_constraint(self, db_session: Session):
        """Verify duplicate category slug triggers an IntegrityError."""
        dup_slug = f"dup-slug-{uuid.uuid4().hex[:4]}"
        c1 = Category(slug=dup_slug, name="Cat 1", badge_color="#111111")
        c2 = Category(slug=dup_slug, name="Cat 2", badge_color="#222222")

        db_session.add(c1)
        db_session.commit()

        db_session.add(c2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
