# Design: スプライトベースのキャラクターアニメーション

## Context

現在の動画生成では、キャラクター（ナレーター）の視覚的な表現が字幕の色のみに限定されている。
視聴者エンゲージメントを高めるため、キャラクターの動きを追加したい。

**制約:**
- Live2D は実装複雑度・ライセンス・Remotion統合の課題から採用しない
- 既存の Remotion ベースのビデオレンダリングパイプラインを維持
- 画像素材の準備コストを最小限にする

**関係者:**
- 動画作成者（ユーザー）: 設定が簡単でなければならない
- 視聴者: 自然な動きを期待

## Goals / Non-Goals

### Goals
- 静止画ベースで口パク、まばたき、揺れアニメーションを実装
- 3人以上の話者切り替えに対応
- Live2D を使わずに実用的なキャラクター表現を実現
- 既存の静的アバター機能（`add-static-avatar-overlay`）との統合

### Non-Goals
- Live2D レベルの滑らかなアニメーション（将来的な拡張オプション）
- リアルタイム音声解析に基づく高精度リップシンク（Phase 1）
- 複雑な表情変化（怒り、笑顔など）

## Decisions

### 1. スプライト方式の採用

**Decision:**
- ベース画像（base.png）、口開き画像（mouth_open.png）、目閉じ画像（eye_close.png）の3枚構成
- CSS Transform と Remotion の spring() を使ってアニメーション

**Rationale:**
- 画像準備が簡単（既存の静止画から作成可能）
- Remotion との統合が容易（`<Img>` コンポーネント + CSS）
- パフォーマンスが良い（WebGL 不要）

**Alternatives Considered:**
1. **Lottie アニメーション**
   - メリット: 滑らかな動き
   - デメリット: Lottie ファイルの作成が必要、ずんだもん等の Lottie 素材が少ない
2. **GIF/APNG**
   - メリット: 既存素材が使える可能性
   - デメリット: 音声同期が困難、ファイルサイズが大きい
3. **AI 動画生成（Kling AI）**
   - メリット: 高品質
   - デメリット: API 課金、レンダリング時間、安定性の課題

### 2. リップシンク実装方式

**Decision (Phase 1):**
- 音声再生中は口開き画像を表示（固定）
- 音声停止中はベース画像（口閉じ）を表示

**Rationale:**
- 実装が単純でバグが少ない
- 視聴者にとって十分自然に見える

**Future Enhancement (Phase 2):**
- Remotion の `useAudioData()` フックで音量を取得
- 音量の閾値で口開閉を切り替える
- より自然なリップシンクを実現

```typescript
// Phase 2 example
import { useAudioData } from 'remotion';

const audioData = useAudioData(audioFile);
const volume = audioData?.getVolumeAtFrame(frame) ?? 0;
const isSpeaking = volume > 0.01;
```

### 3. まばたき実装方式

**Decision:**
- 擬似ランダムな間隔（2-4秒）でまばたき
- 各まばたきは 0.2秒（6フレーム@30fps）継続
- `eye_close.png` をベース画像の上に重ねて表示

**Rationale:**
- 完全にランダムだとフレームごとに結果が変わる（Remotion の deterministic rendering の原則に反する）
- フレーム数ベースの周期的なまばたきで、決定論的かつ自然に見える

```typescript
// Deterministic blinking logic
const blinkCycle = 90; // 3秒@30fps
const blinkDuration = 6; // 0.2秒@30fps
const isBlinking = (frame % blinkCycle) < blinkDuration;
```

### 4. アニメーションスタイルのバリエーション

**Decision:**
- `sway`: 微妙な揺れ（回転 ±2度、スケール ±2%）
- `bounce`: 話している間の上下バウンス（Y座標 ±5%）
- `static`: 揺れなし（リップシンク・まばたきのみ）

**Rationale:**
- ペルソナの性格に合わせて選択可能
- 実装コストが低い（CSS transform のみ）
- 視覚的な変化が大きすぎず、スライドを邪魔しない

