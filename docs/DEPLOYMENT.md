# Deployment & Operations Guide — Canary SRS

This document provides complete instructions for deploying Canary SRS in local development, containerized production environments, and cloud infrastructure.

---

## 1. Environment Configuration

Copy `.env.example` to `.env` in the project root:

```ini
# Core Environment
ENVIRONMENT=production
DEBUG=false
APP_NAME="Canary SRS"
APP_VERSION=0.1.0

# Server Bindings
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=https://canary.example.com
ALLOWED_ORIGINS=["https://canary.example.com"]

# Database & Queue
# For SQLite (Local dev): sqlite:///./canary.db
# For PostgreSQL (Production): postgresql://user:password@postgres:5432/canary
DATABASE_URL=postgresql://canary:secret_pass@localhost:5432/canary_prod
REDIS_URL=redis://localhost:6379/0
USE_IN_MEMORY_QUEUE=false

# Storage & Privacy
STORAGE_PATH=/var/data/canary/storage
MAX_UPLOAD_SIZE_BYTES=10485760   # 10 MB limit
MAX_RECORDS_COUNT=10000          # 10,000 row batch limit
DEFAULT_RETENTION_DAYS=7

# Security Keys
SECRET_KEY="generate-a-strong-random-32-byte-hex-string"
AI_SPENDING_CAP_PER_AUDIT_USD=5.00

# Optional External AI Provider (Requires explicit user consent in UI)
GEMINI_API_KEY=""
```

---

## 2. Deployment Architectures

### Architecture A: Containerized Production (`docker-compose.yml`)
The recommended single-server deployment topology utilizes Docker Compose:

```bash
# Build and run all microservices in the background
docker compose up -d --build
```

**Services Launched:**
- `backend`: FastAPI API application running on port `8000`.
- `worker`: Standalone RQ background execution worker consuming from Redis.
- `frontend`: High-performance Nginx web server serving compiled React 18 production bundle on port `3000`.
- `postgres`: PostgreSQL 16 relational database with persistent volume.
- `redis`: Redis 7 Alpine cache and job queue broker.

### Architecture B: Local Developer Mode (`make dev`)
For zero-dependency local development with SQLite and in-memory queue fallback:

```bash
# 1. Setup backend and frontend dependencies
make setup

# 2. Concurrently start FastAPI (port 8000) and Vite React (port 5173)
make dev
```

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000/api/v1`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`

---

## 3. Database Initialization & Schema Migrations

Canary uses SQLAlchemy 2.0 with automated table declaration:

```bash
# Initialize database tables
cd backend
.venv/bin/python -c "from app.db.session import Base, engine; Base.metadata.create_all(bind=engine)"
```

When switching from SQLite to PostgreSQL, ensure the target database exists:
```sql
CREATE DATABASE canary_prod;
```

---

## 4. Ephemeral Retention Cleanup Daemon

To enforce the **7-day ephemeral retention policy** (Invariant 3), schedule a recurring cron job executing `scripts/cleanup.py` every hour:

```bash
# Crontab entry: Run hourly cleanup
0 * * * * cd /opt/canary && ./backend/.venv/bin/python scripts/cleanup.py >> /var/log/canary_cleanup.log 2>&1
```

---

## 5. Deployment Verification Checklist

Verify your deployment with the following health checks:

1. **System Health Check**:
   ```bash
   curl -f http://localhost:8000/api/v1/health
   # Expected response: {"status":"ok","version":"0.1.0","database":"healthy","queue":"healthy","environment":"production"}
   ```
2. **OpenAPI Docs Availability**:
   Visit `http://localhost:8000/docs` to inspect active endpoint definitions.
3. **Frontend Bundle Delivery**:
   Ensure `curl -I http://localhost:3000` returns `HTTP/1.1 200 OK` with proper MIME types.
4. **CORS Headers**:
   Verify `Access-Control-Allow-Origin` matches your configured `FRONTEND_URL`.
