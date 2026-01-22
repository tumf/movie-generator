# Change: スライド生成の最適化（並列化 + プロンプト効率化）

## Why

現在のスライド生成処理は以下の課題がある：
1. 並列リクエスト数が固定値（max_concurrent=3）でハードコーディングされており、ユーザーが調整できない
2. プロンプトが毎回フルテキストで送信されており、共通部分のオーバーヘッドがある
3. リクエスト制限に達した場合のリカバリーが不十分

この変更により、スライド生成の速度向上とコスト削減を実現する。

## What Changes

### 1. 設定による並列数制御
- `slides.max_concurrent` 設定項目を追加
- デフォルト値: 3（現在と同じ）
- 最小値: 1、最大値: 10（API制限を考慮）

### 2. プロンプト効率化
- 共通のスタイル指示を1回のシステムプロンプトで送信
- 各スライドはセクション固有のプロンプトのみ送信
- トークン使用量の削減

### 3. レート制限対応の強化
- 429エラー（Rate Limit）時の自動バックオフ
- リトライ間隔の指数関数的増加
- 最大リトライ回数の設定化

## Impact

- Affected specs:
  - `config-management`: `slides.max_concurrent` 設定追加
  - `video-generation`: スライド生成の並列処理要件更新

- Affected code:
  - `src/movie_generator/config.py`: SlidesConfig拡張
  - `src/movie_generator/slides/generator.py`: 並列処理ロジック改善
  - `src/movie_generator/cli.py`: CLIオプション追加
