# MCP Agent Feature

This document describes the MCP Agent feature, which allows the LLM to autonomously select and execute MCP (Model Context Protocol) tools for content fetching and analysis.

## Overview

The MCP Agent feature enhances the movie-generator with intelligent content fetching capabilities. Instead of simple URL scraping, the agent can:

- Use multiple tools (Firecrawl, Brave Search, etc.) autonomously
- Make intelligent decisions about which tool to use
- Chain multiple tool calls to gather comprehensive information
- Handle complex content extraction scenarios

## Architecture

```
┌─────────────────────────────────────────────────┐
│  generate_script_from_url_with_agent()         │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  MCPClient (connected to MCP servers)           │
│  - Firecrawl                                     │
│  - Brave Search (optional)                      │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  AgentLoop                                       │
│  1. Convert MCP tools → OpenAI format          │
│  2. Send task to LLM with tools                │
│  3. LLM decides which tools to call            │
│  4. Execute tool via MCPClient                 │
│  5. Return results to LLM                      │
│  6. Repeat until task complete                 │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  generate_script()                              │
│  (Standard LLM-based script generation)         │
└─────────────────────────────────────────────────┘
```

## Components

### 1. AgentLoop (`src/movie_generator/agent/agent_loop.py`)

Core agent implementation that manages the LLM-tool interaction loop.

**Key Features:**
- Converts MCP tools to OpenAI function calling format
- Manages message history between LLM and tools
- Enforces maximum iteration limit (default: 10)
- Handles tool execution errors gracefully

**API:**
```python
async with AgentLoop(
    mcp_client=client,
    openrouter_api_key="...",
    model="openai/gpt-4-turbo-preview",
    max_iterations=10,
) as agent:
    result = await agent.run("Fetch content from https://example.com")
```

### 2. Tool Converter (`src/movie_generator/agent/tool_converter.py`)

Converts MCP tool definitions to OpenAI function calling format.

**Example:**
```python
# MCP format
{
    "name": "firecrawl_scrape",
    "description": "Scrape a URL",
    "inputSchema": {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"]
    }
}

# OpenAI format (after conversion)
{
    "type": "function",
    "function": {
        "name": "firecrawl_scrape",
        "description": "Scrape a URL",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    }
}
```

### 3. Script Generation (`src/movie_generator/script/core.py`)

Two new functions for agent-based script generation:

- `generate_script_from_url_with_agent()` - Async version
- `generate_script_from_url_with_agent_sync()` - Sync wrapper

## Configuration

### MCP Configuration File (mcp.jsonc)

```jsonc
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@mendable/firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}"
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "{env:BRAVE_API_KEY}"
      }
    }
  }
}
```

### Environment Variables

- `OPENROUTER_API_KEY` - Required for LLM access
- `FIRECRAWL_API_KEY` - Required for Firecrawl MCP server
- `BRAVE_API_KEY` - Optional, enables Brave Search
- `MCP_CONFIG_PATH` - Path to mcp.jsonc (worker only)
- `CONFIG_PATH` - Path to config.yaml (worker only)

## Usage

### Python API

```python
from pathlib import Path
from movie_generator.script.core import generate_script_from_url_with_agent_sync

script_path = generate_script_from_url_with_agent_sync(
    url="https://example.com/blog",
    output_dir=Path("output"),
    mcp_config_path=Path("mcp.jsonc"),
    api_key="your-openrouter-key",
)
```

### Web Worker Integration

The worker automatically detects MCP configuration and uses agent mode:

```python
import os
from pathlib import Path

# Check if MCP config exists
mcp_config_path = os.environ.get("MCP_CONFIG_PATH")

if mcp_config_path and Path(mcp_config_path).exists():
    # Use agent mode
    script_path = await generate_script_from_url_with_agent(
        url=url,
        output_dir=output_dir,
        mcp_config_path=Path(mcp_config_path),
        api_key=api_key,
    )
else:
    # Use standard mode
    script_path = await generate_script_from_url(
        url=url,
        output_dir=output_dir,
        api_key=api_key,
    )
```

