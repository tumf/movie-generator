"""Background worker for processing video generation jobs."""

from __future__ import annotations

import asyncio
import logging

try:
    # When run as module: python -m worker.main
    from .settings import WorkerSettings
    from .worker import Worker
except ImportError:
    # When run as script: python main.py (Docker CMD)
    from settings import WorkerSettings
    from worker import Worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    config = WorkerSettings()
    worker = Worker(config)

    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
