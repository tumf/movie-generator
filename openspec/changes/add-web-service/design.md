# Design: Web サービス アーキテクチャ

## Context

movie-generator を一般ユーザー向けの無料 Web サービスとして公開する。
既存の共用 VPS（Docker Compose + Traefik）上にデプロイする。
早期リリースを優先し、シンプルな構成を採用する。

## Goals / Non-Goals

### Goals
- ブラウザから URL 入力だけで動画生成
- 進捗状況のリアルタイム表示
- 生成完了後のダウンロード
- 無料サービスとしての利用制限

### Non-Goals
- ユーザー認証（MVP では IP ベースのレート制限のみ）
- カスタム設定（キャラクター選択、速度調整など）
- スクリプト編集機能
- 複数動画の履歴管理

## Decisions

### 1. モノレポ構成

**決定**: 既存リポジトリに `web/` ディレクトリを追加

**理由**:
- パッケージ管理の複雑さを回避（非公開リポジトリ間の依存が不要）
- 同一リポジトリ内で `movie_generator` を直接 import 可能
- CLI の変更と Web の変更を同時に行える

**ディレクトリ構造**:
```
movie-generator/
├── src/movie_generator/      # 既存（変更なし）
├── web/
│   ├── api/                  # FastAPI アプリ
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   ├── templates/
│   │   └── static/
│   ├── worker/               # ジョブ処理
│   │   └── main.py
│   ├── pocketbase/           # PocketBase 設定
│   │   └── pb_migrations/
│   └── docker-compose.yml
└── pyproject.toml
```

### 2. 3コンテナ構成

**決定**: FastAPI + PocketBase + Worker の分離

**コンテナ構成**:
```yaml
services:
  api:
    build: ./api
    # FastAPI: HTML配信 + ジョブ作成 API
    
  pocketbase:
    image: ghcr.io/muchobien/pocketbase
    # DB + Realtime + Admin UI
    
  worker:
    build: ./worker
    # ジョブポーリング + movie-generator 実行
```

**理由**:
- 責務の明確な分離
- Worker のスケールアウトが容易（将来）
- PocketBase の Admin UI で運用監視が可能

### 3. ジョブキュー設計

**決定**: PocketBase のテーブルをジョブキューとして使用

**jobs コレクション**:
```javascript
{
  id: "string (auto)",
  url: "string",                    // 入力URL
  status: "pending" | "processing" | "completed" | "failed" | "cancelled",
  progress: 0-100,                  // 進捗率
  progress_message: "string",       // 例: "音声生成中..."
  current_step: "string",           // 例: "audio", "slides", "video"
  video_path: "string | null",      // 完成した動画のパス
  video_size: "number | null",      // ファイルサイズ (bytes)
  error_message: "string | null",   // エラー時のメッセージ
  client_ip: "string",              // レート制限用
  created: "datetime",
  updated: "datetime",
  started_at: "datetime | null",    // 処理開始時刻
  completed_at: "datetime | null",  // 処理完了時刻
  expires_at: "datetime",           // 自動削除時刻
}
```

**ステータス遷移**:
```
pending → processing → completed
                    → failed
        → cancelled (キューオーバー時)
```

### 4. 進捗更新方式

**決定**: htmx ポーリング（2秒間隔）

**理由**:
- PocketBase Realtime より実装がシンプル
- JavaScript をほぼ書かずに済む
- 2秒間隔で十分なユーザー体験

**実装**:
```html
<div hx-get="/jobs/{{ job_id }}/status" 
     hx-trigger="every 2s"
     hx-swap="innerHTML">
  <!-- 進捗表示 -->
</div>
```

### 5. 利用制限の実装

**決定**: FastAPI ミドルウェア + PocketBase クエリ

| 制限 | 実装方式 |
|------|----------|
| IP レート制限 | FastAPI ミドルウェア (slowapi) |
| 同時処理数 | Worker 側でセマフォ制御 |
| 動画長制限 | スクリプト生成時にセクション数制限 |
| キュー上限 | ジョブ作成前に pending 件数確認 |
| 保存期間 | cron による定期削除 |

### 6. ファイル管理

**決定**: ローカルボリューム + 24時間後自動削除

**ディレクトリ構成**:
```
/app/data/
├── jobs/
│   └── {job_id}/
│       ├── script.yaml
│       ├── audio/
│       ├── slides/
│       └── output.mp4
└── pocketbase/
    └── pb_data/
```

**自動削除**:
- Worker の定期タスクまたは別 cron コンテナ
- `expires_at < now()` のジョブを削除
- 関連ファイルも同時に削除

## Risks / Trade-offs

### Risk 1: 処理時間が長い（5-10分）
- **影響**: ユーザー離脱の可能性
- **緩和**: 進捗表示の充実、完了通知（将来）

### Risk 2: VPS リソース不足
- **影響**: 同時処理数の制限
- **緩和**: 同時処理 2件、キュー上限 10件

### Risk 3: abuse（大量リクエスト）
- **影響**: サービス停止
- **緩和**: IP レート制限、キュー上限

### Risk 4: VOICEVOX のセットアップ複雑
- **影響**: Docker イメージサイズ大
- **緩和**: マルチステージビルド、レイヤーキャッシュ

## Migration Plan

既存コードへの変更はないため、マイグレーション不要。
新規 `web/` ディレクトリを追加するのみ。

## Open Questions

1. **ドメイン名**: どのドメインで公開するか？
2. **HTTPS 証明書**: Traefik の Let's Encrypt 設定は既存？
3. **モニタリング**: ログ収集・アラートの要件は？
4. **バックアップ**: PocketBase データのバックアップ頻度は？
