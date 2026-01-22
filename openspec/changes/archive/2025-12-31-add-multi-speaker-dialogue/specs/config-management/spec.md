# Configuration Management - Delta Specification

## ADDED Requirements

### Requirement: ペルソナ設定

システムは、複数の話者（ペルソナ）を設定ファイルで定義できなければならない（SHALL）。

#### Scenario: 複数ペルソナの定義
- **WHEN** 以下の設定が`personas`配列で定義されている
  ```yaml
  personas:
    - id: "zundamon"
      name: "ずんだもん"
      character: "元気で明るい東北の妖精"
      synthesizer:
        engine: "voicevox"
        speaker_id: 3
        speed_scale: 1.0
      subtitle_color: "#8FCF4F"
    - id: "metan"
      name: "四国めたん"
      character: "優しくて落ち着いた四国の妖精"
      synthesizer:
        engine: "voicevox"
        speaker_id: 2
        speed_scale: 1.0
      subtitle_color: "#FF69B4"
  ```
- **THEN** 2つのペルソナが登録される
- **AND** 各ペルソナは一意の`id`を持つ
- **AND** 各ペルソナは音声合成設定を持つ

#### Scenario: 単一ペルソナの定義
- **WHEN** `personas`配列に1つのペルソナのみが定義されている
- **THEN** 単一話者として動作する
- **AND** 既存の単一話者動画と同じ挙動になる

#### Scenario: ペルソナIDの重複エラー
- **WHEN** `personas`配列内で同じ`id`が複数定義されている
- **THEN** 設定の検証エラーが発生する
- **AND** エラーメッセージに重複した`id`が表示される

#### Scenario: 必須フィールドの検証
- **WHEN** ペルソナに`id`, `name`, `synthesizer`が含まれていない
- **THEN** 設定の検証エラーが発生する
- **AND** 不足しているフィールド名が表示される

### Requirement: 音声合成エンジンの抽象化設定

各ペルソナは、使用する音声合成エンジンとそのパラメータを`synthesizer`フィールドで指定できなければならない（SHALL）。

#### Scenario: VOICEVOX音声合成設定
- **WHEN** 以下の`synthesizer`設定が定義されている
  ```yaml
  synthesizer:
    engine: "voicevox"
    speaker_id: 3
    speed_scale: 1.0
  ```
- **THEN** VOICEVOX音声合成エンジンが使用される
- **AND** speaker_id=3で音声が生成される
- **AND** 速度倍率1.0で音声が生成される

#### Scenario: 将来的な他エンジン対応（設計のみ）
- **WHEN** `synthesizer.engine`が`"voicevox"`以外（例: `"coefont"`）の場合
- **THEN** 対応するエンジンが存在しない旨のエラーが発生する
- **AND** エラーメッセージに「サポートされていないエンジン」と表示される

### Requirement: 字幕スタイル設定

各ペルソナは、字幕の色を`subtitle_color`フィールドで指定できなければならない（SHALL）。

#### Scenario: 字幕色の設定
- **WHEN** ペルソナに`subtitle_color: "#8FCF4F"`が設定されている
- **THEN** そのペルソナの発言の字幕は緑色（#8FCF4F）で表示される

#### Scenario: 字幕色のデフォルト値
- **WHEN** `subtitle_color`が省略されている
- **THEN** デフォルト色（#FFFFFF）が使用される

#### Scenario: 無効な色コード
- **WHEN** `subtitle_color`に無効な色コード（例: "invalid"）が設定されている
- **THEN** 設定の検証エラーが発生する
- **OR** デフォルト色が使用される

### Requirement: アバター画像フィールド（将来用）

各ペルソナは、`avatar_image`フィールドを持つことができるが、現バージョンでは使用されない（SHALL support the field but not use it）。

#### Scenario: アバター画像パスの定義
- **WHEN** ペルソナに`avatar_image: "assets/zundamon.png"`が設定されている
- **THEN** 設定は正常に読み込まれる
- **AND** 現バージョンでは画像は使用されない
- **AND** 将来のバージョンで使用可能

### Requirement: ナレーション設定

システムは、ナレーションモード（単一話者または対話形式）を設定できなければならない（SHALL）。

#### Scenario: 対話モードの有効化
- **WHEN** 設定に`narration.mode: "dialogue"`が含まれている
- **THEN** 複数話者の対話形式でスクリプトが生成される
- **AND** LLMに対話形式プロンプトが使用される

#### Scenario: 単一話者モード
- **WHEN** 設定に`narration.mode: "single"`が含まれている
- **THEN** 単一話者でスクリプトが生成される
- **AND** 従来の単一話者プロンプトが使用される

#### Scenario: modeのデフォルト値
- **WHEN** `narration.mode`が省略されている
- **AND** `personas`配列に2つ以上のペルソナが定義されている
- **THEN** `"dialogue"`モードが使用される

#### Scenario: modeのデフォルト値（単一ペルソナ）
- **WHEN** `narration.mode`が省略されている
- **AND** `personas`配列に1つのペルソナのみが定義されている
- **THEN** `"single"`モードが使用される

#### Scenario: キャラクター設定の削除
- **WHEN** 対話モードが有効な場合
- **THEN** `narration.character`フィールドは無視される
- **AND** 各ペルソナの`character`フィールドが使用される

#### Scenario: スタイル設定の維持
- **WHEN** `narration.style`が設定されている
- **THEN** 単一話者・対話形式の両方で使用される
- **AND** LLMプロンプトにスタイルが反映される

## MODIFIED Requirements

None. All requirements above are new additions to the existing specification.

## REMOVED Requirements

None. The existing requirements remain valid and are extended by the ADDED and MODIFIED requirements above.

**Note**: While the original design intended to remove global audio settings (`audio.speaker_id`, `audio.speed_scale`) in favor of persona-based configuration, these fields were not formally specified in the existing spec, so no removal deltas are needed.
