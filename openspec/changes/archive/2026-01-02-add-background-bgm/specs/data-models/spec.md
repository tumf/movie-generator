## ADDED Requirements

### Requirement: Section Background Field

The `Section` model SHALL have a section-level background override setting.

#### Scenario: Section Has Background Configuration

- **GIVEN** the script YAML has the following section:
  ```yaml
  sections:
    - title: "Intro"
      background:
        type: "image"
        path: "assets/backgrounds/intro.png"
        fit: "cover"
      narrations:
        - text: "Hello"
  ```
- **WHEN** the script is parsed
- **THEN** `Section.background` is set to a `BackgroundConfig` object
- **AND** `section.background.type` is `"image"`
- **AND** `section.background.path` is `"assets/backgrounds/intro.png"`

#### Scenario: Section Has No Background Configuration

- **GIVEN** the script YAML section does not have a `background` field
- **WHEN** the script is parsed
- **THEN** `Section.background` is `None`
- **AND** global background settings (or black background) are used

#### Scenario: Section Override with Video Background

- **GIVEN** the script YAML has the following section:
  ```yaml
  sections:
    - title: "Demo"
      background:
        type: "video"
        path: "assets/backgrounds/demo.mp4"
      narrations:
        - text: "Watch the demo"
  ```
- **WHEN** the script is parsed
- **THEN** `Section.background.type` is `"video"`

### Requirement: BackgroundConfig Data Model

The `BackgroundConfig` model SHALL represent background settings.

#### Scenario: BackgroundConfig Required Fields

- **GIVEN** background configuration data:
  ```python
  {
      "type": "image",
      "path": "assets/backgrounds/bg.png"
  }
  ```
- **WHEN** a `BackgroundConfig` object is created
- **THEN** `config.type` is `"image"`
- **AND** `config.path` is `"assets/backgrounds/bg.png"`
- **AND** `config.fit` defaults to `"cover"`

#### Scenario: BackgroundConfig Fit Mode

- **GIVEN** background configuration data with fit specified:
  ```python
  {
      "type": "image",
      "path": "assets/backgrounds/bg.png",
      "fit": "contain"
  }
  ```
- **WHEN** a `BackgroundConfig` object is created
- **THEN** `config.fit` is `"contain"`

#### Scenario: BackgroundConfig Type Validation

- **GIVEN** an invalid type is specified:
  ```python
  {
      "type": "audio",
      "path": "assets/music.mp3"
  }
  ```
- **WHEN** creation of a `BackgroundConfig` object is attempted
- **THEN** a `ValidationError` is raised

### Requirement: BgmConfig Data Model

The `BgmConfig` model SHALL represent BGM settings.

#### Scenario: BgmConfig Required Fields

- **GIVEN** BGM configuration data:
  ```python
  {
      "path": "assets/bgm/music.mp3"
  }
  ```
- **WHEN** a `BgmConfig` object is created
- **THEN** `config.path` is `"assets/bgm/music.mp3"`
- **AND** `config.volume` defaults to `0.3`
- **AND** `config.fade_in_seconds` defaults to `2.0`
- **AND** `config.fade_out_seconds` defaults to `2.0`
- **AND** `config.loop` defaults to `True`

#### Scenario: BgmConfig All Fields Set

- **GIVEN** BGM configuration data with all fields specified:
  ```python
  {
      "path": "assets/bgm/music.mp3",
      "volume": 0.5,
      "fade_in_seconds": 3.0,
      "fade_out_seconds": 5.0,
      "loop": False
  }
  ```
- **WHEN** a `BgmConfig` object is created
- **THEN** all fields are set to the specified values

#### Scenario: BgmConfig Volume Validation

- **GIVEN** volume is out of range:
  ```python
  {
      "path": "assets/bgm/music.mp3",
      "volume": 2.0
  }
  ```
- **WHEN** creation of a `BgmConfig` object is attempted
- **THEN** a `ValidationError` is raised
- **AND** the error message indicates the valid range (0.0-1.0)

#### Scenario: BgmConfig Fade Duration Validation

- **GIVEN** fade duration is negative:
  ```python
  {
      "path": "assets/bgm/music.mp3",
      "fade_in_seconds": -1.0
  }
  ```
- **WHEN** creation of a `BgmConfig` object is attempted
- **THEN** a `ValidationError` is raised

### Requirement: Phrase Background Override Field

The `Phrase` model SHALL hold the background override information of the section it belongs to.

#### Scenario: Phrase Has Background Override

- **GIVEN** a section has a background override configured
- **WHEN** a phrase is generated from that section
- **THEN** `Phrase.background_override` is set to a `BackgroundConfig` object

#### Scenario: Phrase Has No Background Override

- **GIVEN** a section has no background override configured
- **WHEN** a phrase is generated from that section
- **THEN** `Phrase.background_override` is `None`
