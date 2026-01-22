## ADDED Requirements

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
