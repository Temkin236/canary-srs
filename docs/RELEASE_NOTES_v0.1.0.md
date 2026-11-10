# Release Notes: Canary SRS v0.1.0

**Release Title**: Canary SRS — Full-Stack Dataset Integrity Platform  
**Tag**: `v0.1.0`  
**Date**: November 10, 2026  
**Maintainer**: Temkin Abdulmelik ([@Temkin236](https://github.com/Temkin236))

---

## Highlights

Canary SRS (Contamination Audit for Human-Written Datasets) is a privacy-first evidence collection and human-review platform designed to help dataset stewards investigate possible chatbot contamination in human-written crowd and vendor datasets.

> **Core Philosophy**: *"Evidence, Not Verdict."* Canary produces calibrated, transparent artifacts for human review. It is never an automated authorship judge or worker punishment mechanism.

---

## What's Included in v0.1.0

### 1. Full-Stack Monorepo Architecture
- **Backend**: Asynchronous Python 3.12+ REST API powered by FastAPI, Pydantic v2 schemas, and SQLAlchemy 2.0.
- **Frontend**: Single Page Application built with React 18, TypeScript (strict mode), Tailwind CSS, Vite, and Lucide icons.
- **Execution Engine**: Dual-mode worker architecture supporting Redis + RQ distributed workers with synchronous in-memory fallback for zero-dependency local developer execution.

### 2. Deterministic Contamination Detection Engine (100% Offline Capable)
- **Check 1 (Canary Markers)**: Invisible zero-width Unicode sequences (`\u200b`, `\u200c`, `\u200d`) and subtle instruction footnotes with exact and bounded Levenshtein typo-matching ($d \le 1$).
- **Check 2 (AI Reference & Peer Distribution)**: Lexical TF-IDF cosine similarity against offline reference answers, contextualized by empirical peer distributions within each task.
- **Check 3 (Cross-Worker Duplicates)**: Exact token hashing and 3-gram Jaccard similarity across distinct worker accounts.
- **Check 4 (Typing Velocity)**: Physical speed plausibility analysis (>15 chars/sec) based on submission timestamps.

### 3. Reviewer Workspaces
- **Reviewer Dashboard (`/dashboard`)**: Centralized visibility across multiple dataset audits with finding category breakdowns, activity volume trends, and dataset size distributions.
- **Evidence Adjudication Workspace (`/audits/:auditId`)**: Interactive human-review environment with multi-factor filters, inline offset viewers, reviewer notes, status progression (`under_review`, `needs_investigation`, `reviewed`, `dismissed`), and side-by-side diff comparisons.
- **Dataset Quality & Hygiene Analytics (`/audits/:auditId?tab=quality`)**: Descriptive dataset health metrics including completeness scoring, worker participation distributions, answer length histograms, and CSV/JSON quality exports.

### 4. Privacy & Security Invariants
- **SHA-256 Token Hashing**: Audit secret access tokens (256-bit entropy) are stored exclusively as SHA-256 digests.
- **7-Day Ephemeral Retention**: Background cascading cleanup daemon paired with an on-demand "Delete Now" capability permanently expunging all relational records and files.
- **Formula Injection Defense**: Automatic single-quote prefix sanitization for CSV exports against spreadsheet macro attacks.
- **Strict Privacy Invariant**: Zero worker data transmission to third-party AI APIs without explicit reviewer opt-in.

### 5. Automated Verification & Quality
- **83 Passing Automated Tests**: 63 backend pytest tests and 20 frontend vitest tests.
- **Empirical Accuracy Benchmark**: Wilson score 95% confidence intervals (TPR: 100.0% [88.65%, 100.0%], FPR: 0.0% [0.00%, 8.76%]).
- **Strict Type Safety**: TypeScript strict mode with zero compilation errors; Ruff formatting clean across all 62 backend files.

---

## Known Limitations
- Evaluated on controlled synthetic benchmarks ($n=70$); continuing empirical validation on large-scale crowd distributions is ongoing.
- Invisible markers can be stripped by aggressive text normalizers or OCR pipelines.
- High typing speed indicates copy-paste or external drafting, not necessarily automated generation.
