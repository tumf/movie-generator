# Tasks: Web サービス実装

## 1. プロジェクト構成

- [x] 1.1 `web/` ディレクトリ構造を作成
- [x] 1.2 `web/api/` の pyproject.toml を作成（FastAPI 依存）
- [x] 1.3 `web/worker/` の pyproject.toml を作成
- [x] 1.4 Docker Compose ファイルを作成（api, pocketbase, worker）

## 2. PocketBase セットアップ

- [x] 2.1 PocketBase コンテナ設定
- [x] 2.2 jobs コレクションのマイグレーション定義
- [x] 2.3 Admin 認証設定

## 3. FastAPI アプリケーション

- [x] 3.1 FastAPI アプリ基本構成（main.py）
- [x] 3.2 Pydantic モデル定義（models.py）
- [x] 3.3 PocketBase クライアントユーティリティ
- [x] 3.4 ジョブ作成 API エンドポイント（POST /jobs）
- [x] 3.5 ジョブ状態取得 API エンドポイント（GET /jobs/{id}/status）
- [x] 3.6 動画ダウンロード API エンドポイント（GET /jobs/{id}/download）

## 4. フロントエンド（テンプレート）

- [x] 4.1 ベーステンプレート（base.html）
- [x] 4.2 トップページ（index.html）- URL 入力フォーム
- [x] 4.3 ジョブ詳細ページ（job.html）- 進捗表示 + ダウンロード
- [x] 4.4 エラーページ（error.html）
- [x] 4.5 CSS スタイリング（Tailwind CDN）
- [x] 4.6 htmx による進捗ポーリング実装

## 5. Worker 実装

- [x] 5.1 PocketBase ポーリングループ
- [x] 5.2 movie-generator 呼び出しラッパー
- [x] 5.3 進捗コールバック実装（PocketBase 更新）
- [x] 5.4 エラーハンドリング
- [x] 5.5 同時実行数制御（セマフォ）
- [x] 5.6 期限切れジョブのクリーンアップ

## 6. 利用制限

- [x] 6.1 IP ベースレート制限（slowapi）
- [x] 6.2 キュー上限チェック
- [x] 6.3 動画長制限（セクション数上限）

## 7. Docker 構成

- [x] 7.1 api 用 Dockerfile
- [x] 7.2 worker 用 Dockerfile（VOICEVOX, Node.js 含む）
- [x] 7.3 Traefik ラベル設定
- [x] 7.4 ボリューム設定（pb_data, output）
- [x] 7.5 環境変数設定（.env.example）

## 8. テスト

- [ ] 8.1 API エンドポイントのユニットテスト
- [ ] 8.2 Worker のユニットテスト
- [ ] 8.3 E2E テスト（ジョブ作成→完了）

## 9. ドキュメント

- [x] 9.1 デプロイ手順書
- [x] 9.2 環境変数の説明
- [x] 9.3 運用ガイド（ログ確認、障害対応）

## 依存関係

```
1.x → 2.x → 3.x → 4.x → 8.x
         → 5.x → 8.x
         → 6.x
    → 7.x → 9.x
```

- Phase 1 (1-2): プロジェクト構成 + DB
- Phase 2 (3-5): アプリケーション実装
- Phase 3 (6-7): 制限 + Docker
- Phase 4 (8-9): テスト + ドキュメント
