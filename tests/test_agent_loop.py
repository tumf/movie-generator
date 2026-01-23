"""Tests for AgentLoop class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from movie_generator.agent.agent_loop import AgentLoop
from movie_generator.exceptions import MCPError


class TestAgentLoop:
    """Test suite for AgentLoop class."""

    @pytest.fixture
    def mock_mcp_client(self) -> MagicMock:
        """Create a mock MCP client."""
        client = MagicMock()
        client.available_tools = [
            {
                "name": "test_tool",
                "description": "A test tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {"arg1": {"type": "string"}},
                },
            }
        ]
        client.call_tool = AsyncMock(return_value={"result": "success"})
        return client

    @pytest.fixture
    def agent_loop(self, mock_mcp_client: MagicMock) -> AgentLoop:
        """Create an AgentLoop instance with mock client."""
        return AgentLoop(
            mcp_client=mock_mcp_client,
            openrouter_api_key="test_key",
            model="test_model",
            max_iterations=5,
        )

    @pytest.mark.asyncio
    async def test_init(self, mock_mcp_client: MagicMock) -> None:
        """Test AgentLoop initialization."""
        agent = AgentLoop(
            mcp_client=mock_mcp_client,
            openrouter_api_key="my_key",
            model="my_model",
            max_iterations=10,
        )

        assert agent.mcp_client == mock_mcp_client
        assert agent.openrouter_api_key == "my_key"
        assert agent.model == "my_model"
        assert agent.max_iterations == 10

    @pytest.mark.asyncio
    async def test_no_tools_available(self, mock_mcp_client: MagicMock) -> None:
        """Test error when no tools are available."""
        mock_mcp_client.available_tools = []

        agent = AgentLoop(
            mcp_client=mock_mcp_client,
            openrouter_api_key="test_key",
            model="test_model",
        )

        with pytest.raises(MCPError, match="No MCP tools available"):
            await agent.run("test task")

    @pytest.mark.asyncio
    async def test_successful_completion_without_tools(
        self, agent_loop: AgentLoop, mock_mcp_client: MagicMock
    ) -> None:
        """Test successful completion without using tools."""
        # Mock LLM response that finishes immediately
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Task completed successfully",
                    },
                    "finish_reason": "stop",
                }
            ]
        }

        with patch.object(agent_loop, "_call_llm", new=AsyncMock(return_value=mock_response)):
            result = await agent_loop.run("Simple task")
            assert result == "Task completed successfully"
            # Ensure no tools were called
            mock_mcp_client.call_tool.assert_not_called()

    @pytest.mark.asyncio
    async def test_tool_call_execution(
        self, agent_loop: AgentLoop, mock_mcp_client: MagicMock
    ) -> None:
        """Test execution of tool calls."""
        # First response: LLM wants to call a tool
        tool_call_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "test_tool",
                                    "arguments": '{"arg1": "value1"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ]
        }

        # Second response: LLM finishes after tool result
        finish_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Final answer",
                    },
                    "finish_reason": "stop",
                }
            ]
        }

        with patch.object(
            agent_loop,
            "_call_llm",
            new=AsyncMock(side_effect=[tool_call_response, finish_response]),
        ):
            result = await agent_loop.run("Task requiring tool")
            assert result == "Final answer"
            # Verify tool was called
            mock_mcp_client.call_tool.assert_called_once_with("test_tool", {"arg1": "value1"})

    @pytest.mark.asyncio
    async def test_max_iterations_exceeded(
        self, agent_loop: AgentLoop, mock_mcp_client: MagicMock
    ) -> None:
        """Test error when max iterations are exceeded."""
        # Mock LLM to always request tool calls
        tool_call_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "test_tool",
                                    "arguments": '{"arg1": "value1"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ]
        }

        with patch.object(agent_loop, "_call_llm", new=AsyncMock(return_value=tool_call_response)):
            with pytest.raises(MCPError, match="exceeded maximum iterations"):
                await agent_loop.run("Endless task")

    @pytest.mark.asyncio
    async def test_invalid_tool_arguments(
        self, agent_loop: AgentLoop, mock_mcp_client: MagicMock
    ) -> None:
        """Test handling of invalid JSON in tool arguments."""
        tool_call_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "test_tool",
                                    "arguments": "invalid json {",
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ]
        }

        with patch.object(agent_loop, "_call_llm", new=AsyncMock(return_value=tool_call_response)):
            with pytest.raises(MCPError, match="Invalid tool arguments JSON"):
                await agent_loop.run("Task with invalid args")

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_mcp_client: MagicMock) -> None:
        """Test AgentLoop as async context manager."""
        async with AgentLoop(
            mcp_client=mock_mcp_client, openrouter_api_key="test_key", model="test_model"
        ) as agent:
            assert agent.http_client is not None

        # HTTP client should be closed after context exit
        assert agent.http_client.is_closed
