# Configuration Management Specification

## Purpose

This specification defines the configuration management system for the movie generator application. The system enables users to customize video generation settings through YAML configuration files, including video styles, audio synthesis, pronunciation dictionaries, slide generation, and video rendering parameters.
## Requirements
### Requirement: YAML Configuration Loading

The system SHALL load and validate YAML configuration files.

#### Scenario: Load Valid Configuration File
- **WHEN** a valid YAML configuration file is specified
- **THEN** a configuration object is created
- **AND** all required fields are validated

#### Scenario: Invalid Configuration File
- **WHEN** a configuration file with missing required fields is provided
- **THEN** a specific error message is displayed
- **AND** the invalid field is clearly indicated

### Requirement: Default Configuration

The system SHALL provide default configuration and merge it with user configuration, including language settings.

#### Scenario: Apply Default Configuration
- **WHEN** user configuration specifies only some fields
- **THEN** unspecified fields use default values
- **AND** `content.languages` defaults to `["ja"]` if not specified

#### Scenario: Override Default Configuration
- **WHEN** user configuration specifies a field
- **THEN** the default value is overridden with the user value
- **AND** custom `content.languages` list replaces the default

### Requirement: Style Configuration

The system SHALL manage video style settings (resolution, colors, fonts, etc.) via configuration file.

#### Scenario: Resolution Settings
- **WHEN** `resolution: [1920, 1080]` is configured
- **THEN** output video is 1920x1080 pixels

#### Scenario: Font Settings
- **WHEN** `font_family` is configured
- **THEN** the specified font is applied to subtitles and slide text

### Requirement: Audio Configuration

The system SHALL manage voice synthesis settings (speaker, speed, etc.) via configuration file.

#### Scenario: Speaker Settings
- **WHEN** `speaker_id: 3` is configured
- **THEN** VOICEVOX generates audio using speaker ID=3 (Zundamon)

#### Scenario: Speed Settings
- **WHEN** `speed_scale: 1.2` is configured
- **THEN** audio is generated at 1.2x speed

### Requirement: Pronunciation Dictionary (VOICEVOX UserDict)

The system SHALL manage pronunciation dictionary for proper nouns via configuration file
and apply it as VOICEVOX UserDict.

#### Scenario: Apply User Dictionary
- **GIVEN** dictionary entries are configured in `pronunciation.custom`
- **WHEN** VOICEVOX is initialized
- **THEN** UserDict is created and applied to OpenJTalk
- **AND** morphological analysis uses correct readings and accents

#### Scenario: Custom Pronunciation (Detailed Settings)
- **GIVEN** the following is configured in `pronunciation.custom`
  ```yaml
  "GitHub":
    reading: "ギットハブ"
    accent: 4
    word_type: "PROPER_NOUN"
    priority: 10
  ```
- **WHEN** the script contains "GitHub"
- **THEN** VOICEVOX morphological analysis recognizes it as "ギットハブ"
- **AND** audio is synthesized with accent position 4
- **AND** subtitles display "GitHub" (original text)

#### Scenario: Simple Format (Backward Compatibility)
- **GIVEN** `"人月": "ニンゲツ"` is configured in `pronunciation.custom` (string only)
- **WHEN** dictionary is loaded
- **THEN** default values are applied (accent: 0, word_type: "COMMON_NOUN", priority: 5)

#### Scenario: Save and Load Dictionary
- **WHEN** user dictionary is created
- **THEN** it can be saved to a JSON file
- **AND** it can be loaded and reused on next startup

### Requirement: Slide Generation Configuration

The system SHALL manage slide generation (OpenRouter + NonobananaPro) configuration.

#### Scenario: OpenRouter API Configuration
- **WHEN** `slides.provider: "openrouter"` is configured
- **THEN** OpenRouter API is used
- **AND** OPENROUTER_API_KEY environment variable is required

#### Scenario: Style Configuration
- **WHEN** `slides.style` is configured
- **THEN** the specified style (presentation, illustration, minimal) is applied to all slides

### Requirement: Remotion Configuration

The system SHALL manage Remotion video rendering configuration.

