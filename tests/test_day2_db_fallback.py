"""Database Connectivity, SQLite Automatic Fallback, and ERD Conformance Test Suite.

Verifies:
- Automatic local SQLite fallback when PostgreSQL is offline or unreachable (ORIGINAL_REQUEST R1)
- In-memory SQLite StaticPool multi-connection state retention
- SQLite foreign key pragma enforcement (PRAGMA foreign_keys=ON)
- Model metadata and table structure conformity to docs/ERD.md
- Idempotent seeding logic and native Bcrypt password verification
"""

import uuid
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import (
    Base,
    configure_sqlite_engine,
    create_app_engine,
)
from app.core.seed import (
    INITIAL_CATEGORIES,
    DEFAULT_USERS,
    hash_password,
    seed_database,
    verify_password,
)
from app.models.category import Category
from app.models.log import ReportLog
from app.models.report import WasteReport
from app.models.user import User


class TestDatabaseConnectivityAndFallback:
    """Test suite verifying database fallback mechanism and SQLite configurations."""

    def test_automatic_sqlite_fallback_on_unreachable_postgres(self):
        """Verify engine automatically falls back to local SQLite when PostgreSQL is unreachable."""
        unreachable_pg_url = "postgresql+psycopg2://postgres:wrong_password@127.0.0.1:59999/swms_nonexistent"
        fallback_sqlite_url = "sqlite:///:memory:"

        fallback_engine = create_app_engine(
            database_url=unreachable_pg_url,
            fallback_url=fallback_sqlite_url,
        )

        assert fallback_engine is not None
        assert "sqlite" in str(fallback_engine.url)

        # Verify engine is functional by executing a simple probe
        with fallback_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1

        fallback_engine.dispose()

    def test_sqlite_engine_direct_creation_without_postgres(self):
        """Verify SQLite URL directly initializes SQLite without probe delays."""
        sqlite_url = "sqlite:///:memory:"
        engine = configure_sqlite_engine(sqlite_url)

        assert engine.url.drivername == "sqlite"
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 42")).scalar()
            assert result == 42

        engine.dispose()

    def test_sqlite_foreign_keys_pragma_active(self, test_engine):
        """Verify PRAGMA foreign_keys is strictly enabled (returns 1) on SQLite connections."""
        with test_engine.connect() as conn:
            cursor = conn.execute(text("PRAGMA foreign_keys;"))
            fk_status = cursor.scalar()
            assert fk_status == 1, f"Expected PRAGMA foreign_keys=1, got {fk_status}"

    def test_foreign_key_enforcement_raises_integrity_error(self, db_session: Session):
        """Verify inserting a WasteReport with non-existent foreign keys triggers IntegrityError."""
        non_existent_user_id = uuid.uuid4()
        non_existent_category_id = 99999

        invalid_report = WasteReport(
            id=uuid.uuid4(),
            user_id=non_existent_user_id,
            category_id=non_existent_category_id,
            title="Laporan Tanpa Relasi Valid",
            image_url="http://localhost:8000/uploads/reports/test.jpg",
            latitude=-6.2088,
            longitude=106.8456,
            status="Pending",
        )

        db_session.add(invalid_report)
        with pytest.raises(IntegrityError):
            db_session.flush()

        db_session.rollback()

    def test_cascade_delete_waste_reports_and_logs(self, db_session: Session, seed_data):
        """Verify cascade delete and foreign key relationships on SQLite."""
        user = User(
            email=f"cascade_{uuid.uuid4().hex[:6]}@example.com",
            password_hash="hash",
            full_name="Cascade User",
            role="user",
        )
        cat = seed_data["categories"][0]
        db_session.add(user)
        db_session.flush()

        report = WasteReport(
            user_id=user.id,
            category_id=cat.id,
            title="Test Cascade Report",
            image_url="http://localhost:8000/uploads/reports/cascade.jpg",
            latitude=-6.2088,
            longitude=106.8456,
            status="Pending",
        )
        db_session.add(report)
        db_session.flush()

        log = ReportLog(
            report_id=report.id,
            actor_id=user.id,
            previous_status=None,
            new_status="Pending",
            remarks="Initial submission",
        )
        db_session.add(log)
        db_session.commit()

        report_id = report.id
        log_id = log.id

        # Deleting the report should cascade delete its report_logs
        db_session.delete(report)
        db_session.commit()

        assert db_session.query(WasteReport).filter_by(id=report_id).first() is None
        assert db_session.query(ReportLog).filter_by(id=log_id).first() is None

        # Deleting the user should cascade delete any attached reports
        report2 = WasteReport(
            user_id=user.id,
            category_id=cat.id,
            title="Test Cascade Report 2",
            image_url="http://localhost:8000/uploads/reports/cascade2.jpg",
            latitude=-6.2088,
            longitude=106.8456,
            status="Pending",
        )
        db_session.add(report2)
        db_session.commit()
        report2_id = report2.id

        db_session.delete(user)
        db_session.commit()

        assert db_session.query(User).filter_by(id=user.id).first() is None
        assert db_session.query(WasteReport).filter_by(id=report2_id).first() is None

    def test_static_pool_in_memory_state_retention(self):

        """Verify StaticPool maintains shared tables across separate connection checkouts."""
        mem_engine = configure_sqlite_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=mem_engine)

        SessionA = sessionmaker(bind=mem_engine)
        SessionB = sessionmaker(bind=mem_engine)

        session_a = SessionA()
        cat = Category(id=101, slug="test-cat", name="Test Category", badge_color="#000000")
        session_a.add(cat)
        session_a.commit()
        session_a.close()

        # Connect with separate session checkout
        session_b = SessionB()
        fetched = session_b.query(Category).filter_by(id=101).first()
        assert fetched is not None
        assert fetched.name == "Test Category"
        session_b.close()

        mem_engine.dispose()


