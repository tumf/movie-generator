"""Tests for phrase splitting and subtitle text generation."""

from movie_generator.script.phrases import Phrase, split_into_phrases


class TestPhrase:
    """Test Phrase class."""

    def test_get_subtitle_text_removes_trailing_period(self) -> None:
        """Test that trailing period is removed from subtitle text."""
        phrase = Phrase(text="これはテストです。")
        assert phrase.get_subtitle_text() == "これはテストです"

    def test_get_subtitle_text_removes_trailing_comma(self) -> None:
        """Test that trailing comma is removed from subtitle text."""
        phrase = Phrase(text="たとえばボタンやカード、")
        assert phrase.get_subtitle_text() == "たとえばボタンやカード"

    def test_get_subtitle_text_removes_multiple_trailing_punctuation(self) -> None:
        """Test that multiple trailing punctuation marks are removed."""
        phrase = Phrase(text="テスト。、")
        assert phrase.get_subtitle_text() == "テスト"

    def test_get_subtitle_text_preserves_mid_sentence_punctuation(self) -> None:
        """Test that punctuation in the middle is preserved."""
        phrase = Phrase(text="こんにちは、世界です。")
        assert phrase.get_subtitle_text() == "こんにちは、世界です"

    def test_get_subtitle_text_with_no_punctuation(self) -> None:
        """Test text with no trailing punctuation."""
        phrase = Phrase(text="テキスト")
        assert phrase.get_subtitle_text() == "テキスト"

    def test_get_subtitle_text_empty(self) -> None:
        """Test empty text."""
        phrase = Phrase(text="")
        assert phrase.get_subtitle_text() == ""

    def test_get_subtitle_text_only_punctuation(self) -> None:
        """Test text with only punctuation."""
        phrase = Phrase(text="。、")
        assert phrase.get_subtitle_text() == ""


class TestSplitIntoPhrases:
    """Test split_into_phrases function."""

    def test_split_at_period(self) -> None:
        """Test splitting at period."""
        text = "これは一文です。これは二文です。"
        phrases = split_into_phrases(text)
        assert len(phrases) == 2
        assert phrases[0].text == "これは一文です。"
        assert phrases[1].text == "これは二文です。"

    def test_split_at_comma(self) -> None:
        """Test splitting at comma."""
        text = "まず最初に、次に、最後に"
        phrases = split_into_phrases(text)
        assert len(phrases) == 3

    def test_no_split_inside_short_quotes(self) -> None:
        """Test that short quoted text is not split inside quotation marks."""
        text = "これは「短い」テストです。"
        phrases = split_into_phrases(text, max_chars=50)
        # Short quoted text should not be split
        assert len(phrases) == 1

    def test_split_inside_long_quotes_at_sentence_boundary(self) -> None:
        """Test that long quoted text splits at sentence boundaries."""
        # This is the actual use case: narration wrapped in quotes
        text = "「これは長いナレーションです。複数の文で構成されています。」"
        phrases = split_into_phrases(text, max_chars=30)
        # Should split at sentence boundaries even inside quotes
        assert len(phrases) >= 2
        # First phrase should start with opening quote
        assert phrases[0].text.startswith("「")

    def test_split_at_quote_end_when_too_long(self) -> None:
        """Test that very long text splits at sentence boundaries."""
        text = "これは非常に長いテキストで「この中に含まれる引用部分も長くて複数の文が入っています。」さらに続きます。"
        phrases = split_into_phrases(text, max_chars=30)
        # Should split into multiple phrases
        assert len(phrases) >= 2

    def test_nested_quotes_not_supported(self) -> None:
        """Test behavior with nested quotes (not currently supported)."""
        # Current implementation doesn't handle nested quotes
        text = "外側「内側『ネスト』内側」外側"
        phrases = split_into_phrases(text)
        # Just verify it doesn't crash
        assert len(phrases) > 0

    def test_max_chars_respected_outside_quotes(self) -> None:
        """Test that max_chars is respected when not in quotes."""
        text = "これは50文字を超える長いテキストですがかぎ括弧は含まれていません。"
        phrases = split_into_phrases(text, max_chars=20)
        # Should split into multiple phrases
        assert len(phrases) > 1

    def test_empty_text(self) -> None:
        """Test empty text."""
        phrases = split_into_phrases("")
        assert len(phrases) == 0

    def test_only_punctuation(self) -> None:
        """Test text with only punctuation."""
        phrases = split_into_phrases("。、。")
        # Each punctuation should create a phrase (but they'll be empty after strip)
        # Actually, after strip they become empty and are not added
        assert len(phrases) == 0
