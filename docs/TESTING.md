# Testing Strategy & Verification Guide — Canary SRS

## Overview
Canary SRS maintains a comprehensive test suite across backend unit, integration, security, and frontend component tests.

## Test Organization
- `backend/tests/unit/`:
  - `test_dataset.py`: CSV/JSONL parsing, row validation, size limits.
  - `test_marker_gen.py`: Entropy, collision resistance, format compatibility.
  - `test_marker_check.py`: Exact, case, whitespace, bounded typo distance.
  - `test_similarity.py`: Lexical TF-IDF cosine, semantic, peer percentile ranking.
  - `test_duplicates.py`: Exact and near-duplicate cluster detection.
  - `test_speed.py`: Velocity computation, boundary conditions, missing metadata.
  - `test_confidence.py`: Deterministic evidence synthesis and limitation notes.
  - `test_calibration.py`: Wilson score confidence interval calculations.
  - `test_reporting.py`: Self-contained HTML and JSON export integrity.
  - `test_cleanup.py`: 7-day TTL expiration logic.
- `backend/tests/security/`:
  - `test_security.py`: CSV formula injection escaping, XSS sanitization, secret token hashing, path traversal defenses.
- `backend/tests/integration/`:
  - `test_api.py`: FastAPI endpoints and HTTP response code fidelity.
  - `test_job.py`: Job lifecycle state transitions (`queued` $\to$ `completed`).
- `frontend/tests/`:
  - Vitest + React Testing Library component tests.

## Running Tests
### Backend
```bash
cd backend
.venv/bin/pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm run test
```
