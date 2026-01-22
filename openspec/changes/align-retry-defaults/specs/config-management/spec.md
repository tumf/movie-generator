## ADDED Requirements
### Requirement: スライド生成リトライ設定の統一
システムは、スライド生成のリトライ回数・遅延・バックオフ係数を共通定数から取得しなければならない（SHALL）。

#### Scenario: リトライ定数の参照
- **WHEN** スライド生成でリトライ処理を行う
- **THEN** `RetryConfig` の定数を参照する
