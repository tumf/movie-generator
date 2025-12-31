# Multi-Language Content Generation Feature

## Overview

The movie-generator now supports generating video content in multiple languages simultaneously. You can configure the system to generate scripts and slides in Japanese, English, or both languages at once.

## Configuration

### Basic Setup

Add the `languages` field to your configuration file under the `content` section:

```yaml
content:
  llm:
    provider: "openrouter"
    model: "openai/gpt-5.2"
  languages: ["ja", "en"]  # Generate content in both Japanese and English
```

### Supported Languages

Currently supported language codes:
- `ja` - Japanese
- `en` - English

More languages can be added by extending the prompt templates in `src/movie_generator/script/generator.py`.

## Output Structure

When multiple languages are configured, the output directory structure will be:

```
output/
├── script_ja.yaml          # Japanese script
├── script_en.yaml          # English script
└── slides/
    ├── ja/                 # Japanese slides
    │   ├── slide_0000.png
    │   ├── slide_0001.png
    │   └── ...
    └── en/                 # English slides
        ├── slide_0000.png
        ├── slide_0001.png
        └── ...
```

### Legacy Compatibility

For backward compatibility, if only one language is configured or if `languages` is not specified:
- Defaults to `["ja"]` (Japanese)
- Script is saved as `script.yaml` (without language suffix)
- Slides are saved directly in `output/slides/` (without language subdirectory)

## Usage

### Using Python API

```python
import asyncio
from pathlib import Path
from movie_generator.config import load_config
from movie_generator.multilang import generate_multilang_content

async def main():
    # Load configuration
    config = load_config(Path("config.yaml"))

    # Generate content for all configured languages
    results = await generate_multilang_content(
        content="Your source content here...",
        title="Video Title",
        description="Video description",
        config=config,
        output_dir=Path("output"),
        api_key="your-api-key",
    )

    # Results is a dict mapping language codes to VideoScript objects
    for lang_code, script in results.items():
        print(f"Generated script for {lang_code}: {script.title}")

asyncio.run(main())
```

### Using Scripts

The `scripts/generate_slides.py` automatically detects language-specific script files:

```bash
# Generate slides for all configured languages
python scripts/generate_slides.py
```

The script will:
1. Look for `script_*.yaml` files (e.g., `script_ja.yaml`, `script_en.yaml`)
2. Generate slides for each language in separate subdirectories
3. Report results per language

## Implementation Details

### Script Generation

Scripts are generated using language-specific prompts:
- `SCRIPT_GENERATION_PROMPT_JA` - Japanese prompt with pronunciation support
- `SCRIPT_GENERATION_PROMPT_EN` - English prompt (no pronunciation needed)

The `generate_script()` function accepts a `language` parameter to select the appropriate prompt.

### Slide Generation

Slides are generated in language-specific subdirectories:
- `generate_slides_for_sections()` accepts a `language` parameter
- Output directory is `{base_dir}/{language}/`
- Slide filenames remain consistent: `slide_0000.png`, `slide_0001.png`, etc.

**Important**: Slide prompts are written in English (for image generation API), but text to be displayed on slides is specified in the target language:
- Japanese example: `"A slide with text 'データベース設計' in the center, modern design"`
- English example: `"A slide with text 'Database Design' in the center, modern design"`

This ensures that slide text appears in the appropriate language for each version.

### Pronunciation Dictionary

Pronunciation entries are language-specific:
- Japanese scripts include a `pronunciations` section for VOICEVOX
- English scripts return an empty pronunciations array

## Configuration Example

See `test-multilang.yaml` for a complete configuration example with multiple languages.

## Testing

Run tests to verify the multi-language configuration:

```bash
pytest tests/test_config.py -v
```

The test suite includes:
- Default language configuration test
- Multi-language configuration loading test
- Configuration merging with language settings
