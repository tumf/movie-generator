# Video Generation Specification

## Purpose

This specification defines the video generation system for creating YouTube slide videos from blog URLs. The system automates the entire workflow from content extraction to final video rendering, including script generation, phrase-based audio synthesis with VOICEVOX, AI-generated slide images, and video composition using Remotion.
## Requirements
### Requirement: URL Content Extraction

The system SHALL fetch content from blog URLs and convert it to text format.

#### Scenario: Successful Content Fetch from Blog URL
- **WHEN** a valid blog URL is specified
- **THEN** HTML/Markdown content is fetched
- **AND** title and body content are extracted

#### Scenario: Invalid URL
- **WHEN** an inaccessible URL is specified
- **THEN** an appropriate error message is displayed

### Requirement: Script Generation

The system SHALL generate YouTube video scripts from extracted content in multiple languages based on configuration.

#### Scenario: Successful Script Generation
- **WHEN** blog content is provided
- **AND** `content.languages` is configured with one or more language codes
- **THEN** a structured script for YouTube is generated for each configured language
- **AND** it includes opening, main content, and ending sections
- **AND** narration text is written in the appropriate language

#### Scenario: Multi-Language Script Generation
- **WHEN** `content.languages: ["ja", "en"]` is configured
- **THEN** two separate scripts are generated
- **AND** Japanese script uses Japanese prompt template with pronunciation support
- **AND** English script uses English prompt template without pronunciation support
- **AND** both scripts include slide prompts in English

#### Scenario: Language-Specific Prompt Selection
- **WHEN** script generation is requested for a specific language
- **THEN** the appropriate prompt template for that language is used
- **AND** the generated narration matches the language's natural speech patterns

#### Scenario: LLM Error Fallback
- **WHEN** LLM API returns an error
- **THEN** retry is attempted or an appropriate error message is displayed
- **AND** failure for one language does not prevent generation of other languages

### Requirement: Phrase-Based Audio Generation

The system SHALL generate audio in phrase units (3-6 seconds) with intelligent splitting that respects quotation marks and natural break points.

#### Scenario: Phrase Audio Generation
- **WHEN** script is split into phrases
- **THEN** an audio file (WAV) is generated for each phrase
- **AND** actual duration (seconds) of each phrase is recorded in metadata

#### Scenario: Proper Noun Pronunciation
- **WHEN** phrase contains a proper noun registered in pronunciation dictionary
- **THEN** audio is synthesized using the dictionary reading (hiragana)

#### Scenario: Quote-Aware Phrase Splitting
- **WHEN** narration text contains Japanese quotation marks (`「」`)
- **THEN** the splitting algorithm does NOT split inside quotation marks
- **AND** quotes remain balanced in each phrase
- **AND** very long quoted sections (>1.5x max_chars) are allowed to split at closing quote boundary

#### Scenario: Prioritized Split Points
- **WHEN** multiple split candidates exist
- **THEN** period (`。`) is prioritized over comma (`、`)
- **AND** comma (`、`) is prioritized over newline (`\n`)
- **AND** emergency splits at max_chars only occur outside quotation marks

#### Scenario: Punctuation-Only Phrase Filtering
- **WHEN** a phrase would contain only punctuation marks (`。、！？\n`)
- **THEN** that phrase is NOT added to the phrase list
- **AND** empty or whitespace-only phrases are also filtered out

### Requirement: Slide Generation with NonobananaPro

The system SHALL generate slide images for each section and language using NonobananaPro via OpenRouter.

#### Scenario: Successful AI Image Generation
- **WHEN** slide generation is requested
- **THEN** NonobananaPro is called via OpenRouter API
- **AND** a 1920x1080 PNG image is generated
- **AND** visual representation aligns with script content
- **AND** slides are saved in language-specific subdirectories

#### Scenario: Multi-Language Slide Generation
- **WHEN** slides are generated for multiple languages
- **THEN** each language's slides are saved in `slides/{lang}/` subdirectory
- **AND** slide filenames remain consistent: `slide_0000.png`, `slide_0001.png`, etc.
- **AND** slide prompts are written in English (for image generation API compatibility)
- **AND** text to display on slides is specified in the target language within the prompt
  - Example (Japanese): "A slide with text 'データベース設計' in the center, modern design"
  - Example (English): "A slide with text 'Database Design' in the center, modern design"

#### Scenario: Style Consistency
- **WHEN** multiple slides are generated
- **THEN** style specified in YAML config (color tone, mood) is applied to all slides
- **AND** style is consistent across all languages

