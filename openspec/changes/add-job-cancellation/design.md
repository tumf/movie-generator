# 設計ドキュメント: ジョブキャンセル機能

## アーキテクチャ概要

ジョブキャンセル機能は、以下の3つのレイヤーで実装されます：

```
[Web UI (HTMX)] → [FastAPI Endpoint] → [PocketBase Database]
                                              ↓
                                        [Worker (Polling)]
```

### データフロー

1. **ユーザー操作**: UIのキャンセルボタンをクリック
2. **API呼び出し**: HTMX が `POST /api/jobs/{job_id}/cancel` を呼び出し
3. **DB更新**: PocketBaseのジョブレコードが `cancelled` ステータスに更新
4. **Worker検出**: Workerが次のステータスチェック時にキャンセルを検出
5. **クリーンアップ**: Workerが処理を中断し、部分的なファイルを削除

## コンポーネント設計

### 1. PocketBase Client (`pocketbase_client.py`)

#### 新規メソッド: `cancel_job(job_id: str)`

```python
async def cancel_job(self, job_id: str) -> dict[str, Any]:
    """Cancel a job if it is in pending or processing state.
    
    Args:
        job_id: Job ID to cancel
        
    Returns:
        Updated job record
        
    Raises:
        HTTPException: If job is not cancellable (completed/failed/cancelled)
                       or job does not exist
    """
    # 1. Get current job
    job = await self.get_job(job_id)
    
    # 2. Check if cancellable
    if job["status"] not in ["pending", "processing"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel a {job['status']} job"
        )
    
    # 3. Update to cancelled
    return await self.update_job(
        job_id,
        {
            "status": "cancelled",
            "completed_at": datetime.now(UTC).isoformat() + "Z",
        }
    )
```

**設計判断**:
- キャンセル可能かのチェックはクライアント側で実施（ビジネスロジック）
- PocketBaseには単純なステータス更新のみを依頼
- エラーハンドリングは FastAPI レイヤーに委譲

### 2. API Routes (`api_routes.py`)

#### 新規エンドポイント: `POST /api/jobs/{job_id}/cancel`

```python
@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, request: Request) -> dict[str, str]:
    """Cancel a pending or processing job.
    
    Args:
        job_id: Job ID to cancel
        request: FastAPI request (for accessing pb_client)
        
    Returns:
        {"status": "cancelled"}
        
    Raises:
        HTTPException: 400 if not cancellable, 404 if not found
    """
    pb_client: PocketBaseClient = request.app.state.pb_client
    
    try:
        await pb_client.cancel_job(job_id)
        return {"status": "cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**設計判断**:
- RESTful設計に従い、POST メソッドを使用（状態変更操作）
- シンプルなレスポンス形式（ステータスのみ）
- エラーはHTTP標準ステータスコードで返却

### 3. Web UI (`job_status.html`)

#### キャンセルボタンの追加

```html
<!-- Cancel Button (only for pending/processing) -->
{% if job.status in ["pending", "processing"] %}
<button
    class="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-6 rounded-lg transition duration-200"
    hx-post="/api/jobs/{{ job.id }}/cancel"
    hx-confirm="このジョブをキャンセルしますか？"
    hx-target="#job-status"
    hx-swap="outerHTML"
>
    🚫 ジョブをキャンセル
</button>
{% endif %}
```

**設計判断**:
- HTMX の `hx-confirm` で確認ダイアログを実装（JavaScriptレス）
- `hx-target="#job-status"` でステータス部分のみを更新（ページリロード不要）
- 赤色ボタンで危険な操作であることを視覚的に示す

#### キャンセルステータスの表示改善

```html
{% elif job.status == "cancelled" %}
<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
    <p class="text-gray-800 font-medium">🚫 このジョブはキャンセルされました</p>
    <p class="text-sm text-gray-700 mt-2">
        ジョブは正常にキャンセルされました。新しいジョブを作成できます。
    </p>
    <a href="/" class="inline-block mt-3 text-blue-600 hover:underline">
        → 新しいジョブを作成
    </a>
</div>
{% endif %}
```

**設計判断**:
- ユーザーフレンドリーなメッセージで次のアクションを促す
- トップページへのリンクで次のジョブ作成を容易に

### 4. Worker (`main.py`)

#### キャンセル検出ロジック

```python
async def process_job(self, job: dict[str, Any]) -> None:
    """Process a single job with cancellation support."""
    job_id = job["id"]
    
    try:
        # Update to processing
        await self.pb_client.update_job(job_id, {"status": "processing", ...})
        
        # Generate video with periodic cancellation checks
        video_path = await self.generator.generate_video(
            job_id, 
            url, 
            update_progress,
            check_cancelled=lambda: self._is_cancelled(job_id)  # NEW
        )
        
        # ... completion logic
        
    except JobCancelledException:  # NEW
        logger.info(f"Job {job_id} was cancelled")
        await self._cleanup_cancelled_job(job_id)
        # Do NOT update status (already cancelled by API)
        
    except Exception as e:
        # ... existing error handling
```

#### キャンセルチェックヘルパー

```python
async def _is_cancelled(self, job_id: str) -> bool:
    """Check if job is cancelled.
    
    Args:
        job_id: Job ID to check
        
    Returns:
        True if job status is 'cancelled'
    """
    job = await self.pb_client.get_job(job_id)
    return job["status"] == "cancelled"
