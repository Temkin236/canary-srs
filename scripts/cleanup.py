#!/usr/bin/env python3
"""
Canary SRS — Retention Cleanup CLI Script (FR-42)
Run periodically (e.g. daily cron job or container task) to purge expired audits.
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("canary-cleanup")

try:
    from app.jobs.cleanup import run_retention_cleanup
except ImportError:
    # If run from repository root, add backend to sys.path
    import os

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
    )
    from app.jobs.cleanup import run_retention_cleanup


def main():
    logger.info("Starting scheduled Canary SRS data retention cleanup...")
    count = run_retention_cleanup()
    logger.info("Retention cleanup completed successfully. Purged audits: %d", count)


if __name__ == "__main__":
    main()
