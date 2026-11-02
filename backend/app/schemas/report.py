"""Pydantic schemas for waste reports, pagination, and status transitions."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class CategoryBrief(BaseModel):
    """Brief category representation embedded in report payloads."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    badge_color: str
    slug: Optional[str] = None


class ReporterBrief(BaseModel):
    """Brief reporter information embedded in report listings and details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: Optional[str] = None


class ReportLogResponse(BaseModel):
    """Audit log entry representing a historical status transition."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    previous_status: Optional[str] = None
    new_status: str
    actor_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None
    created_at: datetime


class ReportCreate(BaseModel):
    """Schema for validating programmatic report submissions."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address_note: Optional[str] = Field(None, max_length=255)


class StatusUpdateRequest(BaseModel):
    """Request payload for admin status transitions."""

    status: str
    admin_notes: Optional[str] = None


class ReportListItem(BaseModel):
    """Item representation in paginated report lists."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    image_url: str
    latitude: float
    longitude: float
    status: str
    created_at: datetime
    category: CategoryBrief
    reporter: ReporterBrief


class ReportDetailData(BaseModel):
    """Detailed waste report object including coordinates, reporter, and audit logs."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str] = None
    image_url: str
    detected_category: Optional[str] = None
    ai_confidence: Optional[float] = 0.0
    latitude: float
    longitude: float
    address_note: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category: CategoryBrief
    reporter: ReporterBrief
    logs: List[ReportLogResponse] = []


class PaginationMeta(BaseModel):
    """Pagination metadata container."""

    total_items: int
    current_page: int
    total_pages: int
    limit: int


class ReportListResponse(BaseModel):
    """Envelope response for GET /reports."""

    status: str = "success"
    meta: PaginationMeta
    data: List[ReportListItem]


class ReportCreateResponse(BaseModel):
    """Envelope response for POST /reports."""

    status: str = "success"
    message: str = "Report submitted successfully"
    data: Dict[str, Any]


class ReportStatusUpdateResponse(BaseModel):
    """Envelope response for PATCH /reports/{id}/status."""

    status: str = "success"
    message: str
    data: Dict[str, Any]


class ReportDetailResponse(BaseModel):
    """Envelope response for GET /reports/{id}."""

    status: str = "success"
    data: ReportDetailData
