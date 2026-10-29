import datetime
import logging
import time
import uuid
from typing import Any, Dict, List

from app.checks.base import CheckFinding
from app.checks.duplicates import run_duplicate_check_for_task
from app.checks.marker import detect_marker_in_text
from app.checks.similarity import run_similarity_check_for_task
from app.checks.speed import run_speed_check
from app.db.session import SessionLocal
from app.models.audit import (
    Audit,
    AuditAnswer,
    CheckResult,
    Finding,
    JobState,
    Marker,
    ReferenceAnswer,
)
from app.services.ai_provider import get_ai_provider

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 1200  # 20 minutes (FR-33)


def execute_audit_job(audit_id: str) -> None:
    """
    Executes an audit job through all detection stages idempotently with durable
    DB state tracking and partial result preservation (FR-31 through FR-34).
    """
    db = SessionLocal()
    start_monotonic = time.monotonic()

    try:
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            logger.error("Audit %s not found in database", audit_id)
            return

        job_state = db.query(JobState).filter(JobState.audit_id == audit_id).first()
        if not job_state:
            job_state = JobState(
                id=str(uuid.uuid4()),
                audit_id=audit_id,
                stage="running",
                progress_percentage=5,
                started_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(job_state)
            db.commit()

        # Update initial running state
        audit.status = "running"
        job_state.stage = "running"
        job_state.progress_percentage = 5
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        # Fetch all answers for this audit
        answers = db.query(AuditAnswer).filter(AuditAnswer.audit_id == audit_id).all()
        if not answers:
            logger.warning("Audit %s has no answers to evaluate", audit_id)
            audit.status = "completed"
            audit.completed_at = datetime.datetime.now(datetime.timezone.utc)
            job_state.stage = "completed"
            job_state.progress_percentage = 100
            db.commit()
            return

        answers_by_task: Dict[str, List[AuditAnswer]] = {}
        for ans in answers:
            answers_by_task.setdefault(ans.task_id, []).append(ans)

        audit.answers_count = len(answers)
        audit.workers_count = len({ans.worker_id for ans in answers})
        db.commit()

        any_stage_failed = False
        all_created_findings: List[Finding] = []

        # -------------------------------------------------------------
        # Stage 1: Canary Marker Check (FR-14 to FR-17)
        # -------------------------------------------------------------
        job_state.current_check = "marker"
        job_state.progress_percentage = 20
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        marker_check = _get_or_create_check_result(db, audit_id, "marker")
        try:
            t0 = time.monotonic()
            marker_check.status = "running"
            db.commit()

            markers = db.query(Marker).filter(Marker.audit_id == audit_id).all()
            marker_map = {m.task_id: m.marker_token for m in markers}

            marker_findings_count = 0
            if marker_map:
                for ans in answers:
                    expected_marker = marker_map.get(ans.task_id)
                    if not expected_marker:
                        continue

                    match = detect_marker_in_text(ans.answer, expected_marker)
                    if match:
                        f_record = Finding(
                            id=str(uuid.uuid4()),
                            audit_id=audit_id,
                            answer_id=ans.id,
                            task_id=ans.task_id,
                            worker_id=ans.worker_id,
                            check_identifier="marker",
                            finding_type=match["finding_type"],
                            evidence_confidence="High",
                            explanation=match["explanation"],
                            evidence_text=match.get("evidence_text"),
                            evidence_offsets=match.get("evidence_offsets"),
                            numerical_measurements={"edit_distance": match["edit_distance"]},
                            limitations="Evidence for human review; does not prove cheating.",
                        )
                        db.add(f_record)
                        all_created_findings.append(f_record)
                        marker_findings_count += 1

            marker_check.status = "completed"
            marker_check.findings_count = marker_findings_count
            marker_check.execution_time_ms = int((time.monotonic() - t0) * 1000)
            db.commit()
        except Exception as e:
            logger.exception("Marker check failed for audit %s: %s", audit_id, e)
            marker_check.status = "failed"
            marker_check.error_message = str(e)
            any_stage_failed = True
            db.commit()

        # Check timeout (FR-33)
        if time.monotonic() - start_monotonic > TIMEOUT_SECONDS:
            _mark_timeout(db, audit, job_state)
            return

        # -------------------------------------------------------------
        # Stage 2: Reference Generation & Similarity Check (FR-18 to FR-22)
        # -------------------------------------------------------------
        job_state.current_check = "similarity"
        job_state.progress_percentage = 45
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        sim_check = _get_or_create_check_result(db, audit_id, "similarity")
        try:
            t0 = time.monotonic()
            sim_check.status = "running"
            db.commit()

            # Ensure reference answers exist for each unique task
            existing_refs = (
                db.query(ReferenceAnswer).filter(ReferenceAnswer.audit_id == audit_id).all()
            )
            refs_by_task: Dict[str, List[Dict[str, Any]]] = {}
            for r in existing_refs:
                refs_by_task.setdefault(r.task_id, []).append(
                    {
                        "provider": r.provider,
                        "model_name": r.model_name,
                        "reference_text": r.reference_text,
                    }
                )

            # Generate references for tasks without them using AIProvider
            ai_provider = get_ai_provider(
                provider_type="gemini" if audit.consent_external_ai else "offline-synthetic",
                consent_external_ai=audit.consent_external_ai,
            )

            for task_id, task_answers in answers_by_task.items():
                if task_id not in refs_by_task and task_answers:
                    prompt = task_answers[0].prompt or f"Task prompt for {task_id}"
                    ref_text = ai_provider.generate_reference(prompt)
                    ref_rec = ReferenceAnswer(
                        id=str(uuid.uuid4()),
                        audit_id=audit_id,
                        task_id=task_id,
                        provider=ai_provider.provider_name,
                        model_name=ai_provider.model_name,
                        reference_text=ref_text,
                    )
                    db.add(ref_rec)
                    refs_by_task.setdefault(task_id, []).append(
                        {
                            "provider": ai_provider.provider_name,
                            "model_name": ai_provider.model_name,
                            "reference_text": ref_text,
                        }
                    )
            db.commit()

            # Execute similarity check per task
            sim_findings_count = 0
            for task_id, task_answers in answers_by_task.items():
                task_refs = refs_by_task.get(task_id, [])
                if not task_refs:
                    continue

                formatted_answers = [
                    {"id": a.id, "worker_id": a.worker_id, "answer": a.answer} for a in task_answers
                ]
                findings = run_similarity_check_for_task(task_id, formatted_answers, task_refs)
                for f in findings:
                    f_record = _finding_to_model(audit_id, f, task_answers)
                    if f_record:
                        db.add(f_record)
                        all_created_findings.append(f_record)
                        sim_findings_count += 1

            sim_check.status = "completed"
            sim_check.findings_count = sim_findings_count
            sim_check.execution_time_ms = int((time.monotonic() - t0) * 1000)
            db.commit()
        except Exception as e:
            logger.exception("Similarity check failed for audit %s: %s", audit_id, e)
            sim_check.status = "failed"
            sim_check.error_message = str(e)
            any_stage_failed = True
            db.commit()

        # Check timeout (FR-33)
        if time.monotonic() - start_monotonic > TIMEOUT_SECONDS:
            _mark_timeout(db, audit, job_state)
            return

        # -------------------------------------------------------------
        # Stage 3: Duplicate Answers Check (FR-23 to FR-26)
        # -------------------------------------------------------------
        job_state.current_check = "duplicates"
        job_state.progress_percentage = 70
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        dup_check = _get_or_create_check_result(db, audit_id, "duplicates")
        try:
            t0 = time.monotonic()
            dup_check.status = "running"
            db.commit()

            dup_findings_count = 0
            for task_id, task_answers in answers_by_task.items():
                formatted_answers = [
                    {"id": a.id, "worker_id": a.worker_id, "answer": a.answer} for a in task_answers
                ]
                findings = run_duplicate_check_for_task(task_id, formatted_answers)
                for f in findings:
                    f_record = _finding_to_model(audit_id, f, task_answers)
                    if f_record:
                        db.add(f_record)
                        all_created_findings.append(f_record)
                        dup_findings_count += 1

            dup_check.status = "completed"
            dup_check.findings_count = dup_findings_count
            dup_check.execution_time_ms = int((time.monotonic() - t0) * 1000)
            db.commit()
        except Exception as e:
            logger.exception("Duplicates check failed for audit %s: %s", audit_id, e)
            dup_check.status = "failed"
            dup_check.error_message = str(e)
            any_stage_failed = True
            db.commit()

        # Check timeout (FR-33)
        if time.monotonic() - start_monotonic > TIMEOUT_SECONDS:
            _mark_timeout(db, audit, job_state)
            return

        # -------------------------------------------------------------
        # Stage 4: Speed Plausibility Check (FR-27, FR-28)
        # -------------------------------------------------------------
        job_state.current_check = "speed"
        job_state.progress_percentage = 85
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        speed_check = _get_or_create_check_result(db, audit_id, "speed")
        try:
            t0 = time.monotonic()
            speed_check.status = "running"
            db.commit()

            speed_findings_count = 0
            for ans in answers:
                record = {
                    "task_id": ans.task_id,
                    "worker_id": ans.worker_id,
                    "answer": ans.answer,
                    "seconds_spent": ans.seconds_spent,
                }
                f = run_speed_check(record)
                if f:
                    f_record = Finding(
                        id=str(uuid.uuid4()),
                        audit_id=audit_id,
                        answer_id=ans.id,
                        task_id=ans.task_id,
                        worker_id=ans.worker_id,
                        check_identifier="speed",
                        finding_type=f.finding_type,
                        evidence_confidence=f.evidence_confidence.value,
                        explanation=f.explanation,
                        evidence_text=f.evidence_text,
                        numerical_measurements=f.numerical_measurements,
                        limitations=f.limitations,
                    )
                    db.add(f_record)
                    all_created_findings.append(f_record)
                    speed_findings_count += 1

            speed_check.status = "completed"
            speed_check.findings_count = speed_findings_count
            speed_check.execution_time_ms = int((time.monotonic() - t0) * 1000)
            db.commit()
        except Exception as e:
            logger.exception("Speed check failed for audit %s: %s", audit_id, e)
            speed_check.status = "failed"
            speed_check.error_message = str(e)
            any_stage_failed = True
            db.commit()

        # -------------------------------------------------------------
        # Stage 5: Confidence Synthesis & Metrics Aggregation (FR-29)
        # -------------------------------------------------------------
        job_state.current_check = "synthesis"
        job_state.progress_percentage = 95
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        # Group findings by worker and calculate summary
        flagged_workers = {f.worker_id for f in all_created_findings}
        audit.flagged_workers_count = len(flagged_workers)

        high_count = sum(1 for f in all_created_findings if f.evidence_confidence == "High")
        med_count = sum(1 for f in all_created_findings if f.evidence_confidence == "Medium")
        low_count = sum(1 for f in all_created_findings if f.evidence_confidence == "Low")

        audit.summary_metrics = {
            "total_answers": audit.answers_count,
            "total_workers": audit.workers_count,
            "flagged_workers_count": audit.flagged_workers_count,
            "high_confidence_findings": high_count,
            "medium_confidence_findings": med_count,
            "low_confidence_findings": low_count,
            "total_findings": len(all_created_findings),
            "clean_answers_count": max(0, audit.answers_count - len(all_created_findings)),
            "execution_duration_sec": round(time.monotonic() - start_monotonic, 2),
        }

        # Set final completion state (FR-31, FR-34)
        audit.status = "partially_completed" if any_stage_failed else "completed"
        audit.completed_at = datetime.datetime.now(datetime.timezone.utc)

        job_state.stage = "completed"
        job_state.progress_percentage = 100
        job_state.current_check = None
        job_state.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        logger.info(
            "Audit %s finished with status %s (%d findings, %d flagged workers)",
            audit_id,
            audit.status,
            len(all_created_findings),
            audit.flagged_workers_count,
        )

    except Exception as e:
        logger.exception("Fatal audit execution error for audit %s: %s", audit_id, e)
        try:
            audit = db.query(Audit).filter(Audit.id == audit_id).first()
            if audit:
                audit.status = "failed"
            job_state = db.query(JobState).filter(JobState.audit_id == audit_id).first()
            if job_state:
                job_state.stage = "failed"
                job_state.error_log = str(e)
            db.commit()
        except Exception:
            pass
    finally:
        db.close()


def _get_or_create_check_result(db, audit_id: str, check_name: str) -> CheckResult:
    cr = (
        db.query(CheckResult)
        .filter(CheckResult.audit_id == audit_id, CheckResult.check_name == check_name)
        .first()
    )
    if not cr:
        cr = CheckResult(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            check_name=check_name,
            status="pending",
        )
        db.add(cr)
        db.commit()
    return cr


def _mark_timeout(db, audit: Audit, job_state: JobState) -> None:
    logger.error("Audit %s exceeded 20-minute execution timeout (FR-33)", audit.id)
    audit.status = "failed"
    job_state.stage = "failed"
    job_state.error_log = "Audit execution timed out (exceeded 20-minute maximum limit)."
    db.commit()


def _finding_to_model(
    audit_id: str,
    finding: CheckFinding,
    task_answers: List[AuditAnswer],
) -> Finding:
    ans_id = next((a.id for a in task_answers if a.worker_id == finding.worker_id), None)
    if not ans_id:
        ans_id = task_answers[0].id if task_answers else str(uuid.uuid4())

    return Finding(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        answer_id=ans_id,
        task_id=finding.task_id,
        worker_id=finding.worker_id,
        check_identifier=finding.check_identifier.value,
        finding_type=finding.finding_type,
        evidence_confidence=finding.evidence_confidence.value,
        explanation=finding.explanation,
        evidence_text=finding.evidence_text,
        evidence_offsets=finding.evidence_offsets,
        numerical_measurements=finding.numerical_measurements,
        related_answer_ids=finding.related_answer_ids,
        limitations=finding.limitations,
    )
