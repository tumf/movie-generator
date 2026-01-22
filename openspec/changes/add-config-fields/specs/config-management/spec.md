## ADDED Requirements
### Requirement: 発音LLMモデルの設定
システムは、発音（フリガナ）生成に使用するLLMモデルIDを設定ファイルで指定できなければならない（SHALL）。

#### Scenario: 発音モデルの指定
- **GIVEN** `audio.pronunciation_model: "openai/gpt-4o-mini"` が設定されている
- **WHEN** 発音LLMが呼び出される
- **THEN** 指定されたモデルIDが使用される

### Requirement: レンダリング実行設定
システムは、動画レンダリングの並列度とタイムアウトを設定ファイルで指定できなければならない（SHALL）。

#### Scenario: レンダリング設定の反映
- **GIVEN** `video.render_concurrency` と `video.render_timeout_seconds` が設定されている
- **WHEN** Remotionレンダリングが実行される
- **THEN** 指定された並列度とタイムアウトが適用される
