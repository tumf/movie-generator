## ADDED Requirements

### Requirement: MCP Configuration File Loading

The system SHALL support loading MCP (Model Context Protocol) configuration files to enable integration with external tools.

#### Scenario: Load opencode.jsonc format

- **WHEN** user provides `opencode.jsonc` path via `--mcp-config` option
- **THEN** the system parses JSONC format (JSON with comments) and extracts MCP server configurations

#### Scenario: Load .cursor/mcp.json format

- **WHEN** user provides `~/.cursor/mcp.json` path via `--mcp-config` option
- **THEN** the system parses JSON format under `mcpServers` key

#### Scenario: Load claude_desktop_config.json format

- **WHEN** user provides Claude Desktop config file path via `--mcp-config` option
- **THEN** the system parses JSON format under `mcpServers` key

#### Scenario: Invalid MCP config file

- **WHEN** MCP config file is malformed or missing
- **THEN** the system raises a clear error message and exits

#### Scenario: No MCP config specified

- **WHEN** user does not provide `--mcp-config` option
- **THEN** the system proceeds without MCP integration (backward compatible)

### Requirement: MCP Client Implementation

The system SHALL communicate with MCP servers to invoke tools such as Firecrawl.

#### Scenario: Invoke Firecrawl tool via MCP

- **WHEN** MCP config contains Firecrawl server configuration
- **THEN** the system can call Firecrawl to scrape web content with URL parameter

#### Scenario: Handle MCP server timeout

- **WHEN** MCP server does not respond within 30 seconds
- **THEN** the system logs an error and falls back to traditional URL fetching

#### Scenario: Handle MCP server unavailable

- **WHEN** MCP server is not running or unreachable
- **THEN** the system logs a warning and falls back to traditional URL fetching

#### Scenario: Environment variable substitution in string values

- **WHEN** MCP config uses `{env:VAR_NAME}` format in string values (e.g., API keys)
- **THEN** the system substitutes `{env:VAR_NAME}` with the actual environment variable value

#### Scenario: Missing environment variable

- **WHEN** MCP config references `{env:VAR_NAME}` but the variable is not set
- **THEN** the system raises a clear error indicating which variable is missing

#### Scenario: Multiple environment variable substitutions

- **WHEN** MCP config contains multiple `{env:...}` references in different fields
- **THEN** the system substitutes all occurrences with corresponding environment variable values

#### Scenario: Nested environment variable in objects

- **WHEN** MCP config has environment variable references in nested objects (e.g., `headers.FIRECRAWL_API_KEY: "{env:FIRECRAWL_API_KEY}"`)
- **THEN** the system recursively substitutes all `{env:...}` patterns throughout the configuration

### Requirement: CLI Option for MCP Config

The CLI SHALL accept an optional `--mcp-config` parameter to specify MCP configuration file path.

#### Scenario: Specify MCP config via CLI

- **WHEN** user runs `movie-generator generate --url <URL> --mcp-config opencode.jsonc`
- **THEN** the system loads MCP configuration from specified file

#### Scenario: Validate MCP config path

- **WHEN** user provides non-existent file path via `--mcp-config`
- **THEN** the system raises a clear error message with the invalid path

### Requirement: Script Generation with MCP Tools

The system SHALL use MCP tools (e.g., Firecrawl) to fetch web content before script generation when MCP config is provided.

#### Scenario: Fetch content via Firecrawl MCP

- **WHEN** user provides URL and MCP config with Firecrawl configured
- **THEN** the system uses Firecrawl to scrape the URL content instead of basic HTTP client

#### Scenario: Enrich script with MCP-fetched content

- **WHEN** Firecrawl successfully retrieves structured content (title, description, markdown)
- **THEN** the system passes this content to `generate_script()` for LLM processing

#### Scenario: Fallback to traditional fetch on MCP failure

- **WHEN** MCP tool invocation fails (timeout, error, unavailable)
- **THEN** the system falls back to traditional URL fetching method
