# Change: Remotion プロジェクトセットアップの段階分割と可読性向上

## Why
Remotion プロジェクト初期化は外部コマンド実行・ファイル生成・workspace 更新など複数責務を含みます。単一関数に集約されると失敗時の切り分けが難しくなるため、段階分割とエラーメッセージの明確化を提案します。

## What Changes
- `Project.setup_remotion_project()` を段階別関数に分割し、各段階で失敗理由を明確化する
- 既存の生成物パス/シンボリックリンク作成などの仕様は維持する

## Impact
- Affected specs: `openspec/specs/video-generation/spec.md`
- Affected code: `src/movie_generator/project.py`
