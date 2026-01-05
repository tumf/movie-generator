# デプロイ手順書

Movie Generator Web Service を本番環境にデプロイする手順。

## 前提条件

- Docker と Docker Compose がインストールされている VPS
- Traefik がリバースプロキシとして動作している（既存の共用 VPS）
- ドメイン名が設定されている
- Let's Encrypt の証明書が Traefik で管理されている

## 環境構築

### 1. リポジトリのクローン

```bash
cd /path/to/projects
git clone <repository-url> movie-generator
cd movie-generator/web
```

### 2. 環境変数の設定

`.env` ファイルを作成:

```bash
cp .env.example .env
```

以下の項目を編集:

```bash
# PocketBase Admin
POCKETBASE_ADMIN_EMAIL=admin@yourdomain.com
POCKETBASE_ADMIN_PASSWORD=<strong-password>

# OpenRouter API Key
OPENROUTER_API_KEY=<your-api-key>

# Domain
DOMAIN=movie.yourdomain.com

# VOICEVOX Paths (Worker container内のパス)
VOICEVOX_DICT_DIR=/app/voicevox/dict
VOICEVOX_MODEL_PATH=/app/voicevox/model
VOICEVOX_ONNXRUNTIME_PATH=/app/voicevox/onnxruntime

# Service Limits (optional)
MAX_QUEUE_SIZE=10
RATE_LIMIT_PER_DAY=5
MAX_VIDEO_DURATION_MINUTES=5
MAX_CONCURRENT_JOBS=2
WORKER_POLL_INTERVAL=5
```

### 3. Traefik ネットワークの確認

Traefik が使用している external network を確認:

```bash
docker network ls | grep traefik
```

`docker-compose.yml` の `traefik-network` の名前が実際の network 名と一致しているか確認。
異なる場合は修正:

```yaml
networks:
  traefik-network:
    external: true
    name: <actual-traefik-network-name>
```

### 4. ビルドと起動

```bash
docker-compose up -d --build
```

初回ビルドには10〜15分程度かかります（VOICEVOX、Node.js のインストール等）。

### 5. PocketBase の初期化

PocketBase Admin UI にアクセスして初期設定:

```
http://your-domain:8090/_/
```

1. `.env` で設定したメールアドレスとパスワードでログイン
2. Collections を確認（`jobs` コレクションが自動作成されているはず）

### 6. 動作確認

1. Web UI にアクセス:
   ```
   https://your-domain/
   ```

2. テスト用の URL を入力して動画生成を実行

3. ログを確認:
   ```bash
   docker-compose logs -f
   ```

## アップデート手順

### コードの更新

```bash
cd /path/to/movie-generator/web
git pull
docker-compose up -d --build
```

### 環境変数の追加

新しい環境変数が追加された場合:

```bash
# .env.example から新しい変数をコピー
diff .env.example .env

# .env に追加後、再起動
docker-compose restart
```

### PocketBase スキーマの更新

マイグレーションファイルが追加された場合:

```bash
# PocketBase を再起動（マイグレーションが自動実行される）
docker-compose restart pocketbase
```

## バックアップ

### PocketBase データのバックアップ

```bash
# バックアップディレクトリを作成
mkdir -p backups

# データベースをバックアップ
docker-compose exec pocketbase tar czf /tmp/pb_backup_$(date +%Y%m%d_%H%M%S).tar.gz /pb_data
docker cp movie-generator-pocketbase:/tmp/pb_backup_*.tar.gz ./backups/

# 古いバックアップを削除
docker-compose exec pocketbase rm /tmp/pb_backup_*.tar.gz
```

### 生成動画のバックアップ

```bash
# 必要に応じて（通常は24時間で自動削除されるため不要）
docker run --rm -v movie-generator_output_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/jobs_$(date +%Y%m%d).tar.gz /data
```

### 自動バックアップの設定

cron で定期バックアップを設定:

```bash
crontab -e
```

以下を追加（毎日午前3時にバックアップ）:

```cron
0 3 * * * cd /path/to/movie-generator/web && ./scripts/backup.sh
```

