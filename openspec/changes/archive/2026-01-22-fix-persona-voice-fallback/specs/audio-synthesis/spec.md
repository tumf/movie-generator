## MODIFIED Requirements

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

#### Scenario: Unknown Persona ID Warning
- **GIVEN** a phrase has `persona_id="unknown"`
- **AND** no persona with ID `"unknown"` is defined in the synthesizers dictionary
- **WHEN** audio synthesis is executed
- **THEN** a warning log message SHALL be emitted
- **AND** the warning SHALL include the unknown persona_id value
- **AND** the warning SHALL indicate which fallback voice is being used
- **AND** the first available synthesizer SHALL be used as fallback

#### Scenario: Persona ID Validation Before Synthesis
- **GIVEN** a list of phrases with various persona_id values
- **AND** a synthesizers dictionary with known persona IDs
- **WHEN** audio synthesis is about to begin
- **THEN** all persona_id values SHALL be validated against the synthesizers dictionary
- **AND** any mismatches SHALL be logged as warnings before synthesis starts
