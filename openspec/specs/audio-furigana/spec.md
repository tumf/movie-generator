# Audio Furigana Generation Specification

## Purpose

This specification defines the automatic furigana (reading) generation capability for Japanese text using morphological analysis to improve VOICEVOX text-to-speech pronunciation accuracy.
## Requirements
### Requirement: Morphological Analysis Integration

The system SHALL use morphological analysis to generate accurate readings for Japanese text.

#### Scenario: Basic text analysis
- **Given** a Japanese text "表計算"
- **When** the FuriganaGenerator analyzes the text
- **Then** it returns morphemes with readings "ヒョウ" for "表" and "ケイサン" for "計算"

#### Scenario: Person-month reading
- **Given** a Japanese text containing "人月"
- **When** the FuriganaGenerator analyzes the text
- **Then** it returns the reading "ニンゲツ" (not "ジンゲツ")

#### Scenario: English word in dictionary
- **Given** a text containing "Excel"
- **When** the FuriganaGenerator analyzes the text
- **Then** it returns the reading "エクセル"

### Requirement: Automatic Dictionary Registration

The system SHALL automatically register morphological analysis results to the pronunciation dictionary.

#### Scenario: Auto-register readings
- **Given** a FuriganaGenerator and PronunciationDictionary
- **When** prepare_phrases() is called with phrases containing kanji
- **Then** readings are automatically added to the dictionary with priority 5

#### Scenario: Manual entries take precedence
- **Given** a manual dictionary entry for "東京" with reading "トーキョー" (priority 10)
- **And** morphological analysis result "トウキョウ" (priority 5)
- **When** both are registered to the dictionary
- **Then** the manual entry "トーキョー" is used

### Requirement: Configuration Option

The system SHALL provide a configuration option to enable/disable furigana generation.

#### Scenario: Enable furigana via config
- **Given** a configuration with `audio.enable_furigana: true`
- **When** VoicevoxSynthesizer is created from config
- **Then** automatic furigana generation is enabled

#### Scenario: Disable furigana via config
- **Given** a configuration with `audio.enable_furigana: false`
- **When** VoicevoxSynthesizer is created from config
- **Then** automatic furigana generation is disabled

### Requirement: Batch Processing

The system SHALL support batch processing of multiple phrases for efficiency.

#### Scenario: Analyze multiple texts
- **Given** a list of phrases ["表計算", "人月", "ボタン"]
- **When** analyze_texts() is called
- **Then** a combined dictionary of all readings is returned

#### Scenario: Process before initialization
- **Given** a VoicevoxSynthesizer with furigana enabled
- **When** prepare_phrases() is called before initialize()
- **Then** all readings are registered to the dictionary for use in initialization

### Requirement: CLI Integration for Morphological Fallback

The CLI SHALL automatically supplement LLM-generated pronunciations with morphological analysis results.

#### Scenario: LLM pronunciation takes precedence
- **Given** a script.yaml with LLM-generated pronunciation for "Turso" -> "ターソ" (priority 10)
- **And** the narration text contains "Turso"
- **When** audio generation is executed
- **Then** the LLM pronunciation "ターソ" is used

#### Scenario: Morphological analysis fills gaps
- **Given** a script.yaml without pronunciation for "BETA"
- **And** the narration contains "今はBETAで"
- **When** audio generation is executed
- **Then** morphological analysis adds "BETA" -> "ベータ" (priority 5) to the dictionary

#### Scenario: Error handling for missing MeCab
- **Given** MeCab/UniDic is not installed or configured
- **When** morphological analysis is attempted
- **Then** a warning is logged and audio generation continues without morphological fallback

### Requirement: Text-based Preparation Method

VoicevoxSynthesizerは、生テキスト文字列から発音を準備するメソッドを提供しなければならない（SHALL）。

#### Scenario: ナレーションテキストからの準備
- **GIVEN** スクリプトセクションからのナレーションテキストリスト
- **WHEN** `prepare_texts()` が呼び出される
- **THEN** すべての形態素読みが辞書に追加される

