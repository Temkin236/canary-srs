# Privacy & Data Retention Policy — Canary SRS

## Plain-Language Privacy Commitments
1. **No Data Mining**: We do not use uploaded datasets to train machine learning models, sell data to third parties, or build profiling systems.
2. **Strict Ephemeral Storage**:
   - All uploaded datasets, intermediate embeddings, reference texts, and generated findings are automatically scheduled for permanent deletion **7 days** after upload.
   - Reviewers can invoke the **"Delete Now"** action at any point to purge all records immediately.
3. **No External AI Egress Without Opt-In**:
   - Canary defaults to 100% offline local analysis.
   - When external model similarity checks are requested, data is only transmitted after explicit confirmation (`consent_external_ai=true`).
4. **Token Security**:
   - Access to audit results is governed by a high-entropy secret link (256-bit).
   - Only cryptographic hashes of links are retained server-side.
   - Audit links are excluded from browser referrer headers and server logging.
