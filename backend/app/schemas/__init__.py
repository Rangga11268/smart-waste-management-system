"""Pydantic schemas for request and response validation."""

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponseData,
    UserResponse,
    UserSummary,
)
from app.schemas.category import CategoriesResponse, CategoryItem
from app.schemas.dashboard import (
    CategoryDistribution,
    DashboardStatsData,
    DashboardStatsResponse,
    DashboardSummary,
    RecentActivity,
)
from app.schemas.predict import PredictResponse, PredictResponseData
from app.schemas.report import (
    CategoryBrief,
    PaginationMeta,
    ReportCreate,
    ReportCreateResponse,
    ReportDetailData,
    ReportDetailResponse,
    ReportListItem,
    ReportListResponse,
    ReportLogResponse,
    ReportStatusUpdateResponse,
    ReporterBrief,
    StatusUpdateRequest,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserSummary",
    "TokenResponseData",
    "RegisterResponse",
    "LoginResponse",
    "UserResponse",
    "PredictResponse",
    "PredictResponseData",
    "CategoryItem",
    "CategoriesResponse",
    "CategoryBrief",
    "ReporterBrief",
    "ReportLogResponse",
    "ReportCreate",
    "StatusUpdateRequest",
    "ReportListItem",
    "ReportDetailData",
    "PaginationMeta",
    "ReportListResponse",
    "ReportCreateResponse",
    "ReportStatusUpdateResponse",
    "ReportDetailResponse",
    "DashboardSummary",
    "CategoryDistribution",
    "RecentActivity",
    "DashboardStatsData",
    "DashboardStatsResponse",
]
