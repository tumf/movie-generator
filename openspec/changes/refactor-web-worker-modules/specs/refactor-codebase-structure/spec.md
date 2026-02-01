## ADDED Requirements
### Requirement: Webワーカーの責務分割
システムは、Webワーカーの設定・PocketBaseクライアント・生成ラッパー・ワーカーループを専用モジュールに分割し、起動経路と挙動を維持しなければならない（SHALL）。

#### Scenario: 既存の起動方法を維持する
- **WHEN** `python web/worker/main.py` を実行する
- **THEN** 既存と同じ環境変数名で設定が読み込まれる
- **AND** ワーカーが起動してジョブポーリングを開始する
