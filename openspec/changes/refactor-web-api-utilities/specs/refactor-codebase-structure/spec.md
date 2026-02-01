## ADDED Requirements
### Requirement: Web APIユーティリティの共通化
システムは、Web APIルートで共通のリクエストユーティリティ（IP取得）と日時処理ユーティリティを再利用可能なモジュールに分割し、応答内容を変えずに保守性を向上させなければならない（SHALL）。

#### Scenario: ルート間で同一のユーティリティを使用する
- **WHEN** `api_routes.py` と `web_routes.py` がリクエスト処理を行う
- **THEN** IP取得と日時処理は共通ユーティリティを経由する
- **AND** レスポンスの内容は変更されない

### Requirement: Pydantic v2 バリデーションの維持
システムは、`JobResponse` の日時フィールドに対する空文字→`None` 変換を、Pydantic v2 のバリデータAPIで維持しなければならない（SHALL）。

#### Scenario: 空文字の日時を `None` に正規化する
- **WHEN** `JobResponse` に空文字の日時フィールドが渡される
- **THEN** そのフィールドは `None` に変換される
