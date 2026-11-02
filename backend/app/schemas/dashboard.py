"""Dashboard schemas for administrator statistics and metrics aggregation."""

from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class DashboardSummary(BaseModel):
    """Aggregated summary counters for waste reports and active users."""

    total_reports: int
    pending_count: int
    in_progress_count: int
    completed_count: int
    rejected_count: int
    completion_rate_percent: float
    active_users: Optional[int] = None


class CategoryDistribution(BaseModel):
    """Waste category breakdown count and relative percentage."""

    category: str
    count: int
    percentage: float


class RecentActivity(BaseModel):
    """Recent status modification audit activity item."""

    report_id: uuid.UUID
    action: str
    timestamp: datetime


class DashboardStatsData(BaseModel):
    """Inner container holding all dashboard metrics and distribution lists."""

    summary: DashboardSummary
    category_distribution: List[CategoryDistribution]
    recent_activities: List[RecentActivity]


class DashboardStatsResponse(BaseModel):
    """Envelope response for GET /dashboard/stats."""

    status: str = "success"
    data: DashboardStatsData
