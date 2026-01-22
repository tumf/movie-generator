## ADDED Requirements

### Requirement: Include Background Information in composition.json

The generated composition.json SHALL include background configuration information.

#### Scenario: Output Global Background Configuration to composition.json

- **GIVEN** the configuration file has the following background settings:
  ```yaml
  video:
    background:
      type: "image"
      path: "assets/backgrounds/default.png"
      fit: "cover"
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** composition.json includes:
  ```json
  {
    "background": {
      "type": "image",
      "path": "backgrounds/default.png",
      "fit": "cover"
    }
  }
  ```

#### Scenario: Output Video Background to composition.json

- **GIVEN** background type is `"video"`
- **WHEN** `update_composition_json()` is called
- **THEN** `background.type` in composition.json is `"video"`
- **AND** Remotion displays the background using the `<Video>` component

#### Scenario: composition.json When Background is Not Set

- **GIVEN** the configuration file has no background settings
- **WHEN** `update_composition_json()` is called
- **THEN** `background` in composition.json is `null`
- **AND** the video is generated with a black background

### Requirement: Include Section Background Override in composition.json

composition.json SHALL include section-specific background override information.

#### Scenario: Output Section Background Override

- **GIVEN** the script YAML has the following sections:
  ```yaml
  sections:
    - title: "Intro"
      background:
        type: "image"
        path: "assets/backgrounds/intro.png"
      narrations:
        - text: "Hello"
    - title: "Main"
      narrations:
        - text: "This is the main content"
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** phrases in composition.json include:
  ```json
  {
    "phrases": [
      {
        "text": "Hello",
        "sectionIndex": 0,
        "backgroundOverride": {
          "type": "image",
          "path": "backgrounds/intro.png",
          "fit": "cover"
        }
      },
      {
        "text": "This is the main content",
        "sectionIndex": 1,
        "backgroundOverride": null
      }
    ]
  }
  ```

#### Scenario: Section Background Overrides Global Settings

- **GIVEN** global background is set to `"backgrounds/default.png"`
- **AND** section 1 background is set to `"backgrounds/intro.png"`
- **WHEN** the video is rendered
- **THEN** `"backgrounds/intro.png"` is displayed as the background during section 1 phrases
- **AND** `"backgrounds/default.png"` is displayed from section 2 onward

### Requirement: Include BGM Information in composition.json

The generated composition.json SHALL include BGM configuration information.

#### Scenario: Output BGM Configuration to composition.json

