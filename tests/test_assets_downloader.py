"""Tests for asset downloader module."""

import pytest

from movie_generator.assets.downloader import sanitize_filename


class TestSanitizeFilename:
    """Test filename sanitization function."""

    def test_simple_name(self) -> None:
        """Test sanitizing a simple product name."""
        result = sanitize_filename("ProductX")
        assert result == "productx"

    def test_name_with_spaces(self) -> None:
        """Test sanitizing name with spaces."""
        result = sanitize_filename("Product Name")
        assert result == "product-name"

    def test_name_with_special_chars(self) -> None:
        """Test sanitizing name with special characters."""
        result = sanitize_filename("Product@Name#123")
        assert result == "productname123"

    def test_name_with_underscores(self) -> None:
        """Test sanitizing name with underscores."""
        result = sanitize_filename("product_name_v2")
        assert result == "product-name-v2"

    def test_consecutive_hyphens(self) -> None:
        """Test removing consecutive hyphens."""
        result = sanitize_filename("product  name")
        assert result == "product-name"

    def test_leading_trailing_hyphens(self) -> None:
        """Test removing leading/trailing hyphens."""
        result = sanitize_filename(" Product Name ")
        assert result == "product-name"

    def test_empty_after_sanitization(self) -> None:
        """Test handling of names that become empty after sanitization."""
        result = sanitize_filename("@#$%")
        assert result == ""

    def test_mixed_case_and_numbers(self) -> None:
        """Test mixed case with numbers."""
        result = sanitize_filename("OpenAI GPT-4")
        assert result == "openai-gpt-4"
