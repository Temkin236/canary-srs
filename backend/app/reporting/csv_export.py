import csv
import io
import json
from typing import List

from app.core.security import sanitize_csv_field
from app.models.audit import Audit, Finding


def generate_csv_report(audit: Audit, findings: List[Finding]) -> str:
    """
    Generates a formula-injection-protected CSV export of audit findings (FR-39).
    All string values are sanitized to defend against spreadsheet macro execution.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header row
    headers = [
        "finding_id",
        "task_id",
        "worker_id",
        "check_identifier",
        "finding_type",
        "evidence_confidence",
        "explanation",
        "evidence_text",
        "numerical_measurements",
        "limitations",
    ]
    writer.writerow([sanitize_csv_field(h) for h in headers])

    for f in findings:
        measurements_str = json.dumps(f.numerical_measurements or {})
        row = [
            f.id,
            f.task_id,
            f.worker_id,
            f.check_identifier,
            f.finding_type,
            f.evidence_confidence,
            f.explanation,
            f.evidence_text or "",
            measurements_str,
            f.limitations or "Evidence for human review only; does not prove cheating.",
        ]
        writer.writerow([sanitize_csv_field(str(cell)) for cell in row])

    return output.getvalue()
