# Design: Video Generator Architecture

## Context

A Python tool for batch generation of slide videos for YouTube from blog URLs.
Users want to generate multiple videos with the same style (fonts, colors, narrator character, etc.),
so we use YAML-based configuration files for unified control.

### Existing Experimental Results

The following have been established through experiments at `/Users/tumf/work/study/daihon/`:

1. **Phrase-based approach**: 3-6 second phrase segmentation is optimal for subtitle synchronization
2. **VOICEVOX integration**: Correct usage of `voicevox_core.blocking` API
3. **Proper noun dictionary**: Pronunciation control through reading dictionaries
4. **Remotion**: TypeScript/React-based video composition

## Goals / Non-Goals

### Goals
- Batch conversion from blog URL → video file
- Unified video style through YAML configuration
- Accurate subtitle synchronization based on phrases
- Accurate pronunciation of proper nouns
- Modern development environment with Python 3.13 + uv

### Non-Goals
- GUI/Web interface (CLI only)
- Real-time preview
- Video editing features (generation only)
- Multi-language support (Japanese only)

## Decisions

### 1. Project Structure

```
movie-generator/
├── pyproject.toml           # uv + Python 3.13
├── config/
│   ├── default.yaml         # Default configuration
│   └── examples/            # Project-specific config examples
├── src/
│   └── movie_generator/
│       ├── __init__.py
│       ├── cli.py           # CLI entry point
│       ├── config.py        # YAML config loading
│       ├── content/
│       │   ├── fetcher.py   # URL → content retrieval
│       │   └── parser.py    # Content parsing
│       ├── script/
│       │   ├── generator.py # LLM script generation
│       │   └── phrases.py   # Phrase segmentation
│       ├── audio/
│       │   ├── voicevox.py  # VOICEVOX integration
│       │   └── dictionary.py # Pronunciation dictionary
│       ├── slides/
│       │   └── generator.py # Slide image generation
│       └── video/
│           └── renderer.py  # Video rendering
└── tests/
```

### 2. Configuration File Format (YAML)

```yaml
# config.yaml
project:
  name: "My YouTube Channel"
  output_dir: "./output"

style:
  resolution: [1920, 1080]
  fps: 30
  font_family: "Noto Sans JP"
  primary_color: "#FFFFFF"
  background_color: "#1a1a2e"

audio:
  engine: "voicevox"
  speaker_id: 3  # Zundamon
  speed_scale: 1.0

narration:
  character: "ずんだもん"
  style: "casual"  # casual, formal, educational

content:
  llm_provider: "openrouter"
  model: "gemini-3-pro"

slides:
  provider: "openrouter"
  model: "nonobananapro"
  style: "presentation"  # presentation, illustration, minimal

video:
  renderer: "remotion"
  template: "default"
  output_format: "mp4"

pronunciation:
  # Proper noun pronunciation dictionary (VOICEVOX UserDict format)
  custom:
    "Bubble Tea":
      reading: "バブルティー"  # Katakana
      accent: 5               # Accent nucleus position
      word_type: "PROPER_NOUN"  # PROPER_NOUN, COMMON_NOUN, VERB, ADJECTIVE, SUFFIX
      priority: 10            # Priority (1-10, higher = more priority)
    "Ratatui":
      reading: "ラタトゥイ"
      accent: 4
      word_type: "PROPER_NOUN"
      priority: 10
    "人月":
      reading: "ニンゲツ"
      accent: 1
      word_type: "COMMON_NOUN"
      priority: 10
```

### 3. Processing Pipeline

```
URL Input
    ↓
[1. Content Fetch] - URL → Markdown/HTML retrieval
    ↓
[2. Script Generation] - Generate YouTube script with LLM
    ↓
[3. Phrase Split] - Segment into 3-6 second phrases
    ↓
[4. Pronunciation] - Apply reading dictionary
    ↓
[5. Audio Generation] - VOICEVOX speech synthesis
    ↓
[6. Slide Generation] - OpenRouter + NonobananaPro
    ↓
[7. Video Render] - Remotion (TypeScript/React)
    ↓
Output: MP4 file + metadata JSON
```

