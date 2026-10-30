import csv
import datetime
import io
import math
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import sanitize_csv_field
from app.db.session import get_db
from app.models.audit import Audit, Finding
from app.schemas.dashboard import (
    DashboardAuditItem,
    DashboardAuditsResponse,
    DashboardStatsResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Reviewer Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated reviewer analytics from persisted audit and finding records.
    All data is derived from actual database records (Invariant 8).
    """
    total_audits = db.query(func.count(Audit.id)).scalar() or 0
    completed_audits = (
        db.query(func.count(Audit.id)).filter(Audit.status == "completed").scalar() or 0
    )
    running_audits = (
        db.query(func.count(Audit.id)).filter(Audit.status.in_(["queued", "running"])).scalar() or 0
    )
    failed_audits = db.query(func.count(Audit.id)).filter(Audit.status == "failed").scalar() or 0

    total_answers = db.query(func.sum(Audit.answers_count)).scalar() or 0

    review_pending_statuses = ["pending_review", "under_review", "needs_investigation"]
    findings_requiring_review = (
        db.query(func.count(Finding.id))
        .filter(Finding.review_status.in_(review_pending_statuses))
        .scalar()
        or 0
    )
    reviewed_findings = (
        db.query(func.count(Finding.id))
        .filter(Finding.review_status.in_(["reviewed", "dismissed"]))
        .scalar()
        or 0
    )

    high_confidence = (
        db.query(func.count(Finding.id)).filter(Finding.evidence_confidence == "High").scalar() or 0
    )
    medium_confidence = (
        db.query(func.count(Finding.id)).filter(Finding.evidence_confidence == "Medium").scalar()
        or 0
    )
    low_confidence = (
        db.query(func.count(Finding.id)).filter(Finding.evidence_confidence == "Low").scalar() or 0
    )

    # Findings by category
    cat_counts = (
        db.query(Finding.check_identifier, func.count(Finding.id))
        .group_by(Finding.check_identifier)
        .all()
    )
    findings_by_category = {cat: count for cat, count in cat_counts}
    for default_cat in ["marker", "similarity", "duplicates", "speed"]:
        findings_by_category.setdefault(default_cat, 0)

    # Audits by status
    status_counts = db.query(Audit.status, func.count(Audit.id)).group_by(Audit.status).all()
    audits_by_status = {status: count for status, count in status_counts}
    for default_status in ["completed", "running", "queued", "failed"]:
        audits_by_status.setdefault(default_status, 0)

    # Dataset size distribution
    audits_all = db.query(Audit.answers_count).all()
    dataset_size_dist = {"<100": 0, "100-500": 0, "500-2k": 0, "2k-10k": 0}
    for (ans_count,) in audits_all:
        if ans_count < 100:
            dataset_size_dist["<100"] += 1
        elif ans_count <= 500:
            dataset_size_dist["100-500"] += 1
        elif ans_count <= 2000:
            dataset_size_dist["500-2k"] += 1
        else:
            dataset_size_dist["2k-10k"] += 1

    # Activity over time (grouped by created_at date)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    activity_map: Dict[str, Dict[str, int]] = {}
    for i in range(13, -1, -1):
        day = (now_utc - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        activity_map[day] = {"audits": 0, "findings": 0}

    # Aggregate audits over time
    audits_dates = (
        db.query(
            func.substr(func.datetime(Audit.created_at), 1, 10).label("day"),
            func.count(Audit.id),
        )
        .group_by("day")
        .all()
    )
    for day_str, count in audits_dates:
        if day_str in activity_map:
            activity_map[day_str]["audits"] = count

    findings_dates = (
        db.query(
            func.substr(func.datetime(Finding.created_at), 1, 10).label("day"),
            func.count(Finding.id),
        )
        .group_by("day")
        .all()
    )
    for day_str, count in findings_dates:
        if day_str in activity_map:
            activity_map[day_str]["findings"] = count

    activity_over_time = [
        {"date": day, "audits": data["audits"], "findings": data["findings"]}
        for day, data in activity_map.items()
    ]

    return DashboardStatsResponse(
        total_audits=total_audits,
        completed_audits=completed_audits,
        running_audits=running_audits,
        failed_audits=failed_audits,
        total_answers_analyzed=int(total_answers),
        findings_requiring_review=findings_requiring_review,
        reviewed_findings=reviewed_findings,
        high_confidence_findings=high_confidence,
        medium_confidence_findings=medium_confidence,
        low_confidence_findings=low_confidence,
        findings_by_category=findings_by_category,
        audits_by_status=audits_by_status,
        activity_over_time=activity_over_time,
        dataset_size_distribution=dataset_size_dist,
    )


@router.get("/audits", response_model=DashboardAuditsResponse)
def get_dashboard_audits(
    search: Optional[str] = Query(None, description="Search by dataset name or audit ID"),
    status: Optional[str] = Query(None, description="Filter by audit status"),
    start_date: Optional[str] = Query(None, description="Filter start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Filter end date YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort column (created_at, answers_count)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
):
    """
    Returns paginated, searchable, filterable list of audits for the reviewer dashboard.
    """
    query = db.query(Audit)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Audit.dataset_name.ilike(search_term)) | (Audit.id.ilike(search_term))
        )

    if status and status.lower() != "all":
        query = query.filter(Audit.status == status.lower())

    if start_date:
        try:
            start_dt = datetime.datetime.fromisoformat(start_date)
            query = query.filter(Audit.created_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.datetime.fromisoformat(end_date)
            query = query.filter(Audit.created_at <= end_dt)
        except ValueError:
            pass

    total = query.count()

    # Sorting
    sort_attr = getattr(Audit, sort_by, Audit.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_attr.asc())
    else:
        query = query.order_by(sort_attr.desc())

    offset = (page - 1) * page_size
    audits = query.offset(offset).limit(page_size).all()

    items: List[DashboardAuditItem] = []
    for aud in audits:
        findings_count = (
            db.query(func.count(Finding.id)).filter(Finding.audit_id == aud.id).scalar() or 0
        )
        duration = None
        if aud.completed_at and aud.created_at:
            duration = round((aud.completed_at - aud.created_at).total_seconds(), 2)

        items.append(
            DashboardAuditItem(
                id=aud.id,
                dataset_name=aud.dataset_name,
                status=aud.status,
                answers_count=aud.answers_count,
                workers_count=aud.workers_count,
                flagged_workers_count=aud.flagged_workers_count,
                findings_count=findings_count,
                created_at=aud.created_at,
                completed_at=aud.completed_at,
                duration_seconds=duration,
                expires_at=aud.expires_at,
                owner_id=aud.owner_id,
            )
        )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return DashboardAuditsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/export")
def export_dashboard_summary_csv(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Exports dashboard audits list as a formula-injection-protected CSV report (FR-39).
    """
    query = db.query(Audit)
    if search:
        query = query.filter(Audit.dataset_name.ilike(f"%{search.strip()}%"))
    if status and status.lower() != "all":
        query = query.filter(Audit.status == status.lower())

    audits = query.order_by(Audit.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    headers = [
        "Audit ID",
        "Dataset Name",
        "Status",
        "Answers Count",
        "Workers Count",
        "Flagged Workers",
        "Findings Count",
        "Created At",
        "Completed At",
        "Expires At",
    ]
    writer.writerow([sanitize_csv_field(h) for h in headers])

    for aud in audits:
        findings_count = (
            db.query(func.count(Finding.id)).filter(Finding.audit_id == aud.id).scalar() or 0
        )
        row = [
            sanitize_csv_field(aud.id),
            sanitize_csv_field(aud.dataset_name),
            sanitize_csv_field(aud.status),
            aud.answers_count,
            aud.workers_count,
            aud.flagged_workers_count,
            findings_count,
            sanitize_csv_field(aud.created_at.isoformat() if aud.created_at else ""),
            sanitize_csv_field(aud.completed_at.isoformat() if aud.completed_at else ""),
            sanitize_csv_field(aud.expires_at.isoformat() if aud.expires_at else ""),
        ]
        writer.writerow(row)

    csv_data = output.getvalue()
    filename = f"canary_dashboard_audits_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
