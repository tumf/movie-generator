# Web Worker Configuration

This directory contains configuration files for the movie-generator web worker.

## Files

### config.yaml

Main configuration file for video generation settings. This includes:

- **project**: Project name and output directory
- **style**: Video resolution, FPS, animation settings
- **narration**: Character and style for narration
- **voicevox**: Voice synthesis settings
- **content.llm**: LLM model for script generation
- **slides.llm**: LLM model for slide image generation

### mcp.jsonc

MCP (Model Context Protocol) server configuration. This file defines external tools that the agent can use:

- **firecrawl**: Web scraping tool (required for agent mode)
- **brave-search**: Web search tool (optional)

## Environment Variables

The following environment variables must be set:

### Required for Standard Mode

- `OPENROUTER_API_KEY`: OpenRouter API key for LLM access
- `CONFIG_PATH`: Path to config.yaml (e.g., `/app/config/config.yaml`)

### Required for Agent Mode

- `OPENROUTER_API_KEY`: OpenRouter API key for LLM access
- `FIRECRAWL_API_KEY`: Firecrawl API key for web scraping
- `CONFIG_PATH`: Path to config.yaml
- `MCP_CONFIG_PATH`: Path to mcp.jsonc (e.g., `/app/config/mcp.jsonc`)

### Optional

- `BRAVE_API_KEY`: Brave Search API key (enables web search in agent mode)

## Usage

### Standard Mode (without MCP agent)

```bash
export OPENROUTER_API_KEY="your-key"
export CONFIG_PATH="/path/to/config.yaml"

# Worker will use standard content fetching
python -m web.worker.main
```

### Agent Mode (with MCP agent)

```bash
export OPENROUTER_API_KEY="your-key"
export FIRECRAWL_API_KEY="your-firecrawl-key"
export CONFIG_PATH="/path/to/config.yaml"
export MCP_CONFIG_PATH="/path/to/mcp.jsonc"

# Worker will use agent-based content fetching
python -m web.worker.main
```

## Docker Example

```dockerfile
ENV CONFIG_PATH=/app/config/config.yaml
ENV MCP_CONFIG_PATH=/app/config/mcp.jsonc
ENV OPENROUTER_API_KEY=your-key-here
ENV FIRECRAWL_API_KEY=your-firecrawl-key-here

COPY web/config/config.yaml /app/config/config.yaml
COPY web/config/mcp.jsonc /app/config/mcp.jsonc
```

## Switching Between Modes

The worker automatically detects whether to use agent mode or standard mode:

- If `MCP_CONFIG_PATH` is set and the file exists → **Agent mode**
- Otherwise → **Standard mode**

This allows seamless switching without code changes.
