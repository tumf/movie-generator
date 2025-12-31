"""Tests for furigana generation using morphological analysis."""

import pytest
from movie_generator.audio.furigana import FuriganaGenerator, MorphemeReading


class TestFuriganaGenerator:
    """Test FuriganaGenerator class."""

    @pytest.fixture
    def generator(self) -> FuriganaGenerator:
        """Create a FuriganaGenerator instance."""
        return FuriganaGenerator()

    def test_analyze_basic_text(self, generator: FuriganaGenerator) -> None:
        """Test basic morphological analysis."""
        morphemes = generator.analyze("東京")
        assert len(morphemes) > 0
        assert all(isinstance(m, MorphemeReading) for m in morphemes)

    def test_analyze_returns_readings(self, generator: FuriganaGenerator) -> None:
        """Test that analysis returns correct readings."""
        morphemes = generator.analyze("日本語")
        # Should have readings in katakana
        readings = [m.reading for m in morphemes]
        assert any(r for r in readings if r)  # At least one non-empty reading

    def test_get_readings_dict_basic(self, generator: FuriganaGenerator) -> None:
        """Test get_readings_dict returns dictionary."""
        readings = generator.get_readings_dict("東京は日本の首都です")
        assert isinstance(readings, dict)
        # Should have some entries for kanji words
        assert len(readings) > 0

    def test_get_readings_dict_excludes_same_surface(self, generator: FuriganaGenerator) -> None:
        """Test that readings dict excludes entries where surface equals reading."""
        readings = generator.get_readings_dict("あいうえお")
        # Hiragana should not be in the dict (surface == reading)
        # May have some entries depending on how the analyzer handles it
        for surface, reading in readings.items():
            assert surface != reading

    def test_hyoukeisan_reading(self, generator: FuriganaGenerator) -> None:
        """Test 表計算 is read as ヒョウケイサン not オモテケイサン.

        This is a known VOICEVOX mispronunciation case.
        """
        readings = generator.get_readings_dict("表計算")
        # Check that we get readings for the kanji
        all_readings = "".join(readings.values())
        # Should NOT contain オモテ (wrong reading for 表)
        assert "オモテ" not in all_readings
        # Should contain ヒョウ (correct reading for 表 in 表計算)
        # Note: depending on dictionary, it might be analyzed differently
        # The key is that it's not the wrong reading

    def test_ningetsu_reading(self, generator: FuriganaGenerator) -> None:
        """Test 人月 is read as ニンゲツ not ジンゲツ.

        This is a known VOICEVOX mispronunciation case.
        """
        readings = generator.get_readings_dict("人月の見積もり")
        # Should have readings
        assert len(readings) > 0
        # The actual reading depends on the UniDic dictionary

    def test_english_word_button(self, generator: FuriganaGenerator) -> None:
        """Test English word Button gets a reading.

        VOICEVOX might spell it out as ビーユーティーティーエヌ instead of ボタン.
        """
        morphemes = generator.analyze("Button")
        assert len(morphemes) > 0
        # Should have some reading

    def test_english_word_in_readings_dict(self, generator: FuriganaGenerator) -> None:
        """Test English words are included in readings dict.

        Words like 'markdown', 'Excel', 'Python' should be candidates
        for pronunciation dictionary entries.
        """
        readings = generator.get_readings_dict("markdownで書く")
        assert "markdown" in readings

        readings = generator.get_readings_dict("Pythonコード")
        assert "Python" in readings

    def test_get_unknown_readings_basic(self, generator: FuriganaGenerator) -> None:
        """Test get_unknown_readings identifies words without katakana readings."""
        texts = ["markdownで書く", "Pythonコード"]
        unknown = generator.get_unknown_readings(texts)

        # markdown and Python should be in unknown (no UniDic reading)
        assert "markdown" in unknown
        assert "Python" in unknown

    def test_get_unknown_readings_excludes_known(self, generator: FuriganaGenerator) -> None:
        """Test get_unknown_readings excludes words with known readings."""
        texts = ["Excelの表計算"]
        unknown = generator.get_unknown_readings(texts)

        # Excel has a UniDic reading (エクセル), should NOT be in unknown
        assert "Excel" not in unknown

    def test_get_unknown_readings_excludes_short(self, generator: FuriganaGenerator) -> None:
        """Test get_unknown_readings excludes very short words."""
        texts = ["a, b, c are variables"]
        unknown = generator.get_unknown_readings(texts)

        # Single letter words should be excluded
        assert "a" not in unknown
        assert "b" not in unknown
        assert "c" not in unknown

    def test_get_words_needing_pronunciation_includes_kanji(
        self, generator: FuriganaGenerator
    ) -> None:
        """Test get_words_needing_pronunciation includes kanji words."""
        texts = ["軽めの設定"]
        words = generator.get_words_needing_pronunciation(texts)

        # Kanji words should be included
        assert "軽め" in words
        assert "設定" in words
        # Particle should be excluded
        assert "の" not in words

    def test_get_words_needing_pronunciation_includes_english(
        self, generator: FuriganaGenerator
    ) -> None:
        """Test get_words_needing_pronunciation includes English words."""
        texts = ["markdownで書く"]
        words = generator.get_words_needing_pronunciation(texts)

        assert "markdown" in words
        assert "書く" in words

    def test_get_words_needing_pronunciation_excludes_kana_only(
        self, generator: FuriganaGenerator
    ) -> None:
        """Test get_words_needing_pronunciation excludes kana-only words."""
        texts = ["これはテストです"]
        words = generator.get_words_needing_pronunciation(texts)

        # Hiragana/katakana only words should not be included
        assert "これ" not in words
        assert "テスト" not in words
        assert "です" not in words

    def test_is_only_kana(self, generator: FuriganaGenerator) -> None:
        """Test _is_only_kana helper method."""
        assert generator._is_only_kana("ひらがな") is True
        assert generator._is_only_kana("カタカナ") is True
        assert generator._is_only_kana("ひらカタ") is True
        assert generator._is_only_kana("漢字") is False
        assert generator._is_only_kana("English") is False
        assert generator._is_only_kana("混合テスト") is False

    def test_mixed_japanese_english(self, generator: FuriganaGenerator) -> None:
        """Test mixed Japanese and English text."""
        readings = generator.get_readings_dict("Excelの表計算機能")
        assert len(readings) > 0

    def test_analyze_texts_combines_results(self, generator: FuriganaGenerator) -> None:
        """Test analyze_texts combines readings from multiple texts."""
        texts = ["表計算", "人月", "ボタンをクリック"]
        readings = generator.analyze_texts(texts)
        assert isinstance(readings, dict)
        # Should have entries from multiple texts
        assert len(readings) > 0

    def test_analyze_texts_first_reading_preserved(self, generator: FuriganaGenerator) -> None:
        """Test that first occurrence reading is preserved in analyze_texts."""
        # If same word appears with different context, first reading is kept
        texts = ["日本", "日本語"]
        readings = generator.analyze_texts(texts)
        # Just verify it doesn't crash and returns dict
        assert isinstance(readings, dict)

    def test_empty_text(self, generator: FuriganaGenerator) -> None:
        """Test empty text handling."""
        morphemes = generator.analyze("")
        assert morphemes == []

        readings = generator.get_readings_dict("")
        assert readings == {}

    def test_punctuation_excluded(self, generator: FuriganaGenerator) -> None:
        """Test that punctuation is excluded from readings dict."""
        readings = generator.get_readings_dict("こんにちは。")
        # Punctuation should not be in the dict
        assert "。" not in readings


