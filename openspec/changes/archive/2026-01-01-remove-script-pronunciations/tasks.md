# Tasks: script.pronunciations フィールドの削除

## 実装タスク

すべてのタスクは完了済み。

### 1. データモデルの更新
- [x] `VideoScript.pronunciations` フィールドを削除
- [x] `PronunciationEntry` クラスを削除（他で使用されていないため）
- [x] 不要な import (`clean_katakana_reading`) を削除

### 2. LLMプロンプトの更新
- [x] `SCRIPT_GENERATION_PROMPT_JA` から pronunciations セクションを削除
- [x] `SCRIPT_GENERATION_PROMPT_EN` から pronunciations セクションを削除
- [x] `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` から pronunciations セクションを削除
- [x] `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` から pronunciations セクションを削除

### 3. パース処理の削除
- [x] `generate_script()` 関数から pronunciations パース処理を削除
- [x] `VideoScript()` コンストラクタ呼び出しから `pronunciations` 引数を削除

### 4. テスト・検証
- [x] 既存テストの実行（201件全てパス）
- [x] 後方互換性の確認（既存YAMLファイルの `pronunciations` フィールドは無視される）

## 並行作業として実施

### reading フィールド品質改善
- [x] アルファベット略語の音引きルール追加（ESP→イーエスピー）
- [x] 促音表記のルール追加（って→ッテ）
- [x] 具体例の拡充

## 検証結果

- コード削減: 69行削除、44行追加（正味25行削減）
- テスト: 201 passed, 2 skipped
- 破壊的変更: なし
