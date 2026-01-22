# Proposal: add-morpheme-pronunciation-fallback

## Why

現状、script.yaml の pronunciations はLLMが生成しているが、LLMが漏らした英単語や専門用語（例: "BETA"）は読み方が登録されず、VOICEVOXが誤読する可能性がある。

形態素解析を使って、LLMが漏らした単語を自動的に補完することで、音声品質を向上させる。

## What Changes

### 1. `VoicevoxSynthesizer.prepare_texts()` の追加

生のテキストリストから形態素解析で pronunciations を抽出し、辞書に登録する新メソッドを追加。

### 2. CLI の音声生成フローに形態素解析補完を統合

1. LLM pronunciations を優先度10で登録
2. 形態素解析で未登録単語を優先度5で補完
3. エラーハンドリング（MeCab未設定時は警告のみ）

### 影響範囲

- `src/movie_generator/audio/voicevox.py`: `prepare_texts()` メソッド追加
- `src/movie_generator/cli.py`: 音声生成フローに形態素解析補完を統合
- `openspec/specs/audio-furigana/spec.md`: 要件とAPIリファレンスを追加
