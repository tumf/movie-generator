## MODIFIED Requirements
### Requirement: Default Configuration

The system SHALL provide default configuration and merge it with user configuration, including language settings.

Default values and validation bounds SHALL be expressed as named constants to avoid scattered magic numbers.

#### Scenario: Apply Default Configuration
- **WHEN** user configuration specifies only some fields
- **THEN** unspecified fields use default values
- **AND** `content.languages` defaults to `["ja"]` if not specified

#### Scenario: Override Default Configuration
- **WHEN** user configuration specifies a field
- **THEN** the default value is overridden with the user value
- **AND** custom `content.languages` list replaces the default
