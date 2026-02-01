## MODIFIED Requirements
### Requirement: Generate Command

The existing `generate` command SHALL remain functional with all current options.

The `generate` command SHALL delegate each pipeline stage to dedicated functions/modules so the command handler remains small and unit-testable.

The `generate` command SHALL internally use the extracted common functions:
- `_create_script()` for script generation
- `_generate_audio()` for audio synthesis
- `_generate_slides()` for slide creation
- `_render_video()` for video rendering

The `generate` command SHALL also support the new common options:
- `--force`
- `--quiet`
- `--verbose`
- `--dry-run`

#### Scenario: Full pipeline execution
- **GIVEN** a valid URL and API key
- **WHEN** user runs `movie-generator generate <URL>`
- **THEN** the system executes all stages sequentially
- **AND** produces a final video file

#### Scenario: Resume from existing script
- **GIVEN** `script.yaml` already exists
- **WHEN** user runs `movie-generator generate <script.yaml>`
- **THEN** the system skips script generation
- **AND** proceeds with audio, slides, and video generation
