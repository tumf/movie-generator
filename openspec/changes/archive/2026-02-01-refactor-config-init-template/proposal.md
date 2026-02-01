# Change: config init のデフォルト YAML 生成をテンプレート化

## Why
デフォルト YAML をコード内で手組みすると、コメントやフォーマットの維持が難しくなります。テンプレート化（リソース化/ゴールデンファイル化）により、差分が明確でレビューしやすくなります。

## What Changes
- `config init` のデフォルト YAML 出力をテンプレート（固定テキスト）として管理する
- テンプレートの妥当性（`load_config()` で読める）をテストで担保する

## Impact
- Affected specs: `openspec/specs/config-management/spec.md`
- Affected code: `src/movie_generator/config.py`
