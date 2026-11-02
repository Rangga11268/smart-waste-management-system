"""SQLAlchemy ORM models package."""

try:
    from app.models.base import Base
    from app.models.user import User
    from app.models.category import Category
    from app.models.report import WasteReport
    from app.models.log import ReportLog
except ImportError:
    from backend.app.models.base import Base
    from backend.app.models.user import User
    from backend.app.models.category import Category
    from backend.app.models.report import WasteReport
    from backend.app.models.log import ReportLog

__all__ = [
    "Base",
    "User",
    "Category",
    "WasteReport",
    "ReportLog",
]
