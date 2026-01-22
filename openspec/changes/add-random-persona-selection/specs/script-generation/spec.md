## ADDED Requirements

### Requirement: Random Persona Selection from Pool

The system SHALL select a random subset of personas from the persona pool when enabled.

#### Scenario: Select 2 Personas from 3
- **GIVEN** 3 personas are defined (zundamon, metan, tsumugi)
- **AND** `persona_pool.enabled: true` and `persona_pool.count: 2`
- **AND** `persona_pool.seed: 42` (for reproducibility)
- **WHEN** `generate_script()` is called
- **THEN** 2 personas are randomly selected
- **AND** the selection is reproducible with the same seed
- **AND** selected persona IDs are logged

#### Scenario: All Personas Selected When Pool Disabled
- **GIVEN** 3 personas are defined
- **AND** `persona_pool.enabled: false`
- **WHEN** `generate_script()` is called
- **THEN** all 3 personas are used for script generation

#### Scenario: All Personas Selected When Pool Not Configured
- **GIVEN** 3 personas are defined
- **AND** `persona_pool` is not specified (None)
- **WHEN** `generate_script()` is called
- **THEN** all 3 personas are used (backward compatibility)

#### Scenario: Different Personas Selected on Each Call
- **GIVEN** 3 personas are defined
- **AND** `persona_pool.enabled: true` and `persona_pool.count: 2`
- **AND** `persona_pool.seed` is `None` (no seed)
- **WHEN** `generate_script()` is called twice
- **THEN** different persona combinations may be selected
- **AND** each combination is random

### Requirement: Persona Selection Function

The system SHALL provide a `select_personas_from_pool()` function for persona selection logic.

#### Scenario: Select Personas with Seed
- **GIVEN** personas list: `[{"id": "zundamon"}, {"id": "metan"}, {"id": "tsumugi"}]`
- **AND** `pool_config.enabled: true`, `pool_config.count: 2`, `pool_config.seed: 42`
- **WHEN** `select_personas_from_pool(personas, pool_config)` is called
- **THEN** 2 personas are returned
- **AND** the same 2 personas are returned on subsequent calls with seed 42

#### Scenario: No Selection When Pool Disabled
- **GIVEN** personas list with 3 personas
- **AND** `pool_config.enabled: false`
- **WHEN** `select_personas_from_pool(personas, pool_config)` is called
- **THEN** the original personas list (all 3) is returned

#### Scenario: No Selection When Pool Not Configured
- **GIVEN** personas list with 3 personas
- **AND** `pool_config` is `None`
- **WHEN** `select_personas_from_pool(personas, pool_config)` is called
- **THEN** the original personas list (all 3) is returned

#### Scenario: Count Validation Error
- **GIVEN** personas list with 3 personas
- **AND** `pool_config.count: 5`
- **WHEN** `select_personas_from_pool(personas, pool_config)` is called
- **THEN** a `ValueError` is raised
- **AND** the error message is "Cannot select 5 personas from pool of 3"

### Requirement: Persona Selection Logging

The system SHALL log persona selection information for debugging and auditing.

#### Scenario: Log Selected Personas
- **GIVEN** 3 personas are defined
- **AND** persona pool is enabled with count=2
- **WHEN** personas are selected
- **THEN** an INFO log is emitted: "Selected personas from pool: zundamon, metan"
- **AND** the log includes the seed if specified

#### Scenario: Log All Personas When Pool Disabled
- **GIVEN** 3 personas are defined
- **AND** persona pool is disabled
- **WHEN** `generate_script()` is called
- **THEN** a DEBUG log is emitted: "Persona pool disabled, using all personas"

### Requirement: CLI Persona Pool Options

The CLI SHALL support `--persona-pool-count` and `--persona-pool-seed` options to override config values.

#### Scenario: Override Count via CLI
- **GIVEN** config has `persona_pool.count: 2`
- **WHEN** `generate` command is run with `--persona-pool-count 3`
- **THEN** 3 personas are selected
- **AND** the CLI option overrides the config value

#### Scenario: Specify Seed via CLI
- **GIVEN** config has `persona_pool.seed: null`
- **WHEN** `generate` command is run with `--persona-pool-seed 42`
- **THEN** seed 42 is used for selection
- **AND** the selection is reproducible

#### Scenario: CLI Options Without Persona Pool in Config
- **GIVEN** config does not have `persona_pool` section
- **WHEN** `generate` command is run with `--persona-pool-count 2`
- **THEN** persona pool is enabled with count=2
- **AND** 2 personas are randomly selected

### Requirement: Integration with Dialogue Mode

The system SHALL automatically use dialogue mode when personas are selected from pool.

#### Scenario: Dialogue Mode with Selected Personas
- **GIVEN** 3 personas are defined
- **AND** persona pool selects 2 personas (zundamon, metan)
- **WHEN** `generate_script()` is called
- **THEN** dialogue mode is used
- **AND** only the 2 selected personas appear in the generated script
- **AND** the unselected persona (tsumugi) is not included

#### Scenario: Single Persona Selected
- **GIVEN** 3 personas are defined
- **AND** `persona_pool.count: 1`
- **WHEN** `generate_script()` is called
- **THEN** single-speaker mode is used
- **AND** the selected persona is used for all narrations

### Requirement: Web UI Default Configuration

The Web UI SHALL use a default configuration with persona pool enabled.

#### Scenario: Web UI Default Config
- **GIVEN** Web UI is initialized
- **WHEN** default config is loaded
- **THEN** 3 personas are defined (zundamon, metan, tsumugi)
- **AND** `persona_pool.enabled: true`
- **AND** `persona_pool.count: 2`
- **AND** `persona_pool.seed: null` (random selection)

#### Scenario: Web UI Random Persona Generation
- **GIVEN** Web UI default config is used
- **WHEN** a user generates a video from a blog URL
- **THEN** 2 personas are randomly selected from the pool
- **AND** the generated video features the selected personas
