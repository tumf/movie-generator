# Change: Remotion レンダリング呼び出しの引数整理と環境チェック共通化

## Why
Remotion レンダリング呼び出しが多数引数/重複した環境チェックを持つと、設定変更の反映漏れや実行経路ごとの差異が生まれやすくなります。引数整理とチェック共通化により保守性を上げます。

## What Changes
- レンダリング呼び出しの引数を設定オブジェクト（param object）にまとめる
- Chrome/コンテナ関連の環境チェックを共通関数へ集約する

## Impact
- Affected specs: `openspec/specs/video-rendering/spec.md`
- Affected code: `src/movie_generator/video/remotion_renderer.py`
