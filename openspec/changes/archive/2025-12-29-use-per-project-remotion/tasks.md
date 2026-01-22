# Implementation Tasks

## 1. 準備フェーズ

- [x] 1.1 pnpmのインストール確認・セットアップ手順をドキュメント化
- [x] 1.2 ルート`pnpm-workspace.yaml`を作成
- [x] 1.3 ルート`package.json`を作成（共有依存関係定義）

## 2. TypeScriptコンポーネント生成ロジック実装

- [x] 2.1 `src/movie_generator/video/templates.py`を作成（TypeScriptテンプレート文字列）
- [x] 2.2 `VideoGenerator.tsx`生成関数を実装（composition.json読み込み版）
- [x] 2.3 `Root.tsx`生成関数を実装（Composition定義、composition.jsonインポート）
- [x] 2.4 `composition.json`生成関数を実装（phrases/audio/slideパスから）
- [x] 2.5 `remotion.config.ts`生成関数を実装

## 3. Python統合実装

- [x] 3.1 `src/movie_generator/project.py`に`setup_remotion_project()`メソッド追加
  - `pnpm create @remotion/video`実行（初回のみ）
  - `package.json`の動的生成（プロジェクト名反映）
  - TypeScriptコンポーネントの動的生成（templates.pyから）
  - `composition.json`の生成（phrases/audio/slideパス）
  - `public/`へのシンボリックリンク作成
- [x] 3.2 `src/movie_generator/video/remotion_renderer.py`を全面改修
  - プロジェクト未初期化時の`setup_remotion_project()`自動呼び出し
  - pnpm installの自動実行（初回のみ）
  - `npx remotion render`の実行
- [x] 3.3 エラーハンドリング追加
  - pnpm未インストール時の適切なエラーメッセージとインストール手順
  - Node.js未インストール時の適切なエラーメッセージとインストール手順
  - `pnpm create`失敗時のエラーハンドリング

## 4. CLI統合

- [x] 4.1 `src/movie_generator/cli.py`のレンダリングフローを更新
- [x] 4.2 進捗表示の改善（Remotionセットアップステップ追加）

## 5. テスト

- [ ] 5.1 `tests/test_video_e2e.py`を新しいフローに対応
- [ ] 5.2 新規プロジェクト生成のE2Eテスト追加
- [ ] 5.3 既存プロジェクトの移行テスト

## 6. ドキュメント更新

- [ ] 6.1 `README.md`の依存関係セクションを更新
- [ ] 6.2 `openspec/project.md`のTech Stack/依存関係を更新
- [ ] 6.3 セットアップ手順にpnpmインストールを追加

## 7. クリーンアップ

- [x] 7.1 既存`remotion/`ディレクトリを削除
- [x] 7.2 不要になったファイル・コードを削除
- [ ] 7.3 `pyproject.toml`から不要な依存関係を削除（あれば）

## 8. 検証

- [ ] 8.1 新規プロジェクト作成から動画生成までのE2E実行
- [ ] 8.2 複数プロジェクトの並列生成テスト
- [ ] 8.3 `openspec validate use-per-project-remotion --strict`実行
