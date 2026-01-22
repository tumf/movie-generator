# Change: CLIサブコマンド構造へのリファクタリング

## Why

現在のCLIは `generate` コマンド一つで全処理を実行する構造になっている。
これでは以下の問題がある:

1. **段階的な実行ができない**: スクリプト生成のみ、音声生成のみなど個別に実行したい場合に対応できない
2. **デバッグが困難**: 途中で失敗した場合、どの段階で失敗したか分かりにくい
3. **ワークフローの柔軟性がない**: 例えばスクリプトを手動で編集してから音声生成したい場合に不便

## What Changes

### コマンド構造の変更

現在:
```bash
movie-generator generate <URL|script.yaml>
movie-generator config init
```

変更後:
```bash
movie-generator script create <URL>       # スクリプト生成のみ
movie-generator audio generate <script>   # 音声生成のみ
movie-generator slides generate <script>  # スライド生成のみ
movie-generator video render <script>     # ビデオレンダリングのみ
movie-generator generate <URL|script>     # 一括実行（既存互換）
movie-generator config init               # 既存のまま
```

### 新規オプションの追加

すべてのコマンドに以下のオプションを追加:
- `--force`: 既存ファイルを強制上書き
- `--quiet`: 出力を抑制（成功時はパスのみ出力）
- `--verbose`: 詳細なデバッグ情報を出力
- `--dry-run`: 実際のファイル操作なしで動作確認

### 後方互換性

- 既存の `generate` コマンドは完全に維持
- 既存のオプション（`--scenes`, `--mcp-config`, `--allow-placeholder` 等）も維持

## Impact

- Affected specs: `cli-interface` (新規作成)
- Affected code:
  - `src/movie_generator/cli.py` - 大幅リファクタリング
  - `tests/test_scene_range.py` - 新コマンドのテスト追加
- Breaking changes: なし（後方互換性維持）
