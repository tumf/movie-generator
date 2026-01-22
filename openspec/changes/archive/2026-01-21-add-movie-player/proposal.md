# Change: 動画生成完了画面にムービープレイヤーを追加

## Why

現在、Web インターフェースで動画生成が完了すると、ダウンロードボタンのみが表示される。
ユーザーはダウンロード前に動画を確認できないため、意図した内容かどうかを確認するために
一度ダウンロードする必要がある。インラインプレイヤーを追加することで、ダウンロード前に
動画を確認でき、ユーザー体験が向上する。

## What Changes

- 生成完了画面 (`partials/job_status.html`) にインライン動画プレイヤーを追加
- プレイヤーはダウンロードボタンの上に配置
- HTML5 video 要素を使用（ブラウザ標準コントロール）
- 動画ストリーミング配信用の API エンドポイントを追加

## Impact

- Affected specs: `web-interface` (新規作成)
- Affected code:
  - `web/api/templates/partials/job_status.html`
  - `web/api/routes/api_routes.py`
