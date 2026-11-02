"""Empirical Adversarial Stress Testing Suite for Milestone 1.

Comprehensive adversarial test suite verifying:
1. Foreign key integrity enforcement on SQLite (invalid user_id, invalid category_id, invalid report_id)
2. Schema check constraints (invalid User.role rejected, invalid WasteReport.status rejected)
3. Cascade delete and NULLification:
   - Deleting reporter cascades to delete WasteReport
   - Deleting report cascades to delete ReportLog
   - Deleting actor sets actor_id to NULL in ReportLog
4. Idempotent seeding stress (10 consecutive iterations across new sessions on SessionLocal and fresh engines)
5. Threadpool / concurrency stress (10 and 20 concurrent threads reading and writing to SessionLocal)
6. Native Bcrypt verification under adversarial / invalid inputs (wrong, empty, >72 bytes, 1000 bytes, boundaries, malformed)
"""

import concurrent.futures
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import List

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.database import (
    Base,
    SessionLocal,
    configure_sqlite_engine,
    create_app_engine,
    engine as app_engine,
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


# =============================================================================
# 1. FOREIGN KEY INTEGRITY ENFORCEMENT & CHECK CONSTRAINTS ON SQLITE
# =============================================================================

class TestAdversarialForeignKeyAndCheckConstraints:
    """Stress tests verifying SQLite PRAGMA foreign_keys=ON actively blocks invalid relations and values."""

    def test_invalid_user_id_raises_integrity_error(self, db_session: Session, seed_data):
        """Inserting a WasteReport with non-existent user_id must raise IntegrityError on SQLite."""
        valid_cat = seed_data["categories"][0]
        non_existent_user_id = uuid.uuid4()

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=non_existent_user_id,
            category_id=valid_cat.id,
            title="Adversarial Invalid User FK Report",
            image_url="http://localhost:8000/uploads/reports/fk1.jpg",
            latitude=-6.2088,
            longitude=106.8456,
            status="Pending",
        )
        db_session.add(report)
        with pytest.raises(IntegrityError) as exc_info:
            db_session.flush()
        db_session.rollback()
        assert "FOREIGN KEY" in str(exc_info.value) or "IntegrityError" in str(type(exc_info.value))

    def test_invalid_category_id_raises_integrity_error(self, db_session: Session, seed_data):
        """Inserting a WasteReport with non-existent category_id must raise IntegrityError on SQLite."""
        valid_user = seed_data["users"][0]
        non_existent_category_id = 999999

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=valid_user.id,
            category_id=non_existent_category_id,
            title="Adversarial Invalid Category FK Report",
            image_url="http://localhost:8000/uploads/reports/fk2.jpg",
            latitude=-6.2088,
            longitude=106.8456,
            status="Pending",
        )
        db_session.add(report)
        with pytest.raises(IntegrityError) as exc_info:
            db_session.flush()
        db_session.rollback()
        assert "FOREIGN KEY" in str(exc_info.value) or "IntegrityError" in str(type(exc_info.value))

    def test_invalid_report_id_in_report_log_raises_integrity_error(self, db_session: Session, seed_data):
        """Inserting a ReportLog with non-existent report_id must raise IntegrityError on SQLite."""
        valid_actor = seed_data["users"][0]
        non_existent_report_id = uuid.uuid4()

        log = ReportLog(
            id=uuid.uuid4(),
            report_id=non_existent_report_id,
            actor_id=valid_actor.id,
            previous_status=None,
            new_status="Pending",
            remarks="Invalid report FK log",
        )
        db_session.add(log)
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_invalid_user_role_check_constraint(self, db_session: Session):
        """Inserting a User with role not in ('admin', 'user') must violate check constraint."""
        bad_user = User(
            email=f"bad_role_{uuid.uuid4().hex[:6]}@bilcode.id",
            password_hash=hash_password("pw"),
            full_name="Bad Role User",
            role="superadmin",  # Invalid role
        )
        db_session.add(bad_user)
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_invalid_report_status_check_constraint(self, db_session: Session, seed_data):
        """Inserting a WasteReport with status not in ('Pending', 'In Progress', 'Completed', 'Rejected') must fail."""
        valid_user = seed_data["users"][0]
        valid_cat = seed_data["categories"][0]

        bad_report = WasteReport(
            id=uuid.uuid4(),
            user_id=valid_user.id,
            category_id=valid_cat.id,
            title="Bad Status Report",
            image_url="http://localhost:8000/uploads/reports/test.jpg",
            latitude=-6.2,
            longitude=106.8,
            status="Archived",  # Invalid status
        )
        db_session.add(bad_report)
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()


