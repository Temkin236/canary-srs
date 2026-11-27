import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from app.core.config import settings

logger = logging.getLogger(__name__)

# Dedicated thread pool for in-memory queue fallback (local development / offline testing)
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="canary-worker")


def enqueue_audit_job(audit_id: str) -> None:
    """
    Enqueues an audit execution job.
    Uses Redis + RQ if configured and available.
    In development mode, falls back to the in-memory background executor.
    In production mode, raises an error if Redis is unreachable to prevent silent failure.
    Requirements FR-31, FR-32, FR-33.
    """
    from app.jobs.runner import execute_audit_job

    is_production = settings.ENVIRONMENT.lower() == "production"

    if not settings.USE_IN_MEMORY_QUEUE or is_production:
        try:
            import redis
            from rq import Queue

            redis_conn = redis.from_url(settings.REDIS_URL)
            redis_conn.ping()
            q = Queue("canary-audits", connection=redis_conn)
            # 20 minutes execution timeout (FR-33) with result TTL for history
            q.enqueue(
                execute_audit_job,
                audit_id,
                job_timeout=1200,
                result_ttl=86400,  # Retain job result for 24h
                failure_ttl=604800,  # Retain failed job logs for 7 days
            )
            logger.info("Enqueued audit %s to Redis RQ queue", audit_id)
            return
        except Exception as e:
            if is_production:
                logger.error(
                    "CRITICAL: Redis queue unavailable in production for audit %s: %s",
                    audit_id,
                    e,
                )
                raise RuntimeError(
                    f"Production Redis queue unavailable. Cannot enqueue audit {audit_id}: {e}"
                ) from e
            logger.warning(
                "Redis unavailable in development (%s), falling back to in-memory queue", e
            )

    # In-memory execution (development / test only)
    logger.info("Dispatching audit %s to in-memory executor", audit_id)
    _executor.submit(_run_safe, execute_audit_job, audit_id)


def _run_safe(fn: Callable[[str], None], audit_id: str) -> None:
    try:
        fn(audit_id)
    except Exception as e:
        logger.exception("In-memory audit job failed for audit %s: %s", audit_id, e)
