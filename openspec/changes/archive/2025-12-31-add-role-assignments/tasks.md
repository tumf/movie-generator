# Tasks: script.yaml に役割割り当て機能を追加

## 1. データモデル拡張

- [x] 1.1 `RoleAssignment` dataclass を `src/movie_generator/script/generator.py` に追加
- [x] 1.2 `VideoScript` dataclass に `role_assignments: list[RoleAssignment] | None` フィールドを追加

## 2. プロンプト改善

- [x] 2.1 `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` に役割割り当てセクションを追加
- [x] 2.2 `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` に役割割り当てセクションを追加
- [x] 2.3 JSON出力形式の例に `role_assignments` を追加

## 3. パース処理拡張

- [x] 3.1 `generate_script()` 関数で `role_assignments` をパースする処理を追加
- [x] 3.2 `role_assignments` が無い場合も許容（後方互換性）

## 4. テスト

- [x] 4.1 `RoleAssignment` の単体テストを追加
- [x] 4.2 `VideoScript` with `role_assignments` のテストを追加
- [x] 4.3 `VideoScript` without `role_assignments` のテスト（後方互換性）
- [x] 4.4 全テスト実行と検証
