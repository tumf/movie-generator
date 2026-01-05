# 運用ガイド

Movie Generator Web Service の日常運用手順。

## 日常チェック

### 1. サービスの稼働確認

```bash
# コンテナの状態確認
docker-compose ps

# 期待される出力:
# NAME                          STATUS
# movie-generator-api           Up (healthy)
# movie-generator-pocketbase    Up (healthy)
# movie-generator-worker        Up
```

### 2. ログの確認

```bash
# エラーログの確認
docker-compose logs --tail=100 | grep -i error

# Worker の処理状況
docker-compose logs --tail=50 worker | grep "job"
```

### 3. ディスク容量の確認

```bash
# システム全体
df -h

# Docker volumes
docker system df -v

# ジョブデータ
docker exec movie-generator-worker du -sh /app/data/jobs
```

## 定期メンテナンス

### 週次

#### 1. ログのローテーション

```bash
# Docker のログサイズ確認
docker inspect movie-generator-api --format='{{.LogPath}}' | xargs ls -lh
docker inspect movie-generator-worker --format='{{.LogPath}}' | xargs ls -lh

# ログが大きい場合はローテーション
docker-compose restart
```

#### 2. バックアップの確認

```bash
# バックアップファイルの存在確認
ls -lh backups/

# 最新バックアップの動作確認（テスト環境で）
```

### 月次

#### 1. Docker イメージの更新

```bash
# ベースイメージの更新確認
docker-compose pull

# 更新があれば適用
docker-compose up -d --build
```

#### 2. 不要なデータのクリーンアップ

```bash
# 古い Docker イメージの削除
docker image prune -a

# 未使用のボリュームの削除（注意: データが消えます）
docker volume prune
```

#### 3. セキュリティアップデート

```bash
# システムパッケージの更新
sudo apt update && sudo apt upgrade

# 再起動が必要な場合
sudo reboot
```

## トラブル対応

### ケース1: API が応答しない

#### 症状
- Web UI にアクセスできない
- ヘルスチェックが失敗

#### 対応手順

1. コンテナの状態確認:
   ```bash
   docker-compose ps api
   ```

2. ログの確認:
   ```bash
   docker-compose logs --tail=100 api
   ```

3. 再起動:
   ```bash
   docker-compose restart api
   ```

4. それでも解決しない場合、再ビルド:
   ```bash
   docker-compose up -d --build api
   ```

### ケース2: Worker がジョブを処理しない

#### 症状
- ジョブが pending のまま進まない
- Worker ログに処理開始のメッセージがない

#### 対応手順

1. Worker のログ確認:
   ```bash
   docker-compose logs --tail=100 worker
   ```

2. PocketBase への接続確認:
   ```bash
   docker-compose exec worker curl http://pocketbase:8090/api/health
   ```

3. PocketBase の jobs 確認（Admin UI）:
   ```
   http://your-domain:8090/_/
   ```

4. Worker の再起動:
   ```bash
   docker-compose restart worker
   ```

5. 手動でジョブを1つ処理してみる:
   ```bash
   docker-compose exec worker python -c "
   import asyncio
   from main import Worker, Config
   
   async def test():
       config = Config()
       worker = Worker(config)
       jobs = await worker.pb_client.get_pending_jobs(limit=1)
       if jobs:
           await worker.process_job(jobs[0])
       await worker.pb_client.close()
   
   asyncio.run(test())
   "
   ```

### ケース3: PocketBase が起動しない

#### 症状
- PocketBase コンテナが起動しない
- Admin UI にアクセスできない

#### 対応手順

1. ログの確認:
   ```bash
   docker-compose logs pocketbase
   ```

2. データの整合性確認:
   ```bash
   # Volume の状態確認
   docker volume inspect movie-generator_pb_data
   ```

3. 再起動:
   ```bash
   docker-compose restart pocketbase
   ```

4. データベース破損の場合、バックアップからリストア（DEPLOYMENT.md 参照）

### ケース4: ディスク容量不足

#### 症状
- 動画生成が失敗する
- "No space left on device" エラー

#### 対応手順

1. 使用量の確認:
   ```bash
   df -h
   docker system df
   ```

2. 期限切れジョブの強制削除:
   ```bash
   docker-compose exec worker python -c "
   import asyncio
   from main import Config, PocketBaseClient
   
   async def force_cleanup():
       config = Config()
       client = PocketBaseClient(config.pocketbase_url)
       
       # 全ジョブを取得
       response = await client.client.get(
           '/api/collections/jobs/records',
           params={'perPage': 500}
       )
       jobs = response.json().get('items', [])
       
       # 完了・失敗ジョブを削除
       deleted = 0
       for job in jobs:
           if job['status'] in ['completed', 'failed']:
               try:
                   await client.client.delete(
                       f'/api/collections/jobs/records/{job[\"id\"]}'
                   )
                   deleted += 1
               except:
                   pass
       
       print(f'Deleted {deleted} jobs')
       await client.close()
   
   asyncio.run(force_cleanup())
   "
   ```

