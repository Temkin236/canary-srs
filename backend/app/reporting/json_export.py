from typing import Any, Dict, List

from app.models.audit import Audit, CheckResult, Finding


def generate_json_report(
    audit: Audit,
    findings: List[Finding],
    check_results: List[CheckResult],
) -> Dict[str, Any]:
    """
    Generates a machine-readable JSON export of findings and metadata (FR-40).
    """
    return {
        "audit_id": audit.id,
        "status": audit.status,
        "created_at": audit.created_at.isoformat() if audit.created_at else None,
        "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
        "expires_at": audit.expires_at.isoformat() if audit.expires_at else None,
        "consent_external_ai": audit.consent_external_ai,
        "summary_metrics": audit.summary_metrics or {},
        "checks_executed": [
            {
                "check_name": cr.check_name,
                "status": cr.status,
                "findings_count": cr.findings_count,
                "execution_time_ms": cr.execution_time_ms,
                "error_message": cr.error_message,
            }
            for cr in check_results
        ],
        "findings": [
            {
                "finding_id": f.id,
                "task_id": f.task_id,
                "worker_id": f.worker_id,
                "answer_id": f.answer_id,
                "check_identifier": f.check_identifier,
                "finding_type": f.finding_type,
                "evidence_confidence": f.evidence_confidence,
                "explanation": f.explanation,
                "evidence_text": f.evidence_text,
                "evidence_offsets": f.evidence_offsets,
                "numerical_measurements": f.numerical_measurements or {},
                "limitations": f.limitations,
            }
            for f in findings
        ],
        "notice": (
            "Philosophical Invariant 1: Findings constitute evidence for human review, "
            "never automated proof of AI authorship or cheating."
        ),
    }
