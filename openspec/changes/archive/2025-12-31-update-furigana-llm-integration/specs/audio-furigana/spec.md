## ADDED Requirements

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

## MODIFIED Requirements

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

## API Reference (Updated)

### FuriganaGenerator Extension

```python
class FuriganaGenerator:
    def get_words_needing_pronunciation(self, texts: list[str]) -> dict[str, str]:
        """Get words that need pronunciation verification by LLM.

        Returns words containing non-kana characters (kanji, ASCII letters, etc.)
        along with their morphological analysis readings for LLM verification.

        Args:
            texts: List of Japanese texts to analyze.

        Returns:
            Dictionary of {surface: suggested_reading} pairs for LLM verification.
        """
```

### LLM Reading Generation

```python
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
    """
```

### Text Utilities

```python
def clean_katakana_reading(text: str) -> str:
    """Clean katakana reading text for VOICEVOX.

    Removes spaces and filters out non-katakana characters.
    VOICEVOX requires pure katakana readings (ァ-ヴ and ー).

    Args:
        text: Katakana reading text to clean.

    Returns:
        Text with only katakana characters.
    """
```
