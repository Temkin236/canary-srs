import datetime
import uuid

from app.db.session import Base, SessionLocal, engine
from app.jobs.cleanup import run_retention_cleanup
from app.models.audit import Audit, AuditAnswer, Finding
from app.services.audit import delete_audit_permanently

Base.metadata.create_all(bind=engine)


def test_delete_audit_permanently_cascades():
    db = SessionLocal()
    audit_id = str(uuid.uuid4())
    audit = Audit(
        id=audit_id,
        token_hash=f"hash_for_delete_{uuid.uuid4().hex}",
        status="completed",
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
    )
    db.add(audit)

    answer = AuditAnswer(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        task_id="t1",
        worker_id="w1",
        prompt="p",
        answer="a",
    )
    db.add(answer)

    finding = Finding(
        id=str(uuid.uuid4()),
        audit_id=audit_id,
        answer_id=answer.id,
        task_id="t1",
        worker_id="w1",
        check_identifier="marker",
        finding_type="exact_marker_leak",
        evidence_confidence="High",
        explanation="Marker leaked",
    )
    db.add(finding)
    db.commit()

    # Verify rows exist
    assert db.query(Audit).filter(Audit.id == audit_id).count() == 1
    assert db.query(AuditAnswer).filter(AuditAnswer.audit_id == audit_id).count() == 1
    assert db.query(Finding).filter(Finding.audit_id == audit_id).count() == 1

    # Permanent purge action (FR-41)
    success = delete_audit_permanently(audit, db)
    assert success is True

    # Verify cascading purge
    assert db.query(Audit).filter(Audit.id == audit_id).count() == 0
    assert db.query(AuditAnswer).filter(AuditAnswer.audit_id == audit_id).count() == 0
    assert db.query(Finding).filter(Finding.audit_id == audit_id).count() == 0
    db.close()


def test_retention_cleanup_purges_only_expired():
    db = SessionLocal()
    past_id = str(uuid.uuid4())
    future_id = str(uuid.uuid4())
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    expired_audit = Audit(
        id=past_id,
        token_hash=f"hash_expired_{uuid.uuid4().hex}",
        status="completed",
        expires_at=now_utc - datetime.timedelta(days=1),  # Expired yesterday
    )
    active_audit = Audit(
        id=future_id,
        token_hash=f"hash_active_{uuid.uuid4().hex}",
        status="completed",
        expires_at=now_utc + datetime.timedelta(days=6),  # Still active
    )
    db.add(expired_audit)
    db.add(active_audit)
    db.commit()
    db.close()

    # Run cleanup (FR-42)
    purged_count = run_retention_cleanup()
    assert purged_count >= 1

    db = SessionLocal()
    assert db.query(Audit).filter(Audit.id == past_id).count() == 0
    assert db.query(Audit).filter(Audit.id == future_id).count() == 1
    db.close()
