import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.core.security import hash_secret_token, sanitize_csv_field
from app.db.session import get_db
from app.models.audit import Audit, AuditAnswer
from app.schemas.quality import DatasetQualityResponse
from app.services.quality import compute_dataset_quality_profile

router = APIRouter(tags=["Dataset Quality Analytics"])


@router.get("/audits/{audit_id}/quality", response_model=DatasetQualityResponse)
def get_audit_dataset_quality(
    audit_id: str,
    db: Session = Depends(get_db),
):
    """Computes and returns descriptive dataset hygiene and quality analytics for an audit.

    Philosophical Invariant:
    Quality indicators (missing timestamps, short answers, worker concentration)
    are descriptive metrics for dataset stewardship. They never constitute evidence
    of AI generation or worker misconduct.
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        # Check if caller provided secret token
        token_hash = hash_secret_token(audit_id)
        audit = db.query(Audit).filter(Audit.token_hash == token_hash).first()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit workspace not found or expired under 7-day retention policy.",
        )

    answers = db.query(AuditAnswer).filter(AuditAnswer.audit_id == audit.id).all()
    return compute_dataset_quality_profile(audit, answers)


@router.get("/audits/{audit_id}/quality/export")
def export_audit_dataset_quality(
    audit_id: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    """Exports dataset quality analytics in CSV or JSON format with formula-injection protection."""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        token_hash = hash_secret_token(audit_id)
        audit = db.query(Audit).filter(Audit.token_hash == token_hash).first()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit workspace not found or expired under 7-day retention policy.",
        )

    answers = db.query(AuditAnswer).filter(AuditAnswer.audit_id == audit.id).all()
    profile = compute_dataset_quality_profile(audit, answers)

    if format == "json":
        return JSONResponse(
            content=profile.model_dump(),
            headers={
                "Content-Disposition": f'attachment; filename="canary_quality_{audit.id[:8]}.json"'
            },
        )

    # Format CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Disclaimer header
    writer.writerow(["# CANARY SRS — DATASET QUALITY & HYGIENE REPORT"])
    writer.writerow(
        ["# NOTICE: Descriptive hygiene metrics only. Does not prove AI use, fraud, or cheating."]
    )
    writer.writerow([])

    # Overview Section
    writer.writerow(["SECTION", "DATASET OVERVIEW"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Audit ID", sanitize_csv_field(profile.audit_id)])
    writer.writerow(["Dataset Name", sanitize_csv_field(profile.dataset_name)])
    writer.writerow(["Total Records", profile.total_records])
    writer.writerow(["Unique Workers", profile.unique_workers])
    writer.writerow(["Unique Tasks", profile.unique_tasks])
    writer.writerow(["Completeness Score (%)", profile.completeness_score])
    writer.writerow(["Empty Answers Count", profile.empty_answers_count])
    writer.writerow(["Missing Worker IDs", profile.missing_worker_ids_count])
    writer.writerow(["Missing Timestamps", profile.missing_timestamps_count])
    writer.writerow(["Duplicate Task Submissions", profile.duplicate_task_submissions_count])
    writer.writerow(["Duplicate Content Submissions", profile.duplicate_submissions_count])
    writer.writerow([])

    # Length Stats
    writer.writerow(["SECTION", "ANSWER LENGTH STATISTICS"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Min Characters", profile.length_stats.min_chars])
    writer.writerow(["Max Characters", profile.length_stats.max_chars])
    writer.writerow(["Average Characters", profile.length_stats.avg_chars])
    writer.writerow(["Median Characters", profile.length_stats.median_chars])
    writer.writerow(["Min Words", profile.length_stats.min_words])
    writer.writerow(["Max Words", profile.length_stats.max_words])
    writer.writerow(["Average Words", profile.length_stats.avg_words])
    writer.writerow(["Median Words", profile.length_stats.median_words])
    writer.writerow(["Short Answers (<20 chars)", profile.length_stats.short_answers_count])
    writer.writerow(["Long Answers (>1000 chars)", profile.length_stats.long_answers_count])
    writer.writerow([])

    # Length Distribution
    writer.writerow(["SECTION", "CHARACTER LENGTH DISTRIBUTION"])
    writer.writerow(["Bucket", "Count", "Percentage"])
    for b in profile.length_distribution:
        writer.writerow([sanitize_csv_field(b.bucket), b.count, f"{b.percentage}%"])
    writer.writerow([])

    # Worker Participation
    writer.writerow(["SECTION", "WORKER PARTICIPATION DISTRIBUTION"])
    writer.writerow(["Bucket", "Count", "Percentage"])
    for wb in profile.worker_participation.distribution_buckets:
        writer.writerow([sanitize_csv_field(wb.bucket), wb.count, f"{wb.percentage}%"])
    writer.writerow([])

    # Top Contributors
    writer.writerow(["SECTION", "TOP WORKER CONTRIBUTORS"])
    writer.writerow(["Worker ID", "Answer Count", "Percentage of Dataset"])
    for tc in profile.worker_participation.top_contributors:
        writer.writerow(
            [sanitize_csv_field(tc.worker_id), tc.answer_count, f"{tc.percentage_of_total}%"]
        )
    writer.writerow([])

    # Task Coverage
    writer.writerow(["SECTION", "TASK COVERAGE DISTRIBUTION"])
    writer.writerow(["Bucket", "Count", "Percentage"])
    for tb in profile.task_coverage.coverage_buckets:
        writer.writerow([sanitize_csv_field(tb.bucket), tb.count, f"{tb.percentage}%"])
    writer.writerow([])

    # Quality Warnings
    writer.writerow(["SECTION", "DATA QUALITY WARNINGS"])
    writer.writerow(["Code", "Severity", "Title", "Message", "Affected Records"])
    if profile.warnings:
        for w in profile.warnings:
            writer.writerow(
                [
                    sanitize_csv_field(w.code),
                    sanitize_csv_field(w.severity),
                    sanitize_csv_field(w.title),
                    sanitize_csv_field(w.message),
                    w.affected_records,
                ]
            )
    else:
        writer.writerow(["NONE", "INFO", "No Quality Warnings", "Clean dataset hygiene", 0])

    csv_data = output.getvalue()
    filename = f"canary_quality_{audit.id[:8]}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
