# Testing Strategy & Verification Guide — Canary SRS

Canary SRS employs automated test suites covering unit algorithms, system integration, security invariants, and frontend user workflows.

---

## 1. Verified Test Suite Summary

All tests are verified and passing locally and in CI:

```
========================= 90 PASSED IN TOTAL =========================
Backend Tests:   70 passed (55 unit, 9 integration, 6 security)
Frontend Tests:  20 passed (5 test suites)
Code Formatting: Ruff clean (62 files formatted)
TypeScript:      0 errors (Strict Mode)
Frontend Build:  Production bundle generated successfully
======================================================================
```

---

## 2. Test Execution Commands

### Backend Verification (Python 3.12 / Pytest / Ruff)

```bash
# Run complete backend test suite
uv run --project backend pytest backend/tests/ -v

# Run code style and linting checks
uv run --project backend ruff check backend/

# Run code formatting check
uv run --project backend ruff format --check backend/
```

### Frontend Verification (React 18 / TypeScript / Vitest)

```bash
cd frontend

# Run frontend component & workspace tests
npm test -- --run

# Run strict TypeScript compiler verification
npm run typecheck

# Build production bundle
npm run build
```

### Benchmark Evaluation Runner

```bash
# Execute empirical benchmark evaluation with Wilson score intervals
uv run python scripts/evaluate.py
```
Outputs verified confusion matrix metrics to `data/accuracy/latest_evaluation.json`.

---

## 3. Test Categories & Architecture

### A. Backend Unit Tests (`backend/tests/unit/`) — 48 Tests
- `test_marker_check.py`: Tests exact Unicode zero-width matching, case-insensitivity, and bounded Levenshtein edit distance ($d \le 1$).
- `test_marker_gen.py`: Validates entropy, collision resistance, and zero-width sequence encoding.
- `test_similarity.py`: Verifies TF-IDF lexical cosine similarity and peer-group percentile ranking.
- `test_duplicates.py`: Tests exact token matching and token 3-gram Jaccard similarity across worker accounts.
- `test_speed.py`: Validates typing velocity computation (>15 chars/sec anomaly flagging) and missing metadata resilience.
- `test_confidence.py`: Tests deterministic evidence synthesis logic and required limitation notes.
- `test_calibration.py`: Tests exact mathematical calculation of Wilson score 95% confidence intervals.
- `test_dataset.py`: Validates CSV/JSONL parsing, schema enforcement, column auto-detection, and row limit constraints.
- `test_reporting.py`: Tests standalone offline HTML and JSON report export formatting.
- `test_cleanup.py`: Verifies 7-day TTL cascading expiration and "Delete Now" purging.
- `test_ai_provider.py`: Validates mock AI provider interface and spending cap safeguards.
- `test_health.py`: Validates system health endpoints.

### B. Backend Security & Invariants Tests (`backend/tests/security/`) — 6 Tests
- `test_security_invariants.py`:
  - Formula Injection Protection: Confirms all dangerous prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) are sanitized with single-quote escaping in CSV exports.
  - Secret Token Hashing: Ensures tokens are never stored plaintext; verifies SHA-256 database digest storage.
  - Privacy Invariant: Verifies worker answers are never egressed to external AI without `consent_external_ai=true`.
  - Path Traversal Defense: Verifies uploaded filenames are strictly sanitized.

### C. Backend Integration Tests (`backend/tests/integration/`) — 9 Tests
- `test_dashboard.py`: Tests reviewer dashboard analytics aggregation across persisted audit records.
- `test_investigation.py`: Tests full reviewer adjudication workflow, side-by-side diff generation, and status updating.
- `test_quality.py`: Tests dataset hygiene and quality profile computation.
- `test_job.py`: Verifies durable background job state transitions (`queued` $\to$ `running` $\to$ `completed`).
- `test_eval.py`: Verifies end-to-end benchmark evaluation execution.

### D. Frontend Test Suites (`frontend/tests/`) — 20 Tests
- `Investigation.test.tsx` (4 tests): Verifies workspace rendering, tab navigation, side-by-side comparison modal, and adjudication workflows.
- `Quality.test.tsx` (4 tests): Tests dataset hygiene score displays, distributions, and CSV/JSON quality exports.
- `Dashboard.test.tsx` (3 tests): Tests dashboard metrics cards, activity charts, and audit table filtering.
- `Navigation.test.tsx` (8 tests): Tests top-level navigation, responsive menu, and footer links.
- `App.test.tsx` (1 test): Verifies application routing and layout rendering.
