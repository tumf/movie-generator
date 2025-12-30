"""Tests for MCP configuration file loading."""

import json
import os
from pathlib import Path

import pytest

from movie_generator.mcp.config import (
    MCPConfig,
    _replace_env_vars,
    _strip_jsonc_comments,
    load_mcp_config,
)


def test_strip_jsonc_comments():
    """Test JSONC comment removal."""
    # Single-line comments
    jsonc = """
    {
        "key": "value", // This is a comment
        "number": 42
    }
    """
    result = _strip_jsonc_comments(jsonc)
    assert "//" not in result
    assert "value" in result

    # Multi-line comments
    jsonc = """
    {
        /* This is a
           multi-line comment */
        "key": "value"
    }
    """
    result = _strip_jsonc_comments(jsonc)
    assert "/*" not in result
    assert "*/" not in result
    assert "value" in result


def test_replace_env_vars_success():
    """Test successful environment variable replacement."""
    # Set test environment variables
    os.environ["TEST_VAR"] = "test_value"
    os.environ["ANOTHER_VAR"] = "another_value"

    # Test simple string replacement
    data = {"key": "{env:TEST_VAR}"}
    result = _replace_env_vars(data)
    assert result["key"] == "test_value"

    # Test nested dictionary
    data = {"outer": {"inner": "{env:ANOTHER_VAR}"}}
    result = _replace_env_vars(data)
    assert result["outer"]["inner"] == "another_value"

    # Test list
    data = {"list": ["{env:TEST_VAR}", "normal", "{env:ANOTHER_VAR}"]}
    result = _replace_env_vars(data)
    assert result["list"] == ["test_value", "normal", "another_value"]

    # Cleanup
    del os.environ["TEST_VAR"]
    del os.environ["ANOTHER_VAR"]


def test_replace_env_vars_multiple_in_string():
    """Test replacing multiple environment variables in a single string."""
    os.environ["VAR_A"] = "valueA"
    os.environ["VAR_B"] = "valueB"

    data = {"key": "prefix_{env:VAR_A}_middle_{env:VAR_B}_suffix"}
    result = _replace_env_vars(data)
    assert result["key"] == "prefix_valueA_middle_valueB_suffix"

    # Cleanup
    del os.environ["VAR_A"]
    del os.environ["VAR_B"]


def test_replace_env_vars_undefined_error():
    """Test error handling for undefined environment variables."""
    # Ensure the variable doesn't exist
    if "UNDEFINED_VAR" in os.environ:
        del os.environ["UNDEFINED_VAR"]

    data = {"key": "{env:UNDEFINED_VAR}"}

    with pytest.raises(ValueError, match="Environment variable 'UNDEFINED_VAR' is referenced"):
        _replace_env_vars(data)


def test_replace_env_vars_nested_objects():
    """Test environment variable replacement in deeply nested structures."""
    os.environ["NESTED_VAR"] = "nested_value"

    data = {
        "level1": {
            "level2": {
                "level3": {
                    "value": "{env:NESTED_VAR}",
                    "list": [{"inner": "{env:NESTED_VAR}"}],
                }
            }
        }
    }

    result = _replace_env_vars(data)
    assert result["level1"]["level2"]["level3"]["value"] == "nested_value"
    assert result["level1"]["level2"]["level3"]["list"][0]["inner"] == "nested_value"

    # Cleanup
    del os.environ["NESTED_VAR"]


def test_load_mcp_config_json(tmp_path: Path):
    """Test loading MCP config from JSON file."""
    os.environ["TEST_API_KEY"] = "test_key_123"

    config_file = tmp_path / "mcp.json"
    config_data = {
        "mcpServers": {
            "firecrawl": {
                "command": "npx",
                "args": ["-y", "@firecrawl/mcp-server-firecrawl"],
                "env": {"FIRECRAWL_API_KEY": "{env:TEST_API_KEY}"},
            }
        }
    }

    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    config = load_mcp_config(config_file)

    assert "firecrawl" in config.mcpServers
    assert config.mcpServers["firecrawl"].command == "npx"
    assert config.mcpServers["firecrawl"].args == ["-y", "@firecrawl/mcp-server-firecrawl"]
    assert config.mcpServers["firecrawl"].env["FIRECRAWL_API_KEY"] == "test_key_123"

    # Cleanup
    del os.environ["TEST_API_KEY"]


def test_load_mcp_config_jsonc(tmp_path: Path):
    """Test loading MCP config from JSONC file with comments."""
    os.environ["TEST_KEY"] = "jsonc_value"

    config_file = tmp_path / "config.jsonc"
    config_content = """
    {
        // This is a comment
        "mcpServers": {
            /* Multi-line
               comment */
            "test_server": {
                "command": "test",
                "args": ["arg1"],
                "env": {
                    "KEY": "{env:TEST_KEY}"
                }
            }
        }
    }
    """
    config_file.write_text(config_content, encoding="utf-8")

    config = load_mcp_config(config_file)

    assert "test_server" in config.mcpServers
    assert config.mcpServers["test_server"].command == "test"
    assert config.mcpServers["test_server"].env["KEY"] == "jsonc_value"

    # Cleanup
    del os.environ["TEST_KEY"]


def test_load_mcp_config_file_not_found():
    """Test error handling for missing config file."""
    with pytest.raises(FileNotFoundError, match="MCP config file not found"):
        load_mcp_config(Path("/nonexistent/config.json"))


def test_load_mcp_config_invalid_json(tmp_path: Path):
    """Test error handling for invalid JSON."""
    config_file = tmp_path / "invalid.json"
    config_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_mcp_config(config_file)


def test_mcp_config_model_validation():
    """Test Pydantic model validation for MCPConfig."""
    # Valid config
    config_data = {
        "mcpServers": {"server1": {"command": "cmd", "args": ["arg1"], "env": {"KEY": "value"}}}
    }
    config = MCPConfig.model_validate(config_data)
    assert "server1" in config.mcpServers

    # Empty config (should be valid)
    empty_config = MCPConfig.model_validate({"mcpServers": {}})
    assert len(empty_config.mcpServers) == 0

    # Missing mcpServers (should use default)
    minimal_config = MCPConfig.model_validate({})
    assert len(minimal_config.mcpServers) == 0
