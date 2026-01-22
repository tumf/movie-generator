# Tasks: Video Generator Implementation

## 1. プロジェクト初期化
- [x] 1.1 uv でPython 3.13プロジェクト作成（`uv init`）
- [x] 1.2 pyproject.toml に依存関係追加
- [x] 1.3 src/movie_generator/ パッケージ構造作成
- [x] 1.4 pytest設定とサンプルテスト

## 2. 設定管理（config-management）
- [x] 2.1 YAML設定スキーマ定義（pydantic）
- [x] 2.2 設定読み込み・バリデーション実装
- [x] 2.3 デフォルト設定ファイル作成
- [x] 2.4 設定マージ機能（デフォルト + ユーザー設定）

## 3. コンテンツ取得
- [x] 3.1 URL→HTML/Markdown取得（httpx）
- [x] 3.2 コンテンツパーサー（BeautifulSoup/markdownify）
- [x] 3.3 メタデータ抽出（タイトル、著者、日付）

## 4. スクリプト生成
- [x] 4.1 LLMプロバイダー抽象化（OpenRouter対応）
- [x] 4.2 YouTube台本生成プロンプト
- [x] 4.3 フレーズ分割ロジック（3-6秒単位）

## 5. 音声合成（VOICEVOX統合）
- [x] 5.1 ユーザー辞書管理（UserDict）
  - [x] 5.1.1 YAML設定からUserDictWord生成
  - [x] 5.1.2 辞書のJSON保存・読み込み
  - [x] 5.1.3 シンプル形式（文字列のみ）対応
- [x] 5.2 VOICEVOX Core初期化ラッパー
  - [x] 5.2.1 OpenJtalk + UserDict統合（プレースホルダー）
  - [x] 5.2.2 Synthesizer初期化（プレースホルダー）
- [x] 5.3 フレーズ単位音声生成（プレースホルダー）
- [x] 5.4 メタデータ（duration）計算
- [x] 5.5 出力ファイル管理

## 6. スライド生成（OpenRouter + NonobananaPro）
- [x] 6.1 OpenRouter APIクライアント実装（プレースホルダー）
- [x] 6.2 NonobananaPro用プロンプト生成
- [x] 6.3 画像取得・保存処理（プレースホルダー）
- [x] 6.4 スライド-フレーズマッピング
- [x] 6.5 エラー時フォールバック（プレースホルダー画像）

## 7. 動画レンダリング（Remotion）
- [x] 7.1 Remotionプロジェクト初期化（別途必要）
- [x] 7.2 composition.jsonスキーマ定義
- [x] 7.3 Python→Remotion連携スクリプト
- [x] 7.4 字幕コンポーネント実装（Remotion側）
- [x] 7.5 スライドトランジション効果（Remotion側）
- [x] 7.6 音声同期（Remotion側）

## 8. CLI
- [x] 8.1 click によるCLIフレームワーク
- [x] 8.2 `generate` コマンド実装
- [x] 8.3 プログレス表示（rich）
- [x] 8.4 エラーハンドリング

## 9. テスト・ドキュメント
- [x] 9.1 ユニットテスト（設定モジュール）
- [x] 9.2 統合テスト（E2Eパイプライン）
- [x] 9.3 README.md
- [x] 9.4 設定ファイルサンプル

## 依存関係
- 2 は 1 完了後
- 3, 4, 5 は並行可能（2完了後）
- 6 は 4 完了後（台本からプロンプト生成のため）
- 7 は 5, 6 完了後
- 8 は 7 完了後
- 9 は全体完了後

## 技術スタック
- **動画合成**: Remotion（TypeScript/React）
- **スライド生成**: OpenRouter経由 NonobananaPro
- **音声合成**: VOICEVOX Core
- **Python**: 3.13 + uv
