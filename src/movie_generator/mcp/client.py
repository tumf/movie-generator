"""MCP client for communicating with MCP servers.

Provides a client to connect to and interact with MCP servers like Firecrawl.
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from .config import MCPConfig, MCPServerConfig

logger = logging.getLogger(__name__)


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
        self.available_tools: list[dict[str, Any]] = []
        self._request_id = 0

    async def connect(self) -> None:
        """Connect to the MCP server.

        Starts the MCP server process and establishes communication.

        Raises:
            RuntimeError: If server process fails to start.
        """
        # Start the MCP server process
        # Inherit parent environment (including PATH) and override with config env
        env = {**os.environ, **self.server_config.env}

        try:
            logger.info(
                f"Starting MCP server: {self.server_config.command} "
                f"{' '.join(self.server_config.args)}"
            )
            self.process = subprocess.Popen(
                [self.server_config.command, *self.server_config.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Wait briefly to ensure process started successfully
            await asyncio.sleep(0.5)

            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                raise RuntimeError(f"MCP server process failed to start: {stderr}")

            # Initialize MCP protocol handshake
            await self._initialize()

            # List available tools
            await self._list_tools()

        except FileNotFoundError as e:
            raise RuntimeError(f"MCP server command not found: {self.server_config.command}") from e

    async def _initialize(self) -> None:
        """Initialize MCP protocol handshake.

        Sends an initialize request to establish the protocol version.
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "movie-generator", "version": "1.0.0"},
            },
        }

        logger.debug(f"Sending initialize request: {request}")
        response = await self._send_request(request)
        logger.info(f"MCP server initialized: {response.get('result', {}).get('serverInfo', {})}")

    async def _list_tools(self) -> None:
        """List available tools from the MCP server.

        Populates self.available_tools with the list of available tools.
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/list",
            "params": {},
        }

        logger.debug("Requesting tools/list")
        response = await self._send_request(request)

        result = response.get("result", {})
        self.available_tools = result.get("tools", [])

        logger.info(f"Available MCP tools: {[t.get('name') for t in self.available_tools]}")

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    async def _send_request(self, request: dict[str, Any], timeout: float = 30.0) -> dict[str, Any]:
        """Send a JSON-RPC request and get response.

        Args:
            request: JSON-RPC request object.
            timeout: Timeout in seconds.

        Returns:
            JSON-RPC response object.

        Raises:
            RuntimeError: If not connected or request fails.
        """
        if self.process is None or self.process.poll() is not None:
            raise RuntimeError("Not connected to MCP server")

        # Send request
        request_json = json.dumps(request) + "\n"
        if self.process.stdin:
            self.process.stdin.write(request_json.encode())
            self.process.stdin.flush()

        request_id = request.get("id")

        # Read responses until we get the matching response
        # (MCP servers may send notifications before the actual response)
        start_time = asyncio.get_event_loop().time()
        while True:
            remaining_timeout = timeout - (asyncio.get_event_loop().time() - start_time)
            if remaining_timeout <= 0:
                raise TimeoutError(
                    f"MCP request '{request.get('method')}' timed out after {timeout}s"
                )

            try:
                response_line = await asyncio.wait_for(
                    self._read_response_line(), timeout=remaining_timeout
                )
            except TimeoutError:
                raise TimeoutError(
                    f"MCP request '{request.get('method')}' timed out after {timeout}s"
                )

            # Parse response
            try:
                response = json.loads(response_line)
                logger.debug(f"Received message: {response}")
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON response from MCP server: {response_line}") from e

            # Check if this is a notification (no id field) - skip it
            if "method" in response and "id" not in response:
                logger.debug(f"Skipping notification: {response.get('method')}")
                continue

            # Check if this is the response we're waiting for
            if response.get("id") == request_id:
                # Check for errors
                if "error" in response:
                    error = response["error"]
                    error_msg = error.get("message", str(error))
                    error_code = error.get("code", "unknown")
                    raise RuntimeError(f"MCP error {error_code}: {error_msg}")

                return response  # type: ignore[no-any-return]

            # If we got a different response, something is wrong
            logger.warning(
                f"Received unexpected response with id={response.get('id')}, expected {request_id}"
            )
            continue

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any], timeout: float = 30.0
    ) -> dict[str, Any]:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call (e.g., "scrape").
            arguments: Tool arguments as a dictionary.
            timeout: Timeout in seconds (default: 30.0).

        Returns:
            Tool response as a dictionary.

        Raises:
            RuntimeError: If not connected or tool call fails.
            asyncio.TimeoutError: If tool call times out.
        """
        # Verify tool exists
        tool_names = [t.get("name") for t in self.available_tools]
        if tool_name not in tool_names:
            raise RuntimeError(f"Tool '{tool_name}' not found. Available tools: {tool_names}")

        # Prepare JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        logger.debug(f"Calling tool '{tool_name}' with args: {arguments}")
        response = await self._send_request(request, timeout=timeout)

        result = response.get("result", {})
        logger.debug(f"Tool '{tool_name}' returned: {result}")

        return result  # type: ignore[no-any-return]

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

        # Try to find the correct scrape tool name
        scrape_tool = None
        for tool in self.available_tools:
            tool_name = tool.get("name", "")
            if "scrape" in tool_name.lower():
                scrape_tool = tool_name
                logger.info(f"Using scrape tool: {scrape_tool}")
                break

        if not scrape_tool:
            raise RuntimeError(
                f"No scrape tool found. Available tools: "
                f"{[t.get('name') for t in self.available_tools]}"
            )

        result = await self.call_tool(scrape_tool, {"url": url, "formats": formats})

        # Extract markdown content from result
        # The structure varies by MCP server implementation
        if "content" in result:
            # Standard MCP response format
            content_list = result["content"]
            for item in content_list:
                if item.get("type") == "text":
                    text_content = item.get("text", "")
                    if text_content:
                        # The text content might be a JSON string, try to parse it
                        try:
                            parsed = json.loads(text_content)
                            if isinstance(parsed, dict) and "markdown" in parsed:
                                markdown = parsed["markdown"]
                                if isinstance(markdown, str):
                                    return markdown
                        except (json.JSONDecodeError, ValueError):
                            # Not JSON, return as is
                            pass
                        if isinstance(text_content, str):
                            return text_content

        if "data" in result:
            data = result["data"]
            if isinstance(data, dict) and "markdown" in data:
                markdown = data["markdown"]
                if isinstance(markdown, str):
                    return markdown
        elif "markdown" in result:
            markdown = result["markdown"]
            if isinstance(markdown, str):
                return markdown

        logger.warning(f"Unexpected response format: {result}")
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
