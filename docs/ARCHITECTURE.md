# Movie Generator Architecture

## Overview

Movie Generator is a generic video production tool designed to create multiple, diverse videos from structured content. This document describes the architecture that enables managing many video projects while maintaining code reusability.

## Design Principles

1. **Data-Driven**: Videos are generated from declarative configuration files
2. **Project Isolation**: Each video project has its own directory with assets and settings
3. **Component Reusability**: Remotion components are generic and shared across all projects
4. **Configuration Hierarchy**: Settings cascade from global → project → composition levels

## Architecture Layers

### Layer 1: CLI & Workflow Management

**Purpose**: Project lifecycle management and orchestration

**Components**:
- `movie-generator` CLI tool
- Project scaffolding
- Pipeline execution
- Asset management

**Commands**:
```bash
# Create new project
movie-generator new <project-name>

# Generate audio from phrases
movie-generator audio <project-name>

# Generate slides
movie-generator slides <project-name>

# Render video
movie-generator render <project-name>

# Complete pipeline
movie-generator build <project-name>
```

### Layer 2: Content Generation

**Purpose**: Transform source content into video assets

**Pipeline**:
```
Source → Script → Phrases → Audio + Slides → Metadata
```

**Components**:
- Script parser
- Phrase segmenter
- Audio synthesizer (VOICEVOX)
- Slide generator (LLM)
- Metadata builder

### Layer 3: Video Rendering

**Purpose**: Compose assets into final video

**Technology**: Remotion (React-based video framework)

**Process**:
```
Metadata.json → Remotion Composition → MP4 Video
```

## Project Structure

### Project Directory Layout

```
projects/<project-name>/
├── project.yaml              # Project-specific configuration
├── script.md                 # Human-readable script
├── phrases.json              # Structured phrase data
├── assets/
│   ├── audio/               # Generated narration files
│   │   ├── 001.wav
│   │   ├── 002.wav
│   │   └── ...
│   ├── slides/              # Generated slide images
│   │   ├── slide_001.png
│   │   ├── slide_002.png
│   │   └── ...
│   └── metadata.json        # Rendering metadata
└── output/
    ├── preview.mp4          # Quick preview
    └── final.mp4            # Final rendered video
```

### Configuration Files

#### Global Config (`config/default.yaml`)

```yaml
# Shared defaults for all projects
style:
  resolution: [1920, 1080]
  fps: 30
  font_family: "Noto Sans JP"

audio:
  engine: "voicevox"
  speaker_id: 3

video:
  renderer: "remotion"
  output_format: "mp4"
```

#### Project Config (`projects/<name>/project.yaml`)

```yaml
# Override global settings per project
project:
  title: "TUI Evolution 2023-2024"
  description: "Evolution of TUI applications"

audio:
  speaker_id: 3  # Zundamon

style:
  background_color: "#1a1a1a"

pronunciation:
  custom:
    "Bubble Tea": "バブルティー"
    "Ratatui": "ラタトゥイ"
```

#### Phrases Data (`projects/<name>/phrases.json`)

```json
[
  {
    "id": "001",
    "subtitle": "Display text",
    "reading": "ひらがな reading for TTS",
    "slide": "slide_001.png",
    "section": "opening",
    "duration": 3.5,
    "audioFile": "001.wav"
  }
]
```

#### Render Metadata (`projects/<name>/assets/metadata.json`)

Generated automatically from phrases.json + measured audio durations:

```json
{
  "project": {
    "name": "TUI Evolution 2023-2024",
    "totalDuration": 78.2,
    "totalFrames": 2346
  },
  "phrases": [
    {
      "id": "001",
      "subtitle": "Display text",
      "slide": "slide_001.png",
      "audioFile": "001.wav",
      "duration": 3.5,
      "startFrame": 0,
      "endFrame": 105
    }
  ]
}
```

## Remotion Component Design

### Generic VideoGenerator Component