バックアップスクリプト (`scripts/backup.sh`):

```bash
#!/bin/bash
set -e

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PocketBase backup
docker-compose exec -T pocketbase tar czf /tmp/pb_backup_${DATE}.tar.gz /pb_data
docker cp movie-generator-pocketbase:/tmp/pb_backup_${DATE}.tar.gz ${BACKUP_DIR}/
docker-compose exec -T pocketbase rm /tmp/pb_backup_${DATE}.tar.gz

# Keep only last 7 days
find ${BACKUP_DIR} -name "pb_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${DATE}"
```

## リストア

### PocketBase データのリストア

```bash
# サービスを停止
docker-compose stop pocketbase

# 既存データを退避
docker-compose exec pocketbase mv /pb_data /pb_data.old

# バックアップからリストア
docker cp ./backups/pb_backup_YYYYMMDD_HHMMSS.tar.gz movie-generator-pocketbase:/tmp/
docker-compose exec pocketbase tar xzf /tmp/pb_backup_YYYYMMDD_HHMMSS.tar.gz -C /
docker-compose exec pocketbase rm /tmp/pb_backup_YYYYMMDD_HHMMSS.tar.gz

# サービスを起動
docker-compose start pocketbase
```

## モニタリング

### ログの確認

```bash
# 全サービス
docker-compose logs -f

# 特定サービス
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f pocketbase

# 最新100行
docker-compose logs --tail=100 api
```

### リソース使用状況

```bash
# コンテナの状態
docker-compose ps

# リソース使用量
docker stats
```

### ディスク使用量

```bash
# 生成データのサイズ
docker exec movie-generator-worker du -sh /app/data/jobs

# PocketBase データのサイズ
docker exec movie-generator-pocketbase du -sh /pb_data
```

## トラブルシューティング

### サービスが起動しない

1. ログを確認:
   ```bash
   docker-compose logs
   ```

2. コンテナの状態を確認:
   ```bash
   docker-compose ps
   ```

3. 環境変数を確認:
   ```bash
   docker-compose config
   ```

### Worker がジョブを処理しない

1. Worker のログを確認:
   ```bash
   docker-compose logs -f worker
   ```

2. PocketBase への接続を確認:
   ```bash
   docker-compose exec worker curl http://pocketbase:8090/api/health
   ```

3. Pending jobs の確認（PocketBase Admin UI）

### Traefik でアクセスできない

1. Traefik のログを確認:
   ```bash
   docker logs <traefik-container-name>
   ```

2. Traefik のルートを確認:
   ```bash
   curl http://localhost:8080/api/http/routers  # Traefik Dashboard
   ```

3. Docker network の接続を確認:
   ```bash
   docker network inspect traefik-network
   ```

### ディスク容量不足

1. 古いジョブデータを手動削除:
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

2. Docker イメージのクリーンアップ:
   ```bash
   docker system prune -a
   ```

## セキュリティ

### 推奨設定

1. **PocketBase Admin パスワードの変更**:
   - 初回ログイン後、強力なパスワードに変更
   - 定期的にパスワードをローテーション

2. **ファイアウォール設定**:
   ```bash
   # PocketBase Admin UI へのアクセスを制限
   sudo ufw allow from <your-ip> to any port 8090
   ```

3. **環境変数の保護**:
   ```bash
   chmod 600 .env
   ```

4. **定期的なアップデート**:
   ```bash
   # システムパッケージ
   sudo apt update && sudo apt upgrade
   
   # Docker イメージ
   docker-compose pull
   docker-compose up -d
   ```

## スケーリング

### Worker を複数起動

同時処理数を増やす場合:

```yaml
# docker-compose.yml
services:
  worker:
    # ... existing config ...
    deploy:
      replicas: 3  # 3つの Worker を起動
```

または、個別に起動:

```bash
docker-compose up -d --scale worker=3
```

### リソース制限

Docker Compose でリソース制限を設定:

```yaml
services:
  worker:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## 参考リンク

- [PocketBase Documentation](https://pocketbase.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
