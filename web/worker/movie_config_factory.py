"""Factory for creating default movie-generator configurations."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from movie_generator.constants import ProjectPaths

if TYPE_CHECKING:
    from movie_generator.config import Config as MovieConfig

logger = logging.getLogger(__name__)


def create_default_movie_config(config_path: Path | None = None) -> MovieConfig:
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
        PersonaConfig,
        VideoConfig,
        VoicevoxSynthesizerConfig,
        load_config,
    )
    from movie_generator.config import (
        Config as MovieConfig,
    )

    # If config_path is provided, load config from file
    if config_path and config_path.exists():
        logger.info(f"Loading config from {config_path}")
        config = load_config(config_path)

        # Override background and BGM with bundled assets
        # NOTE: Paths must be absolute for validation
        project_root = ProjectPaths.get_docker_project_root()
        config.video.background = BackgroundConfig(
            type="video",
            path=str(project_root / "assets/backgrounds/default-background.mp4"),
            fit="cover",
        )
        config.video.bgm = BgmConfig(
            path=str(project_root / "assets/bgm/default-bgm.noart.mp3"),
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
    project_root = ProjectPaths.get_docker_project_root()
    default_background = BackgroundConfig(
        type="video",
        path=str(project_root / "assets/backgrounds/default-background.mp4"),
        fit="cover",
    )

    # Default BGM
    # NOTE: Path must be absolute for BgmConfig validation
    default_bgm = BgmConfig(
        path=str(project_root / "assets/bgm/default-bgm.noart.mp3"),
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
