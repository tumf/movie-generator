# Change: コードベース構造のリファクタリング

## Why

コードベース全体を分析した結果、以下の問題が特定されました：

1. **コードの重複** - ファイル存在チェック、リトライロジック、サブプロセス実行パターンが複数箇所で重複
2. **長すぎる関数** - `cli.py::generate()` が409行、責務が過大
3. **エラーハンドリングの不統一** - bare except句、例外型の混在
4. **マジックナンバー/文字列** - FPS値30、ディレクトリ名などがハードコード
5. **型安全性の不足** - `type: ignore` が9箇所、TypedDictの欠如

これらの問題は保守性、テスト容易性、コードの再利用性に影響を与えています。

## What Changes

### フェーズ1: ユーティリティモジュールの作成
- 新規 `src/movie_generator/utils/` パッケージを作成
  - `filesystem.py` - ファイル存在チェック、パス操作
  - `retry.py` - 指数バックオフ付きリトライロジック
  - `subprocess.py` - サブプロセス実行ヘルパー
  - `text.py` - テキスト処理ユーティリティ

### フェーズ2: 定数の集約
- 新規 `src/movie_generator/constants.py` を作成
  - `VideoConstants` - FPS、解像度
  - `FileExtensions` - サポートファイル拡張子
  - `ProjectPaths` - 標準ディレクトリ名
  - `RetryConfig` - リトライパラメータ

### フェーズ3: 例外体系の整理
- 新規 `src/movie_generator/exceptions.py` を作成
  - `MovieGeneratorError` - ベース例外
  - `ConfigurationError` - 設定関連エラー
  - `RenderingError` - レンダリングエラー
  - `MCPError` - MCP通信エラー

### フェーズ4: CLI関数の分割
- `cli.py::generate()` を小さな関数に分割
- `cli.py::parse_scene_range()` をサブ関数に分割

### フェーズ5: デッドコードの削除
- `video/remotion_renderer.py:109-122` の到達不能コード削除
- 未使用関数の削除または警告追加

### フェーズ6: 型安全性の向上
- TypedDictの導入（CompositionData、PhraseDict）
- `type: ignore` の削減

## Impact

- 影響する仕様: なし（内部リファクタリングのみ）
- 影響するコード:
  - `src/movie_generator/cli.py`
  - `src/movie_generator/slides/generator.py`
  - `src/movie_generator/audio/voicevox.py`
  - `src/movie_generator/video/remotion_renderer.py`
  - `src/movie_generator/project.py`
  - `src/movie_generator/assets/downloader.py`
  - `src/movie_generator/mcp/client.py`

## リスク

- **低リスク**: 後方互換性を維持
- すべての変更は段階的に実装可能
- 各フェーズ後にテストスイート実行で検証

## 成功基準

- `uv run pytest` 全テスト通過
- `uv run mypy src/` エラーなし
- `uv run ruff check .` 警告なし
- コードカバレッジ維持または向上