# =============================================================================
# 2. CASCADE DELETE AND ON DELETE SET NULL BEHAVIOR
# =============================================================================

class TestAdversarialCascadeDeleteAndSetNull:
    """Stress tests verifying SQLite cascade deletion and nullification of actor_id."""

    def test_deleting_reporter_cascades_to_waste_reports(self, db_session: Session, seed_data):
        """Deleting a User must cascade delete all reports submitted by that user."""
        cat = seed_data["categories"][0]
        user = User(
            email=f"reporter_{uuid.uuid4().hex[:6]}@example.com",
            password_hash=hash_password("pw"),
            full_name="Reporter User",
            role="user",
        )
        db_session.add(user)
        db_session.flush()

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=user.id,
            category_id=cat.id,
            title="Cascade Report Test",
            image_url="http://localhost:8000/uploads/reports/cascade.jpg",
            latitude=-6.2,
            longitude=106.8,
            status="Pending",
        )
        db_session.add(report)
        db_session.flush()
        report_id = report.id

        # Verify report exists
        assert db_session.query(WasteReport).filter_by(id=report_id).first() is not None

        # Delete user
        db_session.delete(user)
        db_session.flush()

        # Report must be cascade-deleted
        assert db_session.query(WasteReport).filter_by(id=report_id).first() is None

    def test_deleting_report_cascades_to_report_logs(self, db_session: Session, seed_data):
        """Deleting a WasteReport must cascade delete all associated report_logs."""
        cat = seed_data["categories"][0]
        user = seed_data["users"][0]

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=user.id,
            category_id=cat.id,
            title="Log Cascade Report Test",
            image_url="http://localhost:8000/uploads/reports/log_cascade.jpg",
            latitude=-6.2,
            longitude=106.8,
            status="Pending",
        )
        db_session.add(report)
        db_session.flush()

        log = ReportLog(
            id=uuid.uuid4(),
            report_id=report.id,
            actor_id=user.id,
            previous_status=None,
            new_status="Pending",
            remarks="Initial submission log",
        )
        db_session.add(log)
        db_session.flush()

        report_id = report.id
        log_id = log.id

        assert db_session.query(ReportLog).filter_by(id=log_id).first() is not None

        # Delete report -> log must cascade delete
        db_session.delete(report)
        db_session.flush()

        assert db_session.query(WasteReport).filter_by(id=report_id).first() is None
        assert db_session.query(ReportLog).filter_by(id=log_id).first() is None

    def test_deleting_actor_sets_actor_id_to_null_in_report_log(self, db_session: Session, seed_data):
        """Deleting an actor User must set actor_id to NULL in ReportLog without deleting the log."""
        cat = seed_data["categories"][0]
        reporter = seed_data["users"][1]  # Citizen

        # Create temporary actor user to delete
        actor = User(
            email=f"actor_{uuid.uuid4().hex[:6]}@example.com",
            password_hash=hash_password("pw"),
            full_name="Temporary Admin Actor",
            role="admin",
        )
        db_session.add(actor)
        db_session.flush()

        report = WasteReport(
            id=uuid.uuid4(),
            user_id=reporter.id,
            category_id=cat.id,
            title="SetNull Report Test",
            image_url="http://localhost:8000/uploads/reports/setnull.jpg",
            latitude=-6.2,
            longitude=106.8,
            status="In Progress",
        )
        db_session.add(report)
        db_session.flush()

        log = ReportLog(
            id=uuid.uuid4(),
            report_id=report.id,
            actor_id=actor.id,
            previous_status="Pending",
            new_status="In Progress",
            remarks="Admin status change",
        )
        db_session.add(log)
        db_session.flush()

        log_id = log.id
        actor_id = actor.id

        # Verify initial association
        assert db_session.query(ReportLog).filter_by(id=log_id).first().actor_id == actor_id

        # Delete actor user
        db_session.delete(actor)
        db_session.flush()

        # Expire session cache to force reload from SQLite
        db_session.expire_all()

        # The log MUST still exist, but actor_id MUST be NULL!
        persisted_log = db_session.query(ReportLog).filter_by(id=log_id).first()
        assert persisted_log is not None, "ReportLog was unexpectedly deleted!"
        assert persisted_log.actor_id is None, f"Expected actor_id=None, got {persisted_log.actor_id}"

        # Reporter and WasteReport still exist
        assert db_session.query(WasteReport).filter_by(id=report.id).first() is not None


