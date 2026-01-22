# Change: pronunciations フィールドの完全削除

## Why

`reading` フィールドが各 `Narration` に追加されたことで、音声合成エンジンに直接カタカナ読みを渡せるようになりました。これにより、従来の `pronunciations`（発音辞書）は完全に冗長になりました。

- **現状**: LLM が各ナレーションの `reading` フィールドに正確なカタカナ読みを生成
- **問題**: `pronunciations` は `reading` と機能が重複しており、コードの複雑さを増している
- **解決**: `pronunciations` を完全に削除し、`reading` フィールドのみを使用

## What Changes

### **BREAKING** 変更

1. **データモデル変更**
   - `VideoScript.pronunciations` フィールドを削除
   - `PronunciationEntry` クラスを削除

2. **LLM プロンプト変更**
   - 4つのプロンプトテンプレートから `pronunciations` 生成指示を削除
   - 出力 JSON フォーマット例から `pronunciations` を削除

3. **CLI 処理変更**
   - スクリプト読み込み時の `pronunciations` パース処理を削除
   - 辞書への `pronunciations` 登録処理を削除
   - LLM で生成した読みを `pronunciations` に保存する処理を削除

4. **設定ファイル変更**
   - `config/examples/script-format-example.yaml` から `pronunciations` セクションを削除

### 削除される機能

- スクリプト生成時の `pronunciations` 辞書の自動生成
- `pronunciations` の script.yaml への保存・読み込み
- `pronunciations` から VOICEVOX 辞書への登録

### 維持される機能

- `reading` フィールドによる音声合成用カタカナ読み
- 形態素解析による辞書登録（`audio.enable_furigana` 設定）
- `config.pronunciation.custom` による手動辞書設定

## Impact

- 影響を受けるスペック:
  - `audio-furigana` - Pronunciation Persistence 要件を削除
  - `audio-synthesis` - Backward Compatibility 要件を更新
  - `data-models` - PronunciationEntry、VideoScript.pronunciations を削除
  - `script-generation` - pronunciations 生成関連を削除（暗黙的）

- 影響を受けるコード:
  - `src/movie_generator/script/generator.py`
  - `src/movie_generator/cli.py`
  - `src/movie_generator/multilang.py`
  - `config/examples/script-format-example.yaml`

- 後方互換性:
  - 既存の `pronunciations` を含む script.yaml は読み込み時にその項目が無視される（エラーにはならない）