#### Scenario: API Error Fallback
- **WHEN** NonobananaPro API returns an error
- **THEN** retry is attempted
- **AND** if failure persists, a placeholder image is used
- **AND** failure for one language does not prevent generation of other languages

### Requirement: Video Rendering with Remotion

The system SHALL use Remotion to compose slide images, audio, and subtitles into a video file. Each project SHALL have its own independent Remotion project with pnpm workspace integration.

#### Scenario: Per-Project Remotion Setup
- **WHEN** a new video project is created
- **THEN** a dedicated Remotion project is generated in `projects/<name>/remotion/`
- **AND** the Remotion project is initialized via `pnpm create @remotion/video`
- **AND** TypeScript components (VideoGenerator.tsx, Root.tsx) are dynamically generated
- **AND** pnpm workspace is configured to share `node_modules/`
- **AND** `videoData.ts` is dynamically generated from phrase metadata

#### Scenario: Remotion Integration
- **WHEN** asset generation is completed on Python side
- **THEN** `composition.json` is generated with phrase/audio/slide paths and metadata
- **AND** Remotion components read `composition.json` to configure the video
- **AND** `npx remotion render` is executed with `--props` pointing to `composition.json`
- **AND** rendering happens in the project's `remotion/` directory

#### Scenario: Successful Video Composition
- **WHEN** all assets (slides, audio) are ready
- **THEN** an H.264 encoded MP4 file is output to the project directory
- **AND** subtitles are displayed synchronized with phrase timing

#### Scenario: Subtitle Synchronization
- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy

#### Scenario: Animation Effects
- **WHEN** video is generated
- **THEN** transition effects defined in Remotion template are applied
- **AND** fade and animations between slides are displayed smoothly

#### Scenario: Shared Dependencies via pnpm
- **WHEN** multiple video projects exist
- **THEN** Remotion dependencies are shared via pnpm workspace
- **AND** disk usage is minimized through pnpm's hard-link mechanism
- **AND** each project can independently specify Remotion versions in its `package.json`

#### Scenario: Remotion Version Updates
- **WHEN** `pnpm create @remotion/video` is executed
- **THEN** the latest stable Remotion version is installed
- **AND** existing projects remain on their installed versions unless manually updated

### Requirement: Dynamic Remotion Project Generation

The system SHALL dynamically generate Remotion projects using official tooling and Python-generated TypeScript code.

#### Scenario: Remotion Project Initialization
- **WHEN** `Project.setup_remotion_project()` is called
- **THEN** `pnpm create @remotion/video` is executed with `--template blank`
- **AND** a minimal Remotion project is created in `projects/<name>/remotion/`
- **AND** the project is automatically added to pnpm workspace

#### Scenario: TypeScript Component Generation
- **WHEN** Remotion project is initialized
- **THEN** `VideoGenerator.tsx` is dynamically generated from Python template
- **AND** `Root.tsx` is dynamically generated from Python template
- **AND** `remotion.config.ts` is generated with project-specific settings
- **AND** components include proper TypeScript types and React imports

#### Scenario: Project Configuration
- **WHEN** Remotion project is set up
- **THEN** `package.json` is updated with project-specific name `@projects/<name>`
- **AND** `composition.json` is generated from phrase metadata
- **AND** TypeScript components import and read `composition.json`
- **AND** symbolic links are created from `public/audio` and `public/slides` to project asset directories

### Requirement: pnpm Workspace Configuration

The system SHALL use pnpm workspaces to manage Remotion projects efficiently.

#### Scenario: Workspace Definition
- **GIVEN** a `pnpm-workspace.yaml` file exists at repository root
- **WHEN** the workspace is configured
- **THEN** it includes `projects/*/remotion` as workspace members

#### Scenario: Dependency Installation
- **WHEN** `pnpm install` is executed at repository root
- **THEN** all workspace dependencies are installed
- **AND** `node_modules/` at root contains shared dependencies
- **AND** each project's `remotion/node_modules/` links to the shared store

#### Scenario: pnpm Not Installed
- **WHEN** `pnpm` is not available on the system
- **THEN** an informative error message is displayed
- **AND** installation instructions for pnpm are provided

### Requirement: CLI Interface

The system SHALL execute batch video generation from command line.

#### Scenario: Basic Video Generation
- **GIVEN** a valid configuration file exists
- **WHEN** `movie-generator generate <url>` command is executed
- **THEN** a video file is generated in the specified output directory

