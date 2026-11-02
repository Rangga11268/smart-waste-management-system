"""Categories master data router."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from app.api.deps import get_db
    from app.models.category import Category
    from app.schemas.category import CategoriesResponse, CategoryItem
except ImportError:
    from backend.app.api.deps import get_db
    from backend.app.models.category import Category
    from backend.app.schemas.category import CategoriesResponse, CategoryItem

router = APIRouter()


@router.get("", response_model=CategoriesResponse, summary="List all waste categories")
@router.get("/", response_model=CategoriesResponse, include_in_schema=False)
def list_categories(
    db: Session = Depends(get_db),
) -> CategoriesResponse:
    """Retrieve all master waste categories ordered by ID."""
    categories = db.query(Category).order_by(Category.id.asc()).all()
    items = [CategoryItem.model_validate(c) for c in categories]
    return CategoriesResponse(status="success", data=items)
