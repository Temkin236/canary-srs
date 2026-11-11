import logging
import signal
import sys
import time

import redis
from rq import Connection, Queue, Worker

from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [canary-worker] %(message)s",
)
logger = logging.getLogger("canary-worker")

LISTEN_QUEUES = ["canary-audits"]


def get_redis_connection(max_retries: int = 10, retry_delay_seconds: int = 3) -> redis.Redis:
    """
    Connects to Redis with exponential backoff to handle container orchestrator
    spin-up latency where the worker may start seconds before Redis is ready.
    """
    redis_url = settings.REDIS_URL
    # Mask password for secure logging
    safe_url = redis_url.split("@")[-1] if "@" in redis_url else redis_url
    logger.info("Connecting to Redis queue service at %s...", safe_url)

    for attempt in range(1, max_retries + 1):
        try:
            conn = redis.from_url(redis_url)
            conn.ping()
            logger.info("Successfully connected to Redis.")
            return conn
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(
                "Redis connection attempt %d/%d failed: %s. Retrying in %ds...",
                attempt,
                max_retries,
                e,
                retry_delay_seconds,
            )
            time.sleep(retry_delay_seconds)

    logger.critical("Failed to connect to Redis after %d attempts. Terminating.", max_retries)
    sys.exit(1)


def handle_shutdown(signum, frame):
    logger.info("Received termination signal (%s). Gracefully stopping worker...", signum)
    sys.exit(0)


def run_worker():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    logger.info("Starting Canary SRS Background Worker (Env: %s)", settings.ENVIRONMENT)
    redis_conn = get_redis_connection()

    with Connection(redis_conn):
        queues = [Queue(name) for name in LISTEN_QUEUES]
        worker = Worker(queues, connection=redis_conn, name=f"canary-worker-{settings.ENVIRONMENT}")
        logger.info("Worker listening for audit jobs on queues: %s", LISTEN_QUEUES)
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    run_worker()
