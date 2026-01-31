"""Tests for project root resolution logic."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.constants import ProjectPaths


class TestProjectRootResolution:
    """Test PROJECT_ROOT environment resolution."""

    def test_get_project_root_docker_env(self):
        """Test get_project_root returns PROJECT_ROOT in Docker environment."""
        with patch.dict(os.environ, {"DOCKER_ENV": "1", "PROJECT_ROOT": "/custom/path"}):
            result = ProjectPaths.get_project_root()
            assert result == Path("/custom/path")

    def test_get_project_root_docker_env_default(self):
        """Test get_project_root returns /app by default in Docker."""
        env = {"DOCKER_ENV": "1"}
        if "PROJECT_ROOT" in os.environ:
            # Ensure PROJECT_ROOT is not set
            with patch.dict(os.environ, env, clear=True):
                result = ProjectPaths.get_project_root()
                assert result == Path("/app")
        else:
            with patch.dict(os.environ, env):
                result = ProjectPaths.get_project_root()
                assert result == Path("/app")

    def test_get_project_root_local_env(self):
        """Test get_project_root returns cwd in local environment."""
        env = {}
        if "DOCKER_ENV" in os.environ:
            # Ensure DOCKER_ENV is not set
            with patch.dict(os.environ, env, clear=True):
                result = ProjectPaths.get_project_root()
                assert result == Path.cwd()
        else:
            with patch.dict(os.environ, env):
                result = ProjectPaths.get_project_root()
                assert result == Path.cwd()

    def test_get_docker_project_root_custom(self):
        """Test get_docker_project_root with custom PROJECT_ROOT."""
        with patch.dict(os.environ, {"PROJECT_ROOT": "/my/custom/root"}):
            result = ProjectPaths.get_docker_project_root()
            assert result == Path("/my/custom/root")

    def test_get_docker_project_root_default(self):
        """Test get_docker_project_root returns /app by default."""
        env = {}
        if "PROJECT_ROOT" in os.environ:
            # Ensure PROJECT_ROOT is not set
            with patch.dict(os.environ, env, clear=True):
                result = ProjectPaths.get_docker_project_root()
                assert result == Path("/app")
        else:
            with patch.dict(os.environ, env):
                result = ProjectPaths.get_docker_project_root()
                assert result == Path("/app")
