# Security Policy

## Responsible Disclosure
If you discover a security vulnerability in Canary SRS, please report it via private disclosure rather than opening a public GitHub issue.

Email security reports to: `temkinabdulmelik1@gmail.com`

## Security Principles & Invariants in Canary
1. **Zero Secret Persistence**: API keys (e.g., Google Gemini keys) entered by users for audit-scoped external similarity checks are held only in-memory during job execution and are never stored in databases, logs, reports, or queue messages.
2. **Audit Link Confidentiality**: Audit secret tokens are generated using cryptographically secure random bytes (256-bit entropy). Only cryptographic hashes (SHA-256) of tokens are stored in the database.
3. **Data Isolation & Sanitization**:
   - All uploaded content is treated as untrusted text.
   - Internal filenames use random UUIDs; uploaded file paths are never used directly on the filesystem.
   - HTML exports escape all user input to prevent XSS.
   - CSV exports sanitize leading formula prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) to prevent CSV injection / formula execution.
4. **Data Retention & Deletion**:
   - Audits default to a 7-day retention period, after which all answers, files, findings, and metadata are permanently expunged.
   - "Delete Now" provides immediate, complete cascading deletion of all associated audit assets.
5. **Rate Limiting & Spending Controls**:
   - IP / session-based rate limiting prevents concurrent audit denial-of-service.
   - External provider calls have strict per-audit call and token spending caps.
