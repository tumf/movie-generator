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

### Requirement: キャラクター画像設定（Phase 1: 静的アバター）

システムは、ペルソナ設定でキャラクター画像（ベース画像）を指定可能にしなければならない（SHALL）。

**Note**: この要件は `add-static-avatar-overlay` の `avatar_image` 機能を統合し、`character_image` として拡張します。

#### Scenario: キャラクター画像の設定

- **GIVEN** 設定ファイルに以下のペルソナ設定がある:
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      character_image: "assets/characters/zundamon/base.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_image` フィールドに `"assets/characters/zundamon/base.png"` が設定される
- **AND** ファイルパスの存在チェックが実行される

#### Scenario: avatar_image の後方互換性（alias）

- **GIVEN** 設定ファイルに以下がある（旧フィールド名）:
  ```yaml
  personas:
    - id: "zundamon"
      avatar_image: "assets/avatars/zundamon.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_image` フィールドに値が設定される
- **AND** `avatar_image` は `character_image` の alias として動作する

### Requirement: スプライト画像設定（Phase 2: リップシンク・まばたき）

システムは、ペルソナ設定でスプライト画像（口開き、目閉じ）を指定可能にしなければならない（SHALL）。

#### Scenario: 口開き画像の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_image: "assets/characters/zundamon/base.png"
      mouth_open_image: "assets/characters/zundamon/mouth_open.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `mouth_open_image` フィールドに設定される
- **AND** リップシンクアニメーションに使用される

#### Scenario: 目閉じ画像の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_image: "assets/characters/zundamon/base.png"
      eye_close_image: "assets/characters/zundamon/eye_close.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `eye_close_image` フィールドに設定される
- **AND** まばたきアニメーションに使用される

#### Scenario: 画像未設定時のデフォルト動作

- **GIVEN** ペルソナ設定で `character_image` が設定されていない
- **WHEN** 設定が読み込まれる
- **THEN** `character_image` は `None` である
- **AND** キャラクター表示はスキップされる（静的アバターのフォールバック）

#### Scenario: 画像パスが存在しない場合のエラー

- **GIVEN** `character_image: "nonexistent/file.png"` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** ValidationError が発生する
- **AND** エラーメッセージに不正なパスが含まれる

### Requirement: キャラクター表示位置の設定

システムは、ペルソナごとにキャラクターの表示位置（左/右/中央）を指定可能にしなければならない（SHALL）。

#### Scenario: 左側表示の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_position: "left"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_position` は `"left"` である
- **AND** キャラクターは画面左側に表示される

#### Scenario: 右側表示の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "metan"
      character_position: "right"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_position` は `"right"` である
- **AND** キャラクターは画面右側に表示される

#### Scenario: 中央表示の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "single_speaker"
      character_position: "center"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_position` は `"center"` である
- **AND** キャラクターは画面中央に表示される

#### Scenario: デフォルト位置（未設定時）

- **GIVEN** `character_position` が設定されていない
- **WHEN** 設定が読み込まれる
- **THEN** `character_position` のデフォルト値は `"left"` である

#### Scenario: 不正な位置設定のエラー

- **GIVEN** `character_position: "top"` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** ValidationError が発生する
- **AND** エラーメッセージに有効な値（"left", "right", "center"）が示される

### Requirement: アニメーションスタイルの設定（Phase 3）

システムは、ペルソナごとにアニメーションスタイル（バウンス/揺れ/静止）を指定可能にしなければならない（SHALL）。

#### Scenario: バウンスアニメーションの設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      animation_style: "bounce"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `animation_style` は `"bounce"` である
- **AND** 話している間、キャラクターが上下にバウンスする

#### Scenario: 揺れアニメーションの設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "metan"
      animation_style: "sway"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `animation_style` は `"sway"` である
- **AND** キャラクターが微妙に左右に揺れる

#### Scenario: 静止スタイルの設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "static_char"
      animation_style: "static"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `animation_style` は `"static"` である
- **AND** キャラクターは揺れやバウンスなしで表示される（リップシンク・まばたきのみ）

