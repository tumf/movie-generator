"""Tests for script validation functionality."""

from pathlib import Path
from textwrap import dedent

from movie_generator.script.generator import validate_script


class TestScriptValidation:
    """Test script validation function."""

    def test_valid_script(self, tmp_path: Path) -> None:
        """Test validation of a valid script file."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Introduction"
                    narrations:
                      - text: "こんにちは"
                        reading: "コンニチワ"
                  - title: "Main Content"
                    narrations:
                      - text: "これはテストです"
                        reading: "コレワ テストデス"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.section_count == 2
        assert result.narration_count == 2

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test validation of non-existent file."""
        script_file = tmp_path / "nonexistent.yaml"

        result = validate_script(script_file)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "File not found" in result.errors[0]

    def test_invalid_yaml_syntax(self, tmp_path: Path) -> None:
        """Test validation of file with invalid YAML syntax."""
        script_file = tmp_path / "invalid.yaml"
        script_file.write_text(
            dedent("""
                title: "Test
                # Missing closing quote
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "YAML parse error" in result.errors[0]

    def test_missing_title(self, tmp_path: Path) -> None:
        """Test validation detects missing title field."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narrations:
                      - text: "Test"
                        reading: "テスト"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("Missing required field: title" in error for error in result.errors)

    def test_missing_description(self, tmp_path: Path) -> None:
        """Test validation detects missing description field."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                sections:
                  - title: "Section 1"
                    narrations:
                      - text: "Test"
                        reading: "テスト"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("Missing required field: description" in error for error in result.errors)

    def test_missing_sections(self, tmp_path: Path) -> None:
        """Test validation detects missing sections field."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("Missing required field: sections" in error for error in result.errors)

    def test_empty_sections_warning(self, tmp_path: Path) -> None:
        """Test validation warns about empty sections."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections: []
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        # Empty sections is a warning, not an error
        assert result.is_valid
        assert any("Script has no sections" in warning for warning in result.warnings)

    def test_section_missing_title(self, tmp_path: Path) -> None:
        """Test validation detects section without title."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - narrations:
                      - text: "Test"
                        reading: "テスト"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("missing 'title' field" in error for error in result.errors)

    def test_section_missing_narrations(self, tmp_path: Path) -> None:
        """Test validation detects section without narrations."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("missing narrations" in error for error in result.errors)

    def test_invalid_narration_format(self, tmp_path: Path) -> None:
        """Test validation detects invalid narration format."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narrations:
                      - invalid_field: "test"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("missing 'text' field" in error for error in result.errors)

    def test_unknown_persona_id_warning(self, tmp_path: Path) -> None:
        """Test validation warns about unknown persona_id."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narrations:
                      - text: "こんにちは"
                        reading: "コンニチワ"
                        persona_id: "unknown_id"
            """),
            encoding="utf-8",
        )

        config_personas = [
            {"id": "zundamon", "name": "ずんだもん"},
            {"id": "metan", "name": "四国めたん"},
        ]

        result = validate_script(script_file, config_personas)

        # Unknown persona_id is a warning, not an error
        assert result.is_valid
        assert any("Unknown persona_id: unknown_id" in warning for warning in result.warnings)

    def test_known_persona_id_valid(self, tmp_path: Path) -> None:
        """Test validation passes for known persona_id."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narrations:
                      - text: "こんにちは"
                        reading: "コンニチワ"
                        persona_id: "zundamon"
            """),
            encoding="utf-8",
        )

        config_personas = [
            {"id": "zundamon", "name": "ずんだもん"},
            {"id": "metan", "name": "四国めたん"},
        ]

        result = validate_script(script_file, config_personas)

        assert result.is_valid
        assert len(result.warnings) == 0

    def test_persona_validation_skipped_without_config(self, tmp_path: Path) -> None:
        """Test persona_id validation is skipped when config not provided."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narrations:
                      - text: "こんにちは"
                        reading: "コンニチワ"
                        persona_id: "any_id"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file, config_personas=None)

        # Should pass without warnings since no config provided
        assert result.is_valid
        assert len(result.warnings) == 0

    def test_legacy_dialogue_format(self, tmp_path: Path) -> None:
        """Test validation of legacy dialogue format."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    dialogues:
                      - narration: "こんにちは"
                        reading: "コンニチワ"
                        persona_id: "zundamon"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert result.is_valid
        assert result.narration_count == 1

    def test_legacy_single_narration_format(self, tmp_path: Path) -> None:
        """Test validation of legacy single narration format."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narration: "こんにちは"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert result.is_valid
        assert result.narration_count == 1

    def test_string_narration_format(self, tmp_path: Path) -> None:
        """Test validation of string narration format (legacy)."""
        script_file = tmp_path / "script.yaml"
        script_file.write_text(
            dedent("""
                title: "Test Video"
                description: "Test description"
                sections:
                  - title: "Section 1"
                    narrations:
                      - "こんにちは"
                      - "これはテストです"
            """),
            encoding="utf-8",
        )

        result = validate_script(script_file)

        assert result.is_valid
        assert result.narration_count == 2

    def test_empty_script_file(self, tmp_path: Path) -> None:
        """Test validation of empty script file."""
        script_file = tmp_path / "empty.yaml"
        script_file.write_text("", encoding="utf-8")

        result = validate_script(script_file)

        assert not result.is_valid
        assert any("empty" in error.lower() for error in result.errors)
