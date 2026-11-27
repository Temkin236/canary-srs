# Release Notes: Canary SRS v0.2.0

**Release Title**: Canary SRS — Production Deployment & Cloud Architecture  
**Tag**: `v0.2.0`  
**Date**: November 27, 2026  
**Maintainer**: Temkin Abdulmelik ([@Temkin236](https://github.com/Temkin236))

---

## Highlights

Canary SRS v0.2.0 introduces official cloud deployment blueprints and production-readiness architecture for **Render** (FastAPI, PostgreSQL 16, Redis, RQ Worker, Cron) and **Vercel** (React SPA).

This release formalizes the production infrastructure specifications, database migrations, fail-closed queue safety, and container orchestration probes while preserving all 46 core functional requirements and privacy invariants.

> **Core Philosophy**: *"Evidence, Not Verdict."* Canary produces calibrated, transparent artifacts for human review. It is never an automated authorship judge or worker punishment mechanism.

---

## What's Included in v0.2.0

### 1. Cloud Production Infrastructure (Render Blueprint)
- **Declarative Blueprint (`render.yaml`)**:
  - `canary-api`: High-performance FastAPI web service with automated pre-deploy migration execution (`uv run alembic upgrade head`) and `/health/ready` probe.
  - `canary-postgres`: Managed PostgreSQL 16 database on private network.
  - `canary-redis`: Managed Redis Key-Value queue service on private network.
  - `canary-worker`: Dedicated RQ background worker executing contamination detection jobs.
  - `canary-retention-cleanup`: Scheduled daily cron job (03:00 UTC) executing 7-day ephemeral retention purge (`scripts/cleanup.py`).

### 2. Database Migrations & PostgreSQL Compatibility
- **Alembic Migration Suite**:
  - Initial migration `7d65e5339942_initial_canary_schema.py` mapping all 9 relational tables, foreign key constraints, indexes, and cascading deletion.
  - Dynamic `DATABASE_URL` resolution with automatic `postgres://` to `postgresql://` URI normalization.
  - Production PostgreSQL connection pooling (`pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True`).

### 3. Background Processing & Fail-Closed Safety
- **Dedicated Worker Service (`backend/app/worker.py`)**:
  - Listens on `canary-audits` queue with startup connection retry and exponential backoff.
  - Graceful signal handling (`SIGTERM`, `SIGINT`) for zero dropped jobs during deploys.
- **Fail-Closed Production Safety**:
  - In production mode (`ENVIRONMENT=production`), queue failure raises an explicit `RuntimeError` instead of silently falling back to in-memory processing.
- **Idempotency Guard**:
  - Protects against duplicate audit execution on already-completed jobs.

### 4. Container Probes & Security Hardening
- **Container Health Probes**:
  - `/health/live`: Liveness probe for process uptime.
  - `/health/ready`: Readiness probe verifying live database connectivity.
- **Constant-Time Verification**:
  - `verify_secret_token()` utilizes `hmac.compare_digest` to defend against timing attacks on SHA-256 tokens.
- **Vercel Frontend Hardening (`frontend/vercel.json`)**:
  - SPA catch-all rewrites (`/(.*) -> /index.html`).
  - Strict security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`).
  - Dynamic API routing helper (`frontend/src/services/api.ts`) supporting `VITE_API_BASE_URL`.

### 5. Automated Verification & Quality Assurance
- **98 Passing Automated Tests**:
  - 78 backend pytest tests (including 8 production readiness integration tests).
  - 20 frontend Vitest component & navigation tests.
  - 100% test pass rate.
- **Strict Linting & Type Safety**:
  - TypeScript strict mode: 0 errors (`tsc --noEmit`).
  - Ruff check & format: 100% clean across all 67 backend Python files.
  - Production frontend build: compiled cleanly.

---

## Production Deployment Checklist
1. Connect GitHub repository to Render: Blueprint deploys `canary-api`, `canary-postgres`, `canary-redis`, `canary-worker`, and `canary-retention-cleanup`.
2. Connect frontend repository to Vercel: Set Root Directory to `frontend` and configure `VITE_API_BASE_URL` to the Render API URL.
3. Update `ALLOWED_ORIGINS` in Render to match the Vercel frontend URL.
4. Verify `/health/ready` returns `{"status": "ready", "database": "healthy", "queue": "healthy"}`.
