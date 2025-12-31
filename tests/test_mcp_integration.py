"""Integration tests for MCP client with real Firecrawl server.

These tests require:
1. FIRECRAWL_API_KEY environment variable
2. npm/npx available in PATH
3. Internet connection

These are marked with @pytest.mark.integration and can be skipped with:
    pytest -m "not integration"
"""

import os
from pathlib import Path

import pytest
from movie_generator.mcp.client import MCPClient, fetch_content_with_mcp
from movie_generator.mcp.config import load_mcp_config


@pytest.fixture
def mcp_config_path():
    """Path to MCP configuration file."""
    return Path("config/mcp-example.jsonc")


@pytest.fixture
def has_firecrawl_api_key():
    """Check if FIRECRAWL_API_KEY is set."""
    return "FIRECRAWL_API_KEY" in os.environ


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_scrape_real_url(mcp_config_path, has_firecrawl_api_key):
    """Test real URL scraping via MCP server.

    This test:
    - Starts real Firecrawl MCP server
    - Scrapes example.com
    - Verifies markdown content is returned
    """
    if not has_firecrawl_api_key:
        pytest.skip("FIRECRAWL_API_KEY not set")

    config = load_mcp_config(mcp_config_path)

    async with MCPClient(config, "firecrawl") as client:
        # Verify server connected and tools are available
        assert len(client.available_tools) > 0
        tool_names = [t.get("name") for t in client.available_tools]
        assert "firecrawl_scrape" in tool_names

        # Scrape a simple URL
        content = await client.scrape_url("https://example.com")

        # Verify content
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Example Domain" in content


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_content_with_mcp_convenience(mcp_config_path, has_firecrawl_api_key):
    """Test convenience function for fetching content."""
    if not has_firecrawl_api_key:
        pytest.skip("FIRECRAWL_API_KEY not set")

    content = await fetch_content_with_mcp("https://example.com", mcp_config_path, "firecrawl")

    assert isinstance(content, str)
    assert len(content) > 0
    assert "Example Domain" in content
