"""Background worker for processing video generation jobs."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

try:
    # When run as module: python -m worker.worker
    from .generator import MovieGeneratorWrapper
    from .pocketbase_client import PocketBaseClient
    from .settings import WorkerSettings
except ImportError:
    # When run as script from worker directory
    from generator import MovieGeneratorWrapper
    from pocketbase_client import PocketBaseClient
    from settings import WorkerSettings

logger = logging.getLogger(__name__)


class Worker:
    """Background worker for processing jobs."""

    def __init__(self, config: WorkerSettings) -> None:
        """Initialize worker."""
        self.config = config
        self.pb_client = PocketBaseClient(config.pocketbase_url)
        self.generator = MovieGeneratorWrapper(config.job_data_dir, config)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_jobs)
        self.running = False

    async def process_job(self, job: dict[str, Any]) -> None:
        """Process a single job.

        Args:
            job: Job record from PocketBase
        """
        job_id = job["id"]
        url = job["url"]

        logger.info(f"Starting job {job_id}")

        # Check if this is a resumed job
        is_resumed = job.get("started_at") is not None and job.get("status") == "pending"

        if is_resumed:
            logger.info(f"Resuming job {job_id} (was at {job.get('current_step', 'unknown')} step)")

        # Update job to processing status
        # Keep current progress when resuming, start at 0 for new jobs
        update_data = {
            "status": "processing",
            "started_at": job.get("started_at")
            or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "progress_message": "再開中..." if is_resumed else "開始中...",
        }
        # Only set progress to 0 for new jobs
        if not is_resumed:
            update_data["progress"] = 0

        await self.pb_client.update_job(job_id, update_data)

        async def update_progress(progress: int, message: str, step: str) -> None:
            """Update job progress."""
            await self.pb_client.update_job(
                job_id,
                {
                    "progress": progress,
                    "progress_message": message,
                    "current_step": step,
                },
            )

        try:
            # Generate video
            video_path = await self.generator.generate_video(job_id, url, update_progress)

            # Get file size
            video_size = video_path.stat().st_size

            # Update job to completed status
            await self.pb_client.update_job(
                job_id,
                {
                    "status": "completed",
                    "progress": 100,
                    "video_path": str(video_path),
                    "video_size": video_size,
                    "completed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                },
            )

            logger.info(f"Completed job {job_id}")

        except Exception as e:
            logger.error(f"Failed job {job_id}: {e}", exc_info=True)

            # Update job to failed status
            await self.pb_client.update_job(
                job_id,
                {
                    "status": "failed",
                    "error_message": str(e),
                    "completed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                },
            )

    async def process_job_with_semaphore(self, job: dict[str, Any]) -> None:
        """Process job with semaphore control.

        Args:
            job: Job record from PocketBase
        """
        async with self.semaphore:
            await self.process_job(job)

    async def cleanup_expired_jobs(self) -> None:
        """Clean up expired jobs periodically."""
        while self.running:
            try:
                deleted_count = await self.pb_client.delete_expired_jobs()
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired jobs")
            except Exception as e:
                logger.error(f"Failed to cleanup expired jobs: {e}")

            # Run cleanup every hour
            await asyncio.sleep(3600)

    async def cleanup_stuck_jobs(self, resume: bool = True) -> None:
        """Clean up stuck processing jobs on startup.

        Args:
            resume: If True, reset stuck jobs to pending for resumption.
                   If False, mark stuck jobs as failed.
        """
        try:
            logger.info("Checking for stuck jobs...")
            # Find jobs stuck in processing state
            response = await self.pb_client.client.get(
                "/api/collections/jobs/records",
                params={
                    "filter": "status = 'processing'",
                    "perPage": 100,
                },
            )
            response.raise_for_status()
            stuck_jobs = response.json().get("items", [])

            logger.info(f"Found {len(stuck_jobs)} stuck jobs")

            for job in stuck_jobs:
                job_id = job["id"]

                if resume:
                    # Reset to pending for resumption
                    logger.info(
                        f"Resuming stuck job {job_id} (was at {job.get('current_step', 'unknown')} step, {job.get('progress', 0)}%)"
                    )
                    await self.pb_client.update_job(
                        job_id,
                        {
                            "status": "pending",
                            # Keep progress and current_step for reference
                            # The job will restart from the beginning, but already-generated files will be skipped
                        },
                    )
                else:
                    # Mark as failed
                    logger.warning(f"Found stuck job {job_id}, marking as failed")
                    await self.pb_client.update_job(
                        job_id,
                        {
                            "status": "failed",
                            "error_message": "Job was interrupted by worker restart",
                            "completed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        },
                    )

            if stuck_jobs:
                action = "resumed" if resume else "marked as failed"
                logger.info(f"Cleaned up {len(stuck_jobs)} stuck jobs ({action})")
            else:
                logger.info("No stuck jobs found")

        except Exception as e:
            logger.error(f"Failed to cleanup stuck jobs: {e}", exc_info=True)

    async def run(self) -> None:
        """Run the worker loop."""
        self.running = True
        logger.info("Worker started")

        # Clean up stuck jobs from previous run
        # resume=True: Reset stuck jobs to pending for automatic resumption
        # resume=False: Mark stuck jobs as failed
        await self.cleanup_stuck_jobs(resume=True)

        # Start cleanup task
        cleanup_task = asyncio.create_task(self.cleanup_expired_jobs())

        try:
            while self.running:
                try:
                    # Get pending jobs
                    jobs = await self.pb_client.get_pending_jobs(limit=10)

                    if jobs:
                        logger.info(f"Found {len(jobs)} pending jobs")

                        # Process jobs concurrently (up to max_concurrent_jobs)
                        tasks = [
                            asyncio.create_task(self.process_job_with_semaphore(job))
                            for job in jobs
                        ]

                        # Don't wait for all to complete, just start them
                        # They will run in the background with semaphore control

                    # Wait before next poll
                    await asyncio.sleep(self.config.worker_poll_interval)

                except Exception as e:
                    logger.error(f"Error in worker loop: {e}", exc_info=True)
                    await asyncio.sleep(self.config.worker_poll_interval)

        finally:
            self.running = False
            cleanup_task.cancel()
            await self.pb_client.close()
            logger.info("Worker stopped")

    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
