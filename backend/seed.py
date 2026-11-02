"""Standalone CLI script to initialize database tables and seed initial data."""

import logging
import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Also add project root if applicable
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.database import Base, SessionLocal, engine
from app.core.seed import seed_database
import app.models  # Ensure all models are registered with Base.metadata

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("swms.cli.seed")


def run_seed():
    """Execute table creation and seeding."""
    logger.info("Initializing database schema on engine: %s", engine.url)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    db = SessionLocal()
    try:
        results = seed_database(db)
        print("\n=======================================================")
        print(" [SWMS] Database Seeding Summary")
        print("=======================================================")
        print(f" Categories Added: {results['categories']}")
        print(f" Users Added:      {results['users']}")
        print(" Status:           SUCCESS (Idempotent)")
        print("=======================================================\n")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
