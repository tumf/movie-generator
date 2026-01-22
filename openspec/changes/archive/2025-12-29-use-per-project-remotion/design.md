# Design: 動画ごとのRemotionプロジェクト生成アーキテクチャ

## Context

現在、`remotion/`ディレクトリがリポジトリルートに存在し、全動画で共有されている。これにより：

- リポジトリサイズが肥大化（`node_modules/`約300MB）
- 複数動画の同時生成に制約
- Remotionバージョンアップ時の影響範囲が広い

各動画プロジェクトに独立したRemotionプロジェクトを生成することで、これらの課題を解決する。

## Goals / Non-Goals

### Goals
- リポジトリからRemotion関連ファイルを完全に削除
- 各プロジェクトで独立したRemotionプロジェクトを持つ
- pnpmワークスペースで`node_modules`を効率的に共有
- テンプレートの更新・配布が容易

### Non-Goals
- Remotionの完全なカスタマイズ機能（初期バージョンではテンプレート固定）
- 既存プロジェクトの自動移行（手動移行ガイドを提供）
- Docker化（将来対応）

## Decisions

### 1. ディレクトリ構造

```
movie-generator/                  # リポジトリルート
├── pnpm-workspace.yaml           # ワークスペース定義
├── package.json                  # ルート（共有依存関係）
├── node_modules/                 # pnpmストア（共有）
└── projects/
    └── my-video/
        ├── audio/                # 音声ファイル
        ├── slides/               # スライド画像
        ├── metadata.json         # フレーズデータ
        ├── output.mp4            # 最終動画
        └── remotion/             # ★ プロジェクト専用Remotion
            ├── package.json      # name: "@projects/my-video"
            ├── node_modules/     # → ルートのpnpmストアへのシンボリックリンク
            ├── src/
            │   ├── Root.tsx      # テンプレートからコピー
            │   ├── VideoGenerator.tsx
            │   └── videoData.ts  # ★ 動的生成
            └── public/
                ├── audio -> ../../audio      # シンボリックリンク
                └── slides -> ../../slides    # シンボリックリンク
```

**理由**:
- pnpmワークスペースで`node_modules`を共有し、ディスク使用量を削減
- 各プロジェクトは独立した`src/`を持ち、カスタマイズ可能
- `public/`はシンボリックリンクで実ファイルを参照

### 2. pnpm-workspace.yaml

```yaml
packages:
  - 'projects/*/remotion'
```

**理由**:
- 全プロジェクトのRemotionディレクトリを自動検出
- 新規プロジェクト作成時、自動的にワークスペースメンバーになる
- テンプレートディレクトリは不要（毎回動的生成）

### 3. ルート package.json

```json
{
  "name": "movie-generator",
  "private": true,
  "scripts": {
    "setup": "pnpm install"
  },
  "devDependencies": {
    "@remotion/cli": "^4.0.395",
    "@types/react": "^19.2.7",
    "@types/react-dom": "^19.2.3",
    "react": "^19.2.3",
    "react-dom": "^19.2.3",
    "remotion": "^4.0.395",
    "typescript": "^5.9.3"
  }
}
```

**理由**:
- 全プロジェクトで共有する依存関係をルートで一元管理
- `pnpm install`で全プロジェクトに適用される

### 4. プロジェクト個別 package.json

```json
{
  "name": "@projects/my-video",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "render": "remotion render VideoGenerator ../output.mp4 --props=./input-props.json"
  }
}
```

**理由**:
- プロジェクト固有のスクリプト定義
- ワークスペースメンバーとして識別可能な`name`

### 5. composition.json によるデータ連携

Python側で以下のJSONを生成：

```json
{
  "title": "my-video",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "phrases": [
    {
      "text": "こんにちは",
      "audioFile": "/audio/phrase_0000.wav",
      "slideFile": "/slides/slide_0000.png",
      "duration": 2.5
    }
  ]
}
```

TypeScript側で読み込み：

```typescript
// src/Root.tsx
import compositionData from '../composition.json';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Video"
      component={VideoGenerator}
      defaultProps={{ phrases: compositionData.phrases }}
      // ...
    />
  );
};
```

**理由**:
- JSONは言語に依存しない標準フォーマット
- Pythonから生成しやすい
- Remotion側でそのまま読み込める（TypeScript型定義も自動推論）
- デバッグ時に`composition.json`を直接編集可能

### 6. Remotionプロジェクト初期化と動画生成フロー

**実装方法**: `pnpm create @remotion/video` + `composition.json`読み込み + コード生成

