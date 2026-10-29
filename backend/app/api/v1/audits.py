import datetime
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_secret_token, hash_secret_token, sanitize_filename
from app.db.session import get_db
from app.jobs.queue import enqueue_audit_job
from app.models.audit import Audit, AuditAnswer, JobState, Marker
from app.schemas.audit import AuditCreateResponse, AuditStatusResponse
from app.schemas.dataset import DatasetValidationResponse
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
