"""Tests for worker configuration and MCP agent integration."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestWorkerConfig:
    """Test worker configuration."""

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        # Import inside test to avoid polluting global scope
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "worker"))

        from main import Config

        config = Config()
        assert config.pocketbase_url == "http://localhost:8090"
        assert config.max_concurrent_jobs == 2
        assert config.worker_poll_interval == 5
        assert config.config_path is None
        assert config.mcp_config_path is None

    def test_config_from_env(self) -> None:
        """Test configuration from environment variables."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "worker"))

        env_vars = {
            "POCKETBASE_URL": "http://test:8090",
            "MAX_CONCURRENT_JOBS": "5",
            "WORKER_POLL_INTERVAL": "10",
            "JOB_DATA_DIR": "/test/data",
            "CONFIG_PATH": "/test/config.yaml",
            "MCP_CONFIG_PATH": "/test/mcp.jsonc",
        }

        with patch.dict(os.environ, env_vars):
            from main import Config

            config = Config()
            assert config.pocketbase_url == "http://test:8090"
            assert config.max_concurrent_jobs == 5
            assert config.worker_poll_interval == 10
            assert config.job_data_dir == Path("/test/data")
            assert config.config_path == Path("/test/config.yaml")
            assert config.mcp_config_path == Path("/test/mcp.jsonc")

    def test_config_mcp_optional(self) -> None:
        """Test that MCP config is optional."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "worker"))

        env_vars = {
            "CONFIG_PATH": "/test/config.yaml",
            # MCP_CONFIG_PATH not set
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from main import Config

            config = Config()
            assert config.config_path == Path("/test/config.yaml")
            assert config.mcp_config_path is None