```python
def setup_and_render_video(project: Project, phrases: list[Phrase]):
    remotion_dir = project.project_dir / "remotion"

    # 1. Remotion公式CLIで初期化（初回のみ）
    if not remotion_dir.exists():
        subprocess.run([
            "pnpm", "create", "@remotion/video@latest",
            str(remotion_dir),
            "--template", "blank"
        ])
        setup_workspace(remotion_dir, project.name)

    # 2. composition.jsonを生成（台本からメタデータ）
    composition_data = {
        "title": project.name,
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "phrases": [
            {
                "text": p.text,
                "duration": p.duration,
                "audioFile": f"/audio/phrase_{i:04d}.wav",
                "slideFile": f"/slides/slide_{i:04d}.png"
            }
            for i, p in enumerate(phrases)
        ]
    }
    composition_path = remotion_dir / "composition.json"
    save_json(composition_path, composition_data)

    # 3. TypeScriptコンポーネントを生成（composition.json読み込み版）
    generate_video_component_that_reads_composition(remotion_dir)

    # 4. public/へのシンボリックリンク
    create_asset_symlinks(remotion_dir, project)

    # 5. レンダリング実行
    subprocess.run([
        "npx", "remotion", "render",
        "VideoComposition",
        str(project.output_dir / "video.mp4"),
        "--props", str(composition_path)
    ], cwd=remotion_dir)
```

**TypeScriptコンポーネント例**:

```typescript
// src/VideoComposition.tsx (Pythonから生成)
import { Composition } from 'remotion';
import { VideoGenerator } from './VideoGenerator';

// composition.jsonを読み込む
import compositionData from '../composition.json';

export const RemotionRoot: React.FC = () => {
  const durationInFrames = Math.ceil(
    compositionData.phrases.reduce((sum, p) => sum + p.duration, 0) * compositionData.fps
  );

  return (
    <Composition
      id="VideoComposition"
      component={VideoGenerator}
      durationInFrames={durationInFrames}
      fps={compositionData.fps}
      width={compositionData.width}
      height={compositionData.height}
      defaultProps={{ phrases: compositionData.phrases }}
    />
  );
};
```

**理由**:
- `composition.json`で台本データを一元管理（Python ⇔ Remotion間のインターフェース）
- TypeScriptコンポーネントはシンプル（composition.json読み込みのみ）
- 台本変更時は`composition.json`を再生成してレンダリングするだけ
- デバッグしやすい（composition.jsonを直接編集可能）

## Risks / Trade-offs

### Risk 1: pnpm未インストール環境
- **リスク**: ユーザーがpnpmを持っていない
- **緩和策**: セットアップスクリプトでpnpmインストールをガイド、またはnpmフォールバック

### Risk 2: ディスク使用量（複数プロジェクト）
- **リスク**: pnpm共有でも、プロジェクト数に応じてディスク使用量増加
- **緩和策**: 不要なプロジェクトは削除推奨、`.gitignore`に`projects/*/remotion/node_modules`追加

### Risk 3: Remotionバージョン管理
- **リスク**: 各プロジェクトで異なるRemotionバージョンが使用される可能性
- **緩和策**:
  - ルート`package.json`で推奨バージョンを明示
  - 必要に応じてバージョン固定（`pnpm create @remotion/video@4.0.395`）

### Trade-off: シンプルさ vs 柔軟性
- **選択**: 初期バージョンはローカルコピー方式でシンプルに
- **理由**: 早期リリース優先、npmパッケージ化は後から追加可能

## Migration Plan

### Phase 1: 動的生成実装（本PR）
1. TypeScriptコンポーネント生成ロジックをPythonに実装
2. `pnpm create @remotion/video`統合
3. Python統合実装

### Phase 2: 既存プロジェクト移行（手動）
1. ユーザーガイド提供
2. `movie-generator migrate-remotion <project-name>`コマンド提供（オプション）

### Phase 3: リポジトリクリーンアップ（本PR）
1. 既存`remotion/`削除
2. `.gitignore`更新

### Rollback Plan
- テンプレート方式が失敗した場合、`remotion/`をGitから復元
- 既存プロジェクトは影響なし（独立）

## Open Questions

1. **TypeScriptコードの保守性**
   - Pythonから文字列生成 vs 外部ファイル管理？
   - コンポーネントのテストはどうする？

2. **複数プロジェクトの一括レンダリング**
   - `pnpm -r run render`で並列実行？
   - Pythonから制御？

3. **CI/CD統合**
   - GitHub Actionsでpnpmキャッシュ活用？
   - Dockerイメージに含める？

→ これらは初期実装後に検討
