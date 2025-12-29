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

The system SHALL generate YouTube video scripts from extracted content.

#### Scenario: Successful Script Generation
- **WHEN** blog content is provided
- **THEN** a structured script for YouTube is generated
- **AND** it includes opening, main content, and ending sections

#### Scenario: LLM Error Fallback
- **WHEN** LLM API returns an error
- **THEN** retry is attempted or an appropriate error message is displayed

### Requirement: Phrase-Based Audio Generation

The system SHALL generate audio in phrase units (3-6 seconds).

#### Scenario: Phrase Audio Generation
- **WHEN** script is split into phrases
- **THEN** an audio file (WAV) is generated for each phrase
- **AND** actual duration (seconds) of each phrase is recorded in metadata

#### Scenario: Proper Noun Pronunciation
- **WHEN** phrase contains a proper noun registered in pronunciation dictionary
- **THEN** audio is synthesized using the dictionary reading (hiragana)

### Requirement: Slide Generation with NonobananaPro

The system SHALL generate slide images for each section using NonobananaPro via OpenRouter.

#### Scenario: Successful AI Image Generation
- **WHEN** slide generation is requested
- **THEN** NonobananaPro is called via OpenRouter API
- **AND** a 1920x1080 PNG image is generated
- **AND** visual representation aligns with script content

#### Scenario: Style Consistency
- **WHEN** multiple slides are generated
- **THEN** style specified in YAML config (color tone, mood) is applied to all slides

#### Scenario: API Error Fallback
- **WHEN** NonobananaPro API returns an error
- **THEN** retry is attempted
- **AND** if failure persists, a placeholder image is used

### Requirement: Video Rendering with Remotion

The system SHALL use Remotion to compose slide images, audio, and subtitles into a video file.

#### Scenario: Remotion Integration
- **WHEN** asset generation is completed on Python side
- **THEN** composition.json (metadata) is output
- **AND** Remotion reads this metadata to render the video

#### Scenario: Successful Video Composition
- **WHEN** all assets (slides, audio) are ready
- **THEN** an H.264 encoded MP4 file is output
- **AND** subtitles are displayed synchronized with phrase timing

#### Scenario: Subtitle Synchronization
- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy

#### Scenario: Animation Effects
- **WHEN** video is generated
- **THEN** transition effects defined in Remotion template are applied
- **AND** fade and animations between slides are displayed smoothly

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
