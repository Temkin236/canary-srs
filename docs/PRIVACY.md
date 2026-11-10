# Privacy Architecture & Data Retention Policy

Canary SRS is engineered with strict, privacy-first invariants designed to protect crowd workers and dataset stewards from unauthorized surveillance, accidental secret leakage, and persistent data exposure.

---

## 1. Core Philosophical & Technical Invariants

### Invariant 1: Zero External AI Egress by Default
Canary operates **100% offline-capable**. All core checks (Canary Marker Detection, TF-IDF lexical similarity, MinHash/Jaccard duplicate clustering, and typing speed calculations) run on local CPU compute without outbound internet requests.
- External LLM inference (e.g. Google Gemini reference generation) is **disabled by default**.
- It can only be activated when a steward explicitly sets `consent_external_ai=true` during audit initiation.
- Worker answers are never used to train or fine-tune models.

### Invariant 2: Cryptographic Token Confidentiality (Zero Unhashed Persistence)
Audit results and investigation workspaces are protected by 256-bit entropy secret links (`cnry_sec_...`).
- The raw secret token is presented **exactly once** to the user in the audit creation response.
- The server stores strictly the **SHA-256 one-way cryptographic hash** of the token in the database (`token_hash = sha256(raw_token)`).
- If database backups or tables are exposed, raw access tokens cannot be recovered or reversed.

### Invariant 3: Ephemeral 7-Day Retention & Cascading Purge
- Every audit record, worker submission, reference text, marker, and finding is assigned an expiration timestamp `expires_at = created_at + 7 days`.
- An automated cascading cleanup worker runs hourly (`scripts/cleanup.py`), executing hard SQL `DELETE` cascades across `audits`, `audit_answers`, `reference_answers`, `markers`, `findings`, and `job_states`.
- Uploaded dataset files on disk are unlinked and permanently erased.

### Invariant 4: On-Demand Immediate Deletion ("Delete Now")
- Reviewers can invoke the **"Delete Now"** action at any moment from the Results Portal or Investigation Workspace.
- The backend immediately triggers `delete_audit_permanently(audit_id)`, executing an instantaneous cascading erase across all relational tables and unlinking files on disk.

### Invariant 5: Spreadsheet Formula Injection Defense
CSV exports are protected against Formula Injection (Spreadsheet Macro Attacks / CVE-style CSV vulnerabilities).
- When generating CSV reports, all answer text, prompts, explanations, and IDs are passed through `sanitize_csv_field()`.
- Any field beginning with formula control characters (`=`, `+`, `-`, `@`, `\t`, `\r`) is automatically prepended with a single quote (`'`), neutralizing executable commands in Microsoft Excel, LibreOffice Calc, and Google Sheets.

---

## 2. Technical Invariants Summary Table

| Security Dimension | Technical Mechanism | Guarantee |
|---|---|---|
| **Audit Authentication** | SHA-256 digest lookup | Server cannot leak raw access tokens |
| **External AI Privacy** | Explicit boolean guard (`consent_external_ai`) | Zero unconsented network egress |
| **Data Lifecycle** | 7-day TTL + immediate purge | Zero perpetual data retention |
| **Export Security** | Single-quote prefix sanitization | Macro injection neutralized |
| **Worker Identity** | Arbitrary tokenized `worker_id` string | No PII (names, emails, SSNs) required |
| **Execution Environment** | Local SQLite / Postgres & in-memory queue | Operates in air-gapped VPCs |

---

## 3. Threat Model & Out-of-Scope Behaviors

### What Canary Defends Against:
- Unintended leakage of dataset records to external AI providers.
- Persistent retention of sensitive human annotations.
- Spreadsheet-based client-side exploit execution via CSV export.
- Re-identification through persistent reviewer credentials.

### Explicit Limitations (Evidence, Not Verdict):
- Canary findings **must never** be used to automate penalties, wage withholding, or automated worker bans.
- The platform is explicitly built to present calibrated evidence to human reviewers, who retain ethical accountability for any dataset moderation decisions.
