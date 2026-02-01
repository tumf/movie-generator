## 1. Implementation
- [ ] 1.1 `web/tests/test_worker_progress.py` を現行のワーカー実装に合わせて更新する
  - **Verify**: `MovieGeneratorWrapper` の生成に必要な引数と import が一致していることを確認
- [ ] 1.2 `movie_generator` の生成関数をモック化する（script/audio/slides/video）
  - **Verify**: テストが外部APIキーや実ファイル生成なしに実行できることを確認
- [ ] 1.3 進捗更新の期待値を「レンジ内の進捗」で検証する
  - **Verify**: script/audio/slides/video の progress が意図した範囲に収まることを確認

## 2. Validation
- [ ] 2.1 `cd web && uv run pytest tests/test_worker_progress.py -v` を実行する
  - **Verify**: テストが成功すること
