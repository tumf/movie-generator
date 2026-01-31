## MODIFIED Requirements
### Requirement: Single-Speaker Mode Support

The system SHALL continue to support the traditional single-speaker mode.

The implementation SHALL separate prompt building, LLM calling, and response parsing into testable units while preserving behavior.

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