**File**: `remotion/src/VideoGenerator.tsx`

**Props Interface**:
```typescript
interface VideoGeneratorProps {
  // Path to project metadata (relative to public/)
  projectPath: string;

  // Optional style overrides
  style?: Partial<VideoStyle>;
}

interface VideoStyle {
  backgroundColor: string;
  subtitlePosition: 'top' | 'bottom' | 'middle';
  subtitleStyle: React.CSSProperties;
  slideTransition: 'fade' | 'none' | 'slide';
  slideFit: 'contain' | 'cover';
}
```

**Usage**:
```tsx
<Composition
  id="TUI-Evolution"
  component={VideoGenerator}
  durationInFrames={2346}
  fps={30}
  width={1920}
  height={1080}
  defaultProps={{
    projectPath: "projects/tui-evolution",
    style: {
      backgroundColor: "#1a1a1a"
    }
  }}
/>
```

### Dynamic Composition Generation

**File**: `remotion/src/Root.tsx`

Automatically discover and register all projects:

```typescript
export const RemotionRoot: React.FC = () => {
  const projects = discoverProjects(); // Read from public/projects/

  return (
    <>
      {projects.map(project => (
        <Composition
          key={project.id}
          id={project.id}
          component={VideoGenerator}
          durationInFrames={project.totalFrames}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            projectPath: `projects/${project.id}`,
            style: project.style
          }}
        />
      ))}
    </>
  );
};
```

### Reusable Layer Components

#### SlideLayer
- Handles slide display with transitions
- Groups consecutive identical slides
- Manages fade effects

#### AudioLayer
- Plays narration audio
- Synchronized with frame timing

#### SubtitleLayer
- Displays subtitles with fade-in
- Customizable positioning and styling
- Auto-sizing based on text length

## Data Flow

### Project Creation Flow

```
1. User: movie-generator new my-video
   ↓
2. CLI creates directory structure
   ↓
3. CLI generates project.yaml from template
   ↓
4. User edits script.md
```

### Content Generation Flow

```
1. User: movie-generator build my-video
   ↓
2. Parse script.md → phrases.json
   ↓
3. Generate audio files (VOICEVOX)
   ↓
4. Generate slide images (LLM)
   ↓
5. Measure audio durations
   ↓
6. Create metadata.json with timing
```

### Rendering Flow

```
1. Copy assets to remotion/public/projects/my-video/
   ↓
2. Generate/update Root.tsx compositions
   ↓
3. Execute: npx remotion render my-video output.mp4
   ↓
4. Move output.mp4 to projects/my-video/output/
```

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| CLI | Python (Click) | Project management |
| Config | YAML + Pydantic | Validation & type safety |
| Audio | VOICEVOX | TTS synthesis |
| Slides | OpenRouter (Gemini) | Image generation |
| Video | Remotion | Video composition |
| Runtime | Node.js + TypeScript | Remotion execution |

### File Formats

| Type | Format | Rationale |
|------|--------|-----------|
| Config | YAML | Human-readable, comments |
| Data | JSON | Machine-readable, strict |
| Script | Markdown | Readable, editable |
| Audio | WAV | Lossless, standard |
| Slides | PNG | Lossless, transparency |
| Video | MP4 | Universal compatibility |

## Workflow Examples

### Creating a New Video

```bash
# 1. Create project
movie-generator new my-blog-post

# 2. Edit configuration
vim projects/my-blog-post/project.yaml

# 3. Write script
vim projects/my-blog-post/script.md

# 4. Define phrases interactively
movie-generator phrases projects/my-blog-post/script.md

# 5. Generate all assets and render
movie-generator build my-blog-post

# 6. Preview
open projects/my-blog-post/output/final.mp4
```

### Iterating on Content

