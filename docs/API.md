# API Specification — Canary SRS (v1)

Internal product API endpoints. All endpoints use JSON payloads and standard HTTP status codes.

## Base URL
`/api/v1`

---

### Health & System Status
- `GET /health`
  - Returns `{ "status": "ok", "version": "1.0.0", "database": "healthy", "queue": "healthy" }`

---

### Task Preparation & Marker Generation
- `POST /prepare/markers`
  - **Request**:
    ```json
    {
      "tasks": [
        {
          "task_id": "task-01",
          "prompt": "Explain the concept of quantum entanglement in simple terms."
        }
      ],
      "hiding_method": "zero_width" // "zero_width" | "prompt_embedded"
    }
    ```
  - **Response**:
    ```json
    {
      "tasks": [
        {
          "task_id": "task-01",
          "prompt": "Explain...",
          "marker": "cnry_7f8a9b2c",
          "hiding_method": "zero_width",
          "prepared_prompt": "Explain the concept...[hidden]...",
          "visible_preview": "Explain the concept of quantum entanglement in simple terms.",
          "model_received_preview": "Explain the concept of quantum entanglement [cnry_7f8a9b2c]..."
        }
      ],
      "manifest": {
        "format_version": "1.0",
        "created_at": "2026-10-29T22:00:00Z",
        "items": [...]
      }
    }
    ```

- `POST /prepare/export`
  - Exports marker manifest as JSON or CSV format.

---

### Audits & Dataset Ingestion
- `POST /audits/validate`
  - Validates uploaded CSV or JSONL file against requirements without storing.
  - Returns validation summary: row count, task count, worker count, schema errors, row-level warnings.

- `POST /audits`
  - Initiates a new audit run.
  - **Payload**:
    - `file`: Multipart file upload (CSV or JSONL).
    - `marker_manifest`: Optional JSON or file.
    - `calibration_sample`: Optional human baseline sample.
    - `consent_external_ai`: Boolean (mandatory explicit opt-in if AI providers enabled).
    - `provider_api_key`: Optional temporary reviewer API key (redacted, never saved).
    - `config`: Check settings (typo tolerance, thresholds, enabled checks).
  - **Response (201 Created)**:
    ```json
    {
      "audit_id": "aud_12345",
      "secret_token": "canary_sec_ab89f72c...", // ONLY returned once at creation!
      "secret_url": "/results/canary_sec_ab89f72c...",
      "status": "queued",
      "answers_count": 150,
      "created_at": "2026-10-29T22:00:00Z",
      "expires_at": "2026-11-05T22:00:00Z"
    }
    ```

- `GET /audits/{secret}/status`
  - Status polling endpoint.
  - Returns current state: `queued`, `validating`, `running`, `partially_completed`, `completed`, `failed`.
  - Includes progress percentage and per-check status: marker (done), similarity (running), duplicates (done), speed (skipped).

- `GET /audits/{secret}/report`
  - Comprehensive audit report data:
    - Summary metrics: answers checked, workers checked, flagged workers, category counts.
    - Detailed findings grouped by answer, worker, check type, and confidence tier.
    - Limitations and methodology disclaimers.
    - Calibration score (Wilson confidence interval) if human baseline provided.

- `GET /audits/{secret}/export.html`
  - Standalone, self-contained HTML report with inline CSS. Operates offline without external CDN assets.

- `GET /audits/{secret}/export.csv`
  - Filterable findings export with formula-injection sanitization.

- `GET /audits/{secret}/export.json`
  - Machine-readable structured findings.

- `DELETE /audits/{secret}`
  - Permanently expunges audit data, answers, findings, and temporary storage files immediately.

---

### Accuracy & Calibration
- `GET /accuracy/latest`
  - Returns real measured evaluation results on benchmark datasets.
  - If no evaluation artifact exists, returns 404 with `"Evaluation results are not available yet."`
