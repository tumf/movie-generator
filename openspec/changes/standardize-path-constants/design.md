## Context
生成アセットのパス規約や最小解像度がコード内に散在し、Docker環境のプロジェクトルートも固定値になっている。

## Goals / Non-Goals
- Goals:
  - 生成ファイル名フォーマットを `ProjectPaths` に定義する
  - 最小解像度の基準値を `VideoConstants` に定義する
  - Docker実行時のプロジェクトルートを環境変数で上書き可能にする
- Non-Goals:
  - ファイル命名規則の変更（既存フォーマットは維持）

## Decisions
- `constants.py` に `ProjectPaths` と `VideoConstants` の追加/拡張を行う
- `/app` をデフォルトとしつつ `PROJECT_ROOT` で上書きできるようにする

## Risks / Trade-offs
- 環境変数の誤設定でパス解決が失敗する可能性がある

## Migration Plan
- 既存のデフォルト値と同じ値を定数化して挙動を維持する

## Open Questions
- なし
