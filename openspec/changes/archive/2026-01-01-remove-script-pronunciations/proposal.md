# Proposal: script.pronunciations フィールドの削除

## Why

`VideoScript.pronunciations` フィールドは定義されているが実際には使用されていない。このフィールドとそれに関連するコードを削除し、コードベースを簡素化する必要がある。

### 背景

現在、発音制御には以下の3つの機能が存在する：

1. **`narration.reading`** - 各ナレーションのカタカナ読み（LLM生成、音声合成で実際に使用）
2. **`config.pronunciation.custom`** - プロジェクト全体の手動発音辞書（VOICEVOX UserDict API経由で使用）
3. **`script.pronunciations`** - スクリプトごとの発音辞書（**実装されているが使用されていない**）

調査の結果、`script.pronunciations` は以下の理由で冗長であることが判明：

- LLMがスクリプト生成時に生成するが、音声合成プロセスで一切参照されない
- `narration.reading` フィールドで各フレーズの発音が完全にカバーされている
- プロジェクト全体の辞書は `config.pronunciation.custom` で管理できる

## What Changes

以下を削除する：

1. `VideoScript.pronunciations` フィールド（Pydanticモデル）
2. `PronunciationEntry` クラス（pronunciationsでのみ使用）
3. LLMプロンプト内の pronunciations セクション（全4種類）
4. `generate_script()` 関数内のパース処理

## 影響範囲

### 削除されるもの
- `src/movie_generator/script/generator.py`:
  - `PronunciationEntry` クラス定義
  - `VideoScript.pronunciations` フィールド
  - pronunciations パース処理（約13行）
  - 全4プロンプトから pronunciations 説明セクション（各約8-10行）

### 保持されるもの
- `narration.reading` - 音声合成で実際に使用
- `config.pronunciation.custom` - プロジェクト共通辞書として機能
- `PronunciationDictionary` クラス - config.pronunciation.custom で使用

### 後方互換性
- 既存の `script.yaml` に `pronunciations` フィールドが含まれていても、Pydantic が無視するため問題なし

## 期待される効果

- コード削減: 約70行
- メンテナンス性向上: 使用されない機能の削除
- 明確化: 発音制御の方法が2つに絞られる（reading + config辞書）

## 実装状況

✅ 実装完了（全テスト201件パス）
