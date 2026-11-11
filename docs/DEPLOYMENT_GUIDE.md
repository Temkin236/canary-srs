# Canary SRS — Production Deployment Guide

This guide details the complete production deployment architecture, step-by-step instructions, and operational procedures for deploying **Canary SRS** across **Vercel** (Frontend) and **Render** (FastAPI Backend, PostgreSQL, Redis, Background Worker, and Retention Cron).

---

## 1. Target Infrastructure Architecture

```
                                  ┌───────────────────────────────┐
                                  │         Vercel (Edge)         │
                                  │   Compiled React 18 SPA UI    │
                                  │      canary-srs.vercel.app    │
                                  └───────────────┬───────────────┘
                                                  │ HTTPS
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │       Render Web Service      │
                                  │       canary-api (FastAPI)    │
                                  │      /health/ready, /api/v1   │
                                  └───────┬───────────────┬───────┘
                                          │               │
                 SQLAlchemy Connection    │               │  RQ Enqueue
                 Pool (10+20, TLS)        ▼               ▼  Timeout: 1200s
               ┌─────────────────────────────┐  ┌─────────────────────────────┐
               │      Render PostgreSQL      │  │      Render Key Value       │
               │       canary-postgres       │  │        canary-redis         │
               │  9 tables, indexes, cascade │  │  noeviction, private TLS    │
               └──────────────┬──────────────┘  └──────────────┬──────────────┘
                              ▲                                │
                              │ Read / Write Results           │ Dequeue Job
                              │                                ▼
               ┌──────────────┴──────────────┐  ┌─────────────────────────────┐
               │    Render Cron Service      │  │  Render Background Worker   │
               │   canary-retention-cleanup  │  │        canary-worker        │
               │   Daily @ 03:00 UTC (FR-42) │  │    python -m app.worker     │
               └─────────────────────────────┘  └─────────────────────────────┘
```

| Component | Provider / Service | Configuration |
| :--- | :--- | :--- |
| **Frontend** | Vercel | Single-Page Application (SPA) with rewrite rules (`vercel.json`), zero hardcoded backend references. |
| **API Server** | Render Web Service | Python 3.12, Uvicorn ASGI server, connection pooling, readiness probe `/health/ready`. |
| **Database** | Render PostgreSQL | Managed PostgreSQL 16 with TLS, automated Alembic migrations on pre-deploy. |
| **Job Queue** | Render Key Value | Redis 7 compatible broker with `noeviction` memory policy. |
| **Worker Engine** | Render Background Worker | Dedicated worker running `python -m app.worker` listening on `canary-audits`. |
| **Retention Purge** | Render Cron Job | Daily scheduled task running `python scripts/cleanup.py` expunging audits older than 7 days. |

---

## 2. Infrastructure as Code: `render.yaml`

Canary includes a turnkey Render Blueprint (`render.yaml`) declaring all backend resources, dependencies, and private network bindings:

```yaml
version: "1"

databases:
  - name: canary-postgres
    databaseName: canary
    user: canary_user
    plan: starter
    region: oregon
    ipAllowList: [] # Private network only

services:
  - type: redis
    name: canary-redis
    plan: starter
    region: oregon
    maxmemoryPolicy: noeviction
    ipAllowList: []

  - type: web
    name: canary-api
    runtime: python
    rootDir: backend
    plan: starter
    region: oregon
    buildCommand: pip install uv && uv sync --frozen
    preDeployCommand: uv run alembic upgrade head
    startCommand: uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health/ready

  - type: worker
    name: canary-worker
    runtime: python
    rootDir: backend
    plan: starter
    region: oregon
    buildCommand: pip install uv && uv sync --frozen
    startCommand: uv run python -m app.worker

  - type: cron
    name: canary-retention-cleanup
    runtime: python
    rootDir: backend
    schedule: "0 3 * * *"
    plan: starter
    region: oregon
    buildCommand: pip install uv && uv sync --frozen
    startCommand: uv run python scripts/cleanup.py
```

---

## 3. Step-by-Step Deployment Instructions

### Step 3.1: Deploy Backend Stack to Render via Blueprint

> **Manual Action Required**: This step requires signing into your Render account.

