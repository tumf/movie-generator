# AGENTS.md - AI Coding Agent Instructions

Instructions for AI coding assistants working in this repository.

## Critical Rules

**NEVER use low-quality fallbacks.** When a primary approach fails:

- Do NOT silently degrade to a worse alternative
- Do NOT use placeholder values or dummy data
- Do NOT skip steps that are essential for quality
- Do NOT substitute with inferior implementations

Instead: Report the failure clearly and ask for guidance, or find a proper solution.

### LLM Model Configuration

**NEVER hardcode LLM models in system defaults or example configurations.**

All AI models you know about are outdated. Always use the models specified below for testing and documentation:

- **Script generation**: `"openai/gpt-5.2"`
- **Image generation**: `"google/gemini-3-pro-image-preview"`

**Configuration structure:**
```yaml
content:
  llm:
    provider: "openrouter"
    model: "openai/gpt-5.2"

slides:
  llm:
    provider: "openrouter"
    model: "google/gemini-3-pro-image-preview"
  style: "presentation"
```

**CRITICAL**: The `image_model` field does NOT exist. Never add it to configurations. The `slides.llm.model` handles both text and image generation.

## Project Overview

Movie Generator is a Python CLI tool that generates YouTube slide videos from blog URLs.
It fetches content, generates narration scripts with LLM, synthesizes audio with VOICEVOX,
creates slides, and renders videos using Remotion.

## Quick Reference

### Build/Test/Lint Commands

```bash
# Install with uv (recommended)
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run single test file
uv run pytest tests/test_scene_range.py -v

# Run single test function
uv run pytest tests/test_scene_range.py::TestSceneRangeParsing::test_single_scene -v

# Run tests matching keyword
uv run pytest -k "scene" -v

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy src/
```

### CLI Commands

```bash
# All-in-one generation (backward compatible)
uv run movie-generator generate <URL|script.yaml> [--scenes 1-3]

# Step-by-step workflow
uv run movie-generator script create <URL> [--output DIR]
uv run movie-generator audio generate <script.yaml> [--scenes 1-3]
uv run movie-generator slides generate <script.yaml> [--scenes 1-3]
uv run movie-generator video render <script.yaml> [--scenes 1-3] [--output FILE]

# Common options (available on all commands)
--force / -f          # Force overwrite existing files
--quiet / -q          # Suppress progress output
--verbose / -v        # Show detailed debug info
--dry-run             # Preview without executing

# Configuration
uv run movie-generator config init [--output config.yaml]
```

### Environment Variables

```bash
export OPENROUTER_API_KEY="..."           # Required for LLM/slides
export VOICEVOX_DICT_DIR="..."            # VOICEVOX dictionary path
export VOICEVOX_MODEL_PATH="..."          # VOICEVOX model path
export VOICEVOX_ONNXRUNTIME_PATH="..."    # VOICEVOX ONNX runtime path
```

## Code Style Guidelines

### Python Version & Tools

- **Python**: 3.13+
- **Linter/Formatter**: Ruff (line-length: 100)
- **Type Checker**: mypy (strict mode)
- **Testing**: pytest

### Pydantic Model Serialization

**ALWAYS use `model_dump()` to serialize Pydantic models.** Never manually construct dictionaries.

**Bad** (manual, error-prone):
```python
# Easy to forget fields - causes silent data loss!
narr_dict = {"text": n.text, "reading": n.reading}
if n.persona_id:
    narr_dict["persona_id"] = n.persona_id
```

**Good** (automatic, safe):
```python
# All fields included automatically
narr_dict = n.model_dump(exclude_none=True)
```

**Why this matters:**
- **Past incident**: Manual serialization forgot `reading` field, causing all pronunciation data to be lost
- **Root cause**: Hand-coded dictionary construction doesn't track model changes
- **Solution**: Use Pydantic's built-in serialization - it's type-safe and automatic

**Key principle**: Don't reinvent what the framework provides. Use `model_dump()` for serialization.

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `voicevox.py`, `remotion_renderer.py` |
| Classes | PascalCase | `VoicevoxSynthesizer`, `VideoScript` |
| Functions | snake_case | `parse_scene_range`, `create_composition` |
| Constants | SCREAMING_SNAKE_CASE | `VOICEVOX_AVAILABLE` |
| Variables | snake_case | `audio_paths`, `section_index` |

### Import Organization

```python
"""Module docstring."""

# 1. Standard library
import asyncio
from pathlib import Path

# 2. Third-party packages
import click
import yaml
from pydantic import BaseModel
from rich.console import Console

# 3. Local/project imports
from .audio.voicevox import create_synthesizer_from_config
from .config import Config, load_config
```

### Type Annotations

Always use type annotations for function signatures:

```python
def parse_scene_range(scenes_arg: str) -> tuple[int | None, int | None]:
    """Parse scene range argument."""
    ...

def create_composition(
    title: str,
    phrases: list[Phrase],
    slide_paths: list[Path],
    fps: int = 30,
) -> CompositionData:
    ...
```

### Data Classes

Use `@dataclass` for simple data containers:

