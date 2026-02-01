"""Test transition configuration integration."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.config import Config
from movie_generator.project import Project


@patch("movie_generator.project.subprocess.run")
@patch("movie_generator.project._ensure_nodejs_available")
@patch("movie_generator.project._ensure_pnpm_available")
def test_composition_json_includes_transition_config(
    mock_ensure_pnpm: MagicMock,
    mock_ensure_nodejs: MagicMock,
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    """Test that composition.json includes transition configuration."""
    # Setup mocks
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    # Create project with custom transition config
    config = Config()
    config.video.transition.type = "slide"
    config.video.transition.duration_frames = 30
    config.video.transition.timing = "spring"

    project = Project("test_project", root_dir=tmp_path)
    project.create(config)

    # Create minimal remotion directory structure for mocked setup
    remotion_dir = project.project_dir / "remotion"
    remotion_dir.mkdir(parents=True, exist_ok=True)
    (remotion_dir / "package.json").write_text('{"name": "remotion-template"}')

    # Setup Remotion project
    result_dir = project.setup_remotion_project()

    # Check composition.json
    composition_path = result_dir / "composition.json"
    assert composition_path.exists()

    with composition_path.open("r") as f:
        composition_data = json.load(f)

    # Verify transition config is present
    assert "transition" in composition_data
    assert composition_data["transition"]["type"] == "slide"
    assert composition_data["transition"]["duration_frames"] == 30
    assert composition_data["transition"]["timing"] == "spring"


@patch("movie_generator.project.subprocess.run")
@patch("movie_generator.project._ensure_nodejs_available")
@patch("movie_generator.project._ensure_pnpm_available")
def test_setup_remotion_project_with_phrases_preserves_transition_config(
    mock_ensure_pnpm: MagicMock,
    mock_ensure_nodejs: MagicMock,
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    """Test that setup_remotion_project with existing phrases preserves transition configuration."""
    # Setup mocks
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    # Create project
    config = Config()
    config.video.transition.type = "wipe"
    config.video.transition.duration_frames = 20

    project = Project("test_project", root_dir=tmp_path)
    project.create(config)

    # Save phrases data before setup
    from movie_generator.script.phrases import Phrase

    phrases = [
        Phrase(
            text="Hello",
            section_index=0,
            original_index=0,
            duration=1.5,
            start_time=0.0,
        ),
        Phrase(
            text="World",
            section_index=1,
            original_index=1,
            duration=1.2,
            start_time=1.5,
        ),
    ]
    project.save_phrases(phrases)

    # Create minimal remotion directory structure for mocked setup
    remotion_dir = project.project_dir / "remotion"
    remotion_dir.mkdir(parents=True, exist_ok=True)
    (remotion_dir / "package.json").write_text('{"name": "remotion-template"}')

    # Setup remotion project (should load phrases from phrases.json)
    project.setup_remotion_project()

    # Check composition.json
    composition_path = project.project_dir / "remotion" / "composition.json"
    with composition_path.open("r") as f:
        composition_data = json.load(f)

    # Verify transition config is still present
    assert "transition" in composition_data
    assert composition_data["transition"]["type"] == "wipe"
    assert composition_data["transition"]["duration_frames"] == 20
    assert composition_data["transition"]["timing"] == "linear"  # default timing

    # Verify phrases were loaded
    assert len(composition_data["phrases"]) == 2
    assert composition_data["phrases"][0]["text"] == "Hello"
    assert composition_data["phrases"][1]["text"] == "World"


@patch("movie_generator.project.subprocess.run")
@patch("movie_generator.project._ensure_nodejs_available")
@patch("movie_generator.project._ensure_pnpm_available")
def test_default_transition_config_when_not_specified(
    mock_ensure_pnpm: MagicMock,
    mock_ensure_nodejs: MagicMock,
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    """Test that default transition config is used when not specified."""
    # Setup mocks
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    # Create project with default config
    project = Project("test_project", root_dir=tmp_path)
    project.create()  # No config specified

    # Create minimal remotion directory structure for mocked setup
    remotion_dir = project.project_dir / "remotion"
    remotion_dir.mkdir(parents=True, exist_ok=True)
    (remotion_dir / "package.json").write_text('{"name": "remotion-template"}')

    # Setup Remotion project
    result_dir = project.setup_remotion_project()

    # Check composition.json
    composition_path = result_dir / "composition.json"
    with composition_path.open("r") as f:
        composition_data = json.load(f)

    # Verify default transition config
    assert "transition" in composition_data
    assert composition_data["transition"]["type"] == "fade"
    assert composition_data["transition"]["duration_frames"] == 15
    assert composition_data["transition"]["timing"] == "linear"
