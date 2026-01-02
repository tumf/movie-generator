"""Project management utilities for movie generator.

Handles project creation, asset management, and Remotion integration.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from .config import Config
from .script.phrases import Phrase

console = Console()


def _ensure_pnpm_available() -> None:
    """Check if pnpm is available on the system.

    Raises:
        RuntimeError: If pnpm is not available with installation instructions.
    """
    try:
        subprocess.run(
            ["pnpm", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "pnpm is not installed or not available in PATH.\n\n"
            "Please install pnpm:\n"
            "  npm install -g pnpm\n\n"
            "Or visit: https://pnpm.io/installation"
        )


def _ensure_nodejs_available() -> None:
    """Check if Node.js is available on the system.

    Raises:
        RuntimeError: If Node.js is not available with installation instructions.
    """
    try:
        subprocess.run(
            ["node", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "Node.js is not installed or not available in PATH.\n\n"
            "Please install Node.js 18+ from: https://nodejs.org/"
        )


def _create_symlink_safe(target: Path, link: Path) -> None:
    """Create a symbolic link, removing existing link if present.

    Args:
        target: Target path (what the symlink points to).
        link: Link path (the symlink itself).
    """
    # Remove existing link if present
    if link.exists() or link.is_symlink():
        if link.is_symlink():
            link.unlink()
        elif link.is_dir():
            shutil.rmtree(link)
        else:
            link.unlink()

    # Create parent directory if needed
    link.parent.mkdir(parents=True, exist_ok=True)

    # Ensure target directory exists (create if not)
    target.mkdir(parents=True, exist_ok=True)

    # Create symlink (relative path for portability)
    try:
        link.symlink_to(os.path.relpath(target, link.parent), target_is_directory=True)
    except OSError:
        # Fallback to absolute path on Windows if relative fails
        console.print(
            "[yellow]Warning: Could not create relative symlink, using absolute path[/yellow]"
        )
        link.symlink_to(target.absolute(), target_is_directory=True)


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
        self.logos_dir = self.assets_dir / "logos"
        self.characters_dir = self.assets_dir / "characters"
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
        self.logos_dir.mkdir(exist_ok=True)
        self.characters_dir.mkdir(exist_ok=True)
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

        def convert_tuples(obj: Any) -> Any:
            """Recursively convert tuples to lists for YAML serialization."""
            if isinstance(obj, dict):
                return {k: convert_tuples(v) for k, v in obj.items()}
            elif isinstance(obj, tuple):
                return list(obj)
            elif isinstance(obj, list):
                return [convert_tuples(item) for item in obj]
            else:
                return obj

        config_dict = convert_tuples(config.model_dump())
        with self.config_file.open("w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, allow_unicode=True, sort_keys=False)

    def load_phrases(self) -> list[Phrase]:
        """Load phrases data.

        Returns:
            List of Phrase objects.

        Raises:
            FileNotFoundError: If phrases file doesn't exist.
        """
        if not self.phrases_file.exists():
            raise FileNotFoundError(f"Phrases file not found: {self.phrases_file}")

        with self.phrases_file.open("r", encoding="utf-8") as f:
            phrases_data = json.load(f)
            return [Phrase.model_validate(p) for p in phrases_data]

    def save_phrases(self, phrases: list[Phrase]) -> None:
        """Save phrases data.

        Args:
            phrases: List of Phrase objects.
        """
        with self.phrases_file.open("w", encoding="utf-8") as f:
            phrases_data = [p.model_dump() for p in phrases]
            json.dump(phrases_data, f, ensure_ascii=False, indent=2)

    def copy_character_assets(self, source_root: Path | None = None) -> None:
        """Copy character assets from source to project assets directory.

        Args:
            source_root: Root directory containing assets/ folder.
                        Defaults to current working directory.
        """
        if source_root is None:
            source_root = Path.cwd()

        source_characters = source_root / "assets" / "characters"
        if not source_characters.exists():
            return

        # Copy all character directories
        for character_dir in source_characters.iterdir():
            if character_dir.is_dir():
                dest_dir = self.characters_dir / character_dir.name
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Copy all PNG files
                for png_file in character_dir.glob("*.png"):
                    dest_file = dest_dir / png_file.name
                    if not dest_file.exists():
                        shutil.copy2(png_file, dest_file)

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

    def setup_remotion_project(self) -> Path:
        """Setup per-project Remotion instance.

        Creates a dedicated Remotion project for this video project with:
        - pnpm create @remotion/video initialization
        - Dynamic TypeScript component generation
        - composition.json for phrase data
        - Symbolic links to audio/slides assets

        Returns:
            Path to the created Remotion project directory.

        Raises:
            RuntimeError: If pnpm or Node.js is not available.
            subprocess.CalledProcessError: If Remotion initialization fails.
        """
        # Import here to avoid circular dependency
        from . import video

        remotion_dir = self.project_dir / "remotion"

        # Check if already initialized
        if remotion_dir.exists() and (remotion_dir / "package.json").exists():
            console.print(f"[yellow]Remotion project already exists at {remotion_dir}[/yellow]")
            console.print("[cyan]Updating TypeScript templates...[/cyan]")
            # Update templates even if project exists
            src_dir = remotion_dir / "src"
            src_dir.mkdir(exist_ok=True)

            # Regenerate TypeScript components from latest templates
            (src_dir / "VideoGenerator.tsx").write_text(
                video.templates.get_video_generator_tsx(), encoding="utf-8"
            )
            (src_dir / "Root.tsx").write_text(video.templates.get_root_tsx(), encoding="utf-8")
            (src_dir / "index.ts").write_text(video.templates.get_index_ts(), encoding="utf-8")
            (remotion_dir / "remotion.config.ts").write_text(
                video.templates.get_remotion_config_ts(), encoding="utf-8"
            )

            console.print("[green]✓ Templates updated[/green]")
            return remotion_dir

        # Verify pnpm is available
        _ensure_pnpm_available()

        console.print(f"[cyan]Creating Remotion project for {self.name}...[/cyan]")

        # Create remotion directory
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Create package.json
        console.print("[cyan]Creating package.json...[/cyan]")
        package_json_path = remotion_dir / "package.json"
        package_data = video.templates.get_package_json(self.name)
        with package_json_path.open("w", encoding="utf-8") as f:
            json.dump(package_data, f, indent=2)

        # Install Remotion packages
        console.print("[cyan]Installing Remotion packages...[/cyan]")
        try:
            subprocess.run(
                ["pnpm", "install"],
                cwd=remotion_dir,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            console.print("[red]Failed to install Remotion packages:[/red]")
            console.print(f"[red]{e.stderr}[/red]")
            raise

        # Create src directory
        src_dir = remotion_dir / "src"
        src_dir.mkdir(exist_ok=True)

        # Generate TypeScript components
        console.print("[cyan]Generating TypeScript components...[/cyan]")

        # VideoGenerator.tsx
        (src_dir / "VideoGenerator.tsx").write_text(
            video.templates.get_video_generator_tsx(), encoding="utf-8"
        )

        # Root.tsx
        (src_dir / "Root.tsx").write_text(video.templates.get_root_tsx(), encoding="utf-8")

        # index.ts
        (src_dir / "index.ts").write_text(video.templates.get_index_ts(), encoding="utf-8")

        # remotion.config.ts
        (remotion_dir / "remotion.config.ts").write_text(
            video.templates.get_remotion_config_ts(), encoding="utf-8"
        )

        # tsconfig.json
        tsconfig_path = remotion_dir / "tsconfig.json"
        with tsconfig_path.open("w", encoding="utf-8") as f:
            json.dump(video.templates.get_tsconfig_json(), f, indent=2)

        # Create public directory and symlinks to assets
        public_dir = remotion_dir / "public"
        public_dir.mkdir(exist_ok=True)

        # Create symbolic links to audio, slides, and characters
        _create_symlink_safe(self.audio_dir, public_dir / "audio")
        _create_symlink_safe(self.slides_dir, public_dir / "slides")
        _create_symlink_safe(self.characters_dir, public_dir / "characters")

        # Create directories for backgrounds and BGM (assets will be copied when needed)
        backgrounds_dir = self.project_dir / "assets" / "backgrounds"
        backgrounds_dir.mkdir(parents=True, exist_ok=True)
        _create_symlink_safe(backgrounds_dir, public_dir / "backgrounds")

        bgm_dir = self.project_dir / "assets" / "bgm"
        bgm_dir.mkdir(parents=True, exist_ok=True)
        _create_symlink_safe(bgm_dir, public_dir / "bgm")

        # Load project config to get transition settings
        try:
            project_config = self.load_config()
            transition_config = project_config.video.transition.model_dump()
        except Exception:
            # Fallback to defaults if config loading fails
            from .config import TransitionConfig

            transition_config = TransitionConfig(
                type="fade", duration_frames=15, timing="linear"
            ).model_dump()

        # Create placeholder composition.json
        composition_data = {
            "title": self.name,
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "phrases": [],
            "transition": transition_config,
        }
        composition_path = remotion_dir / "composition.json"
        with composition_path.open("w", encoding="utf-8") as f:
            json.dump(composition_data, f, indent=2)

        console.print(f"[green]✓ Remotion project created at {remotion_dir}[/green]")
        return remotion_dir

    def update_composition_json(self, phrases: list[dict[str, Any]], language: str = "ja") -> None:
        """Update composition.json with phrase data.

        Args:
            phrases: List of phrase dictionaries with text, duration, etc.
            language: Language code for slides path (e.g., "ja", "en"). Defaults to "ja".
        """
        remotion_dir = self.project_dir / "remotion"
        if not remotion_dir.exists():
            raise FileNotFoundError(
                "Remotion project not initialized. Run setup_remotion_project() first."
            )

        # Load project config to get transition settings
        try:
            project_config = self.load_config()
            transition_config = project_config.video.transition.model_dump()
        except Exception:
            # Fallback to defaults if config loading fails
            from .config import TransitionConfig

            transition_config = TransitionConfig(
                type="fade", duration_frames=15, timing="linear"
            ).model_dump()

        # Build composition data
        composition_data = {
            "title": self.name,
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "phrases": [
                {
                    "text": phrase.get("text", ""),
                    "audioFile": f"audio/{phrase.get('audio_file', '')}",
                    "slideFile": f"slides/{language}/{phrase.get('slide_file', '')}"
                    if phrase.get("slide_file")
                    else None,
                    "duration": phrase.get("duration", 0.0),
                }
                for phrase in phrases
            ],
            "transition": transition_config,
        }

        composition_path = remotion_dir / "composition.json"
        with composition_path.open("w", encoding="utf-8") as f:
            json.dump(composition_data, f, indent=2, ensure_ascii=False)

        console.print(
            f"[green]✓ Updated composition.json with {len(phrases)} phrases (language: {language})[/green]"
        )


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
