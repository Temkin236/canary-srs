import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from app.core.config import settings

logger = logging.getLogger(__name__)

# Dedicated thread pool for in-memory queue fallback
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="canary-worker")


def enqueue_audit_job(audit_id: str) -> None:
    """
    Enqueues an audit execution job.
    Uses Redis + RQ if configured and available; otherwise seamlessly falls back to
    the asynchronous in-memory background executor (FR-32).
    """
    from app.jobs.runner import execute_audit_job

    if not settings.USE_IN_MEMORY_QUEUE:
        try:
            import redis
            from rq import Queue

            redis_conn = redis.from_url(settings.REDIS_URL)
            # Test connectivity
            redis_conn.ping()
            q = Queue("canary-audits", connection=redis_conn)
            q.enqueue(execute_audit_job, audit_id, job_timeout=1200)  # 20 minutes (FR-33)
            logger.info("Enqueued audit %s to Redis RQ queue", audit_id)
            return
        except Exception as e:
            logger.warning("Redis unavailable (%s), falling back to in-memory queue", e)

    # In-memory execution
    logger.info("Dispatching audit %s to in-memory executor", audit_id)
    _executor.submit(_run_safe, execute_audit_job, audit_id)


def _run_safe(fn: Callable[[str], None], audit_id: str) -> None:
    try:
        fn(audit_id)
    except Exception as e:
        logger.exception("In-memory audit job failed for audit %s: %s", audit_id, e)
