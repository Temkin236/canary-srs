# Security Checklist & Threat Model — Canary SRS

## Threat Model & Mitigations

### 1. Data Exfiltration via External AI Providers
- **Threat**: Uploaded worker responses containing sensitive or proprietary dataset text are sent to third-party APIs without authorization.
- **Mitigation**:
  - `consent_external_ai` boolean is strictly required. If false or omitted, the backend blocks all external requests.
  - Reviewer-provided temporary API keys are kept in memory only for the duration of the request/job and never written to disk, database, queue, or logs.
  - Offline Mode executes all local checks without external network connectivity.

### 2. CSV Formula Injection (Spreadsheet Macro Execution)
- **Threat**: An adversary crafts answers containing `=cmd|' /C calc'!A0` or similar formulas designed to trigger code execution when a reviewer opens the exported CSV.
- **Mitigation**:
  - In `backend/app/reporting/csv_export.py`, every field beginning with `=`, `+`, `-`, `@`, `\t`, or `\r` is sanitized by prefixing with a single quote `'`.

### 3. Stored XSS via Malicious Dataset Answers
- **Threat**: A worker submits answers containing `<script>alert(document.cookie)</script>` or malicious iframe payloads that execute in the browser when viewed in the web UI or HTML export.
- **Mitigation**:
  - React natively escapes all interpolated text strings.
  - The standalone HTML export uses safe templating with explicit HTML escaping on all evidence and answers.

### 4. Secret URL Enumeration & Link Guessing
- **Threat**: Attackers attempt brute-force scanning of audit URLs to inspect private dataset audits.
- **Mitigation**:
  - Tokens are 32 bytes of cryptographic randomness (256 bits).
  - Backend stores only `sha256(token)`.
  - Constant-time comparison or hash lookup prevents timing attacks.
  - Any non-matching token returns generic 404 (no distinction between non-existent and expired).

### 5. Path Traversal via Uploaded Filenames
- **Threat**: Attackers send malicious `Content-Disposition` filenames (e.g. `../../etc/passwd`).
- **Mitigation**:
  - Uploaded filenames are discarded immediately upon arrival.
  - Storage paths are generated using UUID4 identifiers inside an isolated storage root (`data/storage/`).
