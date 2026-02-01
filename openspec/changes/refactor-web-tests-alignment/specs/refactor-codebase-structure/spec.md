## ADDED Requirements
### Requirement: ワーカー進捗テストのモック化
システムは、Webワーカーの進捗テストにおいて外部依存（LLM/VOICEVOX/Remotion）をモック化し、ローカル実行のみで進捗更新の整合性を検証できなければならない（SHALL）。

#### Scenario: 外部依存なしで進捗テストが実行できる
- **WHEN** `web/tests/test_worker_progress.py` を実行する
- **THEN** 外部APIキーなしでテストが完了する
- **AND** script/audio/slides/video の進捗が想定範囲内で更新される
