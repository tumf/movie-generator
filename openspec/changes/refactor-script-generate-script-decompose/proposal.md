# Change: generate_script() の責務分割（プロンプト構築/呼び出し/パース）

## Why
`generate_script()` が長大で分岐も多いと、プロンプト関連の修正やレスポンスパースの修正が絡み合い、回帰が起きやすくなります。段階分割により、テストを増やしやすくすることを目的とします。

## What Changes
- `generate_script()` を「入力整形」「プロンプト選択/構築」「LLM 呼び出し」「レスポンス検証/パース」「フレーズ分割」などへ分割する
- 外部 I/O（LLM 呼び出し）と純粋処理（パース/検証）を分離する

## Impact
- Affected specs: `openspec/specs/script-generation/spec.md`
- Affected code: `src/movie_generator/script/generator.py`
