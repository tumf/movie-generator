"""Tests for script generation prompt templates.

Verifies that all 4 prompt variants (single/dialogue x ja/en) include
required field descriptions and examples.
"""

import pytest

from movie_generator.script.generator import (
    SCRIPT_GENERATION_PROMPT_DIALOGUE_EN,
    SCRIPT_GENERATION_PROMPT_DIALOGUE_JA,
    SCRIPT_GENERATION_PROMPT_EN,
    SCRIPT_GENERATION_PROMPT_JA,
    get_output_format_json_example,
    get_reading_field_instructions,
    get_slide_image_instructions,
)


class TestPromptTemplateCompleteness:
    """Test that all prompt templates include required instructions."""

    @pytest.mark.parametrize(
        "prompt_template,language,is_dialogue",
        [
            (SCRIPT_GENERATION_PROMPT_JA, "ja", False),
            (SCRIPT_GENERATION_PROMPT_EN, "en", False),
            (SCRIPT_GENERATION_PROMPT_DIALOGUE_JA, "ja", True),
            (SCRIPT_GENERATION_PROMPT_DIALOGUE_EN, "en", True),
        ],
    )
    def test_prompt_has_output_format_placeholder(
        self, prompt_template: str, language: str, is_dialogue: bool
    ):
        """Test that prompt template has {output_format} placeholder."""
        assert "{output_format}" in prompt_template, (
            f"{language}/{is_dialogue} prompt missing {{output_format}} placeholder"
        )

    @pytest.mark.parametrize(
        "prompt_template,language,is_dialogue",
        [
            (SCRIPT_GENERATION_PROMPT_JA, "ja", False),
            (SCRIPT_GENERATION_PROMPT_EN, "en", False),
            (SCRIPT_GENERATION_PROMPT_DIALOGUE_JA, "ja", True),
            (SCRIPT_GENERATION_PROMPT_DIALOGUE_EN, "en", True),
        ],
    )
    def test_prompt_has_reading_instructions_placeholder(
        self, prompt_template: str, language: str, is_dialogue: bool
    ):
        """Test that prompt template has {reading_instructions} placeholder."""
        assert "{reading_instructions}" in prompt_template, (
            f"{language}/{is_dialogue} prompt missing {{reading_instructions}} placeholder"
        )

    @pytest.mark.parametrize(
        "prompt_template,language,is_dialogue",
        [
            (SCRIPT_GENERATION_PROMPT_JA, "ja", False),
            (SCRIPT_GENERATION_PROMPT_EN, "en", False),
            (SCRIPT_GENERATION_PROMPT_DIALOGUE_JA, "ja", True),
            (SCRIPT_GENERATION_PROMPT_DIALOGUE_EN, "en", True),
        ],
    )
    def test_prompt_has_slide_instructions_placeholder(
        self, prompt_template: str, language: str, is_dialogue: bool
    ):
        """Test that prompt template has {slide_instructions} placeholder."""
        assert "{slide_instructions}" in prompt_template, (
            f"{language}/{is_dialogue} prompt missing {{slide_instructions}} placeholder"
        )


class TestOutputFormatExamples:
    """Test that output format examples include all required fields."""

    @pytest.mark.parametrize(
        "language,is_dialogue",
        [
            ("ja", False),
            ("en", False),
            ("ja", True),
            ("en", True),
        ],
    )
    def test_output_format_has_sections_field(self, language: str, is_dialogue: bool):
        """Test that output format example includes 'sections' field."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"sections"' in output_format, (
            f"{language}/{is_dialogue} output format missing 'sections' field"
        )

    @pytest.mark.parametrize(
        "language,is_dialogue",
        [
            ("ja", False),
            ("en", False),
            ("ja", True),
            ("en", True),
        ],
    )
    def test_output_format_has_narrations_field(self, language: str, is_dialogue: bool):
        """Test that output format example includes 'narrations' field."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"narrations"' in output_format, (
            f"{language}/{is_dialogue} output format missing 'narrations' field"
        )

    @pytest.mark.parametrize(
        "language,is_dialogue",
        [
            ("ja", False),
            ("en", False),
            ("ja", True),
            ("en", True),
        ],
    )
    def test_output_format_has_text_field(self, language: str, is_dialogue: bool):
        """Test that output format example includes 'text' field in narrations."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"text"' in output_format, (
            f"{language}/{is_dialogue} output format missing 'text' field"
        )

    @pytest.mark.parametrize(
        "language,is_dialogue",
        [
            ("ja", False),
            ("en", False),
            ("ja", True),
            ("en", True),
        ],
    )
    def test_output_format_has_reading_field(self, language: str, is_dialogue: bool):
        """Test that output format example includes 'reading' field in narrations."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"reading"' in output_format, (
            f"{language}/{is_dialogue} output format missing 'reading' field"
        )

    @pytest.mark.parametrize(
        "language,is_dialogue",
        [
            ("ja", False),
            ("en", False),
            ("ja", True),
            ("en", True),
        ],
    )
    def test_output_format_has_slide_prompt_field(self, language: str, is_dialogue: bool):
        """Test that output format example includes 'slide_prompt' field."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"slide_prompt"' in output_format, (
            f"{language}/{is_dialogue} output format missing 'slide_prompt' field"
        )

    @pytest.mark.parametrize("language,is_dialogue", [("ja", True), ("en", True)])
    def test_dialogue_output_format_has_role_assignments(self, language: str, is_dialogue: bool):
        """Test that dialogue output format includes 'role_assignments' field."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"role_assignments"' in output_format, (
            f"{language}/{is_dialogue} dialogue format missing 'role_assignments' field"
        )

    @pytest.mark.parametrize("language,is_dialogue", [("ja", True), ("en", True)])
    def test_dialogue_output_format_has_persona_id(self, language: str, is_dialogue: bool):
        """Test that dialogue output format includes 'persona_id' field."""
        output_format = get_output_format_json_example(language, is_dialogue)
        assert '"persona_id"' in output_format, (
            f"{language}/{is_dialogue} dialogue format missing 'persona_id' field"
        )


