"""Test backward compatibility for composition.json generation.

Tests that composition.json can be generated without speaker/persona information,
maintaining compatibility with Remotion components that handle missing fields.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.script.phrases import Phrase
from movie_generator.video.remotion_renderer import build_composition_data, update_composition_json
from movie_generator.video.renderer import CompositionConfig


def test_composition_without_personas():
    """Test that composition.json can be generated without persona information."""
    with tempfile.TemporaryDirectory() as tmpdir:
        remotion_root = Path(tmpdir)
        (remotion_root / "public" / "audio").mkdir(parents=True)

        # Create phrases without persona_id
        phrases = [
            Phrase(text="Hello", duration=1.0),
            Phrase(text="World", duration=1.0),
        ]
        for i, p in enumerate(phrases):
            p.original_index = i

        audio_paths = [
            remotion_root / "public" / "audio" / "phrase_0000.wav",
            remotion_root / "public" / "audio" / "phrase_0001.wav",
        ]
        for path in audio_paths:
            path.touch()

        # Generate composition.json without personas parameter
        update_composition_json(
            remotion_root=remotion_root,
            phrases=phrases,
            audio_paths=audio_paths,
            slide_paths=None,
            project_name="test",
            personas=None,  # No personas provided
        )

        # Read and verify composition.json
        composition_path = remotion_root / "composition.json"
        with composition_path.open() as f:
            data = json.load(f)

        # Verify basic structure
        assert "phrases" in data
        assert len(data["phrases"]) == 2

        # Verify that persona fields are absent (backward compatibility)
        for phrase in data["phrases"]:
            assert "personaId" not in phrase
            assert "subtitleColor" not in phrase
            assert "characterImage" not in phrase


def test_composition_config_builder_without_personas():
    """Test CompositionConfig and build_composition_data without personas."""
    with tempfile.TemporaryDirectory() as tmpdir:
        remotion_root = Path(tmpdir)

        # Create phrases without persona_id
        phrases = [
            Phrase(text="Test phrase", duration=1.5),
        ]
        phrases[0].original_index = 0

        audio_paths = [Path("audio/phrase_0000.wav")]

        # Create configuration without personas
        config = CompositionConfig(
            phrases=phrases,
            audio_paths=audio_paths,
            slide_paths=None,
            project_name="test",
            personas=None,
        )

        # Build composition data
        composition_data = build_composition_data(config, remotion_root)

        # Verify structure
        assert "phrases" in composition_data
        assert len(composition_data["phrases"]) == 1

        # Verify no persona fields in output
        phrase = composition_data["phrases"][0]
        assert "personaId" not in phrase
        assert "subtitleColor" not in phrase


def test_composition_mixed_personas_and_none():
    """Test that phrases with and without persona_id work correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        remotion_root = Path(tmpdir)
        (remotion_root / "public" / "audio").mkdir(parents=True)

        # Mix of phrases with and without persona
        phrases = [
            Phrase(text="Has persona", persona_id="alice", persona_name="Alice", duration=1.0),
            Phrase(text="No persona", duration=1.0),
        ]
        for i, p in enumerate(phrases):
            p.original_index = i

        audio_paths = [
            remotion_root / "public" / "audio" / "phrase_0000.wav",
            remotion_root / "public" / "audio" / "phrase_0001.wav",
        ]
        for path in audio_paths:
            path.touch()

        personas = [{"id": "alice", "name": "Alice", "subtitle_color": "#FF0000"}]

        # Generate composition
        update_composition_json(
            remotion_root=remotion_root,
            phrases=phrases,
            audio_paths=audio_paths,
            slide_paths=None,
            project_name="test",
            personas=personas,
        )

        # Verify output
        composition_path = remotion_root / "composition.json"
        with composition_path.open() as f:
            data = json.load(f)

        # First phrase should have persona fields
        assert data["phrases"][0]["personaId"] == "alice"
        assert data["phrases"][0]["subtitleColor"] == "#FF0000"

        # Second phrase should NOT have persona fields
        assert "personaId" not in data["phrases"][1]
        assert "subtitleColor" not in data["phrases"][1]


def test_composition_without_background_and_bgm():
    """Test that composition.json can be generated without background and BGM.

    This verifies the spec requirement:
    'The system SHALL work with composition.json files that lack background and BGM information.'
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        remotion_root = Path(tmpdir)
        (remotion_root / "public" / "audio").mkdir(parents=True)

        # Create simple phrases
        phrases = [
            Phrase(text="Test phrase 1", duration=1.5),
            Phrase(text="Test phrase 2", duration=1.5),
        ]
        for i, p in enumerate(phrases):
            p.original_index = i

        audio_paths = [
            remotion_root / "public" / "audio" / "phrase_0000.wav",
            remotion_root / "public" / "audio" / "phrase_0001.wav",
        ]
        for path in audio_paths:
            path.touch()

        # Generate composition.json without background or BGM
        update_composition_json(
            remotion_root=remotion_root,
            phrases=phrases,
            audio_paths=audio_paths,
            slide_paths=None,
            project_name="test",
            background=None,  # No background provided
            bgm=None,  # No BGM provided
        )

        # Read and verify composition.json
        composition_path = remotion_root / "composition.json"
        with composition_path.open() as f:
            data = json.load(f)

        # Verify basic structure exists
        assert "title" in data
        assert "fps" in data
        assert "width" in data
        assert "height" in data
        assert "phrases" in data
        assert len(data["phrases"]) == 2

        # Verify that background and BGM fields are absent (backward compatibility)
        assert "background" not in data, "background field should not be present when None"
        assert "bgm" not in data, "bgm field should not be present when None"

        # Verify phrases are valid
        for phrase in data["phrases"]:
            assert "text" in phrase
            assert "duration" in phrase
            assert "audioFile" in phrase