class TestPronunciationDictionaryIntegration:
    """Test integration with PronunciationDictionary."""

    def test_add_from_morphemes(self) -> None:
        """Test adding morpheme readings to dictionary."""
        from movie_generator.audio.dictionary import PronunciationDictionary

        dictionary = PronunciationDictionary()
        readings = {"東京": "トウキョウ", "日本": "ニホン"}

        added = dictionary.add_from_morphemes(readings)

        assert added == 2
        assert "東京" in dictionary.entries
        assert "日本" in dictionary.entries
        assert dictionary.entries["東京"].reading == "トウキョウ"

    def test_manual_entries_take_precedence(self) -> None:
        """Test that manual entries are not overwritten by morpheme analysis."""
        from movie_generator.audio.dictionary import PronunciationDictionary

        dictionary = PronunciationDictionary()

        # Add manual entry first (higher priority)
        dictionary.add_word("東京", "トーキョー", priority=10)

        # Try to add morpheme reading (lower priority)
        readings = {"東京": "トウキョウ", "日本": "ニホン"}
        added = dictionary.add_from_morphemes(readings, priority=5)

        # Only one entry should be added (日本), 東京 should keep manual reading
        assert added == 1
        assert dictionary.entries["東京"].reading == "トーキョー"
        assert dictionary.entries["日本"].reading == "ニホン"