### 5. 3人以上の話者切り替え

**Decision:**
- すべてのペルソナが同じ位置（例: left）の場合、退場→登場のクロスフェード
- 直前の話者が画面から消え、新しい話者が登場する

**Rationale:**
- 2人表示（left + right）も検討したが、スライドの視認性が下がる
- 1人表示 + 切り替え演出で、視聴者の注意をコントロールできる

**Alternative Considered:**
- 2人同時表示（left + right）
  - メリット: 誰が話しているか明確
  - デメリット: スライドが小さくなる、レイアウトが複雑

### 6. アセット管理

**Decision:**
- キャラクター画像は `assets/characters/[persona-id]/` に配置
- Remotion プロジェクトの `public/characters/` へシンボリックリンク
- composition.json には `public/` からの相対パス（`characters/zundamon/base.png`）を含める

**Rationale:**
- 既存の assets 管理（logos, slides）と一貫性
- シンボリックリンクでディスク容量を節約
- Remotion の静的ファイル配信ルールに従う

### 7. 画像レイヤー構成

**Decision:**
- レイヤー順序（奥→手前）:
  1. スライド背景（TransitionSeries）
  2. キャラクター画像（CharacterLayer）
  3. 字幕（Sequence + AudioSubtitleLayer）

**Rationale:**
- キャラクターがスライドの前に表示されることで、存在感が増す
- 字幕は最前面で読みやすさを確保

**CSS z-index:**
```typescript
const zIndexLayers = {
  slide: 0,
  character: 10,
  subtitle: 20,
};
```

### 8. PersonaConfig フィールド設計

**Decision:**
- 既存の `avatar_image` を `character_image` に改名推奨（後方互換性維持）
- 新規フィールド:
  - `mouth_open_image: str | None`
  - `eye_close_image: str | None`
  - `character_position: Literal["left", "right", "center"] = "left"`
  - `animation_style: Literal["bounce", "sway", "static"] = "sway"`

**Rationale:**
- `avatar_image` は既に定義されているが未使用（リネームで意図を明確化）
- デフォルト値を設定することで、最小限の設定で動作可能

## Architecture

### データフロー

```
config.yaml (PersonaConfig)
    ↓
Phrase model (persona_id)
    ↓
remotion_renderer._get_persona_fields()
    ↓
composition.json (characterImage, mouthOpenImage, etc.)
    ↓
VideoGenerator.tsx
    ↓
CharacterLayer.tsx (リップシンク、まばたき、アニメーション)
```

### CharacterLayer コンポーネント設計

```typescript
interface CharacterLayerProps {
  characterImage?: string;
  mouthOpenImage?: string;
  eyeCloseImage?: string;
  characterPosition: "left" | "right" | "center";
  animationStyle: "bounce" | "sway" | "static";
  isSpeaking: boolean; // 音声再生中か
  phraseStartFrame: number;
  phraseEndFrame: number;
}

const CharacterLayer: React.FC<CharacterLayerProps> = (props) => {
  const frame = useCurrentFrame();

  // 1. 表示画像の決定（リップシンク）
  const displayImage = props.isSpeaking && props.mouthOpenImage
    ? props.mouthOpenImage
    : props.characterImage;

  // 2. まばたき
  const blinkCycle = 90;
  const isBlinking = (frame % blinkCycle) < 6;
  const eyeOverlay = isBlinking ? props.eyeCloseImage : null;

  // 3. アニメーション（sway/bounce）
  const transform = getAnimationTransform(frame, props.animationStyle, props.isSpeaking);

  // 4. 登場・退場アニメーション
  const opacity = getEntryExitOpacity(frame, props.phraseStartFrame, props.phraseEndFrame);
  const position = getPosition(props.characterPosition);

  return (
    <AbsoluteFill style={{ zIndex: 10, opacity }}>
      <Img src={displayImage} style={{ ...position, transform }} />
      {eyeOverlay && <Img src={eyeOverlay} style={{ ...position, transform }} />}
    </AbsoluteFill>
  );
};
```

