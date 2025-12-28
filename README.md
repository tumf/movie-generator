# Movie Generator

Generate YouTube slide videos from blog URLs automatically.

## Features

- **Content Extraction**: Fetch and parse blog content from URLs
- **AI Script Generation**: Generate video scripts using LLM (OpenRouter)
- **Voice Synthesis**: Text-to-speech using VOICEVOX with pronunciation dictionary
- **Slide Generation**: Create presentation slides using AI image generation
- **Video Rendering**: Compose final video with Remotion

## Installation

### Requirements

- Python 3.13+
- uv package manager
- VOICEVOX Core (for voice synthesis)
- Node.js and Remotion (for video rendering)

### Setup

```bash
# Install dependencies with uv
uv sync

# Optional: Install dev dependencies
uv sync --extra dev
```

### VOICEVOX Setup (Required)

**⚠️ VOICEVOX Core is required for voice synthesis.**

The project will raise an `ImportError` if VOICEVOX Core is not installed:

```
ImportError: VOICEVOX Core is not installed and is required for audio synthesis.
See docs/VOICEVOX_SETUP.md for installation instructions.
```

Manual installation required (not available via pip):

1. Download VOICEVOX Core from the official repository
2. Set environment variables for dylib paths (macOS)
3. Update configuration with dictionary and model paths

**See `docs/VOICEVOX_SETUP.md` for detailed setup instructions.**

#### Testing Without VOICEVOX

For development/testing only, you can run in placeholder mode:

```python
from movie_generator.audio.voicevox import VoicevoxSynthesizer

# Enable placeholder mode (no actual audio generated)
synth = VoicevoxSynthesizer(allow_placeholder=True)
```

**Note:** Placeholder mode generates empty audio files and is only for testing pipeline structure.

## Usage

### Basic Usage

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Generate video from URL
uv run movie-generator generate https://example.com/blog-post

# With custom config
uv run movie-generator generate https://example.com/blog-post -c config/my-config.yaml

# Specify output directory
uv run movie-generator generate https://example.com/blog-post -o ./my-videos
```

### Configuration

#### Initialize Configuration File

Generate a default configuration file with helpful comments:

```bash
# Output to stdout
uv run movie-generator config init

# Save to a file
uv run movie-generator config init --output config.yaml

# Force overwrite existing file
uv run movie-generator config init -o config.yaml --force
```

#### Configuration Options

Create a YAML configuration file (see `config/default.yaml` for reference):

```yaml
project:
  name: "My YouTube Channel"
  output_dir: "./output"

style:
  resolution: [1920, 1080]
  fps: 30
  font_family: "Noto Sans JP"

audio:
  engine: "voicevox"
  speaker_id: 3  # Zundamon
  speed_scale: 1.0

narration:
  character: "ずんだもん"
  style: "casual"

content:
  llm_provider: "openrouter"
  model: "anthropic/claude-3.5-sonnet"

slides:
  provider: "openrouter"
  model: "nonobananapro"

pronunciation:
  custom:
    "TechTerm":
      reading: "テックターム"
      accent: 0  # Auto
      word_type: "PROPER_NOUN"
      priority: 10
```

### Pronunciation Dictionary

Add custom pronunciations for proper nouns and technical terms:

```yaml
pronunciation:
  custom:
    "React":
      reading: "リアクト"
      accent: 3
      word_type: "PROPER_NOUN"
      priority: 10
```

## Architecture

```
URL Input
    ↓
Content Fetch & Parse (httpx, BeautifulSoup)
    ↓
Script Generation (LLM via OpenRouter)
    ↓
Phrase Splitting (3-6 second units)
    ↓
Audio Generation (VOICEVOX with UserDict)
    ↓
Slide Generation (OpenRouter + Image AI)
    ↓
Video Composition (Remotion)
    ↓
Output: MP4 file + metadata
```

## Development

### Run Tests

```bash
uv run pytest
uv run pytest -v  # Verbose
uv run pytest tests/test_config.py  # Specific file
```

### Linting and Formatting

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

### Project Structure

```
movie-generator/
├── src/
│   └── movie_generator/
│       ├── cli.py              # CLI interface
│       ├── config.py           # Configuration management
│       ├── content/            # Content fetching & parsing
│       ├── script/             # Script generation & phrases
│       ├── audio/              # VOICEVOX integration
│       ├── slides/             # Slide generation
│       └── video/              # Video rendering
├── config/
│   ├── default.yaml            # Default configuration
│   └── examples/               # Example configs
├── tests/                      # Test files
└── pyproject.toml              # Project dependencies
```

## Current Limitations

This is Phase 1 implementation with the following limitations:

- VOICEVOX Core integration is placeholder (requires manual installation)
- Slide generation is placeholder (API integration pending)
- Video rendering is placeholder (Remotion integration pending)

See `openspec/changes/add-video-generator/` for implementation roadmap.

## License

MIT

## Contributing

See `AGENTS.md` for development guidelines and coding standards.
