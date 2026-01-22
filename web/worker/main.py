"""Background worker for processing video generation jobs."""

import asyncio
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml

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
    config_path: Path | None = None
    mcp_config_path: Path | None = None

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

        # MCP agent configuration
        config_path_str = os.getenv("CONFIG_PATH")
        if config_path_str:
            self.config_path = Path(config_path_str)

        mcp_config_path_str = os.getenv("MCP_CONFIG_PATH")
        if mcp_config_path_str:
            self.mcp_config_path = Path(mcp_config_path_str)


def create_default_movie_config(config_path: Path | None = None) -> "MovieConfig":
    """Create default movie-generator Config with bundled assets.

    Args:
        config_path: Path to config file. If provided, loads config from file.
                    Otherwise creates default config with single persona.

    Returns:
        Config object with default background, BGM, and persona settings.
    """
    from movie_generator.config import (
        BackgroundConfig,
        BgmConfig,
        Config as MovieConfig,
        PersonaConfig,
        VideoConfig,
        VoicevoxSynthesizerConfig,
        load_config,
    )

    # If config_path is provided, load config from file
    if config_path and config_path.exists():
        logger.info(f"Loading config from {config_path}")
        config = load_config(config_path)

        # Override background and BGM with bundled assets
        # NOTE: Paths must be absolute for validation
        config.video.background = BackgroundConfig(
            type="video",
            path="/app/backgrounds/default-background.mp4",
            fit="cover",
        )
        config.video.bgm = BgmConfig(
            path="/app/bgm/default-bgm.noart.mp3",
            volume=0.15,  # Low volume to not overpower narration
            fade_in_seconds=2.0,
            fade_out_seconds=2.0,
            loop=True,
        )

        logger.info(f"Loaded config with {len(config.personas)} personas")
        if hasattr(config, "persona_pool") and config.persona_pool:
            logger.info(
                f"Persona pool enabled: selecting {config.persona_pool.count} from {len(config.personas)} personas"
            )

        return config

    # Otherwise, create default config with single persona
    logger.info("No config file provided, using default single-persona config")

    # Default persona: Zundamon
    # NOTE: Paths must be relative (will be resolved to public/ directory by renderer)
    default_persona = PersonaConfig(
        id="zundamon",
        name="ずんだもん",
        character="元気で明るい声のキャラクター",
        synthesizer=VoicevoxSynthesizerConfig(
            engine="voicevox",
            speaker_id=3,
            speed_scale=1.0,
        ),
        subtitle_color="#8FCF4F",  # Zundamon's green
        character_image="characters/zundamon/base.png",
        mouth_open_image="characters/zundamon/mouth_open.png",
        eye_close_image="characters/zundamon/eye_close.png",
        animation_style="sway",
    )

    # Default background: video background
    # NOTE: Path must be absolute for BackgroundConfig validation
    default_background = BackgroundConfig(
        type="video",
        path="/app/backgrounds/default-background.mp4",
        fit="cover",
    )

    # Default BGM
    # NOTE: Path must be absolute for BgmConfig validation
    default_bgm = BgmConfig(
        path="/app/bgm/default-bgm.noart.mp3",
        volume=0.15,  # Low volume to not overpower narration
        fade_in_seconds=2.0,
        fade_out_seconds=2.0,
        loop=True,
    )

    # Create video config with background and BGM
    video_config = VideoConfig(
        background=default_background,
        bgm=default_bgm,
    )

    # Create full config
    config = MovieConfig(
        video=video_config,
        personas=[default_persona],
    )

    return config


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
        now = datetime.now(UTC)

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
    """Wrapper for calling movie-generator.

    TODO: Replace subprocess calls with direct Python API calls.
    Current implementation uses subprocess which:
    - Cannot report detailed progress
    - Hides error details
    - Wastes resources spawning new processes

    Should be refactored to call functions directly with progress callbacks.
    """

    def __init__(self, job_data_dir: Path, config: Config) -> None:
        """Initialize wrapper."""
        self.job_data_dir = job_data_dir
        self.config = config
        self.job_data_dir.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: str) -> Path:
        """Get job directory path."""
        return self.job_data_dir / job_id

    def _count_script_items(self, script_path: Path) -> tuple[int, int]:
        """Count number of phrases and slides from script.

        Args:
            script_path: Path to script.yaml

        Returns:
            Tuple of (phrase_count, slide_count)
        """
        try:
            with open(script_path, encoding="utf-8") as f:
                script_data = yaml.safe_load(f)

            # Count narrations (phrases) in all sections
            phrase_count = 0
            for section in script_data.get("sections", []):
                narrations = section.get("narrations", [])
                phrase_count += len(narrations)

            # Slide count = section count
            slide_count = len(script_data.get("sections", []))

            return phrase_count, slide_count

        except Exception as e:
            logger.warning(f"Failed to count script items: {e}")
            return 0, 0

    async def _monitor_file_progress(
        self,
        directory: Path,
        pattern: str,
        total: int,
        progress_callback: callable,
        progress_start: int,
        progress_end: int,
        step_name: str,
        item_name: str,
    ) -> None:
        """Monitor file creation progress in a directory.

        Args:
            directory: Directory to monitor
            pattern: File pattern (e.g., "phrase_*.wav")
            total: Total number of files expected
            progress_callback: Callback for progress updates
            progress_start: Starting progress percentage
            progress_end: Ending progress percentage
            step_name: Step name for logging
            item_name: Item name for display (e.g., "音声", "スライド")
        """
        if total == 0:
            return

        last_count = 0
        poll_interval = 2  # seconds

        while True:
            try:
                if not directory.exists():
                    await asyncio.sleep(poll_interval)
                    continue

                # Count existing files matching pattern
                files = list(directory.glob(pattern))
                current_count = len(files)

                # Only update if count changed
                if current_count != last_count:
                    last_count = current_count

                    # Calculate progress percentage
                    if current_count >= total:
                        progress_pct = progress_end
                        message = f"{item_name}生成完了 ({current_count}/{total})"
                        await progress_callback(progress_pct, message, step_name)
                        break
                    else:
                        # Linear interpolation between start and end
                        progress_pct = progress_start + int(
                            (current_count / total) * (progress_end - progress_start)
                        )
                        message = f"{item_name}生成中 ({current_count}/{total})"
                        await progress_callback(progress_pct, message, step_name)

                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.warning(f"Error monitoring {item_name} progress: {e}")
                await asyncio.sleep(poll_interval)

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
            # Step 1: Generate script (0-20%)
            script_path = job_dir / "script.yaml"

            if script_path.exists():
                logger.info(f"Script already exists for job {job_id}, skipping generation")
                await progress_callback(20, "スクリプト既に存在", "script")
            else:
                await progress_callback(5, "スクリプトを生成中...", "script")
                logger.info(f"Generating script for job {job_id}")

                # Use direct API call instead of subprocess
                import os

                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

                def script_progress(current: int, total: int, message: str) -> None:
                    """Callback for script generation progress."""
                    # Map to 5-20% range
                    progress_percent = 5 + int((current / total) * 15) if total > 0 else 5
                    asyncio.create_task(
                        progress_callback(
                            progress_percent,
                            message,
                            "script",
                        )
                    )
                    logger.debug(f"Script progress: {current}/{total} - {message}")

                # Check if MCP agent mode should be used
                use_agent = (
                    self.config.mcp_config_path is not None and self.config.mcp_config_path.exists()
                )

                try:
                    if use_agent:
                        logger.info(
                            f"Using MCP agent mode with config: {self.config.mcp_config_path}"
                        )
                        from movie_generator.script import generate_script_from_url_with_agent  # type: ignore

                        script_path = await generate_script_from_url_with_agent(
                            url=url,
                            output_dir=job_dir,
                            mcp_config_path=self.config.mcp_config_path,
                            config_path=self.config.config_path,
                            api_key=api_key,
                            progress_callback=script_progress,
                        )
                    else:
                        logger.info("Using standard content fetching mode")
                        from movie_generator.script import generate_script_from_url  # type: ignore

                        script_path = await generate_script_from_url(
                            url=url,
                            output_dir=job_dir,
                            config_path=self.config.config_path,
                            api_key=api_key,
                            progress_callback=script_progress,
                        )
                except Exception as e:
                    logger.error(f"Script generation failed: {e}", exc_info=True)
                    raise RuntimeError(f"Script generation failed: {e}")

                await progress_callback(20, "スクリプト生成完了", "script")

            # Count phrases and slides from generated script
            phrase_count, slide_count = self._count_script_items(script_path)
            logger.info(f"Script has {phrase_count} phrases and {slide_count} slides")

            # Step 2: Generate audio (20-55%)
            audio_dir = job_dir / "audio"
            existing_audio_count = len(list(audio_dir.glob("*.wav"))) if audio_dir.exists() else 0

            if existing_audio_count >= phrase_count:
                logger.info(
                    f"Audio files already exist for job {job_id} ({existing_audio_count}/{phrase_count}), skipping generation"
                )
                await progress_callback(
                    55, f"音声既に存在 ({existing_audio_count}/{phrase_count})", "audio"
                )
            else:
                await progress_callback(
                    22, f"音声を生成中 ({existing_audio_count}/{phrase_count})", "audio"
                )
                logger.info(
                    f"Generating audio for job {job_id} (existing: {existing_audio_count}/{phrase_count})"
                )

                # Use direct API call instead of subprocess
                from movie_generator.audio import generate_audio_for_script  # type: ignore

                # Store latest progress to sync with async callback
                latest_progress = {
                    "percent": 22,
                    "message": f"音声を生成中 ({existing_audio_count}/{phrase_count})",
                }

                def audio_progress(current: int, total: int, message: str) -> None:
                    """Callback for audio generation progress."""
                    # Map to 22-55% range
                    progress_percent = 22 + int((current / total) * 33) if total > 0 else 22
                    latest_progress["percent"] = progress_percent
                    latest_progress["message"] = f"音声を生成中 ({current}/{total})"
                    logger.debug(f"Audio progress: {current}/{total}")

                # Load config for multi-speaker support
                # CRITICAL: Without config, all voices default to Zundamon (speaker_id=3)
                audio_config = create_default_movie_config(self.config.config_path)
                logger.info(f"Audio config loaded with {len(audio_config.personas)} personas")

                # Run audio generation in thread pool to avoid blocking
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None,
                    generate_audio_for_script,
                    script_path,
                    job_dir,
                    None,  # config_path (use config object instead)
                    audio_config,  # config with personas for multi-speaker support
                    None,  # scenes
                    audio_progress,
                )

                # Update final progress
                await progress_callback(
                    latest_progress["percent"], latest_progress["message"], "audio"
                )

            # Step 3: Generate slides (55-80%)
            slides_dir = job_dir / "slides"
            existing_slide_count = len(list(slides_dir.glob("*.png"))) if slides_dir.exists() else 0

            if existing_slide_count >= slide_count:
                logger.info(
                    f"Slide files already exist for job {job_id} ({existing_slide_count}/{slide_count}), skipping generation"
                )
                await progress_callback(
                    80, f"スライド既に存在 ({existing_slide_count}/{slide_count})", "slides"
                )
            else:
                await progress_callback(
                    57, f"スライドを生成中 ({existing_slide_count}/{slide_count})", "slides"
                )
                logger.info(
                    f"Generating slides for job {job_id} (existing: {existing_slide_count}/{slide_count})"
                )

                # Use direct API call instead of subprocess
                from movie_generator.slides import generate_slides_for_script  # type: ignore
                import os

                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

                def slides_progress(current: int, total: int, message: str) -> None:
                    """Callback for slides generation progress."""
                    # Map to 57-80% range
                    progress_percent = 57 + int((current / total) * 23) if total > 0 else 57
                    asyncio.create_task(
                        progress_callback(
                            progress_percent,
                            f"スライドを生成中 ({current}/{total})",
                            "slides",
                        )
                    )
                    logger.debug(f"Slides progress: {current}/{total}")

                try:
                    # Load config to get resolution
                    movie_config = create_default_movie_config(self.config.config_path)

                    await generate_slides_for_script(
                        script_path=script_path,
                        output_dir=job_dir,
                        api_key=api_key,
                        progress_callback=slides_progress,
                        resolution=movie_config.style.resolution,
                    )
                except Exception as e:
                    logger.error(f"Slide generation failed: {e}", exc_info=True)
                    raise RuntimeError(f"Slide generation failed: {e}")

            # Step 4: Render video (80-100%)
            output_path = job_dir / "output.mp4"

            if output_path.exists():
                logger.info(f"Video file already exists for job {job_id}, skipping rendering")
                await progress_callback(100, "動画既に存在", "video")
                return output_path

            await progress_callback(82, "動画をレンダリング中...", "video")
            logger.info(f"Rendering video for job {job_id}")

            # Use direct API call instead of subprocess
            from movie_generator.video import render_video_for_script  # type: ignore

            # Capture the event loop for use in the callback
            loop = asyncio.get_running_loop()

            def video_progress(current: int, total: int, message: str) -> None:
                """Callback for video rendering progress."""
                # Map to 82-100% range
                progress_percent = 82 + int((current / total) * 18) if total > 0 else 82
                # Use run_coroutine_threadsafe since this callback runs in executor thread
                asyncio.run_coroutine_threadsafe(
                    progress_callback(
                        progress_percent,
                        message,
                        "video",
                    ),
                    loop,
                )
                logger.debug(f"Video progress: {current}/{total} - {message}")

            try:
                # Create config with background, BGM, and persona settings
                # Use CONFIG_PATH if provided, otherwise use default single-persona config
                movie_config = create_default_movie_config(self.config.config_path)
                logger.info("Using movie config with background, BGM, and persona")

                # Run in executor since it's synchronous and may take a while
                await loop.run_in_executor(
                    None,
                    render_video_for_script,
                    script_path,
                    output_path,
                    None,  # output_dir
                    None,  # config_path
                    movie_config,  # config with background, bgm, persona
                    None,  # scenes
                    False,  # show_progress
                    video_progress,
                )
            except Exception as e:
                logger.error(f"Video rendering failed: {e}", exc_info=True)
                raise RuntimeError(f"Video rendering failed: {e}")

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
            "started_at": job.get("started_at") or datetime.now(UTC).isoformat() + "Z",
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
                    "completed_at": datetime.now(UTC).isoformat() + "Z",
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
                    "completed_at": datetime.now(UTC).isoformat() + "Z",
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
                            "completed_at": datetime.now(UTC).isoformat() + "Z",
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