#### Scenario: デフォルトアニメーション（未設定時）

- **GIVEN** `animation_style` が設定されていない
- **WHEN** 設定が読み込まれる
- **THEN** `animation_style` のデフォルト値は `"sway"` である

#### Scenario: 不正なアニメーションスタイルのエラー

- **GIVEN** `animation_style: "rotate"` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** ValidationError が発生する
- **AND** エラーメッセージに有効な値（"bounce", "sway", "static"）が示される

### Requirement: マルチスピーカー設定でのキャラクター配置自動調整

システムは、複数ペルソナが設定されている場合、デフォルトの `character_position` を自動調整しなければならない（SHALL）。

#### Scenario: 2人話者のデフォルト配置

- **GIVEN** 設定ファイルに2つのペルソナがあり、`character_position` が未設定である:
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
    - id: "metan"
      name: "四国めたん"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** 1番目のペルソナの `character_position` は `"left"` である
- **AND** 2番目のペルソナの `character_position` は `"right"` である

#### Scenario: 3人以上の話者の配置

- **GIVEN** 設定ファイルに3つのペルソナがある
- **WHEN** 設定が読み込まれる
- **THEN** すべてのペルソナの `character_position` はデフォルト `"left"` である
- **AND** 話者切り替え時に入れ替わりアニメーションが適用される

#### Scenario: 手動設定が優先される

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_position: "right"
    - id: "metan"
      character_position: "left"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** 手動設定が自動調整より優先される
- **AND** ずんだもんは右側、めたんは左側に表示される

### Requirement: Background Configuration

The system SHALL allow specifying video background settings in the configuration file.

#### Scenario: Configure Image Background

- **GIVEN** the configuration file includes:
  ```yaml
  video:
    background:
      type: "image"
      path: "assets/backgrounds/default.png"
      fit: "cover"
  ```
- **WHEN** the configuration is loaded
- **THEN** `VideoConfig.background` is set to a `BackgroundConfig` object
- **AND** `background.type` is `"image"`
- **AND** `background.path` is `"assets/backgrounds/default.png"`
- **AND** `background.fit` is `"cover"`

#### Scenario: Configure Video Background

- **GIVEN** the configuration file includes:
  ```yaml
  video:
    background:
      type: "video"
      path: "assets/backgrounds/loop.mp4"
      fit: "contain"
  ```
- **WHEN** the configuration is loaded
- **THEN** `VideoConfig.background` is set to a `BackgroundConfig` object
- **AND** `background.type` is `"video"`
- **AND** `background.path` is `"assets/backgrounds/loop.mp4"`

#### Scenario: Default When Background is Not Set

- **GIVEN** the configuration file does not include `video.background`
- **WHEN** the configuration is loaded
- **THEN** `VideoConfig.background` is `None`
- **AND** the video is generated with a black background (current behavior maintained)

#### Scenario: Validate Background Type

- **GIVEN** the configuration file includes `video.background.type: "audio"` (invalid value)
- **WHEN** configuration validation is executed
- **THEN** a `ValidationError` is raised
- **AND** the error message indicates valid values ("image", "video")

#### Scenario: Validate Background Fit Mode

- **GIVEN** the configuration file includes `video.background.fit: "stretch"` (invalid value)
- **WHEN** configuration validation is executed
- **THEN** a `ValidationError` is raised
- **AND** the error message indicates valid values ("cover", "contain", "fill")

#### Scenario: Default Background Fit Mode

- **GIVEN** the configuration file does not include `video.background.fit`
- **WHEN** the configuration is loaded
- **THEN** `background.fit` defaults to `"cover"`

### Requirement: BGM Configuration

The system SHALL allow specifying video BGM (background music) settings in the configuration file.

#### Scenario: Basic BGM Configuration

- **GIVEN** the configuration file includes:
  ```yaml
  video:
    bgm:
      path: "assets/bgm/background_music.mp3"
      volume: 0.3
  ```
