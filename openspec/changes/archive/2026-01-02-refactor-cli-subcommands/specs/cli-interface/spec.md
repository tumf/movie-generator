# CLI Interface Specification (Delta)

## ADDED Requirements

### Requirement: Script Creation Command

The CLI SHALL provide a `script create` subcommand that generates a video script from a URL.

The command SHALL accept the following options:
- `--output, -o <dir>`: Output directory (default: `./output`)
- `--config, -c <path>`: Path to config file
- `--api-key <key>`: OpenRouter API key
- `--mcp-config <path>`: Path to MCP configuration file
- `--character <name>`: Narrator character name
- `--style <style>`: Narration style
- `--model <model>`: LLM model to use

#### Scenario: Generate script from URL
- **GIVEN** a valid blog URL
- **WHEN** user runs `movie-generator script create https://example.com/blog`
- **THEN** the system fetches content from the URL
- **AND** generates a video script using LLM
- **AND** saves `script.yaml` to the output directory

#### Scenario: Script already exists
- **GIVEN** `script.yaml` already exists in the output directory
- **WHEN** user runs `movie-generator script create <URL>`
- **THEN** the system skips script generation
- **AND** displays a message indicating the script already exists

---

### Requirement: Audio Generation Command

The CLI SHALL provide an `audio generate` subcommand that generates audio files from a script.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file
- `--scenes <range>`: Scene range to process (e.g., "1-3", "2", "6-")
- `--speaker-id <id>`: VOICEVOX speaker ID
- `--allow-placeholder`: Generate placeholder audio without VOICEVOX

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

---

### Requirement: Slides Generation Command

The CLI SHALL provide a `slides generate` subcommand that generates slide images from a script.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file
- `--api-key <key>`: OpenRouter API key
- `--scenes <range>`: Scene range to process
- `--model <model>`: Image generation model
- `--language, -l <lang>`: Language for slides (default: "ja")
- `--max-concurrent <n>`: Maximum concurrent API requests (default: 2)

#### Scenario: Generate slides from script
- **GIVEN** a valid `script.yaml` file with slide prompts
- **WHEN** user runs `movie-generator slides generate ./output/script.yaml`
- **THEN** the system generates slide images using AI
- **AND** saves PNG files to `slides/<lang>/` directory

#### Scenario: Slides already exist
- **GIVEN** some slide files already exist
- **WHEN** user runs `movie-generator slides generate <script.yaml>`
- **THEN** the system skips existing slide files
- **AND** only generates missing slides

---

### Requirement: Video Render Command

The CLI SHALL provide a `video render` subcommand that renders the final video.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file
- `--scenes <range>`: Scene range to render
- `--output, -o <file>`: Output video filename
- `--progress`: Show real-time rendering progress
- `--transition <type>`: Transition type (fade, slide, wipe, flip, clockWipe, none)
- `--fps <fps>`: Frames per second (default: 30)

#### Scenario: Render video from assets
- **GIVEN** a valid `script.yaml`, audio files, and slide files exist
- **WHEN** user runs `movie-generator video render ./output/script.yaml`
- **THEN** the system sets up Remotion project
- **AND** generates composition.json
- **AND** renders video to `output.mp4`

#### Scenario: Missing audio files
- **GIVEN** audio files are missing
- **WHEN** user runs `movie-generator video render <script.yaml>`
- **THEN** the system displays an error listing missing files
- **AND** suggests running `movie-generator audio generate` first

---

### Requirement: Force Overwrite Option

All CLI commands SHALL support the `--force` option.

When `--force` is specified:
- Existing files SHALL be overwritten without prompting
- No confirmation dialog SHALL be displayed

#### Scenario: Force overwrite script
- **GIVEN** `script.yaml` already exists
- **WHEN** user runs `movie-generator script create <URL> --force`
- **THEN** the system overwrites the existing script

#### Scenario: Force overwrite audio
- **GIVEN** audio files already exist
- **WHEN** user runs `movie-generator audio generate <script.yaml> --force`
- **THEN** the system regenerates all audio files

---

### Requirement: Quiet Mode Option

All CLI commands SHALL support the `--quiet` or `-q` option.

When `--quiet` is specified:
- Progress spinners and step messages SHALL NOT be displayed
- On success, only the final output path SHALL be printed
- Error messages SHALL still be displayed

#### Scenario: Quiet mode success
- **GIVEN** a valid URL
- **WHEN** user runs `movie-generator script create <URL> --quiet`
- **THEN** the system outputs only the script path on success (e.g., `./output/script.yaml`)

#### Scenario: Quiet mode error
- **GIVEN** an invalid URL
- **WHEN** user runs `movie-generator script create <invalid-url> --quiet`
- **THEN** the system displays the error message
- **AND** exits with non-zero status

---

### Requirement: Verbose Mode Option

All CLI commands SHALL support the `--verbose` or `-v` option.

When `--verbose` is specified:
- Detailed debug information SHALL be displayed
- File paths, sizes, and processing times SHALL be logged
- On error, full stack traces SHALL be displayed

#### Scenario: Verbose mode output
- **GIVEN** a valid URL
- **WHEN** user runs `movie-generator script create <URL> --verbose`
- **THEN** the system displays detailed progress including:
  - Content fetch time and size
  - LLM request/response timing
  - Output file path and size

---

### Requirement: Mutual Exclusivity of Quiet and Verbose

The CLI SHALL enforce that `--quiet` and `--verbose` are mutually exclusive.

#### Scenario: Both quiet and verbose specified
- **WHEN** user runs any command with both `--quiet` and `--verbose`
- **THEN** the system displays an error message
- **AND** exits with non-zero status without executing

---

### Requirement: Dry Run Mode Option

All CLI commands SHALL support the `--dry-run` or `-n` option.

When `--dry-run` is specified:
- File read operations SHALL be executed
- File write operations SHALL be skipped
- API calls SHALL be skipped
- External process execution SHALL be skipped
- The system SHALL output what would have been done

#### Scenario: Dry run script creation
- **GIVEN** a valid URL
- **WHEN** user runs `movie-generator script create <URL> --dry-run`
- **THEN** the system outputs:
  ```
  [DRY-RUN] Would fetch content from: <URL>
  [DRY-RUN] Would generate script with model: <model>
  [DRY-RUN] Would save script to: <path>
  ```
- **AND** no files are created

#### Scenario: Dry run with verbose
- **WHEN** user runs `movie-generator audio generate <script> --dry-run --verbose`
- **THEN** the system displays detailed information about what would be executed
- **AND** no audio files are generated

---

## MODIFIED Requirements

### Requirement: Generate Command

The existing `generate` command SHALL remain functional with all current options.

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
