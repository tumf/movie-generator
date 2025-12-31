# Script Generation Specification

## Purpose

This specification defines the script generation system for the movie generator application. The system generates narration scripts using LLM prompts, supporting both single-speaker narration and multi-persona dialogue formats. The generated scripts include speaker assignments, enabling multi-character conversational videos.

## Requirements

### Requirement: Dialogue Format Prompt

The system SHALL be able to generate dialogue-style scripts with multiple personas.

#### Scenario: Generate Dialogue Script
- **GIVEN** persona configuration:
  ```yaml
  personas:
    - id: "zundamon"
      character: "元気で明るい東北の妖精"
    - id: "metan"
      character: "優しくて落ち着いた四国の妖精"
  ```
- **AND** `narration.mode: "dialogue"` is configured
- **WHEN** `generate_script()` is called
- **THEN** a dialogue format prompt is sent to the LLM
- **AND** each persona's `character` configuration is included

#### Scenario: Parse Dialogue Format Response
- **GIVEN** the LLM returns the following response:
  ```json
  {
    "sections": [
      {
        "title": "イントロ",
        "dialogues": [
          {
            "persona_id": "zundamon",
            "narration": "やっほー！"
          },
          {
            "persona_id": "metan",
            "narration": "こんにちは！"
          }
        ],
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **WHEN** the response is parsed
- **THEN** 2 phrases are generated
- **AND** phrase 0 has `persona_id="zundamon"`
- **AND** phrase 1 has `persona_id="metan"`

### Requirement: Single-Speaker Mode Support

The system SHALL continue to support the traditional single-speaker mode.

#### Scenario: Generate Single-Speaker Script
- **GIVEN** `narration.mode: "single"` is configured
- **AND** only one persona is defined
- **WHEN** `generate_script()` is called
- **THEN** the traditional single-speaker prompt is used
- **AND** all phrases are assigned to the same persona

#### Scenario: Parse Single-Speaker Response
- **GIVEN** the LLM returns a traditional format response:
  ```json
  {
    "sections": [
      {
        "title": "イントロ",
        "narration": "やっほー！ずんだもんなのだ。",
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **WHEN** the response is parsed
- **THEN** phrase splitting is executed
- **AND** all phrases are assigned to `personas[0].id`

### Requirement: Automatic Persona Role Assignment

The dialogue format prompt SHALL assign appropriate roles to personas.

#### Scenario: Two-Persona Roles
- **GIVEN** two personas are defined
- **WHEN** a dialogue format prompt is generated
- **THEN** persona 0 is designated as the "explainer" role
- **AND** persona 1 is designated as the "questioner/responder" role

#### Scenario: Three or More Persona Roles
- **GIVEN** three or more personas are defined
- **WHEN** a dialogue format prompt is generated
- **THEN** roles are assigned based on each persona's character traits
- **AND** the LLM is instructed to generate natural conversation

### Requirement: Add Speaker Information to Phrases

Generated phrases SHALL include speaker information.

#### Scenario: Add Speaker Information to Phrase Objects
- **GIVEN** a dialogue format response is parsed
- **WHEN** `Phrase` objects are created
- **THEN** the `persona_id` field is set
- **AND** the `persona_name` field is set

#### Scenario: Unknown Persona ID Error
- **GIVEN** the LLM response includes `persona_id="unknown"`
- **AND** no persona with ID `"unknown"` is defined
- **WHEN** the response is parsed
- **THEN** an error is raised
- **AND** the error message includes the unknown persona ID

### Requirement: Language-Specific Dialogue Prompts

The system SHALL provide dialogue format prompts for Japanese and English.

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

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/script-generation/spec.md`.
