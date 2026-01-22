# タスク

## 1. データモデルの変更

- [x] 1.1 `src/movie_generator/script/generator.py` から `PronunciationEntry` クラスを削除
- [x] 1.2 `VideoScript.pronunciations` フィールドを削除
- [x] 1.3 `src/movie_generator/multilang.py` から `pronunciations` を含めるコードを削除

## 2. LLM プロンプトの更新

- [x] 2.1 `SCRIPT_GENERATION_PROMPT_JA` から `pronunciations` 関連の指示を削除
- [x] 2.2 `SCRIPT_GENERATION_PROMPT_EN` から `pronunciations` 関連の指示を削除
- [x] 2.3 `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` から `pronunciations` 関連の指示を削除
- [x] 2.4 `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` から `pronunciations` 関連の指示を削除
- [x] 2.5 `generate_script()` 関数から `pronunciations` パース処理を削除

## 3. CLI 処理の削除

- [x] 3.1 スクリプト読み込み時の `pronunciations` パース処理を削除
- [x] 3.2 `script.pronunciations` から辞書へ登録する処理を削除（マルチペルソナモード）
- [x] 3.3 `script.pronunciations` から辞書へ登録する処理を削除（シングルスピーカーモード）
- [x] 3.4 LLM 生成読みを `pronunciations` に保存する処理を削除（マルチペルソナモード）
- [x] 3.5 LLM 生成読みを `pronunciations` に保存する処理を削除（シングルスピーカーモード）
- [x] 3.6 `script.pronunciations` の表示処理を削除
- [x] 3.7 `PronunciationEntry` のインポートを削除

## 4. 設定・サンプルの更新

- [x] 4.1 `config/examples/script-format-example.yaml` から `pronunciations` セクションを削除

## 5. テストの確認

- [x] 5.1 既存のテストが `pronunciations` 削除後も通ることを確認
- [x] 5.2 必要に応じてテストを更新

## 6. 検証

- [x] 6.1 `uv run ruff check .` でリントエラーがないことを確認
- [x] 6.2 `uv run mypy src/` で型エラーがないことを確認
- [x] 6.3 `uv run pytest` で全テストが通ることを確認
