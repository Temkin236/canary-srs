# Canary SRS — Application Screenshot Inventory

This directory documents the authentic screenshots captured from the running **Canary SRS** full-stack application (frontend on port 5173, FastAPI backend on port 8000).

All screenshots were captured at a standard desktop viewport resolution (**1440 × 1000 px**) using headless Chromium automation directly against the active development build. No AI mockups or stock graphics are used.

---

## Screenshot Catalog

| File | Route | Description |
|---|---|---|
| [`01-landing-page.png`](screenshots/01-landing-page.png) | `/` | **Landing Page & Philosophy**: Clean editorial presentation of the Canary SRS mission ("Evidence, Not Verdict"), core philosophical invariants, and quick navigation. |
| [`02-task-preparation.png`](screenshots/02-task-preparation.png) | `/prepare` | **Task Preparation & Marker Seeding**: Interface to generate cryptographically unique canary tokens and seed prompts with zero-width Unicode sequences or subtle instruction footnotes. |
| [`03-dataset-audit.png`](screenshots/03-dataset-audit.png) | `/audit` | **Dataset Ingestion & Audit Launch**: File upload (CSV/JSONL), column mapping, and explicit privacy opt-in controls (`consent_external_ai`). |
| [`04-audit-results.png`](screenshots/04-audit-results.png) | `/results/:secret` | **Audit Results & Export Portal**: Token-protected audit progress, summary statistics, multi-format report exports (Standalone HTML, sanitized CSV, JSON), and instant cascading purge. |
| [`05-reviewer-dashboard.png`](screenshots/05-reviewer-dashboard.png) | `/dashboard` | **Reviewer Workspace & Analytics**: Centralized steward dashboard displaying cross-audit metrics, finding activity over time, detection check distributions, and audit status table. |
| [`06-evidence-investigation.png`](screenshots/06-evidence-investigation.png) | `/audits/:auditId` | **Evidence Adjudication Workspace**: Comprehensive human-review workspace with finding filters, evidence offsets, reviewer notes, status adjudication, and side-by-side comparison. |
| [`07-accuracy-benchmark.png`](screenshots/07-accuracy-benchmark.png) | `/accuracy` | **Empirical Benchmark Evaluation**: Real measured benchmark accuracy displaying True Positive Rate (100.0%) and False Positive Rate (0.0%) with exact Wilson score 95% confidence intervals. |
| [`08-how-it-works.png`](screenshots/08-how-it-works.png) | `/how-it-works` | **Methodology & Architecture**: Technical walkthrough of the 4 deterministic detection checks and reviewer guidelines. |
| [`09-privacy.png`](screenshots/09-privacy.png) | `/privacy` | **Privacy Guarantees**: Detailed documentation of SHA-256 token hashing, 7-day retention TTL, and zero third-party data transmission policies. |
| [`10-api-documentation.png`](screenshots/10-api-documentation.png) | `http://localhost:8000/docs` | **Interactive OpenAPI (Swagger) Specification**: Auto-generated REST API documentation exposing all endpoints, schemas, and security schemes. |
| [`11-dataset-quality.png`](screenshots/11-dataset-quality.png) | `/audits/:auditId?tab=quality` | **Dataset Quality & Hygiene Profile**: Completeness scoring, worker participation distributions, answer length histograms, and formatting hygiene alerts. |

---

## Technical Capture Details
- **Capture Date**: November 2026
- **Viewport Dimension**: 1440 × 1000 px
- **Automation Engine**: Chromium Headless (`--virtual-time-budget=4000 --disable-gpu`)
- **Backend**: FastAPI 0.115+ / Python 3.12 (`http://127.0.0.1:8000`)
- **Frontend**: React 18 / TypeScript / Vite (`http://127.0.0.1:5173`)
- **Database Fixture**: Seeded development database with representative multi-modal findings (`canary-audit-demo-8492`).
