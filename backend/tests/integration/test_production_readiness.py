import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from alembic import command
from app.core.config import Settings, settings
from app.core.security import generate_secret_token, hash_secret_token, verify_secret_token
from app.db.session import get_database_url
from app.jobs.cleanup import run_retention_cleanup
from app.jobs.queue import enqueue_audit_job
from app.jobs.runner import execute_audit_job
from app.models.audit import Audit, AuditAnswer, Finding


def test_database_url_normalization():
    """Verifies that postgres:// injected by Render/Heroku is converted to postgresql://."""
    with patch.object(settings, "DATABASE_URL", "postgres://user:secret@dpg-123.render.com/canary"):
        normalized = get_database_url()
        assert normalized == "postgresql://user:secret@dpg-123.render.com/canary"

    with patch.object(settings, "DATABASE_URL", "postgresql://user:secret@localhost:5432/canary"):
        normalized = get_database_url()
        assert normalized == "postgresql://user:secret@localhost:5432/canary"

    with patch.object(settings, "DATABASE_URL", "sqlite:///./canary.db"):
        normalized = get_database_url()
        assert normalized == "sqlite:///./canary.db"


def test_allowed_origins_environment_variable_parsing():
    """Verifies that ALLOWED_ORIGINS parses both comma-separated and JSON string formats."""
    # Test comma-separated string
    s1 = Settings(ALLOWED_ORIGINS="https://canary.vercel.app, https://canary-preview.vercel.app")
    assert s1.ALLOWED_ORIGINS == ["https://canary.vercel.app", "https://canary-preview.vercel.app"]

    # Test JSON array string
    s2 = Settings(ALLOWED_ORIGINS='["https://canary.vercel.app"]')
    assert s2.ALLOWED_ORIGINS == ["https://canary.vercel.app"]

    # Test raw list
    s3 = Settings(ALLOWED_ORIGINS=["https://canary.vercel.app"])
    assert s3.ALLOWED_ORIGINS == ["https://canary.vercel.app"]


def test_alembic_migrations_against_clean_database(tmp_path):
    """Executes the full Alembic migration suite against an empty database."""
    test_db_path = tmp_path / "alembic_test.db"
    test_db_url = f"sqlite:///{test_db_path}"

    alembic_ini_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")
    )
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

    # Run upgrade head
    command.upgrade(alembic_cfg, "head")

    # Verify tables were created by migration
    engine = create_engine(test_db_url)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        )
        tables = [row[0] for row in result.fetchall()]

    assert "alembic_version" in tables
    assert "audits" in tables
    assert "audit_answers" in tables
    assert "findings" in tables
    assert "markers" in tables
    assert "check_results" in tables
    assert "finding_review_history"
    assert "job_states" in tables


def test_production_queue_fails_closed_when_redis_unavailable():
    """In production mode, enqueue_audit_job must raise RuntimeError if Redis is down."""
    with (
        patch.object(settings, "ENVIRONMENT", "production"),
        patch.object(settings, "REDIS_URL", "redis://invalid-host-that-does-not-exist:6379/0"),
        pytest.raises(RuntimeError) as exc_info,
    ):
        enqueue_audit_job("aud_test_fail_closed")

    assert "Production Redis queue unavailable" in str(exc_info.value)


def test_liveness_and_readiness_probes(client: TestClient):
    """Verifies that liveness and readiness endpoints return appropriate HTTP status."""
    # Liveness should always be 200
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json() == {"status": "alive"}

    # Readiness with active SQLite test DB should be 200
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    data = res_ready.json()
    assert data["status"] == "ready"
    assert data["database"] == "healthy"

    # API v1 health
    res_v1 = client.get("/api/v1/health")
    assert res_v1.status_code == 200
    assert res_v1.json()["status"] == "ok"


def test_privacy_sha256_token_invariants():
    """Verifies SHA-256 token hashing invariant: raw token is never recoverable from hash."""
    raw_token, token_hash = generate_secret_token()

    assert len(raw_token) >= 32
    assert len(token_hash) == 64  # SHA-256 hex digest
    assert raw_token != token_hash
    assert verify_secret_token(raw_token, token_hash) is True
    assert verify_secret_token("invalid_token", token_hash) is False


def test_cascading_retention_purge(db_session):
    """Verifies that run_retention_cleanup deletes expired audits and all cascaded children."""
    raw_token, token_hash = generate_secret_token()
    token_hash = hash_secret_token(raw_token)

    # Create an expired audit (created 8 days ago, expired 1 day ago)
    past_date = datetime.now(timezone.utc) - timedelta(days=8)
    expired_date = datetime.now(timezone.utc) - timedelta(days=1)

    audit = Audit(
        id="aud_expired_purge_test",
        token_hash=token_hash,
        status="completed",
        created_at=past_date,
        expires_at=expired_date,
    )
    db_session.add(audit)
    db_session.commit()

    # Add child answer and finding
    answer = AuditAnswer(
        id="ans_expired_test",
        audit_id=audit.id,
        task_id="T001",
        worker_id="W001",
        prompt="Test prompt",
        answer="Test answer",
    )
    finding = Finding(
        id="fnd_expired_test",
        audit_id=audit.id,
        answer_id=answer.id,
        task_id="T001",
        worker_id="W001",
        check_identifier="marker_detection",
        finding_type="synthetic_marker_match",
        evidence_confidence="High",
        explanation="Test explanation",
    )
    db_session.add_all([answer, finding])
    db_session.commit()

    # Run cleanup
    with patch("app.jobs.cleanup.SessionLocal", return_value=db_session):
        purged = run_retention_cleanup()
        assert purged >= 1

    # Verify audit and children are purged
    assert db_session.query(Audit).filter(Audit.id == audit.id).first() is None
    assert db_session.query(AuditAnswer).filter(AuditAnswer.audit_id == audit.id).first() is None
    assert db_session.query(Finding).filter(Finding.audit_id == audit.id).first() is None


def test_idempotent_audit_runner(db_session):
    """Verifies that execute_audit_job skips processing if an audit is already completed."""
    audit = Audit(
        id="aud_already_completed",
        token_hash="hash123",
        status="completed",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(audit)
    db_session.commit()

    with patch("app.jobs.runner.SessionLocal", return_value=db_session):
        # Should return cleanly without reprocessing or throwing errors
        execute_audit_job(audit.id)

    refetched = db_session.query(Audit).filter(Audit.id == audit.id).first()
    assert refetched.status == "completed"
