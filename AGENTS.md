# AGENTS.md — Contributor & Agent Guidelines for Canary SRS

## Project Overview
**Canary SRS** (Contamination Audit for Human-Written Datasets) is an evidence collection and human-review platform designed to help dataset stewards investigate possible chatbot contamination in human-written crowd or vendor datasets.

## Core Philosophical Invariants
1. **Evidence, Not Verdict**: Canary never claims a finding proves AI authorship, fraud, or cheating. Findings must be labeled as evidence for human review with explicit limitations.
2. **No Automated Punishment**: Canary must never automatically reject, ban, or recommend withholding payment from a worker.
3. **No Stylometric Hallucination**: Canary does not infer AI authorship based on subjective "writing style" or uncalibrated perplexity metrics.
4. **Data Privacy & Explicit AI Consent**: Worker answers must never be sent to external AI providers (e.g. Gemini, OpenAI) without explicit user opt-in and consent.
5. **No Secret Leakage**: API keys, audit tokens, and raw private answers must never be committed to Git, logged, or exposed in error traces or URLs.
6. **Deterministic Offline Capability**: Marker detection, duplicate detection, and lexical similarity operate completely offline without external AI services.

## Engineering Standards
- **Monorepo Structure**: Frontend in `frontend/`, Backend in `backend/`, Docs in `docs/`, Scripts in `scripts/`.
- **Frontend Stack**: React, TypeScript (strict mode), Vite, Tailwind CSS, React Router, Vitest + Testing Library.
- **Backend Stack**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, SQLite (dev) / PostgreSQL (prod), pytest, Ruff.
- **Queue/Worker**: Redis + RQ with durable DB job states, plus an in-memory queue fallback for offline local execution without Redis.
- **Code Style & Linting**: Ruff for Python linting and formatting; ESLint & TypeScript compiler for frontend.
- **Testing**: Every functional requirement (FR-1 through FR-46) must be accompanied by unit, integration, or security tests.
- **Git Protocol**: Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `ci:`). No direct pushes to main; feature branches and PRs only.
