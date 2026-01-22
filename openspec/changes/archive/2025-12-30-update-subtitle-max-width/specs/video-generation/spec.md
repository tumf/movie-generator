## MODIFIED Requirements

### Requirement: Subtitle Display Area

The system SHALL render subtitles with a fixed width of 80% of the video width to maximize text display area before wrapping.

#### Scenario: Fixed Subtitle Width

- **WHEN** a subtitle is displayed
- **THEN** the subtitle container has a fixed width of 80% of the video width (not maxWidth)
- **AND** the subtitle is horizontally centered on the screen
- **AND** text utilizes the full 80% width before wrapping

#### Scenario: Long Subtitle Text Wrapping

- **WHEN** subtitle text exceeds the 80% width container
- **THEN** the text wraps to multiple lines within the container
- **AND** maintains a line-height of 1.4 for readability

**Technical Note:**
- Previously used `maxWidth: '80%'` which caused container to shrink based on text length
- Changed to `width: '80%'` to ensure container always uses full 80% width
- This prevents premature text wrapping on shorter text
