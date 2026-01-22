# Change: 動画ごとにRemotionプロジェクトを生成する方式に変更

## Why

現在の実装では以下の課題がある：

1. **リポジトリ肥大化**: `remotion/`ディレクトリとその`node_modules/`がリポジトリに含まれている
2. **バージョン固定**: 全動画が同じRemotionバージョンに依存
3. **テンプレート管理**: VideoGenerator.tsxの本家追従が困難
4. **並列処理制限**: 共有Remotionプロジェクトでは複数動画の同時生成に制約

動画ごとに独立したRemotionプロジェクトを生成することで、以下を実現する：

- リポジトリからRemotion関連ファイルを削除し、Pythonコードのみに集中
- 各プロジェクトで最新のRemotionバージョンを使用可能
- pnpmのワークスペース機能で`node_modules`を効率的に共有
- 動画ごとのカスタマイズが容易

## What Changes

### 削除
- `remotion/` ディレクトリ全体をリポジトリから削除
- `remotion_renderer.py` の既存実装を削除

### 新規追加
- Python側のプロジェクトセットアップ機能
  - `Project.setup_remotion_project()` - Remotionプロジェクトの動的生成・インストール
  - `pnpm create @remotion/video`によるプロジェクト初期化
  - pnpmワークスペース管理
  - TypeScriptコンポーネント（VideoGenerator.tsx等）の動的生成
  - `videoData.ts`の自動生成

### 変更
- `src/movie_generator/video/remotion_renderer.py` - 全面改修
  - `pnpm create @remotion/video`による初期化
  - TypeScriptコンポーネントの動的生成
  - pnpm経由での依存関係インストール
  - プロジェクト内での`npx remotion render`実行
- `src/movie_generator/project.py` - メソッド追加
- `openspec/project.md` - 依存関係とディレクトリ構造を更新
- ルート`pnpm-workspace.yaml` - ワークスペース設定

## Impact

- **Affected specs**: `video-generation`
- **Affected code**:
  - `src/movie_generator/video/remotion_renderer.py` - 全面改修
  - `src/movie_generator/project.py` - `setup_remotion_project()`追加
  - `src/movie_generator/cli.py` - レンダリングフロー調整
  - `remotion/` → 削除
- **Dependencies**:
  - **新規**: pnpm（推奨）またはnpm
  - **新規**: Node.js 18+
  - **継続**: Remotion CLI（各プロジェクトで自動インストール）
  - **削除**: リポジトリ内のffmpeg依存（Remotionに完全移行）

## Breaking Changes

- 既存の`remotion/`ディレクトリに依存するワークフローは動作しなくなる
- 既存プロジェクトは新しいRemotionプロジェクト構造に移行が必要

## Migration Plan

1. Python側に`setup_remotion_project()`を実装
2. 既存プロジェクトに対して`setup_remotion_project()`を実行（各プロジェクトで新規インストール）
3. 動作確認後、リポジトリから`remotion/`を削除
