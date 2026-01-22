# Change: script.yaml に役割割り当て機能を追加

## Why

現在の複数話者モードでは、各キャラクターの役割（解説役、質問役など）が固定化されておらず、
視聴者にとってわかりにくい動画になってしまう問題がある。

LLMにシナリオ内での役割を自由に生成させ、script.yaml単位で役割を固定することで、
一貫性のある、わかりやすい対話形式の動画を生成できるようにする。

## What Changes

- `RoleAssignment` データクラスを追加（persona_id, role, description）
- `VideoScript` クラスに `role_assignments` フィールドを追加
- LLMプロンプト（日本語/英語）に役割割り当て指示を追加
- LLM応答のパース処理で `role_assignments` を抽出
- script.yaml出力に `role_assignments` セクションを含める

## Impact

- Affected specs: `script-generation`
- Affected code:
  - `src/movie_generator/script/generator.py` - データモデルとプロンプト
  - `src/movie_generator/cli.py` - YAML出力処理（既存形式を維持、新フィールド追加のみ）
- Backward compatibility:
  - `role_assignments` はオプショナル
  - 既存のscript.yaml（role_assignments無し）は引き続き読み込み可能
  - 単一話者モードには影響なし