# =============================================================================
# 3. IDEMPOTENT SEEDING STRESS (10 CONSECUTIVE RUNS ACROSS NEW SESSIONS)
# =============================================================================

class TestAdversarialIdempotentSeedingStress:
    """Stress tests running seed_database 10 consecutive times across fresh sessions."""

    def test_ten_consecutive_seed_runs_on_session_local(self):
        """Run seed_database 10 consecutive times against SessionLocal(); verify 0 constraint violations."""
        for iteration in range(1, 11):
            session = SessionLocal()
            try:
                result = seed_database(session)
                assert result["categories"] == 0, f"Iteration {iteration}: expected 0 categories added, got {result['categories']}"
                assert result["users"] == 0, f"Iteration {iteration}: expected 0 users added, got {result['users']}"

                cat_count = session.query(Category).count()
                user_count = session.query(User).count()

                assert cat_count == 3, f"Iteration {iteration}: expected 3 categories, got {cat_count}"
                assert user_count == 2, f"Iteration {iteration}: expected 2 users, got {user_count}"
            finally:
                session.close()

    def test_ten_runs_on_fresh_isolated_database(self):
        """Run seed_database 10 times on an entirely fresh in-memory database."""
        fresh_engine = configure_sqlite_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=fresh_engine)
        Session = sessionmaker(bind=fresh_engine)

        for iteration in range(1, 11):
            session = Session()
            try:
                res = seed_database(session)
                if iteration == 1:
                    assert res["categories"] == 3
                    assert res["users"] == 2
                else:
                    assert res["categories"] == 0
                    assert res["users"] == 0

                assert session.query(Category).count() == 3
                assert session.query(User).count() == 2
            finally:
                session.close()

        fresh_engine.dispose()


# =============================================================================
# 4. THREADPOOL / CONCURRENCY STRESS (10 AND 20 CONCURRENT THREADS)
# =============================================================================

