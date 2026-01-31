## MODIFIED Requirements
### Requirement: Maintain Backward Compatibility

The system SHALL work with composition.json files that lack speaker information.

The implementation SHALL centralize defaulting and schema mapping in a dedicated composition builder to reduce duplication.

#### Scenario: composition.json Without Speaker Information
- **GIVEN** composition.json does not include `personaId` or `subtitleColor`
- **WHEN** it is loaded by Remotion
- **THEN** subtitles are displayed in the default color (#FFFFFF)
- **AND** no error occurs

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/video-rendering/spec.md`.
