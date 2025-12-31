"""Automatic furigana generation using morphological analysis.

Uses fugashi (MeCab wrapper) with UniDic to analyze Japanese text
and generate accurate readings for all words. For unknown words (especially
English terms), uses LLM to generate katakana readings.
"""

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

from ..utils.text import clean_katakana_reading

if TYPE_CHECKING:
    from fugashi import Tagger


@dataclass
class MorphemeReading:
    """A morpheme with its surface form and reading."""

    surface: str  # Original text (e.g., "表計算")
    reading: str  # Katakana reading (e.g., "ヒョウケイサン")
    pos: str  # Part of speech (e.g., "名詞")


class FuriganaGenerator:
    """Generate furigana readings using morphological analysis.

    Uses fugashi with UniDic dictionary for accurate Japanese text analysis.
    Provides readings for kanji and other words that may be mispronounced
    by text-to-speech engines.
    """

    def __init__(self) -> None:
        """Initialize the morphological analyzer.

        The tagger is lazily initialized on first use.
        """
        self._tagger: Tagger | None = None

    @property
    def tagger(self) -> "Tagger":
        """Lazy initialization of fugashi Tagger.

        Returns:
            Initialized Tagger instance.

        Raises:
            ImportError: If fugashi or unidic is not installed.
        """
        if self._tagger is None:
            try:
                from fugashi import Tagger as FugashiTagger

                self._tagger = FugashiTagger()
            except ImportError as e:
                raise ImportError(
                    "fugashi is required for furigana generation. "
                    "Install it with: pip install fugashi unidic"
                ) from e
        return self._tagger

    def analyze(self, text: str) -> list[MorphemeReading]:
        """Analyze text and return morphemes with readings.

        Args:
            text: Japanese text to analyze.

        Returns:
            List of morphemes with surface forms and readings.
        """
        result: list[MorphemeReading] = []
        for word in self.tagger(text):
            surface: str = word.surface
            # UniDic provides reading in feature.kana
            feature: Any = word.feature
            reading: str = getattr(feature, "kana", None) or surface
            pos: str = getattr(feature, "pos1", None) or "Unknown"
            result.append(MorphemeReading(surface=surface, reading=reading, pos=pos))
        return result

    def get_readings_dict(self, text: str) -> dict[str, str]:
        """Get a dictionary mapping surface forms to readings.

        Includes entries where:
        - Surface differs from reading (words containing kanji)
        - Surface contains ASCII alphabetic characters (English words)

        Args:
            text: Japanese text to analyze.

        Returns:
            Dictionary of {surface: reading} pairs.
        """
        readings: dict[str, str] = {}
        for morpheme in self.analyze(text):
            surface = morpheme.surface
            reading = morpheme.reading

            # Skip single characters that are punctuation or symbols
            if len(surface) == 1 and not surface.isalnum():
                continue

            # Check if surface contains ASCII alphabetic characters (English words)
            has_ascii_alpha = any(c.isascii() and c.isalpha() for c in surface)

            # Include if:
            # 1. Reading differs from surface (kanji words)
            # 2. Surface contains ASCII alphabetic characters (English words like "markdown")
            if has_ascii_alpha:
                # For English words, include even if reading == surface
                # Use the reading if available, otherwise use surface as placeholder
                readings[surface] = reading if reading else surface
            elif surface != reading and reading:
                readings[surface] = reading

        return readings

    def analyze_texts(self, texts: list[str]) -> dict[str, str]:
        """Analyze multiple texts and return combined readings dictionary.

        Useful for batch processing all phrases before audio generation.

        Args:
            texts: List of Japanese texts to analyze.

        Returns:
            Combined dictionary of {surface: reading} pairs from all texts.
        """
        combined: dict[str, str] = {}
        for text in texts:
            readings = self.get_readings_dict(text)
            # Later texts don't override earlier readings
            for surface, reading in readings.items():
                if surface not in combined:
                    combined[surface] = reading
        return combined

    def get_words_needing_pronunciation(self, texts: list[str]) -> dict[str, str]:
        """Get words that need pronunciation verification by LLM.

        Returns words that contain non-kana characters (kanji, ASCII letters, etc.)
        along with their morphological analysis readings. These should be verified
        by LLM to ensure correct pronunciation.

        Args:
            texts: List of Japanese texts to analyze.

        Returns:
            Dictionary of {surface: suggested_reading} pairs for LLM verification.
        """
        words: dict[str, str] = {}
        for text in texts:
            for morpheme in self.analyze(text):
                surface = morpheme.surface
                reading = morpheme.reading

                # Skip if surface is only hiragana/katakana (no ambiguity)
                if self._is_only_kana(surface):
                    continue

                # Skip punctuation and single characters
                if len(surface) == 1 and not surface.isalnum():
                    continue

                # Skip particles (助詞) - they are usually read correctly
                if morpheme.pos == "助詞":
                    continue

                # Add to words dict (first occurrence wins)
                if surface not in words:
                    words[surface] = reading

        return words

    def _is_only_kana(self, text: str) -> bool:
        """Check if text contains only hiragana and katakana.

        Args:
            text: Text to check.

        Returns:
            True if text is only hiragana/katakana, False otherwise.
        """
        for char in text:
            # Hiragana: U+3040-U+309F, Katakana: U+30A0-U+30FF
            if not ("\u3040" <= char <= "\u309f" or "\u30a0" <= char <= "\u30ff"):
                return False
        return True

    def get_unknown_readings(self, texts: list[str]) -> list[str]:
        """Get list of words that need pronunciation lookup.

        Returns words where:
        - Surface contains ASCII alphabetic characters AND
        - Reading equals surface (no katakana reading from dictionary)

        These words need to be sent to LLM for pronunciation generation.

        Args:
            texts: List of Japanese texts to analyze.

        Returns:
            List of words that need pronunciation lookup.
        """
        unknown: set[str] = set()
        for text in texts:
            for morpheme in self.analyze(text):
                surface = morpheme.surface
                reading = morpheme.reading

                # Check if surface contains ASCII alphabetic characters
                has_ascii_alpha = any(c.isascii() and c.isalpha() for c in surface)

                # If has ASCII letters and reading == surface, it needs lookup
                if has_ascii_alpha and surface == reading:
                    # Skip very short words (likely abbreviations that can be spelled out)
                    if len(surface) >= 2:
                        unknown.add(surface)

        return sorted(unknown)


