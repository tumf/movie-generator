## Context
`web/worker/main.py` に設定読込、PocketBaseクライアント、生成処理、ワーカーループが集約されており、改修の影響範囲が広い。

## Goals / Non-Goals
- Goals:
  - 責務単位でモジュール分割し、読みやすさと再利用性を高める
  - 起動経路（`python main.py`）と環境変数名を維持する
- Non-Goals:
  - 進捗算出ロジックや生成フローの変更
  - 外部APIの振る舞い変更

## Decisions
- 設定は `pydantic-settings` ベースの `WorkerSettings` に統一する
- `main.py` は最小のエントリポイントにし、他ロジックは専用モジュールへ移動する
- モジュール構成（案）:
  - `settings.py`
  - `pocketbase_client.py`
  - `movie_config_factory.py`
  - `generator.py`
  - `worker.py`

## Risks / Trade-offs
- 既存の相対インポート経路が変わるため、パス解決の不整合が出る可能性がある
- 既存テストが import 経路変更に追従できない場合は追加修正が必要

## Migration Plan
1. 新モジュールへクラス/関数を移動し、`main.py` から参照する
2. 起動確認（ローカル/コンテナ）と import エラーの解消

## Open Questions
- なし