- **GIVEN** the configuration file has the following BGM settings:
  ```yaml
  video:
    bgm:
      path: "assets/bgm/music.mp3"
      volume: 0.3
      fade_in_seconds: 2.0
      fade_out_seconds: 3.0
      loop: true
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** composition.json includes:
  ```json
  {
    "bgm": {
      "path": "bgm/music.mp3",
      "volume": 0.3,
      "fadeInSeconds": 2.0,
      "fadeOutSeconds": 3.0,
      "loop": true
    }
  }
  ```

#### Scenario: composition.json When BGM is Not Set

- **GIVEN** the configuration file has no BGM settings
- **WHEN** `update_composition_json()` is called
- **THEN** `bgm` in composition.json is `null`
- **AND** the video is generated without BGM

### Requirement: Display Background with BackgroundLayer Component

Remotion's BackgroundLayer component SHALL display background images or videos in fullscreen.

#### Scenario: Display Image Background

- **GIVEN** composition.json includes:
  ```json
  {
    "background": {
      "type": "image",
      "path": "backgrounds/default.png",
      "fit": "cover"
    }
  }
  ```
- **WHEN** BackgroundLayer is rendered
- **THEN** the background image is displayed using the `<Img>` component
- **AND** `objectFit: "cover"` is applied
- **AND** the image covers the entire screen

#### Scenario: Display Video Background

- **GIVEN** composition.json includes:
  ```json
  {
    "background": {
      "type": "video",
      "path": "backgrounds/loop.mp4",
      "fit": "cover"
    }
  }
  ```
- **WHEN** BackgroundLayer is rendered
- **THEN** the background video is displayed using the `<Video>` component
- **AND** `loop={true}` is set
- **AND** `muted={true}` is set (audio is muted)

#### Scenario: Loop Background Video

- **GIVEN** the background video is 10 seconds long and the total video is 60 seconds
- **WHEN** the video is rendered
- **THEN** the background video loops 6 times
- **AND** it is displayed seamlessly until the end

#### Scenario: Apply Fit Mode "contain"

- **GIVEN** `background.fit` is `"contain"`
- **WHEN** BackgroundLayer is rendered
- **THEN** the background image/video is displayed with `objectFit: "contain"`
- **AND** aspect ratio is maintained, and margins are filled with black

#### Scenario: Apply Fit Mode "fill"

- **GIVEN** `background.fit` is `"fill"`
- **WHEN** BackgroundLayer is rendered
- **THEN** the background image/video is displayed with `objectFit: "fill"`
- **AND** it is stretched to fill the entire screen, ignoring aspect ratio

#### Scenario: Behavior When Background is Not Set

- **GIVEN** `background` in composition.json is `null`
- **WHEN** BackgroundLayer is rendered
- **THEN** nothing is displayed (black background is default)
- **AND** no error occurs

#### Scenario: Layer Order (z-index)

- **GIVEN** background, slide, character, and subtitle exist
- **WHEN** the video is rendered
- **THEN** the layer order is as follows:
  1. BackgroundLayer (bottommost)
  2. SlideLayer
  3. CharacterLayer
  4. SubtitleLayer (topmost)

### Requirement: Switch Section Background

BackgroundLayer SHALL switch the background to the override setting when the section changes.

#### Scenario: Switch Background at Section Start

- **GIVEN** section 0's backgroundOverride is `null` (uses global background)
- **AND** section 1's backgroundOverride is `"backgrounds/intro.png"`
- **WHEN** the first phrase of section 1 is displayed
- **THEN** the background switches to `"backgrounds/intro.png"`
- **AND** the switch is immediate (no fade)

#### Scenario: Return to Global Background at Section End

- **GIVEN** section 1's backgroundOverride is set
- **AND** section 2's backgroundOverride is `null`
- **WHEN** the first phrase of section 2 is displayed
- **THEN** the background returns to global settings

### Requirement: Play BGM with BgmAudio Component

Remotion's BgmAudio component SHALL play BGM simultaneously with narration audio.

#### Scenario: Basic BGM Playback

- **GIVEN** composition.json includes:
  ```json
  {
    "bgm": {
      "path": "bgm/music.mp3",
      "volume": 0.3,
      "loop": true
    }
  }
  ```
- **WHEN** BgmAudio is rendered
- **THEN** BGM is played using the `<Audio>` component
- **AND** volume is set to `0.3`

#### Scenario: Loop BGM Playback

- **GIVEN** `bgm.loop` is `true`
- **AND** BGM is 30 seconds long and the total video is 120 seconds
- **WHEN** the video is rendered
- **THEN** BGM loops 4 times

#### Scenario: BGM Fade In

- **GIVEN** `bgm.fadeInSeconds` is `3.0`
- **AND** FPS is 30
- **WHEN** the first 90 frames of the video are played
- **THEN** BGM volume increases linearly from 0 to the set value (0.3)
- **AND** it remains constant at the set value from frame 90 onward

#### Scenario: BGM Fade Out

- **GIVEN** `bgm.fadeOutSeconds` is `5.0`
- **AND** the total video is 300 frames (10 seconds)
- **WHEN** the last 150 frames of the video are played
- **THEN** BGM volume decreases linearly from the set value to 0
- **AND** volume is 0 at frame 300

#### Scenario: Simultaneous Playback of BGM and Narration

- **GIVEN** BGM is configured
- **AND** narration audio exists
- **WHEN** the video is rendered
- **THEN** BGM and narration are played simultaneously
- **AND** volumes are set independently

#### Scenario: Behavior When BGM is Not Set

- **GIVEN** `bgm` in composition.json is `null`
- **WHEN** BgmAudio component is rendered
- **THEN** nothing is played
- **AND** no error occurs

### Requirement: Placement of Background/BGM Assets

The system SHALL place background and BGM assets in paths accessible to Remotion.

#### Scenario: Convert Background Image Path

- **GIVEN** the configuration specifies `video.background.path: "assets/backgrounds/bg.png"`
- **WHEN** composition.json is generated
- **THEN** the path is converted to `"backgrounds/bg.png"` (relative to `public/`)
- **AND** the file is copied or symlinked to `public/backgrounds/bg.png`

#### Scenario: Convert BGM File Path

- **GIVEN** the configuration specifies `video.bgm.path: "assets/bgm/music.mp3"`
- **WHEN** composition.json is generated
- **THEN** the path is converted to `"bgm/music.mp3"`
- **AND** the file is copied or symlinked to `public/bgm/music.mp3`

#### Scenario: When Asset File Does Not Exist

- **GIVEN** the specified asset file does not exist
- **WHEN** video generation is executed
- **THEN** a warning message is logged
- **AND** the missing asset is skipped (continues without background/BGM)

### Requirement: Background and BGM Backward Compatibility

The system SHALL work with composition.json files that lack background and BGM information.

#### Scenario: composition.json Without Background or BGM

- **GIVEN** composition.json does not include `background` and `bgm` fields
- **WHEN** Remotion components are rendered
- **THEN** the video is generated with a black background
- **AND** no BGM is played
- **AND** no error occurs
