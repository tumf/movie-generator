## MODIFIED Requirements

### Requirement: Phrase-Based Audio Generation

The system SHALL generate audio in phrase units (3-6 seconds) with intelligent splitting that respects quotation marks and natural break points.

#### Scenario: Phrase Audio Generation
- **WHEN** script is split into phrases
- **THEN** an audio file (WAV) is generated for each phrase
- **AND** actual duration (seconds) of each phrase is recorded in metadata

#### Scenario: Proper Noun Pronunciation
- **WHEN** phrase contains a proper noun registered in pronunciation dictionary
- **THEN** audio is synthesized using the dictionary reading (hiragana)

#### Scenario: Quote-Aware Phrase Splitting
- **WHEN** narration text contains Japanese quotation marks (`「」`)
- **THEN** the splitting algorithm does NOT split inside quotation marks
- **AND** quotes remain balanced in each phrase
- **AND** very long quoted sections (>1.5x max_chars) are allowed to split at closing quote boundary

#### Scenario: Prioritized Split Points
- **WHEN** multiple split candidates exist
- **THEN** period (`。`) is prioritized over comma (`、`)
- **AND** comma (`、`) is prioritized over newline (`\n`)
- **AND** emergency splits at max_chars only occur outside quotation marks

#### Scenario: Punctuation-Only Phrase Filtering
- **WHEN** a phrase would contain only punctuation marks (`。、！？\n`)
- **THEN** that phrase is NOT added to the phrase list
- **AND** empty or whitespace-only phrases are also filtered out

## ADDED Requirements

### Requirement: Subtitle Display Text Separation

The system SHALL provide separate text representations for narration audio and subtitle display to optimize readability.

#### Scenario: Subtitle Text Without Trailing Punctuation
- **WHEN** `Phrase.get_subtitle_text()` is called
- **THEN** trailing Japanese punctuation (`。`, `、`) is removed from the text
- **AND** punctuation in the middle of the text is preserved
- **AND** the original `Phrase.text` remains unchanged for audio generation

#### Scenario: Empty Subtitle Text Handling
- **WHEN** a phrase consists only of trailing punctuation
- **THEN** `get_subtitle_text()` returns an empty string
- **AND** the subtitle is still rendered (or omitted based on rendering logic)

#### Scenario: Multiple Trailing Punctuation Removal
- **WHEN** text has consecutive trailing punctuation (e.g., `。、`)
- **THEN** all trailing punctuation marks are removed iteratively
- **AND** resulting text has no trailing punctuation

### Requirement: Subtitle Synchronization

The system SHALL use cleaned subtitle text in video composition while maintaining phrase timing accuracy.

#### Scenario: Remotion Subtitle Rendering
- **WHEN** Remotion composition is generated
- **THEN** subtitle text is obtained via `Phrase.get_subtitle_text()`
- **AND** subtitles are displayed without trailing punctuation
- **AND** audio narration uses the full `Phrase.text` with punctuation intact

#### Scenario: Subtitle-Audio Timing Consistency
- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy
- **AND** subtitle display uses cleaned text while audio includes all punctuation
