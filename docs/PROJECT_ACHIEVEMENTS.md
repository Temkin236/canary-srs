# Engineering Highlights & Project Achievements

**Canary SRS** (Contamination Audit for Human-Written Datasets) was designed, implemented, tested, and delivered by **Temkin Abdulmelik** as a privacy-first, full-stack dataset integrity platform for dataset stewards, crowd platforms, and machine learning researchers.

---

## 1. Executive Summary & Delivery Scope

- **Architecture**: Monorepo encompassing a high-performance Python 3.12 / FastAPI backend and a responsive React 18 / TypeScript / Tailwind CSS frontend.
- **Delivery**: 13 structured feature pull requests successfully delivered across 3 core milestones.
- **Verification**: **83 passing automated tests** (63 backend pytest tests, 20 frontend vitest tests) enforcing all functional requirements (FR-1 through FR-46) and security invariants.
- **Empirical Grounding**: Measured benchmark accuracy with exact Wilson score 95% confidence intervals, zero stylometric hallucination, and 100% offline-capable deterministic checks.

---

## 2. Key Engineering Achievements

### Full-Stack Architecture & Workspaces
- **Enterprise Reviewer Dashboard (`/dashboard`)**: Centralized analytics workspace aggregating cross-audit findings, 14-day audit volume activity, detection check distributions, and dataset size categorization directly from database records.
- **Evidence Adjudication Workspace (`/audits/:auditId`)**: Multi-tab investigation console featuring real-time finding filters (confidence, category, status, worker ID), inline evidence snippets with offset highlighting, reviewer status workflows (`under_review`, `needs_investigation`, `reviewed`, `dismissed`), and side-by-side diff comparisons.
- **Dataset Quality Profiling Engine (`/audits/:auditId?tab=quality`)**: Descriptive dataset hygiene engine computing completeness scores, worker concentration ratios, answer length histograms, and timestamp coverage without automated penalties.
- **Task Preparation Engine (`/prepare`)**: Automated generation and injection of cryptographically secure canary markers (zero-width Unicode sequences and subtle instruction footnotes) into task prompt CSV/JSONL datasets.

### Deterministic Detection Pipeline (100% Offline Capable)
1. **Hidden Task-Specific Marker Detection (Check 1)**:
   - Seeding and detection of invisible Unicode tokens (`\u200b`, `\u200c`, `\u200d`) and subtle instruction footnotes.
   - Exact token matching combined with bounded Levenshtein edit-distance to detect truncated or minorly altered marker echoes.
2. **AI Reference Similarity & Peer Distribution (Check 2)**:
   - Lexical TF-IDF vectorization and cosine similarity against offline synthetic reference texts.
   - Contextualized against peer-answer similarity percentiles within each task to prevent false positives from shared domain terminology.
3. **Cross-Worker Duplicate Clustering (Check 3)**:
   - Identifies identical and near-verbatim text reuse across different worker IDs for the same task using exact token hashing, MinHash, and 3-gram Jaccard similarity.
4. **Typing Velocity & Speed Plausibility (Check 4)**:
   - Evaluates characters per second against empirical human typing thresholds (>15 chars/sec) when client submission timestamps are available.

### Privacy & Security Engineering
- **Zero Raw Secret Persistence**: Reviewer secret tokens (256 bits of entropy) are displayed once upon audit creation and stored in the database strictly as one-way **SHA-256 digests**.
- **Formula Injection Defense**: All exported CSV reports sanitize leading formula trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`) with single quotes to protect spreadsheet users from macro execution attacks.
- **7-Day Ephemeral Retention & Cascading Purge**: Background worker continuously enforces a 7-day TTL lifecycle. Reviewers can trigger an immediate, irreversible cascading purge ("Delete Now") expunging all answers, markers, and findings.
- **Strict Privacy Invariant**: Worker answers are never transmitted to external AI providers without explicit reviewer consent (`consent_external_ai=true`).

### Reliable Background Processing & Queue Fallback
- Dual-mode execution engine: seamlessly switches between **Redis + RQ** for scalable asynchronous background processing and a **synchronous in-memory fallback** for completely offline, zero-dependency local execution.

---

## 3. Verified Verification & Test Results

```
Backend Test Suite (Pytest 9.2, Python 3.12):
  - Integration Tests:  9 passed (dashboard, investigation, quality, job runner)
  - Security Invariants: 6 passed (token hashing, formula injection, AI consent)
  - Unit Tests:         48 passed (marker detection, duplicates, similarity, speed, reporting)
  Total Backend:        63 PASSED

Frontend Test Suite (Vitest, React Testing Library):
  - Investigation Workspace: 4 passed
  - Dataset Quality Views:   4 passed
  - Reviewer Dashboard:      3 passed
  - Navigation & Layouts:    8 passed
  - Application Routing:     1 passed
  Total Frontend:       20 PASSED

Total Test Suite:       83 PASSED (100% pass rate)
Code Formatting:        Ruff verified (62 backend files formatted)
TypeScript:             Strict mode (0 compilation errors)
```

---

## 4. Git Delivery History & Merged PRs

| Pull Request | Branch | Description |
|---|---|---|
| **#13** | `feat/dataset-quality-analytics` | Dataset quality profiling engine and analytics interface |
| **#12** | `feat/evidence-investigation` | Advanced evidence investigation workspace and reviewer adjudication |
| **#11** | `feat/professional-dashboard` | Reviewer dashboard and analytics workspace |
| **#10** | `chore/dev-makefile-target` | Concurrent development make target for full-stack local workflow |
| **#9** | `chore/release-verification` | Release verification and measured empirical accuracy documentation |
| **#8** | `feat/complete-website` | Complete website navigation, marketing pages, and responsive layout |
| **#7** | `feat/evaluation` | Baseline calibration, benchmark evaluation, and reporting |
| **#6** | `feat/evidence-reports` | Evidence reports (offline HTML, formula-safe CSV, JSON) and cascading purge |
| **#5** | `feat/background-audits` | Durable background audit execution and job polling |
| **#4** | `feat/contamination-checks` | Detection engine core checks (marker, similarity, duplicate, speed) |
| **#3** | `feat/marker-preparation` | Cryptographic canary marker generation and injection |
| **#2** | `feat/dataset-validation` | Dataset validation, parsing, and schema error reporting |
| **#1** | `chore/project-foundation` | Project foundation, monorepo architecture, and CI pipeline |

---

## 5. Engineering Transparency & Known Limitations

1. **Benchmark Scope**: The current synthetic benchmark dataset (`canary-synthetic-benchmark-v1.0`, n=70) validates zero false positives and high sensitivity under controlled conditions; continuing evaluation on larger diverse real-world crowdsourcing distributions is ongoing.
2. **Lexical Similarity Scope**: Lexical TF-IDF similarity flags statistical peer outliers but cannot distinguish legitimate common phrasing without human contextual review.
3. **Typing Speed Scope**: High typing velocity indicates fast copy-paste or pre-written answers, which may be benign (e.g. drafting in an external desktop document editor).
4. **Canary Marker Persistence**: Zero-width Unicode markers survive standard copy-paste operations into chat interfaces but can be stripped by aggressive text normalizers or intermediate OCR pipelines.
