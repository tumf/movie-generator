"""Tests for background and BGM configuration."""

import pytest
from pydantic import ValidationError

from movie_generator.config import BackgroundConfig, BgmConfig, Config


class TestBackgroundConfig:
    """Test BackgroundConfig validation."""

    def test_image_background_valid(self) -> None:
        """Test valid image background configuration."""
        bg = BackgroundConfig(type="image", path="assets/backgrounds/bg.png")
        assert bg.type == "image"
        assert bg.path == "assets/backgrounds/bg.png"
        assert bg.fit == "cover"  # default

    def test_video_background_valid(self) -> None:
        """Test valid video background configuration."""
        bg = BackgroundConfig(type="video", path="assets/backgrounds/bg.mp4", fit="contain")
        assert bg.type == "video"
        assert bg.path == "assets/backgrounds/bg.mp4"
        assert bg.fit == "contain"

    def test_fit_options(self) -> None:
        """Test all fit options are valid."""
        for fit in ["cover", "contain", "fill"]:
            bg = BackgroundConfig(type="image", path="test.png", fit=fit)
            assert bg.fit == fit

    def test_invalid_fit(self) -> None:
        """Test invalid fit value raises error."""
        with pytest.raises(ValidationError):
            BackgroundConfig(type="image", path="test.png", fit="invalid")


class TestBgmConfig:
    """Test BgmConfig validation."""

    def test_bgm_defaults(self) -> None:
        """Test BGM configuration with defaults."""
        bgm = BgmConfig(path="assets/bgm/music.mp3")
        assert bgm.path == "assets/bgm/music.mp3"
        assert bgm.volume == 0.3
        assert bgm.fade_in_seconds == 2.0
        assert bgm.fade_out_seconds == 2.0
        assert bgm.loop is True

    def test_bgm_custom_values(self) -> None:
        """Test BGM configuration with custom values."""
        bgm = BgmConfig(
            path="music.mp3",
            volume=0.5,
            fade_in_seconds=3.0,
            fade_out_seconds=4.0,
            loop=False,
        )
        assert bgm.volume == 0.5
        assert bgm.fade_in_seconds == 3.0
        assert bgm.fade_out_seconds == 4.0
        assert bgm.loop is False

    def test_volume_range(self) -> None:
        """Test volume must be in range 0.0-1.0."""
        # Valid
        BgmConfig(path="test.mp3", volume=0.0)
        BgmConfig(path="test.mp3", volume=1.0)

        # Invalid
        with pytest.raises(ValidationError):
            BgmConfig(path="test.mp3", volume=-0.1)
        with pytest.raises(ValidationError):
            BgmConfig(path="test.mp3", volume=1.1)

    def test_fade_seconds_positive(self) -> None:
        """Test fade seconds must be non-negative."""
        BgmConfig(path="test.mp3", fade_in_seconds=0.0)
        with pytest.raises(ValidationError):
            BgmConfig(path="test.mp3", fade_in_seconds=-1.0)


class TestVideoConfigWithBackgroundBgm:
    """Test VideoConfig with background and BGM fields."""

    def test_video_config_with_background(self) -> None:
        """Test VideoConfig with background field."""
        config = Config(
            video={
                "background": {"type": "image", "path": "bg.png"},
            }
        )
        assert config.video.background is not None
        assert config.video.background.type == "image"
        assert config.video.background.path == "bg.png"

    def test_video_config_with_bgm(self) -> None:
        """Test VideoConfig with BGM field."""
        config = Config(
            video={
                "bgm": {"path": "music.mp3", "volume": 0.2},
            }
        )
        assert config.video.bgm is not None
        assert config.video.bgm.path == "music.mp3"
        assert config.video.bgm.volume == 0.2

    def test_video_config_with_both(self) -> None:
        """Test VideoConfig with both background and BGM."""
        config = Config(
            video={
                "background": {"type": "video", "path": "bg.mp4"},
                "bgm": {"path": "music.mp3"},
            }
        )
        assert config.video.background is not None
        assert config.video.bgm is not None

    def test_video_config_without_background_bgm(self) -> None:
        """Test VideoConfig without background/BGM (backward compatibility)."""
        config = Config()
        assert config.video.background is None
        assert config.video.bgm is None
