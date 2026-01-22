# Tasks: add-narration-reading-field

## タスク一覧

### Phase 1: データモデル更新

- [x] **1.1** `Narration` クラスに `reading: str` フィールドを追加
  - ファイル: `src/movie_generator/script/generator.py`
  - 必須フィールドとして追加
  - テスト: `test_script_generator.py` 更新

### Phase 2: LLMプロンプト更新

- [x] **2.1** 日本語単一話者プロンプト（`SCRIPT_GENERATION_PROMPT_JA`）更新
  - `reading` フィールドの生成指示を追加
  - カタカナ形式、助詞ルール（は→ワ、へ→エ、を→オ）を明記
  - 出力JSONフォーマットに `reading` を追加

- [x] **2.2** 英語単一話者プロンプト（`SCRIPT_GENERATION_PROMPT_EN`）更新
  - 同様に `reading` フィールドを追加

- [x] **2.3** 日本語対話プロンプト（`SCRIPT_GENERATION_PROMPT_DIALOGUE_JA`）更新
  - 同様に `reading` フィールドを追加

- [x] **2.4** 英語対話プロンプト（`SCRIPT_GENERATION_PROMPT_DIALOGUE_EN`）更新
  - 同様に `reading` フィールドを追加

### Phase 3: パーサー更新

- [x] **3.1** `generate_script()` 内のJSONパース処理を更新
  - `reading` フィールドを読み取り
  - `Narration` オブジェクト生成時に `reading` を設定
  - 後方互換性: `reading` がない場合は `text` をフォールバックとして使用

### Phase 4: CLI更新

- [x] **4.1** `Phrase` クラスに `reading: str | None` フィールドを追加
  - ファイル: `src/movie_generator/script/phrases.py`

- [x] **4.2** CLI の Phrase 生成処理を更新
  - `narration.reading` を `phrase.reading` にコピー
  - ファイル: `src/movie_generator/cli.py`
  - YAMLローダーも後方互換性対応

### Phase 5: 音声合成更新

- [x] **5.1** 音声合成時に `reading` を使用するよう変更
  - ファイル: `src/movie_generator/audio/voicevox.py`
  - `reading` がある場合はそれを VOICEVOX に渡す
  - 後方互換性: `reading` がない場合は `text` を使用

### Phase 6: テスト・検証

- [x] **6.1** ユニットテスト追加
  - `reading` フィールドのパーステスト
  - `Narration` バリデーションテスト

- [x] **6.2** 統合テスト更新
  - 既存テストを `reading` フィールド対応に更新
  - 115個のテストすべてパス

- [x] **6.3** E2Eテスト
  - 既存の統合テストで網羅

### Phase 7: ドキュメント

- [x] **7.1** README 更新
  - `reading` フィールドの説明追加
  - Narration Reading Field セクション追加

- [x] **7.2** サンプル YAML 更新
  - `config/examples/script-format-example.yaml` 作成
  - `reading` フィールドを含むサンプル追加

## 依存関係

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
```

## 並列化可能なタスク

- 2.1 〜 2.4 は並列実行可能
- 6.1 と 6.2 は並列実行可能
- 7.1 と 7.2 は並列実行可能
