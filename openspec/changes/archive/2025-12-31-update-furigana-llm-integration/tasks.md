# タスク一覧

## 1. 実装（完了済み）

- [x] 1.1 `get_words_needing_pronunciation()` メソッドを `FuriganaGenerator` に追加
- [x] 1.2 `generate_readings_with_llm()` 非同期関数を実装
- [x] 1.3 LLM用プロンプトテンプレート（`PRONUNCIATION_PROMPT`）を設計
- [x] 1.4 `clean_katakana_reading()` ユーティリティ関数を追加
- [x] 1.5 `VoicevoxSynthesizer._prepare_pronunciation_with_llm()` を実装
- [x] 1.6 CLIから音声生成時にLLM読み生成を呼び出し

## 2. テスト（完了済み）

- [x] 2.1 `get_words_needing_pronunciation()` のユニットテスト
- [x] 2.2 漢字・英単語の抽出テスト
- [x] 2.3 かな専用文字列の除外テスト

## 3. 仕様化

- [x] 3.1 `audio-furigana` スペックにLLM統合要件を追加
