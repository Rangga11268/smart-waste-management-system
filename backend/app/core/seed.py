"""Database seeding logic for master categories and initial test users."""

import logging
from typing import Any, Dict, List
import bcrypt
from sqlalchemy.orm import Session

try:
    from app.models.category import Category
    from app.models.user import User
except ImportError:
    from backend.app.models.category import Category
    from backend.app.models.user import User

logger = logging.getLogger("swms.seed")

INITIAL_CATEGORIES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "slug": "organic",
        "name": "Organic Waste",
        "description": "Sisa makanan, dedaunan, sayuran, dan bahan mudah terurai",
        "badge_color": "#16a34a",
    },
    {
        "id": 2,
        "slug": "plastic",
        "name": "Plastic Waste",
        "description": "Botol plastik, kantong kresek, kemasan sachet, sedotan",
        "badge_color": "#0284c7",
    },
    {
        "id": 3,
        "slug": "paper",
        "name": "Paper Waste",
        "description": "Kertas karton, kardus, koran bekas, dokumen kertas",
        "badge_color": "#d97706",
    },
]

DEFAULT_USERS: List[Dict[str, Any]] = [
    {
        "email": "admin@bilcode.id",
        "password": "Admin123!",
        "role": "admin",
        "full_name": "Super Admin",
        "phone_number": "081234567890",
    },
    {
        "email": "user@bilcode.id",
        "password": "User123!",
        "role": "user",
        "full_name": "Warga Pelapor",
        "phone_number": "08123456789",
    },
]


def hash_password(password: str) -> str:
    """Hash password using native bcrypt (Python 3.12 compatible)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def seed_database(db: Session) -> Dict[str, int]:
    """Seed master categories and default test users into the database idempotently."""
    categories_seeded = 0
    users_seeded = 0

    # Seed categories
    for cat_data in INITIAL_CATEGORIES:
        existing = db.query(Category).filter_by(slug=cat_data["slug"]).first()
        if not existing:
            category = Category(
                id=cat_data["id"],
                slug=cat_data["slug"],
                name=cat_data["name"],
                description=cat_data["description"],
                badge_color=cat_data["badge_color"],
            )
            db.add(category)
            categories_seeded += 1
            logger.info("Seeded category: %s", cat_data["slug"])

    # Seed users
    for user_data in DEFAULT_USERS:
        existing = db.query(User).filter_by(email=user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                phone_number=user_data.get("phone_number"),
                is_active=True,
            )
            db.add(user)
            users_seeded += 1
            logger.info("Seeded user: %s (role: %s)", user_data["email"], user_data["role"])

    db.commit()
    logger.info(
        "Database seeding completed. Added %d categories, %d users.",
        categories_seeded,
        users_seeded,
    )
    return {"categories": categories_seeded, "users": users_seeded}