### リップシンク判定ロジック

```python
# remotion_renderer.py
def _is_phrase_speaking(phrase_index: int, phrases: list[Phrase]) -> bool:
    """フレーズが音声再生中かどうかを判定"""
    # composition.json の Sequence から開始/終了フレームを計算
    # CharacterLayer は phraseStartFrame, phraseEndFrame を受け取る
    return True  # Phase 1 では常に True（音声再生中と仮定）
```

### まばたきの決定論的実装

```typescript
// まばたきは擬似ランダムだが、フレーム数で決定論的
const getBlinkPattern = (frame: number, seed: number): boolean => {
  const blinkCycle = 60 + (seed % 60); // 2-4秒の範囲
  const blinkDuration = 6; // 0.2秒
  return (frame % blinkCycle) < blinkDuration;
};

// seed は personaId のハッシュから生成
const seed = hashCode(personaId);
```

## Risks / Trade-offs

### Risk 1: 画像素材の準備が必要

**Impact:** ユーザーが base.png, mouth_open.png, eye_close.png を用意する必要がある

**Mitigation:**
- サンプル画像セット（ずんだもん）を提供
- 画像生成ツール（口開き・目閉じの自動生成）を将来的に検討
- ドキュメントに推奨画像仕様を明記（PNG、透過背景、512x512推奨）

### Risk 2: 自然さが Live2D に劣る

**Impact:** 視聴者が違和感を感じる可能性

**Mitigation:**
- Phase 2 で音量ベースのリップシンクを追加
- Phase 3 で AI 動画生成との統合オプションを検討（高コスト）

### Risk 3: Remotion レンダリングパフォーマンス

**Impact:** 画像が多いとレンダリング時間が増加する可能性

**Mitigation:**
- 画像プリロード (`usePreload` フック)
- React.memo でコンポーネントのメモ化
- 画像サイズ最適化（WebP 形式推奨、512x512以下）

### Trade-off: シンプルさ vs 自然さ

**Decision:** シンプルさを優先
- Phase 1 は固定リップシンク（音声中=口開き）
- 自然さは段階的に改善

**Rationale:**
- 早期に動くものをリリースし、フィードバックを得る
- 必要に応じて Phase 2/3 で改善

## Migration Plan

### Phase 1: 基本実装（本提案）
1. PersonaConfig 拡張
2. composition.json へのキャラクター画像追加
3. CharacterLayer コンポーネント実装（基本表示 + リップシンク + まばたき）
4. サンプル画像の提供

### Phase 2: アニメーション強化
1. 音量ベースのリップシンク
2. 登場・退場アニメーション改善
3. 話者切り替え演出

### Phase 3: 将来的な拡張
1. AI 動画生成との統合（オプション機能）
2. 表情変化（笑顔、驚きなど）
3. ユーザーカスタムアニメーション（Lottie サポート）

### 後方互換性

- `character_image` 未設定の場合、キャラクター表示はスキップ
- 既存の静的アバター機能（`add-static-avatar-overlay`）との統合を検討
  - `avatar_image` → `character_image` へのマイグレーション

## Open Questions

1. **ずんだもん等の公式キャラクター画像の利用規約**
   - BOOTHで配布されている静止画を加工して使用可能か？
   - 利用規約を確認し、必要であればオリジナル画像の作成を検討

2. **画像生成ツールの必要性**
   - ユーザーが簡単に口開き・目閉じ画像を作成できるツールを提供するか？
   - Python スクリプト or Web ツール？

3. **パフォーマンステスト**
   - 3人話者、10分動画でのレンダリング時間は許容範囲か？
   - 必要に応じて画像サイズ・形式の最適化

4. **`add-static-avatar-overlay` との関係**
   - 統合するか、別機能として並存するか？
   - 提案: 本機能を静的アバターの拡張として実装し、`add-static-avatar-overlay` をベースにする