```python
@dataclass
class Phrase:
    """A single phrase with timing information."""
    text: str
    duration: float = 0.0
    section_index: int = 0
    original_index: int = 0  # Global index for file naming
```

### Error Handling

- Raise `ValueError` for invalid inputs with descriptive messages
- Use `RuntimeError` for system/external failures
- Include context in error messages

```python
if start > end:
    raise ValueError(
        f"Invalid scene range: start ({start}) > end ({end})"
    )
```

### Documentation

- Module docstring at top of each file
- Google-style docstrings for public functions
- Type hints serve as primary documentation

```python
def split_into_phrases(text: str, max_chars: int = 50) -> list[Phrase]:
    """Split text into phrases based on punctuation and length.

    Args:
        text: Input text to split.
        max_chars: Maximum characters per phrase.

    Returns:
        List of Phrase objects.
    """
```

## Project Structure

```
src/movie_generator/
├── cli.py              # Main CLI entry point
├── config.py           # Pydantic configuration models
├── project.py          # Project management
├── assets/             # Logo and asset download/conversion
├── audio/              # Audio synthesis (VOICEVOX)
├── content/            # URL fetching and HTML parsing
├── script/             # Script generation and phrase splitting
├── slides/             # Slide image generation
└── video/              # Video rendering (Remotion)
```

### Key Concepts

- **Phrase**: Text segment with `section_index` (which section) and `original_index` (global ID)
- **Section**: A script section with title, narration, and slide prompt
- **Composition**: JSON data linking phrases, audio files, and slides for Remotion
- **Logo Asset**: Product/company logo downloaded from LLM-identified URLs, stored in `assets/logos/`

## Testing

### Test Structure

```python
class TestSceneRangeParsing:
    """Test scene range parsing function."""

    def test_single_scene(self) -> None:
        """Test parsing single scene number."""
        start, end = parse_scene_range("2")
        assert start == 1  # 0-based
        assert end == 1
```

### Test Naming

- Files: `test_<module>.py`
- Classes: `Test<Feature>`
- Functions: `test_<behavior>` or `test_<input>_<expected>`

## Git Workflow

### Commit Messages (Conventional Commits)

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
- `feat(cli): add --scenes option for scene range filtering`
- `fix(video): always regenerate composition for scene range accuracy`

<!-- OPENSPEC:START -->
# OpenSpec Instructions

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts

## OpenSpec Archive Rules

**CRITICAL**: When archiving OpenSpec changes:

1. **Always use the CLI command**: `openspec archive <id> --yes`
2. **Never create directories manually** - The CLI handles all file operations
3. **Correct archive path**: `openspec/changes/archive/YYYY-MM-DD-<id>/`
4. **Wrong path (DO NOT USE)**: `openspec-archive/` - This is incorrect!

The `openspec archive` command automatically:
- Moves change files to the correct archive location
- Updates spec files with new requirements
- Validates the archive structure

<!-- OPENSPEC:END -->

## Important Reminders

1. **Read before editing** - Always read existing files before modification
2. **Use `original_index`** - For file naming across filtered phrase lists
3. **Use `section_index`** - For mapping phrases to slides
4. **Regenerate composition** - Always regenerate `composition.json` for scene ranges
5. **Test with scene ranges** - Verify `--scenes N`, `--scenes N-M`, `--scenes N-`

## LLM Prompt Management

### Critical Rule: Complete Prompt Coverage

When adding features that require LLM output changes, **ALL prompt variants MUST be updated**.

**Background**: The script generator has 4 prompt templates:
- `SCRIPT_GENERATION_PROMPT_JA` (single-speaker, Japanese)
- `SCRIPT_GENERATION_PROMPT_EN` (single-speaker, English)
- `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` (multi-speaker, Japanese)
- `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` (multi-speaker, English)

### Why This Matters

**Past Incident**: When adding the `reading` field feature:
- ✅ Updated single-speaker prompts (JA/EN) with detailed instructions
- ❌ Updated dialogue prompts (JA/EN) with only example format, no detailed instructions
- **Result**: Generated scripts in dialogue mode were missing `reading` fields

**Root Cause Analysis**:
1. **Incomplete requirements sweep**: Focused on "adding the field" rather than "ensuring LLM generates it correctly"
2. **Lack of systematic verification**: Did not check if all prompts had equivalent instructions
3. **Insufficient testing**: Tests used mocked data, not actual LLM calls
4. **No prompt quality checklist**: No verification that instructions were detailed enough

### Prevention Strategy

When modifying LLM prompts or adding fields to LLM-generated output:

#### 1. Identify All Prompt Variants
```bash
# Find all prompt constants
grep -n "PROMPT.*=" src/movie_generator/script/generator.py
```

#### 2. Update Checklist
For each prompt variant, verify:
- [ ] Field is included in output format example
- [ ] Detailed instructions explain how to generate the field
- [ ] Edge cases and special rules are documented (e.g., particle pronunciation)
- [ ] Examples demonstrate correct output format
- [ ] Required vs optional is explicitly stated

