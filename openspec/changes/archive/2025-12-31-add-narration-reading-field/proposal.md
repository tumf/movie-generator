# Proposal: add-narration-reading-field

## Why

### Problem

現在、VOICEVOXは漢字の読みを誤ることがある：
- 「道案内図」→「どうあんないず」（正：みちあんないず）
- 「97」→「ナナジュウナナ」（正：キュウジュウナナ）
- 助詞「は」→「は」（正：わ）

形態素解析ベースのアプローチでは以下の限界がある：
- 複合語が分割される（「道案内図」→「道」「案内」「図」）
- 文脈依存の読みが判断できない
- 助詞の発音変換が困難

### Solution

LLMがスクリプト生成時に、発音通りのカタカナ読み（`reading`）も同時に生成する。

### Benefits

- 形態素解析不要
- 複合語も正しく読める
- 助詞「は→ワ」「へ→エ」「を→オ」も正確に処理
- LLMの文脈理解力を活用

## What Changes

### Affected Specs

1. **script-generation**: LLMプロンプトに `reading` フィールド生成指示を追加
2. **data-models**: `Narration` クラスに `reading: str` フィールド追加
3. **audio-synthesis**: 音声合成時に `reading` を使用

### Schema Changes

**Before:**
```yaml
narrations:
  - text: "明日は晴れです"
```

**After:**
```yaml
narrations:
  - text: "明日は晴れです"
    reading: "アシタワハレデス"
```

### Design Principles

1. **`reading` は必須フィールド**: 後方互換性より正確な音声合成を優先
2. **カタカナ形式**: VOICEVOXとの親和性が高い
3. **助詞の発音変換をLLMに委譲**: 「は→ワ」等のルールをプロンプトに明記
4. **既存の `pronunciations` は維持**: 追加の微調整用として残す

### Risks and Mitigations

| リスク | 対策 |
|--------|------|
| LLMが誤った読みを生成 | プロンプトに明確なルールと例を記載 |
| 後方互換性の破壊 | スクリプト再生成の手順をドキュメント化、フォールバック機能実装 |
| トークン数増加 | `reading` は `text` より短くなることが多いため影響は限定的 |

## Related

- Issue: N/A
- Related Specs: `script-generation`, `data-models`, `audio-synthesis`
