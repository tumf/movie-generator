# Tasks: dataclass から Pydantic への移行

## 1. audio モジュール

- [x] 1.1 `audio/furigana.py` の `MorphemeReading` を Pydantic に移行
- [x] 1.2 `audio/dictionary.py` の `DictionaryEntry` を Pydantic に移行
- [x] 1.3 `audio/voicevox.py` の `AudioMetadata` を Pydantic に移行
- [x] 1.4 audio モジュールのテスト実行で動作確認

## 2. content モジュール

- [x] 2.1 `content/parser.py` の `ContentMetadata` を Pydantic に移行
- [x] 2.2 `content/parser.py` の `ImageInfo` を Pydantic に移行
- [x] 2.3 `content/parser.py` の `ParsedContent` を Pydantic に移行
- [x] 2.4 content モジュールのテスト実行で動作確認

## 3. script モジュール

- [x] 3.1 `script/phrases.py` の `Phrase` を Pydantic に移行（`get_subtitle_text()` メソッド維持）
- [x] 3.2 `script/generator.py` の `Narration` を Pydantic に移行
- [x] 3.3 `script/generator.py` の `ScriptSection` を Pydantic に移行
- [x] 3.4 `script/generator.py` の `PronunciationEntry` を Pydantic に移行
- [x] 3.5 `script/generator.py` の `VideoScript` を Pydantic に移行
- [x] 3.6 script モジュールのテスト実行で動作確認

## 4. video モジュール

- [x] 4.1 `video/renderer.py` の `CompositionData` を Pydantic に移行
- [x] 4.2 `video/renderer.py` の `asdict()` を `model_dump()` に置換
- [x] 4.3 `video/remotion_renderer.py` の `RemotionPhrase` を Pydantic に移行
- [x] 4.4 video モジュールのテスト実行で動作確認

## 5. 統合検証

- [x] 5.1 全テスト実行 (`uv run pytest`)
- [x] 5.2 型チェック実行 (`uv run mypy src/`)
- [x] 5.3 リントチェック実行 (`uv run ruff check .`)
- [x] 5.4 E2E テストで動画生成の動作確認
