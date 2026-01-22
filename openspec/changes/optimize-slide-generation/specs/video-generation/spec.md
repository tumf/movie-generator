## MODIFIED Requirements

### Requirement: Slide Generation with NonobananaPro

The system SHALL generate slide images for each section and language using NonobananaPro via OpenRouter, with configurable concurrency and improved retry handling.

#### Scenario: Successful AI Image Generation

- **WHEN** slide generation is requested
- **THEN** NonobananaPro is called via OpenRouter API
- **AND** a 1920x1080 PNG image is generated
- **AND** visual representation aligns with script content
- **AND** slides are saved in language-specific subdirectories

#### Scenario: Multi-Language Slide Generation

- **WHEN** slides are generated for multiple languages
- **THEN** each language's slides are saved in `slides/{lang}/` subdirectory
- **AND** slide filenames remain consistent: `slide_0000.png`, `slide_0001.png`, etc.
- **AND** slide prompts are written in English (for image generation API compatibility)
- **AND** text to display on slides is specified in the target language within the prompt
  - Example (Japanese): "A slide with text 'データベース設計' in the center, modern design"
  - Example (English): "A slide with text 'Database Design' in the center, modern design"

#### Scenario: Style Consistency

- **WHEN** multiple slides are generated
- **THEN** style specified in YAML config (color tone, mood) is applied to all slides
- **AND** style is consistent across all languages

#### Scenario: API Error Fallback

- **WHEN** NonobananaPro API returns an error
- **THEN** retry is attempted
- **AND** if failure persists, a placeholder image is used
- **AND** failure for one language does not prevent generation of other languages

#### Scenario: Configurable Concurrent Requests

- **WHEN** `slides.max_concurrent` is configured
- **THEN** the system limits concurrent API requests to the specified value
- **AND** requests are processed in batches of `max_concurrent` size
- **AND** each batch completes before the next batch starts

#### Scenario: Rate Limit Handling

- **WHEN** the API returns HTTP 429 (Rate Limit Exceeded)
- **THEN** the system waits with exponential backoff
- **AND** the wait time doubles with each retry (initial: `retry_delay` seconds)
- **AND** retry continues up to `max_retries` times
- **AND** progress display shows rate limit status

#### Scenario: Batch Delay Between Requests

- **WHEN** a batch of concurrent requests completes
- **AND** more batches remain
- **THEN** the system waits 1 second before starting the next batch
- **AND** this prevents rate limiting from rapid sequential batches

## ADDED Requirements

### Requirement: Efficient Prompt Structure

The system SHALL use an efficient prompt structure to reduce token usage in slide generation.

#### Scenario: Shared Style Instructions

- **WHEN** multiple slides are generated in a session
- **THEN** common style instructions are included once as a system-level context
- **AND** each slide prompt contains only section-specific details
- **AND** total token usage is reduced compared to repeating full instructions

#### Scenario: Minimal Slide Prompt

- **WHEN** a slide prompt is generated
- **THEN** the prompt includes only:
  - Section title
  - Section-specific content description
  - Language-specific text to display (if any)
- **AND** common style directives (resolution, design style) are not repeated

#### Scenario: Prompt Template Efficiency

- **WHEN** the full prompt is constructed
- **THEN** the total prompt length is less than 500 characters per slide
- **AND** the prompt is human-readable for debugging purposes
