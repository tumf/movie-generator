# Change: スライド生成の「タスク準備」と「実行」を分離

## Why
スライド生成が単一関数にまとまっていると、並列度制御・スキップ判定・リトライ・進捗表示が絡み合い、読みづらさとバグ混入につながります。タスク準備と実行を分離し、各責務をテストしやすくします。

## What Changes
- セクション→生成タスクの計画（対象/出力パス/スキップ）と、実際の生成実行を分離する
- 並列度/レート制御の境界を明確にする（振る舞いは維持）

## Impact
- Affected specs: `openspec/specs/cli-interface/spec.md`
- Affected code: `src/movie_generator/slides/generator.py`
