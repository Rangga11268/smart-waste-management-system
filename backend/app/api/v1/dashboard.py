"""Admin Dashboard statistics and metrics router."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from app.api.deps import get_current_admin, get_db
    from app.models.category import Category
    from app.models.log import ReportLog
    from app.models.report import WasteReport
    from app.models.user import User
    from app.schemas.dashboard import (
        CategoryDistribution,
        DashboardStatsData,
        DashboardStatsResponse,
        DashboardSummary,
        RecentActivity,
    )
except ImportError:
    from backend.app.api.deps import get_current_admin, get_db
    from backend.app.models.category import Category
    from backend.app.models.log import ReportLog
    from backend.app.models.report import WasteReport
    from backend.app.models.user import User
    from backend.app.schemas.dashboard import (
        CategoryDistribution,
        DashboardStatsData,
        DashboardStatsResponse,
        DashboardSummary,
        RecentActivity,
    )

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse, summary="Get dashboard statistics")
def get_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DashboardStatsResponse:
    """Calculate and return aggregate report metrics, category distributions, and recent audit activity."""
    # 1. Summary metrics
    total_reports = db.query(WasteReport).count()
    pending_count = db.query(WasteReport).filter(WasteReport.status == "Pending").count()
    in_progress_count = db.query(WasteReport).filter(WasteReport.status == "In Progress").count()
    completed_count = db.query(WasteReport).filter(WasteReport.status == "Completed").count()
    rejected_count = db.query(WasteReport).filter(WasteReport.status == "Rejected").count()

    completion_rate_percent = (
        round((completed_count / total_reports * 100.0), 2) if total_reports > 0 else 0.0
    )
    active_users = db.query(User).filter(User.is_active.is_(True)).count()

    summary = DashboardSummary(
        total_reports=total_reports,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        rejected_count=rejected_count,
        completion_rate_percent=completion_rate_percent,
        active_users=active_users,
    )

    # 2. Category distribution
    categories = db.query(Category).order_by(Category.id.asc()).all()
    category_distribution: List[CategoryDistribution] = []
    for cat in categories:
        cat_count = db.query(WasteReport).filter(WasteReport.category_id == cat.id).count()
        cat_pct = round((cat_count / total_reports * 100.0), 2) if total_reports > 0 else 0.0
        category_distribution.append(
            CategoryDistribution(
                category=cat.name,
                count=cat_count,
                percentage=cat_pct,
            )
        )

    # 3. Recent activities (audit trail)
    recent_logs = (
        db.query(ReportLog)
        .order_by(ReportLog.created_at.desc())
        .limit(10)
        .all()
    )

    recent_activities: List[RecentActivity] = []
    for l in recent_logs:
        action = (
            f"Status changed to {l.new_status}"
            if l.previous_status
            else f"Report created ({l.new_status})"
        )
        recent_activities.append(
            RecentActivity(
                report_id=l.report_id,
                action=action,
                timestamp=l.created_at,
            )
        )

    return DashboardStatsResponse(
        status="success",
        data=DashboardStatsData(
            summary=summary,
            category_distribution=category_distribution,
            recent_activities=recent_activities,
        ),
    )
