## 1. Implementation
- [x] 1.1 `script create` と `generate` で重複している URL 取得/スクリプト生成処理を抽出する（検証: 両コマンドが同一の共通関数を利用することを確認）

## 2. Tests
- [x] 2.1 `script create` の既存挙動（既存 script のスキップ等）をモックで検証するテストを追加する（検証: `uv run pytest -k "script create" -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] src/movie_generator/cli.py: create() uses Path.cwd() and help text says default current directory; update default output to ./output per openspec/changes/refactor-cli-create-dedup/specs/cli-interface/spec.md