class TestReadingFieldInstructions:
    """Test that reading field instructions include required content."""

    def test_japanese_reading_instructions_has_katakana_rule(self):
        """Test that Japanese reading instructions mention katakana requirement."""
        instructions = get_reading_field_instructions("ja")
        assert "カタカナ" in instructions, "Japanese reading instructions missing katakana rule"

    def test_japanese_reading_instructions_has_particle_rules(self):
        """Test that Japanese reading instructions include particle pronunciation rules."""
        instructions = get_reading_field_instructions("ja")
        assert "は」→「ワ" in instructions, "Japanese reading instructions missing は→ワ rule"
        assert "へ」→「エ" in instructions, "Japanese reading instructions missing へ→エ rule"

    def test_japanese_reading_instructions_has_sokuon_examples(self):
        """Test that Japanese reading instructions include sokuon (促音) examples."""
        instructions = get_reading_field_instructions("ja")
        assert "促音" in instructions or "ッ" in instructions, (
            "Japanese reading instructions missing sokuon examples"
        )

    def test_japanese_reading_instructions_has_examples(self):
        """Test that Japanese reading instructions include practical examples."""
        instructions = get_reading_field_instructions("ja")
        # Check for example pattern: text: "..." → reading: "..."
        assert "→ reading:" in instructions or "→「" in instructions, (
            "Japanese reading instructions missing examples"
        )

    def test_english_reading_instructions_mentions_copy_text(self):
        """Test that English reading instructions mention copying text field."""
        instructions = get_reading_field_instructions("en")
        assert "copy" in instructions.lower() or "same" in instructions.lower(), (
            "English reading instructions should mention copying text to reading"
        )


class TestSlideImageInstructions:
    """Test that slide image instructions include required content."""

    @pytest.mark.parametrize("language", ["ja", "en"])
    def test_slide_instructions_mention_source_image_url(self, language: str):
        """Test that slide instructions mention source_image_url option."""
        instructions = get_slide_image_instructions(language)
        assert "source_image_url" in instructions, (
            f"{language} slide instructions missing source_image_url"
        )

    @pytest.mark.parametrize("language", ["ja", "en"])
    def test_slide_instructions_mention_slide_prompt(self, language: str):
        """Test that slide instructions mention slide_prompt option."""
        instructions = get_slide_image_instructions(language)
        assert "slide_prompt" in instructions, f"{language} slide instructions missing slide_prompt"

    @pytest.mark.parametrize("language", ["ja", "en"])
    def test_slide_instructions_mention_alt_title_description(self, language: str):
        """Test that slide instructions mention checking Alt/Title/Description."""
        instructions = get_slide_image_instructions(language)
        assert "Alt" in instructions, f"{language} slide instructions missing Alt mention"
        assert "Title" in instructions or "title" in instructions, (
            f"{language} slide instructions missing Title mention"
        )
        assert "Description" in instructions or "description" in instructions, (
            f"{language} slide instructions missing Description mention"
        )


class TestPromptConsistency:
    """Test that shared components are consistently used across all variants."""

    def test_all_variants_use_shared_placeholders(self):
        """Test that all 4 prompt variants use the shared placeholder format."""
        prompts = [
            ("ja_single", SCRIPT_GENERATION_PROMPT_JA),
            ("en_single", SCRIPT_GENERATION_PROMPT_EN),
            ("ja_dialogue", SCRIPT_GENERATION_PROMPT_DIALOGUE_JA),
            ("en_dialogue", SCRIPT_GENERATION_PROMPT_DIALOGUE_EN),
        ]

        required_placeholders = [
            "{output_format}",
            "{reading_instructions}",
            "{slide_instructions}",
        ]

        for name, prompt in prompts:
            for placeholder in required_placeholders:
                assert placeholder in prompt, (
                    f"{name} prompt missing required placeholder: {placeholder}"
                )
