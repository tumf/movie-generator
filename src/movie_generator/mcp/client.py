"""MCP client for communicating with MCP servers.

Provides a client to connect to and interact with MCP servers like Firecrawl.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

from .config import MCPConfig, MCPServerConfig


class MCPClient:
    """Client for communicating with MCP servers.

    Manages connection to MCP servers and provides methods to call their tools.
    """

    def __init__(self, config: MCPConfig, server_name: str = "firecrawl"):
        """Initialize MCP client.

        Args:
            config: MCP configuration containing server definitions.
            server_name: Name of the server to use (default: "firecrawl").

        Raises:
            ValueError: If specified server is not found in config.
        """
        if server_name not in config.mcpServers:
            raise ValueError(
                f"Server '{server_name}' not found in MCP config. "
                f"Available servers: {list(config.mcpServers.keys())}"
            )

        self.config = config
        self.server_name = server_name
        self.server_config: MCPServerConfig = config.mcpServers[server_name]
        self.process: subprocess.Popen[bytes] | None = None

    async def connect(self) -> None:
        """Connect to the MCP server.

        Starts the MCP server process and establishes communication.

        Raises:
            RuntimeError: If server process fails to start.
        """
        # Start the MCP server process
        env = {**self.server_config.env}

        try:
            self.process = subprocess.Popen(
                [self.server_config.command, *self.server_config.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**env},
            )

            # Wait briefly to ensure process started successfully
            await asyncio.sleep(0.5)

            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                raise RuntimeError(f"MCP server process failed to start: {stderr}")

        except FileNotFoundError as e:
            raise RuntimeError(f"MCP server command not found: {self.server_config.command}") from e

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any], timeout: float = 30.0
    ) -> dict[str, Any]:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call (e.g., "firecrawl_scrape").
            arguments: Tool arguments as a dictionary.
            timeout: Timeout in seconds (default: 30.0).

        Returns:
            Tool response as a dictionary.

        Raises:
            RuntimeError: If not connected or tool call fails.
            asyncio.TimeoutError: If tool call times out.
        """
        if self.process is None or self.process.poll() is not None:
            raise RuntimeError("Not connected to MCP server")

        # Prepare JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        # Send request
        request_json = json.dumps(request) + "\n"
        if self.process.stdin:
            self.process.stdin.write(request_json.encode())
            self.process.stdin.flush()

        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(self._read_response_line(), timeout=timeout)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"MCP tool call '{tool_name}' timed out after {timeout}s")

        # Parse response
        try:
            response = json.loads(response_line)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from MCP server: {response_line}") from e

        # Check for errors
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"MCP tool call failed: {error.get('message', error)}")

        return response.get("result", {})

    async def _read_response_line(self) -> str:
        """Read a single line from the server's stdout.

        Returns:
            Response line as string.

        Raises:
            RuntimeError: If process is not available.
        """
        if self.process is None or self.process.stdout is None:
            raise RuntimeError("Process stdout not available")

        # Read line asynchronously
        loop = asyncio.get_event_loop()
        line = await loop.run_in_executor(None, self.process.stdout.readline)
        return line.decode().strip()

    async def scrape_url(self, url: str, formats: list[str] | None = None) -> str:
        """Scrape a URL using Firecrawl MCP tool.

        Args:
            url: URL to scrape.
            formats: List of formats to return (default: ["markdown"]).

        Returns:
            Scraped content as markdown text.

        Raises:
            RuntimeError: If scraping fails.
        """
        if formats is None:
            formats = ["markdown"]

        result = await self.call_tool(
            "firecrawl_firecrawl_scrape", {"url": url, "formats": formats}
        )

        # Extract markdown content from result
        if "data" in result and "markdown" in result["data"]:
            return result["data"]["markdown"]
        elif "markdown" in result:
            return result["markdown"]
        else:
            raise RuntimeError(f"Unexpected response format from Firecrawl: {result}")

    async def close(self) -> None:
        """Close connection to MCP server.

        Terminates the server process gracefully.
        """
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception:
                pass
            finally:
                self.process = None

    async def __aenter__(self) -> "MCPClient":
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()


async def fetch_content_with_mcp(
    url: str, config_path: Path, server_name: str = "firecrawl"
) -> str:
    """Fetch content from URL using MCP server.

    Convenience function to fetch content using MCP without manually
    managing client lifecycle.

    Args:
        url: URL to fetch content from.
        config_path: Path to MCP configuration file.
        server_name: Name of MCP server to use (default: "firecrawl").

    Returns:
        Fetched content as markdown text.

    Raises:
        FileNotFoundError: If config file not found.
        RuntimeError: If MCP operation fails.
    """
    from .config import load_mcp_config

    config = load_mcp_config(config_path)

    async with MCPClient(config, server_name) as client:
        return await client.scrape_url(url)