```bash
# Regenerate audio only (fast)
movie-generator audio my-blog-post

# Regenerate specific slide
movie-generator slides my-blog-post --slide 5

# Quick preview (first 30 seconds)
movie-generator render my-blog-post --preview

# Full render
movie-generator render my-blog-post
```

### Managing Multiple Projects

```bash
# List all projects
movie-generator list

# Get project status
movie-generator status my-blog-post

# Clean generated files (keep source)
movie-generator clean my-blog-post

# Archive completed project
movie-generator archive my-blog-post
```

## Extensibility Points

### Custom Slide Styles

Users can define custom slide generation prompts:

```yaml
# projects/my-video/project.yaml
slides:
  style: custom
  custom_prompt: |
    Create a minimalist slide with dark theme.
    Use neon accents and geometric shapes.
```

### Custom Remotion Components

Advanced users can override components:

```yaml
# projects/my-video/project.yaml
video:
  custom_components:
    subtitle: "./custom/MySubtitle.tsx"
```

### Post-Processing Hooks

```yaml
# projects/my-video/project.yaml
hooks:
  post_render:
    - "ffmpeg -i {output} -vf 'fade=in:0:30' {output}.tmp"
    - "mv {output}.tmp {output}"
```

## Performance Considerations

### Parallel Processing

- Audio generation: Parallelize per phrase
- Slide generation: Batch API calls
- Rendering: Use Remotion's built-in parallelization

### Caching

- Unchanged audio files are not regenerated
- Slides cached by content hash
- Metadata only rebuilt when source changes

### Optimization Targets

| Phase | Target | Current |
|-------|--------|---------|
| Audio (20 phrases) | <2 min | ~2 min |
| Slides (10 images) | <5 min | ~5 min |
| Render (2 min video) | <3 min | ~2 min |
| **Total** | **<10 min** | **~9 min** |

## Security & Privacy

### API Keys

Store in environment variables, not config files:

```bash
export OPENROUTER_API_KEY=sk-or-...
export VOICEVOX_API_KEY=...
```

### Data Isolation

Each project's data stays in its directory. No cross-project contamination.

### Gitignore Strategy

```gitignore
# Ignore generated assets
projects/*/assets/
projects/*/output/

# Keep source files
!projects/*/project.yaml
!projects/*/script.md
!projects/*/phrases.json
```

## Testing Strategy

### Unit Tests
- Configuration loading/merging
- Phrase parsing
- Timing calculations

### Integration Tests
- End-to-end project creation
- Audio generation pipeline
- Metadata generation

### Visual Regression Tests
- Remotion component snapshots
- Subtitle rendering
- Slide transitions

## Future Enhancements

### Short-term (1 month)
- [ ] Web UI for phrase editing
- [ ] Real-time preview in browser
- [ ] Batch project operations

### Medium-term (3 months)
- [ ] Multi-language support
- [ ] Custom fonts and themes
- [ ] Background music integration
- [ ] Animated transitions

### Long-term (6+ months)
- [ ] AI-powered script generation
- [ ] Auto-subtitling in multiple languages
- [ ] Cloud rendering service
- [ ] YouTube upload integration

## Migration Path

### From Current Setup

1. Move `voicevox/output_phrases/` → `projects/tui-evolution/assets/audio/`
2. Move `slides/` → `projects/tui-evolution/assets/slides/`
3. Create `projects/tui-evolution/project.yaml` from existing config
4. Update `remotion/src/Root.tsx` to use new VideoGenerator
5. Test rendering with new structure
6. Archive old structure

### Backward Compatibility

During transition, maintain both structures:
- New projects use `projects/` structure
- Legacy project (tui-evolution) stays in old structure
- CLI detects and handles both

## Conclusion

This architecture provides:
- **Scalability**: Easy to add new projects
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Customizable at multiple levels
- **Reusability**: Shared Remotion components
- **Simplicity**: Intuitive project structure

The key insight is treating Remotion as a **rendering engine** rather than a project-specific tool, with all project-specific data provided via props and external files.
