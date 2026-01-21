# Configuration Guide

This document describes the configuration options for Movie Generator.

## Persona Pool Configuration

The persona pool feature allows random selection of personas from a defined pool for multi-speaker dialogue generation. This adds variety to generated videos by changing the speaker combinations.

### Basic Configuration

```yaml
# Define multiple personas
personas:
  - id: "zundamon"
    name: "ずんだもん"
    character: "元気で明るい東北の妖精"
    synthesizer:
      engine: "voicevox"
      speaker_id: 3
      speed_scale: 1.0
    subtitle_color: "#8FCF4F"
  - id: "metan"
    name: "四国めたん"
    character: "優しくて落ち着いた四国の妖精"
    synthesizer:
      engine: "voicevox"
      speaker_id: 2
      speed_scale: 1.0
    subtitle_color: "#FF69B4"
  - id: "tsumugi"
    name: "春日部つむぎ"
    character: "明るく元気な春日部出身の女の子"
    synthesizer:
      engine: "voicevox"
      speaker_id: 8
      speed_scale: 1.0
    subtitle_color: "#FFA07A"

# Enable persona pool for random selection
persona_pool:
  enabled: true
  count: 2       # Number of personas to randomly select
  seed: null     # Optional: set for reproducible selection (testing only)
```

### Configuration Fields

#### `persona_pool.enabled` (boolean, default: `false`)
- Enables or disables random persona selection
- When `false` or not specified, all defined personas are used
- When `true`, randomly selects `count` personas from the pool

#### `persona_pool.count` (integer, default: `2`)
- Number of personas to randomly select from the pool
- Must be >= 1 and <= total number of personas
- Only used when `enabled` is `true`

#### `persona_pool.seed` (integer, optional)
- Random seed for reproducible persona selection
- Primarily for testing and debugging
- Leave as `null` for truly random selection in production

### CLI Options

You can override persona pool settings via CLI:

```bash
# Override persona pool count
uv run movie-generator generate <url> --persona-pool-count 3

# Set seed for reproducible selection (testing)
uv run movie-generator generate <url> --persona-pool-seed 42

# Combine both
uv run movie-generator generate <url> --persona-pool-count 2 --persona-pool-seed 42
```

### Example Configurations

#### Web UI Default (3 personas, select 2 randomly)
```yaml
personas:
  - id: "zundamon"
    name: "ずんだもん"
    character: "元気で明るい東北の妖精"
    # ... synthesizer config ...
  - id: "metan"
    name: "四国めたん"
    character: "優しくて落ち着いた四国の妖精"
    # ... synthesizer config ...
  - id: "tsumugi"
    name: "春日部つむぎ"
    character: "明るく元気な春日部出身の女の子"
    # ... synthesizer config ...

persona_pool:
  enabled: true
  count: 2
  seed: null  # Random selection
```

#### Fixed 2-Persona Dialogue (no random selection)
```yaml
personas:
  - id: "alice"
    name: "Alice"
    # ... config ...
  - id: "bob"
    name: "Bob"
    # ... config ...

# persona_pool not specified - uses all personas
```

#### Testing with Reproducible Selection
```yaml
personas:
  - id: "persona1"
    # ...
  - id: "persona2"
    # ...
  - id: "persona3"
    # ...

persona_pool:
  enabled: true
  count: 2
  seed: 42  # Same seed = same selection every time
```

### Behavior

- **Pool disabled** (`enabled: false` or not specified): All defined personas are used
- **Pool enabled** (`enabled: true`): 
  1. Randomly selects `count` personas from the pool
  2. Only selected personas participate in dialogue
  3. Script generation uses only selected personas
  4. Selected persona IDs are logged for debugging

### Use Cases

- **Web UI**: Default random selection adds variety to automated video generation
- **Testing**: Use `seed` for reproducible test cases
- **CLI**: Manual control with explicit persona specification (no pool)
