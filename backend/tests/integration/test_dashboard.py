import datetime
import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.audit import Audit, Finding

client = TestClient(app)


def test_dashboard_stats_empty():
    res = client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_audits" in data
    assert "completed_audits" in data
    assert "running_audits" in data
    assert "failed_audits" in data
    assert "total_answers_analyzed" in data
    assert "findings_requiring_review" in data
    assert "reviewed_findings" in data
    assert "findings_by_category" in data
    assert "activity_over_time" in data
    assert len(data["activity_over_time"]) == 14


def test_dashboard_stats_and_filtering_populated():
    db = SessionLocal()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    audit_id = str(uuid.uuid4())
    token_hash = f"dash_hash_{uuid.uuid4().hex}"

    audit = Audit(
        id=audit_id,
        token_hash=token_hash,
        dataset_name="crowd_eval_batch_1.csv",
        status="completed",
        answers_count=250,
        workers_count=15,
        flagged_workers_count=2,
        created_at=now_utc,
        completed_at=now_utc + datetime.timedelta(seconds=45),
        expires_at=now_utc + datetime.timedelta(days=7),
    )
    db.add(audit)

    # Add findings
    finding1 = Finding(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        answer_id="ans-1",
        task_id="t1",
        worker_id="w1",
        check_identifier="marker",
        finding_type="exact_marker_leak",
        evidence_confidence="High",
        explanation="Secret marker detected in answer",
        review_status="pending_review",
        created_at=now_utc,
    )
    finding2 = Finding(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        answer_id="ans-2",
        task_id="t2",
        worker_id="w2",
        check_identifier="similarity",
        finding_type="model_similarity_peer_outlier",
        evidence_confidence="Medium",
        explanation="High cosine similarity to reference answer",
        review_status="reviewed",
        created_at=now_utc,
    )
    db.add(finding1)
    db.add(finding2)
    db.commit()

    # Query stats
    res = client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_audits"] >= 1
    assert stats["total_answers_analyzed"] >= 250
    assert stats["findings_requiring_review"] >= 1
    assert stats["reviewed_findings"] >= 1
    assert stats["findings_by_category"]["marker"] >= 1

    # Query audits with search filter
    search_res = client.get("/api/v1/dashboard/audits?search=crowd_eval")
    assert search_res.status_code == 200
    audits_data = search_res.json()
    assert audits_data["total"] >= 1
    item = next((i for i in audits_data["items"] if i["id"] == audit_id), None)
    assert item is not None
    assert item["dataset_name"] == "crowd_eval_batch_1.csv"
    assert item["findings_count"] == 2
    assert item["duration_seconds"] == 45.0

    # Query audits with status filter
    status_res = client.get("/api/v1/dashboard/audits?status=completed")
    assert status_res.status_code == 200
    assert status_res.json()["total"] >= 1

    # Export CSV summary
    csv_res = client.get("/api/v1/dashboard/export?search=crowd_eval")
    assert csv_res.status_code == 200
    assert csv_res.headers["content-type"] == "text/csv; charset=utf-8"
    assert "crowd_eval_batch_1.csv" in csv_res.text
    assert "Audit ID,Dataset Name,Status" in csv_res.text