#### Scenario: Template Configuration
- **WHEN** `video.template` is configured
- **THEN** the specified Remotion template is used

#### Scenario: Output Configuration
- **WHEN** `video.output_format` is configured
- **THEN** output is rendered in the specified format (mp4, webm)

---

**Note**: This specification was translated from the original Japanese version
archived in `openspec-archive/changes/add-video-generator/specs/config-management/spec.md`.

### Requirement: Configuration File Initialization Command

The system SHALL provide a CLI command to output the default configuration file.

#### Scenario: Output to stdout
- **WHEN** `movie-generator config init` is executed without options
- **THEN** the default configuration is output to stdout in YAML format
- **AND** the output includes helpful comments explaining each field

#### Scenario: Output to file
- **WHEN** `movie-generator config init --output config.yaml` is executed
- **THEN** the default configuration is written to `config.yaml`
- **AND** the file includes helpful comments explaining each field

#### Scenario: File already exists
- **GIVEN** a file named `config.yaml` exists
- **WHEN** `movie-generator config init --output config.yaml` is executed
- **THEN** a warning message is displayed
- **AND** the user is prompted to confirm overwrite
- **AND** the file is overwritten only if confirmed

#### Scenario: Invalid output path
- **WHEN** `movie-generator config init --output /invalid/path/config.yaml` is executed
- **AND** the directory `/invalid/path/` does not exist
- **THEN** an error message is displayed
- **AND** the command exits with non-zero status

#### Scenario: Generated config is valid
- **GIVEN** the output from `config init` is saved to a file
- **WHEN** the file is loaded with `load_config()`
- **THEN** the configuration is successfully validated
- **AND** all fields match the default values

### Requirement: Configuration File Format

The system SHALL generate configuration files with inline documentation, including language configuration.

#### Scenario: Comments for each section
- **WHEN** configuration is output
- **THEN** each top-level section includes a comment explaining its purpose
- **AND** `content.languages` includes a comment with examples: `["ja"]` or `["ja", "en"]`
- **AND** complex fields include inline comments with examples

#### Scenario: YAML format only
- **WHEN** configuration is output
- **THEN** the format is valid YAML
- **AND** the structure matches `config/default.yaml`
- **AND** the `languages` field is properly formatted as a YAML list

### Requirement: Multi-Language Content Configuration

The system SHALL support multiple output languages through the `content.languages` configuration field.

#### Scenario: Configure multiple languages
- **WHEN** `content.languages: ["ja", "en"]` is configured
- **THEN** the system generates scripts and slides for both Japanese and English
- **AND** language-specific files are created: `script_ja.yaml`, `script_en.yaml`
- **AND** language-specific slide directories are created: `slides/ja/`, `slides/en/`

#### Scenario: Default single language
- **WHEN** `content.languages` is not specified
- **THEN** the system defaults to `["ja"]` (Japanese only)
- **AND** maintains backward compatibility with existing behavior

#### Scenario: Single language specified
- **WHEN** `content.languages: ["en"]` is configured
- **THEN** the system generates English-only content
- **AND** creates `script_en.yaml` and `slides/en/` directory

#### Scenario: Invalid language code
- **WHEN** an unsupported language code is configured (e.g., `["fr"]`)
- **THEN** the system generates content using the default Japanese prompt template
- **OR** logs a warning about the unsupported language

### Requirement: Language-Specific Output Structure

The system SHALL organize generated content by language code.

#### Scenario: Language-specific script files
- **WHEN** multiple languages are configured
- **THEN** each language gets a separate script file named `script_{lang}.yaml`
- **AND** each file contains language-appropriate narration text

#### Scenario: Language-specific slide directories
- **WHEN** slides are generated for multiple languages
- **THEN** slides are saved in `{output_dir}/slides/{lang}/` subdirectories
- **AND** slide filenames remain consistent across languages: `slide_0000.png`, `slide_0001.png`, etc.

#### Scenario: Legacy single-language compatibility
- **WHEN** only one language is configured OR languages field is omitted
- **THEN** script is saved as `script.yaml` (without language suffix)
- **AND** slides are saved directly in `slides/` (without language subdirectory)
