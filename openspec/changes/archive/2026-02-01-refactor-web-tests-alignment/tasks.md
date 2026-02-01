## 1. Implementation
- [x] 1.1 `web/tests/test_worker_progress.py` を現行のワーカー実装に合わせて更新する
  - **Verify**: `MovieGeneratorWrapper` の生成に必要な引数と import が一致していることを確認
  - **Complete**: `Config` パラメータを追加し、`sys.path` に worker ディレクトリを追加
- [x] 1.2 `movie_generator` の生成関数をモック化する（script/audio/slides/video）
  - **Verify**: テストが外部APIキーや実ファイル生成なしに実行できることを確認
  - **Complete**: `generate_script_from_url`, `generate_audio_for_script`, `generate_slides_for_script`, `render_video_for_script` をモック化
- [x] 1.3 進捗更新の期待値を「レンジ内の進捗」で検証する
  - **Verify**: script/audio/slides/video の progress が意図した範囲に収まることを確認
  - **Complete**: script(0-20%), audio(20-55%), slides(55-80%), video(80-100%) の範囲で検証

## 2. Validation
- [x] 2.1 `cd web && uv run pytest tests/test_worker_progress.py -v` を実行する
  - **Verify**: テストが成功すること
  - **Complete**: 5つのテストすべてが成功。外部APIキーなしでも動作確認済み
