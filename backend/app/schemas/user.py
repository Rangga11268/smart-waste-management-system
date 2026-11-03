"""Pydantic schemas for user management endpoints."""

from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class UserDetailItem(BaseModel):
    """Detailed user item for admin management."""

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    phone_number: Optional[str] = None
    is_active: bool = True
    total_reports: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Enveloped response for GET /api/v1/users."""

    status: str = "success"
    data: List[UserDetailItem]
