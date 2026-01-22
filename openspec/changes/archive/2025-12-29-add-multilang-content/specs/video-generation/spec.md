# Video Generation - Multi-Language Support

## MODIFIED Requirements

### Requirement: Script Generation

The system SHALL generate YouTube video scripts from extracted content in multiple languages based on configuration.

#### Scenario: Successful Script Generation
- **WHEN** blog content is provided
- **AND** `content.languages` is configured with one or more language codes
- **THEN** a structured script for YouTube is generated for each configured language
- **AND** it includes opening, main content, and ending sections
- **AND** narration text is written in the appropriate language

#### Scenario: Multi-Language Script Generation
- **WHEN** `content.languages: ["ja", "en"]` is configured
- **THEN** two separate scripts are generated
- **AND** Japanese script uses Japanese prompt template with pronunciation support
- **AND** English script uses English prompt template without pronunciation support
- **AND** both scripts include slide prompts in English

#### Scenario: Language-Specific Prompt Selection
- **WHEN** script generation is requested for a specific language
- **THEN** the appropriate prompt template for that language is used
- **AND** the generated narration matches the language's natural speech patterns

#### Scenario: LLM Error Fallback
- **WHEN** LLM API returns an error
- **THEN** retry is attempted or an appropriate error message is displayed
- **AND** failure for one language does not prevent generation of other languages

### Requirement: Slide Generation with NonobananaPro

The system SHALL generate slide images for each section and language using NonobananaPro via OpenRouter.

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

## ADDED Requirements

### Requirement: Multi-Language Content Integration

The system SHALL provide a unified interface for generating scripts and slides for multiple languages.

#### Scenario: Batch Multi-Language Generation
- **WHEN** `generate_multilang_content()` is called with a config containing multiple languages
- **THEN** scripts are generated for all configured languages
- **AND** slides are generated for all configured languages
- **AND** language-specific output files are created
- **AND** a dictionary mapping language codes to VideoScript objects is returned

#### Scenario: Language-Specific Script Files
- **WHEN** multi-language generation is complete
- **THEN** each language has a separate script file: `script_{lang}.yaml`
- **AND** each script file contains language-appropriate narration
- **AND** Japanese scripts include pronunciation dictionary entries
- **AND** English scripts have empty pronunciation arrays

#### Scenario: Backward Compatibility Mode
- **WHEN** only one language is configured OR languages field is omitted
- **THEN** single script file `script.yaml` is created (legacy format)
- **AND** slides are saved directly in `slides/` without language subdirectory
- **AND** existing tools and scripts continue to work without modification

### Requirement: Language-Specific Script Detection

The system SHALL automatically detect and process language-specific script files.

#### Scenario: Detect Language-Specific Scripts
- **WHEN** the slide generation script runs
- **THEN** it searches for `script_*.yaml` files (e.g., `script_ja.yaml`, `script_en.yaml`)
- **AND** processes each detected language sequentially
- **AND** reports progress and results per language

#### Scenario: Legacy Script Fallback
- **WHEN** no `script_*.yaml` files are found
- **THEN** the system looks for legacy `script.yaml` file
- **AND** treats it as Japanese content
- **AND** generates slides in the legacy location

#### Scenario: Mixed Legacy and Multi-Language
- **WHEN** both `script.yaml` and `script_*.yaml` files exist
- **THEN** `script_*.yaml` files take precedence
- **AND** legacy `script.yaml` is ignored
