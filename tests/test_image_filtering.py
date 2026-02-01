"""Tests for image candidate filtering in content pipeline.

Verifies that only images with is_candidate=True are passed to script generation.
"""

from unittest.mock import MagicMock, patch

import pytest

from movie_generator.content.parser import ImageInfo, ParsedContent, ContentMetadata


class TestImageCandidateFiltering:
    """Test that image candidate filtering works correctly in the pipeline."""

    def test_candidate_filtering_in_parsed_content(self):
        """Test that ParsedContent tracks both candidates and non-candidates."""
        images = [
            ImageInfo(
                src="https://example.com/good.jpg",
                alt="Meaningful description",
                is_candidate=True,
            ),
            ImageInfo(
                src="https://example.com/icon.png",
                alt="",
                is_candidate=False,
            ),
            ImageInfo(
                src="https://example.com/another-good.jpg",
                title="Good title",
                is_candidate=True,
            ),
            ImageInfo(
                src="https://example.com/bad.jpg",
                alt="x",
                is_candidate=False,
            ),
        ]

        parsed = ParsedContent(
            content="Test content",
            markdown="# Test",
            metadata=ContentMetadata(title="Test", description="Test description"),
            images=images,
        )

        # All images should be tracked
        assert len(parsed.images) == 4

        # Only 2 are candidates
        candidates = [img for img in parsed.images if img.is_candidate]
        assert len(candidates) == 2
        assert all(img.is_candidate for img in candidates)

        # 2 are non-candidates
        non_candidates = [img for img in parsed.images if not img.is_candidate]
        assert len(non_candidates) == 2
        assert all(not img.is_candidate for img in non_candidates)

    @patch("movie_generator.script.core.fetch_url_sync")
    @patch("movie_generator.script.core.parse_html")
    @patch("movie_generator.script.core.generate_script")
    def test_generate_script_from_url_filters_candidates(
        self, mock_generate_script, mock_parse_html, mock_fetch_url
    ):
        """Test that generate_script_from_url only passes candidate images."""
        from pathlib import Path
        from movie_generator.script.core import generate_script_from_url_sync
        from movie_generator.script.generator import VideoScript, ScriptSection, Narration

        # Setup mock parsed content with mixed candidates
        mock_images = [
            ImageInfo(
                src="https://example.com/candidate1.jpg",
                alt="Good description",
                is_candidate=True,
            ),
            ImageInfo(
                src="https://example.com/non-candidate.png",
                alt="x",
                is_candidate=False,
            ),
            ImageInfo(
                src="https://example.com/candidate2.jpg",
                title="Good title",
                is_candidate=True,
            ),
        ]

        mock_parsed = ParsedContent(
            content="Test content",
            markdown="# Test Article",
            metadata=ContentMetadata(title="Test Title", description="Test description"),
            images=mock_images,
        )

        mock_fetch_url.return_value = "<html>Test</html>"
        mock_parse_html.return_value = mock_parsed

        # Setup mock script
        mock_script = VideoScript(
            title="Test",
            description="Test",
            sections=[
                ScriptSection(
                    title="Section 1",
                    narrations=[Narration(text="Test", reading="Test")],
                )
            ],
        )
        mock_generate_script.return_value = mock_script

        # Call the function
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generate_script_from_url_sync(
                url="https://example.com/test",
                output_dir=output_dir,
                api_key="test-key",
            )

        # Verify generate_script was called with only candidate images
        mock_generate_script.assert_called_once()
        call_kwargs = mock_generate_script.call_args.kwargs
        images_arg = call_kwargs.get("images")

        # Should have 2 images (only candidates)
        assert images_arg is not None, "images_arg should not be None"
        assert len(images_arg) == 2, f"Expected 2 candidate images, got {len(images_arg)}"

        # Verify only candidates were passed
        srcs = [img["src"] for img in images_arg]
        assert "https://example.com/candidate1.jpg" in srcs
        assert "https://example.com/candidate2.jpg" in srcs
        assert "https://example.com/non-candidate.png" not in srcs
