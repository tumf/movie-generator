# Design: Random Persona Selection

## Context

現在のシステムは、設定ファイルで定義されたすべてのペルソナを動画生成に使用する。Web UIからの動画生成では、常に同じペルソナの組み合わせが使われるため、コンテンツの多様性に欠ける。

**Constraints:**
- 既存の設定ファイル（単一ペルソナ、固定多話者）は引き続き動作すること
- CLIからの明示的なペルソナ指定は優先されること
- Web UIではデフォルトでランダム選択を有効化すること

**Stakeholders:**
- Web UIユーザー（自動化された動画生成）
- CLIユーザー（細かい制御が必要）
- システム開発者（テストとデバッグの容易性）

## Goals / Non-Goals

**Goals:**
- 3名のペルソナプールから2名をランダムに選択して対話を生成
- 設定ファイルでの有効/無効切り替え
- テスト時の再現性確保（seed指定）
- 後方互換性の維持

**Non-Goals:**
- ペルソナの重み付け選択（将来的な拡張候補）
- 動的なペルソナ特性の変更
- 3名以上の対話生成（現在は2名のみ対応）

## Decisions

### Decision 1: Configuration Structure

**What:** `persona_pool` セクションを `Config` に追加

```yaml
personas:
  - id: "zundamon"
    name: "ずんだもん"
    character: "..."
    synthesizer: {...}
  - id: "metan"
    name: "四国めたん"
    character: "..."
    synthesizer: {...}
  - id: "tsumugi"
    name: "春日部つむぎ"
    character: "..."
    synthesizer: {...}

persona_pool:
  enabled: true
  count: 2
  seed: null  # Optional, for testing
```

**Why:**
- 明示的な有効/無効切り替えが可能
- `count` により将来的な拡張（3名以上）に対応可能
- `seed` によりテストの再現性を確保

**Alternatives considered:**
- ❌ `narration.mode: "random_dialogue"` の追加
  - 理由: modeは台本フォーマット（single/dialogue）を表すべきで、選択ロジックと混在させるべきでない
- ❌ CLI専用オプション（設定ファイル不要）
  - 理由: Web UIではデフォルト動作として設定ファイルに記述したい

### Decision 2: Selection Timing

**What:** `generate_script()` の開始時にペルソナを選択

**Why:**
- スクリプト生成前に選択することで、LLMプロンプトに正しいペルソナ情報を渡せる
- 選択されたペルソナIDをログに残せる（デバッグ用）
- 音声合成・動画生成では選択後のペルソナリストのみ使用

**Alternatives considered:**
- ❌ 設定ファイル読み込み時に選択
  - 理由: 同じ設定で複数回生成する場合、毎回異なる組み合わせを得たい
- ❌ プロンプト生成時に選択
  - 理由: プロンプト生成関数はピュアであるべき（副作用を持たない）

### Decision 3: Random Selection Algorithm

**What:** Python標準ライブラリの `random.sample()` を使用

```python
import random

def select_personas_from_pool(
    personas: list[dict],
    pool_config: PersonaPoolConfig | None
) -> list[dict]:
    if not pool_config or not pool_config.enabled:
        return personas
    
    if pool_config.seed is not None:
        random.seed(pool_config.seed)
    
    if pool_config.count > len(personas):
        raise ValueError(
            f"Cannot select {pool_config.count} personas from pool of {len(personas)}"
        )
    
    selected = random.sample(personas, k=pool_config.count)
    return selected
```

**Why:**
- `random.sample()` は重複なしのランダム抽出を保証
- `seed` 指定により再現可能なテストが可能
- シンプルで保守しやすい

**Alternatives considered:**
- ❌ `numpy.random.choice()` の使用
  - 理由: 依存関係を増やしたくない、標準ライブラリで十分
- ❌ 重み付けランダム選択（weighted random）
  - 理由: 現時点で要件にない、将来的な拡張として検討

### Decision 4: CLI Option Design

**What:** `--persona-pool-count` および `--persona-pool-seed` オプションを追加

```bash
# Use config default (2 personas)
uv run movie-generator generate <url> -c config.yaml

# Override count
uv run movie-generator generate <url> -c config.yaml --persona-pool-count 3

# Reproducible selection for testing
uv run movie-generator generate <url> -c config.yaml --persona-pool-seed 42
```

**Why:**
- 設定ファイルのデフォルト値を尊重しつつ、実行時のオーバーライドが可能
- `--persona-pool-seed` によりCI/CD環境での再現可能なテストが可能
- オプション名が明確で、既存のCLIインターフェースと一貫性がある

**Alternatives considered:**
- ❌ `--random-personas 2` のような単一オプション
  - 理由: seedを別途指定したい場合に不便

## Risks / Trade-offs

### Risk 1: ペルソナの偏り

**Risk:** ランダム選択により、特定のペルソナが長期間選ばれない可能性

**Mitigation:**
- 現時点では許容（3名から2名選択なので、極端な偏りは発生しにくい）
- 将来的な拡張: ペルソナ使用回数を記録し、均等化するロジックを追加

### Risk 2: Seed指定の誤用

**Risk:** ユーザーがseedを固定したまま運用し、ランダム性が失われる

**Mitigation:**
- ドキュメントで「seedはテスト用」と明記
- Web UIではseed指定なし（完全にランダム）

### Risk 3: 後方互換性の破壊

**Risk:** 既存の設定ファイルでの動作変更

**Mitigation:**
- `persona_pool` 未指定時は従来通りすべてのペルソナを使用
- `persona_pool.enabled: false` で明示的に無効化可能
- テストケースで既存設定の動作を保証

## Migration Plan

### Phase 1: Implementation (Week 1)
1. Data modelの追加（`PersonaPoolConfig`）
2. Selection logicの実装（`select_personas_from_pool()`）
3. Unit testsの作成

### Phase 2: Integration (Week 2)
1. `generate_script()` への統合
2. CLI optionsの追加
3. Integration testsの作成

### Phase 3: Web UI Integration (Week 3)
1. Web UI用デフォルト設定の作成
2. E2E testsの実行
3. ドキュメント更新

### Rollback Plan

もしバグや問題が発生した場合:
1. `persona_pool.enabled: false` を設定して従来動作に戻す
2. コードの変更をrevert
3. Web UIのデフォルト設定を無効化

## Open Questions

- Q1: 3名以上のペルソナ対話をサポートする予定はあるか？
  - A: 現時点では予定なし。将来的な拡張としてcountを増やす可能性はあるが、Remotionテンプレートの対応が必要。

- Q2: ペルソナ選択後のログ出力はどの程度詳細にするか？
  - A: 選択されたペルソナIDのみをINFOレベルでログ出力。デバッグ時は `--verbose` で全候補と選択理由を出力。

- Q3: Web UIからseed指定できるようにするか？
  - A: 現時点では不要。将来的にユーザーが「同じ組み合わせを再生成したい」という要望があれば検討。