#### 3. Verification Requirements
- [ ] Read all prompt templates end-to-end
- [ ] Compare instruction completeness across variants
- [ ] Ensure language-specific nuances are covered (e.g., katakana vs romaji)
- [ ] Test with actual LLM calls, not just mocked data

#### 4. Testing Strategy
```python
# Bad: Mock test (doesn't catch prompt issues)
def test_reading_field():
    data = {"text": "test", "reading": "テスト"}
    assert Narration.model_validate(data)

# Good: Integration test with LLM
@pytest.mark.integration
async def test_dialogue_prompt_generates_reading():
    script = await generate_script(
        content="sample",
        personas=[...],
        language="ja"
    )
    for section in script.sections:
        for narration in section.narrations:
            assert narration.reading, "LLM must generate reading field"
            assert narration.reading != narration.text, "Reading should be katakana"
```

#### 5. Documentation Requirements
When adding LLM-dependent features, document in code:
```python
# PROMPT COVERAGE CHECKLIST:
# - SCRIPT_GENERATION_PROMPT_JA: ✓ Updated with reading field instructions
# - SCRIPT_GENERATION_PROMPT_EN: ✓ Updated with reading field instructions
# - SCRIPT_GENERATION_PROMPT_DIALOGUE_JA: ✓ Updated with reading field instructions
# - SCRIPT_GENERATION_PROMPT_DIALOGUE_EN: ✓ Updated with reading field instructions
```

### Quick Verification Script

Before committing prompt changes:
```bash
# Verify all prompts mention new fields
NEW_FIELD="reading"
for prompt in JA EN DIALOGUE_JA DIALOGUE_EN; do
  echo "Checking SCRIPT_GENERATION_PROMPT_$prompt..."
  grep -A50 "SCRIPT_GENERATION_PROMPT_$prompt" src/movie_generator/script/generator.py | \
    grep -q "$NEW_FIELD" && echo "✓ Found" || echo "✗ MISSING"
done
```

### Reading Field Quality Checklist

When modifying `reading` field generation rules (katakana pronunciation):

1. **Verify ALL 4 prompts contain identical rules**:
   - Particle pronunciation (は→ワ, へ→エ, を→オ)
   - Alphabet acronym long vowels (ESP→イーエスピー, NOT イーエスピージ)
   - Sokuon notation (って→ッテ, った→ッタ)
   - No spaces in katakana
   - Sufficient examples covering edge cases

2. **Test with actual LLM calls**:
   ```bash
   # Run reading quality test
   uv run python test_reading_quality.py
   ```

3. **Check common mistakes**:
   - ESP/API/CPU missing final long vowel mark (ー)
   - Incorrect sokuon (small ッ) in particles like って
   - Spaces in katakana (should be removed)
   - Hiragana instead of katakana

### Summary

**Golden Rule**: If you add a field to the LLM output schema, you must add explicit generation instructions to ALL prompt variants. Half-updated prompts lead to silent failures in production.

## Subtitle Color Management

### Single Source of Truth

Subtitle colors are defined in `constants.py` and must be used consistently across all modules:

```python
# constants.py - THE definitive source
class SubtitleConstants:
    DEFAULT_COLOR = "#FFFFFF"  # White
```

**Modules that use this constant:**
| Module | Usage |
|--------|-------|
| `config.py` | Default for `PersonaConfig.subtitle_color` |
| `remotion_renderer.py` | Fallback in `_get_persona_fields()` |
| `templates.py` | Embedded in generated VideoGenerator.tsx |

### Why This Matters

**Past Incidents**: Multiple regressions occurred due to:
1. Hardcoded `#8FCF4F` (green/Zundamon's color) as default in templates.py
2. Inconsistent defaults between Python and TypeScript
3. JSON serialization losing `subtitleColor` field (snake_case vs camelCase)
4. Manual sed updates breaking all colors

### Prevention Measures

1. **Use constants, never hardcode colors**
   ```python
   # Good
   from ..constants import SubtitleConstants
   color = SubtitleConstants.DEFAULT_COLOR

   # Bad - DO NOT DO THIS
   color = "#FFFFFF"  # Hardcoded
   color = "#8FCF4F"  # Persona-specific as default
   ```

2. **Test coverage in `tests/test_subtitle_color.py`**
   - Verifies constant definition
   - Tests config defaults
   - Tests composition.json propagation
   - Tests VideoGenerator.tsx template generation
   - Integration tests for multi-speaker colors

3. **JSON serialization with aliases**
   ```python
   # CompositionPhrase uses serialization_alias for camelCase JSON
   subtitle_color: str | None = Field(default=None, serialization_alias="subtitleColor")

   # Must use by_alias=True when dumping
   phrase.model_dump(exclude_none=True, by_alias=True)
   ```

### Quick Verification

Before modifying subtitle-related code:
```bash
# Run subtitle color tests
uv run pytest tests/test_subtitle_color.py -v

# Verify no hardcoded colors in templates
grep -n "#8FCF4F" src/movie_generator/video/templates.py
# Should return nothing

# Verify constant is used
grep -r "SubtitleConstants.DEFAULT_COLOR" src/
```
