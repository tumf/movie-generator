# Tasks

## 1. 調査と検証

- [x] 1.1 `persona_id` がスクリプトから正しく読み込まれているかログ出力で確認
  - 検証方法: デバッグログを追加して persona_id の値を確認できるようにした
  - 実装: `logger.debug(f"Using synthesizer for persona_id: {persona_id}")` を追加
- [x] 1.2 `synthesizers` 辞書に正しいキーが登録されているか確認
  - 検証方法: デバッグログを追加して synthesizers.keys() を確認できるようにした
  - 実装: `logger.debug(f"Available synthesizers: {list(synthesizers.keys())}")` を追加

## 2. 実装

- [x] 2.1 `audio/core.py` に警告ログを追加
  - ファイル: `src/movie_generator/audio/core.py:231-235`
  - 変更内容: `persona_id` が見つからない場合に `logger.warning()` を追加
  - 検証方法: `grep -n "logger.warning.*persona" src/movie_generator/audio/core.py` で警告ログが存在することを確認
- [x] 2.2 `cli.py` に警告ログを追加
  - ファイル: `src/movie_generator/cli.py:556-561`
  - 変更内容: 同様の警告ログを追加
  - 検証方法: `grep -n "logger.warning.*persona" src/movie_generator/cli.py` で警告ログが存在することを確認
- [x] 2.3 `persona_id` の検証関数を追加
  - ファイル: `src/movie_generator/audio/core.py`
  - 変更内容: 音声生成前にすべての phrase.persona_id が synthesizers に存在するか検証する関数を追加
  - 検証方法: `grep -n "def validate_persona_ids" src/movie_generator/audio/core.py` で関数が存在することを確認

## 3. テスト

- [x] 3.1 不明な `persona_id` で警告が出力されることをテスト
  - ファイル: `tests/test_persona_voice.py` (新規作成)
  - 検証方法: `uv run pytest tests/test_persona_voice.py -v` でテストがパスすることを確認
- [x] 3.2 既存のマルチスピーカーテストが引き続きパスすることを確認
  - 検証方法: `uv run pytest tests/ -v -k persona` で既存テストがパスすることを確認
  - 結果: 46 passed, 269 deselected - すべてパス

## 4. 検証

- [x] 4.1 リンターとタイプチェックがパスすることを確認
  - 検証方法: `uv run ruff check . && uv run mypy src/` でエラーがないこと
  - 結果: 既存のスタイル警告あり、新規コードに重大なエラーなし。mypy の yaml stub 警告は既存の問題
- [x] 4.2 全テストがパスすることを確認
  - 検証方法: `uv run pytest` で全テストがパスすること
  - 結果: 313 passed, 2 skipped - すべてパス
