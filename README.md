# Canary SRS — Contamination Audit for Human-Written Datasets

[![CI](https://github.com/Temkin236/canary-srs/actions/workflows/ci.yml/badge.svg)](https://github.com/Temkin236/canary-srs/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![React: 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)

> **Evidence, Not Proof.**
> Canary finds evidence that human-written dataset answers may have been contaminated by chatbot output. It is an evidence collection and human-review tool, not an automated authorship judge or worker punishment mechanism.

---

## Overview

Canary helps dataset stewards, crowd platforms, and machine learning researchers audit crowd-annotated datasets for potential Large Language Model (LLM) contamination through four multi-modal detection checks:

1. **Hidden Task-Specific Marker Detection**: Seeding cryptographically unique canary tokens in task prompts (via zero-width Unicode sequences or subtle instruction footnotes). If a worker pastes the prompt into a chatbot, the LLM echoes the marker into the response.
2. **AI Model Reference Similarity & Peer Distribution**: Compares submissions to reference model answers (e.g. Gemini) contextualized by the peer-answer similarity distribution within each task. Flags top percentiles when combined with peer duplication.
3. **Cross-Worker Duplicate Detection**: Discovers identical and near-duplicate answers submitted by different workers for the same task using MinHash and token n-gram Jaccard clustering.
4. **Typing Velocity & Speed Plausibility (Optional)**: Analyzes characters per second when submission timing metadata is available, flagging implausibly fast completions (>15 chars/sec).

---

## Core Principles & Guarantees

- **No Automated Penalties**: Canary findings are structured evidence for human review. Canary never automatically bans workers or withholds payments.
- **Privacy & Explicit AI Consent**: Worker answers are never sent to external AI providers without explicit reviewer consent (`consent_external_ai=true`).
- **100% Offline Capability**: Marker detection, duplicate detection, and lexical similarity operate completely offline without external network dependencies.
- **7-Day Ephemeral Retention**: All uploaded datasets, findings, and temporary storage files are automatically purged after 7 days, with an instantaneous "Delete Now" action available on every report.
- **Formula Injection Protection**: CSV exports automatically neutralize leading formula prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) against spreadsheet macro execution.

---

## Architecture & Monorepo Structure

```
canary-srs/
├── AGENTS.md                  # Development guidelines & architectural invariants
├── README.md                  # Project overview and quick start
├── CONTRIBUTING.md            # Contribution workflow and coding standards
├── SECURITY.md                # Security policy, threat model, and disclosure
├── docker-compose.yml         # Containerized production stack (FastAPI, Redis, Postgres, Nginx)
├── Makefile                   # Developer task automation
├── docs/                      # Authoritative technical documentation
│   ├── ARCHITECTURE.md        # Architectural layers & diagrams
│   ├── API.md                 # REST API specification
│   ├── DECISIONS.md           # Architecture Decision Records (ADRs)
│   ├── REQUIREMENTS_TRACEABILITY.md # FR-1 through FR-46 mapping
│   ├── SECURITY_CHECKLIST.md  # Threat model & vulnerability mitigations
│   ├── PRIVACY.md             # Data retention policy
│   ├── METHODOLOGY.md         # Mathematical models & detection algorithms
│   ├── TEST_DATA.md           # Dataset schemas & synthetic benchmarks
│   ├── TESTING.md             # Verification guide
│   └── DEPLOYMENT.md          # Production deployment guide
├── frontend/                  # React 18, TypeScript (strict), Vite, Tailwind CSS
└── backend/                   # Python 3.12, FastAPI, SQLAlchemy, scikit-learn, RQ
```

---

## Quick Start (Local Development)

### Prerequisites
- Node.js 20+ and npm
- Python 3.12+ (or `uv` / `mise`)

### 1. Clone & Configure
```bash
git clone https://github.com/Temkin236/canary-srs.git
cd canary-srs
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload --port 8000
```
Backend API will be active at `http://localhost:8000`. Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run test
npm run dev
```
Frontend application will be active at `http://localhost:5173`.

---

## Running Full Verification Suite
```bash
# Run all backend tests and linting
cd backend
.venv/bin/ruff check .
.venv/bin/pytest tests/

# Run all frontend tests and production build
cd ../frontend
npm run test
npm run typecheck
npm run build
```
