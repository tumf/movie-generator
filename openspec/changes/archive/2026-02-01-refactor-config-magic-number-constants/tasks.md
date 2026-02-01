## 1. Implementation
- [x] 1.1 設定の数値デフォルト/制約を命名定数へ集約する（検証: 主要な数値リテラルが定数参照に置換されることを確認）

## 2. Tests
- [x] 2.1 既存の設定ロード/検証テストが維持される（検証: `uv run pytest -k config -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] `src/movie_generator/config.py` の検証境界が数値リテラルのままの箇所を命名定数に置き換える（例: `VoicevoxSynthesizerConfig.speaker_id` の `ge=0` は `src/movie_generator/config.py:21`、`StyleConfig.fps` の `ge=1` は `src/movie_generator/config.py:81`、`TransitionConfig.duration_frames` の `ge=1` は `src/movie_generator/config.py:189`、`BgmConfig.fade_in_seconds`/`fade_out_seconds` の `ge=0.0` は `src/movie_generator/config.py:260-266`、`VideoConfig.render_concurrency`/`render_timeout_seconds` の `ge=1` は `src/movie_generator/config.py:302-308`、`PronunciationWord.accent` の `ge=0` は `src/movie_generator/config.py:317-318`、`PersonaPoolConfig.count` の `ge=1` は `src/movie_generator/config.py:342-344`）
- [x] `generate_default_config_yaml` 内の数値デフォルトを命名定数参照に置換する（例: `resolution: [1280, 720]`, `fps: 30`, `crf: 28`, `speaker_id: 3`, `speed_scale: 1.0` が `src/movie_generator/config.py:464-476`）
