## MODIFIED Requirements
### Requirement: Language-Specific Dialogue Prompts

The system SHALL provide dialogue format prompts for Japanese and English.

Prompt templates SHALL be managed in a way that makes updating all language variants reliable (e.g., shared building blocks and tests).

#### Scenario: Japanese Dialogue Prompt
- **GIVEN** `language="ja"` is configured
- **AND** `narration.mode="dialogue"` is configured
- **WHEN** a prompt is generated
- **THEN** `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` is used

#### Scenario: English Dialogue Prompt
- **GIVEN** `language="en"` is configured
- **AND** `narration.mode="dialogue"` is configured
- **WHEN** a prompt is generated
- **THEN** `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` is used

#### Scenario: Prompt variants stay in sync
- **WHEN** a developer updates prompt output fields
- **THEN** all dialogue prompt variants are updated consistently
- **AND** tests fail if any variant misses required instructions/examples