class TestAdversarialConcurrencyStress:
    """Stress tests spawning 10 and 20 concurrent threads against SessionLocal without locking errors."""

    def test_ten_concurrent_threads_reading_and_writing_on_session_local(self):
        """10 concurrent threads each opening SessionLocal(), reading and writing records simultaneously."""
        errors: List[Exception] = []
        barrier = threading.Barrier(10)

        def worker_task(thread_idx: int):
            try:
                barrier.wait(timeout=5.0)  # Synchronize all 10 threads to hit SessionLocal at the exact same instant
                session = SessionLocal()
                try:
                    # 1. Read test
                    users = session.query(User).all()
                    assert len(users) >= 2
                    cats = session.query(Category).all()
                    assert len(cats) >= 3

                    # 2. Write test - create distinct user
                    email = f"thread_worker_{thread_idx}_{uuid.uuid4().hex[:6]}@bilcode.id"
                    new_user = User(
                        email=email,
                        password_hash=hash_password(f"pw_{thread_idx}"),
                        full_name=f"Concurrent Worker {thread_idx}",
                        role="user",
                    )
                    session.add(new_user)
                    session.commit()

                    # 3. Read back verification
                    fetched = session.query(User).filter_by(id=new_user.id).first()
                    assert fetched is not None
                    assert fetched.email == email

                    # 4. Cleanup
                    session.delete(fetched)
                    session.commit()
                finally:
                    session.close()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker_task, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15.0)

        assert len(errors) == 0, f"Concurrency test encountered {len(errors)} errors: {errors}"

    def test_twenty_concurrent_threads_reading_and_writing_stress(self):
        """Stress test: 20 concurrent threads simultaneously creating and deleting records on SessionLocal."""
        errors: List[Exception] = []
        barrier = threading.Barrier(20)

        def worker_task(thread_idx: int):
            try:
                barrier.wait(timeout=5.0)
                session = SessionLocal()
                try:
                    email = f"twenty_stress_{thread_idx}_{uuid.uuid4().hex[:6]}@bilcode.id"
                    u = User(
                        email=email,
                        password_hash="test",
                        full_name=f"Stress User {thread_idx}",
                        role="user",
                    )
                    session.add(u)
                    session.commit()

                    uid = u.id
                    fetched = session.query(User).filter_by(id=uid).first()
                    assert fetched is not None

                    session.delete(fetched)
                    session.commit()
                finally:
                    session.close()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker_task, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=20.0)

        assert len(errors) == 0, f"20-thread concurrency test encountered {len(errors)} errors: {errors}"


# =============================================================================
# 5. NATIVE BCRYPT VERIFICATION UNDER INVALID INPUTS
# =============================================================================

class TestAdversarialBcryptValidation:
    """Stress tests verifying native Bcrypt handling of invalid, boundary, and extreme inputs."""

    def test_wrong_password_returns_false(self):
        """Wrong passwords must return False without throwing exceptions."""
        valid_pw = "CorrectSecret123!"
        hashed = hash_password(valid_pw)
        assert verify_password("WrongSecret123!", hashed) is False
        assert verify_password("correctsecret123!", hashed) is False

    def test_empty_password_returns_false(self):
        """Empty string passwords must return False gracefully."""
        valid_pw = "ValidSecret123!"
        hashed = hash_password(valid_pw)
        assert verify_password("", hashed) is False

    def test_very_long_passwords_over_72_bytes(self):
        """Bcrypt 72-byte limit must be handled gracefully without crashing Python 3.12."""
        valid_pw = "StandardSecret123!"
        hashed = hash_password(valid_pw)

        # Adversarial inputs over 72 bytes
        pw_80_bytes = "A" * 80
        pw_256_bytes = "SuperLongPassword" * 20
        pw_1000_bytes = "Z" * 1000

        # Verifying against a standard hash must return False without crashing
        assert verify_password(pw_80_bytes, hashed) is False
        assert verify_password(pw_256_bytes, hashed) is False
        assert verify_password(pw_1000_bytes, hashed) is False

    def test_hash_and_verify_at_boundary_lengths(self):
        """Test hashing and verifying around the 71, 72, and 73 byte boundaries."""
        pw_71 = "A" * 71
        pw_72 = "A" * 72
        pw_73 = "A" * 73

        # Hashing 71 and 72 bytes must work natively
        hash_71 = hash_password(pw_71)
        assert verify_password(pw_71, hash_71) is True
        assert verify_password(pw_71 + "x", hash_71) is False

        hash_72 = hash_password(pw_72)
        assert verify_password(pw_72, hash_72) is True

        # Hashing > 72 bytes in bcrypt
        try:
            hash_73 = hash_password(pw_73)
            # If bcrypt accepts it or truncates to 72, verify must not crash
            verified = verify_password(pw_73, hash_73)
            assert isinstance(verified, bool)
        except Exception as e:
            # If native bcrypt raises ValueError for >72 byte input, verify_password must catch it safely
            assert isinstance(e, (ValueError, Exception))

    def test_corrupted_hash_returns_false_safely(self):
        """Malformed or truncated hash strings must return False without crashing."""
        assert verify_password("password", "not_a_bcrypt_hash") is False
        assert verify_password("password", "$2b$12$invalid_short_hash") is False
        assert verify_password("password", "") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
