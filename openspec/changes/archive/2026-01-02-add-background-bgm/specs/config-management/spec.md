## ADDED Requirements

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
