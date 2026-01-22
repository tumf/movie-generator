# Tasks: ffmpeg→Remotion完全移行

## 1. Remotion側の修正

### 1.1 不要ファイルの削除
- [ ] 1.1.1 `remotion/src/VideoPhrases.tsx` 削除（旧実装、未使用）
- [ ] 1.1.2 `remotion/src/videoData.ts` 削除（ハードコードデータ、未使用）
- [ ] 1.1.3 `remotion/src/Video.tsx` 削除（旧コンポーネント、未使用）

### 1.2 VideoGenerator.tsx修正
- [ ] 1.2.1 `staticFile()`のパス解決確認・修正
- [ ] 1.2.2 TypeScriptエラー修正

### 1.3 Root.tsx修正
- [ ] 1.3.1 動的生成に対応した形式に変更
- [ ] 1.3.2 TypeScriptエラー修正

## 2. Python側の実装

### 2.1 renderer.py全面改修
- [ ] 2.1.1 ffmpeg実装を削除
- [ ] 2.1.2 `ensure_nodejs_available()` 実装
- [ ] 2.1.3 `setup_remotion_public()` 実装
- [ ] 2.1.4 `generate_root_tsx()` 実装
- [ ] 2.1.5 `ensure_npm_dependencies()` 実装
- [ ] 2.1.6 `run_remotion_render()` 実装
- [ ] 2.1.7 `render_video_remotion()` メイン関数実装

### 2.2 CLI修正
- [ ] 2.2.1 `cli.py`のレンダリング呼び出しを`render_video_remotion()`に変更
- [ ] 2.2.2 remotion_rootパスの解決ロジック追加
- [ ] 2.2.3 エラーハンドリング追加

### 2.3 composition.json形式変更
- [ ] 2.3.1 `create_composition()`の出力形式をRemotionに合わせる
- [ ] 2.3.2 フレーズごとにスライドファイルを関連付けるロジック追加

## 3. ドキュメント更新

### 3.1 project.md修正
- [ ] 3.1.1 `ffmpeg`依存を削除
- [ ] 3.1.2 `Node.js/npm`依存を追加
- [ ] 3.1.3 Remotion説明を更新

## 4. テスト

### 4.1 ユニットテスト
- [ ] 4.1.1 `setup_remotion_public()`のテスト
- [ ] 4.1.2 `generate_root_tsx()`のテスト
- [ ] 4.1.3 `create_composition()`のテスト

### 4.2 統合テスト
- [ ] 4.2.1 E2Eレンダリングテスト（最小データセット）
- [ ] 4.2.2 エラーケーステスト（Node.js未インストール時など）

## 依存関係
- 1.x は並行可能
- 2.x は 1.x 完了後
- 3.x は 2.x 完了後
- 4.x は 2.x 完了後

## 完了条件
- `movie-generator generate URL`で字幕付き動画が生成される
- ffmpeg依存が完全に削除されている
- Node.js/npm依存は初回自動インストール
