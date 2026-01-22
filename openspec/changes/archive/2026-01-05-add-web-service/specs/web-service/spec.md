# Web Service Specification

一般ユーザー向けの動画生成 Web サービス。

## ADDED Requirements

### Requirement: Web UI によるジョブ投入

システムは、ブラウザから URL を入力して動画生成をリクエストできる Web UI を提供しなければならない (SHALL)。

#### Scenario: URL を入力して動画生成を開始
- **GIVEN** ユーザーがトップページにアクセスしている
- **WHEN** ブログ URL を入力して送信ボタンをクリック
- **THEN** ジョブが作成され、ジョブ詳細ページにリダイレクトされる

#### Scenario: 無効な URL を入力
- **GIVEN** ユーザーがトップページにアクセスしている
- **WHEN** 無効な URL（空、不正な形式）を入力して送信
- **THEN** エラーメッセージが表示され、ジョブは作成されない

---

### Requirement: 進捗表示

システムは、ジョブの処理状況をリアルタイムで表示しなければならない (SHALL)。

#### Scenario: 処理中の進捗確認
- **GIVEN** ジョブが processing 状態である
- **WHEN** ユーザーがジョブ詳細ページを表示している
- **THEN** 進捗率（0-100%）と現在のステップが 2 秒ごとに更新される

#### Scenario: 完了後の表示
- **GIVEN** ジョブが completed 状態である
- **WHEN** ユーザーがジョブ詳細ページを表示している
- **THEN** ダウンロードリンクが表示される

#### Scenario: 失敗時の表示
- **GIVEN** ジョブが failed 状態である
- **WHEN** ユーザーがジョブ詳細ページを表示している
- **THEN** エラーメッセージが表示される

---

### Requirement: 動画ダウンロード

システムは、生成された動画をダウンロードする機能を提供しなければならない (SHALL)。

#### Scenario: 動画のダウンロード
- **GIVEN** ジョブが completed 状態である
- **WHEN** ダウンロードリンクをクリック
- **THEN** MP4 ファイルがダウンロードされる

#### Scenario: 期限切れ動画のアクセス
- **GIVEN** ジョブの expires_at を過ぎている
- **WHEN** ダウンロードを試みる
- **THEN** 404 エラーが返される

---

### Requirement: IP ベースレート制限

システムは、abuse 防止のため IP アドレスごとに利用回数を制限しなければならない (MUST)。

#### Scenario: 制限内のリクエスト
- **GIVEN** ユーザーの IP が過去 24 時間に 4 回リクエスト済み
- **WHEN** 新しいジョブ作成をリクエスト
- **THEN** ジョブが正常に作成される（5 回/日の上限内）

#### Scenario: 制限超過のリクエスト
- **GIVEN** ユーザーの IP が過去 24 時間に 5 回リクエスト済み
- **WHEN** 新しいジョブ作成をリクエスト
- **THEN** 429 Too Many Requests が返される

---

### Requirement: キュー上限

システムは、過負荷防止のため待機中ジョブの上限を設けなければならない (MUST)。

#### Scenario: キューに空きがある
- **GIVEN** pending 状態のジョブが 9 件以下
- **WHEN** 新しいジョブ作成をリクエスト
- **THEN** ジョブが正常に作成される

#### Scenario: キューが満杯
- **GIVEN** pending 状態のジョブが 10 件
- **WHEN** 新しいジョブ作成をリクエスト
- **THEN** 503 Service Unavailable が返される

---

### Requirement: 動画長制限

システムは、処理時間とストレージ節約のため動画の長さを制限しなければならない (MUST)。

#### Scenario: 制限内のコンテンツ
- **GIVEN** 入力 URL のコンテンツから 10 セクション以下のスクリプトが生成される
- **WHEN** 動画生成を実行
- **THEN** 正常に動画が生成される（約 5 分以内）

#### Scenario: 制限超過のコンテンツ
- **GIVEN** 入力 URL のコンテンツから 11 セクション以上のスクリプトが生成される
- **WHEN** 動画生成を実行
- **THEN** 最初の 10 セクションのみで動画が生成される

---

### Requirement: 自動クリーンアップ

システムは、ストレージ節約のため期限切れジョブを自動削除しなければならない (MUST)。

#### Scenario: 期限切れジョブの削除
- **GIVEN** ジョブの expires_at が現在時刻を過ぎている
- **WHEN** クリーンアップタスクが実行される
- **THEN** ジョブレコードと関連ファイルが削除される

---

### Requirement: 同時処理数制限

システムは、VPS リソース保護のため同時処理数を制限しなければならない (MUST)。

#### Scenario: 同時処理枠に空きがある
- **GIVEN** processing 状態のジョブが 1 件
- **WHEN** Worker が新しい pending ジョブを検出
- **THEN** そのジョブの処理を開始する

#### Scenario: 同時処理枠が満杯
- **GIVEN** processing 状態のジョブが 2 件
- **WHEN** Worker が新しい pending ジョブを検出
- **THEN** そのジョブは pending 状態のまま待機する

---

### Requirement: ジョブ状態管理

システムは、ジョブを明確な状態遷移に従って管理しなければならない (SHALL)。

#### Scenario: 正常な状態遷移（成功）
- **GIVEN** ジョブが作成された
- **WHEN** 処理が正常に完了する
- **THEN** pending → processing → completed と遷移する

#### Scenario: 正常な状態遷移（失敗）
- **GIVEN** ジョブが processing 状態である
- **WHEN** 処理中にエラーが発生する
- **THEN** failed に遷移し、error_message が設定される

---

### Requirement: PocketBase Admin UI

システムは、運用者が PocketBase Admin UI でジョブを管理できる機能を提供しなければならない (SHALL)。

#### Scenario: ジョブ一覧の確認
- **GIVEN** 運用者が PocketBase Admin UI にログイン済み
- **WHEN** jobs コレクションを表示
- **THEN** 全ジョブの状態、URL、作成日時を確認できる

#### Scenario: ジョブの手動削除
- **GIVEN** 運用者が PocketBase Admin UI にログイン済み
- **WHEN** 特定のジョブを削除
- **THEN** ジョブレコードが削除される（ファイルは別途削除が必要）

---

### Requirement: 環境変数による設定

システムは、各種制限値を環境変数で設定可能にしなければならない (SHALL)。

#### Scenario: 制限値のカスタマイズ
- **GIVEN** 環境変数 `RATE_LIMIT_PER_DAY=10` が設定されている
- **WHEN** サービスが起動する
- **THEN** IP レート制限が 10 回/日に設定される

#### Scenario: デフォルト値の適用
- **GIVEN** 環境変数が設定されていない
- **WHEN** サービスが起動する
- **THEN** デフォルト値（5 回/日など）が適用される
