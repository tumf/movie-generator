# Video Rendering Specification

## Purpose

This specification defines the video rendering system for the movie generator application. The system manages composition data generation and Remotion-based video rendering with support for per-persona subtitle styling. This enables multi-speaker videos with distinct visual styling for each character's dialogue.
## Requirements
### Requirement: Add Speaker Information to composition.json

The generated composition.json SHALL include speaker information for each phrase.

#### Scenario: composition.json with Speaker Information
- **GIVEN** a phrase list:
  ```python
  [
    Phrase(text="やっほー！", persona_id="zundamon", persona_name="ずんだもん"),
    Phrase(text="こんにちは", persona_id="metan", persona_name="四国めたん")
  ]
  ```
- **AND** persona configuration:
  ```yaml
  personas:
    - id: "zundamon"
      subtitle_color: "#8FCF4F"
    - id: "metan"
      subtitle_color: "#FF69B4"
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** composition.json includes:
  ```json
  {
    "phrases": [
      {
        "text": "やっほー！",
        "personaId": "zundamon",
        "personaName": "ずんだもん",
        "subtitleColor": "#8FCF4F",
        ...
      },
      {
        "text": "こんにちは",
        "personaId": "metan",
        "personaName": "四国めたん",
        "subtitleColor": "#FF69B4",
        ...
      }
    ]
  }
  ```

#### Scenario: composition.json for Single Speaker
- **GIVEN** all phrases have the same persona
- **WHEN** `update_composition_json()` is called
- **THEN** all phrases have the same `personaId` and `subtitleColor`
- **AND** the video appears identical to traditional single-speaker videos

### Requirement: Render Per-Persona Subtitle Styles

Remotion SHALL apply different subtitle styles for each speaker.

#### Scenario: Apply Subtitle Color
- **GIVEN** a phrase's `subtitleColor` is `"#8FCF4F"`
- **WHEN** the subtitle is rendered
- **THEN** the subtitle border color is `#8FCF4F` (green)

#### Scenario: Switch Subtitle Colors for Multiple Speakers
- **GIVEN** phrase 0's `subtitleColor` is `"#8FCF4F"`
- **AND** phrase 1's `subtitleColor` is `"#FF69B4"`
- **WHEN** the video is rendered
- **THEN** phrase 0's subtitle is displayed in green
- **AND** phrase 1's subtitle is displayed in pink

### Requirement: Prepare Persona Name Display (Future Use)

The composition.json SHALL include personaName, but it is not displayed in the current version.

#### Scenario: Persona Name Field Exists
- **GIVEN** composition.json includes `personaName`
- **WHEN** it is loaded by Remotion
- **THEN** the field exists but is not displayed on screen
- **AND** display functionality can be added in future versions

### Requirement: Reserve Avatar Image Field (Future Use)

The composition.json SHALL reserve an avatarImage field, but it is not used in the current version.

#### Scenario: Reserve Avatar Image Field
- **GIVEN** a persona has `avatar_image` configured
- **WHEN** composition.json is generated
- **THEN** the `avatarImage` field is not included (or is `null`)
- **AND** it can be implemented in future versions

### Requirement: Maintain Backward Compatibility

The system SHALL work with composition.json files that lack speaker information.

