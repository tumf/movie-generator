# 設計ドキュメント: 複数話者対応

## Context

現在の動画生成システムは単一話者を前提に設計されており、以下の制約がある：
- 音声合成パラメータ（speaker_id）がグローバルに1つのみ
- フレーズデータに話者情報が含まれていない
- LLMプロンプトが単一キャラクター想定
- 字幕スタイルが全フレーズで統一

複数話者対応により、これらを拡張する必要がある。

## Goals / Non-Goals

### Goals
- フレーズ単位で話者を切り替えられる仕組み
- 3名以上の話者にも対応可能な拡張性
- 音声合成エンジンに依存しない抽象化
- 設定ファイルのわかりやすさ重視
- アバター画像表示の将来実装に向けた設計

### Non-Goals
- アバター画像表示機能の実装（今回は設計のみ）
- 話者ごとの音量調整
- リアルタイムプレビュー機能
- 既存設定ファイルの自動移行ツール

## Decisions

### 1. ペルソナ（Persona）という概念の導入

話者を「ペルソナ」という概念で定義し、以下の情報を持たせる：
- `id`: 一意識別子（例: "zundamon", "metan"）
- `name`: 表示名（例: "ずんだもん"）
- `character`: キャラクター設定（LLMプロンプト用）
- `synthesizer`: 音声合成エンジン設定（抽象化）
- `subtitle_color`: 字幕色
- `avatar_image`: アバター画像パス（将来用、今回は未使用）

**理由**:
- 話者ごとに異なる音声合成エンジンを使える柔軟性
- 設定の見通しが良い
- 将来的にアバター画像などの拡張が容易

**代替案**:
- ~~話者を`audio.speakers`配列で定義~~ → 音声合成に限定されてしまう
- ~~話者をトップレベルで`speakers`として定義~~ → "persona"の方が概念として明確

### 2. 音声合成エンジンの抽象化

各ペルソナの`synthesizer`フィールドで、使用する音声合成エンジンとパラメータを指定：

```yaml
personas:
  - id: "zundamon"
    synthesizer:
      engine: "voicevox"
      speaker_id: 3
      speed_scale: 1.0
```

**理由**:
- VOICEVOX以外のエンジン（CoeFont, AIVIS, etc.）にも対応可能
- エンジン固有のパラメータを柔軟に設定
- ペルソナごとに異なるエンジンを使用可能

**実装**:
- `SynthesizerConfig`基底クラスを作成
- `VoicevoxSynthesizerConfig`, `CoefontSynthesizerConfig`などを派生
- ファクトリパターンで適切なSynthesizerインスタンスを生成

### 3. フレーズデータへの話者情報追加

`Phrase`データクラスに以下を追加：
- `persona_id: str`: ペルソナID
- `persona_name: str`: ペルソナ名（UI表示用）

**理由**:
- フレーズごとに話者が明確
- 音声合成時にペルソナ設定を参照可能
- Remotionで字幕スタイルを決定可能

### 4. LLMプロンプトの拡張

対話形式用の新プロンプトテンプレートを追加：
- `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA`
- `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN`

レスポンス形式を拡張：
```json
{
  "sections": [
    {
      "title": "セクション1",
      "dialogues": [
        {
          "persona_id": "zundamon",
          "narration": "やっほー！"
        },
        {
          "persona_id": "metan",
          "narration": "こんにちは！"
        }
      ],
      "slide_prompt": "..."
    }
  ]
}
```

**理由**:
- フレーズ単位で話者を指定できる
- 既存の`narration`フィールドと明確に区別
- 対話モードと単一話者モードを設定で切り替え

### 5. 設定形式の設計

トップレベルに`personas`配列を追加し、`narration.mode`で動作モードを指定：

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

narration:
  mode: "dialogue"  # "single" or "dialogue"
  style: "casual"
```

単一話者の場合:
```yaml
personas:
  - id: "zundamon"
    name: "ずんだもん"
    synthesizer:
      engine: "voicevox"
      speaker_id: 3
    subtitle_color: "#8FCF4F"

narration:
  mode: "single"
```

**理由**:
- 単一話者と複数話者を統一的に扱える
- わかりやすい設定構造
- 将来的な拡張が容易

**代替案検討**:
- ~~`audio.speakers`で定義~~ → 音声合成に限定されてしまう
- ~~後方互換性を維持~~ → 要件上不要、わかりやすさ優先

### 6. 字幕レンダリングの拡張

Remotion `composition.json`に話者情報を追加：
```json
{
  "phrases": [
    {
      "text": "やっほー！",
      "audioFile": "audio/phrase_0000.wav",
      "slideFile": "slides/ja/slide_0000.png",
      "duration": 0.8,
      "personaId": "zundamon",
      "personaName": "ずんだもん",
      "subtitleColor": "#8FCF4F"
    }
  ]
}
```

Remotion `VideoGenerator.tsx`で話者ごとに字幕スタイルを適用：
- `subtitleColor`を使用
- 将来的に話者名表示や位置変更にも対応可能

## Risks / Trade-offs

### Risk 1: 設定の複雑化
- **リスク**: ペルソナ設定が増えることで設定ファイルが長くなる
- **軽減策**: サンプル設定を充実させる、デフォルトペルソナを提供

### Risk 2: 音声合成エンジン抽象化の複雑性
- **リスク**: VOICEVOX以外のエンジン実装が複雑になる可能性
- **軽減策**: 最初はVOICEVOXのみ実装、インターフェースを明確に定義

### Risk 3: LLMの対話生成品質
- **リスク**: 自然な掛け合いを生成できない可能性
- **軽減策**: プロンプトエンジニアリングで改善、手動編集も可能にする

### Trade-off: 後方互換性 vs わかりやすさ
- **決定**: わかりやすさを優先し、後方互換性は切り捨て
- **理由**: 要件として明示的に指定されている
- **影響**: 既存ユーザーは設定ファイルの書き換えが必要

## Migration Plan

### Phase 1: データモデルとインフラ整備
1. `Persona`データモデル追加
2. `Phrase`に話者情報追加
3. `Config`にペルソナ設定追加
4. 音声合成抽象化レイヤー実装

### Phase 2: スクリプト生成とオーディオ合成
1. 対話形式LLMプロンプト実装
2. ペルソナごとの音声合成実装
3. CLIでのペルソナ指定対応

### Phase 3: ビデオレンダリング
1. composition.jsonに話者情報追加
2. Remotion字幕レイヤー拡張
3. 話者別字幕色適用

### Phase 4: テストと調整
1. 単一話者のテスト
2. 複数話者（2名）のテスト
3. 3名以上の話者のテスト
4. ドキュメント整備

### ロールバック計画
- 新機能はオプトイン（設定で`narration.mode: "dialogue"`を指定した場合のみ有効）
- 問題があれば`narration.mode: "single"`で従来動作に戻せる

## Open Questions

1. ~~音声合成エンジンの抽象化をどこまで進めるか？~~ → 最初はVOICEVOXのみ実装、インターフェースのみ定義
2. ~~LLMが生成する対話の最適な長さは？~~ → 実装後に調整
3. ~~ペルソナのデフォルト設定を提供するか？~~ → サンプル設定のみ提供
