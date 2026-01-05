"""Convert MCP tool definitions to OpenAI function calling format.

This module provides conversion utilities to transform MCP tool definitions
(which use JSON Schema for inputSchema) into OpenAI's function calling format.
"""

from typing import Any


def convert_mcp_tools_to_openai(mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert MCP tool definitions to OpenAI function calling format.

    Args:
        mcp_tools: List of MCP tool definitions. Each tool should have:
            - name: Tool name
            - description: Tool description
            - inputSchema: JSON Schema defining input parameters

    Returns:
        List of tools in OpenAI format. Each tool has:
            - type: "function"
            - function:
                - name: Function name
                - description: Function description
                - parameters: JSON Schema for parameters

    Example:
        >>> mcp_tools = [{
        ...     "name": "firecrawl_scrape",
        ...     "description": "Scrape a URL",
        ...     "inputSchema": {
        ...         "type": "object",
        ...         "properties": {"url": {"type": "string"}},
        ...         "required": ["url"]
        ...     }
        ... }]
        >>> openai_tools = convert_mcp_tools_to_openai(mcp_tools)
        >>> openai_tools[0]["type"]
        'function'
        >>> openai_tools[0]["function"]["name"]
        'firecrawl_scrape'
    """
    openai_tools = []

    for tool in mcp_tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": tool.get("inputSchema", {}),
            },
        }
        openai_tools.append(openai_tool)

    return openai_tools
