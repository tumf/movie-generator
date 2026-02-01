# Change: docker-compose 環境変数の重複解消

## Why
`web/docker-compose.yml` の PocketBase 環境変数に重複があり、設定の曖昧さや運用ミスを誘発する。

## What Changes
- PocketBase の環境変数定義を一意化し、重複を削除する

## Impact
- Affected specs: `specs/refactor-codebase-structure/spec.md`
- Affected code: `web/docker-compose.yml`
