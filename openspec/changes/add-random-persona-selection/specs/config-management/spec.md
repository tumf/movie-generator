## ADDED Requirements

### Requirement: Persona Pool Configuration

The system SHALL support persona pool configuration that enables random persona selection from a predefined pool.

#### Scenario: Define Persona Pool in Config
- **GIVEN** a configuration file with multiple personas
- **WHEN** `persona_pool` section is added:
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      character: "..."
    - id: "metan"
      name: "四国めたん"
      character: "..."
    - id: "tsumugi"
      name: "春日部つむぎ"
      character: "..."
  
  persona_pool:
    enabled: true
    count: 2
    seed: null
  ```
- **THEN** the config is parsed successfully
- **AND** `config.persona_pool.enabled` is `True`
- **AND** `config.persona_pool.count` is `2`
- **AND** `config.persona_pool.seed` is `None`

#### Scenario: Persona Pool with Seed
- **GIVEN** `persona_pool.seed: 42` is configured
- **WHEN** the config is loaded
- **THEN** `config.persona_pool.seed` is `42`
- **AND** the seed is used for reproducible random selection

#### Scenario: Persona Pool Disabled
- **GIVEN** `persona_pool.enabled: false` is configured
- **WHEN** the config is loaded
- **THEN** random selection is disabled
- **AND** all defined personas are used

#### Scenario: Persona Pool Not Specified (Backward Compatibility)
- **GIVEN** a config file without `persona_pool` section
- **WHEN** the config is loaded
- **THEN** `config.persona_pool` is `None`
- **AND** all defined personas are used (traditional behavior)

### Requirement: Persona Pool Count Validation

The system SHALL validate that the persona pool count does not exceed the number of available personas.

#### Scenario: Valid Count
- **GIVEN** 3 personas are defined
- **AND** `persona_pool.count: 2` is configured
- **WHEN** the config is validated
- **THEN** validation passes

#### Scenario: Count Exceeds Available Personas
- **GIVEN** 3 personas are defined
- **AND** `persona_pool.count: 5` is configured
- **WHEN** the config is validated
- **THEN** a `ValueError` is raised
- **AND** the error message is "Cannot select 5 personas from pool of 3"

#### Scenario: Count is Zero or Negative
- **GIVEN** `persona_pool.count: 0` is configured
- **WHEN** the config is validated
- **THEN** a `ValueError` is raised
- **AND** the error message is "Persona pool count must be positive"

### Requirement: PersonaPoolConfig Data Model

The system SHALL provide a `PersonaPoolConfig` Pydantic model for persona pool configuration.

#### Scenario: Create PersonaPoolConfig
- **GIVEN** persona pool data:
  - enabled: `True`
  - count: `2`
  - seed: `None`
- **WHEN** `PersonaPoolConfig` is instantiated
- **THEN** all fields are stored correctly
- **AND** the model can be serialized to dict/YAML

#### Scenario: PersonaPoolConfig with Seed
- **GIVEN** `seed: 42` is provided
- **WHEN** `PersonaPoolConfig` is instantiated
- **THEN** `config.seed` is `42`
- **AND** the seed is used for random selection

#### Scenario: PersonaPoolConfig Default Values
- **GIVEN** only `enabled: true` is provided
- **WHEN** `PersonaPoolConfig` is instantiated
- **THEN** `count` defaults to `2`
- **AND** `seed` defaults to `None`