PRONUNCIATION_PROMPT = """
以下のテキストに含まれる単語のカタカナ読みを確認・生成してください。
音声合成エンジン（VOICEVOX）で正しく発音されるように、文脈に応じた自然なカタカナ読みを指定してください。

【元テキスト】
{context}

【確認が必要な単語】（形態素解析による読み候補付き）
{words}

【出力形式】
JSON形式で以下を出力してください：
{{
  "readings": {{
    "単語1": "カタカナ読み1",
    "単語2": "カタカナ読み2"
  }}
}}

【注意事項】
- カタカナ読みにはスペースを含めないでください
- **文脈に応じて**正しい読みを判断してください
- 形態素解析の読み候補が正しければそのまま使用してください
- 誤っている場合は正しい読みに修正してください
- **複合語で誤読されやすいものがあれば、複合語ごと追加してください**
  - 例: "検索時" → "ケンサクジ"（「ケンサクトキ」ではない）
  - 例: "実行時" → "ジッコウジ"（「ジッコウトキ」ではない）
- 例:
  - "markdown" → "マークダウン"
  - "Python" → "パイソン"
  - "GitHub" → "ギットハブ"
  - "軽め" → "カルメ"（「ケイメ」ではない）
  - "行う" → "オコナウ"（「イウ」ではない）
  - "今日" → 文脈により「キョウ」または「コンニチ」
  - "生" → 文脈により「ナマ」「セイ」「ショウ」など
"""


async def generate_readings_with_llm(
    words: dict[str, str],
    context: str,
    api_key: str | None = None,
    model: str = "openai/gpt-4o-mini",
    base_url: str = "https://openrouter.ai/api/v1",
) -> dict[str, str]:
    """Generate/verify katakana readings for words using LLM with context.

    Args:
        words: Dict of {word: suggested_reading} pairs from morphological analysis.
        context: Original text for context-aware reading determination.
        api_key: OpenRouter API key.
        model: Model identifier.
        base_url: API base URL.

    Returns:
        Dictionary mapping words to katakana readings.

    Raises:
        RuntimeError: If API request fails.
    """
    if not words:
        return {}

    if not api_key:
        import os

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Warning: OPENROUTER_API_KEY not set, skipping LLM pronunciation lookup")
            return {}

    # Format words for prompt
    words_text = "\n".join(f"- {word} (候補: {reading})" for word, reading in words.items())

    prompt = PRONUNCIATION_PROMPT.format(context=context, words=words_text)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{base_url}/chat/completions"
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            error_detail = response.text[:500] if response.text else "No response body"
            raise RuntimeError(
                f"LLM API request failed: {response.status_code} for {url}\n"
                f"Model: {model}\n"
                f"Response: {error_detail}"
            )
        data = response.json()

    # Parse response
    message_content = data["choices"][0]["message"]["content"]
    result = json.loads(message_content)

    # Clean readings (remove spaces, ensure katakana only)
    readings: dict[str, str] = {}
    for word, reading in result.get("readings", {}).items():
        readings[word] = clean_katakana_reading(reading)

    return readings
