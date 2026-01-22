# Web Progress Monitoring

動画生成ジョブの進捗をWebブラウザでリアルタイム監視する機能。

## ADDED Requirements

### Requirement: Realtime Progress Subscription

システムは、PocketBase Realtime API (SSE) を使用してジョブ進捗をリアルタイムで購読できなければならない (SHALL)。

#### Scenario: ジョブ進捗の購読開始
- **WHEN** ユーザーがジョブ詳細ページ (`/jobs/{job_id}`) にアクセスした場合
- **THEN** システムはPocketBase Realtime APIに接続し、該当ジョブレコードの変更を購読する

#### Scenario: 進捗更新の受信
- **WHEN** Workerがジョブの進捗を更新した場合
- **THEN** ブラウザはSSEイベントを受信し、UIを即座に更新する
- **AND** ポーリングによるHTTPリクエストは発生しない

#### Scenario: ジョブ完了時の購読解除
- **WHEN** ジョブのステータスが `completed` または `failed` に変更された場合
- **THEN** システムはSSE購読を解除し、接続リソースを解放する

### Requirement: SSE Connection Fallback

システムは、SSE接続が失敗した場合にHTTPポーリングにフォールバックしなければならない (SHALL)。

#### Scenario: SSE接続失敗時のフォールバック
- **WHEN** PocketBase Realtime APIへの接続が失敗した場合
- **THEN** システムはコンソールに警告を出力する
- **AND** 2秒間隔のHTTPポーリングを開始する

#### Scenario: SSE接続復旧
- **WHEN** SSE接続が切断され、PocketBase SDKが自動再接続した場合
- **THEN** リアルタイム更新が再開される
- **AND** フォールバックポーリングは停止される

### Requirement: Progress UI Elements

進捗表示UIは、JavaScript DOM操作で更新可能な要素IDを持たなければならない (SHALL)。

#### Scenario: 進捗バーの更新
- **WHEN** 進捗更新イベント (`progress` フィールド変更) を受信した場合
- **THEN** 進捗バー要素 (`#progress-bar`) の幅が更新される
- **AND** 進捗パーセント表示 (`#progress-percent`) が更新される

#### Scenario: 進捗メッセージの更新
- **WHEN** 進捗更新イベント (`progress_message` フィールド変更) を受信した場合
- **THEN** メッセージ表示要素 (`#progress-message`) のテキストが更新される

#### Scenario: ステップ表示の更新
- **WHEN** 進捗更新イベント (`current_step` フィールド変更) を受信した場合
- **THEN** ステップ表示要素 (`#current-step`) のテキストが更新される

## REMOVED Requirements

### Requirement: HTMX Polling for Progress

**Reason**: SSEベースのリアルタイム更新に置き換え

**Migration**: 
- `hx-get` および `hx-trigger="every 2s"` 属性を削除
- 代わりにPocketBase SDK購読を使用
