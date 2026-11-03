"""User management endpoints for administrative oversight."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

try:
    from app.api.deps import get_current_admin, get_db
    from app.models.user import User
    from app.models.report import WasteReport
    from app.schemas.user import UserDetailItem, UserListResponse
except ImportError:
    from backend.app.api.deps import get_current_admin, get_db
    from backend.app.models.user import User
    from backend.app.models.report import WasteReport
    from backend.app.schemas.user import UserDetailItem, UserListResponse

router = APIRouter()


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all users with administrative filtering",
)
def list_users(
    search: Optional[str] = Query(None, description="Search by full name or email"),
    role: Optional[str] = Query(None, description="Filter by role: admin or user"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> UserListResponse:
    """Retrieve registered users list (Admin only)."""
    query = db.query(User)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (User.full_name.ilike(search_pattern)) | (User.email.ilike(search_pattern))
        )

    if role:
        query = query.filter(User.role == role.strip().lower())

    users = query.order_by(User.created_at.desc()).all()

    # Calculate report counts per user
    report_counts = dict(
        db.query(WasteReport.user_id, func.count(WasteReport.id))
        .group_by(WasteReport.user_id)
        .all()
    )

    result = []
    for u in users:
        result.append(
            UserDetailItem(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                phone_number=u.phone_number,
                is_active=u.is_active,
                total_reports=report_counts.get(u.id, 0),
                created_at=u.created_at,
            )
        )

    return UserListResponse(status="success", data=result)
