"""Project management utilities for movie generator.

Handles project creation, asset management, and Remotion integration.
"""

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from .config import Config


class Project:
    """Represents a single video project."""

    def __init__(self, name: str, root_dir: Path | None = None):
        """Initialize project.

        Args:
            name: Project name (directory name).
            root_dir: Root directory containing all projects (defaults to ./projects).
        """
        self.name = name
        self.root_dir = root_dir or Path.cwd() / "projects"
        self.project_dir = self.root_dir / name
        self.assets_dir = self.project_dir / "assets"
        self.audio_dir = self.assets_dir / "audio"
        self.slides_dir = self.assets_dir / "slides"
        self.output_dir = self.project_dir / "output"
        self.config_file = self.project_dir / "project.yaml"
        self.phrases_file = self.project_dir / "phrases.json"
        self.script_file = self.project_dir / "script.md"

    @property
    def exists(self) -> bool:
        """Check if project directory exists."""
        return self.project_dir.exists()

    def create(self, config: Config | None = None) -> None:
        """Create project directory structure.

        Args:
            config: Project configuration. If None, uses defaults.

        Raises:
            FileExistsError: If project already exists.
        """
        if self.exists:
            raise FileExistsError(f"Project already exists: {self.project_dir}")

        # Create directory structure
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)
        self.slides_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Write configuration
        if config:
            self.save_config(config)
        else:
            # Create default config
            default_config = Config()
            self.save_config(default_config)

        # Create empty script file
        self.script_file.write_text("# Video Script\n\n", encoding="utf-8")

    def load_config(self) -> Config:
        """Load project configuration.

        Returns:
            Project configuration.

        Raises:
            FileNotFoundError: If project doesn't exist.
        """
        if not self.config_file.exists():
            raise FileNotFoundError(f"Project config not found: {self.config_file}")

        with self.config_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return Config(**data)

    def save_config(self, config: Config) -> None:
        """Save project configuration.

        Args:
            config: Configuration to save.
        """
        config_dict = config.model_dump()
        with self.config_file.open("w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, allow_unicode=True, sort_keys=False)

    def load_phrases(self) -> list[dict[str, Any]]:
        """Load phrases data.

        Returns:
            List of phrase dictionaries.

        Raises:
            FileNotFoundError: If phrases file doesn't exist.
        """
        if not self.phrases_file.exists():
            raise FileNotFoundError(f"Phrases file not found: {self.phrases_file}")

        with self.phrases_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_phrases(self, phrases: list[dict[str, Any]]) -> None:
        """Save phrases data.

        Args:
            phrases: List of phrase dictionaries.
        """
        with self.phrases_file.open("w", encoding="utf-8") as f:
            json.dump(phrases, f, ensure_ascii=False, indent=2)

    def copy_to_remotion(self, remotion_dir: Path | None = None) -> None:
        """Copy project assets to Remotion public directory.

        Args:
            remotion_dir: Remotion project directory (defaults to ./artifacts/remotion).
        """
        if remotion_dir is None:
            remotion_dir = Path.cwd() / "artifacts" / "remotion"

        remotion_public = remotion_dir / "public" / "projects" / self.name

        # Create directories
        remotion_public.mkdir(parents=True, exist_ok=True)
        (remotion_public / "audio").mkdir(exist_ok=True)
        (remotion_public / "slides").mkdir(exist_ok=True)

        # Copy audio files
        if self.audio_dir.exists():
            for audio_file in self.audio_dir.glob("*.wav"):
                shutil.copy2(audio_file, remotion_public / "audio" / audio_file.name)

        # Copy slide files
        if self.slides_dir.exists():
            for slide_file in self.slides_dir.glob("*.png"):
                shutil.copy2(slide_file, remotion_public / "slides" / slide_file.name)

        # Copy phrases metadata
        if self.phrases_file.exists():
            shutil.copy2(self.phrases_file, remotion_public / "metadata.json")


def list_projects(root_dir: Path | None = None) -> list[Project]:
    """List all projects.

    Args:
        root_dir: Root directory containing projects (defaults to ./projects).

    Returns:
        List of Project objects.
    """
    if root_dir is None:
        root_dir = Path.cwd() / "projects"

    if not root_dir.exists():
        return []

    projects = []
    for project_dir in root_dir.iterdir():
        if project_dir.is_dir() and (project_dir / "project.yaml").exists():
            projects.append(Project(project_dir.name, root_dir))

    return projects


def create_project(
    name: str, config: Config | None = None, root_dir: Path | None = None
) -> Project:
    """Create a new project.

    Args:
        name: Project name.
        config: Project configuration. If None, uses defaults.
        root_dir: Root directory for projects (defaults to ./projects).

    Returns:
        Created Project object.

    Raises:
        FileExistsError: If project already exists.
    """
    project = Project(name, root_dir)
    project.create(config)
    return project
