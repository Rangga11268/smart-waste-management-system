"""User model definition representing system users (citizens and admins)."""

import uuid
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

try:
    from app.models.base import Base
except ImportError:
    from backend.app.models.base import Base


class User(Base):
    """User account entity for authentication and report ownership."""

    __tablename__ = "users"

    id = sa.Column(sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    password_hash = sa.Column(sa.String(255), nullable=False)
    full_name = sa.Column(sa.String(150), nullable=False)
    role = sa.Column(sa.String(20), nullable=False, default="user", index=True)
    phone_number = sa.Column(sa.String(30), nullable=True)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        sa.CheckConstraint("role IN ('admin', 'user')", name="check_user_role"),
    )

    # Relationships
    waste_reports = relationship(
        "WasteReport",
        back_populates="reporter",
        cascade="all, delete-orphan",
    )
    report_logs = relationship(
        "ReportLog",
        back_populates="actor",
    )
