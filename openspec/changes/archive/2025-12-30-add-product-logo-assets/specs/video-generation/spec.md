# Video Generation Specification - Delta

## ADDED Requirements

### Requirement: LLM-Driven Logo Asset Identification

The system SHALL allow the LLM to identify required product logos during script generation and output logo URLs in the script metadata.

#### Scenario: LLM Identifies Required Logos

- **WHEN** script generation LLM analyzes blog content
- **AND** detects mentions of products or services
- **THEN** the LLM outputs `logo_assets` field in the script YAML
- **AND** each logo entry contains `name` and `url` fields
- **EXAMPLE**:
  ```yaml
  logo_assets:
    - name: "ProductX"
      url: "https://example.com/logo.svg"
  ```

#### Scenario: No Logos Needed

- **WHEN** blog content does not mention specific products or services
- **THEN** `logo_assets` field is omitted or empty list
- **AND** slide generation proceeds normally without logos

#### Scenario: LLM Cannot Find Logo URL

- **WHEN** LLM identifies a product but cannot determine official logo URL
- **THEN** LLM omits that product from `logo_assets`
- **AND** slide generation proceeds without that logo

### Requirement: Product Logo Asset Download

The system SHALL download product logos from LLM-specified URLs and store them in the project assets directory.

#### Scenario: Successful Logo Download

- **WHEN** script contains `logo_assets` with valid URLs
- **THEN** each logo image is downloaded from the specified URL
- **AND** saved to `projects/<name>/assets/logos/<sanitized-name>.png`
- **AND** filename is sanitized from the `name` field (alphanumeric + hyphens only)

#### Scenario: SVG to PNG Conversion

- **WHEN** downloaded logo is in SVG format
- **THEN** the system automatically converts it to PNG using cairosvg
- **AND** the converted PNG is saved to `assets/logos/`
- **AND** the original SVG is discarded after successful conversion

#### Scenario: Logo Already Exists

- **WHEN** a logo with the same name already exists in `assets/logos/`
- **THEN** download is skipped
- **AND** existing file is reused

#### Scenario: Download Failure Handling

- **WHEN** logo download fails due to network error or invalid URL
- **THEN** a warning message is displayed
- **AND** slide generation continues without that logo
- **AND** retry is attempted up to 3 times with exponential backoff

#### Scenario: SVG Conversion Failure

- **WHEN** SVG to PNG conversion fails
- **THEN** an error message is logged
- **AND** the unconverted SVG is kept in `assets/logos/`
- **AND** a warning suggests using PNG URL instead

### Requirement: Logo Asset Integration in Slide Generation

The system SHALL include downloaded logo assets in the slide generation prompt to guide the LLM.

#### Scenario: Logo Information in Prompt

- **WHEN** logos are successfully downloaded
- **THEN** slide generation prompt includes textual description of available logos
- **AND** prompt instructs LLM to incorporate logos appropriately
- **EXAMPLE**: "The following product logos are available: ProductX, ServiceY. Include ProductX logo in the top-right corner of the slide."

#### Scenario: Multiple Logos Available

- **WHEN** multiple logos are configured
- **THEN** all logos are mentioned in the prompt
- **AND** LLM is instructed to use appropriate logo based on slide content

#### Scenario: No Logos Configured

- **WHEN** `product_logos` field is omitted or empty
- **THEN** slide generation proceeds as normal without logo references
- **AND** behavior is identical to current implementation (backward compatible)

### Requirement: Script Generation Prompt Extension

The system SHALL instruct the LLM to identify and output product logo URLs during script generation.

#### Scenario: Logo Identification Prompt

- **WHEN** script generation prompt is constructed
- **THEN** prompt includes instruction to identify product/service logos
- **AND** instructs LLM to output `logo_assets` field with name and official logo URL
- **EXAMPLE**: "If the blog content mentions specific products or services, identify them and provide their official logo URLs in the `logo_assets` field."

#### Scenario: LLM Prompt Includes Examples

- **WHEN** script generation prompt is constructed
- **THEN** prompt includes example output format for `logo_assets`
- **AND** clarifies that URLs should point to official, publicly accessible logos

### Requirement: Project Directory Structure

The system SHALL create a dedicated directory for logo assets within the project structure.

#### Scenario: Logo Directory Creation

- **WHEN** a new project is initialized
- **THEN** `projects/<name>/assets/logos/` directory is created
- **AND** directory permissions allow read/write access

#### Scenario: Logo Directory in Existing Projects

- **WHEN** logo download is requested in an existing project without `logos/` directory
- **THEN** the directory is automatically created before download
- **AND** no error occurs if directory already exists
