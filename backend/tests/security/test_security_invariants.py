import datetime
import uuid

import pytest

from app.checks.base import CheckFinding, CheckIdentifier, EvidenceConfidence
from app.checks.duplicates import run_duplicate_check_for_task
from app.checks.marker import detect_marker_in_text
from app.checks.similarity import run_similarity_check_for_task
from app.core.security import (
    generate_secret_token,
    hash_secret_token,
    sanitize_csv_field,
    sanitize_filename,
)
from app.models.audit import Audit, Finding
from app.reporting.csv_export import generate_csv_report
from app.reporting.html_export import generate_html_report
from app.services.ai_provider import ExternalAIProvider


def test_invariant_1_evidence_not_verdict():
    """Invariant 1: Findings and reports must state limitations and never claim absolute proof."""
    finding = CheckFinding(
        task_id="task_1",
        worker_id="worker_1",
        check_identifier=CheckIdentifier.MARKER,
        finding_type="marker_hit",
        evidence_confidence=EvidenceConfidence.HIGH,
        explanation="Marker token found in submission",
        limitations="Evidence for human review only; does not prove AI authorship or cheating.",
    )
    assert "Evidence for human review only" in finding.limitations
    assert "cheating" in finding.limitations or "AI authorship" in finding.limitations

    now = datetime.datetime.now(datetime.timezone.utc)
    audit = Audit(
        id="aud_123",
        status="completed",
        answers_count=1,
        workers_count=1,
        flagged_workers_count=1,
        created_at=now,
        expires_at=now + datetime.timedelta(days=7),
    )
    db_finding = Finding(
        id="f1",
        audit_id="aud_123",
        task_id="task_1",
        worker_id="worker_1",
        check_identifier="marker",
        finding_type="marker_hit",
        evidence_confidence="High",
        explanation="Marker token found in submission",
        limitations="Evidence for human review only; does not prove cheating.",
    )

    html = generate_html_report(audit, [db_finding], [])
    assert "Evidence, Not Verdict" in html
    assert "does not prove cheating" in html.lower() or "human review" in html.lower()


def test_invariant_4_explicit_ai_consent():
    """Invariant 4: Answers must not be sent to AI providers without explicit consent."""
    with pytest.raises(PermissionError) as exc_info:
        ExternalAIProvider(consent_external_ai=False)
    assert "Philosophical Invariant 4 Violation" in str(exc_info.value)

    # When consent is granted but API key is missing, raises ValueError rather than leaking
    with pytest.raises(ValueError) as exc_val:
        ExternalAIProvider(consent_external_ai=True, api_key=None)
    assert "API key missing" in str(exc_val.value)


def test_invariant_5_zero_unhashed_secret_persistence(db_session):
    """Invariant 5: 256-bit secret tokens stored only as SHA-256 hashes, never plaintext."""
    token, token_hash = generate_secret_token()
    audit_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=7)

    audit = Audit(
        id=audit_id,
        token_hash=token_hash,
        status="queued",
        answers_count=10,
        workers_count=2,
        expires_at=expires,
    )
    db_session.add(audit)
    db_session.commit()

    # Query back from DB
    queried = db_session.query(Audit).filter_by(token_hash=token_hash).first()
    assert queried is not None
    assert queried.token_hash == hash_secret_token(token)
    assert len(queried.token_hash) == 64

    # Plaintext token must not be an attribute on Audit model
    assert not hasattr(queried, "token")
    assert not hasattr(queried, "secret_token")


def test_invariant_6_deterministic_offline_capability():
    """Invariant 6: Marker detection, similarity, and duplicate checks run 100% offline."""
    # Marker check
    marker_res = detect_marker_in_text("Hello cnry_test123 world", "cnry_test123")
    assert marker_res is not None
    assert marker_res["match_method"] == "exact"
    assert "cnry_test123" in marker_res["evidence_text"]

    # Lexical similarity check
    answers = [
        {"id": "1", "task_id": "t1", "worker_id": "w1", "answer": "The quick brown fox"},
        {"id": "2", "task_id": "t1", "worker_id": "w2", "answer": "The quick brown fox"},
    ]
    sim_findings = run_similarity_check_for_task(
        "t1",
        answers,
        [{"reference_text": "The quick brown fox", "provider": "mock", "model_name": "mock"}],
    )
    assert isinstance(sim_findings, list)

    # Duplicate check
    dup_findings = run_duplicate_check_for_task("t1", answers)
    assert isinstance(dup_findings, list)


def test_formula_injection_defense():
    """CSV export and sanitization must neutralize spreadsheet formula injection vectors."""
    assert sanitize_csv_field("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_csv_field("+1+2") == "'+1+2"
    assert sanitize_csv_field("-5*10") == "'-5*10"
    assert sanitize_csv_field("@SUM(B1:B10)") == "'@SUM(B1:B10)"
    assert sanitize_csv_field("\t=1+1") == "'\t=1+1"
    assert sanitize_csv_field("\r=1+1") == "'\r=1+1"

    # CSV report generator output check
    audit = Audit(id="aud_test")
    finding = Finding(
        id="f1",
        audit_id="aud_test",
        answer_id="ans_1",
        task_id="=1+1",
        worker_id="+worker_admin",
        check_identifier="similarity",
        finding_type="similarity_hit",
        evidence_confidence="Medium",
        explanation="=cmd|' /C calc'!A0",
        limitations="Evidence for human review only",
    )
    csv_content = generate_csv_report(audit, [finding])
    assert "'=cmd|" in csv_content
    assert "'+worker_admin" in csv_content


def test_sanitize_filename_path_traversal():
    """Path traversal and forbidden characters must be stripped from filenames."""
    assert sanitize_filename("../../../../etc/passwd") == "etc_passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "windows_system32_cmd.exe"
    assert sanitize_filename("safe_dataset.jsonl") == "safe_dataset.jsonl"
