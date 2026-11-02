"""Category schemas for master waste category requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CategoryItem(BaseModel):
    """Schema for individual waste category item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: Optional[str] = None
    badge_color: str


class CategoriesResponse(BaseModel):
    """Response envelope for listing waste categories."""

    status: str = "success"
    data: List[CategoryItem]