## Agent Behavior

The agent receives a task prompt like:

```
Fetch and analyze the content from the following URL: https://example.com/blog

Your task is to:
1. Scrape the URL to get the full content
2. Extract the main article/blog content in markdown format
3. Return the complete markdown content

Please use the available tools to accomplish this task.
```

The LLM then:
1. Analyzes the task
2. Decides which tool(s) to use (e.g., `firecrawl_scrape`)
3. Calls the tool with appropriate arguments
4. Processes the results
5. Returns the final markdown content

## Error Handling

### Maximum Iterations

If the agent exceeds the maximum number of iterations (default: 10), an `MCPError` is raised:

```python
MCPError: Agent loop exceeded maximum iterations (10)
```

**Solution:** Increase `max_iterations` or simplify the task.

### Tool Execution Failures

When a tool fails, the error is returned to the LLM as a tool result:

```json
{
  "error": "Tool execution failed: Connection timeout"
}
```

The LLM can then:
- Try a different tool
- Retry with different parameters
- Report the error to the user

### MCP Server Connection Issues

If MCP server fails to start:

```python
MCPError: MCP server process failed to start: <stderr>
```

**Solutions:**
- Check that `npx` is installed
- Verify API keys are set correctly
- Check MCP server package name
- Review server logs

## Troubleshooting

### Agent Not Using Tools

**Symptom:** Agent returns empty or generic responses without calling tools.

**Possible Causes:**
- LLM model doesn't support function calling
- System prompt is unclear
- Task description is ambiguous

**Solutions:**
- Use a model that supports function calling (e.g., GPT-4, GPT-3.5-turbo)
- Clarify the task prompt
- Check that tools are properly converted to OpenAI format

### Infinite Loop

**Symptom:** Agent keeps calling tools without finishing.

**Cause:** LLM cannot determine when the task is complete.

**Solution:**
- Add explicit success criteria in the task prompt
- Lower `max_iterations`
- Review LLM responses in logs

### Tool Arguments Invalid

**Symptom:** `MCPError: Invalid tool arguments JSON`

**Cause:** LLM generated malformed JSON for tool arguments.

**Solution:**
- Use a more capable LLM model
- Simplify tool schemas
- Add examples in tool descriptions

## Testing

### Unit Tests

```bash
# Test tool converter
uv run pytest tests/test_tool_converter.py -v

# Test agent loop
uv run pytest tests/test_agent_loop.py -v
```

### Integration Tests

```bash
# Test script generation with agent
uv run pytest tests/test_script_with_agent.py -v
```

### Manual Testing

```python
import asyncio
from pathlib import Path
from movie_generator.mcp.client import MCPClient
from movie_generator.mcp.config import load_mcp_config
from movie_generator.agent.agent_loop import AgentLoop

async def test_agent():
    mcp_config = load_mcp_config(Path("mcp.jsonc"))
    
    async with MCPClient(mcp_config, "firecrawl") as client:
        async with AgentLoop(
            mcp_client=client,
            openrouter_api_key="your-key",
            model="openai/gpt-4-turbo-preview",
        ) as agent:
            result = await agent.run(
                "Scrape https://example.com and extract the main content"
            )
            print(result)

asyncio.run(test_agent())
```

## Performance Considerations

- Each tool call adds latency (LLM inference + tool execution)
- Complex tasks may require multiple iterations
- Set appropriate `max_iterations` to balance thoroughness vs speed
- Use faster LLM models for simpler tasks

## Future Enhancements

- Support for MCP Sampling (server-side LLM calls)
- Additional MCP servers (Google Search, Wikipedia, etc.)
- Caching of tool results
- Parallel tool execution
- Agent decision logging and analytics

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OpenRouter Function Calling](https://openrouter.ai/docs#function-calling)
- [Firecrawl MCP Server](https://github.com/mendableai/firecrawl-mcp)
