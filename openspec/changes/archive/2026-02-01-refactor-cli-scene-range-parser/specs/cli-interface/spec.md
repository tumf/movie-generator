## MODIFIED Requirements
### Requirement: Audio Generation Command

The CLI SHALL provide an `audio generate` subcommand that generates audio files from a script.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file
- `--scenes <range>`: Scene range to process (e.g., "1-3", "2", "6-")
- `--speaker-id <id>`: VOICEVOX speaker ID
- `--allow-placeholder`: Generate placeholder audio without VOICEVOX

Scene range parsing and validation SHALL be shared across commands and report consistent errors.

#### Scenario: Generate audio from script
- **GIVEN** a valid `script.yaml` file
- **WHEN** user runs `movie-generator audio generate ./output/script.yaml`
- **THEN** the system splits narration into phrases
- **AND** generates audio using VOICEVOX
- **AND** saves WAV files to `audio/` directory

#### Scenario: Audio files already exist
- **GIVEN** some audio files already exist in `audio/` directory
- **WHEN** user runs `movie-generator audio generate <script.yaml>`
- **THEN** the system skips existing audio files
- **AND** only generates missing audio files

#### Scenario: Script file not found
- **GIVEN** the specified script file does not exist
- **WHEN** user runs `movie-generator audio generate <non-existent.yaml>`
- **THEN** the system displays an error message
- **AND** exits with non-zero status

#### Scenario: Invalid scene range
- **GIVEN** the user specifies an invalid scene range (e.g., `--scenes 0`, `--scenes 3-2`, `--scenes a-b`)
- **WHEN** user runs `movie-generator audio generate <script.yaml> --scenes <range>`
- **THEN** the system displays a consistent validation error message
- **AND** exits with non-zero status
