import datetime
import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.audit import Audit, AuditAnswer, Finding, Marker, ReferenceAnswer

client = TestClient(app)


def test_investigation_workspace_workflow():
    db = SessionLocal()
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=7)

    # 1. Seed audit with an answer, reference answer, marker, and finding
    audit_id = str(uuid.uuid4())
    token_hash = "f" * 64
    audit = Audit(
        id=audit_id,
        token_hash=token_hash,
        status="completed",
        answers_count=2,
        workers_count=2,
        flagged_workers_count=1,
        consent_external_ai=False,
        dataset_name="crowd_eval_batch.csv",
        created_at=now,
        completed_at=now,
        expires_at=expires,
    )
    db.add(audit)

    ans_id = str(uuid.uuid4())
    answer = AuditAnswer(
        id=ans_id,
        audit_id=audit_id,
        task_id="task_101",
        worker_id="worker_99",
        prompt="Explain photosynthesis.",
        answer=(
            "Photosynthesis is the process used by plants to convert light energy "
            "into chemical energy."
        ),
        submitted_at=now,
    )
    db.add(answer)

    ref = ReferenceAnswer(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        task_id="task_101",
        provider="offline-synthetic",
        model_name="synthetic-v1",
        reference_text=(
            "Photosynthesis is the process used by plants to convert light energy "
            "into chemical sugar."
        ),
    )
    db.add(ref)

    marker = Marker(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        task_id="task_101",
        marker_token="cnry_alpha_99",
        hiding_method="zero_width",
    )
    db.add(marker)

    finding_id = str(uuid.uuid4())
    finding = Finding(
        id=finding_id,
        audit_id=audit_id,
        answer_id=ans_id,
        task_id="task_101",
        worker_id="worker_99",
        check_identifier="similarity",
        finding_type="model_reference_top_percentile",
        evidence_confidence="High",
        explanation=(
            "Answer exhibits high lexical and semantic overlap with model reference output."
        ),
        evidence_text="Photosynthesis is the process used by plants to convert light energy...",
        numerical_measurements={"jaccard_similarity": 0.94, "tfidf_cosine": 0.96},
        review_status="pending_review",
    )
    db.add(finding)
    db.commit()

    # 2. Test GET /api/v1/audits/{id}/investigate
    res = client.get(f"/api/v1/audits/{audit_id}/investigate")
    assert res.status_code == 200
    data = res.json()
    assert data["audit"]["id"] == audit_id
    assert len(data["findings"]) == 1
    f_data = data["findings"][0]
    assert f_data["id"] == finding_id
    assert f_data["worker_id"] == "worker_99"
    assert f_data["worker_answer"] is not None
    assert len(data["markers"]) == 1
    assert data["markers"][0]["expected_marker"] == "cnry_alpha_99"

    # 3. Test PATCH /api/v1/findings/{finding_id}/review
    update_res = client.patch(
        f"/api/v1/findings/{finding_id}/review",
        json={
            "review_status": "under_review",
            "reviewer_notes": "Reviewer initiated deep dive into task 101 context.",
            "assigned_reviewer": "sarah_lead",
            "reviewer_id": "sarah_lead",
        },
    )
    assert update_res.status_code == 200
    updated_f = update_res.json()
    assert updated_f["review_status"] == "under_review"
    assert updated_f["assigned_reviewer"] == "sarah_lead"
    assert updated_f["reviewer_notes"] == "Reviewer initiated deep dive into task 101 context."
    assert len(updated_f["history"]) == 1
    assert updated_f["history"][0]["action"] == "status_change"
    assert updated_f["history"][0]["previous_status"] == "pending_review"
    assert updated_f["history"][0]["new_status"] == "under_review"

    # 4. Test GET /api/v1/findings/{finding_id}/history
    hist_res = client.get(f"/api/v1/findings/{finding_id}/history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) == 1
    assert history[0]["reviewer_id"] == "sarah_lead"

    # 5. Test GET /api/v1/findings/{finding_id}/comparison
    comp_res = client.get(f"/api/v1/findings/{finding_id}/comparison")
    assert comp_res.status_code == 200
    comp = comp_res.json()
    assert comp["finding_id"] == finding_id
    assert comp["task_id"] == "task_101"
    assert "Photosynthesis" in comp["source_answer"]
    assert "Photosynthesis" in comp["target_answer"]
    assert len(comp["diff_segments"]) > 0
    # Must have matched segments
    matches = [s for s in comp["diff_segments"] if s["is_match"]]
    assert len(matches) > 0
    assert comp["similarity_score"] == 0.94
    assert "Evidence for human review only" in comp["limitations"]

    # 6. Test invalid status rejection
    bad_res = client.patch(
        f"/api/v1/findings/{finding_id}/review",
        json={"review_status": "invalid_status_value"},
    )
    assert bad_res.status_code == 422