1. Navigate to the [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Blueprint**.
3. Connect your GitHub repository: `https://github.com/Temkin236/canary-srs`.
4. Render will detect the `render.yaml` blueprint file at the repository root.
5. In the configuration overview, review the 5 declared resources:
   - `canary-postgres` (Database)
   - `canary-redis` (Key-Value)
   - `canary-api` (Web Service)
   - `canary-worker` (Background Worker)
   - `canary-retention-cleanup` (Cron Job)
6. Click **Apply**. Render will automatically provision PostgreSQL and Redis, run the Alembic migrations (`alembic upgrade head`), and boot the API and worker.
7. Once deployed, note down your public API URL (e.g. `https://canary-api.onrender.com`).

### Step 3.2: Configure Render Environment Variables

In your Render dashboard for `canary-api`:
- **`ALLOWED_ORIGINS`**: Set to your Vercel deployment URL (e.g. `https://canary-srs.vercel.app,https://canary.yourdomain.com`).
- **`FRONTEND_URL`**: Set to your production frontend URL (e.g. `https://canary-srs.vercel.app`).
- **`SECRET_KEY`**: Automatically populated with a cryptographically secure random token by Render Blueprint.

### Step 3.3: Deploy Frontend to Vercel

> **Manual Action Required**: This step requires signing into your Vercel account.

1. Navigate to the [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** > **Project**.
3. Import your repository: `Temkin236/canary-srs`.
4. Configure Project Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. In the **Environment Variables** section, add:
   - `VITE_API_BASE_URL`: The HTTPS URL of your Render API service (e.g. `https://canary-api.onrender.com`).
6. Click **Deploy**. Vercel will build the SPA and deploy it globally.
7. Test the deployment by loading your Vercel URL. Check the browser console to confirm zero CORS errors.

---

## 4. Production Database Migrations & Safety

### Automated Pre-Deploy Migrations
Render automatically executes Alembic migrations prior to serving traffic via:
```bash
uv run alembic upgrade head
```

### Safe Manual Migration Procedure
If applying a new schema change manually:
```bash
cd backend
export DATABASE_URL="postgresql://canary_user:<PASSWORD>@<HOST>/canary"

# 1. Inspect current migration state
uv run alembic current

# 2. View pending SQL statements without applying them (dry run)
uv run alembic upgrade head --sql

# 3. Apply migrations transactionally
uv run alembic upgrade head

# 4. Verify new head
uv run alembic heads
```

### Invariant & Rollback Safety:
- Migrations never issue `DROP TABLE` on production data.
- Column additions must be nullable or provide server-side defaults.
- All indexes use `IF NOT EXISTS` or standard idempotent definitions.
- If a migration fails, the pre-deploy command halts deployment, leaving the prior stable container running.

---

## 5. Background Worker & Queue Management

### Process Separation:
- **API Web Service (`canary-api`)**: Handles request validation, dataset ingestion, and job queuing (`q.enqueue`). Never executes heavy ML or similarity computations synchronously.
- **Worker (`canary-worker`)**: Dedicated container running `python -m app.worker`. Consumes from queue `canary-audits`.
- **Fail-Closed Queue Safety**: In production mode (`ENVIRONMENT=production`), Canary strictly raises a `RuntimeError` if Redis is unreachable rather than silently falling back to an in-memory queue that would be lost on container cycling.

### Job Lifecycle & Observability:
- Audit jobs run with a **1200-second (20 minute) timeout** (FR-33).
- Completed job records persist for 24 hours (`result_ttl=86400`).
- Failed job traceback records persist for 7 days (`failure_ttl=604800`) for human inspection without holding raw private worker responses.
- Idempotency guard: If an audit already has `status == "completed"`, re-triggering skips recomputation.

---

## 6. Seven-Day Ephemeral Retention Daemon (FR-42)

Canary adheres to **Invariant 3**: private worker answers must never be retained perpetually.

### Scheduled Execution:
- Defined in `render.yaml` as `canary-retention-cleanup`.
- Schedule: `0 3 * * *` (Daily at 03:00 UTC).
- Command: `uv run python scripts/cleanup.py`.

### Execution Logic:
1. Queries all audits where `expires_at <= NOW()` (defaulting to 7 days post-creation).
2. Executes cascading database deletion across:
   - `audit_answers`
   - `findings`
   - `finding_review_history`
   - `markers`
   - `check_results`
   - `job_states`
   - `calibration_runs`
   - `reference_answers`
3. Expunges uploaded raw dataset files and cached artifacts from persistent disk storage.
4. Logs the exact number of purged records without exposing worker IDs or private content.

### Immediate On-Demand Purge:
Reviewers can trigger an immediate cascading deletion at any point by clicking **"Delete Now"** or issuing:
```http
DELETE /api/v1/audits/{secret_token}
```
This triggers the identical cascading purge synchronously.

---

## 7. Health Probes & Readiness Endpoints

Canary exposes dedicated liveness and readiness probes:

| Endpoint | Purpose | Checks Performed | Expected Response |
| :--- | :--- | :--- | :--- |
| `GET /health/live` | Container Liveness | Process is responding to HTTP | `200 OK: {"status": "alive"}` |
| `GET /health/ready` | Orchestrator Readiness | DB connectivity (`SELECT 1`) + Redis ping | `200 OK: {"status": "ready"}` or `503 Unavailable` |
| `GET /api/v1/health` | Application Telemetry | Database, queue, version, and environment status | `200 OK: HealthResponse` |

Render's Web Service is configured with `healthCheckPath: /health/ready`, preventing traffic routing until both PostgreSQL and Redis are ready.
