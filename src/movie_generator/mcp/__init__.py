"""MCP (Model Context Protocol) integration for movie generator.

Provides functionality to connect to MCP servers (like Firecrawl) and
use their tools for enhanced content fetching.
"""

from .client import MCPClient, fetch_content_with_mcp
from .config import MCPConfig, load_mcp_config

__all__ = ["MCPClient", "MCPConfig", "load_mcp_config", "fetch_content_with_mcp"]