#### Scenario: LLM統合による準備
- **GIVEN** ナレーションテキストリストとOpenRouter APIキー
- **WHEN** `prepare_texts(texts, api_key=key)` が呼び出される
- **THEN** 形態素解析で抽出した単語がLLMで検証され、辞書に追加される

#### Scenario: LLM呼び出しの進捗表示
- **GIVEN** 発音確認が必要な単語が見つかった場合
- **WHEN** LLM読み生成が実行される
- **THEN** 「Found N words needing pronunciation」と「LLM verified/generated readings for M words」がコンソールに表示される

### Requirement: LLM-based Pronunciation Generation

The system SHALL use LLM to generate context-aware pronunciations for words that morphological analysis cannot accurately read.

#### Scenario: Context-aware reading generation
- **Given** a text containing "今日は軽めの作業です"
- **When** LLM pronunciation generation is invoked
- **Then** it returns context-appropriate readings like "キョウ" for "今日" and "カルメ" for "軽め"

#### Scenario: English word pronunciation
- **Given** a text containing "markdownを使います"
- **When** LLM pronunciation generation is invoked
- **Then** it returns "マークダウン" for "markdown"

#### Scenario: Compound word detection
- **Given** a text containing "検索時に実行する"
- **When** LLM pronunciation generation is invoked
- **Then** it detects compound words and returns "ケンサクジ" for "検索時" (not "ケンサクトキ")

#### Scenario: Words needing pronunciation extraction
- **Given** a text with kanji and English words
- **When** get_words_needing_pronunciation() is called
- **Then** it returns words containing kanji or ASCII letters, excluding kana-only words

### Requirement: LLM-Based Context-Aware Reading Generation

システムは、形態素解析で抽出した単語をLLMに送信し、文脈を考慮した正確なカタカナ読みを生成しなければならない（SHALL）。

#### Scenario: 文脈依存の漢字読み判定
- **GIVEN** ナレーションテキスト「軽めの設定で始めましょう」
- **WHEN** 形態素解析で「軽め」が抽出され、読み候補「カルメ」とともにLLMに送信される
- **THEN** LLMは文脈から正しい読み「カルメ」を返す（「ケイメ」ではない）

#### Scenario: 英単語のカタカナ変換
- **GIVEN** ナレーションテキスト「markdownで書く」
- **WHEN** 「markdown」がLLMに送信される
- **THEN** LLMは「マークダウン」を返す

#### Scenario: 同音異義語の文脈判定
- **GIVEN** ナレーションテキスト「今日の予定」
- **WHEN** 「今日」がLLMに送信される
- **THEN** LLMは文脈から「キョウ」を返す（「コンニチ」ではない）

#### Scenario: API失敗時のフォールバック
- **GIVEN** OpenRouter APIが利用できない状況
- **WHEN** LLM読み生成が失敗する
- **THEN** 形態素解析の読み候補がそのまま使用される

### Requirement: Pronunciation Candidate Extraction

システムは、読み確認が必要な単語（漢字・英字を含む単語）を形態素解析から抽出し、読み候補とともに取得できなければならない（SHALL）。

#### Scenario: 漢字単語の抽出
- **GIVEN** テキスト「設定を変更」
- **WHEN** `get_words_needing_pronunciation()` が呼び出される
- **THEN** `{"設定": "セッテイ", "変更": "ヘンコウ"}` のような辞書が返される

#### Scenario: 英単語の抽出
- **GIVEN** テキスト「Pythonコード」
- **WHEN** `get_words_needing_pronunciation()` が呼び出される
- **THEN** `{"Python": "Python"}` が返される（読みなしは表層形がそのまま候補）

#### Scenario: かな専用単語の除外
- **GIVEN** テキスト「これはテストです」
- **WHEN** `get_words_needing_pronunciation()` が呼び出される
- **THEN** 「これ」「テスト」「です」は含まれない（読み確認不要）

#### Scenario: 助詞の除外
- **GIVEN** テキスト「軽めの設定」
- **WHEN** `get_words_needing_pronunciation()` が呼び出される
- **THEN** 「の」（助詞）は含まれない

### Requirement: Katakana Reading Sanitization

