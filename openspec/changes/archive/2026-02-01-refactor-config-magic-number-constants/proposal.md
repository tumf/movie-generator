# Change: 設定デフォルト値/制約の数値を定数化して参照を統一

## Why
設定モデルのデフォルト値や範囲制約が散発的な数値リテラルになると、意味が読み取りづらく、変更時の一括更新漏れが起きます。命名された定数に集約して可読性と変更容易性を上げます。

## What Changes
- 代表的なデフォルト値/制約（例: 音量上限、CRF 範囲など）を定数として定義する
- モデル定義/バリデーション/ドキュメント生成で同一定数を参照する

## Impact
- Affected specs: `openspec/specs/config-management/spec.md`
- Affected code: `src/movie_generator/config.py`
