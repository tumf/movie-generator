# Configuration Management Specification

## ADDED Requirements

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

The system SHALL provide default configuration and merge it with user configuration.

#### Scenario: Apply Default Configuration
- **WHEN** user configuration specifies only some fields
- **THEN** unspecified fields use default values

#### Scenario: Override Default Configuration
- **WHEN** user configuration specifies a field
- **THEN** the default value is overridden with the user value

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
