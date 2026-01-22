# Change: Reading Field品質の修正（促音・スペース・強調）

## Why

現在のLLMプロンプトには促音ルール（「って」→「ッテ」）が含まれているが、実際の生成結果で以下の問題が発生している：

1. **促音が正しく生成されない**: 「って」→「ツッテ」（×）、正しくは「ッテ」
2. **スペースがない**: 「ウェブスリーツッテムズカシイノニ」→読みにくい
3. **ルールの優先度が低い**: LLMが他の指示に従いすぎて、reading品質が犠牲になる

実例：
```yaml
text: Web3って難しいのに。操作できるの！？
reading: ウェブスリーツッテムズカシイノニ。ソウサデキルノ！？  # ❌

# 正しくは：
reading: ウェブスリー ッテ ムズカシイノニ。ソウサデキルノ！？  # ✅
```

## What Changes

### 1. 促音ルールの強調
- プロンプト内で **CRITICAL** マーカーを使用
- 促音の例を3倍に増やす（現在3例→9例以上）
- 誤った例も明示（「ツッテ」は×、「ッテ」が○）

### 2. スペースルールの追加
- **NEW**: カタカナ読み仮名に適切なスペースを入れる指示
- 単語の区切り、助詞の前後にスペース
- 例: 「ウェブスリー ッテ ムズカシイノニ」

### 3. Reading Field優先度の明示
- プロンプトの冒頭に **CRITICAL REQUIREMENT** セクションを追加
- reading品質がシステム失敗につながることを強調
- 生成後の自己チェック項目に追加

## Impact

### Affected specs
- `script-generation`: Reading Field品質要件を強化（MODIFIED）

### Affected code
- `src/movie_generator/script/generator.py`: 4つのプロンプト定数を更新
  - `SCRIPT_GENERATION_PROMPT_JA`
  - `SCRIPT_GENERATION_PROMPT_EN`
  - `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA`
  - `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN`

### Breaking Changes
なし（既存の reading フィールド検証はそのまま、生成品質のみ改善）

## Success Criteria

1. **促音正確度**: 「って」「った」を含む100個の生成で、95%以上が正しく「ッテ」「ッタ」に変換される
2. **スペース挿入**: 生成された reading の90%以上で適切なスペースが挿入される
3. **読みやすさ**: 人間評価者が「読みやすい」と評価する割合が80%以上
