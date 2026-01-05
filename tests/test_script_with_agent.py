"""Integration tests for script generation with MCP agent."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from movie_generator.config import Config
from movie_generator.script.core import (
    generate_script_from_url_with_agent,
    generate_script_from_url_with_agent_sync,
)


class TestScriptWithAgent:
    """Test suite for agent-based script generation."""

    @pytest.fixture
    def mock_mcp_config(self, tmp_path: Path) -> Path:
        """Create a mock MCP config file."""
        config_path = tmp_path / "mcp.jsonc"
        config_content = {
            "mcpServers": {
                "firecrawl": {
                    "command": "npx",
                    "args": ["-y", "@mendable/firecrawl-mcp"],
                    "env": {"FIRECRAWL_API_KEY": "test_key"},
                }
            }
        }
        import json

        config_path.write_text(json.dumps(config_content))
        return config_path

    @pytest.fixture
    def mock_config(self) -> Config:
        """Create a mock Config object."""
        return Config()

    @pytest.mark.asyncio
    async def test_generate_script_with_agent_basic(
        self, tmp_path: Path, mock_mcp_config: Path, mock_config: Config
    ) -> None:
        """Test basic script generation with agent."""
        output_dir = tmp_path / "output"

        # Mock the MCP client and agent
        mock_markdown = "# Test Article\n\nThis is test content."
        mock_script_data = {
            "title": "Generated Video",
            "description": "Test video description",
            "sections": [
                {
                    "title": "Introduction",
                    "narrations": [{"text": "Hello, world!", "reading": "ハロー、ワールド!"}],
                    "slide_prompt": "Introduction slide",
                }
            ],
        }

        with (
            patch("movie_generator.script.core.MCPClient") as mock_mcp_client_class,
            patch("movie_generator.script.core.AgentLoop") as mock_agent_loop_class,
            patch("movie_generator.script.core.generate_script") as mock_generate_script,
        ):
            # Setup mocks
            mock_mcp_instance = MagicMock()
            mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            mock_mcp_instance.__aexit__ = AsyncMock(return_value=None)
            mock_mcp_client_class.return_value = mock_mcp_instance

            mock_agent_instance = MagicMock()
            mock_agent_instance.__aenter__ = AsyncMock(return_value=mock_agent_instance)
            mock_agent_instance.__aexit__ = AsyncMock(return_value=None)
            mock_agent_instance.run = AsyncMock(return_value=mock_markdown)
            mock_agent_loop_class.return_value = mock_agent_instance

            # Mock script generation
            from movie_generator.script.generator import VideoScript

            mock_script = VideoScript.model_validate(mock_script_data)
            mock_generate_script.return_value = mock_script

            # Run test
            script_path = await generate_script_from_url_with_agent(
                url="https://example.com/blog",
                output_dir=output_dir,
                mcp_config_path=mock_mcp_config,
                config=mock_config,
                api_key="test_api_key",
            )

            # Verify results
            assert script_path.exists()
            assert script_path.name == "script.yaml"

            # Verify script content
            with open(script_path, encoding="utf-8") as f:
                saved_script = yaml.safe_load(f)

            assert saved_script["title"] == "Generated Video"
            assert len(saved_script["sections"]) == 1
            assert saved_script["sections"][0]["title"] == "Introduction"

    @pytest.mark.asyncio
    async def test_generate_script_with_agent_custom_filename(
        self, tmp_path: Path, mock_mcp_config: Path, mock_config: Config
    ) -> None:
        """Test script generation with custom filename."""
        output_dir = tmp_path / "output"

        with (
            patch("movie_generator.script.core.MCPClient") as mock_mcp_client_class,
            patch("movie_generator.script.core.AgentLoop") as mock_agent_loop_class,
            patch("movie_generator.script.core.generate_script") as mock_generate_script,
        ):
            # Setup mocks
            mock_mcp_instance = MagicMock()
            mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            mock_mcp_instance.__aexit__ = AsyncMock(return_value=None)
            mock_mcp_client_class.return_value = mock_mcp_instance

            mock_agent_instance = MagicMock()
            mock_agent_instance.__aenter__ = AsyncMock(return_value=mock_agent_instance)
            mock_agent_instance.__aexit__ = AsyncMock(return_value=None)
            mock_agent_instance.run = AsyncMock(return_value="# Content")
            mock_agent_loop_class.return_value = mock_agent_instance

            from movie_generator.script.generator import VideoScript

            mock_script = VideoScript.model_validate(
                {
                    "title": "Test",
                    "description": "",
                    "sections": [{"title": "S1", "narrations": []}],
                }
            )
            mock_generate_script.return_value = mock_script

            # Run test with custom filename
            script_path = await generate_script_from_url_with_agent(
                url="https://example.com/blog",
                output_dir=output_dir,
                mcp_config_path=mock_mcp_config,
                script_filename="custom_script.yaml",
                config=mock_config,
                api_key="test_api_key",
            )

            assert script_path.name == "custom_script.yaml"
            assert script_path.exists()

    def test_generate_script_with_agent_sync(
        self, tmp_path: Path, mock_mcp_config: Path, mock_config: Config
    ) -> None:
        """Test synchronous wrapper for agent-based generation."""
        output_dir = tmp_path / "output"

        with (
            patch("movie_generator.script.core.MCPClient") as mock_mcp_client_class,
            patch("movie_generator.script.core.AgentLoop") as mock_agent_loop_class,
            patch("movie_generator.script.core.generate_script") as mock_generate_script,
        ):
            # Setup mocks
            mock_mcp_instance = MagicMock()
            mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            mock_mcp_instance.__aexit__ = AsyncMock(return_value=None)
            mock_mcp_client_class.return_value = mock_mcp_instance

            mock_agent_instance = MagicMock()
            mock_agent_instance.__aenter__ = AsyncMock(return_value=mock_agent_instance)
            mock_agent_instance.__aexit__ = AsyncMock(return_value=None)
            mock_agent_instance.run = AsyncMock(return_value="# Content")
            mock_agent_loop_class.return_value = mock_agent_instance

            from movie_generator.script.generator import VideoScript

            mock_script = VideoScript.model_validate(
                {
                    "title": "Test",
                    "description": "",
                    "sections": [{"title": "S1", "narrations": []}],
                }
            )
            mock_generate_script.return_value = mock_script

            # Run synchronous version
            script_path = generate_script_from_url_with_agent_sync(
                url="https://example.com/blog",
                output_dir=output_dir,
                mcp_config_path=mock_mcp_config,
                config=mock_config,
                api_key="test_api_key",
            )

            assert script_path.exists()
            assert script_path.name == "script.yaml"

    @pytest.mark.asyncio
    async def test_progress_callback(
        self, tmp_path: Path, mock_mcp_config: Path, mock_config: Config
    ) -> None:
        """Test that progress callback is called during generation."""
        output_dir = tmp_path / "output"
        progress_calls = []

        def progress_callback(current: int, total: int, message: str) -> None:
            progress_calls.append((current, total, message))

        with (
            patch("movie_generator.script.core.MCPClient") as mock_mcp_client_class,
            patch("movie_generator.script.core.AgentLoop") as mock_agent_loop_class,
            patch("movie_generator.script.core.generate_script") as mock_generate_script,
        ):
            # Setup mocks
            mock_mcp_instance = MagicMock()
            mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            mock_mcp_instance.__aexit__ = AsyncMock(return_value=None)
            mock_mcp_client_class.return_value = mock_mcp_instance

            mock_agent_instance = MagicMock()
            mock_agent_instance.__aenter__ = AsyncMock(return_value=mock_agent_instance)
            mock_agent_instance.__aexit__ = AsyncMock(return_value=None)
            mock_agent_instance.run = AsyncMock(return_value="# Content")
            mock_agent_loop_class.return_value = mock_agent_instance

            from movie_generator.script.generator import VideoScript

            mock_script = VideoScript.model_validate(
                {
                    "title": "Test",
                    "description": "",
                    "sections": [{"title": "S1", "narrations": []}],
                }
            )
            mock_generate_script.return_value = mock_script

            # Run with progress callback
            await generate_script_from_url_with_agent(
                url="https://example.com/blog",
                output_dir=output_dir,
                mcp_config_path=mock_mcp_config,
                config=mock_config,
                api_key="test_api_key",
                progress_callback=progress_callback,
            )

            # Verify progress callbacks were called
            assert len(progress_calls) > 0
            assert progress_calls[0][2] == "Loading MCP configuration..."
            assert progress_calls[-1][2] == "Script generation complete"
            assert progress_calls[-1][0] == 100
