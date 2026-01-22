# Change: ペルソナ音声フォールバックのバグ修正

## Why

マルチスピーカーモードで動画を生成する際、ランダムに選択された2人のアクターが全員ずんだもんの声で話してしまうバグが発生している。

期待される動作: 各アクターが自分のキャラクター音声で話す
実際の動作: 全員がずんだもん（最初のペルソナ）の声で話す

## What Changes

- `persona_id` が `synthesizers` 辞書に見つからない場合の警告ログを追加
- 音声生成前に `persona_id` の検証を追加し、不明な `persona_id` を早期に検出
- フォールバック動作を明確化：エラーを発生させるか、警告付きで続行するかを設定可能に

## Impact

- Affected specs: `audio-synthesis`
- Affected code:
  - `src/movie_generator/audio/core.py` (L231-235)
  - `src/movie_generator/cli.py` (L556-561)
