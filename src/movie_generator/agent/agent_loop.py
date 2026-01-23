"""Agent loop for LLM-driven tool execution via MCP.

This module implements a simple agent loop where an LLM can autonomously
select and execute MCP tools through OpenRouter's function calling API.
"""

import json
import logging
from typing import Any

import httpx

from ..exceptions import MCPError
from ..mcp.client import MCPClient
from .tool_converter import convert_mcp_tools_to_openai

logger = logging.getLogger(__name__)


class AgentLoop:
    """Agent loop for LLM-driven MCP tool execution.

    This class manages the interaction between an LLM (via OpenRouter) and
    MCP tools. The LLM can autonomously select and execute tools to accomplish
    a given task.
    """

    def __init__(
        self,
        mcp_client: MCPClient,
        openrouter_api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
        max_iterations: int = 10,
    ):
        """Initialize agent loop.

        Args:
            mcp_client: Connected MCP client with available tools.
            openrouter_api_key: OpenRouter API key for LLM access.
            model: OpenRouter model identifier (default: gpt-4-turbo-preview).
            base_url: API base URL (default: https://openrouter.ai/api/v1).
            max_iterations: Maximum number of tool call iterations (default: 10).
        """
        self.mcp_client = mcp_client
        self.openrouter_api_key = openrouter_api_key
        self.model = model
        self.base_url = base_url
        self.max_iterations = max_iterations
        self.http_client = httpx.AsyncClient()

    async def run(self, task_prompt: str) -> str:
        """Run the agent loop to accomplish a task.

        Args:
            task_prompt: Natural language description of the task.

        Returns:
            Final response from the LLM after completing the task.

        Raises:
            MCPError: If agent loop fails or exceeds max iterations.
        """
        # Convert MCP tools to OpenAI format
        openai_tools = convert_mcp_tools_to_openai(self.mcp_client.available_tools)

        if not openai_tools:
            raise MCPError("No MCP tools available for agent execution")

        logger.info(f"Starting agent loop with {len(openai_tools)} available tools")

        # Initialize message history
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that can use tools to accomplish tasks. "
                    "Use the available tools to fetch and analyze web content as needed. "
                    "Be thorough and provide comprehensive information."
                ),
            },
            {"role": "user", "content": task_prompt},
        ]

        # Agent loop
        for iteration in range(self.max_iterations):
            logger.debug(f"Agent iteration {iteration + 1}/{self.max_iterations}")

            # Call LLM with tools
            response = await self._call_llm(messages, openai_tools)

            # Extract response message
            response_message = response.get("choices", [{}])[0].get("message")
            if not response_message:
                raise MCPError("Invalid LLM response: missing message")

            # Add assistant's response to message history
            messages.append(response_message)

            # Check finish reason
            finish_reason = response.get("choices", [{}])[0].get("finish_reason")

            if finish_reason == "stop":
                # LLM finished - return final content
                final_content = response_message.get("content", "")
                logger.info("Agent loop completed successfully")
                return final_content

            elif finish_reason == "tool_calls":
                # LLM wants to call tools
                tool_calls = response_message.get("tool_calls", [])

                if not tool_calls:
                    raise MCPError("finish_reason is 'tool_calls' but no tool_calls present")

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_result = await self._execute_tool_call(tool_call)

                    # Add tool result to message history
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.get("id", ""),
                            "content": json.dumps(tool_result),
                        }
                    )

            else:
                # Unexpected finish reason
                logger.warning(f"Unexpected finish_reason: {finish_reason}")
                raise MCPError(f"Unexpected finish_reason: {finish_reason}")

        # Max iterations reached
        raise MCPError(f"Agent loop exceeded maximum iterations ({self.max_iterations})")

    async def _call_llm(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call OpenRouter LLM with function calling support.

        Args:
            messages: Message history.
            tools: Available tools in OpenAI format.

        Returns:
            LLM response as dictionary.

        Raises:
            MCPError: If LLM call fails.
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }

        try:
            response = await self.http_client.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise MCPError(
                f"OpenRouter API error: {e.response.status_code} - {error_detail}"
            ) from e
        except Exception as e:
            raise MCPError(f"Failed to call OpenRouter LLM: {e}") from e

    async def _execute_tool_call(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        """Execute a single tool call via MCP.

        Args:
            tool_call: Tool call object from LLM response.

        Returns:
            Tool execution result.

        Raises:
            MCPError: If tool execution fails.
        """
        function = tool_call.get("function", {})
        tool_name = function.get("name", "")
        arguments_str = function.get("arguments", "{}")

        logger.info(f"Executing tool: {tool_name}")

        try:
            # Parse arguments
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid tool arguments JSON: {arguments_str}") from e

        # Call MCP tool
        try:
            result = await self.mcp_client.call_tool(tool_name, arguments)
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            error_msg = f"Tool execution failed: {e}"
            logger.error(error_msg)
            # Return error as tool result so LLM can handle it
            return {"error": error_msg}

    async def close(self) -> None:
        """Close HTTP client resources."""
        await self.http_client.aclose()

    async def __aenter__(self) -> "AgentLoop":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()
