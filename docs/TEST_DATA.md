# Test Data Specifications — Canary SRS

## Test Data Directory Structure
- `backend/tests/fixtures/`: Synthetic datasets for automated tests.
  - `valid_sample.csv`: Compliant CSV with all required and optional columns.
  - `valid_sample.jsonl`: Compliant JSONL with varied answer lengths and task IDs.
  - `malformed_rows.csv`: Dataset with missing columns, invalid UTF-8, and empty answers.
  - `synthetic_contaminated.jsonl`: Benchmarking dataset with known ground-truth contamination labels (markers, AI copies, duplicates).
  - `synthetic_clean_human.jsonl`: Benchmarking dataset with human-verified clean responses for false-positive rate evaluation.

## Schema Specifications
### Required Fields
- `task_id`: String (1-128 chars).
- `prompt`: String (1-50,000 chars).
- `worker_id`: String (1-128 chars).
- `answer`: String (1-100,000 chars).

### Optional Fields
- `submitted_at`: ISO 8601 UTC timestamp string.
- `seconds_spent`: Float / Integer ($\ge 0$).