3. ジョブデータの手動削除:
   ```bash
   # 古いジョブディレクトリを削除
   docker exec movie-generator-worker find /app/data/jobs -type d -mtime +1 -exec rm -rf {} +
   ```

4. Docker のクリーンアップ:
   ```bash
   docker system prune -a
   ```

### ケース5: 動画生成が失敗する

#### 症状
- ジョブが failed になる
- Worker ログにエラーメッセージ

#### 対応手順

1. エラーメッセージの確認（PocketBase Admin UI または Worker ログ）

2. 一般的なエラーと対応:

   | エラー | 原因 | 対応 |
   |--------|------|------|
   | "Script generation failed" | OpenRouter API エラー | API キーの確認、クレジット残高確認 |
   | "Audio generation failed" | VOICEVOX エラー | VOICEVOX 設定の確認 |
   | "Slide generation failed" | 画像生成エラー | OpenRouter API キーの確認 |
   | "Video rendering failed" | Remotion エラー | Node.js/npm の確認 |
   | "Timeout" | 処理時間超過 | タイムアウト時間の延長 |

3. 問題のあるジョブを手動で再試行:
   - PocketBase Admin UI でジョブのステータスを "pending" に戻す
   - Worker が自動的に再処理

### ケース6: レート制限が機能しない

#### 症状
- 同じ IP から大量のリクエストが来る
- キューが常に満杯

#### 対応手順

1. レート制限の設定確認:
   ```bash
   docker-compose exec api printenv | grep RATE_LIMIT
   ```

2. IP のブロック（一時的）:
   ```bash
   # PocketBase で特定 IP のジョブを削除
   # Admin UI で client_ip でフィルタして削除
   ```

3. レート制限の強化（.env を編集）:
   ```bash
   RATE_LIMIT_PER_DAY=3  # 5 → 3 に減らす
   ```

4. サービスの再起動:
   ```bash
   docker-compose restart api
   ```

## 緊急時対応

### サービス全体の停止

```bash
# 全サービス停止
docker-compose stop

# 緊急時は強制停止
docker-compose kill
```

### サービスの再起動

```bash
# 全サービス再起動
docker-compose restart

# 特定サービスのみ
docker-compose restart api
docker-compose restart worker
docker-compose restart pocketbase
```

### ロールバック

```bash
# 以前のバージョンに戻す
git checkout <previous-commit>
docker-compose up -d --build

# データベースもロールバックする場合
# DEPLOYMENT.md の「リストア」参照
```

## モニタリングとアラート

### 推奨設定

1. **Uptime Monitor** (例: UptimeRobot)
   - URL: `https://your-domain/health`
   - 間隔: 5分
   - アラート: メール/Slack

2. **Disk Space Alert**
   ```bash
   # cron でディスク使用率をチェック
   0 * * * * df -h | awk '$5 > 80 {print "WARNING: Disk usage > 80% on "$6}' | mail -s "Disk Alert" admin@example.com
   ```

3. **Log Monitoring**
   - Grafana Loki + Promtail
   - または Elasticsearch + Kibana

## 問い合わせ対応

### よくある質問

1. **Q: 動画が生成されません**
   - A: ジョブの状態を確認してください（PocketBase Admin UI）
   - 失敗している場合はエラーメッセージを確認

2. **Q: ダウンロードリンクが切れました**
   - A: 動画は24時間で自動削除されます。再度生成してください

3. **Q: 1日の制限を超えてしまいました**
   - A: 翌日0時（UTC）にリセットされます

4. **Q: キューが満杯で使えません**
   - A: しばらく待ってから再度お試しください

### ログの収集

問い合わせ対応時に必要な情報:

```bash
# ジョブ ID から情報を収集
JOB_ID=<job-id>

# ジョブ情報（PocketBase Admin UI から）
# Worker ログ
docker-compose logs worker | grep $JOB_ID > logs_${JOB_ID}.txt

# ジョブディレクトリの確認
docker exec movie-generator-worker ls -la /app/data/jobs/$JOB_ID
```

## 連絡先

- 技術的な問題: [GitHub Issues]
- 運用に関する相談: [Slack/Email]
- 緊急連絡: [電話番号]
