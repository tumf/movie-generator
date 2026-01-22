## ADDED Requirements

### Requirement: スライド生成並列数の設定

システムは、スライド生成の並列リクエスト数を設定で制御可能にしなければならない（SHALL）。

#### Scenario: 並列数のデフォルト値

- **GIVEN** 設定ファイルに `slides.max_concurrent` が設定されていない
- **WHEN** スライド生成が実行される
- **THEN** 並列リクエスト数は `3` である

#### Scenario: カスタム並列数の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  slides:
    max_concurrent: 5
  ```
- **WHEN** 設定が読み込まれる
- **THEN** `SlidesConfig.max_concurrent` は `5` である
- **AND** スライド生成時に最大5つのリクエストが同時に実行される

#### Scenario: 並列数の最小値バリデーション

- **GIVEN** 設定ファイルに `slides.max_concurrent: 0` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** `ValidationError` が発生する
- **AND** エラーメッセージに最小値 `1` が示される

#### Scenario: 並列数の最大値バリデーション

- **GIVEN** 設定ファイルに `slides.max_concurrent: 15` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** `ValidationError` が発生する
- **AND** エラーメッセージに最大値 `10` が示される

### Requirement: スライド生成リトライ設定

システムは、スライド生成のリトライ動作を設定で制御可能にしなければならない（SHALL）。

#### Scenario: リトライ回数のデフォルト値

- **GIVEN** 設定ファイルに `slides.max_retries` が設定されていない
- **WHEN** スライド生成が実行される
- **THEN** 最大リトライ回数は `3` である

#### Scenario: リトライ間隔のデフォルト値

- **GIVEN** 設定ファイルに `slides.retry_delay` が設定されていない
- **WHEN** スライド生成が実行される
- **THEN** 初期リトライ間隔は `2.0` 秒である

#### Scenario: カスタムリトライ設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  slides:
    max_retries: 5
    retry_delay: 3.0
  ```
- **WHEN** 設定が読み込まれる
- **THEN** `SlidesConfig.max_retries` は `5` である
- **AND** `SlidesConfig.retry_delay` は `3.0` である

#### Scenario: リトライ回数の最小値バリデーション

- **GIVEN** 設定ファイルに `slides.max_retries: 0` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** `ValidationError` が発生する
- **AND** エラーメッセージに最小値 `1` が示される

#### Scenario: リトライ回数の最大値バリデーション

- **GIVEN** 設定ファイルに `slides.max_retries: 15` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** `ValidationError` が発生する
- **AND** エラーメッセージに最大値 `10` が示される
