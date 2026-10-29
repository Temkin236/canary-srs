import os
from pathlib import Path

from app.services.dataset import resolve_column_mapping, validate_and_parse_dataset
from app.services.storage import delete_stored_file, save_uploaded_file

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_valid_csv_parsing():
    content = (FIXTURES_DIR / "valid_sample.csv").read_bytes()
    resp, records = validate_and_parse_dataset(content, "valid_sample.csv")

    assert resp.valid is True
    assert resp.total_rows == 3
    assert resp.tasks_count == 2
    assert resp.workers_count == 2
    assert len(resp.errors) == 0
    assert len(records) == 3
    assert records[0]["task_id"] == "task_101"
    assert records[0]["seconds_spent"] == 45.2
    assert records[0]["submitted_at"] is not None


def test_valid_jsonl_parsing():
    content = (FIXTURES_DIR / "valid_sample.jsonl").read_bytes()
    resp, records = validate_and_parse_dataset(content, "valid_sample.jsonl")

    assert resp.valid is True
    assert resp.total_rows == 3
    assert resp.tasks_count == 2
    assert resp.workers_count == 3
    assert len(resp.errors) == 0
    assert len(records) == 3


def test_malformed_csv_row_errors():
    content = (FIXTURES_DIR / "malformed_rows.csv").read_bytes()
    resp, records = validate_and_parse_dataset(content, "malformed_rows.csv")

    assert resp.valid is False
    assert len(resp.errors) >= 3

    # Check row-specific error messages and row indices
    error_fields = {e.field for e in resp.errors if e.field}
    assert "answer" in error_fields
    assert "task_id" in error_fields
    assert "prompt" in error_fields

    # Check warnings for invalid timestamp and negative seconds
    warning_fields = {w.field for w in resp.warnings if w.field}
    assert "seconds_spent" in warning_fields
    assert "submitted_at" in warning_fields


def test_empty_answers_jsonl():
    content = (FIXTURES_DIR / "empty_answers.jsonl").read_bytes()
    resp, records = validate_and_parse_dataset(content, "empty_answers.jsonl")

    assert resp.valid is False
    assert any(e.field == "answer" for e in resp.errors)
    assert len(records) == 0


def test_column_mapping_resolution():
    headers = ["ID", "Query", "Annotator", "Completion", "Timestamp"]
    mapping = resolve_column_mapping(headers)

    assert mapping["task_id"] == "ID"
    assert mapping["prompt"] == "Query"
    assert mapping["worker_id"] == "Annotator"
    assert mapping["answer"] == "Completion"
    assert mapping["submitted_at"] == "Timestamp"


def test_file_size_limit_rejection():
    # 11 MB artificial payload exceeding 10 MB limit
    large_payload = b"a" * (11 * 1024 * 1024)
    resp, records = validate_and_parse_dataset(large_payload, "large.csv")

    assert resp.valid is False
    assert any("exceeds maximum limit" in e.message for e in resp.errors)


def test_storage_uuid_sanitization():
    test_content = b"sample,test,data"
    stored_path = save_uploaded_file(test_content, "../../dangerous/path/exploit.csv")

    assert os.path.exists(stored_path)
    # The filename must be an internal UUID hex, not the original path
    filename = os.path.basename(stored_path)
    assert not filename.startswith("..")
    assert filename.endswith(".csv")
    assert len(filename) > 30  # UUID hex length + extension

    # Clean up
    deleted = delete_stored_file(stored_path)
    assert deleted is True
    assert not os.path.exists(stored_path)


def test_api_validate_endpoint(client):
    content = (FIXTURES_DIR / "valid_sample.csv").read_bytes()
    response = client.post(
        "/api/v1/audits/validate",
        files={"file": ("valid_sample.csv", content, "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["total_rows"] == 3
    assert len(data["preview"]) > 0
