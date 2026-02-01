## ADDED Requirements
### Requirement: Docker Compose 環境変数の一意性
システムは、`web/docker-compose.yml` における環境変数定義を一意に保ち、同一キーの重複を排除しなければならない（SHALL）。

#### Scenario: PocketBase の環境変数が重複しない
- **WHEN** `docker-compose config` を実行する
- **THEN** PocketBase の環境変数に同一キーの重複がない
