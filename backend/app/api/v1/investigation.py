import datetime
import difflib
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit import (
    Audit,
    AuditAnswer,
    Finding,
    FindingReviewHistory,
    Marker,
    ReferenceAnswer,
)
from app.schemas.investigation import (
    ComparisonDiffSegment,
    DuplicateClusterItem,
    FindingDetailedItem,
    FindingReviewHistoryItem,
    FindingReviewUpdateRequest,
    InvestigationWorkspaceResponse,
    MarkerInvestigationItem,
    SideBySideComparisonResponse,
)

router = APIRouter(tags=["Investigation"])


def _compute_diff_segments(source: str, target: str) -> List[ComparisonDiffSegment]:
    """Uses SequenceMatcher to generate explainable diff segments between source and target text."""
    matcher = difflib.SequenceMatcher(None, source, target)
    segments: List[ComparisonDiffSegment] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            segments.append(
                ComparisonDiffSegment(
                    text=source[i1:i2],
                    is_match=True,
                    is_source_only=False,
                    is_target_only=False,
                )
            )
        elif tag == "replace":
            if i1 < i2:
                segments.append(
                    ComparisonDiffSegment(
                        text=source[i1:i2],
                        is_match=False,
                        is_source_only=True,
                        is_target_only=False,
                    )
                )
            if j1 < j2:
                segments.append(
                    ComparisonDiffSegment(
                        text=target[j1:j2],
                        is_match=False,
                        is_source_only=False,
                        is_target_only=True,
                    )
                )
        elif tag == "delete":
            segments.append(
                ComparisonDiffSegment(
                    text=source[i1:i2],
                    is_match=False,
                    is_source_only=True,
                    is_target_only=False,
                )
            )
        elif tag == "insert":
            segments.append(
                ComparisonDiffSegment(
                    text=target[j1:j2],
                    is_match=False,
                    is_source_only=False,
                    is_target_only=True,
                )
            )

    return segments


