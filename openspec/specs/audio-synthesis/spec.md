# Audio Synthesis Specification

## Purpose

This specification defines the audio synthesis system for the movie generator application. The system provides an abstraction layer for multiple speech synthesis engines, supports per-persona voice synthesis, and manages pronunciation dictionaries. This enables multi-speaker dialogue videos with different voice characteristics for each persona.

## Requirements

### Requirement: Speech Synthesis Engine Abstraction

The system SHALL provide an abstraction interface that supports multiple speech synthesis engines.

#### Scenario: VOICEVOX Speech Synthesis
- **GIVEN** a persona's `synthesizer.engine` is set to `"voicevox"`
- **WHEN** phrase audio synthesis is requested
- **THEN** audio is generated using the VOICEVOX engine
- **AND** the `speaker_id` and `speed_scale` parameters are applied

#### Scenario: Unsupported Engine
- **GIVEN** a persona's `synthesizer.engine` is set to an unsupported engine (e.g., `"coefont"`)
- **WHEN** audio synthesis is initialized
- **THEN** an error is raised
- **AND** the error message indicates "unsupported engine"

#### Scenario: Engine-Specific Parameters
- **GIVEN** a persona's `synthesizer` contains arbitrary parameters
- **WHEN** the corresponding engine is implemented
- **THEN** those parameters are applied to the audio synthesis

### Requirement: Per-Persona Audio Synthesis

The system SHALL synthesize audio according to the persona assigned to each phrase.

#### Scenario: Multi-Persona Audio Synthesis
- **GIVEN** a phrase list:
  ```
  Phrase(text="やっほー！", persona_id="zundamon")
  Phrase(text="こんにちは", persona_id="metan")
  ```
- **AND** persona configuration:
  ```yaml
  personas:
    - id: "zundamon"
      synthesizer: {engine: "voicevox", speaker_id: 3}
    - id: "metan"
      synthesizer: {engine: "voicevox", speaker_id: 2}
  ```
- **WHEN** `synthesize_phrases()` is called
- **THEN** phrase 0 is synthesized with speaker_id=3
- **AND** phrase 1 is synthesized with speaker_id=2

#### Scenario: Unknown Persona ID Error
- **GIVEN** a phrase has `persona_id="unknown"`
- **AND** no persona with ID `"unknown"` is defined
- **WHEN** audio synthesis is executed
- **THEN** an error is raised
- **AND** the error message includes the unknown persona ID

### Requirement: Per-Persona Pronunciation Dictionary

Each persona SHALL support having an independent pronunciation dictionary (optional in current version).

#### Scenario: Shared Pronunciation Dictionary
- **GIVEN** the global pronunciation dictionary has `"ENGINE" -> "エンジン"`
- **WHEN** audio synthesis is executed for any persona
- **THEN** all personas use this dictionary

#### Scenario: Persona-Specific Pronunciation Dictionary (Future Extension)
- **GIVEN** persona A has `"東京" -> "トーキョー"`
- **AND** persona B has `"東京" -> "とうきょう"`
- **WHEN** audio synthesis is executed for each persona
- **THEN** different pronunciations are applied per persona

### Requirement: Audio File Naming Convention

Generated audio files SHALL be named using the phrase's `original_index`.

#### Scenario: Audio File Name
- **GIVEN** a phrase's `original_index` is 5
- **WHEN** audio synthesis is executed
- **THEN** the filename is `phrase_0005.wav`
- **AND** the persona ID is not included (original_index ensures uniqueness)

### Requirement: Audio Synthesis Caching

When an existing audio file is present, re-synthesis SHALL be skipped.

#### Scenario: Skip Existing Audio
- **GIVEN** `phrase_0000.wav` already exists
- **AND** the file size is greater than 0 bytes
- **WHEN** `synthesize_phrases()` is called
- **THEN** audio synthesis for that phrase is skipped
- **AND** a "Skipping existing audio" message is displayed

#### Scenario: Regenerate Corrupted Files
- **GIVEN** `phrase_0000.wav` exists but has 0 byte size
- **WHEN** `synthesize_phrases()` is called
- **THEN** the audio is regenerated

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/audio-synthesis/spec.md`.
