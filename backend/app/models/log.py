"""ReportLog model definition representing status transition audit logs."""

import uuid
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

try:
    from app.models.base import Base
except ImportError:
    from backend.app.models.base import Base


class ReportLog(Base):
    """Audit log tracking lifecycle status transitions of waste reports."""

    __tablename__ = "report_logs"

    id = sa.Column(sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = sa.Column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("waste_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = sa.Column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    previous_status = sa.Column(sa.String(30), nullable=True)
    new_status = sa.Column(sa.String(30), nullable=False)
    remarks = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    report = relationship("WasteReport", back_populates="logs")
    actor = relationship("User", back_populates="report_logs")
