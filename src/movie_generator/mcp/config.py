"""MCP configuration file loader.

Supports loading MCP server configurations from multiple file formats:
- opencode.jsonc (JSONC format with comments)
- .cursor/mcp.json (JSON format)
- claude_desktop_config.json (JSON format)

All formats support environment variable references in the form {env:VAR_NAME}.
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class MCPConfig(BaseModel):
    """MCP configuration containing multiple server definitions."""

    mcpServers: dict[str, MCPServerConfig] = Field(default_factory=dict)


def _strip_jsonc_comments(content: str) -> str:
    """Remove comments from JSONC content.

    Handles both single-line (//) and multi-line (/* */) comments.

    Args:
        content: JSONC file content.

    Returns:
        JSON content with comments removed.
    """
    # Remove single-line comments
    content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    # Remove multi-line comments
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    return content


def _replace_env_vars(data: Any) -> Any:
    """Recursively replace environment variable references in data structure.

    Replaces strings in the format {env:VAR_NAME} with the actual environment
    variable value. Supports nested dictionaries and lists.

    Args:
        data: Data structure to process (dict, list, str, or other).

    Returns:
        Data structure with environment variables replaced.

    Raises:
        ValueError: If an environment variable is referenced but not defined.
    """
    if isinstance(data, dict):
        return {key: _replace_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_replace_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Find all {env:VAR_NAME} patterns
        pattern = r"\{env:([A-Z_][A-Z0-9_]*)\}"
        matches = re.finditer(pattern, data)

        result = data
        for match in matches:
            var_name = match.group(1)
            var_value = os.environ.get(var_name)

            if var_value is None:
                raise ValueError(f"Environment variable '{var_name}' is referenced but not defined")

            # Replace the entire {env:VAR_NAME} with the value
            result = result.replace(match.group(0), var_value)

        return result
    else:
        return data


def load_mcp_config(config_path: Path) -> MCPConfig:
    """Load MCP configuration from file.

    Supports JSON and JSONC formats. Automatically replaces environment
    variable references in the form {env:VAR_NAME}.

    Args:
        config_path: Path to the MCP configuration file.

    Returns:
        Parsed MCP configuration.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If file format is invalid or env var is undefined.
        json.JSONDecodeError: If JSON/JSONC parsing fails.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"MCP config file not found: {config_path}")

    # Read file content
    content = config_path.read_text(encoding="utf-8")

    # Strip comments if JSONC format
    if config_path.suffix == ".jsonc":
        content = _strip_jsonc_comments(content)

    # Parse JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {config_path}: {e.msg}", e.doc, e.pos) from e

    # Replace environment variables
    data = _replace_env_vars(data)

    # Validate and parse with Pydantic
    return MCPConfig.model_validate(data)
