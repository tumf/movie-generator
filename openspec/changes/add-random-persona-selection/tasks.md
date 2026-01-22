# Implementation Tasks

## 1. Data Models and Configuration

- [x] 1.1 Add `PersonaPoolConfig` model to `config.py`
  - [x] 1.1.1 Define `enabled` field (bool)
  - [x] 1.1.2 Define `count` field (int, default=2)
  - [x] 1.1.3 Define `seed` field (int | None, for reproducible testing)
- [x] 1.2 Add `persona_pool` field to `Config` model
  - [x] 1.2.1 Field type: `PersonaPoolConfig | None`
  - [x] 1.2.2 Default: `None` (backward compatible)
- [x] 1.3 Create Web UI default config with persona pool
  - [x] 1.3.1 Define 3 personas (zundamon, metan, tsumugi)
  - [x] 1.3.2 Enable persona_pool with count=2

## 2. Persona Selection Logic

- [x] 2.1 Implement `select_personas_from_pool()` in `script/generator.py`
  - [x] 2.1.1 Check if `persona_pool` is enabled
  - [x] 2.1.2 Validate `count <= len(personas)`
  - [x] 2.1.3 Use `random.sample()` for random selection
  - [x] 2.1.4 Support seed for reproducibility
  - [x] 2.1.5 Return selected personas
- [x] 2.2 Integrate selection into `generate_script()`
  - [x] 2.2.1 Call selection before prompt generation
  - [x] 2.2.2 Pass selected personas to prompt
  - [x] 2.2.3 Log selected persona IDs

## 3. CLI Integration

- [x] 3.1 Add `--persona-pool-count` option to `generate` command
  - [x] 3.1.1 Optional override for config value
  - [x] 3.1.2 Default: use config value
- [x] 3.2 Add `--persona-pool-seed` option for testing
  - [x] 3.2.1 Integer seed for reproducible selection
  - [x] 3.2.2 Default: None (random)

## 4. Testing

- [x] 4.1 Unit tests for `select_personas_from_pool()`
  - [x] 4.1.1 Test random selection with seed
  - [x] 4.1.2 Test selection count validation
  - [x] 4.1.3 Test backward compatibility (pool disabled)
- [x] 4.2 Integration tests
  - [x] 4.2.1 Test script generation with random personas
  - [x] 4.2.2 Test Web UI config
  - [x] 4.2.3 Test CLI options


## 5. Documentation

- [x] 5.1 Update `docs/CONFIGURATION.md`
  - [x] 5.1.1 Document `persona_pool` section
  - [x] 5.1.2 Add example configurations
- [x] 5.2 Update `README.md`
  - [x] 5.2.1 Mention random persona feature
  - [x] 5.2.2 Add CLI option examples
- [x] 5.3 Add inline code comments
  - [x] 5.3.1 Document selection algorithm
  - [x] 5.3.2 Document seed usage

## Future Work

- E2E test with actual video generation (manual verification required)
  - Generate video with random personas
  - Verify selected personas in output script.yaml