@router.get("/audits/{audit_id}/investigate", response_model=InvestigationWorkspaceResponse)
def get_audit_investigation_workspace(
    audit_id: str,
    db: Session = Depends(get_db),
):
    """Returns complete investigation payload for an audit: findings, worker answers,

    markers, duplicate clusters, and reviewer status.
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        # Check if the parameter passed was a token hash or secret
        from app.core.security import hash_audit_token

        token_hash = hash_audit_token(audit_id)
        audit = db.query(Audit).filter(Audit.token_hash == token_hash).first()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit workspace not found or expired under 7-day retention policy.",
        )

    # 1. Fetch Findings with correlated answers & history
    db_findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
    detailed_findings: List[FindingDetailedItem] = []

    for f in db_findings:
        answer = f.audit_answer
        history_items = [
            FindingReviewHistoryItem(
                id=h.id,
                finding_id=h.finding_id,
                action=h.action,
                previous_status=h.previous_status,
                new_status=h.new_status,
                reviewer_id=h.reviewer_id,
                notes=h.notes,
                dismissal_reason=h.dismissal_reason,
                created_at=h.created_at,
            )
            for h in (f.review_history or [])
        ]

        detailed_findings.append(
            FindingDetailedItem(
                id=f.id,
                audit_id=f.audit_id,
                answer_id=f.answer_id,
                task_id=f.task_id,
                worker_id=f.worker_id,
                check_identifier=f.check_identifier,
                finding_type=f.finding_type,
                evidence_confidence=f.evidence_confidence,
                explanation=f.explanation,
                evidence_text=f.evidence_text,
                evidence_offsets=f.evidence_offsets,
                numerical_measurements=f.numerical_measurements or {},
                related_answer_ids=f.related_answer_ids or [],
                limitations=f.limitations,
                review_status=f.review_status,
                reviewer_notes=f.reviewer_notes,
                assigned_reviewer=f.assigned_reviewer,
                reviewed_at=f.reviewed_at,
                created_at=f.created_at,
                worker_answer=answer.answer if answer else None,
                prompt=answer.prompt if answer else None,
                history=history_items,
            )
        )

    # 2. Markers correlation
    db_markers = db.query(Marker).filter(Marker.audit_id == audit.id).all()
    marker_items: List[MarkerInvestigationItem] = []

    # Map task markers to finding if detected
    marker_finding_map = {f.task_id: f for f in db_findings if f.check_identifier == "marker"}

    for m in db_markers:
        matched_finding = marker_finding_map.get(m.task_id)
        is_detected = matched_finding is not None
        marker_items.append(
            MarkerInvestigationItem(
                id=m.id,
                task_id=m.task_id,
                marker_id=m.id,
                expected_marker=m.marker_token,
                detected=is_detected,
                detected_marker=m.marker_token if is_detected else None,
                location_in_answer=matched_finding.evidence_offsets if matched_finding else None,
                preparation_version="v1.0",
                finding_id=matched_finding.id if matched_finding else None,
            )
        )

    # 3. Duplicate clusters
    duplicate_findings = [f for f in db_findings if f.check_identifier == "duplicates"]
    clusters_by_task: dict[str, list[Finding]] = {}
    for df in duplicate_findings:
        clusters_by_task.setdefault(df.task_id, []).append(df)

    cluster_items: List[DuplicateClusterItem] = []
    cluster_idx = 1
    for task_id, task_findings in clusters_by_task.items():
        worker_set = list(set([f.worker_id for f in task_findings]))
        answer_set = list(set([f.answer_id for f in task_findings]))
        rep_text = task_findings[0].evidence_text or ""
        sim_scores: dict[str, float] = {}
        for f in task_findings:
            score = (
                f.numerical_measurements.get("jaccard_similarity")
                or f.numerical_measurements.get("similarity")
                or 0.95
            )
            sim_scores[f.worker_id] = float(score)

        cluster_items.append(
            DuplicateClusterItem(
                cluster_id=f"cluster_{cluster_idx:03d}",
                task_id=task_id,
                worker_ids=worker_set,
                answer_ids=answer_set,
                representative_text=rep_text,
                similarity_matrix=sim_scores,
                findings_count=len(task_findings),
            )
        )
        cluster_idx += 1

    # 4. Calibration metrics
    cal_data = None
    if audit.calibration_run:
        c = audit.calibration_run
        cal_data = {
            "sample_size": c.sample_size,
            "flagged_count": c.flagged_count,
            "estimated_fp_rate": c.estimated_fp_rate,
            "ci_lower": c.ci_lower,
            "ci_upper": c.ci_upper,
            "ci_method": c.ci_method,
        }

    return InvestigationWorkspaceResponse(
        audit={
            "id": audit.id,
            "dataset_name": audit.dataset_name,
            "status": audit.status,
            "answers_count": audit.answers_count,
            "workers_count": audit.workers_count,
            "flagged_workers_count": audit.flagged_workers_count,
            "consent_external_ai": audit.consent_external_ai,
            "created_at": audit.created_at.isoformat(),
            "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
            "expires_at": audit.expires_at.isoformat(),
            "owner_id": audit.owner_id,
            "summary_metrics": audit.summary_metrics or {},
        },
        findings=detailed_findings,
        markers=marker_items,
        duplicate_clusters=cluster_items,
        calibration=cal_data,
    )


@router.patch("/findings/{finding_id}/review", response_model=FindingDetailedItem)
def update_finding_review_status(
    finding_id: str,
    payload: FindingReviewUpdateRequest,
    db: Session = Depends(get_db),
):
    """Adjudicates a finding with an explicit human review status, notes, dismissal reasons,

    and persists an immutable audit log entry.
    """
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found.",
        )

    previous_status = finding.review_status
    new_status = payload.review_status
    now = datetime.datetime.now(datetime.timezone.utc)

    # Determine audit log action
    if previous_status != new_status:
        action = "status_change"
    elif payload.dismissal_reason:
        action = "dismissal"
    elif payload.assigned_reviewer and payload.assigned_reviewer != finding.assigned_reviewer:
        action = "assignment"
    else:
        action = "note_added"

    # Update finding
    finding.review_status = new_status
    if payload.reviewer_notes is not None:
        finding.reviewer_notes = payload.reviewer_notes
    if payload.assigned_reviewer is not None:
        finding.assigned_reviewer = payload.assigned_reviewer
    finding.reviewed_at = now

    # Record review history audit trail
    history_entry = FindingReviewHistory(
        id=str(uuid.uuid4()),
        finding_id=finding.id,
        audit_id=finding.audit_id,
        action=action,
        previous_status=previous_status,
        new_status=new_status,
        reviewer_id=payload.reviewer_id,
        notes=payload.reviewer_notes,
        dismissal_reason=payload.dismissal_reason,
        created_at=now,
    )
    db.add(history_entry)
    db.commit()
    db.refresh(finding)

    answer = finding.audit_answer
    history_items = [
        FindingReviewHistoryItem(
            id=h.id,
            finding_id=h.finding_id,
            action=h.action,
            previous_status=h.previous_status,
            new_status=h.new_status,
            reviewer_id=h.reviewer_id,
            notes=h.notes,
            dismissal_reason=h.dismissal_reason,
            created_at=h.created_at,
        )
        for h in finding.review_history
    ]

    return FindingDetailedItem(
        id=finding.id,
        audit_id=finding.audit_id,
        answer_id=finding.answer_id,
        task_id=finding.task_id,
        worker_id=finding.worker_id,
        check_identifier=finding.check_identifier,
        finding_type=finding.finding_type,
        evidence_confidence=finding.evidence_confidence,
        explanation=finding.explanation,
        evidence_text=finding.evidence_text,
        evidence_offsets=finding.evidence_offsets,
        numerical_measurements=finding.numerical_measurements or {},
        related_answer_ids=finding.related_answer_ids or [],
        limitations=finding.limitations,
        review_status=finding.review_status,
        reviewer_notes=finding.reviewer_notes,
        assigned_reviewer=finding.assigned_reviewer,
        reviewed_at=finding.reviewed_at,
        created_at=finding.created_at,
        worker_answer=answer.answer if answer else None,
        prompt=answer.prompt if answer else None,
        history=history_items,
    )


@router.get("/findings/{finding_id}/history", response_model=List[FindingReviewHistoryItem])
def get_finding_review_history(
    finding_id: str,
    db: Session = Depends(get_db),
):
    """Returns chronological audit trail of human adjudications and notes for a finding."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found.")

    history_records = (
        db.query(FindingReviewHistory)
        .filter(FindingReviewHistory.finding_id == finding_id)
        .order_by(FindingReviewHistory.created_at.desc())
        .all()
    )

    return [
        FindingReviewHistoryItem(
            id=h.id,
            finding_id=h.finding_id,
            action=h.action,
            previous_status=h.previous_status,
            new_status=h.new_status,
            reviewer_id=h.reviewer_id,
            notes=h.notes,
            dismissal_reason=h.dismissal_reason,
            created_at=h.created_at,
        )
        for h in history_records
    ]


