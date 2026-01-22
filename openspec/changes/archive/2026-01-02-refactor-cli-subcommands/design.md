# Design: CLIサブコマンド構造

## Context

Movie GeneratorのCLIは現在、`generate` コマンドのみで全処理（スクリプト生成 → 音声生成 → スライド生成 → ビデオレンダリング）を実行する。
ユーザーからの要望として、各段階を個別に実行できるようにしたいという要求がある。

### 制約

- Python 3.13+
- Click ライブラリを使用（既存）
- Rich ライブラリで進捗表示（既存）
- 後方互換性を維持する必要がある

## Goals / Non-Goals

### Goals

1. 各処理段階を個別に実行可能にする
2. 段階的なデバッグを容易にする
3. 中間ファイルの再利用を明示的にサポート
4. 共通オプション（`--force`, `--quiet`, `--verbose`, `--dry-run`）の追加

### Non-Goals

- インタラクティブモードの追加（将来検討）
- コマンドエイリアスの追加
- 設定ファイルのマイグレーション

## Decisions

### 1. ファイル構造: `cli.py` 内でグループ化

**決定**: `cli.py` 内で `@cli.group()` を使用してサブコマンドをグループ化する。

**理由**:
- シンプルで保守しやすい
- 現在のコードベースの規模に適している
- 将来的に分割が必要になった場合も対応可能

**却下した代替案**:
- `cli/commands/` ディレクトリへの分割: 現時点では過剰な抽象化

### 2. 共通ロジックの抽出

各段階のロジックを以下の内部関数として抽出:

```python
def _create_script(url: str, output_dir: Path, cfg: Config, ...) -> VideoScript:
    """スクリプト生成ロジック"""
    ...

def _generate_audio(script: VideoScript, output_dir: Path, ...) -> list[Path]:
    """音声生成ロジック"""
    ...

def _generate_slides(script: VideoScript, output_dir: Path, ...) -> list[Path]:
    """スライド生成ロジック"""
    ...

def _render_video(script: VideoScript, output_dir: Path, ...) -> Path:
    """ビデオレンダリングロジック"""
    ...
```

### 3. オプションの相互排他性

- `--quiet` と `--verbose` は相互排他
- `--dry-run` は `--force` と組み合わせ可能（dry-run中はforce無視）
- `--dry-run` は `--verbose` と組み合わせ可能（詳細な処理内容表示）

### 4. 出力レベルの定義

| モード | 成功時出力 | エラー時出力 | 進捗表示 |
|--------|-----------|-------------|---------|
| 通常（デフォルト） | ステップ完了メッセージ | エラー詳細 | スピナー |
| `--quiet` | 最終出力パスのみ | エラー詳細 | なし |
| `--verbose` | 詳細ログ（パス、サイズ、時間等） | スタックトレース | 詳細プログレス |

### 5. `--dry-run` の動作

- ファイルの読み込みは実行
- ファイルの書き込み、API呼び出し、外部プロセス実行はスキップ
- 「何が実行されるか」を出力

```
[DRY-RUN] Would fetch content from: https://example.com/blog
[DRY-RUN] Would generate script with model: anthropic/claude-3.5-sonnet
[DRY-RUN] Would save script to: ./output/script.yaml
```

### 6. 中間ファイルの扱い

| ファイル | 存在時のデフォルト動作 | `--force` 時 |
|---------|----------------------|-------------|
| `script.yaml` | スキップ（既存を使用） | 上書き |
| `audio/*.wav` | スキップ（既存を使用） | 上書き |
| `slides/*.png` | スキップ（既存を使用） | 上書き |
| `output.mp4` | 上書き | 上書き |

## Risks / Trade-offs

### リスク1: コードの複雑化
- **リスク**: 関数抽出により一時的にコードが複雑になる
- **軽減策**: 段階的なリファクタリング、テストの充実

### リスク2: 既存テストの影響
- **リスク**: CLI構造変更によりテストが壊れる可能性
- **軽減策**: 既存の `generate` コマンドの動作を維持

## Migration Plan

1. **Phase 1**: 共通ロジックの関数抽出（既存動作維持）
2. **Phase 2**: サブコマンドの追加
3. **Phase 3**: 共通オプションの追加
4. **Phase 4**: テスト・ドキュメント更新

ロールバック:
- 各Phaseは独立してrevertできる
- `generate` コマンドは常に動作を維持

## Open Questions

- なし（ユーザーとの確認で解決済み）
