# Change: ふりがな生成のLLM統合改善

## Why

VOICEVOXの音声合成において、漢字や英単語の読み間違いが発生する問題を解決するため、形態素解析とLLMを組み合わせた読み生成機能を強化した。従来の形態素解析のみでは文脈に応じた正確な読み（例：「軽め」→「カルメ」vs「ケイメ」、「今日」→「キョウ」vs「コンニチ」）を判定できなかった。

## What Changes

- LLMによる文脈考慮の読み生成機能を追加
- 形態素解析で読み候補を抽出し、LLMで検証・修正するワークフローを導入
- カタカナ読みのクリーニングユーティリティを追加
- 読み生成用プロンプトの設計・最適化

## Impact

- 影響する仕様: `audio-furigana`
- 影響するコード:
  - `src/movie_generator/audio/furigana.py`
  - `src/movie_generator/audio/voicevox.py`
  - `src/movie_generator/utils/text.py`
