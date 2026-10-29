import datetime

from app.models.audit import Audit, CheckResult, Finding
from app.reporting.csv_export import generate_csv_report
from app.reporting.html_export import generate_html_report
from app.reporting.json_export import generate_json_report


def test_html_export_xss_escaping_and_self_contained():
    audit = Audit(
        id="audit-test-12345",
        status="completed",
        answers_count=10,
        workers_count=2,
        flagged_workers_count=1,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
    )
    # Finding with malicious script tags to test XSS escaping
    malicious_finding = Finding(
        id="f1",
        audit_id="audit-test-12345",
        answer_id="ans-1",
        task_id="<script>alert('xss')</script>",
        worker_id="<img src=x onerror=alert(1)>",
        check_identifier="marker",
        finding_type="exact_marker_leak",
        evidence_confidence="High",
        explanation="Exact marker found <script>evil()</script>",
        evidence_text="Secret token <b>leak</b>",
    )
    html_out = generate_html_report(audit, [malicious_finding], [])

    # Invariant: Must escape all XSS payloads (FR-38)
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out
    assert "&lt;img src=x" in html_out
    assert "Evidence, Not Verdict" in html_out  # Philosophical invariant notice
    assert "Canary SRS" in html_out


def test_csv_export_formula_injection_defense():
    audit = Audit(id="audit-csv-123")
    # Finding containing formula injection triggers: =, +, -, @
    finding = Finding(
        id="f2",
        audit_id="audit-csv-123",
        answer_id="ans-2",
        task_id="=cmd|' /C calc'!A0",
        worker_id="+worker_123",
        check_identifier="duplicates",
        finding_type="cross_worker_exact_duplicate",
        evidence_confidence="Medium",
        explanation="@explanation starting with at",
        evidence_text="-minus formula",
    )
    csv_out = generate_csv_report(audit, [finding])

    # Formula injection defense (FR-39): leading =, +, -, @ must be quoted with '
    assert "'=cmd|" in csv_out
    assert "'+worker_123" in csv_out
    assert "'@explanation" in csv_out
    assert "'-minus" in csv_out


def test_json_export_structure():
    audit = Audit(
        id="audit-json-123",
        status="completed",
        answers_count=5,
        workers_count=2,
        flagged_workers_count=1,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
    )
    cr = CheckResult(
        id="cr1",
        audit_id="audit-json-123",
        check_name="marker",
        status="completed",
        findings_count=1,
        execution_time_ms=12,
    )
    f = Finding(
        id="f3",
        audit_id="audit-json-123",
        task_id="t1",
        worker_id="w1",
        answer_id="ans1",
        check_identifier="marker",
        finding_type="exact_marker_leak",
        evidence_confidence="High",
        explanation="Marker leaked",
    )
    json_out = generate_json_report(audit, [f], [cr])
    assert json_out["audit_id"] == "audit-json-123"
    assert len(json_out["findings"]) == 1
    assert len(json_out["checks_executed"]) == 1
    assert "Philosophical Invariant 1" in json_out["notice"]
