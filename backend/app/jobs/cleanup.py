import datetime
import logging

from app.db.session import SessionLocal
from app.models.audit import Audit
from app.services.audit import delete_audit_permanently

logger = logging.getLogger(__name__)


def run_retention_cleanup() -> int:
    """
    Scans for expired audits beyond the 7-day retention window and purges them (FR-42).
    Returns:
        Number of expired audits purged.
    """
    db = SessionLocal()
    purged_count = 0
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        # Handle SQLite naive datetimes or aware datetimes
        expired_audits = db.query(Audit).filter(Audit.expires_at <= now_utc).all()

        for audit in expired_audits:
            logger.info("Found expired audit %s (expired at %s)", audit.id, audit.expires_at)
            success = delete_audit_permanently(audit, db)
            if success:
                purged_count += 1

        logger.info("Retention cleanup completed: purged %d expired audits", purged_count)
        return purged_count
    finally:
        db.close()
