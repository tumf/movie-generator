# Change: ffmpegを削除しRemotionに完全移行

## Why

現在の`renderer.py`にあるffmpegベースの動画レンダリング実装では以下の問題がある：

1. **字幕機能がない**: 静止画+音声のみで字幕が表示されない
2. **スライド切り替えがない**: 最初のスライドのみが使用される
3. **アニメーションがない**: フェードイン/アウト等の効果がない
4. **品質が低い**: 本番用動画として使用できない

既存の`remotion/`ディレクトリには高品質なコンポーネント（`VideoGenerator.tsx`）が実装済みであり、
これを活用することで上記問題をすべて解決できる。

## What Changes

- **削除**: `src/movie_generator/video/renderer.py`のffmpeg実装
- **新規**: Python → Remotion連携機能
  - `remotion/public/`ディレクトリの自動構築
  - `remotion/src/Root.tsx`の動的生成
  - npm依存の自動インストール
  - `npx remotion render`の自動実行
- **修正**: `openspec/project.md`からffmpeg依存を削除
- **修正**: CLI（`cli.py`）のレンダリング呼び出し

## Impact

- Affected specs: `video-generation`
- Affected code:
  - `src/movie_generator/video/renderer.py` - 全面改修
  - `src/movie_generator/cli.py` - レンダリング呼び出し修正
  - `remotion/src/Root.tsx` - 動的生成対応
- Dependencies:
  - ~~ffmpeg~~ → 不要に
  - Node.js / npm → 必須（初回自動インストール）
  - Remotion CLI → 必須（npm経由で自動インストール）

## 参考

- 既存Remotionコンポーネント: `remotion/src/VideoGenerator.tsx`
- 既存設計: `openspec/changes/add-video-generator/design.md`
