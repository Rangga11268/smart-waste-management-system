"""Category model definition representing waste classification categories."""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

try:
    from app.models.base import Base
except ImportError:
    from backend.app.models.base import Base


class Category(Base):
    """Waste classification category entity."""

    __tablename__ = "categories"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    slug = sa.Column(sa.String(50), unique=True, nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    badge_color = sa.Column(sa.String(20), default="#059669", nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    waste_reports = relationship(
        "WasteReport",
        back_populates="category",
    )
