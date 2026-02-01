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

The system SHALL use Remotion to compose slide images, audio, and subtitles into a video file. Each project SHALL have its own independent Remotion project with pnpm workspace integration. Slide transitions SHALL be rendered using Remotion's official `@remotion/transitions` package.

#### Scenario: Per-Project Remotion Setup

- **WHEN** a new video project is created
- **THEN** a dedicated Remotion project is generated in `projects/<name>/remotion/`
- **AND** the Remotion project is initialized via `pnpm create @remotion/video`
- **AND** TypeScript components (VideoGenerator.tsx, Root.tsx) are dynamically generated
- **AND** pnpm workspace is configured to share `node_modules/`
- **AND** `videoData.ts` is dynamically generated from phrase metadata
- **AND** `@remotion/transitions` package is included as a dependency

#### Scenario: Remotion Integration

- **WHEN** asset generation is completed on Python side
- **THEN** `composition.json` is generated with phrase/audio/slide paths, metadata, and transition settings
- **AND** Remotion components read `composition.json` to configure the video and transitions
- **AND** `npx remotion render` is executed with `--props` pointing to `composition.json`
- **AND** rendering happens in the project's `remotion/` directory

#### Scenario: Successful Video Composition

- **WHEN** all assets (slides, audio) are ready
- **THEN** an H.264 encoded MP4 file is output to the project directory
- **AND** subtitles are displayed synchronized with phrase timing
- **AND** configured transition effects are applied between slides

#### Scenario: Subtitle Synchronization

- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy

#### Scenario: Animation Effects

- **WHEN** video is generated
- **THEN** transition effects defined in configuration are applied between slides
- **AND** transitions are rendered using Remotion's `TransitionSeries` component
- **AND** the transition presentation and timing match the configuration

#### Scenario: Shared Dependencies via pnpm

- **WHEN** multiple video projects exist
- **THEN** Remotion dependencies including `@remotion/transitions` are shared via pnpm workspace
- **AND** disk usage is minimized through pnpm's hard-link mechanism
- **AND** each project can independently specify Remotion versions in its `package.json`

#### Scenario: Remotion Version Updates

- **WHEN** `pnpm create @remotion/video` is executed
- **THEN** the latest stable Remotion version is installed
- **AND** `@remotion/transitions` version is matched to the Remotion core version
- **AND** existing projects remain on their installed versions unless manually updated

### Requirement: Dynamic Remotion Project Generation

The system SHALL dynamically generate Remotion projects using official tooling and Python-generated TypeScript code.

The implementation SHALL split setup into well-named steps so failures are easier to diagnose while preserving behavior.

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

The system SHALL render subtitles with a fixed width of 80% of the video width to maximize text display area before wrapping.

#### Scenario: Fixed Subtitle Width

- **WHEN** a subtitle is displayed
- **THEN** the subtitle container has a fixed width of 80% of the video width (not maxWidth)
- **AND** the subtitle is horizontally centered on the screen
- **AND** text utilizes the full 80% width before wrapping

#### Scenario: Long Subtitle Text Wrapping

- **WHEN** subtitle text exceeds the 80% width container
- **THEN** the text wraps to multiple lines within the container
- **AND** maintains a line-height of 1.4 for readability

**Technical Note:**
- Previously used `maxWidth: '80%'` which caused container to shrink based on text length
- Changed to `width: '80%'` to ensure container always uses full 80% width
- This prevents premature text wrapping on shorter text

### Requirement: Blog Image Extraction

The system SHALL extract image information from blog HTML content for potential reuse as slide materials.

#### Scenario: Successful Image Extraction
- **WHEN** HTML content is parsed
- **THEN** all `<img>` elements are extracted
- **AND** `src` attribute is converted to absolute URL
- **AND** `alt` and `title` attributes are captured
- **AND** `aria-describedby` attribute is resolved to the referenced element's text content if present
- **AND** `width` and `height` attributes are captured if present

#### Scenario: Filtering Images by Alt Text Quality
- **WHEN** images are extracted from blog content
- **THEN** only images with meaningful description are included as slide candidates
- **AND** meaningful description is defined as: alt text (10+ characters) OR title attribute present OR aria-describedby text present
- **AND** images without any meaningful description are excluded from candidates but still tracked

#### Scenario: Relative URL Resolution
- **WHEN** image src is a relative URL
- **THEN** it is resolved to an absolute URL using the blog's base URL
- **AND** the absolute URL is stored in the image metadata

#### Scenario: Aria-Describedby Reference Resolution
- **WHEN** an `<img>` element has an `aria-describedby` attribute
- **THEN** the system looks up the element with the matching `id` in the same HTML document
- **AND** extracts the text content of that element
- **AND** stores it in the `aria_describedby` field of ImageInfo
- **AND** if the referenced element does not exist, `aria_describedby` is set to None

### Requirement: Source Image Reference in Script

The system SHALL allow script sections to reference existing blog images instead of generating new slides.

#### Scenario: LLM Image Assignment
- **WHEN** script generation is requested
- **AND** blog content contains extractable images with meaningful alt text
- **THEN** the image list is provided to the LLM
- **AND** LLM assigns appropriate images to relevant sections
- **AND** assigned images are stored as `source_image_url` in section metadata

