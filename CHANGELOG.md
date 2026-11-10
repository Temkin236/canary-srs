# Changelog

All notable changes to **Canary SRS** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-11-10

### Added
- **Full-Stack Monorepo Architecture**:
  - FastAPI backend (Python 3.12+) with Pydantic v2 schemas and SQLAlchemy 2.0 ORM.
  - React 18 frontend with TypeScript strict mode, Tailwind CSS, Vite, and Lucide icons.
  - Dual-mode execution engine supporting Redis + RQ background workers and synchronous in-memory fallback.
- **Deterministic Contamination Detection Engine (100% Offline Capable)**:
  - *Hidden Canary Marker Detection (Check 1)*: Invisible zero-width Unicode injection (`\u200b`, `\u200c`, `\u200d`) and subtle instruction footnotes with exact and bounded Levenshtein edit-distance matching.
  - *AI Reference & Peer Similarity Distribution (Check 2)*: Lexical TF-IDF cosine similarity against reference models, contextualized by empirical peer percentiles within each task.
  - *Cross-Worker Duplicate Clustering (Check 3)*: Exact token hashing and 3-gram Jaccard similarity across worker accounts.
  - *Typing Velocity Plausibility (Check 4)*: Typing speed anomaly detection (>15 chars/sec) based on worker submission timestamps.
- **Enterprise Reviewer Dashboard (`/dashboard`)**:
  - Centralized aggregate analytics across historical audits and findings.
  - 14-day daily audit volume and findings activity histograms.
  - Finding distribution breakdown by check category.
  - Dataset size distribution categorization (<100, 100-500, 500-2k, 2k-10k).
  - Searchable, status-filtered audit table with direct deep-links to investigation workspaces.
- **Evidence Adjudication Workspace (`/audits/:auditId`)**:
  - Detailed finding table with multi-factor filters (confidence, check category, adjudication status, worker/task query).
  - Inline evidence snippets with offset highlighting.
  - Side-by-side diff comparison modal between worker submissions, reference texts, and peer duplicates.
  - Human review adjudication workflow with status progression (`under_review`, `needs_investigation`, `reviewed`, `dismissed`) and reviewer notes.
  - Audit investigation history tracking.
- **Dataset Quality & Hygiene Profiling (`/audits/:auditId?tab=quality`)**:
  - Dataset completeness scoring weighted by valid text, worker IDs, and timestamps.
  - Worker participation distribution histograms and answer length distribution charts.
  - Formatting hygiene alerts (empty rows, duplicate task IDs, missing timestamps).
  - Dedicated CSV and JSON quality report exports with formula injection protection.
- **Task Preparation Engine (`/prepare`)**:
  - Automated canary marker generation and injection for prompt datasets.
  - Dual hiding strategies: invisible zero-width Unicode sequences and subtle instruction footnotes.
  - Downloadable marker manifest JSON and instrumented prompt dataset CSV.
- **Privacy & Security Invariants**:
  - One-way **SHA-256 token hashing** for audit access secrets (256-bit entropy).
  - Automated **7-day ephemeral retention** lifecycle with cascading deletion (`scripts/cleanup.py`).
  - Instant on-demand **"Delete Now"** cascading purge.
  - CSV formula injection protection escaping leading `=,+,-,@,\t,\r` characters.
  - Strict privacy invariant: worker answers are never egressed to external AI without explicit consent.
- **Empirical Accuracy Benchmark (`/accuracy`)**:
  - Benchmark evaluation CLI (`scripts/evaluate.py`) computing confusion matrices and exact Wilson score 95% confidence intervals.
  - Measured True Positive Rate: 100.0% [88.65%, 100.0%] (n=30).
  - Measured False Positive Rate: 0.0% [0.00%, 8.76%] (n=40).
- **Automated Testing Suite**:
  - 63 backend pytest tests (unit, integration, and security invariants).
  - 20 frontend vitest component and navigation tests.
  - 100% pass rate (83/83 passing tests).
