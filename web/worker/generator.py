"""Movie generation wrapper for background workers."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import yaml

try:
    # When run as module
    from .movie_config_factory import create_default_movie_config
    from .settings import WorkerSettings
except ImportError:
    # When run as script from worker directory
    from movie_config_factory import create_default_movie_config
    from settings import WorkerSettings

logger = logging.getLogger(__name__)


class MovieGeneratorWrapper:
    """Wrapper for calling movie-generator.

    TODO: Replace subprocess calls with direct Python API calls.
    Current implementation uses subprocess which:
    - Cannot report detailed progress
    - Hides error details
    - Wastes resources spawning new processes

    Should be refactored to call functions directly with progress callbacks.
    """

    def __init__(self, job_data_dir: Path, config: WorkerSettings) -> None:
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
                        from movie_generator.script import (
                            generate_script_from_url_with_agent,  # type: ignore
                        )

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
                import os

                from movie_generator.slides import generate_slides_for_script  # type: ignore

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
                    # Load config to get resolution and model
                    movie_config = create_default_movie_config(self.config.config_path)

                    await generate_slides_for_script(
                        script_path=script_path,
                        output_dir=job_dir,
                        api_key=api_key,
                        model=movie_config.slides.llm.model,
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
