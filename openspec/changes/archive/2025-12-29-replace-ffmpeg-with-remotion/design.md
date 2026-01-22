# Design: ffmpeg→Remotion完全移行

## Context

`movie-generator generate`コマンドで動画を生成する際、現在はffmpegを使用しているが、
字幕・スライド切り替え・アニメーションが実装されていない。

既存の`remotion/`ディレクトリには高品質な`VideoGenerator.tsx`コンポーネントがあり、
これを活用することで本番品質の動画生成が可能になる。

### 既存資産

1. **VideoGenerator.tsx**: フレーズベースの字幕・音声・スライド同期
2. **package.json**: Remotion依存関係定義済み
3. **remotion.config.ts**: 基本設定済み

## Goals / Non-Goals

### Goals
- `movie-generator generate`実行時にRemotionで動画レンダリング
- ユーザーは追加操作不要（完全自動化）
- 字幕・スライド切り替え・音声同期が正しく動作

### Non-Goals
- Remotionテンプレートのカスタマイズ機能（将来対応）
- GUI/プレビュー機能
- ffmpegフォールバック機能

## Decisions

### 1. アーキテクチャ

```
Python側                           Remotion側
─────────                          ──────────
generate command
    ↓
1. コンテンツ取得
2. スクリプト生成
3. フレーズ分割
4. 音声生成 → output/audio/
5. スライド生成 → output/slides/
    ↓
6. composition.json生成
    ↓
7. remotion/public/にファイルコピー
    ↓
8. Root.tsx動的生成
    ↓
9. npm install（初回のみ）
    ↓
10. npx remotion render → output/final.mp4
```

### 2. データフォーマット

**composition.json**（Pythonが生成）:
```json
{
  "title": "動画タイトル",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "phrases": [
    {
      "text": "字幕テキスト",
      "audioFile": "audio/phrase_0000.wav",
      "slideFile": "slides/slide_0000.png",
      "duration": 3.5
    }
  ]
}
```

### 3. Root.tsx動的生成

```typescript
import React from 'react';
import { Composition } from 'remotion';
import { VideoGenerator, calculateTotalFrames } from './VideoGenerator';

const compositionData = ${JSON.stringify(data)};

export const RemotionRoot: React.FC = () => {
  const totalFrames = calculateTotalFrames(compositionData.phrases);
  return (
    <Composition
      id="VideoGenerator"
      component={VideoGenerator}
      durationInFrames={totalFrames}
      fps={compositionData.fps}
      width={compositionData.width}
      height={compositionData.height}
      defaultProps={{ phrases: compositionData.phrases }}
    />
  );
};
```

### 4. ファイル配置

```
remotion/
├── public/                    # 動的構築（Python側が管理）
│   ├── audio/
│   │   └── phrase_XXXX.wav
│   ├── slides/
│   │   └── slide_XXXX.png
│   └── composition.json
├── src/
│   ├── VideoGenerator.tsx    # 既存（変更なし）
│   ├── Root.tsx              # 動的生成
│   └── index.ts              # 既存（変更なし）
└── package.json              # 既存（変更なし）
```

### 5. npm依存管理

```python
def ensure_npm_dependencies(remotion_root: Path) -> None:
    node_modules = remotion_root / "node_modules"
    if not node_modules.exists():
        console.print("Installing Remotion dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=remotion_root,
            check=True,
        )
```

### 6. レンダリング実行

```python
def run_remotion_render(remotion_root: Path, output_path: Path) -> None:
    subprocess.run(
        [
            "npx", "remotion", "render",
            "VideoGenerator",
            str(output_path),
            "--overwrite",
        ],
        cwd=remotion_root,
        check=True,
    )
```

## Risks / Trade-offs

| リスク | 軽減策 |
|--------|--------|
| Node.js未インストール | 明確なエラーメッセージ + インストールガイド |
| npm install失敗 | エラーログ表示 + 手動実行コマンド提示 |
| レンダリング時間が長い | プログレス表示、並列オプション案内 |
| メモリ不足 | `--concurrency=1`オプション案内 |

## Migration Plan

1. **Phase 1**: renderer.py改修（ffmpeg削除、Remotion連携実装）
2. **Phase 2**: CLI統合（render_video_remotion呼び出し）
3. **Phase 3**: テスト・ドキュメント整備

## Open Questions

- [x] ffmpegフォールバック → 不要（完全削除）
- [ ] Remotionライセンス確認（商用利用の場合）
