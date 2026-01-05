"""Agent module for LLM-driven tool execution via MCP.

This module provides an agent loop that allows LLMs to autonomously select
and execute MCP tools to accomplish tasks.
"""

from .agent_loop import AgentLoop
from .tool_converter import convert_mcp_tools_to_openai

__all__ = [
    "AgentLoop",
    "convert_mcp_tools_to_openai",
]
