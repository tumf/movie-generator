# Movie Generator Web Service

ブログ記事から自動で動画を生成する無料Webサービス。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Traefik (既存・共用)                      │
│               movie.example.com → api:8000                  │
└─────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   FastAPI       │  │   PocketBase    │  │    Worker       │
│   (api)         │  │   (db)          │  │                 │
│                 │  │                 │  │                 │
│ - HTML 配信     │  │ - jobs DB       │  │ - ジョブ監視    │
│ - フォーム処理  │◀─│ - Realtime API  │─▶│ - 動画生成      │
│ - 進捗表示     │  │ - Admin UI      │  │ - 進捗更新      │
│ (htmx polling)  │  │   (/admin)      │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Volumes      │
                    │ - pb_data       │
                    │ - output/       │
                    └─────────────────┘
```

## デプロイ手順

### 1. 環境変数の設定

`.env` ファイルを作成:

```bash
cp .env.example .env
```

必須の環境変数を設定:

- `OPENROUTER_API_KEY`: OpenRouter API キー
- `DOMAIN`: 公開するドメイン名
- `POCKETBASE_ADMIN_EMAIL`: PocketBase 管理者メールアドレス
- `POCKETBASE_ADMIN_PASSWORD`: PocketBase 管理者パスワード
- `VOICEVOX_*`: VOICEVOX 関連のパス

### 2. Docker Compose でビルド・起動

```bash
cd web
docker-compose up -d --build
```

### 3. PocketBase の初期化

PocketBase の Admin UI にアクセス:

```
http://your-domain:8090/_/
```

初回アクセス時に管理者アカウントを作成してください。

### 4. 動作確認

ブラウザで Web サービスにアクセス:

```
https://your-domain/
```

## ローカル開発

### API のみ起動

```bash
cd web/api
uv pip install -e .
uvicorn main:app --reload --port 8000
```

### Worker のみ起動

```bash
cd web/worker
python main.py
```

### PocketBase のみ起動

```bash
docker run -d \
  -p 8090:8090 \
  -v pb_data:/pb_data \
  ghcr.io/muchobien/pocketbase:latest
```

## 利用制限

| 項目 | 制限値 | 環境変数 |
|------|--------|----------|
| 同時処理数 | 2 件 | `MAX_CONCURRENT_JOBS` |
| 動画の長さ上限 | 5 分 | `MAX_VIDEO_DURATION_MINUTES` |
| 1日の利用回数 | 5 回/IP | `RATE_LIMIT_PER_DAY` |
| 動画保存期間 | 24 時間 | (固定) |
| キュー待機上限 | 10 件 | `MAX_QUEUE_SIZE` |

## 運用

### ログ確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f pocketbase
```

### PocketBase Admin UI

ジョブの状態確認、手動削除などが可能:

```
http://your-domain:8090/_/
```

### 期限切れジョブのクリーンアップ

Worker が自動的に1時間ごとに実行します。手動で実行する場合:

```bash
docker-compose exec worker python -c "
import asyncio
from main import Config, PocketBaseClient

async def cleanup():
    config = Config()
    client = PocketBaseClient(config.pocketbase_url)
    count = await client.delete_expired_jobs()
    print(f'Deleted {count} expired jobs')
    await client.close()

asyncio.run(cleanup())
"
```

### バックアップ

PocketBase データのバックアップ:

```bash
docker-compose exec pocketbase tar czf /pb_data/backup-$(date +%Y%m%d).tar.gz /pb_data/*.db
docker cp movie-generator-pocketbase:/pb_data/backup-*.tar.gz ./backups/
```

## トラブルシューティング

### Worker がジョブを処理しない

1. Worker ログを確認:
   ```bash
   docker-compose logs -f worker
   ```

2. PocketBase に接続できているか確認:
   ```bash
   docker-compose exec worker curl http://pocketbase:8090/api/health
   ```

### 動画生成が失敗する

1. Worker ログでエラー内容を確認
2. VOICEVOX の設定を確認 (`VOICEVOX_*` 環境変数)
3. OpenRouter API キーが有効か確認
4. ディスク容量を確認

### PocketBase Admin UI にアクセスできない

1. PocketBase が起動しているか確認:
   ```bash
   docker-compose ps pocketbase
   ```

2. ポート 8090 が開放されているか確認

## テスト

### API テスト

```bash
cd web/api
uv run pytest
```

### Worker テスト

```bash
cd web/worker
uv run pytest
```

### E2E テスト

```bash
cd web
uv run pytest tests/test_e2e.py
```

## ディレクトリ構造

```
web/
├── api/                      # FastAPI アプリケーション
│   ├── main.py               # アプリエントリーポイント
│   ├── models.py             # Pydantic モデル
│   ├── config.py             # 設定
│   ├── pocketbase_client.py  # PocketBase クライアント
│   ├── routes/               # ルート定義
│   │   ├── api_routes.py     # API エンドポイント
│   │   └── web_routes.py     # HTML ページ
│   ├── templates/            # Jinja2 テンプレート
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── job.html
│   │   ├── error.html
│   │   └── partials/
│   │       └── job_status.html
│   ├── static/               # 静的ファイル
│   ├── Dockerfile
│   └── pyproject.toml
├── worker/                   # バックグラウンド Worker
│   ├── main.py               # Worker エントリーポイント
│   ├── Dockerfile
│   └── pyproject.toml
├── pocketbase/               # PocketBase 設定
│   └── pb_migrations/        # マイグレーション
│       └── 1704412800_created_jobs.js
├── docker-compose.yml        # Docker Compose 設定
├── .env.example              # 環境変数サンプル
└── README.md                 # このファイル
```

## ライセンス

親プロジェクトと同じライセンスを適用。

## Docker Build Instructions

### Method 1: Mount Local VOICEVOX (Recommended - No Download)

If you have VOICEVOX installed locally (at `~/.local/share/voicevox/`), mount it into the Docker container:

```bash
cd web
docker compose build
docker compose up -d
```

The compose file automatically mounts `~/.local/share/voicevox` to `/host/voicevox` in the container.

### Method 2: Download Assets Manually

If you don't have VOICEVOX locally, download assets to `assets/voicevox/`:

```bash
./download-voicevox.sh
```

This downloads VOICEVOX (dict, onnxruntime, models) to `assets/voicevox/`.

Then build Docker images:
```bash
cd web
docker compose build
docker compose up -d
```
docker compose up -d
```

### Troubleshooting

**ERROR: VOICEVOX assets not found**

Dockerfile checks in order:
1. `/app/assets/voicevox/` (pre-downloaded to project)
2. `/host/voicevox/` (mounted from host at `~/.local/share/voicevox/`)

If both are missing, you need to:
1. Run `./download-voicevox.sh` (downloads to `assets/voicevox/`), OR
2. Ensure `~/.local/share/voicevox/` exists (for mounting)

**GitHub API rate limit**

The `download-voicevox.sh` script uses `gh` CLI to avoid rate limits. If you still hit limits:
1. Authenticate with `gh auth login`
2. Wait 1 hour for rate limit reset
3. Run the script again
