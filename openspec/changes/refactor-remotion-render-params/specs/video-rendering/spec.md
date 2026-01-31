## MODIFIED Requirements
### Requirement: Background and BGM Backward Compatibility

The system SHALL work with composition.json files that lack background and BGM information.

The implementation SHALL centralize rendering execution parameters and environment checks to avoid duplicated logic.

#### Scenario: composition.json Without Background or BGM

- **GIVEN** composition.json does not include `background` and `bgm` fields
- **WHEN** Remotion components are rendered
- **THEN** the video is generated with a black background
- **AND** no BGM is played
- **AND** no error occurs
