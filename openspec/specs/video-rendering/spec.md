# Video Rendering Specification

## Purpose

This specification defines the video rendering system for the movie generator application. The system manages composition data generation and Remotion-based video rendering with support for per-persona subtitle styling. This enables multi-speaker videos with distinct visual styling for each character's dialogue.

## Requirements

### Requirement: Add Speaker Information to composition.json

The generated composition.json SHALL include speaker information for each phrase.

#### Scenario: composition.json with Speaker Information
- **GIVEN** a phrase list:
  ```python
  [
    Phrase(text="やっほー！", persona_id="zundamon", persona_name="ずんだもん"),
    Phrase(text="こんにちは", persona_id="metan", persona_name="四国めたん")
  ]
  ```
- **AND** persona configuration:
  ```yaml
  personas:
    - id: "zundamon"
      subtitle_color: "#8FCF4F"
    - id: "metan"
      subtitle_color: "#FF69B4"
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** composition.json includes:
  ```json
  {
    "phrases": [
      {
        "text": "やっほー！",
        "personaId": "zundamon",
        "personaName": "ずんだもん",
        "subtitleColor": "#8FCF4F",
        ...
      },
      {
        "text": "こんにちは",
        "personaId": "metan",
        "personaName": "四国めたん",
        "subtitleColor": "#FF69B4",
        ...
      }
    ]
  }
  ```

#### Scenario: composition.json for Single Speaker
- **GIVEN** all phrases have the same persona
- **WHEN** `update_composition_json()` is called
- **THEN** all phrases have the same `personaId` and `subtitleColor`
- **AND** the video appears identical to traditional single-speaker videos

### Requirement: Render Per-Persona Subtitle Styles

Remotion SHALL apply different subtitle styles for each speaker.

#### Scenario: Apply Subtitle Color
- **GIVEN** a phrase's `subtitleColor` is `"#8FCF4F"`
- **WHEN** the subtitle is rendered
- **THEN** the subtitle border color is `#8FCF4F` (green)

#### Scenario: Switch Subtitle Colors for Multiple Speakers
- **GIVEN** phrase 0's `subtitleColor` is `"#8FCF4F"`
- **AND** phrase 1's `subtitleColor` is `"#FF69B4"`
- **WHEN** the video is rendered
- **THEN** phrase 0's subtitle is displayed in green
- **AND** phrase 1's subtitle is displayed in pink

### Requirement: Prepare Persona Name Display (Future Use)

The composition.json SHALL include personaName, but it is not displayed in the current version.

#### Scenario: Persona Name Field Exists
- **GIVEN** composition.json includes `personaName`
- **WHEN** it is loaded by Remotion
- **THEN** the field exists but is not displayed on screen
- **AND** display functionality can be added in future versions

### Requirement: Reserve Avatar Image Field (Future Use)

The composition.json SHALL reserve an avatarImage field, but it is not used in the current version.

#### Scenario: Reserve Avatar Image Field
- **GIVEN** a persona has `avatar_image` configured
- **WHEN** composition.json is generated
- **THEN** the `avatarImage` field is not included (or is `null`)
- **AND** it can be implemented in future versions

### Requirement: Maintain Backward Compatibility

The system SHALL work with composition.json files that lack speaker information.

#### Scenario: composition.json Without Speaker Information
- **GIVEN** composition.json does not include `personaId` or `subtitleColor`
- **WHEN** it is loaded by Remotion
- **THEN** subtitles are displayed in the default color (#FFFFFF)
- **AND** no error occurs

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/video-rendering/spec.md`.
