"""End-to-end tests for script generation with MCP integration."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from movie_generator.mcp import fetch_content_with_mcp


@pytest.fixture
def sample_mcp_config(tmp_path: Path):
    """Create a sample MCP config file."""
    config_data = {
        "mcpServers": {
            "firecrawl": {
                "command": "npx",
                "args": ["-y", "@firecrawl/mcp-server-firecrawl"],
                "env": {"FIRECRAWL_API_KEY": "test_key"},
            }
        }
    }

    config_file = tmp_path / "mcp.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")
    return config_file


@pytest.mark.asyncio
async def test_fetch_content_with_mcp_success(sample_mcp_config):
    """Test fetching content using MCP (mocked)."""
    expected_content = "# Test Article\n\nThis is test content from MCP."

    # Mock the MCPClient
    with patch("movie_generator.mcp.client.MCPClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.scrape_url.return_value = expected_content
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        result = await fetch_content_with_mcp("https://example.com", sample_mcp_config)

        assert result == expected_content
        mock_client.scrape_url.assert_called_once_with("https://example.com")


@pytest.mark.asyncio
async def test_fetch_content_with_mcp_file_not_found():
    """Test error handling when config file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        await fetch_content_with_mcp("https://example.com", Path("/nonexistent/config.json"))


@pytest.mark.asyncio
async def test_fetch_content_with_mcp_server_error(sample_mcp_config):
    """Test handling of MCP server errors."""
    # Mock the MCPClient to raise an error
    with patch("movie_generator.mcp.client.MCPClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.scrape_url.side_effect = RuntimeError("MCP server error")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        with pytest.raises(RuntimeError, match="MCP server error"):
            await fetch_content_with_mcp("https://example.com", sample_mcp_config)


@pytest.mark.asyncio
async def test_mcp_integration_with_custom_server(tmp_path: Path):
    """Test using a custom MCP server (not firecrawl)."""
    # Create config with custom server
    config_data = {
        "mcpServers": {
            "custom": {
                "command": "custom-mcp",
                "args": ["--arg1"],
                "env": {"API_KEY": "custom_key"},
            }
        }
    }

    config_file = tmp_path / "custom.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    with patch("movie_generator.mcp.client.MCPClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.scrape_url.return_value = "Custom content"
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        result = await fetch_content_with_mcp(
            "https://example.com", config_file, server_name="custom"
        )

        assert result == "Custom content"
