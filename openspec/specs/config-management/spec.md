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

### Requirement: Persona Configuration

The system SHALL allow defining multiple speakers (personas) in the configuration file.

#### Scenario: Define Multiple Personas
- **WHEN** the following configuration is defined in the `personas` array:
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      character: "元気で明るい東北の妖精"
      synthesizer:
        engine: "voicevox"
        speaker_id: 3
        speed_scale: 1.0
      subtitle_color: "#8FCF4F"
    - id: "metan"
      name: "四国めたん"
      character: "優しくて落ち着いた四国の妖精"
      synthesizer:
        engine: "voicevox"
        speaker_id: 2
        speed_scale: 1.0
      subtitle_color: "#FF69B4"
  ```
- **THEN** 2 personas are registered
- **AND** each persona has a unique `id`
- **AND** each persona has audio synthesis settings

#### Scenario: Define Single Persona
- **WHEN** only one persona is defined in the `personas` array
- **THEN** the system operates as a single speaker
- **AND** behaves identically to existing single-speaker videos

#### Scenario: Duplicate Persona ID Error
- **WHEN** the same `id` is defined multiple times in the `personas` array
- **THEN** a configuration validation error occurs
- **AND** the error message displays the duplicate `id`

#### Scenario: Required Field Validation
- **WHEN** a persona does not include `id`, `name`, or `synthesizer`
- **THEN** a configuration validation error occurs
- **AND** the missing field name is displayed

### Requirement: Speech Synthesis Engine Abstraction Configuration

Each persona SHALL be able to specify the speech synthesis engine and its parameters via the `synthesizer` field.

#### Scenario: VOICEVOX Speech Synthesis Configuration
- **WHEN** the following `synthesizer` configuration is defined:
  ```yaml
  synthesizer:
    engine: "voicevox"
    speaker_id: 3
    speed_scale: 1.0
  ```
- **THEN** the VOICEVOX speech synthesis engine is used
- **AND** audio is generated with speaker_id=3
- **AND** audio is generated with speed_scale=1.0

#### Scenario: Future Support for Other Engines (Design Only)
- **WHEN** `synthesizer.engine` is set to a value other than `"voicevox"` (e.g., `"coefont"`)
- **THEN** an error occurs indicating the engine is not supported
- **AND** the error message displays "unsupported engine"

### Requirement: Subtitle Style Configuration

Each persona SHALL be able to specify the subtitle color via the `subtitle_color` field.

#### Scenario: Configure Subtitle Color
- **WHEN** a persona has `subtitle_color: "#8FCF4F"`
- **THEN** that persona's dialogue subtitles are displayed in green (#8FCF4F)

#### Scenario: Default Subtitle Color
- **WHEN** `subtitle_color` is omitted
- **THEN** the default color (#FFFFFF) is used

#### Scenario: Invalid Color Code
- **WHEN** `subtitle_color` is set to an invalid color code (e.g., "invalid")
- **THEN** a configuration validation error occurs
- **OR** the default color is used

### Requirement: Avatar Image Field (Future Use)

Each persona SHALL support having an `avatar_image` field, but it is not used in the current version.

#### Scenario: Define Avatar Image Path
- **WHEN** a persona has `avatar_image: "assets/zundamon.png"`
- **THEN** the configuration is loaded successfully
- **AND** the image is not used in the current version
- **AND** it can be used in future versions

### Requirement: Narration Configuration

The system SHALL allow configuring narration mode (single speaker or dialogue format).

#### Scenario: Enable Dialogue Mode
- **WHEN** the configuration includes `narration.mode: "dialogue"`
- **THEN** a multi-speaker dialogue format script is generated
- **AND** a dialogue format prompt is used for the LLM

#### Scenario: Single Speaker Mode
- **WHEN** the configuration includes `narration.mode: "single"`
- **THEN** a single-speaker script is generated
- **AND** the traditional single-speaker prompt is used

#### Scenario: Default Mode Value
- **WHEN** `narration.mode` is omitted
- **AND** 2 or more personas are defined in the `personas` array
- **THEN** `"dialogue"` mode is used

#### Scenario: Default Mode Value (Single Persona)
- **WHEN** `narration.mode` is omitted
- **AND** only one persona is defined in the `personas` array
- **THEN** `"single"` mode is used

#### Scenario: Remove Character Configuration
- **WHEN** dialogue mode is enabled
- **THEN** the `narration.character` field is ignored
- **AND** each persona's `character` field is used

#### Scenario: Maintain Style Configuration
- **WHEN** `narration.style` is configured
- **THEN** it is used for both single-speaker and dialogue formats
- **AND** the style is reflected in the LLM prompt

---

**Note**: Requirements added by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/config-management/spec.md`.
