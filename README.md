# Movie Generator

Generate YouTube slide videos from blog URLs automatically.

## Features

- **Content Extraction**: Fetch and parse blog content from URLs
- **MCP Integration**: Enhanced web scraping via MCP servers (Firecrawl, etc.)
- **AI Script Generation**: Generate video scripts using LLM (OpenRouter)
- **Logo Asset Management**: Automatically download product/company logos from official sources
- **Voice Synthesis**: Text-to-speech using VOICEVOX with pronunciation dictionary
- **Character Animation**: Static character display with configurable positioning (Phase 1)
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

### Narration Reading Field

When generating scripts, the LLM automatically creates a `reading` field for each narration line. This field contains the correct pronunciation in katakana, which is used for audio synthesis:

```yaml
sections:
  - title: "Introduction"
    narrations:
      - text: "明日は晴れです"
        reading: "アシタワハレデス"  # Automatically generated by LLM
```

The `reading` field ensures:
- Correct pronunciation of kanji (e.g., "道案内図" → "ミチアンナイズ")
- Proper particle pronunciation (は → ワ, へ → エ, を → オ)
- Accurate reading of numbers (e.g., "97" → "キュウジュウナナ")

The LLM handles this automatically during script generation, so manual editing is rarely needed.

### Character Animation

Display animated character images alongside your slides to enhance visual engagement. Features include static positioning, lip sync during speech, automatic blinking, and animation styles (sway/bounce). Characters can be configured per persona in multi-speaker mode.

#### Setup

1. **Generate character assets from PSD:**

If you have the official character PSD files:

**For Zundamon:**
```bash
# Place PSD file in assets/
# assets/ずんだもん立ち絵素材2.3.psd

# Generate character assets automatically
uv run python scripts/generate_zundamon_assets.py

# Output: assets/characters/zundamon/
#   - base.png
#   - mouth_open.png
#   - eye_close.png
```

**For Shikoku Metan:**
```bash
# Place PSD file in assets/
# assets/四国めたん立ち絵素材2.1.psd

# Generate character assets automatically
uv run python scripts/generate_metan_assets.py

# Output: assets/characters/shikoku-metan/
#   - base.png
#   - mouth_open.png
#   - eye_close.png
```

**For Kasukabe Tsumugi:**
```bash
# Place PSD file in assets/
# assets/春日部つむぎ立ち絵素材.psd

# Generate character assets automatically
uv run python scripts/generate_tsumugi_assets.py

# Output: assets/characters/kasukabe-tsumugi/
#   - base.png
#   - mouth_open.png
#   - eye_close.png
```

Or **manually create character images** following the [Character Asset Guide](docs/CHARACTER_ASSET_GUIDE.md):

```bash
mkdir -p assets/characters/your-character
# Place your character images:
# - base.png (required) - Character with mouth closed, eyes open
# - mouth_open.png (optional) - For lip sync animation
# - eye_close.png (optional) - For blinking animation
```

2. **Configure personas with character images:**

```yaml
personas:
  - id: "zundamon"
    name: "ずんだもん"
    character: "元気で明るい東北の妖精"
    synthesizer:
      speaker_id: 3
      speed_scale: 1.0
    subtitle_color: "#8FCF4F"
    # Character animation settings
    character_image: "assets/characters/zundamon/base.png"
    character_position: "left"  # left, right, or center
    # Lip sync and blinking (optional)
    mouth_open_image: "assets/characters/zundamon/mouth_open.png"
    eye_close_image: "assets/characters/zundamon/eye_close.png"
    animation_style: "sway"      # bounce, sway, or static (Phase 3)
```

#### Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `character_image` | `str \| None` | `None` | Path to base character image (PNG with transparency recommended) |
| `character_position` | `"left" \| "right" \| "center"` | `"left"` | Screen position for character |
| `mouth_open_image` | `str \| None` | `None` | Path to mouth-open image for lip sync (toggles every 0.1s during speech) |
| `eye_close_image` | `str \| None` | `None` | Path to eye-closed image for blinking (blinks every 3 seconds for 0.2s) |
| `animation_style` | `"bounce" \| "sway" \| "static"` | `"sway"` | Animation motion: `sway` (gentle horizontal), `bounce` (vertical), or `static` (none) |

#### Image Specifications

- **Format**: PNG with transparent background (recommended)
- **Size**: 512x512px or similar square aspect ratio
- **Content**: Full-body or bust-up character illustration
- **Transparency**: Required for proper layering over slides

**For Lip Sync and Blinking:**
- All images (base, mouth_open, eye_close) should have the same dimensions and character position
- Only the mouth or eyes should differ between images
- Example preparation:
  - `base.png` - Mouth closed, eyes open
  - `mouth_open.png` - Mouth open, eyes open (for speech)
  - `eye_close.png` - Mouth closed, eyes closed (for blinking)

#### Multi-Speaker Positioning

For 2-speaker dialogue, position characters on opposite sides:

```yaml
personas:
  - id: "zundamon"
    name: "ずんだもん"
    character_image: "assets/characters/zundamon/base.png"
    character_position: "left"
    mouth_open_image: "assets/characters/zundamon/mouth_open.png"
    eye_close_image: "assets/characters/zundamon/eye_close.png"
    subtitle_color: "#8FCF4F"  # Green

  - id: "metan"
    name: "四国めたん"
    character_image: "assets/characters/shikoku-metan/base.png"
    character_position: "right"
    mouth_open_image: "assets/characters/shikoku-metan/mouth_open.png"
    eye_close_image: "assets/characters/shikoku-metan/eye_close.png"
    subtitle_color: "#F09CB2"  # Pink
```

See `config-zundamon.yaml` and `config-metan.yaml` for complete examples.

#### Animation Styles

Choose from three animation styles to add motion to your characters:

- **`sway` (default)**: Gentle side-to-side swaying motion (2-second cycle, ±5px)
- **`bounce`**: Vertical bouncing motion (1.5-second cycle, 0-10px)
- **`static`**: No animation (character stays still)

Example configuration:

```yaml
personas:
  - id: "energetic"
    animation_style: "bounce"  # For energetic characters
  - id: "calm"
    animation_style: "sway"    # For calm, gentle characters
  - id: "serious"
    animation_style: "static"  # For serious, professional tone
```

#### Phase Roadmap

- **Phase 1 (✅ Complete)**: Static character display with positioning
- **Phase 2 (✅ Complete)**: Lip sync (0.1s toggle during speech) and blinking (every 3s)
- **Phase 3 (✅ Complete)**: Sway/bounce animations

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
