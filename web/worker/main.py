"""Background worker for processing video generation jobs."""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Config:
    """Worker configuration."""

    pocketbase_url: str = "http://localhost:8090"
    max_concurrent_jobs: int = 2
    worker_poll_interval: int = 5  # seconds
    job_data_dir: Path = Path("/app/data/jobs")

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        import os

        self.pocketbase_url = os.getenv("POCKETBASE_URL", self.pocketbase_url)
        self.max_concurrent_jobs = int(
            os.getenv("MAX_CONCURRENT_JOBS", str(self.max_concurrent_jobs))
        )
        self.worker_poll_interval = int(
            os.getenv("WORKER_POLL_INTERVAL", str(self.worker_poll_interval))
        )
        job_data_dir_str = os.getenv("JOB_DATA_DIR", str(self.job_data_dir))
        self.job_data_dir = Path(job_data_dir_str)


class PocketBaseClient:
    """Client for interacting with PocketBase."""

    def __init__(self, base_url: str) -> None:
        """Initialize PocketBase client."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_pending_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get pending jobs."""
        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": "status = 'pending'",
                "sort": "created",
                "perPage": limit,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    async def update_job(self, job_id: str, update_data: dict[str, Any]) -> dict[str, Any]:
        """Update a job."""
        response = await self.client.patch(
            f"/api/collections/jobs/records/{job_id}",
            json=update_data,
        )
        response.raise_for_status()
        return response.json()

    async def delete_expired_jobs(self) -> int:
        """Delete jobs that have passed their expiration time."""
        now = datetime.utcnow()

        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": f"expires_at < '{now.isoformat()}Z'",
                "perPage": 100,
            },
        )
        response.raise_for_status()
        data = response.json()
        jobs = data.get("items", [])

        deleted_count = 0
        for job in jobs:
            try:
                await self.client.delete(f"/api/collections/jobs/records/{job['id']}")
                deleted_count += 1
                logger.info(f"Deleted expired job {job['id']}")
            except httpx.HTTPError:
                continue

        return deleted_count


class MovieGeneratorWrapper:
    """Wrapper for calling movie-generator."""

    def __init__(self, job_data_dir: Path) -> None:
        """Initialize wrapper."""
        self.job_data_dir = job_data_dir
        self.job_data_dir.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: str) -> Path:
        """Get job directory path."""
        return self.job_data_dir / job_id

    async def generate_video(self, job_id: str, url: str, progress_callback: callable) -> Path:
        """Generate video from URL.

        Args:
            job_id: Job ID
            url: URL to process
            progress_callback: Async callback function for progress updates

        Returns:
            Path to generated video file

        Raises:
            Exception: If video generation fails
        """
        job_dir = self.get_job_dir(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Generate script (0-30%)
            await progress_callback(10, "スクリプトを生成中...", "script")
            script_path = job_dir / "script.yaml"

            # Import movie_generator here to avoid import issues
            sys.path.insert(0, "/app/src")
            from movie_generator.cli import cli

            # Run script generation
            import subprocess

            logger.info(f"Generating script for job {job_id}")
            result = subprocess.run(
                [
                    "movie-generator",
                    "script",
                    "create",
                    url,
                    "--output",
                    str(job_dir),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Script generation failed: {result.stderr}")

            await progress_callback(30, "スクリプト生成完了", "script")

            # Step 2: Generate audio (30-60%)
            await progress_callback(40, "音声を生成中...", "audio")
            logger.info(f"Generating audio for job {job_id}")

            result = subprocess.run(
                [
                    "movie-generator",
                    "audio",
                    "generate",
                    str(script_path),
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Audio generation failed: {result.stderr}")

            await progress_callback(60, "音声生成完了", "audio")

            # Step 3: Generate slides (60-80%)
            await progress_callback(65, "スライドを生成中...", "slides")
            logger.info(f"Generating slides for job {job_id}")

            result = subprocess.run(
                [
                    "movie-generator",
                    "slides",
                    "generate",
                    str(script_path),
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Slide generation failed: {result.stderr}")

            await progress_callback(80, "スライド生成完了", "slides")

            # Step 4: Render video (80-100%)
            await progress_callback(85, "動画をレンダリング中...", "video")
            logger.info(f"Rendering video for job {job_id}")

            output_path = job_dir / "output.mp4"
            result = subprocess.run(
                [
                    "movie-generator",
                    "video",
                    "render",
                    str(script_path),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                timeout=1200,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Video rendering failed: {result.stderr}")

            await progress_callback(100, "動画生成完了", "video")

            if not output_path.exists():
                raise RuntimeError("Video file was not created")

            return output_path

        except Exception as e:
            logger.error(f"Video generation failed for job {job_id}: {e}", exc_info=True)
            raise


class Worker:
    """Background worker for processing jobs."""

    def __init__(self, config: Config) -> None:
        """Initialize worker."""
        self.config = config
        self.pb_client = PocketBaseClient(config.pocketbase_url)
        self.generator = MovieGeneratorWrapper(config.job_data_dir)
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

        # Update job to processing status
        await self.pb_client.update_job(
            job_id,
            {
                "status": "processing",
                "progress": 0,
                "started_at": datetime.utcnow().isoformat() + "Z",
            },
        )

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
                    "completed_at": datetime.utcnow().isoformat() + "Z",
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
                    "completed_at": datetime.utcnow().isoformat() + "Z",
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

    async def run(self) -> None:
        """Run the worker loop."""
        self.running = True
        logger.info("Worker started")

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


async def main() -> None:
    """Main entry point."""
    config = Config()
    worker = Worker(config)

    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