```

#### クリーンアップロジック

```python
async def _cleanup_cancelled_job(self, job_id: str) -> None:
    """Clean up files for a cancelled job.
    
    Args:
        job_id: Job ID to clean up
    """
    job_dir = self.config.job_data_dir / job_id
    
    if job_dir.exists():
        logger.info(f"Cleaning up cancelled job {job_id}")
        shutil.rmtree(job_dir)
        logger.info(f"Cleaned up cancelled job {job_id}")
```

**設計判断**:
- 各処理ステップの前にキャンセルをチェック（細粒度の中断）
- 専用例外 `JobCancelledException` でキャンセルを伝播
- クリーンアップは専用メソッドで責任分離
- ステータス更新はしない（API側で既に更新済み）

## エラーハンドリング

### 競合状態の防止

**問題**: ユーザーがキャンセルボタンをクリックした直後にジョブが完了した場合

**解決策**:
1. PocketBaseの楽観的ロック（`updated` フィールドの自動更新）
2. API側で現在のステータスを確認してからキャンセル
3. Workerはステータスを上書きしない

### 部分的なファイル削除

**問題**: キャンセル時に一部のファイルが使用中で削除できない

**解決策**:
1. ベストエフォートで削除を試行
2. 削除失敗はログに記録するが、エラーとしない
3. 有効期限切れジョブの定期削除で最終的にクリーンアップ

### ネットワークエラー

**問題**: Worker がステータスをチェックできない（PocketBase接続エラー）

**解決策**:
1. リトライロジックを追加（最大3回）
2. リトライ失敗時は処理を継続（安全側に倒す）
3. 次のチェックポイントで再度確認

## パフォーマンス考慮事項

### キャンセルチェック頻度

- **スクリプト生成前**: 1回
- **音声生成**: 各フレーズ処理前（1-5秒間隔）
- **スライド生成**: 各スライド生成前（10-30秒間隔）
- **動画レンダリング**: Remotionのフレームバッチごと（5-10秒間隔）

**トレードオフ**:
- 高頻度: 即座のキャンセルだが、PocketBaseへのリクエスト増加
- 低頻度: リクエスト削減だが、キャンセル反映が遅延

**選択**: 中程度の頻度（各ステップの境界）
- ユーザー体験とシステム負荷のバランス
- 10秒以内のキャンセル反映で十分

### データベースアクセス最適化

```python
# BAD: 毎回フルジョブレコードを取得
job = await self.pb_client.get_job(job_id)
is_cancelled = job["status"] == "cancelled"

# GOOD: ステータスのみを取得（将来的な改善）
status = await self.pb_client.get_job_status(job_id)
is_cancelled = status == "cancelled"
```

**現時点**: フルレコード取得（実装の単純さ優先）
**将来**: PocketBase API の `fields` パラメータでステータスのみ取得

## セキュリティ考慮事項

### 認証・認可

**現状**: 認証なし（ジョブIDのみで操作可能）

**リスク**: 他人のジョブをキャンセル可能

**軽減策**（将来実装）:
1. ジョブ作成時にセッションIDを記録
2. キャンセル時にセッションIDを検証
3. または、ジョブIDを推測困難なUUIDv4に変更（現状で十分）

### レート制限

**現状**: なし

**将来実装**: FastAPIのミドルウェアでレート制限
- 同一IPから1分間に最大10回のキャンセルリクエスト

## テスト戦略

### ユニットテスト

1. `test_pocketbase_client.py::test_cancel_job`
   - pendingジョブのキャンセル
   - processingジョブのキャンセル
   - completed/failed/cancelledジョブのキャンセル失敗

2. `test_api_routes.py::test_cancel_endpoint`
   - 正常系: 200レスポンス
   - 異常系: 400/404レスポンス

### 統合テスト

3. `test_worker.py::test_cancel_during_processing`
   - モックジョブでキャンセルをシミュレート
   - クリーンアップの検証

### E2Eテスト

4. 手動テスト
   - ブラウザでキャンセルボタンをクリック
   - Workerログでキャンセル検出を確認
   - ジョブディレクトリの削除を確認

## ロールバック計画

万が一、本機能に重大なバグがあった場合のロールバック手順：

1. **UIの無効化**: `job_status.html` からキャンセルボタンを削除
2. **APIの無効化**: エンドポイントを404を返すように変更
3. **Workerの無効化**: キャンセルチェックロジックをスキップ

各レイヤーは独立しているため、段階的なロールバックが可能。

## 将来の拡張

### フェーズ2: バッチキャンセル

複数のジョブを一括でキャンセル

```
POST /api/jobs/cancel-batch
{
  "job_ids": ["abc123", "def456", ...]
}
```

### フェーズ3: キャンセル理由の記録

ユーザーがキャンセル理由を選択できるように

```
POST /api/jobs/{job_id}/cancel
{
  "reason": "wrong_url" | "too_slow" | "duplicate" | "other"
}
```

### フェーズ4: キャンセル統計

キャンセル率の追跡とダッシュボード表示

## 参考資料

- [HTMX Confirm Pattern](https://htmx.org/attributes/hx-confirm/)
- [PocketBase API - Update Record](https://pocketbase.io/docs/api-records/#update-record)
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
