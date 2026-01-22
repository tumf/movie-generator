## ADDED Requirements

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
