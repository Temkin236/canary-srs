import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.schemas.dataset import DatasetValidationResponse, RowError, RowWarning

REQUIRED_STANDARD_FIELDS = ["task_id", "prompt", "worker_id", "answer"]
OPTIONAL_STANDARD_FIELDS = ["submitted_at", "seconds_spent"]

COMMON_ALIASES = {
    "task_id": ["task_id", "taskid", "task", "item_id", "id"],
    "prompt": ["prompt", "instruction", "query", "question", "task_text", "input"],
    "worker_id": [
        "worker_id",
        "workerid",
        "worker",
        "annotator",
        "annotator_id",
        "user_id",
        "agent_id",
    ],
    "answer": ["answer", "response", "completion", "output", "worker_answer", "text"],
    "submitted_at": ["submitted_at", "timestamp", "created_at", "submission_time"],
    "seconds_spent": [
        "seconds_spent",
        "duration",
        "duration_seconds",
        "time_taken",
        "elapsed_seconds",
    ],
}


def resolve_column_mapping(
    headers: List[str], custom_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Resolves source file column headers to standard required/optional schema fields.
    Returns: mapping of {standard_field: source_column_name}
    """
    resolved: Dict[str, str] = {}
    normalized_headers = {h.strip().lower(): h for h in headers if h}

    # 1. Apply custom user mappings if provided
    if custom_mapping:
        for std_field, src_col in custom_mapping.items():
            if src_col and src_col in headers:
                resolved[std_field] = src_col

    # 2. Auto-resolve remaining fields using standard aliases
    for std_field, aliases in COMMON_ALIASES.items():
        if std_field not in resolved:
            for alias in aliases:
                if alias.lower() in normalized_headers:
                    resolved[std_field] = normalized_headers[alias.lower()]
                    break

    return resolved


def parse_timestamp(val: Any) -> Optional[datetime]:
    """Attempts to parse ISO 8601 UTC timestamp."""
    if not val:
        return None
    s = str(val).strip()
    try:
        # Replace trailing Z with +00:00 for fromisoformat compatibility
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        # Try common fallback formats
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
    return None


def validate_and_parse_dataset(
    content_bytes: bytes,
    filename: str,
    custom_mapping: Optional[Dict[str, str]] = None,
) -> Tuple[DatasetValidationResponse, List[Dict[str, Any]]]:
    """
    Validates CSV or JSONL dataset bytes against FR-1 through FR-8 requirements.
    Returns:
        (ValidationResponse, ValidatedRecordsList)
    """
    errors: List[RowError] = []
    warnings: List[RowWarning] = []
    records: List[Dict[str, Any]] = []

    # Check file size limit (FR-4)
    if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        size_mb = len(content_bytes) / (1024 * 1024)
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        errors.append(
            RowError(message=f"File size ({size_mb:.2f} MB) exceeds maximum limit of {max_mb} MB.")
        )
        return (
            DatasetValidationResponse(
                valid=False,
                total_rows=0,
                tasks_count=0,
                workers_count=0,
                detected_columns=[],
                column_mapping_used={},
                errors=errors,
            ),
            [],
        )

    # Decode bytes (UTF-8 or UTF-8-sig)
    try:
        text = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = content_bytes.decode("latin-1")
            warnings.append(
                RowWarning(message="File was not valid UTF-8; decoded using Latin-1 fallback.")
            )
        except Exception:
            errors.append(
                RowError(message="Unable to decode file. Please provide valid UTF-8 CSV or JSONL.")
            )
            return (
                DatasetValidationResponse(
                    valid=False,
                    total_rows=0,
                    tasks_count=0,
                    workers_count=0,
                    detected_columns=[],
                    column_mapping_used={},
                    errors=errors,
                    warnings=warnings,
                ),
                [],
            )

    is_jsonl = filename.lower().endswith(".jsonl") or (
        not filename.lower().endswith(".csv") and text.strip().startswith("{")
    )

    raw_rows: List[Dict[str, Any]] = []
    headers: List[str] = []

    if is_jsonl:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line_num, line in enumerate(lines, start=1):
            try:
                row_dict = json.loads(line)
                if not isinstance(row_dict, dict):
                    errors.append(
                        RowError(row=line_num, message="JSONL row is not a valid JSON object.")
                    )
                    continue
                raw_rows.append(row_dict)
                for k in row_dict.keys():
                    if k not in headers:
                        headers.append(k)
            except json.JSONDecodeError as e:
                errors.append(
                    RowError(row=line_num, message=f"Malformed JSON on line {line_num}: {e.msg}")
                )
    else:
        # Parse CSV
        f = io.StringIO(text)
        try:
            reader = csv.DictReader(f)
            headers = [h for h in (reader.fieldnames or []) if h]
            for row_idx, row in enumerate(reader, start=2):  # 1-indexed, row 1 is header
                raw_rows.append(row)
        except Exception as e:
            errors.append(RowError(message=f"Failed to parse CSV: {str(e)}"))

    if not headers and not raw_rows and not errors:
        errors.append(RowError(message="Uploaded file is empty."))

    # Resolve column mappings
    mapping = resolve_column_mapping(headers, custom_mapping)

    # Check for missing required columns
    for req in REQUIRED_STANDARD_FIELDS:
        if req not in mapping or not mapping[req]:
            headers_str = ", ".join(headers) if headers else "none"
            errors.append(
                RowError(
                    field=req,
                    message=f"Missing required column '{req}'. Detected: {headers_str}.",
                )
            )

    # If critical structural errors exist, return early
    if any(e.field in REQUIRED_STANDARD_FIELDS for e in errors):
        return (
            DatasetValidationResponse(
                valid=False,
                total_rows=len(raw_rows),
                tasks_count=0,
                workers_count=0,
                detected_columns=headers,
                column_mapping_used=mapping,
                errors=errors,
                warnings=warnings,
                preview=[],
            ),
            [],
        )

    # Validate row by row
    unique_tasks = set()
    unique_workers = set()
    seen_row_hashes = set()

    for idx, row in enumerate(raw_rows, start=1):
        row_num = idx if is_jsonl else idx + 1  # in CSV row 1 is header

        task_id = str(row.get(mapping.get("task_id", ""), "")).strip()
        prompt = str(row.get(mapping.get("prompt", ""), "")).strip()
        worker_id = str(row.get(mapping.get("worker_id", ""), "")).strip()
        answer = str(row.get(mapping.get("answer", ""), "")).strip()

        row_errors = []

        if not task_id:
            row_errors.append(RowError(row=row_num, field="task_id", message="task_id is empty."))
        if not prompt:
            row_errors.append(RowError(row=row_num, field="prompt", message="prompt is empty."))
        if not worker_id:
            row_errors.append(
                RowError(row=row_num, field="worker_id", message="worker_id is empty.")
            )
        if not answer:
            row_errors.append(RowError(row=row_num, field="answer", message="answer is empty."))

        # Optional field: seconds_spent
        seconds_spent_val: Optional[float] = None
        if "seconds_spent" in mapping and mapping["seconds_spent"] in row:
            raw_sec = row.get(mapping["seconds_spent"])
            if raw_sec is not None and str(raw_sec).strip() != "":
                try:
                    sec_float = float(raw_sec)
                    if sec_float < 0:
                        warnings.append(
                            RowWarning(
                                row=row_num,
                                field="seconds_spent",
                                message="seconds_spent is negative; ignored.",
                            )
                        )
                    else:
                        seconds_spent_val = sec_float
                except ValueError:
                    warnings.append(
                        RowWarning(
                            row=row_num,
                            field="seconds_spent",
                            message=f"seconds_spent '{raw_sec}' is not numeric; ignored.",
                        )
                    )

        # Optional field: submitted_at
        submitted_at_val: Optional[datetime] = None
        if "submitted_at" in mapping and mapping["submitted_at"] in row:
            raw_ts = row.get(mapping["submitted_at"])
            if raw_ts is not None and str(raw_ts).strip() != "":
                parsed_dt = parse_timestamp(raw_ts)
                if parsed_dt is None:
                    warnings.append(
                        RowWarning(
                            row=row_num,
                            field="submitted_at",
                            message=f"submitted_at '{raw_ts}' could not be parsed as timestamp.",
                        )
                    )
                else:
                    submitted_at_val = parsed_dt

        # Check duplicate identical answer row
        row_key = (task_id, worker_id, answer)
        if row_key in seen_row_hashes and task_id and worker_id and answer:
            warnings.append(
                RowWarning(
                    row=row_num,
                    message="Duplicate identical answer row detected for the same task and worker.",
                )
            )
        seen_row_hashes.add(row_key)

        if row_errors:
            errors.extend(row_errors)
        else:
            unique_tasks.add(task_id)
            unique_workers.add(worker_id)
            records.append(
                {
                    "task_id": task_id,
                    "prompt": prompt,
                    "worker_id": worker_id,
                    "answer": answer,
                    "submitted_at": submitted_at_val,
                    "seconds_spent": seconds_spent_val,
                }
            )

    # Check record count limit (FR-4)
    if len(records) > settings.MAX_RECORDS_COUNT:
        errors.append(
            RowError(
                message=(
                    f"Dataset contains {len(records)} answers, which exceeds "
                    f"the limit of {settings.MAX_RECORDS_COUNT} answers."
                )
            )
        )

    is_valid = len(errors) == 0 and len(records) > 0

    preview = [
        {
            "task_id": r["task_id"],
            "worker_id": r["worker_id"],
            "prompt": r["prompt"][:80] + "..." if len(r["prompt"]) > 80 else r["prompt"],
            "answer": r["answer"][:120] + "..." if len(r["answer"]) > 120 else r["answer"],
            "seconds_spent": r["seconds_spent"],
        }
        for r in records[:5]
    ]

    response = DatasetValidationResponse(
        valid=is_valid,
        total_rows=len(records),
        tasks_count=len(unique_tasks),
        workers_count=len(unique_workers),
        detected_columns=headers,
        column_mapping_used=mapping,
        errors=errors,
        warnings=warnings,
        preview=preview,
    )

    return response, records
