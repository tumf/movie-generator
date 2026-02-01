# CLI Interface Specification

## Purpose

This specification defines the command-line interface for the movie-generator tool, which provides a modular workflow for generating YouTube slide videos from blog content.
## Requirements
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

The implementation SHALL reuse the same common URL/content/script pipeline as `generate` to avoid drift.

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

The implementation SHALL reuse the same script loading and phrase preparation logic as `generate` to avoid drift.

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

### Requirement: Slides Generation Command

The CLI SHALL provide a `slides generate` subcommand that generates slide images from a script.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file
- `--api-key <key>`: OpenRouter API key
- `--scenes <range>`: Scene range to process
- `--model <model>`: Image generation model
- `--language, -l <lang>`: Language for slides (default: "ja")
- `--max-concurrent <n>`: Maximum concurrent API requests (default: 2)

The implementation SHALL separate task planning (which slides to generate/skip) from task execution for maintainability.

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

### Requirement: Config Validation Command

The CLI SHALL provide a `config validate` subcommand that validates configuration files.

The command SHALL accept the following options:
- `--quiet, -q`: Suppress progress output, only show errors

The validation SHALL check:
- YAML syntax correctness
- Pydantic schema validation
- Existence of referenced files (background images, BGM, character images)
- Duplicate persona IDs

#### Scenario: Valid configuration file
- **GIVEN** a valid `config.yaml` file
- **WHEN** user runs `movie-generator config validate config.yaml`
- **THEN** the system displays a success message
- **AND** exits with status 0

#### Scenario: Invalid YAML syntax
- **GIVEN** a config file with invalid YAML syntax
- **WHEN** user runs `movie-generator config validate config.yaml`
- **THEN** the system displays YAML parsing error details
- **AND** exits with non-zero status

