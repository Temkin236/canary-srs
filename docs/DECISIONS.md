# Architecture Decision Records (ADRs) — Canary SRS

## ADR-001: Separation of Engine from Web Framework
- **Context**: The contamination detection engine contains sophisticated algorithms (fuzzy string search, TF-IDF lexical matching, MinHash/Jaccard duplicate clustering, Wilson confidence bounds).
- **Decision**: Keep `app/checks/` and `app/evaluation/` completely decoupled from FastAPI request/response objects and ORM models. Checks receive clean dataclasses and return structured findings.
- **Consequences**: Enables 100% deterministic, standalone unit testing of all detection logic and reproducibility in offline CLI scripts (`scripts/evaluate.py`).

## ADR-002: Dual Queue Architecture (Redis + In-Memory Fallback)
- **Context**: Production requires Redis/RQ for durable asynchronous worker execution. However, local developer setups and lightweight reviewer environments may not have a running Redis daemon.
- **Decision**: Provide an abstract queue interface with a Redis backend (`app/jobs/redis_queue.py`) and a synchronous/threaded in-memory queue backend (`app/jobs/memory_queue.py`) controlled by `USE_IN_MEMORY_QUEUE=true` in `.env`.
- **Consequences**: Immediate developer productivity out-of-the-box with zero background dependencies, while retaining full production scaling capability.

## ADR-003: Secret Token Hashing & Link Guessing Resistance
- **Context**: Audit results are accessible via secret URLs without requiring user account registration (for low-friction reviewer usage).
- **Decision**: Generate 256 bits of cryptographic entropy (`secrets.token_urlsafe(32)`). Store only the SHA-256 hash in the database. When a secret URL is visited, the backend hashes the incoming token and looks up the audit by hash. Invalid tokens yield a generic 404.
- **Consequences**: Even a full database compromise or access log leak does not disclose unhashed audit tokens.

## ADR-004: Explicit Opt-in for External AI Model Inference
- **Context**: Comparing crowd answers to AI model references can require querying external LLM APIs (e.g., Google Gemini). Uploaded crowd datasets may contain proprietary or sensitive human worker texts.
- **Decision**: Require an explicit boolean parameter `consent_external_ai=true`. If false or absent, external AI calls are strictly blocked and the system runs in Offline Mode (using markers, duplicates, and local lexical similarity).
- **Consequences**: Strict privacy compliance and protection against inadvertent third-party data egress.

## ADR-005: Formula Injection Defense in CSV Exports
- **Context**: Attackers or rogue crowd workers may submit answers starting with `=`, `+`, `-`, `@`, `\t`, or `\r`. When exported to CSV and opened in Microsoft Excel or Google Sheets, this can trigger arbitrary command execution (CSV formula injection).
- **Decision**: All string fields written to CSV exports are sanitized: if the value starts with dangerous characters, it is prefixed with a single quote `'` or properly escaped.
- **Consequences**: Complete safety against spreadsheet formula execution exploits.
