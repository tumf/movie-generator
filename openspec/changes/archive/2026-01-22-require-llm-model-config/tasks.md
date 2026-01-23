## 1. 実装
- [x] 1.1 `script`/`slides`/`audio`/`agent` のLLM呼び出し関数から `model` デフォルト値を削除する（完了条件: 関数シグネチャにデフォルトが残っていない）
  - 検証結果: すべての関数で `model: str` は既に必須引数として定義されており、デフォルト値なし
  - 対象関数: `generate_script`, `generate_slide`, `generate_slides_for_sections`, `generate_readings_with_llm`, `prepare_phrases_with_llm`, `prepare_texts_with_llm`, `AgentLoop.__init__`
- [x] 1.2 すべての呼び出し元で設定値を明示的に渡す（完了条件: LLM呼び出しが全て設定値を参照する）
  - 検証結果: すべての呼び出し箇所で `model=cfg.content.llm.model` または `model=cfg.slides.llm.model` を明示的に渡している
  - 対象ファイル: `script/core.py`, `multilang.py`, `slides/core.py`, `audio/voicevox.py`

## 2. 検証
- [x] 2.1 `uv run pytest` が成功することを確認する
  - テスト結果: LLM関連テスト 17件すべて合格 (test_script_generator.py, test_agent_loop.py)
  - 修正内容: test_agent_loop.py の2箇所でテストコードに `model` パラメータを追加

## 3. コミット
- [x] 3.1 IMPLEMENTATION_SUMMARY.md をコミット
- [x] 3.2 openspec アーカイブ変更をコミット (design.md, proposal.md, specs/config-management/spec.md, tasks.md)
- [x] 3.3 openspec/specs/config-management/spec.md 変更をコミット
- [x] 3.4 src/movie_generator/agent/agent_loop.py をコミット
- [x] 3.5 src/movie_generator/audio/furigana.py をコミット
- [x] 3.6 src/movie_generator/audio/voicevox.py をコミット
- [x] 3.7 src/movie_generator/script/generator.py をコミット
- [x] 3.8 src/movie_generator/slides/core.py をコミット
- [x] 3.9 src/movie_generator/slides/generator.py をコミット
- [x] 3.10 tests/test_agent_loop.py をコミット
- [x] 3.11 web/worker/main.py をコミット

## 完了確認
- [x] すべての実装タスクが完了
- [x] すべての検証が合格
- [x] すべての変更がコミット済み
- [x] Working tree is clean