#### Scenario: Missing referenced file
- **GIVEN** a config file that references a non-existent background image
- **WHEN** user runs `movie-generator config validate config.yaml`
- **THEN** the system displays a warning about the missing file
- **AND** exits with status 0 (warnings don't fail validation)

#### Scenario: Schema validation error
- **GIVEN** a config file with invalid field values
- **WHEN** user runs `movie-generator config validate config.yaml`
- **THEN** the system displays Pydantic validation errors
- **AND** exits with non-zero status

---

### Requirement: Script Validation Command

The CLI SHALL provide a `script validate` subcommand that validates script files.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file for persona_id validation
- `--quiet, -q`: Suppress progress output, only show errors

The validation SHALL check:
- YAML syntax correctness
- Presence of required fields (title, sections)
- Section narrations format (list of objects with text field)
- persona_id references (when config is provided)
- Legacy format support (dialogues, single narration)

#### Scenario: Valid script file
- **GIVEN** a valid `script.yaml` file
- **WHEN** user runs `movie-generator script validate script.yaml`
- **THEN** the system displays success message with statistics
- **AND** shows section count and narration count
- **AND** exits with status 0

#### Scenario: Missing required fields
- **GIVEN** a script file without a title field
- **WHEN** user runs `movie-generator script validate script.yaml`
- **THEN** the system displays an error about missing title
- **AND** exits with non-zero status

#### Scenario: Invalid persona_id reference
- **GIVEN** a script with persona_id "unknown" and a config file
- **WHEN** user runs `movie-generator script validate script.yaml --config config.yaml`
- **THEN** the system displays an error about invalid persona_id
- **AND** exits with non-zero status

#### Scenario: Script validation with statistics
- **GIVEN** a valid script with 5 sections and 20 narrations
- **WHEN** user runs `movie-generator script validate script.yaml`
- **THEN** the system displays "✓ Valid script: 5 sections, 20 narrations"
- **AND** exits with status 0

---

### Requirement: Generate Command

The existing `generate` command SHALL remain functional with all current options.

The `generate` command SHALL delegate each pipeline stage to dedicated functions/modules so the command handler remains small and unit-testable.

The `generate` command SHALL internally use the extracted stage functions:
- `stage_script_resolution()` for script generation
- `stage_audio_generation()` for audio synthesis
- `stage_slides_generation()` for slide creation
- `stage_video_rendering()` for video rendering

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

### Requirement: Config Validate Command

CLI は `config validate` サブコマンドを提供しなければならない（SHALL）。
このコマンドは設定ファイル（YAML）を検証し、エラーがあれば報告する。

コマンドは以下のオプションを受け付ける:
- `<path>`: 検証する設定ファイルのパス（必須）
- `--quiet, -q`: エラーのみ表示

#### Scenario: 有効な設定ファイルの検証

- **GIVEN** 有効な YAML 形式の設定ファイル `config.yaml` が存在する
- **WHEN** ユーザーが `movie-generator config validate config.yaml` を実行する
- **THEN** 「✓ Configuration is valid」と表示される
- **AND** 終了コード 0 で終了する

#### Scenario: YAML 構文エラーの検出

- **GIVEN** YAML 構文が不正な設定ファイルが存在する
- **WHEN** ユーザーが `movie-generator config validate invalid.yaml` を実行する
- **THEN** YAML パースエラーメッセージが表示される
- **AND** エラー行番号が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: スキーマバリデーションエラーの検出

- **GIVEN** YAML 構文は正しいがスキーマに違反する設定ファイルが存在する
  ```yaml
  audio:
    speaker_id: "invalid"  # 数値であるべき
  ```
- **WHEN** ユーザーが `movie-generator config validate invalid-schema.yaml` を実行する
- **THEN** バリデーションエラーメッセージが表示される
- **AND** 不正なフィールド名が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: 参照ファイル不在エラーの検出

- **GIVEN** 設定ファイルに存在しないファイルへのパスが含まれる
  ```yaml
  video:
    background:
      type: "image"
      path: "/nonexistent/background.png"
  ```
- **WHEN** ユーザーが `movie-generator config validate config-missing-file.yaml` を実行する
- **THEN** 「File not found」エラーメッセージが表示される
- **AND** 不正なパスが含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: ペルソナ ID 重複エラーの検出

- **GIVEN** 設定ファイルに重複するペルソナ ID が含まれる
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      ...
    - id: "zundamon"  # 重複
      name: "ずんだもん2号"
      ...
  ```
- **WHEN** ユーザーが `movie-generator config validate config-duplicate-id.yaml` を実行する
- **THEN** 「Duplicate persona ID」エラーメッセージが表示される
- **AND** 重複した ID が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: ファイルが存在しない場合

- **GIVEN** 指定されたパスにファイルが存在しない
- **WHEN** ユーザーが `movie-generator config validate nonexistent.yaml` を実行する
- **THEN** 「File not found」エラーメッセージが表示される
- **AND** 終了コード 1 で終了する

---

### Requirement: Script Validate Command

CLI は `script validate` サブコマンドを提供しなければならない（SHALL）。
このコマンドはスクリプトファイル（YAML）を検証し、エラーがあれば報告する。

コマンドは以下のオプションを受け付ける:
- `<path>`: 検証するスクリプトファイルのパス（必須）
- `--config, -c <path>`: 設定ファイル（persona_id 参照検証用、オプション）
- `--quiet, -q`: エラーのみ表示

#### Scenario: 有効なスクリプトファイルの検証

- **GIVEN** 有効なスクリプトファイル `script.yaml` が存在する
- **WHEN** ユーザーが `movie-generator script validate script.yaml` を実行する
- **THEN** 「✓ Script is valid」と表示される
- **AND** セクション数と総 narration 数が表示される
- **AND** 終了コード 0 で終了する

#### Scenario: 必須フィールド不足の検出

- **GIVEN** `title` フィールドがないスクリプトファイルが存在する
- **WHEN** ユーザーが `movie-generator script validate invalid.yaml` を実行する
- **THEN** 「Missing required field: title」エラーメッセージが表示される
- **AND** 終了コード 1 で終了する

#### Scenario: 空の sections の検出

- **GIVEN** `sections` が空のスクリプトファイルが存在する
  ```yaml
  title: "Test"
  description: "Test video"
  sections: []
  ```
- **WHEN** ユーザーが `movie-generator script validate empty-sections.yaml` を実行する
- **THEN** 「Script has no sections」警告メッセージが表示される
- **AND** 終了コード 0 で終了する（警告のみ）

#### Scenario: 不正な narrations 形式の検出

- **GIVEN** narrations に不正な形式のエントリが含まれるスクリプト
  ```yaml
  sections:
    - title: "Section 1"
      narrations:
        - invalid_field: "test"  # text フィールドがない
  ```
- **WHEN** ユーザーが `movie-generator script validate invalid-narration.yaml` を実行する
- **THEN** 「Invalid narration format」エラーメッセージが表示される
- **AND** 問題のあるセクション番号が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: 存在しない persona_id の検出（config 指定時）

- **GIVEN** スクリプトファイルに存在しない persona_id が含まれる
- **AND** 設定ファイルにペルソナが定義されている
- **WHEN** ユーザーが `movie-generator script validate script.yaml --config config.yaml` を実行する
- **THEN** 「Unknown persona_id: xxx」警告メッセージが表示される
- **AND** 定義されている persona_id の一覧が表示される
- **AND** 終了コード 0 で終了する（警告のみ）

#### Scenario: config 未指定時の persona_id 検証スキップ

- **GIVEN** スクリプトファイルに persona_id が含まれる
- **WHEN** ユーザーが `movie-generator script validate script.yaml` を実行する（--config なし）
- **THEN** persona_id の参照妥当性チェックはスキップされる
- **AND** 構文とスキーマの検証のみ実行される

