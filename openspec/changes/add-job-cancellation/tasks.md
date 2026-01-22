# タスクリスト: ジョブキャンセル機能

## フェーズ1: API実装

### 1. PocketBaseClientにキャンセルメソッドを追加

**ファイル**: `web/api/pocketbase_client.py`

**実装内容**:
```python
async def cancel_job(self, job_id: str) -> dict[str, Any]:
    """Cancel a job if it is in pending or processing state."""
```

**完了条件**:
- メソッドが定義されている (`web/api/pocketbase_client.py` 内)
- `pending` または `processing` のジョブを `cancelled` に更新できる
- 完了時刻 (`completed_at`) を設定する
- それ以外のステータスの場合は HTTPException を発生させる

**検証方法**:
```bash
# ユニットテストで確認
uv run pytest web/tests/test_pocketbase_client.py::test_cancel_job -v
```

### 2. キャンセルAPIエンドポイントを追加

**ファイル**: `web/api/routes/api_routes.py`

**実装内容**:
```python
@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, request: Request) -> dict[str, str]:
    """Cancel a pending or processing job."""
```

**完了条件**:
- エンドポイントが追加されている (`web/api/routes/api_routes.py`)
- `PocketBaseClient.cancel_job()` を呼び出す
- 成功時は `{"status": "cancelled"}` を返す
- 失敗時は適切なHTTPエラーを返す (400: キャンセル不可, 404: ジョブが存在しない)

**検証方法**:
```bash
# 統合テストで確認
uv run pytest web/tests/test_api_routes.py::test_cancel_job -v

# 手動確認
curl -X POST http://localhost:8000/api/jobs/{job_id}/cancel
```

## フェーズ2: UI実装

### 3. キャンセルボタンをジョブステータスUIに追加

**ファイル**: `web/api/templates/partials/job_status.html`

**実装内容**:
- `pending` または `processing` ステータスの場合にキャンセルボタンを表示
- HTMXを使用してキャンセルAPIを呼び出し
- `hx-confirm` でキャンセル確認ダイアログを表示

**完了条件**:
- キャンセルボタンが `pending`/`processing` ジョブに表示される
- ボタンクリック時に確認ダイアログが表示される
- キャンセル後にステータスが更新される
- `completed`/`failed`/`cancelled` ジョブではボタンが表示されない

**検証方法**:
```bash
# ブラウザで確認
# 1. http://localhost:8000 でジョブを作成
# 2. ジョブ詳細ページでキャンセルボタンが表示されることを確認
# 3. キャンセルボタンをクリックして確認ダイアログが表示されることを確認
# 4. 確認後、ステータスが "キャンセル" に変わることを確認
```

### 4. キャンセル後のフィードバックメッセージを改善

**ファイル**: `web/api/templates/partials/job_status.html`

**実装内容**:
- キャンセルされたジョブに対して、より詳細なメッセージを表示
- 例: "ジョブは正常にキャンセルされました。新しいジョブを作成できます。"

**完了条件**:
- キャンセルステータスのメッセージが更新されている (line 139-142)
- メッセージが分かりやすい

**検証方法**:
```bash
# ブラウザでキャンセルされたジョブを表示し、メッセージを確認
```

## フェーズ3: Worker対応

### 5. Workerにキャンセル検出ロジックを追加

**ファイル**: `web/worker/main.py`

**実装内容**:
- `process_job()` メソッド内で各処理ステップの前にジョブステータスをチェック
- `cancelled` ステータスを検出したら即座に処理を中断
- クリーンアップ処理を実行（部分的なファイルの削除など）

**完了条件**:
- `process_job()` が定期的にジョブステータスをチェックする
- `cancelled` を検出したら `MovieGeneratorCancelled` 例外を発生させる
- 例外ハンドラでクリーンアップを実行する
- ログに "Job {job_id} was cancelled" を出力

**検証方法**:
```bash
# 統合テスト
uv run pytest web/tests/test_worker.py::test_cancel_during_processing -v

# 手動確認
# 1. Workerを起動
# 2. ジョブを作成
# 3. 処理中にキャンセル
# 4. Workerログで "Job XXX was cancelled" を確認
docker logs movie-generator-worker 2>&1 | grep "cancelled"
```

