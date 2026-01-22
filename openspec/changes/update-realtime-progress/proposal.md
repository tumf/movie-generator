# Change: 動画生成進捗のリアルタイム更新

## Why

現在のフロントエンドは2秒間隔のHTTPポーリングで進捗を取得している。
これにより以下の問題が発生している：

1. **不要なHTTPリクエスト**: 変更がなくても2秒ごとにリクエストが発生
2. **サーバー負荷**: 同時接続ユーザーが増えるとAPI負荷が線形に増加
3. **遅延**: 最大2秒の遅延が発生（平均1秒）
4. **リソース消費**: クライアント・サーバー双方でCPU/ネットワーク帯域を消費

PocketBaseはRealtime API（Server-Sent Events）を標準でサポートしており、
これを活用することでプッシュ型の進捗通知が可能になる。

## What Changes

- **フロントエンド**: HTMXポーリングからPocketBase JavaScript SDK + SSEに変更
- **API**: `/jobs/{job_id}/status-html` エンドポイントは廃止（HTML直接更新）
- **Worker**: 変更なし（既にPocketBaseに進捗を書き込んでいる）
- **テンプレート**: job.htmlでSSE購読ロジックを追加

### 技術的アプローチ

1. PocketBase JavaScript SDKをCDN経由で読み込み
2. `pb.collection('jobs').subscribe(job_id, callback)` で特定ジョブを購読
3. `update` イベント受信時にDOM更新（進捗バー、メッセージ等）
4. ジョブ完了時に `unsubscribe` で購読解除

## Impact

- 影響するファイル:
  - `web/api/templates/job.html` - SSE購読ロジック追加
  - `web/api/templates/partials/job_status.html` - DOM ID追加（JavaScript操作用）
  - `web/api/templates/base.html` - PocketBase SDK追加
  - `web/api/routes/web_routes.py` - status-htmlエンドポイント廃止

- 新規依存関係:
  - PocketBase JavaScript SDK (CDN: `https://unpkg.com/pocketbase`)

- **BREAKING**: `/jobs/{job_id}/status-html` エンドポイント廃止
  - 現在のHTMXポーリングは非推奨となる
