# Requirements Traceability Matrix — Canary SRS

Authoritative mapping of Functional Requirements (FR-1 through FR-46) to implementation modules, routes, test suites, and acceptance test status.

| Req ID | Requirement Description | Implementation Module | API / UI Route | Test Suite | Status |
|---|---|---|---|---|---|
| **FR-1** | Accept CSV and JSONL dataset uploads | `backend/app/services/dataset.py` | `POST /api/v1/audits/validate` | `backend/tests/unit/test_dataset.py` | Passed |
| **FR-2** | Validate required fields (`task_id`, `prompt`, `worker_id`, `answer`) | `backend/app/services/dataset.py` | `POST /api/v1/audits/validate` | `backend/tests/unit/test_dataset.py` | Passed |
| **FR-3** | Support optional fields (`submitted_at`, `seconds_spent`) | `backend/app/services/dataset.py` | `POST /api/v1/audits/validate` | `backend/tests/unit/test_dataset.py` | Passed |
| **FR-4** | Enforce file size limit (10 MB) & row limit (10,000 answers) | `backend/app/services/dataset.py` | `POST /api/v1/audits` | `backend/tests/unit/test_dataset.py` | Passed |
| **FR-5** | Row-specific validation error reporting | `backend/app/services/dataset.py` | `POST /api/v1/audits/validate` | `backend/tests/unit/test_dataset.py` | Passed |
| **FR-6** | Drag-and-drop & file selection with data preview | `frontend/src/features/audit/UploadStep.tsx` | `/audit` | `frontend/tests/UploadStep.test.tsx` | Passed |
| **FR-7** | Column mapping interface for non-standard CSV headers | `frontend/src/features/audit/ColumnMapStep.tsx` | `/audit` | `frontend/tests/ColumnMap.test.tsx` | Passed |
| **FR-8** | Generate internal random UUID filenames (untrusted path defense) | `backend/app/services/storage.py` | `POST /api/v1/audits` | `backend/tests/security/test_security.py` | Passed |
| **FR-9** | Generate cryptographically random task-specific markers | `backend/app/services/marker_gen.py` | `POST /api/v1/prepare/markers` | `backend/tests/unit/test_marker_gen.py` | In Progress |
| **FR-10** | Provide editable task ID and prompt text with unique markers | `frontend/src/features/prepare/PrepareView.tsx` | `/prepare` | `frontend/tests/PrepareView.test.tsx` | In Progress |
| **FR-11** | Preview visible text vs model-received text | `frontend/src/features/prepare/PrepareView.tsx` | `/prepare` | `frontend/tests/PrepareView.test.tsx` | In Progress |
| **FR-12** | At least two marker hiding approaches (Zero-width, prompt embedded) | `backend/app/services/marker_gen.py` | `POST /api/v1/prepare/markers` | `backend/tests/unit/test_marker_gen.py` | In Progress |
| **FR-13** | Downloadable and importable marker manifest (format versioned) | `backend/app/services/marker_gen.py` | `POST /api/v1/prepare/export` | `backend/tests/unit/test_marker_gen.py` | In Progress |
| **FR-14** | Marker check runs 100% offline | `backend/app/checks/marker.py` | Background Engine | `backend/tests/unit/test_marker_check.py` | In Progress |
| **FR-15** | Marker exact matching and case-insensitive matching | `backend/app/checks/marker.py` | Background Engine | `backend/tests/unit/test_marker_check.py` | In Progress |
| **FR-16** | Marker whitespace normalization and bounded typo tolerance | `backend/app/checks/marker.py` | Background Engine | `backend/tests/unit/test_marker_check.py` | In Progress |
| **FR-17** | Provide context excerpts and character offsets for marker hits | `backend/app/checks/marker.py` | Background Engine | `backend/tests/unit/test_marker_check.py` | In Progress |
| **FR-18** | Reference answer generation support (up to 3 per provider) | `backend/app/services/ai_provider.py` | Background Engine | `backend/tests/unit/test_similarity.py` | In Progress |
| **FR-19** | Lexical TF-IDF cosine similarity comparison | `backend/app/checks/similarity.py` | Background Engine | `backend/tests/unit/test_similarity.py` | In Progress |
| **FR-20** | Semantic embedding similarity comparison | `backend/app/checks/similarity.py` | Background Engine | `backend/tests/unit/test_similarity.py` | In Progress |
| **FR-21** | Peer-answer group distribution and percentile ranking | `backend/app/checks/similarity.py` | Background Engine | `backend/tests/unit/test_similarity.py` | In Progress |
| **FR-22** | Guard against misleading percentiles in small peer groups (<5 answers) | `backend/app/checks/similarity.py` | Background Engine | `backend/tests/unit/test_similarity.py` | In Progress |
| **FR-23** | Normalized exact duplicate answer detection across workers | `backend/app/checks/duplicates.py` | Background Engine | `backend/tests/unit/test_duplicates.py` | In Progress |
| **FR-24** | Explainable near-duplicate detection across workers | `backend/app/checks/duplicates.py` | Background Engine | `backend/tests/unit/test_duplicates.py` | In Progress |
| **FR-25** | Efficient candidate generation for near-duplicates (up to 10k items) | `backend/app/checks/duplicates.py` | Background Engine | `backend/tests/unit/test_duplicates.py` | In Progress |
| **FR-26** | Grouping of duplicate clusters with matching phrase excerpts | `backend/app/checks/duplicates.py` | Background Engine | `backend/tests/unit/test_duplicates.py` | In Progress |
| **FR-27** | Speed plausibility check based on typing velocity threshold | `backend/app/checks/speed.py` | Background Engine | `backend/tests/unit/test_speed.py` | In Progress |
| **FR-28** | Skip speed analysis gracefully when timing data is missing | `backend/app/checks/speed.py` | Background Engine | `backend/tests/unit/test_speed.py` | In Progress |
| **FR-29** | Unified deterministic evidence confidence rules (High, Medium, Low) | `backend/app/checks/base.py` | Background Engine | `backend/tests/unit/test_confidence.py` | In Progress |
| **FR-30** | Prominent limitation notices: "Evidence for review, not proof" | `frontend/src/features/results/ResultSummary.tsx`| `/results/:secret` | `frontend/tests/ResultSummary.test.tsx`| In Progress |
| **FR-31** | Durable database-backed audit job lifecycle states | `backend/app/models/audit.py` | `GET /api/v1/audits/{secret}/status`| `backend/tests/integration/test_job.py` | In Progress |
| **FR-32** | Asynchronous worker process with Redis and In-Memory fallback | `backend/app/jobs/` | Worker | `backend/tests/integration/test_job.py` | In Progress |
| **FR-33** | Bounded retries, backoff, and 20-minute execution timeout | `backend/app/jobs/runner.py` | Worker | `backend/tests/integration/test_job.py` | In Progress |
| **FR-34** | Idempotent stage execution and partial result preservation | `backend/app/jobs/runner.py` | Worker | `backend/tests/integration/test_job.py` | In Progress |
| **FR-35** | Secret URL generation with 256-bit cryptographic entropy | `backend/app/core/security.py` | `POST /api/v1/audits` | `backend/tests/security/test_security.py` | In Progress |
| **FR-36** | Store only SHA-256 hash of audit secret tokens in database | `backend/app/models/audit.py` | `POST /api/v1/audits` | `backend/tests/security/test_security.py` | In Progress |
| **FR-37** | Audit results UI with summary cards, worker filters, and findings | `frontend/src/features/results/` | `/results/:secret` | `frontend/tests/ResultsView.test.tsx` | In Progress |
| **FR-38** | Self-contained offline HTML report generation (inline CSS) | `backend/app/reporting/html_export.py` | `GET /api/v1/audits/{secret}/export.html`| `backend/tests/unit/test_reporting.py` | In Progress |
| **FR-39** | Formula-injection protected CSV export | `backend/app/reporting/csv_export.py` | `GET /api/v1/audits/{secret}/export.csv`| `backend/tests/security/test_security.py` | In Progress |
| **FR-40** | Machine-readable JSON export of findings and metadata | `backend/app/reporting/json_export.py`| `GET /api/v1/audits/{secret}/export.json`| `backend/tests/unit/test_reporting.py` | In Progress |
| **FR-41** | "Delete Now" action cascading immediate purge of audit data | `backend/app/services/audit.py` | `DELETE /api/v1/audits/{secret}` | `backend/tests/unit/test_audit_delete.py`| In Progress |
| **FR-42** | Automatic 7-day data retention cleanup job | `backend/app/jobs/cleanup.py` | Cron / Worker | `backend/tests/unit/test_cleanup.py` | In Progress |
| **FR-43** | Human-labeled baseline sample calibration with Wilson interval | `backend/app/services/calibration.py` | `POST /api/v1/audits` | `backend/tests/unit/test_calibration.py` | In Progress |
| **FR-44** | Reproducible evaluation CLI script (`scripts/evaluate.py`) | `scripts/evaluate.py` | CLI Command | `backend/tests/integration/test_eval.py` | In Progress |
| **FR-45** | Real measured Accuracy page loading latest evaluation artifact | `frontend/src/pages/AccuracyPage.tsx` | `/accuracy` | `frontend/tests/AccuracyPage.test.tsx` | In Progress |
| **FR-46** | Full website navigation: Home, How it works, Prepare, Audit, Accuracy, Privacy, Terms, Contact | `frontend/src/pages/` | All Routes | `frontend/tests/Navigation.test.tsx` | In Progress |
