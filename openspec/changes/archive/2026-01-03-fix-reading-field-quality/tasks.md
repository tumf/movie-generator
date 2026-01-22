# Implementation Tasks

## 1. プロンプト設計

- [x] 1.1 促音ルールの強化
  - [x] 1.1.1 CRITICAL マーカーの追加
  - [x] 1.1.2 促音例の拡充（3例→9例以上）
  - [x] 1.1.3 誤った例の明示（「ツッテ」×、「ッテ」○）
- [x] 1.2 スペースルールの追加
  - [x] 1.2.1 スペース挿入ルールの定義
  - [x] 1.2.2 良い例・悪い例の作成
- [x] 1.3 優先度の明示
  - [x] 1.3.1 CRITICAL REQUIREMENT セクションの追加
  - [x] 1.3.2 自己チェック項目への追加

## 2. プロンプト実装

- [x] 2.1 日本語単話者プロンプト更新（`SCRIPT_GENERATION_PROMPT_JA`）
  - [x] 2.1.1 CRITICAL REQUIREMENT セクション追加
  - [x] 2.1.2 促音ルール強化（9例）
  - [x] 2.1.3 スペースルール追加
- [x] 2.2 英語単話者プロンプト更新（`SCRIPT_GENERATION_PROMPT_EN`）
  - [x] 2.2.1 CRITICAL REQUIREMENT セクション追加
- [x] 2.3 日本語対話プロンプト更新（`SCRIPT_GENERATION_PROMPT_DIALOGUE_JA`）
  - [x] 2.3.1 単話者版と同じルールを適用
- [x] 2.4 英語対話プロンプト更新（`SCRIPT_GENERATION_PROMPT_DIALOGUE_EN`）
  - [x] 2.4.1 CRITICAL REQUIREMENT セクション追加

## 3. 検証

- [x] 3.1 促音テストケース作成
  - [x] 3.1.1 「って」「った」「っぱ」など促音パターンを含むサンプル作成（9パターン）
  - [x] 3.1.2 プロンプトに組み込み完了
  - [x] 3.1.3 自動検証スクリプトで確認済み
- [x] 3.2 スペーステストケース作成
  - [x] 3.2.1 良い例・悪い例をプロンプトに追加
  - [x] 3.2.2 プロンプト内で明示的にルール化
- [x] 3.3 既存テストの実行
  - [x] 3.3.1 test_script_generator.py 実行 - 全10テスト合格
  - [x] 3.3.2 後方互換性確認 - 問題なし

## 4. ドキュメント更新

- [x] 4.1 `AGENTS.md`のReading Field Quality Checklistを更新
- [ ] 4.2 `docs/SLIDE_PROMPT_EXAMPLES.md`に促音・スペースルール追加（オプショナル）