- **WHEN** the configuration is loaded
- **THEN** `VideoConfig.bgm` is set to a `BgmConfig` object
- **AND** `bgm.path` is `"assets/bgm/background_music.mp3"`
- **AND** `bgm.volume` is `0.3`

#### Scenario: BGM Fade Configuration

- **GIVEN** the configuration file includes:
  ```yaml
  video:
    bgm:
      path: "assets/bgm/music.mp3"
      fade_in_seconds: 3.0
      fade_out_seconds: 5.0
  ```
- **WHEN** the configuration is loaded
- **THEN** `bgm.fade_in_seconds` is `3.0`
- **AND** `bgm.fade_out_seconds` is `5.0`

#### Scenario: BGM Loop Configuration

- **GIVEN** the configuration file includes:
  ```yaml
  video:
    bgm:
      path: "assets/bgm/short_loop.mp3"
      loop: true
  ```
- **WHEN** the configuration is loaded
- **THEN** `bgm.loop` is `true`

#### Scenario: Default BGM Loop

- **GIVEN** the configuration file does not include `video.bgm.loop`
- **WHEN** the configuration is loaded
- **THEN** `bgm.loop` defaults to `true`

#### Scenario: Default When BGM is Not Set

- **GIVEN** the configuration file does not include `video.bgm`
- **WHEN** the configuration is loaded
- **THEN** `VideoConfig.bgm` is `None`
- **AND** the video is generated without BGM

#### Scenario: Validate BGM Volume

- **GIVEN** the configuration file includes `video.bgm.volume: 1.5` (out of range)
- **WHEN** configuration validation is executed
- **THEN** a `ValidationError` is raised
- **AND** the error message indicates the valid range (0.0-1.0)

#### Scenario: Default BGM Volume

- **GIVEN** the configuration file does not include `video.bgm.volume`
- **WHEN** the configuration is loaded
- **THEN** `bgm.volume` defaults to `0.3`

#### Scenario: Default BGM Fade

- **GIVEN** the configuration file does not include `video.bgm.fade_in_seconds` and `fade_out_seconds`
- **WHEN** the configuration is loaded
- **THEN** `bgm.fade_in_seconds` defaults to `2.0`
- **AND** `bgm.fade_out_seconds` defaults to `2.0`

### Requirement: Supported File Formats

The system SHALL support specific file formats for background and BGM.

#### Scenario: Support Background Image Formats

- **GIVEN** the background path has one of `.png`, `.jpg`, `.jpeg` extensions
- **WHEN** the configuration is loaded
- **THEN** the file format is accepted as valid

#### Scenario: Support Background Video Formats

- **GIVEN** the background path has one of `.mp4`, `.webm` extensions
- **WHEN** the configuration is loaded
- **THEN** the file format is accepted as valid

#### Scenario: Support BGM Audio Formats

- **GIVEN** the BGM path has one of `.mp3`, `.wav`, `.m4a` extensions
- **WHEN** the configuration is loaded
- **THEN** the file format is accepted as valid

### Requirement: Unified Slide Generation Retry Configuration

The system SHALL retrieve slide generation retry count, delay, and backoff factor from common constants (SHALL).

#### Scenario: Refer to Retry Constants

- **WHEN** performing retry processing in slide generation
- **THEN** reference constants from `RetryConfig`

### Requirement: スライド生成リトライ設定の統一
システムは、スライド生成のリトライ回数・遅延・バックオフ係数を共通定数から取得しなければならない（SHALL）。

#### Scenario: リトライ定数の参照
- **WHEN** スライド生成でリトライ処理を行う
- **THEN** `RetryConfig` の定数を参照する

### Requirement: LLMモデルの明示指定
システムは、LLM呼び出し時にモデルIDを設定ファイルから明示的に指定しなければならない（SHALL）。

#### Scenario: モデル指定の強制
- **GIVEN** 設定ファイルに `content.llm.model` と `slides.llm.model` が定義されている
- **WHEN** LLM呼び出しが実行される
- **THEN** 関数デフォルトに依存せず、設定値が渡される
