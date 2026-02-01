# Change: generate コマンドのパイプライン責務分割

## Why
`src/movie_generator/cli.py` の `generate()` が肥大化しており、読みづらさ・変更容易性低下・テスト困難さを招いています。機能追加やバグ修正のたびに影響範囲が広がりやすいため、段階ごとの責務分割を提案します。

## What Changes
- `generate()` の内部処理を「入力解決（URL/スクリプト）」「スクリプト生成」「音声生成」「スライド生成」「動画レンダリング」などの段階別関数へ分割する
- 共通のエラーハンドリングとログ/進捗表示を段階境界で揃える（振る舞いは変えない）
- 既存オプション/出力ファイルの互換性を維持する

## Impact
- Affected specs: `openspec/specs/cli-interface/spec.md`
- Affected code: `src/movie_generator/cli.py`（および抽出先の新規モジュール）

## Out of Scope
- CLI 引数仕様、生成物（script/audio/slides/video）の形式や配置の変更
- 外部 API（OpenRouter/VOICEVOX/Remotion）の呼び出し仕様変更
