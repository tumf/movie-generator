# Design: 動画生成進捗のリアルタイム更新

## Context

### 現在のアーキテクチャ

```
[Worker] --update--> [PocketBase] <--poll (2s)--> [API] <--poll (2s)--> [Browser/HTMX]
```

- Worker: ジョブ進捗をPocketBaseに書き込み
- API: `/jobs/{job_id}/status-html` でHTMLフラグメントを返す
- Browser: HTMXが2秒ごとにポーリング

### 問題点

1. ポーリング間隔（2秒）による遅延
2. 不要なHTTPリクエスト（変更がなくてもリクエスト）
3. 同時接続数に比例するサーバー負荷

## Goals

- ポーリングをやめてプッシュ型のリアルタイム更新を実現
- 進捗変更時のみUIを更新
- サーバー負荷を削減
- ユーザー体験の向上（即時反映）

## Non-Goals

- 認証付きRealtime接続（現在の実装では不要）
- 複数ジョブの同時監視
- オフライン対応

## Decisions

### 1. SSE (Server-Sent Events) を採用

PocketBaseのRealtime APIはSSEベースで実装されており、
WebSocketと比較して以下の利点がある：

- HTTP/2との親和性が高い
- 標準のHTTPインフラで動作（プロキシ、ロードバランサー対応）
- PocketBase SDKが透過的に扱う

**代替案**: 自前のWebSocket実装
- 却下理由: PocketBaseが既にSSEを提供しており、追加実装不要

### 2. PocketBase JavaScript SDKを使用

```javascript
import PocketBase from 'pocketbase';
const pb = new PocketBase('http://localhost:8090');

pb.collection('jobs').subscribe(jobId, (e) => {
    if (e.action === 'update') {
        updateProgressUI(e.record);
    }
});
```

**代替案**: 直接EventSource APIを使用
- 却下理由: PocketBase固有のプロトコル（clientId管理等）をSDKが隠蔽

### 3. フォールバック機構

SSE接続失敗時はHTTPポーリングにフォールバック：

```javascript
pb.collection('jobs').subscribe(jobId, handler)
    .catch(() => {
        console.warn('SSE connection failed, falling back to polling');
        startPolling();
    });
```

### 4. UI更新方式

HTMX部分更新からVanilla JavaScript DOM操作に変更：

```javascript
function updateProgressUI(record) {
    document.getElementById('progress-bar').style.width = `${record.progress}%`;
    document.getElementById('progress-text').textContent = record.progress_message;
    document.getElementById('progress-step').textContent = record.current_step;
    
    if (record.status === 'completed' || record.status === 'failed') {
        pb.collection('jobs').unsubscribe(jobId);
        updateCompletedUI(record);
    }
}
```

## Risks / Trade-offs

### Risk: SSE接続断

- **軽減策**: 自動再接続（PocketBase SDKの標準機能）
- **軽減策**: フォールバックポーリング

### Risk: ブラウザ互換性

- SSEはIE11以外のモダンブラウザでサポート
- IE11は対象外（2025年時点でサポート終了済み）

### Trade-off: HTMX依存の削減

- 利点: 軽量化（HTMXのポーリング機能不要）
- 欠点: Vanilla JSでのDOM操作が必要
- 判断: 進捗更新は単純なDOM操作であり、許容範囲

## Migration Plan

1. **Phase 1**: 新しいSSEベースのUI実装を追加
2. **Phase 2**: テスト・検証
3. **Phase 3**: 既存ポーリング実装を削除

ロールバック: Phase 1-2の期間中は両方の実装が共存可能

## Open Questions

- [ ] Traefik経由でSSEが正しく動作するか確認が必要
  - 通常は問題ないが、タイムアウト設定の確認が必要
