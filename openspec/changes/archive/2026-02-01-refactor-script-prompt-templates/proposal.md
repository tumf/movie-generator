# Change: スクリプト生成プロンプトのテンプレート管理を整理

## Why
スクリプト生成プロンプト（言語/モード別）が巨大文字列として散在すると、更新漏れや差分確認のコストが増えます。全バリエーションの同時更新を確実にし、レビューしやすい形に整えるため、テンプレート管理のリファクタリングを提案します。

## What Changes
- プロンプト生成を「テンプレート選択」「変数差し込み」「出力フォーマット例の共有」などに分割する
- 4 バリエーション（single/dialogue × ja/en）の更新漏れを検出できる仕組み（テスト/静的チェック）を追加する

## Impact
- Affected specs: `openspec/specs/script-generation/spec.md`
- Affected code: `src/movie_generator/script/generator.py`