#### Scenario: Progress Display
- **WHEN** video generation is in progress
- **THEN** progress of each step is displayed in the terminal

---

**Note**: This specification was translated from the original Japanese version  
archived in `openspec-archive/changes/add-video-generator/specs/video-generation/spec.md`.

### Requirement: Multi-Language Content Integration

The system SHALL provide a unified interface for generating scripts and slides for multiple languages.

#### Scenario: Batch Multi-Language Generation
- **WHEN** `generate_multilang_content()` is called with a config containing multiple languages
- **THEN** scripts are generated for all configured languages
- **AND** slides are generated for all configured languages
- **AND** language-specific output files are created
- **AND** a dictionary mapping language codes to VideoScript objects is returned

#### Scenario: Language-Specific Script Files
- **WHEN** multi-language generation is complete
- **THEN** each language has a separate script file: `script_{lang}.yaml`
- **AND** each script file contains language-appropriate narration
- **AND** Japanese scripts include pronunciation dictionary entries
- **AND** English scripts have empty pronunciation arrays

#### Scenario: Backward Compatibility Mode
- **WHEN** only one language is configured OR languages field is omitted
- **THEN** single script file `script.yaml` is created (legacy format)
- **AND** slides are saved directly in `slides/` without language subdirectory
- **AND** existing tools and scripts continue to work without modification

### Requirement: Language-Specific Script Detection

The system SHALL automatically detect and process language-specific script files.

#### Scenario: Detect Language-Specific Scripts
- **WHEN** the slide generation script runs
- **THEN** it searches for `script_*.yaml` files (e.g., `script_ja.yaml`, `script_en.yaml`)
- **AND** processes each detected language sequentially
- **AND** reports progress and results per language

#### Scenario: Legacy Script Fallback
- **WHEN** no `script_*.yaml` files are found
- **THEN** the system looks for legacy `script.yaml` file
- **AND** treats it as Japanese content
- **AND** generates slides in the legacy location

#### Scenario: Mixed Legacy and Multi-Language
- **WHEN** both `script.yaml` and `script_*.yaml` files exist
- **THEN** `script_*.yaml` files take precedence
- **AND** legacy `script.yaml` is ignored

### Requirement: Subtitle Display Text Separation

The system SHALL provide separate text representations for narration audio and subtitle display to optimize readability.

#### Scenario: Subtitle Text Without Trailing Punctuation
- **WHEN** `Phrase.get_subtitle_text()` is called
- **THEN** trailing Japanese punctuation (`。`, `、`) is removed from the text
- **AND** punctuation in the middle of the text is preserved
- **AND** the original `Phrase.text` remains unchanged for audio generation

#### Scenario: Empty Subtitle Text Handling
- **WHEN** a phrase consists only of trailing punctuation
- **THEN** `get_subtitle_text()` returns an empty string
- **AND** the subtitle is still rendered (or omitted based on rendering logic)

#### Scenario: Multiple Trailing Punctuation Removal
- **WHEN** text has consecutive trailing punctuation (e.g., `。、`)
- **THEN** all trailing punctuation marks are removed iteratively
- **AND** resulting text has no trailing punctuation

### Requirement: Subtitle Synchronization

The system SHALL use cleaned subtitle text in video composition while maintaining phrase timing accuracy.

#### Scenario: Remotion Subtitle Rendering
- **WHEN** Remotion composition is generated
- **THEN** subtitle text is obtained via `Phrase.get_subtitle_text()`
- **AND** subtitles are displayed without trailing punctuation
- **AND** audio narration uses the full `Phrase.text` with punctuation intact

#### Scenario: Subtitle-Audio Timing Consistency
- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy
- **AND** subtitle display uses cleaned text while audio includes all punctuation

### Requirement: Subtitle Display Area

The system SHALL display subtitles within a horizontally constrained area to ensure readability.

#### Scenario: Maximum Subtitle Width

- **WHEN** a subtitle is rendered on the video
- **THEN** the subtitle container width SHALL NOT exceed 80% of the video width
- **AND** the subtitle text is horizontally centered within the video frame
- **AND** the subtitle remains fully visible without extending to screen edges

#### Scenario: Long Subtitle Text Wrapping

- **WHEN** subtitle text exceeds the maximum width
- **THEN** the text wraps to multiple lines within the 80% width constraint
- **AND** line height is maintained at 1.4 for readability
- **AND** all wrapped lines remain within the constrained area

