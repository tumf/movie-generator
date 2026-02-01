"""Tests for slide generation task planning."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.slides.generator import plan_slide_generation_tasks


class TestSlideTaskPlanning:
    """Test slide generation task planning."""

    def test_plan_all_new_slides(self, tmp_path: Path) -> None:
        """Test planning when no slides exist yet."""
        sections = [
            ("Title 1", "Prompt 1"),
            ("Title 2", "Prompt 2", None),
            ("Title 3", "Prompt 3", "http://example.com/image.png"),
        ]

        tasks, paths = plan_slide_generation_tasks(
            sections=sections, output_dir=tmp_path, language="ja"
        )

        # Should plan 3 tasks (all new)
        assert len(tasks) == 3
        assert len(paths) == 3

        # Verify task types
        assert tasks[0].task_type == "generate"
        assert tasks[1].task_type == "generate"
        assert tasks[2].task_type == "download_or_generate"

        # Verify indices
        assert tasks[0].index == 0
        assert tasks[1].index == 1
        assert tasks[2].index == 2

        # Verify file paths
        for i, path in enumerate(paths):
            assert path == tmp_path / "ja" / f"slide_{i:04d}.png"

    def test_plan_skip_existing_slides(self, tmp_path: Path) -> None:
        """Test planning skips existing slides."""
        sections = [
            ("Title 1", "Prompt 1"),
            ("Title 2", "Prompt 2"),
            ("Title 3", "Prompt 3"),
        ]

        # Create output directory and simulate existing slide
        output_dir = tmp_path / "ja"
        output_dir.mkdir(parents=True)
        existing_slide = output_dir / "slide_0001.png"
        existing_slide.write_bytes(b"fake image data")

        tasks, paths = plan_slide_generation_tasks(
            sections=sections, output_dir=tmp_path, language="ja"
        )

        # Should plan only 2 tasks (skip existing slide_0001.png)
        assert len(tasks) == 2
        assert len(paths) == 3

        # Verify skipped slide
        assert tasks[0].index == 0  # slide_0000.png
        assert tasks[1].index == 2  # slide_0002.png (skip 0001)

    def test_plan_custom_indices(self, tmp_path: Path) -> None:
        """Test planning with custom section indices."""
        sections = [
            ("Title 1", "Prompt 1"),
            ("Title 2", "Prompt 2"),
        ]

        tasks, paths = plan_slide_generation_tasks(
            sections=sections,
            output_dir=tmp_path,
            language="ja",
            section_indices=[5, 10],
        )

        # Verify file indices
        assert tasks[0].file_index == 5
        assert tasks[1].file_index == 10
        assert paths[0] == tmp_path / "ja" / "slide_0005.png"
        assert paths[1] == tmp_path / "ja" / "slide_0010.png"

    def test_plan_skip_missing_data(self, tmp_path: Path) -> None:
        """Test planning skips sections without prompt or image."""
        sections = [
            ("Title 1", "Prompt 1"),
            ("Title 2", None, None),  # No prompt, no image
            ("Title 3", "Prompt 3"),
        ]

        tasks, paths = plan_slide_generation_tasks(
            sections=sections, output_dir=tmp_path, language="ja"
        )

        # Should plan only 2 tasks (skip section without data)
        assert len(tasks) == 2
        assert len(paths) == 3

        # Verify task indices
        assert tasks[0].index == 0
        assert tasks[1].index == 2  # Skipped index 1

    def test_plan_download_only(self, tmp_path: Path) -> None:
        """Test planning download-only task."""
        sections = [
            ("Title 1", None, "http://example.com/image.png"),
        ]

        tasks, paths = plan_slide_generation_tasks(
            sections=sections, output_dir=tmp_path, language="ja"
        )

        # Should plan 1 download task
        assert len(tasks) == 1
        assert tasks[0].task_type == "download"
        assert tasks[0].source_image_url == "http://example.com/image.png"
        assert tasks[0].prompt is None

    def test_plan_empty_sections(self, tmp_path: Path) -> None:
        """Test planning with empty sections list."""
        sections: list[tuple[str, str]] = []

        tasks, paths = plan_slide_generation_tasks(
            sections=sections, output_dir=tmp_path, language="ja"
        )

        # Should return empty lists
        assert len(tasks) == 0
        assert len(paths) == 0
