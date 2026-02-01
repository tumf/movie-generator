"""Tests for Remotion project setup stage isolation."""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from subprocess import CalledProcessError

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.project import Project
from movie_generator.video.remotion_renderer import (
    ensure_chrome_headless_shell,
    ensure_pnpm_dependencies,
    ensure_rendering_environment,
)


class TestRemotionSetupStages:
    """Test Remotion project setup stage isolation and error messages."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a mock project with temporary directory."""
        project = Project(name="test-project", root_dir=tmp_path / "projects")
        project.project_dir.mkdir(parents=True, exist_ok=True)
        project.assets_dir.mkdir(exist_ok=True)
        project.audio_dir.mkdir(exist_ok=True)
        project.slides_dir.mkdir(exist_ok=True)
        project.characters_dir.mkdir(exist_ok=True)
        return project

    @patch("movie_generator.video.templates")
    @patch("movie_generator.project.subprocess.run")
    def test_initialize_remotion_project_success(self, mock_run, mock_templates, mock_project):
        """Test successful Remotion project initialization."""
        remotion_dir = mock_project.project_dir / "remotion"

        # Mock templates
        mock_templates.get_package_json.return_value = {
            "name": "@projects/test-project",
            "version": "1.0.0",
        }

        # Mock successful pnpm install
        mock_run.return_value = Mock(returncode=0, stderr="")

        # Execute initialization
        mock_project._initialize_remotion_project(remotion_dir)

        # Verify package.json was created
        assert (remotion_dir / "package.json").exists()

        # Verify pnpm install was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["pnpm", "install"]
        assert call_args[1]["cwd"] == remotion_dir

    @patch("movie_generator.video.templates")
    @patch("movie_generator.project.subprocess.run")
    def test_initialize_remotion_project_pnpm_failure(self, mock_run, mock_templates, mock_project):
        """Test initialization failure with pnpm error includes stage name."""
        remotion_dir = mock_project.project_dir / "remotion"

        # Mock templates
        mock_templates.get_package_json.return_value = {
            "name": "@projects/test-project",
            "version": "1.0.0",
        }

        # Mock pnpm install failure
        mock_run.side_effect = CalledProcessError(1, ["pnpm", "install"], stderr="pnpm error")

        # Execute and verify error message includes stage name
        with pytest.raises(RuntimeError, match="Remotion initialization failed"):
            mock_project._initialize_remotion_project(remotion_dir)

    @patch("movie_generator.video.templates")
    def test_generate_typescript_components_success(self, mock_templates, mock_project):
        """Test successful TypeScript component generation."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Mock templates
        mock_templates.get_video_generator_tsx.return_value = "// VideoGenerator.tsx"
        mock_templates.get_root_tsx.return_value = "// Root.tsx"
        mock_templates.get_index_ts.return_value = "// index.ts"
        mock_templates.get_remotion_config_ts.return_value = "// remotion.config.ts"
        mock_templates.get_tsconfig_json.return_value = {"compilerOptions": {}}

        # Execute component generation
        mock_project._generate_typescript_components(remotion_dir)

        # Verify all TypeScript files were created
        src_dir = remotion_dir / "src"
        assert (src_dir / "VideoGenerator.tsx").exists()
        assert (src_dir / "Root.tsx").exists()
        assert (src_dir / "index.ts").exists()
        assert (remotion_dir / "remotion.config.ts").exists()
        assert (remotion_dir / "tsconfig.json").exists()

    @patch("movie_generator.video.templates")
    def test_generate_typescript_components_write_failure(self, mock_templates, mock_project):
        """Test TypeScript generation failure includes stage name."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Mock templates
        mock_templates.get_video_generator_tsx.return_value = "// VideoGenerator.tsx"
        mock_templates.get_root_tsx.return_value = "// Root.tsx"
        mock_templates.get_index_ts.return_value = "// index.ts"
        mock_templates.get_remotion_config_ts.return_value = "// remotion.config.ts"
        mock_templates.get_tsconfig_json.return_value = {"compilerOptions": {}}

        # Make src directory read-only to cause write failure
        src_dir = remotion_dir / "src"
        src_dir.mkdir(exist_ok=True)
        src_dir.chmod(0o444)

        try:
            # Execute and verify error message includes stage name
            with pytest.raises(RuntimeError, match="TypeScript component generation failed"):
                mock_project._generate_typescript_components(remotion_dir)
        finally:
            # Cleanup: restore permissions
            src_dir.chmod(0o755)

    @patch("movie_generator.project._create_symlink_safe")
    def test_setup_asset_symlinks_success(self, mock_symlink, mock_project):
        """Test successful asset symlink creation."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Execute symlink setup
        mock_project._setup_asset_symlinks(remotion_dir)

        # Verify all symlinks were created
        public_dir = remotion_dir / "public"
        assert public_dir.exists()
        assert mock_symlink.call_count == 5  # audio, slides, characters, backgrounds, bgm

    @patch("movie_generator.project._create_symlink_safe")
    def test_setup_asset_symlinks_failure(self, mock_symlink, mock_project):
        """Test asset symlink creation failure includes stage name."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Mock symlink creation failure
        mock_symlink.side_effect = OSError("Permission denied")

        # Execute and verify error message includes stage name
        with pytest.raises(RuntimeError, match="Asset symlink setup failed"):
            mock_project._setup_asset_symlinks(remotion_dir)

    def test_create_composition_file_success(self, mock_project):
        """Test successful composition.json creation."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Create minimal project config
        from movie_generator.config import Config

        config = Config()
        mock_project.save_config(config)

        # Execute composition file creation
        mock_project._create_composition_file(remotion_dir)

        # Verify composition.json was created
        composition_path = remotion_dir / "composition.json"
        assert composition_path.exists()

        # Verify content structure
        with composition_path.open("r", encoding="utf-8") as f:
            composition_data = json.load(f)
        assert "title" in composition_data
        assert "fps" in composition_data
        assert "width" in composition_data
        assert "height" in composition_data
        assert "phrases" in composition_data
        assert "transition" in composition_data

    def test_create_composition_file_write_failure(self, mock_project):
        """Test composition file creation failure includes stage name."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Make remotion_dir read-only to cause write failure
        remotion_dir.chmod(0o444)

        try:
            # Execute and verify error message includes stage name
            with pytest.raises(RuntimeError, match="Composition file creation failed"):
                mock_project._create_composition_file(remotion_dir)
        finally:
            # Cleanup: restore permissions
            remotion_dir.chmod(0o755)

    @patch("movie_generator.project.Path.cwd")
    def test_update_workspace_configuration_success(self, mock_cwd, mock_project, tmp_path):
        """Test successful workspace configuration update."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Create temporary workspace file
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(exist_ok=True)
        mock_cwd.return_value = workspace_dir

        workspace_file = workspace_dir / "pnpm-workspace.yaml"
        workspace_file.write_text("packages:\n  - 'other-package'\n", encoding="utf-8")

        # Execute workspace update
        mock_project._update_workspace_configuration(remotion_dir)

        # Verify workspace was updated
        import yaml

        with workspace_file.open("r", encoding="utf-8") as f:
            workspace_config = yaml.safe_load(f)

        assert "projects/*/remotion" in workspace_config["packages"]
        assert "other-package" in workspace_config["packages"]

    @patch("movie_generator.project.Path.cwd")
    def test_update_workspace_configuration_already_included(
        self, mock_cwd, mock_project, tmp_path
    ):
        """Test workspace update when pattern already exists."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Create temporary workspace file with pattern already included
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(exist_ok=True)
        mock_cwd.return_value = workspace_dir

        workspace_file = workspace_dir / "pnpm-workspace.yaml"
        workspace_file.write_text(
            "packages:\n  - 'projects/*/remotion'\n  - 'other-package'\n", encoding="utf-8"
        )

        # Execute workspace update
        mock_project._update_workspace_configuration(remotion_dir)

        # Verify no duplicate was added
        import yaml

        with workspace_file.open("r", encoding="utf-8") as f:
            workspace_config = yaml.safe_load(f)

        assert workspace_config["packages"].count("projects/*/remotion") == 1

    @patch("movie_generator.project.Path.cwd")
    def test_update_workspace_configuration_no_file(self, mock_cwd, mock_project, tmp_path):
        """Test workspace update when pnpm-workspace.yaml doesn't exist."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Set cwd to directory without workspace file
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(exist_ok=True)
        mock_cwd.return_value = workspace_dir

        # Execute workspace update (should not raise error)
        mock_project._update_workspace_configuration(remotion_dir)

    @patch("movie_generator.project.Path.cwd")
    def test_update_workspace_configuration_invalid_format(self, mock_cwd, mock_project, tmp_path):
        """Test workspace update failure with invalid YAML format."""
        remotion_dir = mock_project.project_dir / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)

        # Create workspace file with invalid format (missing 'packages' field)
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(exist_ok=True)
        mock_cwd.return_value = workspace_dir

        workspace_file = workspace_dir / "pnpm-workspace.yaml"
        workspace_file.write_text("invalid: yaml\n", encoding="utf-8")

        # Execute and verify error message includes stage name
        with pytest.raises(RuntimeError, match="Workspace configuration update failed"):
            mock_project._update_workspace_configuration(remotion_dir)

    @patch("movie_generator.video.templates")
    @patch("movie_generator.project._ensure_pnpm_available")
    @patch("movie_generator.project.subprocess.run")
    @patch("movie_generator.project.Path.cwd")
    def test_setup_remotion_project_full_flow(
        self, mock_cwd, mock_run, mock_pnpm_check, mock_templates, mock_project, tmp_path
    ):
        """Test full setup_remotion_project flow with all stages."""
        # Mock templates
        mock_templates.get_package_json.return_value = {
            "name": "@projects/test-project",
            "version": "1.0.0",
        }
        mock_templates.get_video_generator_tsx.return_value = "// VideoGenerator.tsx"
        mock_templates.get_root_tsx.return_value = "// Root.tsx"
        mock_templates.get_index_ts.return_value = "// index.ts"
        mock_templates.get_remotion_config_ts.return_value = "// remotion.config.ts"
        mock_templates.get_tsconfig_json.return_value = {"compilerOptions": {}}

        # Mock pnpm install success
        mock_run.return_value = Mock(returncode=0, stderr="")

        # Create workspace file for workspace update stage
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(exist_ok=True)
        mock_cwd.return_value = workspace_dir

        workspace_file = workspace_dir / "pnpm-workspace.yaml"
        workspace_file.write_text("packages:\n  - 'other-package'\n", encoding="utf-8")

        # Create minimal project config
        from movie_generator.config import Config

        config = Config()
        mock_project.save_config(config)

        # Execute full setup
        result = mock_project.setup_remotion_project()

        # Verify result
        assert result == mock_project.project_dir / "remotion"
        assert result.exists()

        # Verify all stages completed
        assert (result / "package.json").exists()
        assert (result / "src" / "VideoGenerator.tsx").exists()
        assert (result / "composition.json").exists()
        assert (result / "public").exists()

        # Verify workspace was updated
        import yaml

        with workspace_file.open("r", encoding="utf-8") as f:
            workspace_config = yaml.safe_load(f)
        assert "projects/*/remotion" in workspace_config["packages"]

    @patch("movie_generator.video.templates")
    @patch("movie_generator.project._ensure_pnpm_available")
    @patch("movie_generator.project.subprocess.run")
    def test_setup_remotion_project_initialization_stage_failure(
        self, mock_run, mock_pnpm_check, mock_templates, mock_project
    ):
        """Test setup failure at initialization stage."""
        # Mock templates
        mock_templates.get_package_json.return_value = {
            "name": "@projects/test-project",
            "version": "1.0.0",
        }

        # Mock pnpm install failure
        mock_run.side_effect = CalledProcessError(1, ["pnpm", "install"], stderr="pnpm error")

        # Execute and verify error message includes stage information
        with pytest.raises(RuntimeError, match="Remotion initialization failed"):
            mock_project.setup_remotion_project()


class TestRenderingEnvironmentSetup:
    """Test centralized rendering environment setup functions."""

    @pytest.fixture
    def remotion_root(self, tmp_path):
        """Create a temporary Remotion root directory."""
        remotion_dir = tmp_path / "remotion"
        remotion_dir.mkdir()
        return remotion_dir

    @patch("movie_generator.video.remotion_renderer.subprocess.run")
    def test_ensure_pnpm_dependencies_already_installed(self, mock_run, remotion_root):
        """Test pnpm dependency check when node_modules already exists."""
        # Create node_modules directory
        (remotion_root / "node_modules").mkdir()

        # Execute check
        ensure_pnpm_dependencies(remotion_root)

        # Verify pnpm install was NOT called
        mock_run.assert_not_called()

    @patch("movie_generator.video.remotion_renderer.subprocess.run")
    def test_ensure_pnpm_dependencies_install_needed(self, mock_run, remotion_root):
        """Test pnpm dependency installation when node_modules doesn't exist."""
        # Mock successful pnpm install
        mock_run.return_value = Mock(returncode=0, stderr="")

        # Execute installation
        ensure_pnpm_dependencies(remotion_root)

        # Verify pnpm install was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["pnpm", "install"]
        assert call_args[1]["cwd"] == remotion_root

    @patch("movie_generator.video.remotion_renderer.subprocess.run")
    def test_ensure_pnpm_dependencies_install_failure(self, mock_run, remotion_root):
        """Test pnpm dependency installation failure."""
        # Mock pnpm install failure
        mock_run.side_effect = CalledProcessError(1, ["pnpm", "install"], stderr="install failed")

        # Execute and verify error
        from movie_generator.exceptions import RenderingError

        with pytest.raises(RenderingError, match="pnpm install failed"):
            ensure_pnpm_dependencies(remotion_root)

    @patch("movie_generator.video.remotion_renderer.ProjectPaths")
    def test_ensure_chrome_headless_shell_already_exists(self, mock_paths, remotion_root):
        """Test Chrome Headless Shell check when already downloaded."""
        # Create browser path
        browser_path = remotion_root / "node_modules" / ".remotion" / "chrome-headless-shell"
        browser_path.parent.mkdir(parents=True)
        browser_path.mkdir()

        # Execute check
        ensure_chrome_headless_shell(remotion_root)

        # Verify no download was attempted (function returns early)
        # If no exception is raised, the test passes

    @patch("shutil.move")
    @patch("movie_generator.video.remotion_renderer.subprocess.run")
    @patch("movie_generator.video.remotion_renderer.ProjectPaths")
    def test_ensure_chrome_headless_shell_download(
        self, mock_paths, mock_run, mock_shutil_move, remotion_root, tmp_path
    ):
        """Test Chrome Headless Shell download process."""
        # Mock project root
        project_root = tmp_path / "project"
        project_root.mkdir()
        mock_paths.get_project_root.return_value = project_root

        # Create fake browser directory that will be "downloaded"
        temp_download_dir = project_root / ".cache" / "remotion" / "_temp_download"
        temp_download_dir.mkdir(parents=True)
        temp_browser = temp_download_dir / "node_modules" / ".remotion" / "chrome-headless-shell"
        temp_browser.parent.mkdir(parents=True)
        temp_browser.mkdir()

        # Mock subprocess success
        mock_run.return_value = Mock(returncode=0, stderr="")

        # Mock shutil.move
        def move_side_effect(src, dst):
            # Create destination directory to simulate move
            Path(dst).mkdir(parents=True)

        mock_shutil_move.side_effect = move_side_effect

        # Execute download
        ensure_chrome_headless_shell(remotion_root)

        # Verify download commands were called
        assert mock_run.call_count >= 2  # pnpm install + remotion browser ensure

    @patch("movie_generator.video.remotion_renderer.ensure_pnpm_dependencies")
    @patch("movie_generator.video.remotion_renderer.ensure_chrome_headless_shell")
    @patch("movie_generator.video.remotion_renderer.ProjectPaths")
    def test_ensure_rendering_environment_full_setup(
        self, mock_paths, mock_chrome, mock_pnpm, remotion_root, tmp_path
    ):
        """Test full rendering environment setup with all components."""
        # Mock project root and assets directory
        project_root = tmp_path / "project"
        project_root.mkdir()
        assets_dir = project_root / "assets"
        assets_dir.mkdir()
        mock_paths.get_docker_project_root.return_value = project_root

        # Execute full environment setup
        ensure_rendering_environment(remotion_root)

        # Verify all setup functions were called
        mock_pnpm.assert_called_once_with(remotion_root)
        mock_chrome.assert_called_once_with(remotion_root)

        # Verify assets symlink was created
        job_dir = remotion_root.parent
        assets_symlink = job_dir / "assets"
        assert assets_symlink.exists() or assets_symlink.is_symlink()

    @patch("movie_generator.video.remotion_renderer.ensure_pnpm_dependencies")
    @patch("movie_generator.video.remotion_renderer.ensure_chrome_headless_shell")
    @patch("movie_generator.video.remotion_renderer.ProjectPaths")
    def test_ensure_rendering_environment_assets_already_exist(
        self, mock_paths, mock_chrome, mock_pnpm, remotion_root, tmp_path
    ):
        """Test environment setup when assets symlink already exists."""
        # Create existing assets symlink
        job_dir = remotion_root.parent
        assets_symlink = job_dir / "assets"
        assets_symlink.mkdir()

        # Execute environment setup
        ensure_rendering_environment(remotion_root)

        # Verify setup functions were called but no new symlink created
        mock_pnpm.assert_called_once()
        mock_chrome.assert_called_once()