#### Scenario: Exclusive Slide Source
- **WHEN** a section has `source_image_url` set
- **THEN** `slide_prompt` for that section MAY be omitted
- **AND** the source image takes precedence over AI generation

#### Scenario: Manual Override
- **WHEN** user manually specifies `source_image_url` in script.yaml
- **THEN** that URL is used regardless of LLM assignment
- **AND** the image is downloaded and used as the slide

### Requirement: Source Image Download and Processing

The system SHALL download and process source images for use as slide materials.

#### Scenario: Successful Image Download
- **WHEN** a section has `source_image_url` specified
- **THEN** the image is downloaded from the URL
- **AND** the image is resized to fit 1920x1080 (maintaining aspect ratio)
- **AND** the processed image is saved as the slide for that section

#### Scenario: Image Download Failure Fallback
- **WHEN** source image download fails
- **AND** `slide_prompt` is available for the section
- **THEN** AI slide generation is used as fallback
- **AND** a warning is logged about the fallback

#### Scenario: Image Download Failure Without Fallback
- **WHEN** source image download fails
- **AND** no `slide_prompt` is available for the section
- **THEN** an error is raised indicating missing slide source
- **AND** processing continues with placeholder image

#### Scenario: Minimum Resolution Check
- **WHEN** source image is downloaded
- **AND** image resolution is below 800x600
- **THEN** the image is rejected as too low quality
- **AND** fallback to AI generation is attempted if `slide_prompt` is available

### Requirement: LLM-Driven Logo Asset Identification

The system SHALL allow the LLM to identify required product logos during script generation and output logo URLs in the script metadata.

#### Scenario: LLM Identifies Required Logos

- **WHEN** script generation LLM analyzes blog content
- **AND** detects mentions of products or services
- **THEN** the LLM outputs `logo_assets` field in the script YAML
- **AND** each logo entry contains `name` and `url` fields
- **EXAMPLE**:
  ```yaml
  logo_assets:
    - name: "ProductX"
      url: "https://example.com/logo.svg"
  ```

#### Scenario: No Logos Needed

- **WHEN** blog content does not mention specific products or services
- **THEN** `logo_assets` field is omitted or empty list
- **AND** slide generation proceeds normally without logos

#### Scenario: LLM Cannot Find Logo URL

- **WHEN** LLM identifies a product but cannot determine official logo URL
- **THEN** LLM omits that product from `logo_assets`
- **AND** slide generation proceeds without that logo

### Requirement: Product Logo Asset Download

The system SHALL download product logos from LLM-specified URLs and store them in the project assets directory.

#### Scenario: Successful Logo Download

- **WHEN** script contains `logo_assets` with valid URLs
- **THEN** each logo image is downloaded from the specified URL
- **AND** saved to `projects/<name>/assets/logos/<sanitized-name>.png`
- **AND** filename is sanitized from the `name` field (alphanumeric + hyphens only)

#### Scenario: SVG to PNG Conversion

- **WHEN** downloaded logo is in SVG format
- **THEN** the system automatically converts it to PNG using cairosvg
- **AND** the converted PNG is saved to `assets/logos/`
- **AND** the original SVG is discarded after successful conversion

#### Scenario: Logo Already Exists

- **WHEN** a logo with the same name already exists in `assets/logos/`
- **THEN** download is skipped
- **AND** existing file is reused

#### Scenario: Download Failure Handling

- **WHEN** logo download fails due to network error or invalid URL
- **THEN** a warning message is displayed
- **AND** slide generation continues without that logo
- **AND** retry is attempted up to 3 times with exponential backoff

#### Scenario: SVG Conversion Failure

- **WHEN** SVG to PNG conversion fails
- **THEN** an error message is logged
- **AND** the unconverted SVG is kept in `assets/logos/`
- **AND** a warning suggests using PNG URL instead

### Requirement: Logo Asset Integration in Slide Generation

The system SHALL include downloaded logo assets in the slide generation prompt to guide the LLM.

#### Scenario: Logo Information in Prompt

- **WHEN** logos are successfully downloaded
- **THEN** slide generation prompt includes textual description of available logos
- **AND** prompt instructs LLM to incorporate logos appropriately
- **EXAMPLE**: "The following product logos are available: ProductX, ServiceY. Include ProductX logo in the top-right corner of the slide."

#### Scenario: Multiple Logos Available

- **WHEN** multiple logos are configured
- **THEN** all logos are mentioned in the prompt
- **AND** LLM is instructed to use appropriate logo based on slide content

#### Scenario: No Logos Configured

- **WHEN** `product_logos` field is omitted or empty
- **THEN** slide generation proceeds as normal without logo references
- **AND** behavior is identical to current implementation (backward compatible)

### Requirement: Script Generation Prompt Extension

The system SHALL instruct the LLM to identify and output product logo URLs during script generation.

#### Scenario: Logo Identification Prompt