### 6. キャンセル時のクリーンアップロジックを実装

**ファイル**: `web/worker/main.py`

**実装内容**:
- キャンセルされたジョブのディレクトリ (`/app/data/jobs/{job_id}`) を削除
- 部分的に生成されたファイル（script.yaml, audio, slides など）を削除

**完了条件**:
- `_cleanup_cancelled_job(job_id)` メソッドが追加されている
- ジョブディレクトリが削除される
- ログに "Cleaned up cancelled job {job_id}" を出力

**検証方法**:
```bash
# キャンセル後にジョブディレクトリが削除されることを確認
docker exec movie-generator-worker ls /app/data/jobs/{job_id}
# Should return: No such file or directory
```

## フェーズ4: テストとドキュメント

### 7. ユニットテストを追加

**ファイル**: `web/tests/test_pocketbase_client.py`, `web/tests/test_api_routes.py`

**実装内容**:
- `test_cancel_pending_job()` - pendingジョブのキャンセル
- `test_cancel_processing_job()` - processingジョブのキャンセル
- `test_cancel_completed_job_fails()` - completedジョブのキャンセル失敗
- `test_cancel_nonexistent_job()` - 存在しないジョブのキャンセル失敗

**完了条件**:
- 全てのテストがパスする
- カバレッジが追加したコードの90%以上

**検証方法**:
```bash
uv run pytest web/tests/test_pocketbase_client.py web/tests/test_api_routes.py -v
```

### 8. 統合テストを追加

**ファイル**: `web/tests/test_worker.py`

**実装内容**:
- `test_cancel_during_processing()` - 処理中のキャンセル
- `test_cleanup_after_cancel()` - キャンセル後のクリーンアップ

**完了条件**:
- 全てのテストがパスする
- 実際のWorkerの動作をシミュレート

**検証方法**:
```bash
uv run pytest web/tests/test_worker.py::test_cancel_during_processing -v
```

### 9. ドキュメントを更新

**ファイル**: `web/README.md`

**実装内容**:
- ジョブキャンセル機能の説明を追加
- APIエンドポイントのドキュメント更新
- UIの使い方を説明

**完了条件**:
- README.mdに "ジョブのキャンセル" セクションが追加されている
- APIエンドポイント一覧に `POST /api/jobs/{job_id}/cancel` が記載されている

**検証方法**:
```bash
# READMEを確認
cat web/README.md | grep -A 10 "キャンセル"
```

## フェーズ5: E2Eテスト

### 10. E2Eテストシナリオを実行

**実装内容**:
- 手動でE2Eテストを実施

**テストシナリオ**:

1. **Pendingジョブのキャンセル**
   - ジョブを作成
   - 処理開始前にキャンセル
   - ステータスが `cancelled` になることを確認

2. **Processingジョブのキャンセル**
   - ジョブを作成
   - 処理中にキャンセル
   - Workerがログに "cancelled" を出力
   - ジョブディレクトリが削除されることを確認

3. **Completedジョブのキャンセル不可**
   - 完了したジョブのページを開く
   - キャンセルボタンが表示されないことを確認

**完了条件**:
- 全てのシナリオが正常に動作する
- UIが期待通りに表示される
- エラーケースが適切に処理される

**検証方法**:
```bash
# Docker環境で実際に操作して確認
docker-compose up -d
# ブラウザで http://localhost:8000 を開いてテスト
```

## 依存関係

- タスク2は1に依存
- タスク3-4は2に依存（API実装後にUI実装）
- タスク5-6は並行実行可能
- タスク7-8は1-6完了後に実行
- タスク9は1-8完了後に実行
- タスク10は全タスク完了後に実行

## 見積もり

- フェーズ1: 2時間
- フェーズ2: 1.5時間
- フェーズ3: 2時間
- フェーズ4: 2時間
- フェーズ5: 1時間

**合計**: 約8.5時間