@router.get("/findings/{finding_id}/comparison", response_model=SideBySideComparisonResponse)
def get_finding_comparison(
    finding_id: str,
    db: Session = Depends(get_db),
):
    """Computes side-by-side comparison between the worker answer and reference/duplicate answer

    with highlighted diff segments and explainable metrics.
    """
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found.")

    worker_answer = finding.audit_answer
    source_text = worker_answer.answer if worker_answer else (finding.evidence_text or "")

    target_text = ""
    target_label = "Comparison Reference"
    comparison_type = "reference_model"

    if finding.check_identifier == "similarity":
        # Check for model reference answer
        ref = (
            db.query(ReferenceAnswer)
            .filter(
                ReferenceAnswer.audit_id == finding.audit_id,
                ReferenceAnswer.task_id == finding.task_id,
            )
            .first()
        )
        if ref:
            target_text = ref.reference_text
            target_label = f"Model Reference Output ({ref.provider} / {ref.model_name})"
        else:
            target_text = finding.evidence_text or "No model reference answer stored."
            target_label = "Reference Baseline"

    elif finding.check_identifier == "duplicates":
        comparison_type = "duplicate_worker"
        target_label = "Duplicate Peer Answer"
        if finding.related_answer_ids:
            peer_answer = (
                db.query(AuditAnswer)
                .filter(AuditAnswer.id == finding.related_answer_ids[0])
                .first()
            )
            if peer_answer:
                target_text = peer_answer.answer
                target_label = f"Worker {peer_answer.worker_id} (Task {peer_answer.task_id})"
            else:
                target_text = finding.evidence_text or ""
        else:
            target_text = finding.evidence_text or ""

    elif finding.check_identifier == "marker":
        comparison_type = "marker_verification"
        target_label = "Expected Hidden Task Marker"
        marker = (
            db.query(Marker)
            .filter(Marker.audit_id == finding.audit_id, Marker.task_id == finding.task_id)
            .first()
        )
        target_text = marker.marker_token if marker else (finding.evidence_text or "")

    else:
        target_text = finding.evidence_text or "Descriptive benchmark pattern"
        target_label = "Reference Baseline"

    diff_segments = _compute_diff_segments(source_text, target_text)

    sim_score = (
        finding.numerical_measurements.get("jaccard_similarity")
        or finding.numerical_measurements.get("similarity")
        or finding.numerical_measurements.get("tfidf_cosine")
    )
    if sim_score is not None:
        sim_score = float(sim_score)

    return SideBySideComparisonResponse(
        finding_id=finding.id,
        task_id=finding.task_id,
        worker_id=finding.worker_id,
        comparison_type=comparison_type,
        source_answer=source_text,
        target_answer=target_text,
        target_label=target_label,
        similarity_score=sim_score,
        measurements=finding.numerical_measurements or {},
        explanation=finding.explanation,
        diff_segments=diff_segments,
        limitations=finding.limitations,
    )
