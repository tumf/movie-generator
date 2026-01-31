## MODIFIED Requirements
### Requirement: Slides Generation Command

The CLI SHALL provide a `slides generate` subcommand that generates slide images from a script.

The command SHALL accept the following options:
- `--config, -c <path>`: Path to config file
- `--api-key <key>`: OpenRouter API key
- `--scenes <range>`: Scene range to process
- `--model <model>`: Image generation model
- `--language, -l <lang>`: Language for slides (default: "ja")
- `--max-concurrent <n>`: Maximum concurrent API requests (default: 2)

The implementation SHALL separate task planning (which slides to generate/skip) from task execution for maintainability.

#### Scenario: Generate slides from script
- **GIVEN** a valid `script.yaml` file with slide prompts
- **WHEN** user runs `movie-generator slides generate ./output/script.yaml`
- **THEN** the system generates slide images using AI
- **AND** saves PNG files to `slides/<lang>/` directory

#### Scenario: Slides already exist
- **GIVEN** some slide files already exist
- **WHEN** user runs `movie-generator slides generate <script.yaml>`
- **THEN** the system skips existing slide files
- **AND** only generates missing slides

---