システムは、LLMから返されたカタカナ読みをVOICEVOXが受け入れ可能な形式にクリーニングしなければならない（SHALL）。

#### Scenario: スペース除去
- **GIVEN** LLMが「マーク ダウン」を返した場合
- **WHEN** `clean_katakana_reading()` で処理される
- **THEN** 「マークダウン」が返される

#### Scenario: 非カタカナ文字の除去
- **GIVEN** LLMが「マークダウン!」を返した場合
- **WHEN** `clean_katakana_reading()` で処理される
- **THEN** 「マークダウン」が返される（!は除去）

#### Scenario: 長音符の保持
- **GIVEN** LLMが「サーバー」を返した場合
- **WHEN** `clean_katakana_reading()` で処理される
- **THEN** 「サーバー」がそのまま返される（ーは有効な文字）

### Requirement: LLM Pronunciation Priority

LLMで生成された読みは、手動辞書エントリより低く、形態素解析フォールバックより高い優先度で登録されなければならない（SHALL）。

#### Scenario: LLM読みと手動エントリの優先度
- **GIVEN** 手動辞書に「Turso」→「ターソ」（優先度10）が登録済み
- **WHEN** LLMが「Turso」→「タルソ」を生成
- **THEN** 手動エントリ「ターソ」が使用される

#### Scenario: LLM読みと形態素解析の優先度
- **GIVEN** 形態素解析が「軽め」→「ケイメ」を候補として出力
- **WHEN** LLMが「軽め」→「カルメ」を生成
- **THEN** LLMの読み「カルメ」が使用される

## Dependencies

- `fugashi>=1.3.0`: MeCab wrapper for Python
- `unidic>=1.1.0`: UniDic dictionary (full version)

## API Reference

### FuriganaGenerator

```python
class FuriganaGenerator:
    def analyze(self, text: str) -> list[MorphemeReading]:
        """Analyze text and return morphemes with readings."""

    def get_readings_dict(self, text: str) -> dict[str, str]:
        """Get dictionary mapping surface forms to readings."""

    def analyze_texts(self, texts: list[str]) -> dict[str, str]:
        """Analyze multiple texts and return combined readings."""

    def get_words_needing_pronunciation(self, text: str) -> list[str]:
        """Get words that need pronunciation (kanji or English words)."""
```

### LLM Pronunciation Generation

```python
async def generate_readings_with_llm(
    words: list[str],
    context: str,
    api_key: str | None = None,
    model: str = "openai/gpt-4o-mini",
) -> dict[str, str]:
    """Generate katakana readings for words using LLM.

    Args:
        words: List of words needing pronunciation.
        context: Original text for context-aware reading.
        api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var).
        model: LLM model to use.

    Returns:
        Dictionary mapping words to katakana readings.
    """
```

### PronunciationDictionary Extension

```python
class PronunciationDictionary:
    def add_from_morphemes(
        self,
        readings: dict[str, str],
        priority: int = 5,
        word_type: str = "COMMON_NOUN",
    ) -> int:
        """Add entries from morphological analysis results."""
```

### VoicevoxSynthesizer Extension

```python
class VoicevoxSynthesizer:
    def __init__(
        self,
        ...,
        enable_furigana: bool = True,
    ):
        """Initialize with optional furigana generation."""

    def prepare_phrases(self, phrases: list[Phrase]) -> int:
        """Prepare dictionary entries for all phrases."""

    def prepare_texts(self, texts: list[str]) -> int:
        """Prepare dictionary entries from raw text strings.

        Similar to prepare_phrases() but accepts raw text strings.
        Returns the number of dictionary entries added.
        """

    async def prepare_texts_with_llm(
        self,
        texts: list[str],
        api_key: str | None = None,
        model: str = "openai/gpt-4o-mini",
    ) -> dict[str, str]:
        """Prepare pronunciations using LLM for context-aware readings.

        Args:
            texts: List of narration texts.
            api_key: OpenRouter API key.
            model: LLM model to use.

        Returns:
            Dictionary of new pronunciations generated by LLM.
        """
```

## Configuration Schema

```yaml
audio:
  enable_furigana: true  # Enable automatic furigana generation (default: true)
```
