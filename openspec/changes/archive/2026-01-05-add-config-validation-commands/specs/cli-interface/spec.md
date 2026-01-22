## ADDED Requirements

### Requirement: Config Validate Command

CLI は `config validate` サブコマンドを提供しなければならない（SHALL）。
このコマンドは設定ファイル（YAML）を検証し、エラーがあれば報告する。

コマンドは以下のオプションを受け付ける:
- `<path>`: 検証する設定ファイルのパス（必須）
- `--quiet, -q`: エラーのみ表示

#### Scenario: 有効な設定ファイルの検証

- **GIVEN** 有効な YAML 形式の設定ファイル `config.yaml` が存在する
- **WHEN** ユーザーが `movie-generator config validate config.yaml` を実行する
- **THEN** 「✓ Configuration is valid」と表示される
- **AND** 終了コード 0 で終了する

#### Scenario: YAML 構文エラーの検出

- **GIVEN** YAML 構文が不正な設定ファイルが存在する
- **WHEN** ユーザーが `movie-generator config validate invalid.yaml` を実行する
- **THEN** YAML パースエラーメッセージが表示される
- **AND** エラー行番号が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: スキーマバリデーションエラーの検出

- **GIVEN** YAML 構文は正しいがスキーマに違反する設定ファイルが存在する
  ```yaml
  audio:
    speaker_id: "invalid"  # 数値であるべき
  ```
- **WHEN** ユーザーが `movie-generator config validate invalid-schema.yaml` を実行する
- **THEN** バリデーションエラーメッセージが表示される
- **AND** 不正なフィールド名が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: 参照ファイル不在エラーの検出

- **GIVEN** 設定ファイルに存在しないファイルへのパスが含まれる
  ```yaml
  video:
    background:
      type: "image"
      path: "/nonexistent/background.png"
  ```
- **WHEN** ユーザーが `movie-generator config validate config-missing-file.yaml` を実行する
- **THEN** 「File not found」エラーメッセージが表示される
- **AND** 不正なパスが含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: ペルソナ ID 重複エラーの検出

- **GIVEN** 設定ファイルに重複するペルソナ ID が含まれる
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      ...
    - id: "zundamon"  # 重複
      name: "ずんだもん2号"
      ...
  ```
- **WHEN** ユーザーが `movie-generator config validate config-duplicate-id.yaml` を実行する
- **THEN** 「Duplicate persona ID」エラーメッセージが表示される
- **AND** 重複した ID が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: ファイルが存在しない場合

- **GIVEN** 指定されたパスにファイルが存在しない
- **WHEN** ユーザーが `movie-generator config validate nonexistent.yaml` を実行する
- **THEN** 「File not found」エラーメッセージが表示される
- **AND** 終了コード 1 で終了する

---

### Requirement: Script Validate Command

CLI は `script validate` サブコマンドを提供しなければならない（SHALL）。
このコマンドはスクリプトファイル（YAML）を検証し、エラーがあれば報告する。

コマンドは以下のオプションを受け付ける:
- `<path>`: 検証するスクリプトファイルのパス（必須）
- `--config, -c <path>`: 設定ファイル（persona_id 参照検証用、オプション）
- `--quiet, -q`: エラーのみ表示

#### Scenario: 有効なスクリプトファイルの検証

- **GIVEN** 有効なスクリプトファイル `script.yaml` が存在する
- **WHEN** ユーザーが `movie-generator script validate script.yaml` を実行する
- **THEN** 「✓ Script is valid」と表示される
- **AND** セクション数と総 narration 数が表示される
- **AND** 終了コード 0 で終了する

#### Scenario: 必須フィールド不足の検出

- **GIVEN** `title` フィールドがないスクリプトファイルが存在する
- **WHEN** ユーザーが `movie-generator script validate invalid.yaml` を実行する
- **THEN** 「Missing required field: title」エラーメッセージが表示される
- **AND** 終了コード 1 で終了する

#### Scenario: 空の sections の検出

- **GIVEN** `sections` が空のスクリプトファイルが存在する
  ```yaml
  title: "Test"
  description: "Test video"
  sections: []
  ```
- **WHEN** ユーザーが `movie-generator script validate empty-sections.yaml` を実行する
- **THEN** 「Script has no sections」警告メッセージが表示される
- **AND** 終了コード 0 で終了する（警告のみ）

#### Scenario: 不正な narrations 形式の検出

- **GIVEN** narrations に不正な形式のエントリが含まれるスクリプト
  ```yaml
  sections:
    - title: "Section 1"
      narrations:
        - invalid_field: "test"  # text フィールドがない
  ```
- **WHEN** ユーザーが `movie-generator script validate invalid-narration.yaml` を実行する
- **THEN** 「Invalid narration format」エラーメッセージが表示される
- **AND** 問題のあるセクション番号が含まれる
- **AND** 終了コード 1 で終了する

#### Scenario: 存在しない persona_id の検出（config 指定時）

- **GIVEN** スクリプトファイルに存在しない persona_id が含まれる
- **AND** 設定ファイルにペルソナが定義されている
- **WHEN** ユーザーが `movie-generator script validate script.yaml --config config.yaml` を実行する
- **THEN** 「Unknown persona_id: xxx」警告メッセージが表示される
- **AND** 定義されている persona_id の一覧が表示される
- **AND** 終了コード 0 で終了する（警告のみ）

#### Scenario: config 未指定時の persona_id 検証スキップ

- **GIVEN** スクリプトファイルに persona_id が含まれる
- **WHEN** ユーザーが `movie-generator script validate script.yaml` を実行する（--config なし）
- **THEN** persona_id の参照妥当性チェックはスキップされる
- **AND** 構文とスキーマの検証のみ実行される
