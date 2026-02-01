## MODIFIED Requirements
### Requirement: Script Creation Command

The CLI SHALL provide a `script create` subcommand that generates a video script from a URL.

The command SHALL accept the following options:
- `--output, -o <dir>`: Output directory (default: `./output`)
- `--config, -c <path>`: Path to config file
- `--api-key <key>`: OpenRouter API key
- `--mcp-config <path>`: Path to MCP configuration file
- `--character <name>`: Narrator character name
- `--style <style>`: Narration style
- `--model <model>`: LLM model to use

The implementation SHALL reuse the same common URL/content/script pipeline as `generate` to avoid drift.

#### Scenario: Generate script from URL
- **GIVEN** a valid blog URL
- **WHEN** user runs `movie-generator script create https://example.com/blog`
- **THEN** the system fetches content from the URL
- **AND** generates a video script using LLM
- **AND** saves `script.yaml` to the output directory

#### Scenario: Script already exists
- **GIVEN** `script.yaml` already exists in the output directory
- **WHEN** user runs `movie-generator script create <URL>`
- **THEN** the system skips script generation
- **AND** displays a message indicating the script already exists

---
