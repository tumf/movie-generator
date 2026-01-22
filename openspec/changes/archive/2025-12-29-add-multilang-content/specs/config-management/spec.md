# Configuration Management - Multi-Language Support

## ADDED Requirements

### Requirement: Multi-Language Content Configuration

The system SHALL support multiple output languages through the `content.languages` configuration field.

#### Scenario: Configure multiple languages
- **WHEN** `content.languages: ["ja", "en"]` is configured
- **THEN** the system generates scripts and slides for both Japanese and English
- **AND** language-specific files are created: `script_ja.yaml`, `script_en.yaml`
- **AND** language-specific slide directories are created: `slides/ja/`, `slides/en/`

#### Scenario: Default single language
- **WHEN** `content.languages` is not specified
- **THEN** the system defaults to `["ja"]` (Japanese only)
- **AND** maintains backward compatibility with existing behavior

#### Scenario: Single language specified
- **WHEN** `content.languages: ["en"]` is configured
- **THEN** the system generates English-only content
- **AND** creates `script_en.yaml` and `slides/en/` directory

#### Scenario: Invalid language code
- **WHEN** an unsupported language code is configured (e.g., `["fr"]`)
- **THEN** the system generates content using the default Japanese prompt template
- **OR** logs a warning about the unsupported language

### Requirement: Language-Specific Output Structure

The system SHALL organize generated content by language code.

#### Scenario: Language-specific script files
- **WHEN** multiple languages are configured
- **THEN** each language gets a separate script file named `script_{lang}.yaml`
- **AND** each file contains language-appropriate narration text

#### Scenario: Language-specific slide directories
- **WHEN** slides are generated for multiple languages
- **THEN** slides are saved in `{output_dir}/slides/{lang}/` subdirectories
- **AND** slide filenames remain consistent across languages: `slide_0000.png`, `slide_0001.png`, etc.

#### Scenario: Legacy single-language compatibility
- **WHEN** only one language is configured OR languages field is omitted
- **THEN** script is saved as `script.yaml` (without language suffix)
- **AND** slides are saved directly in `slides/` (without language subdirectory)

## MODIFIED Requirements

### Requirement: Default Configuration

The system SHALL provide default configuration and merge it with user configuration, including language settings.

#### Scenario: Apply Default Configuration
- **WHEN** user configuration specifies only some fields
- **THEN** unspecified fields use default values
- **AND** `content.languages` defaults to `["ja"]` if not specified

#### Scenario: Override Default Configuration
- **WHEN** user configuration specifies a field
- **THEN** the default value is overridden with the user value
- **AND** custom `content.languages` list replaces the default

### Requirement: Configuration File Format

The system SHALL generate configuration files with inline documentation, including language configuration.

#### Scenario: Comments for each section
- **WHEN** configuration is output
- **THEN** each top-level section includes a comment explaining its purpose
- **AND** `content.languages` includes a comment with examples: `["ja"]` or `["ja", "en"]`
- **AND** complex fields include inline comments with examples

#### Scenario: YAML format only
- **WHEN** configuration is output
- **THEN** the format is valid YAML
- **AND** the structure matches `config/default.yaml`
- **AND** the `languages` field is properly formatted as a YAML list
