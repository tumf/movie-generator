## ADDED Requirements

### Requirement: ユーティリティモジュール

システムは、共通ユーティリティ関数を `src/movie_generator/utils/` パッケージで提供しなければならない（SHALL）。

#### Scenario: ファイル存在チェック
- **WHEN** `is_valid_file(path)` が呼び出される
- **THEN** ファイルが存在し、サイズが0より大きい場合に `True` を返す

#### Scenario: リトライ実行
- **WHEN** `retry_with_backoff(func, max_retries=3)` が呼び出される
- **AND** 関数が最初の2回失敗し、3回目で成功する
- **THEN** 成功結果を返し、指数バックオフで待機する

#### Scenario: サブプロセス実行
- **WHEN** `run_command_safely(command)` が呼び出される
- **AND** コマンドが失敗する
- **THEN** 標準エラー出力を含む `RuntimeError` を発生させる

### Requirement: 定数管理

システムは、すべてのマジックナンバーと文字列を `src/movie_generator/constants.py` で一元管理しなければならない（SHALL）。

#### Scenario: ビデオ定数の使用
- **WHEN** FPS値が必要な場合
- **THEN** `VideoConstants.DEFAULT_FPS` を使用する

#### Scenario: ファイル拡張子の判定
- **WHEN** ファイルタイプを判定する場合
- **THEN** `FileExtensions.YAML` などの定数セットを使用する

### Requirement: カスタム例外階層

システムは、`MovieGeneratorError` をベースとするカスタム例外階層を提供しなければならない（SHALL）。

#### Scenario: 設定エラー
- **WHEN** 設定ファイルが無効な場合
- **THEN** `ConfigurationError` を発生させる

#### Scenario: レンダリングエラー
- **WHEN** 動画レンダリングが失敗した場合
- **THEN** `RenderingError` を発生させる

#### Scenario: MCP通信エラー
- **WHEN** MCPサーバーとの通信が失敗した場合
- **THEN** `MCPError` を発生させる

### Requirement: CLI関数の責務分離

`cli.py` のコマンド関数は、単一責任の原則に従い、パイプラインステップごとに分離されたヘルパー関数を使用しなければならない（SHALL）。

#### Scenario: スクリプト読み込み
- **WHEN** `generate` コマンドが実行される
- **THEN** スクリプトの読み込み/生成は専用のヘルパー関数で処理される

#### Scenario: 音声生成
- **WHEN** 音声ファイルを生成する場合
- **THEN** `_generate_audio_files()` ヘルパー関数で処理される

#### Scenario: スライド生成
- **WHEN** スライド画像を生成する場合
- **THEN** `_generate_slides_files()` ヘルパー関数で処理される

### Requirement: 型安全性

システムは、JSON構造に対して `TypedDict` を使用し、`# type: ignore` コメントを最小化しなければならない（SHALL）。

#### Scenario: コンポジションデータ
- **WHEN** `composition.json` を生成する場合
- **THEN** `CompositionData` TypedDictに準拠した構造を使用する

#### Scenario: フレーズデータ
- **WHEN** フレーズ情報を辞書として扱う場合
- **THEN** `PhraseDict` TypedDictを使用する

### Requirement: デッドコードの排除

システムは、到達不能コードや未使用関数を含んではならない（SHALL NOT）。

#### Scenario: 到達不能コードの検出
- **WHEN** `return` 文の後にコードが存在する場合
- **THEN** そのコードは削除される

#### Scenario: 未使用関数の処理
- **WHEN** 関数がどこからも呼び出されていない場合
- **THEN** 削除するか、非推奨警告を追加する
