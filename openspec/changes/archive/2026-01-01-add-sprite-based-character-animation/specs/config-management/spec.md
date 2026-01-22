## ADDED Requirements

### Requirement: キャラクター画像設定（Phase 1: 静的アバター）

システムは、ペルソナ設定でキャラクター画像（ベース画像）を指定可能にしなければならない（SHALL）。

**Note**: この要件は `add-static-avatar-overlay` の `avatar_image` 機能を統合し、`character_image` として拡張します。

#### Scenario: キャラクター画像の設定

- **GIVEN** 設定ファイルに以下のペルソナ設定がある:
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      character_image: "assets/characters/zundamon/base.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_image` フィールドに `"assets/characters/zundamon/base.png"` が設定される
- **AND** ファイルパスの存在チェックが実行される

#### Scenario: avatar_image の後方互換性（alias）

- **GIVEN** 設定ファイルに以下がある（旧フィールド名）:
  ```yaml
  personas:
    - id: "zundamon"
      avatar_image: "assets/avatars/zundamon.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_image` フィールドに値が設定される
- **AND** `avatar_image` は `character_image` の alias として動作する

### Requirement: スプライト画像設定（Phase 2: リップシンク・まばたき）

システムは、ペルソナ設定でスプライト画像（口開き、目閉じ）を指定可能にしなければならない（SHALL）。

#### Scenario: 口開き画像の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_image: "assets/characters/zundamon/base.png"
      mouth_open_image: "assets/characters/zundamon/mouth_open.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `mouth_open_image` フィールドに設定される
- **AND** リップシンクアニメーションに使用される

#### Scenario: 目閉じ画像の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_image: "assets/characters/zundamon/base.png"
      eye_close_image: "assets/characters/zundamon/eye_close.png"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `eye_close_image` フィールドに設定される
- **AND** まばたきアニメーションに使用される

#### Scenario: 画像未設定時のデフォルト動作

- **GIVEN** ペルソナ設定で `character_image` が設定されていない
- **WHEN** 設定が読み込まれる
- **THEN** `character_image` は `None` である
- **AND** キャラクター表示はスキップされる（静的アバターのフォールバック）

#### Scenario: 画像パスが存在しない場合のエラー

- **GIVEN** `character_image: "nonexistent/file.png"` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** ValidationError が発生する
- **AND** エラーメッセージに不正なパスが含まれる

### Requirement: キャラクター表示位置の設定

システムは、ペルソナごとにキャラクターの表示位置（左/右/中央）を指定可能にしなければならない（SHALL）。

#### Scenario: 左側表示の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_position: "left"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_position` は `"left"` である
- **AND** キャラクターは画面左側に表示される

#### Scenario: 右側表示の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "metan"
      character_position: "right"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_position` は `"right"` である
- **AND** キャラクターは画面右側に表示される

#### Scenario: 中央表示の設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "single_speaker"
      character_position: "center"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `character_position` は `"center"` である
- **AND** キャラクターは画面中央に表示される

#### Scenario: デフォルト位置（未設定時）

- **GIVEN** `character_position` が設定されていない
- **WHEN** 設定が読み込まれる
- **THEN** `character_position` のデフォルト値は `"left"` である

#### Scenario: 不正な位置設定のエラー

- **GIVEN** `character_position: "top"` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** ValidationError が発生する
- **AND** エラーメッセージに有効な値（"left", "right", "center"）が示される

### Requirement: アニメーションスタイルの設定（Phase 3）

システムは、ペルソナごとにアニメーションスタイル（バウンス/揺れ/静止）を指定可能にしなければならない（SHALL）。

#### Scenario: バウンスアニメーションの設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      animation_style: "bounce"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `animation_style` は `"bounce"` である
- **AND** 話している間、キャラクターが上下にバウンスする

#### Scenario: 揺れアニメーションの設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "metan"
      animation_style: "sway"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `animation_style` は `"sway"` である
- **AND** キャラクターが微妙に左右に揺れる

#### Scenario: 静止スタイルの設定

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "static_char"
      animation_style: "static"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** PersonaConfig の `animation_style` は `"static"` である
- **AND** キャラクターは揺れやバウンスなしで表示される（リップシンク・まばたきのみ）

#### Scenario: デフォルトアニメーション（未設定時）

- **GIVEN** `animation_style` が設定されていない
- **WHEN** 設定が読み込まれる
- **THEN** `animation_style` のデフォルト値は `"sway"` である

#### Scenario: 不正なアニメーションスタイルのエラー

- **GIVEN** `animation_style: "rotate"` が設定されている
- **WHEN** 設定バリデーションが実行される
- **THEN** ValidationError が発生する
- **AND** エラーメッセージに有効な値（"bounce", "sway", "static"）が示される

### Requirement: マルチスピーカー設定でのキャラクター配置自動調整

システムは、複数ペルソナが設定されている場合、デフォルトの `character_position` を自動調整しなければならない（SHALL）。

#### Scenario: 2人話者のデフォルト配置

- **GIVEN** 設定ファイルに2つのペルソナがあり、`character_position` が未設定である:
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
    - id: "metan"
      name: "四国めたん"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** 1番目のペルソナの `character_position` は `"left"` である
- **AND** 2番目のペルソナの `character_position` は `"right"` である

#### Scenario: 3人以上の話者の配置

- **GIVEN** 設定ファイルに3つのペルソナがある
- **WHEN** 設定が読み込まれる
- **THEN** すべてのペルソナの `character_position` はデフォルト `"left"` である
- **AND** 話者切り替え時に入れ替わりアニメーションが適用される

#### Scenario: 手動設定が優先される

- **GIVEN** 設定ファイルに以下が含まれる:
  ```yaml
  personas:
    - id: "zundamon"
      character_position: "right"
    - id: "metan"
      character_position: "left"
  ```
- **WHEN** 設定が読み込まれる
- **THEN** 手動設定が自動調整より優先される
- **AND** ずんだもんは右側、めたんは左側に表示される
