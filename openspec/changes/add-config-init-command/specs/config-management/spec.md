## ADDED Requirements

### Requirement: Configuration File Initialization Command

The system SHALL provide a CLI command to output the default configuration file.

#### Scenario: Output to stdout
- **WHEN** `movie-generator config init` is executed without options
- **THEN** the default configuration is output to stdout in YAML format
- **AND** the output includes helpful comments explaining each field

#### Scenario: Output to file
- **WHEN** `movie-generator config init --output config.yaml` is executed
- **THEN** the default configuration is written to `config.yaml`
- **AND** the file includes helpful comments explaining each field

#### Scenario: File already exists
- **GIVEN** a file named `config.yaml` exists
- **WHEN** `movie-generator config init --output config.yaml` is executed
- **THEN** a warning message is displayed
- **AND** the user is prompted to confirm overwrite
- **AND** the file is overwritten only if confirmed

#### Scenario: Invalid output path
- **WHEN** `movie-generator config init --output /invalid/path/config.yaml` is executed
- **AND** the directory `/invalid/path/` does not exist
- **THEN** an error message is displayed
- **AND** the command exits with non-zero status

#### Scenario: Generated config is valid
- **GIVEN** the output from `config init` is saved to a file
- **WHEN** the file is loaded with `load_config()`
- **THEN** the configuration is successfully validated
- **AND** all fields match the default values

### Requirement: Configuration File Format

The system SHALL generate configuration files with inline documentation.

#### Scenario: Comments for each section
- **WHEN** configuration is output
- **THEN** each top-level section includes a comment explaining its purpose
- **AND** complex fields include inline comments with examples

#### Scenario: YAML format only
- **WHEN** configuration is output
- **THEN** the format is valid YAML
- **AND** the structure matches `config/default.yaml`
