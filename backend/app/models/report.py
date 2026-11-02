"""WasteReport model definition representing citizen waste reports."""

import uuid
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

try:
    from app.models.base import Base
except ImportError:
    from backend.app.models.base import Base


class WasteReport(Base):
    """Waste report submitted by citizens with AI detection and geotagging."""

    __tablename__ = "waste_reports"

    id = sa.Column(sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    image_url = sa.Column(sa.String(500), nullable=False)
    detected_category = sa.Column(sa.String(100), nullable=True)
    ai_confidence = sa.Column(sa.Float, default=0.0, nullable=False)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)
    address_note = sa.Column(sa.String(255), nullable=True)
    status = sa.Column(
        sa.String(30),
        default="Pending",
        nullable=False,
        index=True,
    )
    admin_notes = sa.Column(sa.Text, nullable=True)
    resolved_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        sa.CheckConstraint(
            "status IN ('Pending', 'In Progress', 'Completed', 'Rejected')",
            name="check_report_status",
        ),
        sa.Index("idx_reports_created_at_desc", created_at.desc()),
    )

    # Relationships
    reporter = relationship("User", back_populates="waste_reports")
    category = relationship("Category", back_populates="waste_reports")
    logs = relationship(
        "ReportLog",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="desc(ReportLog.created_at)",
    )
