"""Tests for persona voice fallback and validation."""

import logging
from typing import Any

import pytest

from movie_generator.audio.core import validate_persona_ids
from movie_generator.script.phrases import Phrase


class TestValidatePersonaIds:
    """Test validate_persona_ids function."""

    def test_all_valid_persona_ids(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that no warnings are logged when all persona_ids are valid."""
        phrases = [
            Phrase(text="Hello", persona_id="alice"),
            Phrase(text="World", persona_id="bob"),
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        assert unknown_ids == []
        assert len(caplog.records) == 0

    def test_unknown_persona_id_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that warning is logged for unknown persona_id."""
        phrases = [
            Phrase(text="Hello", persona_id="alice"),
            Phrase(text="World", persona_id="charlie"),  # Unknown
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        assert unknown_ids == ["charlie"]
        assert len(caplog.records) == 1
        assert "Unknown persona_id 'charlie'" in caplog.text
        assert "World" in caplog.text

    def test_multiple_unknown_persona_ids(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that warnings are logged for multiple unknown persona_ids."""
        phrases = [
            Phrase(text="One", persona_id="charlie"),
            Phrase(text="Two", persona_id="david"),
            Phrase(text="Three", persona_id="charlie"),  # Duplicate
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        # Should report each unique unknown ID once
        assert unknown_ids == ["charlie", "david"]
        assert len(caplog.records) == 2
        assert "charlie" in caplog.text
        assert "david" in caplog.text

    def test_empty_persona_id_no_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that empty persona_id doesn't trigger warning."""
        phrases = [
            Phrase(text="Hello", persona_id=""),
            Phrase(text="World", persona_id="alice"),
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        assert unknown_ids == []
        assert len(caplog.records) == 0

    def test_none_persona_id_no_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that None persona_id doesn't trigger warning."""
        phrases = [
            Phrase(text="Hello"),  # persona_id defaults to ""
            Phrase(text="World", persona_id="alice"),
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        assert unknown_ids == []
        assert len(caplog.records) == 0

    def test_no_phrases(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test validation with empty phrase list."""
        phrases: list[Phrase] = []
        synthesizers: dict[str, Any] = {"alice": "synthesizer1"}

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        assert unknown_ids == []
        assert len(caplog.records) == 0

    def test_no_synthesizers(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that all persona_ids are unknown when no synthesizers exist."""
        phrases = [
            Phrase(text="Hello", persona_id="alice"),
            Phrase(text="World", persona_id="bob"),
        ]
        synthesizers: dict[str, Any] = {}

        with caplog.at_level(logging.WARNING):
            unknown_ids = validate_persona_ids(phrases, synthesizers)

        assert unknown_ids == ["alice", "bob"]
        assert len(caplog.records) == 2

    def test_strict_mode_raises_error_for_unknown_persona(self) -> None:
        """Test that ValueError is raised in strict mode for unknown persona_id."""
        phrases = [
            Phrase(text="Hello", persona_id="alice"),
            Phrase(text="World", persona_id="unknown"),
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        with pytest.raises(ValueError) as excinfo:
            validate_persona_ids(phrases, synthesizers, strict=True)

        error_msg = str(excinfo.value)
        assert "unknown" in error_msg
        assert "alice" in error_msg or "bob" in error_msg  # Available personas listed

    def test_strict_mode_includes_all_unknown_ids_in_error(self) -> None:
        """Test that error message includes all unknown persona_ids."""
        phrases = [
            Phrase(text="One", persona_id="charlie"),
            Phrase(text="Two", persona_id="david"),
        ]
        synthesizers: dict[str, Any] = {"alice": "synthesizer1"}

        with pytest.raises(ValueError) as excinfo:
            validate_persona_ids(phrases, synthesizers, strict=True)

        error_msg = str(excinfo.value)
        assert "charlie" in error_msg
        assert "david" in error_msg
        assert "alice" in error_msg  # Available persona listed

    def test_strict_mode_no_error_when_all_valid(self) -> None:
        """Test that no error is raised in strict mode when all persona_ids are valid."""
        phrases = [
            Phrase(text="Hello", persona_id="alice"),
            Phrase(text="World", persona_id="bob"),
        ]
        synthesizers: dict[str, Any] = {
            "alice": "synthesizer1",
            "bob": "synthesizer2",
        }

        # Should not raise any error
        unknown_ids = validate_persona_ids(phrases, synthesizers, strict=True)
        assert unknown_ids == []