### 4. Video Rendering: Remotion

Using **Remotion** (leveraging existing experimental assets):
- High-quality animations
- Flexible templates based on TypeScript/React
- Proven track record at `/Users/tumf/work/study/daihon/`

**Architecture**:
- Python side: Generate assets (audio, slides) + output metadata JSON
- Remotion side: Load JSON and render video

```
Python → assets/ + composition.json → Remotion → output.mp4
```

### 5. Slide Generation: OpenRouter + NonobananaPro

Generate slide images using **NonobananaPro** (via OpenRouter):
- High-quality illustration/slide image generation
- Visually appealing content for YouTube

```yaml
# Example configuration in config.yaml
slides:
  provider: "openrouter"
  model: "nonobananapro"
  style: "presentation"  # presentation, illustration, minimal
```

**Processing Flow**:
1. Generate prompts from each section of the script
2. Call NonobananaPro via OpenRouter API
3. Retrieve and save 1920x1080 images

### 6. Speech Synthesis and User Dictionary

Direct use of VOICEVOX Core (migrating existing implementation):
```python
from voicevox_core import UserDictWord
from voicevox_core.blocking import UserDict, OpenJtalk, Synthesizer, VoiceModelFile

# Create user dictionary
user_dict = UserDict()
user_dict.add_word(UserDictWord(
    surface="Bubble Tea",
    pronunciation="バブルティー",  # Katakana
    accent_type=5,
    word_type="PROPER_NOUN",
    priority=10
))

# Apply to OpenJTalk
open_jtalk = OpenJtalk(dict_dir)
open_jtalk.use_user_dict(user_dict)

# Pass to Synthesizer
synthesizer = Synthesizer(onnxruntime, open_jtalk)
```

**Benefits of User Dictionary**:
- Morphological analysis works correctly (proper accent and intonation)
- Dictionary managed in YAML, automatically applied on startup
- Dictionary can be saved and loaded in JSON format

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| VOICEVOX environment dependency (macOS dylib) | Make path configurable via environment variables |
| LLM API costs | Caching mechanism, local LLM support |
| Memory for long videos | Streaming processing |
| Difficulty setting accent positions | Provide default value (0=auto-estimate) |

## Migration Plan

1. Phase 1: Core functionality (URL → script → audio generation + Remotion integration foundation)
2. Phase 2: Slide generation (NonobananaPro integration)
3. Phase 3: Full pipeline completion + CLI

## Open Questions

- [ ] Distribution method for voice models (.vvm)
- [ ] Whether YouTube auto-upload functionality is needed
- [ ] How to share Remotion templates

## Technical Notes

### VOICEVOX UserDict Investigation Results

Confirmed through experiments (2024-12-29):

1. **VOICEVOX Core supports user dictionaries**
   - Create entries with `voicevox_core.UserDictWord`
   - Manage dictionary with `voicevox_core.blocking.UserDict`
   - Apply with `OpenJtalk.use_user_dict()`

2. **Morphological analysis issues resolved**
   - Simple hiragana substitution breaks morphological analysis
   - Using UserDict properly registers in OpenJTalk dictionary, maintaining correct accent and intonation

3. **Implementation pattern**
   ```python
   user_dict = UserDict()
   user_dict.add_word(UserDictWord(
       surface="Bubble Tea",
       pronunciation="バブルティー",  # Katakana required
       accent_type=5,                # 0=auto-estimate
       word_type="PROPER_NOUN",
       priority=10
   ))
   open_jtalk = OpenJtalk(dict_dir)
   open_jtalk.use_user_dict(user_dict)
   ```

4. **Dictionary persistence**
   - Save to JSON with `user_dict.save("dict.json")`
   - Load with `user_dict.load("dict.json")`
