from fastapi.testclient import TestClient

from app.core.security import hash_secret_token
from app.db.session import Base, SessionLocal, engine
from app.jobs.runner import execute_audit_job
from app.main import app
from app.models.audit import Audit, CheckResult

# Ensure tables exist for integration test
Base.metadata.create_all(bind=engine)

client = TestClient(app)


SAMPLE_CSV = (
    "task_id,worker_id,prompt,answer,seconds_spent\n"
    'task_1,worker_A,Explain gravity,"Gravity attracts physical bodies with force.",45.0\n'
    'task_1,worker_B,Explain gravity,"Gravity causes mutual attraction.",50.0\n'
    'task_1,worker_C,Explain gravity,"Gravity attracts mass in universe.",40.0\n'
    'task_1,worker_D,Explain gravity,"Spacetime curvature describes gravity.",60.0\n'
    'task_1,worker_E,Explain gravity,"Massive centers attract via gravity.",35.0\n'
    'task_2,worker_A,Photosynthesis,"Light energy becomes chemical energy in plants.",120.0\n'
    'task_2,worker_B,Photosynthesis,"Plants synthesize glucose from sunlight.",110.0\n'
    'task_2,worker_C,Photosynthesis,"Light energy becomes chemical energy in plants.",2.0\n'
)


def test_audit_lifecycle_integration():
    # 1. Create audit via API
    resp = client.post(
        "/api/v1/audits",
        files={"file": ("sample.csv", SAMPLE_CSV.encode("utf-8"), "text/csv")},
        data={"consent_external_ai": "false"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "audit_id" in data
    assert "secret_token" in data
    assert data["status"] == "queued"
    assert data["answers_count"] == 8

    audit_id = data["audit_id"]
    secret_token = data["secret_token"]

    # 2. Invariant Check: token must NEVER be stored plaintext (FR-36)
    db = SessionLocal()
    audit_record = db.query(Audit).filter(Audit.id == audit_id).first()
    assert audit_record is not None
    assert audit_record.token_hash == hash_secret_token(secret_token)
    assert secret_token not in audit_record.token_hash
    db.close()

    # 3. Check status polling endpoint
    status_resp = client.get(f"/api/v1/audits/{secret_token}/status")
    assert status_resp.status_code == 200
    st_data = status_resp.json()
    assert st_data["audit_id"] == audit_id
    assert st_data["answers_count"] == 8

    # 4. Execute the audit job synchronously to verify all stages complete
    execute_audit_job(audit_id)

    # 5. Check completed status
    status_after = client.get(f"/api/v1/audits/{secret_token}/status")
    assert status_after.status_code == 200
    after_data = status_after.json()
    assert after_data["status"] in ("completed", "partially_completed")
    assert after_data["progress_percentage"] == 100
    assert "summary_metrics" in after_data
    assert after_data["summary_metrics"]["total_answers"] == 8

    # 6. Verify check results were persisted (FR-34)
    db = SessionLocal()
    results = db.query(CheckResult).filter(CheckResult.audit_id == audit_id).all()
    check_names = {r.check_name for r in results}
    assert "marker" in check_names
    assert "similarity" in check_names
    assert "duplicates" in check_names
    assert "speed" in check_names
    db.close()


def test_invalid_secret_token_returns_404():
    resp = client.get("/api/v1/audits/cnry_sec_invalidtoken1234567890/status")
    assert resp.status_code == 404
