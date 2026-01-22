# Tasks: 動画生成進捗のリアルタイム更新

## 1. 準備

- [ ] 1.1 PocketBase Realtime APIの動作確認（ローカル環境）
- [ ] 1.2 Traefik経由でのSSE動作確認

## 2. フロントエンド実装

- [ ] 2.1 `base.html`: PocketBase JavaScript SDKをCDNから読み込み
- [ ] 2.2 `job_status.html`: DOM要素にIDを追加（JavaScript操作用）
- [ ] 2.3 `job.html`: SSE購読ロジックを実装
  - PocketBase SDKの初期化
  - `pb.collection('jobs').subscribe(jobId, callback)` で購読開始
  - `update` イベントでDOM更新
  - 完了/失敗時に `unsubscribe` で購読解除
- [ ] 2.4 フォールバック機構の実装（SSE失敗時のポーリング）

## 3. バックエンド変更

- [ ] 3.1 `web_routes.py`: `/jobs/{job_id}/status-html` エンドポイントを非推奨化
  - 即座に削除せず、フォールバック用に維持
- [ ] 3.2 `job.html`: HTMXポーリング属性を削除

## 4. テスト

- [ ] 4.1 手動テスト: 進捗更新のリアルタイム反映を確認
- [ ] 4.2 手動テスト: ジョブ完了時の購読解除を確認
- [ ] 4.3 手動テスト: SSE接続断→再接続を確認
- [ ] 4.4 手動テスト: フォールバックポーリングを確認

## 5. クリーンアップ

- [ ] 5.1 動作確認後、ポーリングエンドポイントを削除
- [ ] 5.2 ドキュメント更新（POCKETBASE.mdにRealtime使用例を追加）

## 依存関係

- タスク2.3は2.1, 2.2に依存
- タスク3.2は2.3完了後に実施
- タスク5.xはタスク4.x完了後に実施
