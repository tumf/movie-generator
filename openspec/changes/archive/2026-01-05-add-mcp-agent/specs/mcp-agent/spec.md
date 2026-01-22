# MCP Agent Specification

## Purpose

This specification defines the MCP Agent system that enables LLM to autonomously select and use MCP tools (Firecrawl, Brave Search, etc.) for content fetching. The agent loop allows intelligent tool selection based on the URL and content requirements.

## ADDED Requirements

### Requirement: MCP Tool Format Conversion

The system SHALL convert MCP tool definitions to OpenAI tools format for use with OpenRouter's Tool Calling API.

#### Scenario: Convert MCP Tool to OpenAI Format
- **GIVEN** an MCP tool definition:
  ```json
  {
    "name": "firecrawl_scrape",
    "description": "Scrape content from a URL",
    "inputSchema": {
      "type": "object",
      "properties": {
        "url": {"type": "string", "description": "URL to scrape"}
      },
      "required": ["url"]
    }
  }
  ```
- **WHEN** `convert_mcp_tools_to_openai()` is called
- **THEN** the output SHALL be:
  ```json
  {
    "type": "function",
    "function": {
      "name": "firecrawl_scrape",
      "description": "Scrape content from a URL",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {"type": "string", "description": "URL to scrape"}
        },
        "required": ["url"]
      }
    }
  }
  ```

#### Scenario: Convert Multiple MCP Tools
- **GIVEN** a list of 3 MCP tool definitions
- **WHEN** `convert_mcp_tools_to_openai()` is called with the list
- **THEN** a list of 3 OpenAI tool definitions SHALL be returned
- **AND** each tool SHALL have `type: "function"` and a `function` object

### Requirement: Agent Loop Execution

The system SHALL execute an agent loop that allows LLM to call MCP tools iteratively until content is successfully retrieved.

#### Scenario: Single Tool Call Success
- **GIVEN** an MCPClient connected to Firecrawl
- **AND** a URL "https://example.com/blog"
- **WHEN** `AgentLoop.run()` is called
- **THEN** the LLM SHALL receive available tools
- **AND** if LLM requests `firecrawl_scrape` tool
- **THEN** `MCPClient.call_tool()` SHALL be invoked
- **AND** the tool result SHALL be added to message history
- **AND** LLM SHALL generate final content

#### Scenario: Multiple Tool Calls
- **GIVEN** an MCPClient with Firecrawl and Brave Search tools
- **AND** a URL that requires search before scraping
- **WHEN** `AgentLoop.run()` is called
- **THEN** LLM MAY call multiple tools in sequence
- **AND** each tool result SHALL be added to message history
- **AND** LLM SHALL generate final content after all tools complete

#### Scenario: Maximum Iteration Limit
- **GIVEN** max_iterations is set to 10
- **WHEN** LLM continues to request tool calls beyond 10 iterations
- **THEN** the agent loop SHALL terminate
- **AND** a `RuntimeError` SHALL be raised with message indicating iteration limit

#### Scenario: Stop Condition
- **GIVEN** an agent loop in progress
- **WHEN** LLM response has `finish_reason: "stop"`
- **THEN** the agent loop SHALL terminate
- **AND** the final text content SHALL be returned

### Requirement: Agent-Based Script Generation

The system SHALL provide a script generation function that uses the MCP agent for content fetching.

#### Scenario: Generate Script with Agent
- **GIVEN** a URL "https://example.com/blog"
- **AND** MCP configuration with Firecrawl server
- **AND** movie-generator configuration
- **WHEN** `generate_script_from_url_with_agent()` is called
- **THEN** the agent loop SHALL fetch content from the URL
- **AND** the fetched content SHALL be passed to script generation
- **AND** a VideoScript SHALL be returned

#### Scenario: Agent Fetches Content via Tool Selection
- **GIVEN** an MCPClient connected with multiple tools
- **WHEN** `generate_script_from_url_with_agent()` is called
- **THEN** LLM SHALL autonomously select appropriate tools
- **AND** content SHALL be extracted and formatted

### Requirement: Worker MCP Configuration

The worker SHALL support MCP agent configuration via environment variables.

#### Scenario: Worker with MCP Configuration
- **GIVEN** environment variable `CONFIG_PATH=/app/config/config.yaml`
- **AND** environment variable `MCP_CONFIG_PATH=/app/config/mcp.jsonc`
- **WHEN** the worker processes a job
- **THEN** `generate_script_from_url_with_agent()` SHALL be used
- **AND** MCP tools SHALL be available for content fetching

#### Scenario: Worker without MCP Configuration
- **GIVEN** environment variable `CONFIG_PATH=/app/config/config.yaml`
- **AND** environment variable `MCP_CONFIG_PATH` is NOT set
- **WHEN** the worker processes a job
- **THEN** `generate_script_from_url()` SHALL be used (standard behavior)
- **AND** no MCP agent features SHALL be invoked

#### Scenario: Worker with Invalid MCP Configuration
- **GIVEN** environment variable `MCP_CONFIG_PATH=/app/config/invalid.jsonc`
- **AND** the file does not exist or is invalid
- **WHEN** the worker starts processing a job
- **THEN** an error SHALL be raised
- **AND** the job SHALL be marked as failed with error message

### Requirement: MCP Configuration Files

The system SHALL support MCP configuration files for defining available MCP servers.

#### Scenario: Valid MCP Configuration
- **GIVEN** an MCP configuration file:
  ```jsonc
  {
    "mcpServers": {
      "firecrawl": {
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-firecrawl"],
        "env": {
          "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}"
        }
      }
    }
  }
  ```
- **WHEN** the configuration is loaded
- **THEN** the Firecrawl server SHALL be available
- **AND** environment variable references SHALL be resolved

#### Scenario: Multiple MCP Servers
- **GIVEN** an MCP configuration with Firecrawl and Brave Search
- **WHEN** the agent loop is initialized
- **THEN** tools from both servers SHALL be available
- **AND** LLM SHALL be able to call tools from either server
