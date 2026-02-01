"""Test transition configuration integration."""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.config import Config
from movie_generator.project import Project
from movie_generator.script.phrases import Phrase
from movie_generator.video.remotion_renderer import update_composition_json


def test_composition_json_includes_transition_config(tmp_path: Path) -> None:
    """Test that composition.json includes transition configuration."""
    # Create project with custom transition config
    config = Config()
    config.video.transition.type = "slide"
    config.video.transition.duration_frames = 30
    config.video.transition.timing = "spring"

    project = Project("test_project", root_dir=tmp_path)
    project.create(config)

    # Setup Remotion project
    remotion_dir = project.setup_remotion_project()

    # Check composition.json
    composition_path = remotion_dir / "composition.json"
    assert composition_path.exists()

    with composition_path.open("r") as f:
        composition_data = json.load(f)

    # Verify transition config is present
    assert "transition" in composition_data
    assert composition_data["transition"]["type"] == "slide"
    assert composition_data["transition"]["duration_frames"] == 30
    assert composition_data["transition"]["timing"] == "spring"


def test_update_composition_json_preserves_transition_config(tmp_path: Path) -> None:
    """Test that updating composition.json preserves transition configuration."""
    # Create project
    config = Config()
    config.video.transition.type = "wipe"
    config.video.transition.duration_frames = 20

    project = Project("test_project", root_dir=tmp_path)
    project.create(config)
    remotion_dir = project.setup_remotion_project()

    # Create phrase objects
    phrase_objs = [
        Phrase(text="Hello", duration=1.5, start_time=0.0, section_index=0, original_index=0),
        Phrase(text="World", duration=1.2, start_time=1.5, section_index=0, original_index=1),
    ]

    # Create audio and slide paths
    audio_paths = [
        project.project_dir / "audio" / "hello.wav",
        project.project_dir / "audio" / "world.wav",
    ]
    slide_paths = [
        project.project_dir / "slides" / "ja" / "slide1.png",
        project.project_dir / "slides" / "ja" / "slide2.png",
    ]

    # Update composition.json using centralized function
    transition_config = config.video.transition.model_dump()
    update_composition_json(
        remotion_root=remotion_dir,
        phrases=phrase_objs,
        audio_paths=audio_paths,
        slide_paths=slide_paths,
        project_name=project.name,
        transition=transition_config,
        fps=config.style.fps,
        resolution=config.style.resolution,
    )

    # Check composition.json
    composition_path = remotion_dir / "composition.json"
    with composition_path.open("r") as f:
        composition_data = json.load(f)

    # Verify transition config is still present
    assert "transition" in composition_data
    assert composition_data["transition"]["type"] == "wipe"
    assert composition_data["transition"]["duration_frames"] == 20
    assert composition_data["transition"]["timing"] == "linear"  # default timing

    # Verify phrases were updated
    assert len(composition_data["phrases"]) == 2
    assert composition_data["phrases"][0]["text"] == "Hello"


def test_default_transition_config_when_not_specified(tmp_path: Path) -> None:
    """Test that default transition config is used when not specified."""
    # Create project with default config
    project = Project("test_project", root_dir=tmp_path)
    project.create()  # No config specified

    # Setup Remotion project
    remotion_dir = project.setup_remotion_project()

    # Check composition.json
    composition_path = remotion_dir / "composition.json"
    with composition_path.open("r") as f:
        composition_data = json.load(f)

    # Verify default transition config
    assert "transition" in composition_data
    assert composition_data["transition"]["type"] == "fade"
    assert composition_data["transition"]["duration_frames"] == 15
    assert composition_data["transition"]["timing"] == "linear"
