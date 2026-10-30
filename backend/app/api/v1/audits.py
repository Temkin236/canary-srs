import datetime
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_secret_token, hash_secret_token, sanitize_filename
from app.db.session import get_db
from app.jobs.queue import enqueue_audit_job
from app.models.audit import Audit, AuditAnswer, CheckResult, Finding, JobState, Marker
from app.reporting.csv_export import generate_csv_report
from app.reporting.html_export import generate_html_report
from app.reporting.json_export import generate_json_report
from app.schemas.audit import AuditCreateResponse, AuditStatusResponse
from app.schemas.dataset import DatasetValidationResponse
from app.services.audit import delete_audit_permanently
from app.services.dataset import validate_and_parse_dataset
from app.services.storage import save_uploaded_file

router = APIRouter(prefix="/audits", tags=["Audits"])


@router.post("/validate", response_model=DatasetValidationResponse)
async def validate_dataset_endpoint(
    file: UploadFile = File(...),
    column_mapping: Optional[str] = Form(None),
):
    """
    Validates uploaded CSV or JSONL dataset against requirements FR-1 through FR-8.
    Does not persist the audit or answers to the database.
    """
    custom_map = None
    if column_mapping:
        try:
            custom_map = json.loads(column_mapping)
        except Exception:
            pass

    safe_name = sanitize_filename(file.filename or "dataset.csv")
    content = await file.read()

    validation_resp, _ = validate_and_parse_dataset(
        content_bytes=content,
        filename=safe_name,
        custom_mapping=custom_map,
    )

    return validation_resp


@router.post("", response_model=AuditCreateResponse)
async def create_audit_endpoint(
    file: UploadFile = File(...),
    column_mapping: Optional[str] = Form(None),
    consent_external_ai: bool = Form(False),
    manifest_file: Optional[UploadFile] = File(None),
    manifest_json: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Initiates an asynchronous durable audit job.
    Requirements FR-31 through FR-36:
    - Parses dataset and saves to path-traversal proof storage.
    - Generates a 256-bit cryptographically random secret token.
    - Stores only the SHA-256 hash in the database.
    - Sets 7-day retention expiry.
    - Enqueues background worker execution.
    - Returns one-time raw secret token for client results retrieval.
    """
    safe_name = sanitize_filename(file.filename or "dataset.csv")
    content = await file.read()

    custom_map = None
    if column_mapping:
        try:
            custom_map = json.loads(column_mapping)
        except Exception:
            pass

    validation_resp, parsed_rows = validate_and_parse_dataset(
        content_bytes=content,
        filename=safe_name,
        custom_mapping=custom_map,
    )

    if not validation_resp.valid or not parsed_rows:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Dataset validation failed. Please correct errors before submitting.",
                "errors": [err.model_dump() for err in validation_resp.errors],
            },
        )

    # Save raw uploaded file safely
    save_uploaded_file(content, safe_name)

    # Cryptographic secret token generation (FR-35, FR-36)
    raw_token, token_hash = generate_secret_token()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now_utc + datetime.timedelta(days=settings.DEFAULT_RETENTION_DAYS)

    audit_id = str(uuid.uuid4())
    audit = Audit(
        id=audit_id,
        token_hash=token_hash,
        status="queued",
        dataset_name=safe_name,
        answers_count=len(parsed_rows),
        workers_count=len({r["worker_id"] for r in parsed_rows}),
        consent_external_ai=consent_external_ai,
        expires_at=expires_at,
        created_at=now_utc,
    )
    db.add(audit)

    # Populate answers
    for r in parsed_rows:
        ans_record = AuditAnswer(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            task_id=str(r["task_id"]),
            worker_id=str(r["worker_id"]),
            prompt=str(r.get("prompt", "")),
            answer=str(r["answer"]),
            submitted_at=r.get("submitted_at"),
            seconds_spent=r.get("seconds_spent"),
        )
        db.add(ans_record)

    # Handle optional marker manifest
    manifest_data = None
    if manifest_file:
        try:
            manifest_bytes = await manifest_file.read()
            manifest_data = json.loads(manifest_bytes.decode("utf-8"))
        except Exception:
            pass
    elif manifest_json:
        try:
            manifest_data = json.loads(manifest_json)
        except Exception:
            pass

    if manifest_data and isinstance(manifest_data, dict):
        tasks = manifest_data.get("tasks", [])
        for t in tasks:
            if "task_id" in t and "marker_token" in t:
                marker_rec = Marker(
                    id=str(uuid.uuid4()),
                    audit_id=audit_id,
                    task_id=str(t["task_id"]),
                    marker_token=str(t["marker_token"]),
                    hiding_method=str(t.get("hiding_method", "zero_width")),
                    prompt_template=t.get("prompt_template"),
                    created_at=now_utc,
                )
                db.add(marker_rec)

    # Initial durable job state (FR-31)
    job_state = JobState(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        stage="queued",
        progress_percentage=0,
        started_at=now_utc,
        last_heartbeat=now_utc,
    )
    db.add(job_state)
    db.commit()

    # Enqueue execution job (FR-32)
    enqueue_audit_job(audit_id)

    return AuditCreateResponse(
        audit_id=audit_id,
        secret_token=raw_token,
        status="queued",
        expires_at=expires_at,
        answers_count=len(parsed_rows),
    )


@router.get("/{secret_token}/status", response_model=AuditStatusResponse)
def get_audit_status_endpoint(
    secret_token: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves execution status for an active or completed audit using the secret token.
    Never exposes raw tokens or private data without authentication.
    """
    token_hash = hash_secret_token(secret_token)
    audit = db.query(Audit).filter(Audit.token_hash == token_hash).first()

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit not found or secret link is invalid.",
        )

    # Expiry verification
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Handle both naive and timezone-aware datetime comparisons
    audit_exp = audit.expires_at
    if audit_exp.tzinfo is None:
        audit_exp = audit_exp.replace(tzinfo=datetime.timezone.utc)

    if now_utc > audit_exp:
        raise HTTPException(
            status_code=410,
            detail=(
                "This audit has expired and its data has been purged "
                "under the 7-day retention policy."
            ),
        )

    job_state = db.query(JobState).filter(JobState.audit_id == audit.id).first()

    return AuditStatusResponse(
        audit_id=audit.id,
        status=audit.status,
        stage=job_state.stage if job_state else audit.status,
        progress_percentage=job_state.progress_percentage if job_state else 100,
        current_check=job_state.current_check if job_state else None,
        answers_count=audit.answers_count,
        workers_count=audit.workers_count,
        flagged_workers_count=audit.flagged_workers_count,
        expires_at=audit.expires_at,
        summary_metrics=audit.summary_metrics or {},
    )


