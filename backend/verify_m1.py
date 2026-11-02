"""Standalone verification script for Milestone 1 (M1).

Verifies:
1. Engine connects to SQLite fallback when PostgreSQL is offline.
2. All 4 tables exist and match schema constraints.
3. Seeding creates 3 categories and 2 users, and is idempotent when run twice.
4. Password verification passes with native bcrypt.
5. Foreign keys and cascade delete work in SQLite (PRAGMA foreign_keys=ON;).
"""

import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, configure_sqlite_engine, create_app_engine
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


def verify_m1():
    print("==================================================================")
    print(" [SWMS M1 VERIFICATION] Running Milestone 1 Validation Checks")
    print("==================================================================")

    # -------------------------------------------------------------------------
    # Check 1: Engine connects to SQLite fallback when PostgreSQL offline
    # -------------------------------------------------------------------------
    print("\n[Check 1/5] Verifying PostgreSQL probe & SQLite automatic fallback...")
    dummy_pg = "postgresql+psycopg2://postgres:wrong_pwd@127.0.0.1:59999/swms_dummy"
    test_sqlite = "sqlite:///:memory:"
    engine = create_app_engine(database_url=dummy_pg, fallback_url=test_sqlite)
    assert engine is not None, "Failed to instantiate engine"
    assert "sqlite" in str(engine.url), f"Expected sqlite in url, got {engine.url}"
    with engine.connect() as conn:
        val = conn.execute(text("SELECT 100")).scalar()
        assert val == 100, f"Expected 100, got {val}"
    print(" -> PASS: PostgreSQL probe timed out safely and fell back to SQLite.")

    # -------------------------------------------------------------------------
    # Check 2: All 4 tables exist and match schema
    # -------------------------------------------------------------------------
    print("\n[Check 2/5] Verifying all 4 ERD tables and schema structure...")
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    expected_tables = {"users", "categories", "waste_reports", "report_logs"}
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

    # Check key columns
    user_cols = {c["name"] for c in inspector.get_columns("users")}
    assert {"id", "email", "password_hash", "full_name", "role", "is_active"}.issubset(user_cols)

    cat_cols = {c["name"] for c in inspector.get_columns("categories")}
    assert {"id", "slug", "name", "badge_color"}.issubset(cat_cols)

    report_cols = {c["name"] for c in inspector.get_columns("waste_reports")}
    assert {"id", "user_id", "category_id", "title", "image_url", "latitude", "longitude", "status"}.issubset(report_cols)

    log_cols = {c["name"] for c in inspector.get_columns("report_logs")}
    assert {"id", "report_id", "actor_id", "previous_status", "new_status", "created_at"}.issubset(log_cols)
    print(" -> PASS: All 4 tables (users, categories, waste_reports, report_logs) exist with valid schema.")

    # -------------------------------------------------------------------------
    # Check 3: Seeding creates 3 categories, 2 users, and is idempotent
    # -------------------------------------------------------------------------
    print("\n[Check 3/5] Verifying seeding counts and idempotency...")
    Session = sessionmaker(bind=engine)
    session = Session()

    res1 = seed_database(session)
    assert res1["categories"] == 3, f"Expected 3 categories seeded, got {res1['categories']}"
    assert res1["users"] == 2, f"Expected 2 users seeded, got {res1['users']}"

    # Run second time
    res2 = seed_database(session)
    assert res2["categories"] == 0, f"Expected 0 categories on second run, got {res2['categories']}"
    assert res2["users"] == 0, f"Expected 0 users on second run, got {res2['users']}"

    total_cats = session.query(Category).count()
    total_users = session.query(User).count()
    assert total_cats == 3, f"Total categories should be 3, got {total_cats}"
    assert total_users == 2, f"Total users should be 2, got {total_users}"
    print(" -> PASS: Seeding is 100% idempotent; 3 categories and 2 users created.")

    # -------------------------------------------------------------------------
    # Check 4: Password verification passes with native bcrypt
    # -------------------------------------------------------------------------
    print("\n[Check 4/5] Verifying native bcrypt password hashing & verification...")
    admin = session.query(User).filter_by(email="admin@bilcode.id").first()
    assert admin is not None, "Admin user missing"
    assert verify_password("Admin123!", admin.password_hash) is True, "Admin password verification failed"
    assert verify_password("WrongPassword!", admin.password_hash) is False, "False positive in verification"

    user = session.query(User).filter_by(email="user@bilcode.id").first()
    assert user is not None, "Citizen user missing"
    assert verify_password("User123!", user.password_hash) is True, "Citizen password verification failed"
    assert verify_password("WrongPassword!", user.password_hash) is False, "False positive in verification"
    print(" -> PASS: Native bcrypt hashing and verification succeeded for all accounts.")

    # -------------------------------------------------------------------------
    # Check 5: Foreign keys and cascade delete in SQLite
    # -------------------------------------------------------------------------
    print("\n[Check 5/5] Verifying SQLite foreign keys (PRAGMA foreign_keys=ON) & cascade delete...")
    with engine.connect() as conn:
        fk_on = conn.execute(text("PRAGMA foreign_keys;")).scalar()
        assert fk_on == 1, f"Expected PRAGMA foreign_keys=1, got {fk_on}"

    # Test cascade delete:
    test_user = User(
        email="cascade_tester@example.com",
        password_hash=hash_password("password"),
        full_name="Cascade Tester",
        role="user",
    )
    session.add(test_user)
    session.flush()

    test_report = WasteReport(
        user_id=test_user.id,
        category_id=1,
        title="Cascade Report Test",
        image_url="http://localhost:8000/uploads/reports/test.jpg",
        latitude=-6.2,
        longitude=106.8,
        status="Pending",
    )
    session.add(test_report)
    session.flush()

    test_log = ReportLog(
        report_id=test_report.id,
        actor_id=test_user.id,
        previous_status=None,
        new_status="Pending",
        remarks="Test log entry",
    )
    session.add(test_log)
    session.commit()

    report_id = test_report.id
    log_id = test_log.id

    # Delete report -> log should be cascade deleted
    session.delete(test_report)
    session.commit()
    assert session.query(WasteReport).filter_by(id=report_id).first() is None
    assert session.query(ReportLog).filter_by(id=log_id).first() is None
    print(" -> PASS: SQLite PRAGMA foreign_keys=ON active and cascade delete functions correctly.")

    session.close()
    engine.dispose()

    print("\n==================================================================")
    print(" [SWMS M1 VERIFICATION] ALL 5 CHECKS PASSED (100% SUCCESS)!")
    print("==================================================================\n")


if __name__ == "__main__":
    verify_m1()
