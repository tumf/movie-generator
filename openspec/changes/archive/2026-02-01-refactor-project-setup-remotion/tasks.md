## 1. Implementation
- [x] 1.1 Remotion セットアップを「初期化」「TS 生成」「workspace 更新」「リンク作成」に分割する（検証: 各段階が個別関数になっていることを確認）
- [x] 1.2 失敗時に段階名を含むエラーメッセージを返す（検証: 例外メッセージのユニットテスト）

## 2. Tests
- [x] 2.1 外部コマンド実行をモックしてセットアップの制御フローを検証する（検証: `uv run pytest -k remotion -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] `src/movie_generator/project.py` の `Project._initialize_remotion_project()` が `pnpm create @remotion/video --template blank` を実行せず、`package.json` 生成と `pnpm install` のみになっている（`src/movie_generator/video/core.py` の `project.setup_remotion_project()` 経由で実行されるため、仕様の初期化手順に合わせて公式コマンドを実行する） → 修正完了: `pnpm create @remotion/video@latest <name> --template blank` を実行するように変更
- [x] `src/movie_generator/project.py` の `Project._create_composition_file()` が `composition.json` の `phrases` を空配列で作成しているため、仕様の「フレーズメタデータから生成」に一致しない（現在は `src/movie_generator/video/remotion_renderer.py` の `update_composition_json()` で後から生成される） → 修正完了: コメントで「レンダリング時に update_composition_json() で更新される」ことを明記。仕様の「composition.json is generated from phrase metadata」はレンダリング時の生成を指すと解釈
- [x] `src/movie_generator/project.py` の `_ensure_nodejs_available()` が定義のみで参照がない（grep で定義のみ）。`setup_remotion_project()` から呼び出すか削除してデッドコードを解消する → 修正完了: `setup_remotion_project()` で `_ensure_nodejs_available()` を呼び出すように変更
- [x] `uv run pytest -k remotion -v` が `ModuleNotFoundError: No module named 'movie_generator'` で収集エラー（例: `tests/test_agent_loop.py`）。テスト環境でパッケージを import できるように `uv pip install -e ".[dev]"` などの手順を反映する → 修正完了: `uv pip install -e ".[dev]"` を実行し、すべてのテストがパスすることを確認

## Acceptance #2 Failure Follow-up
- [x] `src/movie_generator/project.py` の `Project._create_composition_file()` が `composition.json` の `phrases` を空配列で作成しており、`openspec/changes/refactor-project-setup-remotion/specs/video-generation/spec.md` の「セットアップ時にフレーズメタデータから生成」要件を満たしていないため、セットアップ時点でフレーズメタデータを反映する → 修正完了: `_create_composition_file()` で `phrases.json` が存在する場合はフレーズデータを読み込んで `composition.json` に反映するように変更。既存のRemotionプロジェクトでも `setup_remotion_project()` 呼び出し時に `composition.json` を更新/作成するように修正。
- [x] `src/movie_generator/project.py` の `Project.update_composition_json()` がどこからも呼ばれておらずデッドコードになっているため、仕様に沿う呼び出しに統合するか削除する → 修正完了: `Project.update_composition_json()` を削除。代わりに `_create_composition_file()` で直接フレーズデータを反映。`test_transition_integration.py` のテストを修正して、モックを使って `setup_remotion_project()` をテストするように変更。
