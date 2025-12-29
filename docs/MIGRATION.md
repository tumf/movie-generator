# Migration Guide: Generic Multi-Project Architecture

This document explains the new architecture and how to migrate existing projects.

## What Changed?

### Before (Single Project)
```
movie-generator/
├── remotion/              # Hardcoded for one project
│   └── src/
│       └── VideoPhrases.tsx  # Project-specific
├── voicevox/
│   └── output_phrases/   # Global audio directory
└── slides/               # Global slides directory
```

### After (Multi-Project)
```
movie-generator/
├── projects/              # Source projects (version controlled)
│   ├── tui-evolution/
│   │   ├── project.yaml  # Project config
│   │   ├── script.md     # Script source
│   │   ├── phrases.json  # Phrase data
│   │   └── assets/       # Generated assets
│   │       ├── audio/
│   │       └── slides/
│   └── another-video/    # Additional projects
│
├── artifacts/             # Generated artifacts (gitignored)
│   └── remotion/         # Shared Remotion renderer
│       ├── src/
│       │   └── VideoGenerator.tsx  # Generic component
│       └── public/
│           └── projects/  # Symlinked project assets
│
└── src/movie_generator/
    ├── cli.py
    ├── config.py
    └── project.py        # NEW: Project management
```

## Key Benefits

1. **Multiple Projects**: Manage many videos in one repository
2. **Clean Separation**: Source (projects/) vs artifacts (artifacts/)
3. **Reusable Components**: One Remotion project serves all videos
4. **Git-Friendly**: Only track source files, ignore generated assets

## Migration Steps

### Step 1: Move Assets to Project Directory

If you have an existing project (e.g., TUI Evolution), move its assets:

```bash
# Create project structure
mkdir -p projects/tui-evolution/assets/{audio,slides}

# Move audio files
mv voicevox/output_phrases/*.wav projects/tui-evolution/assets/audio/

# Move slide files
mv slides/*.png projects/tui-evolution/assets/slides/

# Move metadata
mv voicevox/output_phrases/phrases_metadata.json projects/tui-evolution/phrases.json
```

### Step 2: Create Project Configuration

Create `projects/tui-evolution/project.yaml`:

```yaml
project:
  title: "TUI Evolution 2023-2024"
  description: "Evolution of TUI applications"

audio:
  speaker_id: 3  # Zundamon

pronunciation:
  custom:
    "Bubble Tea": "バブルティー"
    "Ratatui": "ラタトゥイ"
```

### Step 3: Update .gitignore

```gitignore
# Ignore artifacts
artifacts/

# Ignore generated project assets
projects/*/assets/
projects/*/output/

# Keep source files
!projects/*/project.yaml
!projects/*/script.md
!projects/*/phrases.json
```

### Step 4: Use Python Project API

```python
from movie_generator.project import Project

# Load existing project
project = Project("tui-evolution")

# Copy assets to Remotion
project.copy_to_remotion()

# Render video
# (See CLI commands below)
```

## CLI Commands

### Project Management

```bash
# Create new project
movie-generator new my-video

# List projects
movie-generator list

# Show project status
movie-generator status tui-evolution
```

### Content Generation

```bash
# Generate from URL (creates new project)
movie-generator generate https://blog.example.com/post

# Generate audio for existing project
movie-generator audio tui-evolution

# Generate slides for existing project
movie-generator slides tui-evolution
```

### Video Rendering

```bash
# Copy assets and render
movie-generator render tui-evolution

# Quick preview (30 seconds)
movie-generator render tui-evolution --preview
```

## Remotion Changes

### Old: Project-Specific Component

```tsx
// VideoPhrases.tsx (hardcoded paths)
import metadata from '../../voicevox/output_phrases/phrases_metadata.json';
<Audio src={staticFile(`audio_phrases/${audioFile}`)} />
```

### New: Generic Component

```tsx
// VideoGenerator.tsx (dynamic paths)
export interface VideoGeneratorProps {
  projectName: string;
  phrases: PhraseData[];
}

<Audio src={staticFile(`projects/${projectName}/audio/${audioFile}`)} />
```

### Composition Definition

```tsx
// Root.tsx
<Composition
  id="TUI-Evolution"
  component={VideoGenerator}
  defaultProps={{
    projectName: "tui-evolution",
    phrases: phrasesData
  }}
/>
```

## Project Structure

### Required Files

Every project must have:

- `project.yaml` - Configuration
- `phrases.json` - Phrase data with timings
- `assets/audio/*.wav` - Audio files
- `assets/slides/*.png` - Slide images (optional)

### Optional Files

- `script.md` - Human-readable script
- `output/*.mp4` - Rendered videos

## Troubleshooting

### "Cannot find module" errors in old remotion/

The old `remotion/` directory should not be used. All rendering happens in `artifacts/remotion/`.

**Solution**: Delete or ignore the old `remotion/` directory.

### Assets not found during rendering

Ensure assets are copied to Remotion before rendering:

```bash
# Copy assets
movie-generator prepare tui-evolution

# Or use project API
from movie_generator.project import Project
project = Project("tui-evolution")
project.copy_to_remotion()
```

### Phrase timing mismatches

Ensure `phrases.json` has accurate `duration` fields:

```json
{
  "id": "001",
  "subtitle": "Text to display",
  "audioFile": "001.wav",
  "duration": 3.5,  // Must match actual audio duration
  "slide": "slide_01.png"
}
```

## Best Practices

1. **Version Control**: Commit `project.yaml`, `phrases.json`, `script.md`
2. **Ignore Artifacts**: Never commit `assets/` or `artifacts/`
3. **Descriptive Names**: Use clear project names (e.g., `blog-post-title`)
4. **Configuration Inheritance**: Use global `config/default.yaml` for common settings
5. **Pronunciation Dictionary**: Share common terms in global config

## Next Steps

1. Create your first project: `movie-generator new my-first-video`
2. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
3. Explore project management with `movie_generator.project` module

## Rollback

If you need to revert to the old structure:

1. Keep the old `remotion/` directory
2. Continue using `voicevox/output_phrases/` and `slides/`
3. Use `VideoPhrases.tsx` component

Both structures can coexist during transition.
