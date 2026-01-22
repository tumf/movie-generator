# Change: ランダムペルソナ選択機能の追加

## Why

Web UIから動画生成を行う際、毎回同じペルソナの組み合わせで対話が生成されるため、コンテンツに単調さが生じる。3名のペルソナ（ずんだもん、めたん、つむぎ）からランダムに2名を抽出して対話させることで、動画のバリエーションを増やし、視聴者の飽きを防ぐ。

## What Changes

- **Config Management**: ペルソナプールの概念を追加
  - 利用可能なペルソナをプールとして定義
  - ランダム選択の設定（有効/無効、選択人数）
- **Script Generation**: ランダム選択ロジックを追加
  - プールから指定人数のペルソナをランダム抽出
  - 抽出されたペルソナで対話シナリオを生成
  - 選択されなかったペルソナは無視
- **Web UI Integration**: Web UIからの動画生成時に自動適用
  - デフォルトで3名プールから2名ランダム選択
  - CLIからは従来通りの動作（明示的に指定されたペルソナのみ使用）

## Impact

- **Affected specs**: 
  - `config-management` (ペルソナプール設定追加)
  - `script-generation` (ランダム選択ロジック追加)
- **Affected code**:
  - `src/movie_generator/config.py` (Config data models)
  - `src/movie_generator/script/generator.py` (Persona selection logic)
  - Web UI configuration (default config with persona pool)
- **Backward compatibility**: 維持される
  - 既存の設定ファイル（personas直接指定）は引き続き動作
  - persona_pool未指定時は従来通りpersonas全員使用
