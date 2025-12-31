# Movie Generator

Generate YouTube slide videos from blog URLs automatically.

## Features

- **Content Extraction**: Fetch and parse blog content from URLs
- **MCP Integration**: Enhanced web scraping via MCP servers (Firecrawl, etc.)
- **AI Script Generation**: Generate video scripts using LLM (OpenRouter)
- **Logo Asset Management**: Automatically download product/company logos from official sources
- **Voice Synthesis**: Text-to-speech using VOICEVOX with pronunciation dictionary
- **Slide Generation**: Create presentation slides using AI image generation with logo integration
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

VOICEVOX Core is not available via PyPI and must be installed manually. If not installed, the generator will raise an error:

```
ImportError: VOICEVOX Core is not installed and is required for audio synthesis.
Please install voicevox_core or see docs/VOICEVOX_SETUP.md for instructions.
To run without VOICEVOX (placeholder mode for testing), set allow_placeholder=True.
```

#### Quick Setup (macOS)

```bash
# Run the automated setup script
bash scripts/install_voicevox_macos.sh

# Set environment variables
source ~/.local/share/voicevox/env.sh
```

#### Manual Setup

1. **Install VOICEVOX Core**: Download from [VOICEVOX releases](https://github.com/VOICEVOX/voicevox_core/releases)
2. **Link to virtual environment**:
   ```bash
   # If installed via pyenv
   ln -sf ~/.pyenv/versions/3.13.1/lib/python3.13/site-packages/voicevox_core .venv/lib/python3.13/site-packages/
   ln -sf ~/.pyenv/versions/3.13.1/lib/python3.13/site-packages/voicevox_core-*.dist-info .venv/lib/python3.13/site-packages/
   ```
3. **Configure paths**: See `docs/VOICEVOX_SETUP.md` for detailed instructions

#### Testing Without VOICEVOX

For development/testing only, use placeholder mode:

```bash
# CLI with placeholder mode
uv run movie-generator generate https://example.com --allow-placeholder

# Programmatic usage
from movie_generator.audio.voicevox import VoicevoxSynthesizer
synth = VoicevoxSynthesizer(allow_placeholder=True)
```

**Note:** Placeholder mode generates empty audio files for testing pipeline structure only.

## Usage

### Basic Usage

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Generate video from URL
uv run movie-generator generate https://example.com/blog-post

# Generate from existing script.yaml
uv run movie-generator generate path/to/script.yaml

# With custom config
uv run movie-generator generate https://example.com/blog-post -c config/my-config.yaml

# Specify output directory
uv run movie-generator generate https://example.com/blog-post -o ./my-videos

# Testing mode without VOICEVOX
uv run movie-generator generate https://example.com/blog-post --allow-placeholder
```

### MCP Integration (Optional)

Use MCP (Model Context Protocol) servers for enhanced web scraping capabilities:

```bash
# Generate video using Firecrawl MCP server for better content extraction
uv run movie-generator generate https://example.com/blog-post --mcp-config opencode.jsonc

# Works with different MCP config formats
uv run movie-generator generate https://example.com/blog-post --mcp-config ~/.cursor/mcp.json
uv run movie-generator generate https://example.com/blog-post --mcp-config ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### MCP Configuration File

Create an MCP configuration file (supports JSON or JSONC format):

**Example: `opencode.jsonc`**
```jsonc
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@firecrawl/mcp-server-firecrawl"],
      "env": {
        "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}"
      }
    }
  }
}
```

**Environment Variable Replacement:**
- Use `{env:VAR_NAME}` syntax to reference environment variables
- Variables are replaced at runtime
- Example: `{env:FIRECRAWL_API_KEY}` → actual API key value

**Example: `.cursor/mcp.json`**
```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@firecrawl/mcp-server-firecrawl"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-your-api-key-here"
      }
    }
  }
}
```

**Benefits of MCP Integration:**
- Better content extraction from complex websites
- Handles JavaScript-rendered content
- More robust parsing of modern web pages
- Falls back to standard fetcher if MCP fails

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

video:
  transition:
    type: "fade"              # Transition type: fade, slide, wipe, flip, clockWipe, none
    duration_frames: 15       # Transition duration in frames (at 30fps)
    timing: "linear"          # Timing function: linear or spring

pronunciation:
  custom:
    "TechTerm":
      reading: "テックターム"
      accent: 0  # Auto
      word_type: "PROPER_NOUN"
      priority: 10
```

### Slide Transitions

Configure smooth transitions between slides using the `video.transition` settings:

```yaml
video:
  transition:
    type: "fade"              # Transition type (see below)
    duration_frames: 15       # Duration in frames (at 30fps: 15 frames ≈ 0.5 seconds)
    timing: "linear"          # Timing function: linear or spring
```

**Available Transition Types:**
- `fade` - Fade in/out between slides (default)
- `slide` - Slide in from the side
- `wipe` - Wipe across the screen
- `flip` - 3D flip effect
- `clockWipe` - Circular wipe like clock hands
- `none` - No transition, instant cut

**Timing Functions:**
- `linear` - Constant speed throughout (use `duration_frames` to control length)
- `spring` - Natural spring animation (ignores `duration_frames`, uses physics)

**Examples:**

```yaml
# Fast slide transition
video:
  transition:
    type: "slide"
    duration_frames: 10
    timing: "linear"

# Smooth spring-based fade
video:
  transition:
    type: "fade"
    duration_frames: 15
    timing: "spring"

# No transition (instant cuts)
video:
  transition:
    type: "none"
    duration_frames: 0
    timing: "linear"
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
# Manual linting
uv run ruff check .
uv run ruff format .
uv run mypy src/

# Pre-commit hooks (recommended)
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files

# Pre-commit will automatically run on git commit
git commit -m "your message"
```

#### Pre-commit Hooks

This project uses pre-commit hooks to automatically check code quality before commits:

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with a newline
- **check-yaml/toml**: Validate YAML and TOML files
- **ruff**: Fast Python linter with auto-fix
- **ruff-format**: Python code formatter
- **mypy**: Static type checker (src directory only)

To skip hooks temporarily (not recommended):
```bash
git commit --no-verify -m "your message"
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
│       ├── video/              # Video rendering
│       └── mcp/                # MCP integration
│           ├── config.py       # MCP config loader
│           └── client.py       # MCP client
├── config/
│   ├── default.yaml            # Default configuration
│   ├── examples/               # Example configs
│   └── mcp-example.jsonc       # Example MCP config
├── tests/                      # Test files
└── pyproject.toml              # Project dependencies
```

## Current Status

**Implemented Features:**
- ✅ Content extraction from URLs
- ✅ MCP server integration for enhanced web scraping (Firecrawl, etc.)
- ✅ AI-powered script generation
- ✅ VOICEVOX voice synthesis with pronunciation dictionary
- ✅ Automatic furigana generation for technical terms
- ✅ AI slide generation (OpenRouter integration)
- ✅ Video rendering with Remotion
- ✅ Smooth slide transitions (fade, slide, wipe, flip, clockWipe)
- ✅ Generate from URL or existing script.yaml

**Known Limitations:**
- VOICEVOX Core requires manual installation (not available via PyPI)
- Script generation requires OpenRouter API key
- Slide generation may take time depending on API rate limits

See `openspec/` for detailed specifications and roadmap.

## License

MIT

## Contributing

See `AGENTS.md` for development guidelines and coding standards.
