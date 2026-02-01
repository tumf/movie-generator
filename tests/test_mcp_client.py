"""Tests for MCP client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from movie_generator.exceptions import ConfigurationError, MCPError
from movie_generator.mcp.client import MCPClient
from movie_generator.mcp.config import MCPConfig, MCPServerConfig


@pytest.fixture
def mock_config():
    """Create a mock MCP configuration."""
    return MCPConfig(
        mcpServers={
            "firecrawl": MCPServerConfig(
                command="npx",
                args=["-y", "@firecrawl/mcp-server-firecrawl"],
                env={"FIRECRAWL_API_KEY": "test_key"},
            ),
            "another": MCPServerConfig(command="other", args=[], env={}),
        }
    )


def test_mcp_client_init_success(mock_config):
    """Test MCPClient initialization with valid server."""
    client = MCPClient(mock_config, "firecrawl")

    assert client.server_name == "firecrawl"
    assert client.server_config.command == "npx"
    assert client.process is None


def test_mcp_client_init_invalid_server(mock_config):
    """Test MCPClient initialization with invalid server name."""
    with pytest.raises(ConfigurationError, match="Server 'nonexistent' not found"):
        MCPClient(mock_config, "nonexistent")


@pytest.mark.asyncio
async def test_mcp_client_connect_failure(mock_config):
    """Test connection failure handling."""
    client = MCPClient(mock_config, "firecrawl")

    with patch("subprocess.Popen") as mock_popen:
        # Simulate process that exits immediately
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited
        mock_process.stderr.read.return_value = b"Error message"
        mock_popen.return_value = mock_process

        with pytest.raises(MCPError, match="MCP server process failed to start"):
            await client.connect()


@pytest.mark.asyncio
async def test_mcp_client_connect_command_not_found(mock_config):
    """Test handling when MCP server command is not found."""
    client = MCPClient(mock_config, "firecrawl")

    with patch("subprocess.Popen", side_effect=FileNotFoundError()):
        with pytest.raises(MCPError, match="MCP server command not found"):
            await client.connect()


@pytest.mark.asyncio
async def test_mcp_client_call_tool_not_connected(mock_config):
    """Test calling tool when not connected (tool not found)."""
    client = MCPClient(mock_config, "firecrawl")

    # With no tools available, should raise error about tool not found
    with pytest.raises(RuntimeError, match="Tool 'test_tool' not found"):
        await client.call_tool("test_tool", {})


@pytest.mark.asyncio
async def test_mcp_client_call_tool_timeout(mock_config):
    """Test tool call timeout."""
    client = MCPClient(mock_config, "firecrawl")

    # Mock a connected process
    mock_process = MagicMock()
    mock_process.poll.return_value = None  # Still running
    mock_process.stdin = MagicMock()
    client.process = mock_process

    # Add a fake tool to available_tools
    client.available_tools = [{"name": "test_tool"}]

    # Mock readline to never return (simulating timeout)
    with patch.object(client, "_read_response_line", side_effect=TimeoutError()):
        with pytest.raises(asyncio.TimeoutError, match="timed out"):
            await client.call_tool("test_tool", {}, timeout=0.1)


@pytest.mark.asyncio
async def test_mcp_client_scrape_url_success(mock_config):
    """Test successful URL scraping via MCP."""
    client = MCPClient(mock_config, "firecrawl")

    # Mock process
    mock_process = MagicMock()
    mock_process.poll.return_value = None
    mock_process.stdin = MagicMock()
    client.process = mock_process

    # Add firecrawl_scrape to available tools
    client.available_tools = [{"name": "firecrawl_scrape"}]

    # Mock successful response in MCP format
    markdown_content = "# Test Content\n\nThis is test content."
    import json as json_module

    response_data = {
        "content": [
            {
                "type": "text",
                "text": json_module.dumps({"markdown": markdown_content}),
            }
        ]
    }

    # Mock call_tool to return the response
    async def mock_call_tool(tool_name, arguments, timeout=30.0):
        return response_data

    with patch.object(client, "call_tool", side_effect=mock_call_tool):
        result = await client.scrape_url("https://example.com")
        assert result == markdown_content


@pytest.mark.asyncio
async def test_mcp_client_close(mock_config):
    """Test closing MCP client connection."""
    client = MCPClient(mock_config, "firecrawl")

    # Mock process
    mock_process = MagicMock()
    mock_process.poll.return_value = None
    client.process = mock_process

    await client.close()

    # Verify terminate was called
    mock_process.terminate.assert_called_once()
    assert client.process is None


@pytest.mark.asyncio
async def test_mcp_client_context_manager(mock_config):
    """Test MCPClient as async context manager."""
    client = MCPClient(mock_config, "firecrawl")

    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process running
        mock_popen.return_value = mock_process

        # Mock _initialize and _list_tools to avoid actual JSON-RPC calls
        with patch.object(client, "_initialize", new_callable=AsyncMock):
            with patch.object(client, "_list_tools", new_callable=AsyncMock):
                async with client:
                    assert client.process is not None

                # Verify process was terminated
                mock_process.terminate.assert_called()
