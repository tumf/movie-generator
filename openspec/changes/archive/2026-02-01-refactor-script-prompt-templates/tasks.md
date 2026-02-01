## 1. Implementation
- [x] 1.1 プロンプト組み立ての責務を分割する（検証: `src/movie_generator/script/generator.py` でテンプレート選択/組み立て/検証が分離されていることを確認）
- [x] 1.2 4 バリエーションを同時に更新するための共通部品を導入する（検証: 4 つのプロンプトが同じ共通関数/テンプレート部品を参照することを確認）

## 2. Tests
- [x] 2.1 4 バリエーションが必須フィールド（例: `sections`, `narration`/`narrations`, `slide_prompt`）の説明と例を含むことを確認するテストを追加する（検証: `uv run pytest -k prompt -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] Git working tree is dirty: Modified `openspec/changes/refactor-script-prompt-templates/tasks.md`