@router.get("/{secret_token}/report")
def get_audit_report_endpoint(
    secret_token: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves full audit report including executive summary, check status, and findings (FR-37).
    """
    audit = _get_authenticated_audit(secret_token, db)
    findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
    check_results = db.query(CheckResult).filter(CheckResult.audit_id == audit.id).all()

    return generate_json_report(audit, findings, check_results)


@router.get("/{secret_token}/export.html", response_class=HTMLResponse)
def export_html_report_endpoint(
    secret_token: str,
    db: Session = Depends(get_db),
):
    """
    Exports a 100% self-contained offline HTML audit report with inline CSS (FR-38).
    """
    audit = _get_authenticated_audit(secret_token, db)
    findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
    check_results = db.query(CheckResult).filter(CheckResult.audit_id == audit.id).all()

    html_content = generate_html_report(audit, findings, check_results)
    return HTMLResponse(
        content=html_content,
        headers={"Content-Disposition": f"attachment; filename=canary_report_{audit.id[:8]}.html"},
    )


@router.get("/{secret_token}/export.csv")
def export_csv_report_endpoint(
    secret_token: str,
    db: Session = Depends(get_db),
):
    """
    Exports formula-injection protected CSV of audit findings (FR-39).
    """
    audit = _get_authenticated_audit(secret_token, db)
    findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()

    csv_data = generate_csv_report(audit, findings)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=canary_findings_{audit.id[:8]}.csv"},
    )


@router.get("/{secret_token}/export.json")
def export_json_report_endpoint(
    secret_token: str,
    db: Session = Depends(get_db),
):
    """
    Exports machine-readable JSON of audit metadata and findings (FR-40).
    """
    audit = _get_authenticated_audit(secret_token, db)
    findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
    check_results = db.query(CheckResult).filter(CheckResult.audit_id == audit.id).all()

    report_dict = generate_json_report(audit, findings, check_results)
    return Response(
        content=json.dumps(report_dict, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=canary_audit_{audit.id[:8]}.json"},
    )


@router.delete("/{secret_token}")
def delete_audit_endpoint(
    secret_token: str,
    db: Session = Depends(get_db),
):
    """
    'Delete Now' immediate purge action cascading complete deletion of audit data (FR-41).
    """
    audit = _get_authenticated_audit(secret_token, db)
    success = delete_audit_permanently(audit, db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to purge audit data.")

    return {"message": "Audit and all associated data permanently deleted."}


def _get_authenticated_audit(secret_token: str, db: Session) -> Audit:
    token_hash = hash_secret_token(secret_token)
    audit = db.query(Audit).filter(Audit.token_hash == token_hash).first()

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit not found or secret link is invalid.",
        )

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    audit_exp = audit.expires_at
    if audit_exp.tzinfo is None:
        audit_exp = audit_exp.replace(tzinfo=datetime.timezone.utc)

    if now_utc > audit_exp:
        raise HTTPException(
            status_code=410,
            detail=(
                "This audit has expired and its data has been purged "
                "under the 7-day retention policy."
            ),
        )

    return audit