#### Scenario: composition.json Without Speaker Information
- **GIVEN** composition.json does not include `personaId` or `subtitleColor`
- **WHEN** it is loaded by Remotion
- **THEN** subtitles are displayed in the default color (#FFFFFF)
- **AND** no error occurs

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/video-rendering/spec.md`.

### Requirement: トランジション使用時の音声同期

スライド間トランジションを使用する場合、音声/字幕シーケンスはトランジションによるフレームオーバーラップを考慮して配置されなければならない（SHALL）。

#### Scenario: トランジションありで音声が最後まで再生される

- **GIVEN** 以下のフレーズデータがある:
  - フレーズ1: duration=2.0秒（60フレーム）、スライドA
  - フレーズ2: duration=2.0秒（60フレーム）、スライドA
  - フレーズ3: duration=2.0秒（60フレーム）、スライドB
  - フレーズ4: duration=2.0秒（60フレーム）、スライドB
- **AND** トランジション設定が `duration_frames: 15` である
- **WHEN** 動画がレンダリングされる
- **THEN** 動画総フレーム数は `240 - 15 = 225`フレームである（トランジション1回分のオーバーラップ）
- **AND** フレーズ1の音声は0フレームから開始する
- **AND** フレーズ2の音声は60フレームから開始する
- **AND** フレーズ3の音声は `120 - 15 = 105`フレームから開始する（トランジション後）
- **AND** フレーズ4の音声は `180 - 15 = 165`フレームから開始する
- **AND** すべての音声が完全に再生される

#### Scenario: トランジションなしの場合の互換性

- **GIVEN** トランジション設定が `type: none` または `duration_frames: 0` である
- **WHEN** 動画がレンダリングされる
- **THEN** 音声シーケンスの開始位置は元のタイミング通りである
- **AND** 動画総フレーム数はフレーズ総フレーム数と一致する

#### Scenario: 複数トランジションがある場合

- **GIVEN** 3つの異なるスライドがあり、トランジションが2回発生する
- **AND** トランジション設定が `duration_frames: 15` である
- **WHEN** 動画がレンダリングされる
- **THEN** 最初のスライドグループの音声はオフセットなし
- **AND** 2番目のスライドグループの音声は15フレーム前にシフト
- **AND** 3番目のスライドグループの音声は30フレーム前にシフト
- **AND** すべての音声が完全に再生される

### Requirement: キャラクター画像情報を composition.json に含める（Phase 1-3）

生成される composition.json は、各フレーズのキャラクター画像情報を含まなければならない（SHALL）。

**Phase 1**: ベース画像のみ
**Phase 2**: ベース画像 + 口開き + 目閉じ
**Phase 3**: Phase 2 + アニメーションスタイル

#### Scenario: Phase 1 - ベース画像のみの composition.json 生成

- **GIVEN** フレーズリストとペルソナ設定がある:
  ```python
  [
    Phrase(text="やっほー！", persona_id="zundamon"),
  ]
  ```
  ```yaml
  personas:
    - id: "zundamon"
      character_image: "assets/characters/zundamon/base.png"
      character_position: "left"
  ```
- **WHEN** `update_composition_json()` が呼ばれる
- **THEN** composition.json に以下が含まれる:
  ```json
  {
    "phrases": [
      {
        "text": "やっほー！",
        "personaId": "zundamon",
        "characterImage": "characters/zundamon/base.png",
        "characterPosition": "left",
        ...
      }
    ]
  }
  ```

#### Scenario: Phase 2/3 - 全フィールドを含む composition.json 生成

- **GIVEN** フレーズリストとペルソナ設定がある:
  ```python
  [
    Phrase(text="やっほー！", persona_id="zundamon"),
  ]
  ```
  ```yaml
  personas:
    - id: "zundamon"
      character_image: "assets/characters/zundamon/base.png"
      mouth_open_image: "assets/characters/zundamon/mouth_open.png"
      eye_close_image: "assets/characters/zundamon/eye_close.png"
      character_position: "left"
      animation_style: "bounce"
  ```
- **WHEN** `update_composition_json()` が呼ばれる
- **THEN** composition.json に以下が含まれる:
  ```json
  {
    "phrases": [
      {
        "text": "やっほー！",
        "personaId": "zundamon",
        "characterImage": "characters/zundamon/base.png",
        "mouthOpenImage": "characters/zundamon/mouth_open.png",
        "eyeCloseImage": "characters/zundamon/eye_close.png",
        "characterPosition": "left",
        "animationStyle": "bounce",
        ...
      }
    ]
  }
  ```

#### Scenario: キャラクター画像未設定時の composition.json

- **GIVEN** ペルソナ設定で `character_image` が設定されていない
- **WHEN** `update_composition_json()` が呼ばれる
- **THEN** composition.json の `characterImage` は `null` である
- **AND** `mouthOpenImage` と `eyeCloseImage` も `null` である
- **AND** キャラクター表示はスキップされる

#### Scenario: 相対パス変換（public/ 基準）

- **GIVEN** ペルソナ設定で `character_image: "assets/characters/zundamon/base.png"` が設定されている
- **WHEN** composition.json が生成される
- **THEN** パスは `"characters/zundamon/base.png"` に変換される（`public/` 基準）

### Requirement: CharacterLayer コンポーネントでキャラクター表示（Phase 1）

Remotion の CharacterLayer コンポーネントは、キャラクター画像を指定された位置に表示しなければならない（SHALL）。

**Note**: Phase 1 では静的な画像表示のみ。Phase 2/3 でアニメーションを追加。

#### Scenario: 左側にキャラクター表示

- **GIVEN** composition.json に以下が含まれる:
  ```json
  {
    "characterImage": "characters/zundamon/base.png",
    "characterPosition": "left"
  }
  ```
- **WHEN** CharacterLayer が描画される
- **THEN** キャラクター画像が画面左側（x=10%）に表示される
- **AND** 画像サイズは高さ50%にスケールされる
- **AND** z-index はスライドより前、字幕より後ろである

#### Scenario: 右側にキャラクター表示

- **GIVEN** `characterPosition: "right"` が設定されている
- **WHEN** CharacterLayer が描画される
- **THEN** キャラクター画像が画面右側（x=90%）に表示される

#### Scenario: 中央にキャラクター表示

- **GIVEN** `characterPosition: "center"` が設定されている
- **WHEN** CharacterLayer が描画される
- **THEN** キャラクター画像が画面中央（x=50%）に表示される

#### Scenario: キャラクター画像なしの場合

- **GIVEN** `characterImage: null` が設定されている
- **WHEN** CharacterLayer が描画される
- **THEN** 何も表示されない
- **AND** エラーが発生しない

### Requirement: リップシンク（口パク）アニメーション（Phase 2）

CharacterLayer は、音声再生中に口開き画像を表示しなければならない（SHALL）。

#### Scenario: 音声再生中の口パク

- **GIVEN** フレーズの開始フレームが 0、終了フレームが 60 である
- **AND** `mouthOpenImage: "characters/zundamon/mouth_open.png"` が設定されている
- **WHEN** フレーム 0-60 が描画される
- **THEN** フレーム 0-60 では `mouth_open.png` が表示される
- **AND** フレーム 61 以降では `base.png`（口閉じ）が表示される

#### Scenario: 音声停止中は口閉じ

- **GIVEN** フレーズ1が終了し、フレーズ2が開始するまでの間がある
- **WHEN** 音声が再生されていないフレームが描画される
- **THEN** ベース画像（口閉じ）が表示される

#### Scenario: 口開き画像未設定時のフォールバック

- **GIVEN** `mouthOpenImage: null` が設定されている
- **WHEN** 音声再生中のフレームが描画される
- **THEN** 常にベース画像が表示される
- **AND** 口パクアニメーションはスキップされる

### Requirement: まばたきアニメーション（Phase 2）

CharacterLayer は、一定間隔で目閉じ画像を短時間表示しなければならない（SHALL）。

#### Scenario: 2-4秒間隔でのまばたき

- **GIVEN** `eyeCloseImage: "characters/zundamon/eye_close.png"` が設定されている
- **AND** FPS が 30 である
- **WHEN** フレームが描画される
- **THEN** 2-4秒間隔（60-120フレーム間隔）でまばたきが発生する
- **AND** 各まばたきは 0.2秒（6フレーム）継続する

#### Scenario: まばたき中の画像表示

- **GIVEN** まばたきが発生するフレームである
- **WHEN** そのフレームが描画される
- **THEN** `eye_close.png` がベース画像の上に重ねて表示される
- **AND** 口開き状態（リップシンク）は保持される

#### Scenario: 目閉じ画像未設定時のフォールバック

- **GIVEN** `eyeCloseImage: null` が設定されている
- **WHEN** フレームが描画される
- **THEN** まばたきアニメーションはスキップされる
- **AND** 常にベース画像の目が表示される

### Requirement: 揺れアニメーション（Sway）（Phase 3）

`animationStyle: "sway"` の場合、CharacterLayer は微妙な左右の揺れを適用しなければならない（SHALL）。

#### Scenario: 揺れアニメーションの適用

- **GIVEN** `animationStyle: "sway"` が設定されている
- **WHEN** フレームが描画される
- **THEN** キャラクター画像に ±2度の回転が適用される
- **AND** 回転は sin 波でスムーズに変化する（周期: 約4秒）

#### Scenario: 呼吸感のスケール変化

- **GIVEN** `animationStyle: "sway"` が設定されている
- **WHEN** フレームが描画される
- **THEN** キャラクター画像に ±2% のスケール変化が適用される
- **AND** スケールは sin 波でスムーズに変化する（周期: 約3秒）

### Requirement: バウンスアニメーション（Bounce）（Phase 3）

`animationStyle: "bounce"` の場合、CharacterLayer は話している間に上下バウンスを適用しなければならない（SHALL）。

#### Scenario: 話している間のバウンス

- **GIVEN** `animationStyle: "bounce"` が設定されている
- **AND** 音声が再生されている
- **WHEN** フレームが描画される
- **THEN** キャラクター画像の Y座標が ±5% の範囲で振動する
- **AND** バウンスは sin 波で表現される（周期: 約0.5秒）

#### Scenario: 話していない間は静止

- **GIVEN** `animationStyle: "bounce"` が設定されている
- **AND** 音声が再生されていない
- **WHEN** フレームが描画される
- **THEN** バウンスは停止する
- **AND** 基本の呼吸感（微妙なスケール変化）のみ適用される

### Requirement: 静止スタイル（Static）（Phase 3）

`animationStyle: "static"` の場合、CharacterLayer は揺れやバウンスを適用してはならない（SHALL NOT）。

#### Scenario: 静止スタイルでの表示

- **GIVEN** `animationStyle: "static"` が設定されている
- **WHEN** フレームが描画される
- **THEN** キャラクター画像は固定位置に表示される
- **AND** リップシンクとまばたきは動作する
- **AND** 揺れやバウンスは適用されない

### Requirement: 登場アニメーション（Phase 3）

CharacterLayer は、フレーズ開始時にフェードイン + スライドインアニメーションを適用しなければならない（SHALL）。

#### Scenario: 左からスライドイン

- **GIVEN** `characterPosition: "left"` が設定されている
- **AND** 新しいペルソナのフレーズが開始する
- **WHEN** フレーズ開始から 0.5秒（15フレーム）が描画される
- **THEN** キャラクター画像が画面外左側から左側位置へスライドする
- **AND** 同時に opacity が 0 から 1 へフェードインする

#### Scenario: 右からスライドイン

- **GIVEN** `characterPosition: "right"` が設定されている
- **WHEN** 登場アニメーションが実行される
- **THEN** キャラクター画像が画面外右側から右側位置へスライドする

#### Scenario: 中央へのフェードイン

- **GIVEN** `characterPosition: "center"` が設定されている
- **WHEN** 登場アニメーションが実行される
- **THEN** キャラクター画像がその場でフェードインする（スライドなし）

### Requirement: 退場アニメーション（Phase 3）

CharacterLayer は、話者が変わる時にフェードアウト + スライドアウトアニメーションを適用しなければならない（SHALL）。

#### Scenario: 左へスライドアウト

- **GIVEN** `characterPosition: "left"` のペルソナから別のペルソナへ切り替わる
- **WHEN** 切り替えの 0.5秒前（15フレーム前）から描画される
- **THEN** キャラクター画像が左側位置から画面外左側へスライドする
- **AND** 同時に opacity が 1 から 0 へフェードアウトする

#### Scenario: 右へスライドアウト

- **GIVEN** `characterPosition: "right"` のペルソナから切り替わる
- **WHEN** 退場アニメーションが実行される
- **THEN** キャラクター画像が右側位置から画面外右側へスライドする

#### Scenario: 同一話者継続時はアニメーションなし

- **GIVEN** フレーズ1とフレーズ2が同じペルソナである
- **WHEN** フレーズ2が開始される
- **THEN** 登場・退場アニメーションは発生しない
- **AND** キャラクター画像は継続して表示される

### Requirement: 3人以上の話者切り替え（Phase 3）

3人以上のペルソナがある場合、CharacterLayer は話者切り替え時に入れ替わりアニメーションを適用しなければならない（SHALL）。

#### Scenario: 3人目の登場で1人目と入れ替わる

- **GIVEN** ペルソナA、B、C があり、すべて `character_position` が未設定（デフォルト "left"）である
- **AND** フレーズ1はペルソナA、フレーズ2はペルソナB、フレーズ3はペルソナC である
- **WHEN** フレーズ3が開始される
- **THEN** ペルソナB が退場アニメーションで消える
- **AND** ペルソナC が登場アニメーションで現れる
- **AND** 同時に実行される（クロスフェード）

#### Scenario: 直前の話者に戻る場合

- **GIVEN** フレーズ1-2はペルソナA、フレーズ3はペルソナB、フレーズ4は再びペルソナA である
- **WHEN** フレーズ4が開始される
- **THEN** ペルソナB が退場する
- **AND** ペルソナA が再度登場する（キャッシュされていても登場アニメーションを実行）

### Requirement: 画像プリロード

CharacterLayer は、すべてのキャラクター画像をプリロードしなければならない（SHALL）。

#### Scenario: 画像のプリロード

- **GIVEN** composition.json に3つのペルソナのキャラクター画像がある
- **WHEN** Remotion コンポーネントがマウントされる
- **THEN** すべての `characterImage`、`mouthOpenImage`、`eyeCloseImage` がプリロードされる
- **AND** プリロード完了まで描画を待機する

#### Scenario: プリロード失敗時のエラーハンドリング

- **GIVEN** `characterImage` のパスが不正である
- **WHEN** プリロードが実行される
- **THEN** エラーがログに記録される
- **AND** そのキャラクター画像はスキップされる（動画レンダリングは継続）

### Requirement: 後方互換性の維持

CharacterLayer は、キャラクター画像情報がない composition.json でも動作しなければならない（SHALL）。

#### Scenario: キャラクター画像なしの composition.json

- **GIVEN** composition.json に `characterImage` フィールドがない
- **WHEN** CharacterLayer が描画される
- **THEN** キャラクター表示はスキップされる
- **AND** 字幕とスライドは正常に表示される
- **AND** エラーが発生しない

### Requirement: Include Background Information in composition.json

The generated composition.json SHALL include background configuration information.

#### Scenario: Output Global Background Configuration to composition.json

- **GIVEN** the configuration file has the following background settings:
  ```yaml
  video:
    background:
      type: "image"
      path: "assets/backgrounds/default.png"
      fit: "cover"
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** composition.json includes:
  ```json
  {
    "background": {
      "type": "image",
      "path": "backgrounds/default.png",
      "fit": "cover"
    }
  }
  ```

#### Scenario: Output Video Background to composition.json

- **GIVEN** background type is `"video"`
- **WHEN** `update_composition_json()` is called
- **THEN** `background.type` in composition.json is `"video"`
- **AND** Remotion displays the background using the `<Video>` component

#### Scenario: composition.json When Background is Not Set

- **GIVEN** the configuration file has no background settings
- **WHEN** `update_composition_json()` is called
- **THEN** `background` in composition.json is `null`
- **AND** the video is generated with a black background

### Requirement: Include Section Background Override in composition.json

composition.json SHALL include section-specific background override information.

#### Scenario: Output Section Background Override

- **GIVEN** the script YAML has the following sections:
  ```yaml
  sections:
    - title: "Intro"
      background:
        type: "image"
        path: "assets/backgrounds/intro.png"
      narrations:
        - text: "Hello"
    - title: "Main"
      narrations:
        - text: "This is the main content"
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** phrases in composition.json include:
  ```json
  {
    "phrases": [
      {
        "text": "Hello",
        "sectionIndex": 0,
        "backgroundOverride": {
          "type": "image",
          "path": "backgrounds/intro.png",
          "fit": "cover"
        }
      },
      {
        "text": "This is the main content",
        "sectionIndex": 1,
        "backgroundOverride": null
      }
    ]
  }
  ```

#### Scenario: Section Background Overrides Global Settings

- **GIVEN** global background is set to `"backgrounds/default.png"`
- **AND** section 1 background is set to `"backgrounds/intro.png"`
- **WHEN** the video is rendered
- **THEN** `"backgrounds/intro.png"` is displayed as the background during section 1 phrases
- **AND** `"backgrounds/default.png"` is displayed from section 2 onward

### Requirement: Include BGM Information in composition.json

The generated composition.json SHALL include BGM configuration information.

#### Scenario: Output BGM Configuration to composition.json

- **GIVEN** the configuration file has the following BGM settings:
  ```yaml
  video:
    bgm:
      path: "assets/bgm/music.mp3"
      volume: 0.3
      fade_in_seconds: 2.0
      fade_out_seconds: 3.0
      loop: true
  ```
- **WHEN** `update_composition_json()` is called
- **THEN** composition.json includes:
  ```json
  {
    "bgm": {
      "path": "bgm/music.mp3",
      "volume": 0.3,
      "fadeInSeconds": 2.0,
      "fadeOutSeconds": 3.0,
      "loop": true
    }
  }
  ```

#### Scenario: composition.json When BGM is Not Set

- **GIVEN** the configuration file has no BGM settings
- **WHEN** `update_composition_json()` is called
- **THEN** `bgm` in composition.json is `null`
- **AND** the video is generated without BGM

### Requirement: Display Background with BackgroundLayer Component

Remotion's BackgroundLayer component SHALL display background images or videos in fullscreen.

#### Scenario: Display Image Background

- **GIVEN** composition.json includes:
  ```json
  {
    "background": {
      "type": "image",
      "path": "backgrounds/default.png",
      "fit": "cover"
    }
  }
  ```
- **WHEN** BackgroundLayer is rendered
- **THEN** the background image is displayed using the `<Img>` component
- **AND** `objectFit: "cover"` is applied
- **AND** the image covers the entire screen

#### Scenario: Display Video Background

- **GIVEN** composition.json includes:
  ```json
  {
    "background": {
      "type": "video",
      "path": "backgrounds/loop.mp4",
      "fit": "cover"
    }
  }
  ```
- **WHEN** BackgroundLayer is rendered
- **THEN** the background video is displayed using the `<Video>` component
- **AND** `loop={true}` is set
- **AND** `muted={true}` is set (audio is muted)

#### Scenario: Loop Background Video

- **GIVEN** the background video is 10 seconds long and the total video is 60 seconds
- **WHEN** the video is rendered
- **THEN** the background video loops 6 times
- **AND** it is displayed seamlessly until the end

#### Scenario: Apply Fit Mode "contain"

- **GIVEN** `background.fit` is `"contain"`
- **WHEN** BackgroundLayer is rendered
- **THEN** the background image/video is displayed with `objectFit: "contain"`
- **AND** aspect ratio is maintained, and margins are filled with black

#### Scenario: Apply Fit Mode "fill"

- **GIVEN** `background.fit` is `"fill"`
- **WHEN** BackgroundLayer is rendered
- **THEN** the background image/video is displayed with `objectFit: "fill"`
- **AND** it is stretched to fill the entire screen, ignoring aspect ratio

#### Scenario: Behavior When Background is Not Set

- **GIVEN** `background` in composition.json is `null`
- **WHEN** BackgroundLayer is rendered
- **THEN** nothing is displayed (black background is default)
- **AND** no error occurs

#### Scenario: Layer Order (z-index)

- **GIVEN** background, slide, character, and subtitle exist
- **WHEN** the video is rendered
- **THEN** the layer order is as follows:
  1. BackgroundLayer (bottommost)
  2. SlideLayer
  3. CharacterLayer
  4. SubtitleLayer (topmost)

### Requirement: Switch Section Background

BackgroundLayer SHALL switch the background to the override setting when the section changes.

#### Scenario: Switch Background at Section Start

- **GIVEN** section 0's backgroundOverride is `null` (uses global background)
- **AND** section 1's backgroundOverride is `"backgrounds/intro.png"`
- **WHEN** the first phrase of section 1 is displayed
- **THEN** the background switches to `"backgrounds/intro.png"`
- **AND** the switch is immediate (no fade)

#### Scenario: Return to Global Background at Section End

- **GIVEN** section 1's backgroundOverride is set
- **AND** section 2's backgroundOverride is `null`
- **WHEN** the first phrase of section 2 is displayed
- **THEN** the background returns to global settings

### Requirement: Play BGM with BgmAudio Component

Remotion's BgmAudio component SHALL play BGM simultaneously with narration audio.

#### Scenario: Basic BGM Playback

- **GIVEN** composition.json includes:
  ```json
  {
    "bgm": {
      "path": "bgm/music.mp3",
      "volume": 0.3,
      "loop": true
    }
  }
  ```
- **WHEN** BgmAudio is rendered
- **THEN** BGM is played using the `<Audio>` component
- **AND** volume is set to `0.3`

#### Scenario: Loop BGM Playback

- **GIVEN** `bgm.loop` is `true`
- **AND** BGM is 30 seconds long and the total video is 120 seconds
- **WHEN** the video is rendered
- **THEN** BGM loops 4 times

#### Scenario: BGM Fade In

- **GIVEN** `bgm.fadeInSeconds` is `3.0`
- **AND** FPS is 30
- **WHEN** the first 90 frames of the video are played
- **THEN** BGM volume increases linearly from 0 to the set value (0.3)
- **AND** it remains constant at the set value from frame 90 onward

#### Scenario: BGM Fade Out

- **GIVEN** `bgm.fadeOutSeconds` is `5.0`
- **AND** the total video is 300 frames (10 seconds)
- **WHEN** the last 150 frames of the video are played
- **THEN** BGM volume decreases linearly from the set value to 0
- **AND** volume is 0 at frame 300

#### Scenario: Simultaneous Playback of BGM and Narration

- **GIVEN** BGM is configured
- **AND** narration audio exists
- **WHEN** the video is rendered
- **THEN** BGM and narration are played simultaneously
- **AND** volumes are set independently

#### Scenario: Behavior When BGM is Not Set

- **GIVEN** `bgm` in composition.json is `null`
- **WHEN** BgmAudio component is rendered
- **THEN** nothing is played
- **AND** no error occurs

### Requirement: Placement of Background/BGM Assets

The system SHALL place background and BGM assets in paths accessible to Remotion.

#### Scenario: Convert Background Image Path

- **GIVEN** the configuration specifies `video.background.path: "assets/backgrounds/bg.png"`
- **WHEN** composition.json is generated
- **THEN** the path is converted to `"backgrounds/bg.png"` (relative to `public/`)
- **AND** the file is copied or symlinked to `public/backgrounds/bg.png`

#### Scenario: Convert BGM File Path

- **GIVEN** the configuration specifies `video.bgm.path: "assets/bgm/music.mp3"`
- **WHEN** composition.json is generated
- **THEN** the path is converted to `"bgm/music.mp3"`
- **AND** the file is copied or symlinked to `public/bgm/music.mp3`

#### Scenario: When Asset File Does Not Exist

- **GIVEN** the specified asset file does not exist
- **WHEN** video generation is executed
- **THEN** a warning message is logged
- **AND** the missing asset is skipped (continues without background/BGM)

### Requirement: Background and BGM Backward Compatibility

The system SHALL work with composition.json files that lack background and BGM information.

The implementation SHALL centralize rendering execution parameters and environment checks to avoid duplicated logic.

#### Scenario: composition.json Without Background or BGM

- **GIVEN** composition.json does not include `background` and `bgm` fields
- **WHEN** Remotion components are rendered
- **THEN** the video is generated with a black background
- **AND** no BGM is played
- **AND** no error occurs