class TestERDSchemaConformance:
    """Test suite verifying table schema, columns, and constraints conform to docs/ERD.md."""

    def test_erd_required_tables_exist(self, test_engine):
        """Verify all 4 core tables specified in docs/ERD.md exist in the database."""
        inspector = inspect(test_engine)
        tables = set(inspector.get_table_names())
        required_tables = {"users", "categories", "waste_reports", "report_logs"}

        assert required_tables.issubset(tables), f"Missing required tables: {required_tables - tables}"

    def test_users_table_columns_and_nullability(self, test_engine):
        """Verify users table columns conform to docs/ERD.md."""
        inspector = inspect(test_engine)
        cols = {col["name"]: col for col in inspector.get_columns("users")}

        assert "id" in cols
        assert "email" in cols and not cols["email"]["nullable"]
        assert "password_hash" in cols and not cols["password_hash"]["nullable"]
        assert "full_name" in cols and not cols["full_name"]["nullable"]
        assert "role" in cols and not cols["role"]["nullable"]
        assert "phone_number" in cols and cols["phone_number"]["nullable"]
        assert "is_active" in cols
        assert "created_at" in cols
        assert "updated_at" in cols

    def test_categories_table_columns_and_nullability(self, test_engine):
        """Verify categories table columns conform to docs/ERD.md."""
        inspector = inspect(test_engine)
        cols = {col["name"]: col for col in inspector.get_columns("categories")}

        assert "id" in cols
        assert "slug" in cols and not cols["slug"]["nullable"]
        assert "name" in cols and not cols["name"]["nullable"]
        assert "description" in cols and cols["description"]["nullable"]
        assert "badge_color" in cols
        assert "created_at" in cols

    def test_waste_reports_table_columns_and_nullability(self, test_engine):
        """Verify waste_reports table columns conform to docs/ERD.md."""
        inspector = inspect(test_engine)
        cols = {col["name"]: col for col in inspector.get_columns("waste_reports")}

        assert "id" in cols
        assert "user_id" in cols and not cols["user_id"]["nullable"]
        assert "category_id" in cols and not cols["category_id"]["nullable"]
        assert "title" in cols and not cols["title"]["nullable"]
        assert "image_url" in cols and not cols["image_url"]["nullable"]
        assert "latitude" in cols and not cols["latitude"]["nullable"]
        assert "longitude" in cols and not cols["longitude"]["nullable"]
        assert "status" in cols and not cols["status"]["nullable"]
        assert "detected_category" in cols
        assert "ai_confidence" in cols
        assert "admin_notes" in cols
        assert "resolved_at" in cols
        assert "created_at" in cols
        assert "updated_at" in cols

    def test_report_logs_table_columns_and_nullability(self, test_engine):
        """Verify report_logs table columns conform to docs/ERD.md."""
        inspector = inspect(test_engine)
        cols = {col["name"]: col for col in inspector.get_columns("report_logs")}

        assert "id" in cols
        assert "report_id" in cols and not cols["report_id"]["nullable"]
        assert "actor_id" in cols
        assert "previous_status" in cols
        assert "new_status" in cols and not cols["new_status"]["nullable"]
        assert "remarks" in cols
        assert "created_at" in cols


class TestDatabaseSeedingAndSecurity:
    """Test suite verifying master data seeding and native bcrypt password utilities."""

    def test_seed_database_populates_required_categories(self, seed_data):
        """Verify 3 standard master categories are seeded per docs/RUNBOOK.md."""
        categories_by_slug = seed_data["categories_by_slug"]

        assert "organic" in categories_by_slug
        assert categories_by_slug["organic"].name == "Organic Waste"
        assert categories_by_slug["organic"].badge_color == "#16a34a"

        assert "plastic" in categories_by_slug
        assert categories_by_slug["plastic"].name == "Plastic Waste"
        assert categories_by_slug["plastic"].badge_color == "#0284c7"

        assert "paper" in categories_by_slug
        assert categories_by_slug["paper"].name == "Paper Waste"
        assert categories_by_slug["paper"].badge_color == "#d97706"

    def test_seed_database_populates_default_users(self, seed_data):
        """Verify default admin and user accounts are seeded per docs/RUNBOOK.md."""
        users_by_email = seed_data["users_by_email"]

        assert "admin@bilcode.id" in users_by_email
        admin = users_by_email["admin@bilcode.id"]
        assert admin.role == "admin"
        assert admin.full_name == "Super Admin"
        assert verify_password("Admin123!", admin.password_hash)

        assert "user@bilcode.id" in users_by_email
        user = users_by_email["user@bilcode.id"]
        assert user.role == "user"
        assert user.full_name == "Warga Pelapor"
        assert verify_password("User123!", user.password_hash)

    def test_seed_database_is_idempotent(self, db_session: Session):
        """Verify executing seed_database multiple times does not duplicate records or error."""
        first_run = seed_database(db_session)
        second_run = seed_database(db_session)

        assert second_run["categories"] == 0
        assert second_run["users"] == 0

        total_categories = db_session.query(Category).count()
        total_users = db_session.query(User).count()

        assert total_categories == 3
        assert total_users == 2

    def test_native_bcrypt_hashing_and_verification_rules(self):
        """Verify native bcrypt password hashing conforms to standard prefix and validation rules."""
        raw_password = "SecretPassword123!"
        hashed = hash_password(raw_password)

        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
        assert verify_password(raw_password, hashed) is True
        assert verify_password("WrongPassword123!", hashed) is False
        assert verify_password("", hashed) is False
