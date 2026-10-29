import logging

from sqlalchemy.orm import Session

from app.models.audit import Audit

logger = logging.getLogger(__name__)


def delete_audit_permanently(audit: Audit, db: Session) -> bool:
    """
    Cascades immediate purge of all audit data and associated database records (FR-41).
    All answers, findings, markers, and job states are removed.
    """
    try:
        audit_id = audit.id
        logger.info("Purging audit %s immediately from database", audit_id)

        # Deleting the parent audit row cascades to all child tables
        # (answers, markers, check_results, findings, reference_answers, calibration, job_state)
        # via SQLAlchemy cascade="all, delete-orphan" and ON DELETE CASCADE foreign keys.
        db.delete(audit)
        db.commit()
        return True
    except Exception as e:
        logger.exception("Failed to purge audit %s: %s", audit.id, e)
        db.rollback()
        return False
