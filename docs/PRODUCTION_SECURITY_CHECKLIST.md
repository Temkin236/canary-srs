# Canary SRS — Production Security & Privacy Checklist

This document details the security posture, privacy invariants, and verification steps for Canary SRS production deployments.

---

## 1. Core Philosophical Invariants Verification

| Invariant | Implementation Mechanism | Verification Test | Status |
| :--- | :--- | :--- | :---: |
| **1. Evidence, Not Verdict** | Every finding payload enforces `limitations` stating evidence is for human adjudication only and never proves cheating. | `test_invariant_1_evidence_not_verdict` | ✅ Verified |
| **2. No Automated Punishment** | Canary API contains zero endpoints for banning, penalizing, or withholding payment from workers. | Route inspection & API schema audit | ✅ Verified |
| **3. Ephemeral 7-Day Retention** | Automated cascading deletion expunges DB rows and storage files after 7 days (FR-42). | `test_cascading_retention_purge` | ✅ Verified |
| **4. Explicit AI Consent Guard** | External AI checks (e.g. Gemini) strictly reject execution unless `consent_external_ai == True`. | `test_external_ai_provider_strictly_blocks_without_consent` | ✅ Verified |
| **5. Zero Unhashed Secret Persistence** | Raw audit access tokens are generated with 256 bits of entropy and stored solely as SHA-256 digests. | `test_privacy_sha256_token_invariants` | ✅ Verified |
| **6. Deterministic Offline Capability** | Marker insertion, Levenshtein distance, duplicate Jaccard similarity, and speed checks run offline with zero cloud AI dependencies. | `test_invariant_6_deterministic_offline_capability` | ✅ Verified |

---

## 2. Infrastructure & Network Security

- [x] **Render Private Network Isolation**: PostgreSQL (`canary-postgres`) and Redis (`canary-redis`) are configured with empty `ipAllowList: []`, restricting all ingress traffic to Render internal private network.
- [x] **PostgreSQL TLS In-Transit Encryption**: All database connections require TLS in production via `sslmode=require` / managed connection string.
- [x] **Database Connection Pooling**: SQLAlchemy configured with `pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, and `pool_pre_ping=True` to prevent connection leaks and handle database failovers safely.
- [x] **Strict CORS Policy**: `ALLOWED_ORIGINS` restricts cross-origin resource sharing to the designated Vercel frontend domain. Supports both JSON and comma-delimited strings without crashing on startup.
- [x] **HTTP Security Headers on Vercel**: `frontend/vercel.json` applies:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`

---

## 3. Data Ingestion & Storage Protections

- [x] **Strict Upload Size Limits**: Uploads exceeding `MAX_UPLOAD_SIZE_BYTES` (10 MB default) are rejected with HTTP 413 prior to memory buffering.
- [x] **Batch Record Limit**: Datasets exceeding `MAX_RECORDS_COUNT` (10,000 rows default) are rejected with HTTP 400.
- [x] **Path Traversal Sanitization**: Uploaded filenames are sanitized via `sanitize_filename()` stripping `..`, `/`, and path separators before saving to disk.
- [x] **Spreadsheet Formula Injection Defense**: All exported CSV cells are sanitized using `sanitize_csv_field()`, prefixing dangerous leading characters (`=`, `+`, `-`, `@`, `\t`, `\r`) with single quotes (`'`) to protect reviewers opening exports in Excel or Google Sheets.

---

## 4. Authentication, Tokens & Access Control

- [x] **Zero-Knowledge Token Architecture**: The raw access token (e.g. `cnry_sec_...`) is returned exactly once in the response of `POST /api/v1/audits`.
- [x] **No Token Logging**: Logging configurations in `canary`, `canary-worker`, and `canary-cleanup` explicitly redact authorization tokens and audit secrets.
- [x] **Constant-Time Verification**: Secret tokens are verified against stored hashes using `secrets.compare_digest` in `verify_secret_token()` to eliminate timing attack vectors.
- [x] **Immediate Cascading Purge**: Any user with a valid access token can invoke `DELETE /api/v1/audits/{secret_token}` to instantly expunge all associated answers, findings, and disk files without delay.

---

## 5. Background Queue & Worker Resilience

- [x] **Production Fail-Closed Queue**: If Redis is unreachable in production (`ENVIRONMENT=production`), the application raises a `RuntimeError` rather than silently executing jobs on an ephemeral web instance.
- [x] **Redis Memory Safety**: Redis instance configured with `maxmemoryPolicy: noeviction` to ensure queued audit jobs and status keys are never dropped under memory pressure.
- [x] **Graceful Shutdown**: Worker catches `SIGINT` and `SIGTERM` signals to allow active task finalization before terminating.
- [x] **Job Timeout Protection**: All jobs enforce a hard 1200s (20 minute) timeout to prevent stuck workers from hanging indefinitely.

---

## 6. Pre-Launch Verification Checklist

Before taking Canary SRS live on your production domains:

1. [ ] **Render Blueprint Deployed**: Confirm all 5 services (`canary-postgres`, `canary-redis`, `canary-api`, `canary-worker`, `canary-retention-cleanup`) are green in Render Dashboard.
2. [ ] **Alembic Migrations Landed**: Verify `alembic_version` table is populated in PostgreSQL with revision `7d65e5339942`.
3. [ ] **Readiness Probe Verified**: Navigate to `https://<YOUR-RENDER-API>/health/ready` and ensure HTTP 200 with `{"status": "ready"}`.
4. [ ] **Vercel Deployed**: Verify Vercel frontend builds and loads cleanly at `https://<YOUR-VERCEL-DOMAIN>`.
5. [ ] **CORS Configured**: Confirm `ALLOWED_ORIGINS` on Render matches your exact Vercel HTTPS domain.
6. [ ] **End-to-End Test Audit**: Upload `backend/tests/fixtures/clean_dataset.csv` through the production web UI and confirm job executes through the background worker to completion.
7. [ ] **Immediate Purge Tested**: Click "Delete Now" on the completed audit and verify immediate expungement from the database.
