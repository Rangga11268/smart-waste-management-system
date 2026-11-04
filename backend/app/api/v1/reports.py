"""Waste Reports management router for submission, listing, detail, and triage."""

from datetime import datetime, timezone
import io
from pathlib import Path
import sys
import json
import urllib.request
from typing import Any, Dict, List, Optional, Set
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError
import sqlalchemy as sa
from sqlalchemy.orm import Session

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml_pipeline.predict import get_default_predictor


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """Reverse geocode latitude and longitude to human-readable address via OSM Nominatim."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "SWMS-Backend/1.0 (bilcode-assessment)"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("display_name")
    except Exception:
        return None

try:
    from app.api.deps import get_current_admin, get_current_user, get_db
    from app.core.config import settings
    from app.models.category import Category
    from app.models.log import ReportLog
    from app.models.report import WasteReport
    from app.models.user import User
    from app.schemas.report import (
        CategoryBrief,
        PaginationMeta,
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
except ImportError:
    from backend.app.api.deps import get_current_admin, get_current_user, get_db
    from backend.app.core.config import settings
    from backend.app.models.category import Category
    from backend.app.models.log import ReportLog
    from backend.app.models.report import WasteReport
    from backend.app.models.user import User
    from backend.app.schemas.report import (
        CategoryBrief,
        PaginationMeta,
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

router = APIRouter()

ALLOWED_EXTENSIONS: Set[str] = {".bmp", ".jpeg", ".jpg", ".png", ".webp"}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReportCreateResponse, summary="Submit waste report")
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportCreateResponse, include_in_schema=False)
async def submit_report(
    file: UploadFile = File(..., description="Evidence photo"),
    title: str = Form(..., description="Report title"),
    description: Optional[str] = Form(None, description="Detailed description"),
    category_id: int = Form(..., description="Master category ID"),
    latitude: float = Form(..., description="GPS Latitude (-90 to 90)"),
    longitude: float = Form(..., description="GPS Longitude (-180 to 180)"),
    address_note: Optional[str] = Form(None, description="Address or landmark note"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    """Submit a new citizen waste report with photo, GPS, and automated AI classification."""
    # 1. Coordinate boundary validation
    if latitude < -90.0 or latitude > 90.0:
        raise HTTPException(
            status_code=422,
            detail="Latitude must be between -90 and 90 degrees",
        )
    if longitude < -180.0 or longitude > 180.0:
        raise HTTPException(
            status_code=422,
            detail="Longitude must be between -180 and 180 degrees",
        )

    # 2. Category lookup and validation
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )

    # 3. Image file validation
    filename = file.filename or "evidence.jpg"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image extension. Allowed: ['.bmp', '.jpeg', '.jpg', '.png', '.webp']",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid image file",
        )

    try:
        img_verify = Image.open(io.BytesIO(content))
        img_verify.verify()

        image = Image.open(io.BytesIO(content))
        if image.mode != "RGB":
            image = image.convert("RGB")
    except (UnidentifiedImageError, OSError, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid image file",
        )

    # 4. Save file to disk
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    reports_dir = Path(settings.UPLOAD_DIR)
    reports_dir.mkdir(parents=True, exist_ok=True)
    file_path = reports_dir / unique_filename
    with open(file_path, "wb") as f:
        f.write(content)

    image_url = f"/uploads/reports/{unique_filename}"

    # 5. ML inference via MobileNetV2 predictor
    predictor = get_default_predictor()
    try:
        pred_res = await run_in_threadpool(predictor.predict_image, image)
        detected_category = pred_res.get("category")
        ai_confidence = float(pred_res.get("confidence", 0.0))
    except Exception:
        detected_category = category.name
        ai_confidence = 0.0

    # 6. Auto-resolve address note via reverse geocoding if not provided
    resolved_address = address_note
    if not resolved_address or not resolved_address.strip():
        resolved_address = reverse_geocode(latitude, longitude)

    now = datetime.now(timezone.utc)

    # 7. Insert WasteReport and initial audit log
    report = WasteReport(
        id=uuid.uuid4(),
        user_id=current_user.id,
        category_id=category_id,
        title=title,
        description=description,
        image_url=image_url,
        detected_category=detected_category,
        ai_confidence=ai_confidence,
        latitude=latitude,
        longitude=longitude,
        address_note=resolved_address,
        status="Pending",
        created_at=now,
        updated_at=now,
    )
    db.add(report)
    db.flush()

    initial_log = ReportLog(
        id=uuid.uuid4(),
        report_id=report.id,
        actor_id=current_user.id,
        previous_status=None,
        new_status="Pending",
        remarks="Initial report submission",
        created_at=now,
    )
    db.add(initial_log)
    db.commit()
    db.refresh(report)

    created_iso = report.created_at.isoformat() if report.created_at else now.isoformat()
    if created_iso and not created_iso.endswith("Z") and "+" not in created_iso:
        created_iso += "Z"

    return ReportCreateResponse(
        status="success",
        message="Report submitted successfully",
        data={
            "id": str(report.id),
            "title": report.title,
            "image_url": report.image_url,
            "detected_category": report.detected_category,
            "ai_confidence": report.ai_confidence,
            "status": report.status,
            "created_at": created_iso,
        },
    )


@router.get("", response_model=ReportListResponse, summary="List waste reports")
@router.get("/", response_model=ReportListResponse, include_in_schema=False)
def list_reports(
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search keyword across title, description, address note"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportListResponse:
    """Retrieve paginated and filterable list of waste reports."""
    query = db.query(WasteReport)

    if status:
        query = query.filter(WasteReport.status == status)

    if category_id:
        query = query.filter(WasteReport.category_id == category_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            sa.or_(
                WasteReport.title.ilike(term),
                WasteReport.description.ilike(term),
                WasteReport.address_note.ilike(term),
            )
        )

    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    reports = (
        query.order_by(WasteReport.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items = []
    for r in reports:
        cat_brief = (
            CategoryBrief(
                id=r.category.id,
                name=r.category.name,
                badge_color=r.category.badge_color,
                slug=r.category.slug,
            )
            if r.category
            else CategoryBrief(id=0, name="Unknown", badge_color="#999999")
        )
        rep_brief = (
            ReporterBrief(
                id=r.reporter.id,
                full_name=r.reporter.full_name,
                email=r.reporter.email,
            )
            if r.reporter
            else ReporterBrief(id=r.user_id, full_name="Unknown")
        )

        items.append(
            ReportListItem(
                id=r.id,
                title=r.title,
                image_url=r.image_url,
                latitude=r.latitude,
                longitude=r.longitude,
                address_note=r.address_note,
                detected_category=r.detected_category,
                ai_confidence=r.ai_confidence,
                status=r.status,
                created_at=r.created_at,
                category=cat_brief,
                reporter=rep_brief,
            )
        )

    return ReportListResponse(
        status="success",
        meta=PaginationMeta(
            total_items=total_items,
            current_page=page,
            total_pages=total_pages,
            limit=limit,
        ),
        data=items,
    )


@router.get("/{id}", response_model=ReportDetailResponse, summary="Get waste report details")
def get_report_detail(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportDetailResponse:
    """Retrieve full details of a single waste report by UUID including audit logs."""
    try:
        report_uuid = uuid.UUID(str(id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    report = db.query(WasteReport).filter(WasteReport.id == report_uuid).first()
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    # Fetch logs ordered chronologically
    logs = (
        db.query(ReportLog)
        .filter(ReportLog.report_id == report_uuid)
        .order_by(ReportLog.created_at.asc())
        .all()
    )

    log_items = [
        ReportLogResponse(
            id=l.id,
            previous_status=l.previous_status,
            new_status=l.new_status,
            actor_id=l.actor_id,
            remarks=l.remarks,
            created_at=l.created_at,
        )
        for l in logs
    ]

    cat_brief = (
        CategoryBrief(
            id=report.category.id,
            name=report.category.name,
            badge_color=report.category.badge_color,
            slug=report.category.slug,
        )
        if report.category
        else CategoryBrief(id=0, name="Unknown", badge_color="#999999")
    )

    rep_brief = (
        ReporterBrief(
            id=report.reporter.id,
            full_name=report.reporter.full_name,
            email=report.reporter.email,
        )
        if report.reporter
        else ReporterBrief(id=report.user_id, full_name="Unknown")
    )

    detail_data = ReportDetailData(
        id=report.id,
        title=report.title,
        description=report.description,
        image_url=report.image_url,
        detected_category=report.detected_category,
        ai_confidence=report.ai_confidence,
        latitude=report.latitude,
        longitude=report.longitude,
        address_note=report.address_note,
        status=report.status,
        admin_notes=report.admin_notes,
        resolved_at=report.resolved_at,
        created_at=report.created_at,
        updated_at=report.updated_at,
        category=cat_brief,
        reporter=rep_brief,
        logs=log_items,
    )

    return ReportDetailResponse(status="success", data=detail_data)


@router.patch("/{id}/status", response_model=ReportStatusUpdateResponse, summary="Update report status (Admin only)")
def update_report_status(
    id: str,
    payload: StatusUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ReportStatusUpdateResponse:
    """Transition report status according to SWMS state machine rules (Admin only)."""
    try:
        report_uuid = uuid.UUID(str(id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    report = db.query(WasteReport).filter(WasteReport.id == report_uuid).first()
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    current_status = report.status
    new_status = payload.status

    # Terminal state check
    if current_status in ("Completed", "Rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is already in terminal state '{current_status}'",
        )

    # Valid transitions:
    # Pending -> In Progress, Rejected
    # In Progress -> Completed, Rejected
    allowed_transitions = {
        "Pending": {"In Progress", "Rejected"},
        "In Progress": {"Completed", "Rejected"},
    }

    if new_status not in allowed_transitions.get(current_status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}",
        )

    # Completed status sets resolved_at timestamp
    now = datetime.now(timezone.utc)
    if new_status == "Completed":
        report.resolved_at = now

    report.status = new_status
    report.admin_notes = payload.admin_notes
    report.updated_at = now

    # Record audit log entry
    log = ReportLog(
        id=uuid.uuid4(),
        report_id=report.id,
        actor_id=current_admin.id,
        previous_status=current_status,
        new_status=new_status,
        remarks=payload.admin_notes,
        created_at=now,
    )
    db.add(log)
    db.commit()
    db.refresh(report)

    return ReportStatusUpdateResponse(
        status="success",
        message=f"Report status updated to {new_status}",
        data={
            "id": str(report.id),
            "status": report.status,
            "admin_notes": report.admin_notes,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None,
        },
    )
