import datetime
import uuid

from app.models.audit import Audit, AuditAnswer


def test_quality_analytics_workflow(client, db_session):
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=7)

    # 1. Create audit with diverse answer records
    audit_id = str(uuid.uuid4())
    token_hash = "a" * 64
    audit = Audit(
        id=audit_id,
        token_hash=token_hash,
        status="completed",
        answers_count=5,
        workers_count=3,
        flagged_workers_count=0,
        consent_external_ai=False,
        dataset_name="=FormulaTest_dataset.csv",  # Tests CSV formula injection protection
        created_at=now,
        completed_at=now,
        expires_at=expires,
    )
    db_session.add(audit)

    # Add 5 answers with varying characteristics
    records = [
        # Normal record
        AuditAnswer(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            task_id="task_1",
            worker_id="worker_alpha",
            prompt="Summarize relativity.",
            answer=(
                "Relativity is a physical theory formulated by Albert Einstein "
                "describing gravity and spacetime."
            ),
            submitted_at=now,
            seconds_spent=45.0,
        ),
        # Short answer (<20 chars) by same worker (concentration test)
        AuditAnswer(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            task_id="task_1",  # duplicate task submission
            worker_id="worker_alpha",
            prompt="Summarize relativity.",
            answer="Too short text.",
            submitted_at=now,
            seconds_spent=10.0,
        ),
        # Another answer by worker_alpha
        AuditAnswer(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            task_id="task_2",
            worker_id="worker_alpha",
            prompt="Explain gravity.",
            answer="Gravity is the universal force of attraction acting between all matter.",
            submitted_at=now,
            seconds_spent=35.0,
        ),
        # Duplicate text answer
        AuditAnswer(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            task_id="task_3",
            worker_id="+worker_beta",  # Formula injection test for worker ID
            prompt="Explain gravity.",
            answer="Gravity is the universal force of attraction acting between all matter.",
            submitted_at=now,
            seconds_spent=50.0,
        ),
        # Empty answer, missing timestamp, missing worker ID
        AuditAnswer(
            id=str(uuid.uuid4()),
            audit_id=audit_id,
            task_id="task_4",
            worker_id="",
            prompt="What is entropy?",
            answer="",
            submitted_at=None,
            seconds_spent=None,
        ),
    ]
    for r in records:
        db_session.add(r)
    db_session.commit()

    # 2. Query Quality Analytics API
    res = client.get(f"/api/v1/audits/{audit_id}/quality")
    assert res.status_code == 200
    data = res.json()

    assert data["audit_id"] == audit_id
    assert data["total_records"] == 5
    assert data["unique_workers"] == 2  # worker_alpha and +worker_beta
    assert data["unique_tasks"] == 4
    assert data["empty_answers_count"] == 1
    assert data["missing_worker_ids_count"] == 1
    assert data["missing_timestamps_count"] == 1
    assert data["duplicate_task_submissions_count"] == 1  # task_1 submitted twice
    assert data["duplicate_submissions_count"] == 1  # exact same text twice
    assert 0.0 <= data["completeness_score"] <= 100.0

    # Length stats
    assert data["length_stats"]["min_chars"] == 15
    assert data["length_stats"]["short_answers_count"] == 1
    assert len(data["length_distribution"]) == 6

    # Worker participation
    assert data["worker_participation"]["top_contributors"][0]["worker_id"] == "worker_alpha"
    assert data["worker_participation"]["top_contributors"][0]["answer_count"] == 3

    # Task coverage
    assert data["task_coverage"]["max_answers_per_task"] == 2

    # Warnings
    warning_codes = [w["code"] for w in data["warnings"]]
    assert "EMPTY_ANSWERS" in warning_codes
    assert "MISSING_WORKER_IDS" in warning_codes

    # 3. Test CSV export with formula injection mitigation
    csv_res = client.get(f"/api/v1/audits/{audit_id}/quality/export?format=csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    csv_text = csv_res.text

    # Verify formula injection mitigation: leading '=' and '+' escaped with single quote
    assert "'=FormulaTest_dataset.csv" in csv_text
    assert "'+worker_beta" in csv_text
    # Verify disclaimer header
    assert "NOTICE: Descriptive hygiene metrics only" in csv_text

    # 4. Test JSON export
    json_res = client.get(f"/api/v1/audits/{audit_id}/quality/export?format=json")
    assert json_res.status_code == 200
    json_data = json_res.json()
    assert json_data["total_records"] == 5


def test_empty_audit_quality_analytics(client, db_session):
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=7)

    empty_audit_id = str(uuid.uuid4())
    audit = Audit(
        id=empty_audit_id,
        token_hash="b" * 64,
        status="completed",
        answers_count=0,
        workers_count=0,
        flagged_workers_count=0,
        consent_external_ai=False,
        dataset_name="empty.csv",
        created_at=now,
        completed_at=now,
        expires_at=expires,
    )
    db_session.add(audit)
    db_session.commit()

    res = client.get(f"/api/v1/audits/{empty_audit_id}/quality")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] == 0
    assert data["completeness_score"] == 0.0
    assert len(data["warnings"]) == 1
    assert data["warnings"][0]["code"] == "EMPTY_DATASET"


def test_quality_analytics_404(client):
    fake_id = str(uuid.uuid4())
    res = client.get(f"/api/v1/audits/{fake_id}/quality")
    assert res.status_code == 404
