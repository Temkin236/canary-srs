# Deployment Guide — Canary SRS

## Deployment Architectures

### 1. Containerized Multi-Service Deployment (Docker Compose)
Suitable for single-node virtual servers (e.g. AWS EC2, DigitalOcean Droplet, Hetzner):
```bash
docker compose up -d --build
```
This runs:
- `backend`: FastAPI API service on port 8000.
- `worker`: Dedicated background processing process.
- `frontend`: Nginx serving built static React assets on port 3000.
- `db`: PostgreSQL 16 database.
- `redis`: Redis 7 job queue.

### 2. Cloud Native Split Deployment (Vercel + Render)
- **Frontend on Vercel**:
  - Build Command: `npm run build`
  - Output Directory: `dist`
  - Framework Preset: Vite
  - Environment Variable: `VITE_API_URL=https://your-backend.onrender.com`
- **Backend on Render**:
  - Environment: Python 3.12+
  - Build Command: `cd backend && uv pip install -e .`
  - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Attached PostgreSQL instance and Redis instance.