- **WHEN** script generation prompt is constructed
- **THEN** prompt includes instruction to identify product/service logos
- **AND** instructs LLM to output `logo_assets` field with name and official logo URL
- **EXAMPLE**: "If the blog content mentions specific products or services, identify them and provide their official logo URLs in the `logo_assets` field."

#### Scenario: LLM Prompt Includes Examples

- **WHEN** script generation prompt is constructed
- **THEN** prompt includes example output format for `logo_assets`
- **AND** clarifies that URLs should point to official, publicly accessible logos

### Requirement: Project Directory Structure

The system SHALL create a dedicated directory for logo assets within the project structure.

#### Scenario: Logo Directory Creation

- **WHEN** a new project is initialized
- **THEN** `projects/<name>/assets/logos/` directory is created
- **AND** directory permissions allow read/write access

#### Scenario: Logo Directory in Existing Projects

- **WHEN** logo download is requested in an existing project without `logos/` directory
- **THEN** the directory is automatically created before download
- **AND** no error occurs if directory already exists

### Requirement: Slide Transition Configuration

The system SHALL support configurable transitions between slides using Remotion's official `@remotion/transitions` package.

#### Scenario: Default Fade Transition

- **WHEN** video generation is requested without explicit transition configuration
- **THEN** slides transition using the `fade` effect
- **AND** the transition duration is 15 frames (0.5 seconds at 30fps)
- **AND** the timing function is `linear`

#### Scenario: Custom Transition Type Selection

- **WHEN** `video.transition.type` is set to a supported type (`fade`, `slide`, `wipe`, `flip`, `clockWipe`)
- **THEN** the specified transition effect is applied between slides
- **AND** the transition is rendered using Remotion's `TransitionSeries` component

#### Scenario: Transition Duration Configuration

- **WHEN** `video.transition.duration_frames` is specified
- **THEN** the transition effect lasts for the specified number of frames
- **AND** the total video duration is adjusted accordingly (subtracting transition overlap)

#### Scenario: Timing Function Selection

- **WHEN** `video.transition.timing` is set to `linear`
- **THEN** the transition progresses at a constant rate
- **WHEN** `video.transition.timing` is set to `spring`
- **THEN** the transition uses spring physics animation

#### Scenario: Disable Transitions

- **WHEN** `video.transition.type` is set to `none`
- **THEN** no transition effect is applied between slides
- **AND** slides switch instantaneously
- **AND** the standard `Sequence` component is used instead of `TransitionSeries`

#### Scenario: Invalid Transition Type

- **WHEN** an unsupported transition type is specified
- **THEN** a validation error is raised
- **AND** the error message lists the supported transition types

### Requirement: Asset Regeneration Policy

The system SHALL apply different regeneration policies based on asset type to balance cost efficiency and configuration freshness.

#### Scenario: Script File Preservation

- **WHEN** `movie-generator generate` is executed
- **AND** a script file (`script.yaml` or `script_*.yaml`) already exists
- **THEN** the existing script file is reused
- **AND** script generation is skipped
- **AND** a message indicates the script was loaded from existing file

#### Scenario: Audio File Preservation

- **WHEN** audio generation is requested
- **AND** an audio file (`phrase_XXXX.wav`) already exists and is not empty
- **THEN** the existing audio file is reused
- **AND** audio synthesis is skipped for that phrase
- **AND** duration metadata is read from the existing file

#### Scenario: Slide File Preservation

- **WHEN** slide generation is requested
- **AND** a slide file (`slide_XXXX.png`) already exists and is not empty
- **THEN** the existing slide file is reused
- **AND** AI image generation is skipped for that slide

#### Scenario: Composition Always Regenerated

- **WHEN** `movie-generator generate` is executed
- **AND** `composition.json` already exists
- **THEN** `composition.json` is always regenerated with current configuration
- **AND** transition settings from the current config are applied
- **AND** the file is overwritten without prompting

#### Scenario: Video Always Re-rendered

- **WHEN** `movie-generator generate` is executed
- **AND** an output video file (`output.mp4`) already exists
- **THEN** the video is always re-rendered with current composition
- **AND** the existing video file is overwritten
- **AND** latest transition and style settings are applied

#### Scenario: Transition Configuration Change Detection

- **WHEN** video is re-rendered after configuration change
- **THEN** the new transition settings are reflected in the output video
- **AND** no manual intervention is required to apply new settings

#### Scenario: Language-Specific Video Output Filename

- **WHEN** video generation is executed
- **THEN** the output video filename includes the language identifier
- **AND** the filename follows the pattern `output_{lang}.mp4` (e.g., `output_ja.mp4`, `output_en.mp4`)
- **AND** when scene range is specified, the filename follows `output_{lang}_{range}.mp4`
  - Example: `output_ja_2.mp4` for single scene
  - Example: `output_en_1-3.mp4` for scene range

#### Scenario: Multi-Language Video Output Without Collision

- **WHEN** multiple languages are configured (e.g., `["ja", "en"]`)
- **AND** video generation is executed for each language
- **THEN** each language produces a separate video file
- **AND** video files do not overwrite each other
- **AND** all language-specific videos coexist in the same output directory

