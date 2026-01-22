# Change: スプライトベースのキャラクターアニメーション追加

**統合**: この変更は `add-static-avatar-overlay` を吸収し、静的アバターから段階的にアニメーション機能を追加します。

## Why

現在のスライド動画では、キャラクター（ナレーター）の存在が字幕の色でしか表現されていない。
視聴者エンゲージメントを高めるため、Live2D を使わずに以下を段階的に実現したい:

- **口パク（リップシンク）** - 音声再生時に口の開閉
- **まばたき** - 一定間隔での目の開閉
- **自然な揺れ** - 髪や体の微妙な動き（呼吸感）
- **登場・退場** - フェードイン/スライドインアニメーション
- **話者切り替え** - 3人以上の場合の入れ替わり演出

**Live2D を採用しない理由:**
- Remotion との統合が複雑（WebGL + フレームレンダリングの同期課題）
- SDK ライセンスの制約
- 実装・デバッグコストが高い

**代替アプローチ:**
スプライト画像（口開き/閉じ、目開き/閉じ）+ CSS/Remotion アニメーションで実現する。

## What Changes

### 設定（config-management）
- `PersonaConfig` に以下フィールドを追加:
  - `mouth_open_image`: 口開き画像パス（リップシンク用）
  - `eye_close_image`: 目閉じ画像パス（まばたき用）
  - `character_position`: 表示位置 ("left" | "right" | "center")
  - `animation_style`: アニメーションスタイル ("bounce" | "sway" | "static")

### データモデル（data-models）
- `CompositionPhrase` に以下フィールドを追加:
  - `characterImage`: ベース画像（既存 `avatarImage` から改名推奨）
  - `mouthOpenImage`: 口開き画像
  - `eyeCloseImage`: 目閉じ画像
  - `characterPosition`: 表示位置
  - `animationStyle`: アニメーションスタイル

### Remotion テンプレート（video-rendering）
- `CharacterLayer` コンポーネントを追加:
  - **リップシンク**: 音声再生中は `mouthOpenImage` を表示
  - **まばたき**: 2-4秒間隔で `eyeCloseImage` を0.2秒間表示
  - **揺れアニメーション**: CSS transform で微妙な回転・スケール変化
  - **登場・退場**: フェードイン/アウト + スライドイン/アウト
  - **位置制御**: left/right/center に配置

### アセット管理
- `assets/characters/[persona-id]/` ディレクトリ構造:
  ```
  assets/characters/zundamon/
  ├── base.png          # 通常状態（口閉じ、目開き）
  ├── mouth_open.png    # 口開き
  └── eye_close.png     # まばたき用
  ```

## Impact

- **Affected specs**: `config-management`, `video-rendering`
- **Affected code**:
  - `src/movie_generator/config.py` - PersonaConfig 拡張
  - `src/movie_generator/video/renderer.py` - CompositionPhrase モデル拡張
  - `src/movie_generator/video/remotion_renderer.py` - キャラクター画像の composition.json への追加
  - `src/movie_generator/video/templates.py` - CharacterLayer コンポーネント追加
  - `src/movie_generator/project.py` - キャラクター画像のアセット管理

## 技術的な実装アプローチ

### リップシンクの実現方法

**方式1: 音声再生中は口開き固定（シンプル）**
```typescript
const isSpeaking = frame >= startFrame && frame < endFrame;
const mouthImage = isSpeaking ? mouthOpenImage : baseImage;
```

**方式2: 音量ベースの開閉（より自然）**
```typescript
// 音声データから音量を取得し、閾値で口開閉を切り替え
const volume = useAudioData(audioFile).getVolumeAtFrame(frame);
const mouthImage = volume > threshold ? mouthOpenImage : baseImage;
```

→ **Phase 1 は方式1、Phase 2 で方式2を検討**

### まばたきの実装

```typescript
// 2-4秒間隔でランダムにまばたき
const blinkInterval = 2 + Math.random() * 2; // 2-4秒
const isBlinking = (frame % (blinkInterval * fps)) < (0.2 * fps); // 0.2秒間
```

### 揺れアニメーション

```typescript
// 微妙な回転・スケール変化
const sway = Math.sin(frame * 0.05) * 2; // ±2度の回転
const breathe = 1 + Math.sin(frame * 0.03) * 0.02; // ±2% のスケール
```

## 段階的な実装計画

### Phase 1: 静的アバター表示（`add-static-avatar-overlay` 統合）
- ベース画像（`character_image`）の表示
- 位置制御（left/right/center）
- 話者切り替え時の画像切り替え
- **成果物**: 静的だが視覚的な存在感のあるキャラクター表示

### Phase 2: リップシンクとまばたき
- 口開き画像（`mouth_open_image`）の追加
- 音声再生中の口開閉（方式1: 固定）
- 目閉じ画像（`eye_close_image`）の追加
- 一定間隔のまばたき
- **成果物**: 基本的なキャラクターアニメーション

### Phase 3: アニメーション強化
- 揺れアニメーション（sway/bounce）
- 登場・退場演出（フェードイン/アウト）
- 話者切り替え演出（クロスフェード）
- **成果物**: 自然な動きのあるキャラクター表示

## 代替案との比較

| 手法 | 実装コスト | 自然さ | 制約 |
|------|----------|--------|------|
| **スプライト + CSS（本提案）** | 低 | 中 | 画像準備が必要 |
| Live2D | 高 | 高 | ライセンス、Remotion統合複雑 |
| Lottie | 中 | 高 | Lottieファイル作成が必要 |
| AI動画生成（Kling） | 低 | 最高 | API課金、レンダリング遅い |

## 依存関係

- **統合**: `add-static-avatar-overlay` をこの変更に統合（Phase 1として実装）
- **ブロッキング**: なし
- **関連**: 将来的に AI動画生成との統合オプション検討可能

## add-static-avatar-overlay との統合について

本変更は `add-static-avatar-overlay` を吸収し、以下のように拡張します：

| 項目 | 静的アバター（旧） | 統合版（新） |
|------|------------------|-------------|
| **フィールド名** | `avatar_image` | `character_image`（`avatar_image` は alias） |
| **画像枚数** | 1枚 | 1-3枚（base, mouth_open, eye_close） |
| **表示位置** | 右下固定（円形） | 左/右/中央（設定可能） |
| **サイズ** | 200x200px | 大きめ（高さ50%）、設定可能 |
| **アニメーション** | なし → Phase 1 | 口パク・まばたき → Phase 2/3 |

**移行パス:**
- Phase 1 完了時点で、`add-static-avatar-overlay` 相当の機能が実現
- Phase 2/3 はオプション機能として段階的に追加

## リスクと対策

### リスク1: 画像素材の準備が必要
- **対策**: サンプル画像を提供、または既存の静止画から自動生成ツール検討

### リスク2: 自然さがLive2Dに劣る
- **対策**: 段階的に改善、必要に応じてLottieやAI動画生成を後続フェーズで検討

### リスク3: Remotion レンダリングパフォーマンス
- **対策**: 画像プリロード、メモ化を適切に使用
