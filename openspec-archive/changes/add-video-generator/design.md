# Design: Video Generator Architecture

## Context

YouTube向けスライド動画を、ブログURLから一括生成するPythonツール。
ユーザーは複数の動画を同じスタイル（フォント、色、ナレーターキャラなど）で生成したいため、
YAMLベースの設定ファイルで統一的な制御を行う。

### 既存の実験成果

`/Users/tumf/work/study/daihon/` での実験により、以下が確立済み：

1. **フレーズベース方式**: 3-6秒単位のフレーズ分割が字幕同期に最適
2. **VOICEVOX統合**: `voicevox_core.blocking` APIの正しい使用法
3. **固有名詞辞書**: 読み方辞書による発音制御
4. **Remotion**: TypeScript/Reactベースの動画合成

## Goals / Non-Goals

### Goals
- ブログURL → 動画ファイル の一括変換
- YAML設定による動画スタイルの統一
- フレーズベースの正確な字幕同期
- 固有名詞の正確な発音
- Python 3.13 + uv によるモダンな開発環境

### Non-Goals
- GUI/Webインターフェース（CLIのみ）
- リアルタイムプレビュー
- 動画編集機能（生成のみ）
- マルチ言語対応（日本語のみ）

## Decisions

### 1. プロジェクト構成

```
movie-generator/
├── pyproject.toml           # uv + Python 3.13
├── config/
│   ├── default.yaml         # デフォルト設定
│   └── examples/            # プロジェクト別設定例
├── src/
│   └── movie_generator/
│       ├── __init__.py
│       ├── cli.py           # CLIエントリーポイント
│       ├── config.py        # YAML設定読み込み
│       ├── content/
│       │   ├── fetcher.py   # URL→コンテンツ取得
│       │   └── parser.py    # コンテンツ解析
│       ├── script/
│       │   ├── generator.py # LLMスクリプト生成
│       │   └── phrases.py   # フレーズ分割
│       ├── audio/
│       │   ├── voicevox.py  # VOICEVOX統合
│       │   └── dictionary.py # 発音辞書
│       ├── slides/
│       │   └── generator.py # スライド画像生成
│       └── video/
│           └── renderer.py  # 動画レンダリング
└── tests/
```

### 2. 設定ファイル形式（YAML）

```yaml
# config.yaml
project:
  name: "My YouTube Channel"
  output_dir: "./output"

style:
  resolution: [1920, 1080]
  fps: 30
  font_family: "Noto Sans JP"
  primary_color: "#FFFFFF"
  background_color: "#1a1a2e"

audio:
  engine: "voicevox"
  speaker_id: 3  # Zundamon
  speed_scale: 1.0

narration:
  character: "ずんだもん"
  style: "casual"  # casual, formal, educational

content:
  llm_provider: "openrouter"
  model: "gemini-3-pro"

slides:
  provider: "openrouter"
  model: "nonobananapro"
  style: "presentation"  # presentation, illustration, minimal

video:
  renderer: "remotion"
  template: "default"
  output_format: "mp4"

pronunciation:
  # 固有名詞読み方辞書（VOICEVOX UserDict形式）
  custom:
    "Bubble Tea":
      reading: "バブルティー"  # カタカナ
      accent: 5               # アクセント核位置
      word_type: "PROPER_NOUN"  # PROPER_NOUN, COMMON_NOUN, VERB, ADJECTIVE, SUFFIX
      priority: 10            # 優先度 (1-10, 高いほど優先)
    "Ratatui":
      reading: "ラタトゥイ"
      accent: 4
      word_type: "PROPER_NOUN"
      priority: 10
    "人月":
      reading: "ニンゲツ"
      accent: 1
      word_type: "COMMON_NOUN"
      priority: 10
```

### 3. 処理パイプライン

```
URL入力
    ↓
[1. Content Fetch] - URL→Markdown/HTML取得
    ↓
[2. Script Generation] - LLMでYouTube台本生成
    ↓
[3. Phrase Split] - 3-6秒単位のフレーズ分割
    ↓
[4. Pronunciation] - 読み方辞書適用
    ↓
[5. Audio Generation] - VOICEVOX音声合成
    ↓
[6. Slide Generation] - OpenRouter + NonobananaPro
    ↓
[7. Video Render] - Remotion（TypeScript/React）
    ↓
出力: MP4ファイル + メタデータJSON
```

### 4. 動画レンダリング: Remotion

**Remotion**を使用（既存実験資産を活用）:
- 高品質なアニメーション
- TypeScript/Reactベースで柔軟なテンプレート
- `/Users/tumf/work/study/daihon/`での実績あり

**構成**:
- Python側: アセット生成（音声、スライド）+ メタデータJSON出力
- Remotion側: JSONを読み込んで動画レンダリング

```
Python → assets/ + composition.json → Remotion → output.mp4
```

### 5. スライド生成: OpenRouter + NonobananaPro

**NonobananaPro**（OpenRouter経由）を使用してスライド画像を生成:
- 高品質なイラスト/スライド画像生成
- YouTube向けの視覚的に魅力的なコンテンツ

```yaml
# config.yaml での設定例
slides:
  provider: "openrouter"
  model: "nonobananapro"
  style: "presentation"  # presentation, illustration, minimal
```

**処理フロー**:
1. 台本の各セクションからプロンプト生成
2. OpenRouter API経由でNonobananaPro呼び出し
3. 1920x1080画像を取得・保存

### 6. 音声合成とユーザー辞書

VOICEVOX Core直接使用（既存実装を移植）:
```python
from voicevox_core import UserDictWord
from voicevox_core.blocking import UserDict, OpenJtalk, Synthesizer, VoiceModelFile

# ユーザー辞書を作成
user_dict = UserDict()
user_dict.add_word(UserDictWord(
    surface="Bubble Tea",
    pronunciation="バブルティー",  # カタカナ
    accent_type=5,
    word_type="PROPER_NOUN",
    priority=10
))

# OpenJTalkに適用
open_jtalk = OpenJtalk(dict_dir)
open_jtalk.use_user_dict(user_dict)

# Synthesizerに渡す
synthesizer = Synthesizer(onnxruntime, open_jtalk)
```

**ユーザー辞書の利点**:
- 形態素解析が正しく動作（アクセント・イントネーション正常）
- YAMLで辞書管理、起動時に自動適用
- 辞書はJSON形式で保存・読み込み可能

## Risks / Trade-offs

| リスク | 軽減策 |
|--------|--------|
| VOICEVOX環境依存（macOS dylib） | 環境変数でパス設定可能に |
| LLM API料金 | キャッシュ機構、ローカルLLM対応 |
| 長時間動画のメモリ | ストリーミング処理 |
| アクセント位置の設定が難しい | デフォルト値（0=自動推定）を提供 |

## Migration Plan

1. Phase 1: コア機能（URL→台本→音声生成 + Remotion連携基盤）
2. Phase 2: スライド生成（NonobananaPro統合）
3. Phase 3: フルパイプライン完成 + CLI

## Open Questions

- [ ] 音声モデル（.vvm）の配布方法
- [ ] YouTube自動アップロード機能の要否
- [ ] Remotionテンプレートの共有方法

## Technical Notes

### VOICEVOX UserDict調査結果

実験により以下が確認済み（2024-12-29）:

1. **VOICEVOX Coreはユーザー辞書をサポート**
   - `voicevox_core.UserDictWord` でエントリ作成
   - `voicevox_core.blocking.UserDict` で辞書管理
   - `OpenJtalk.use_user_dict()` で適用

2. **形態素解析の問題は解決済み**
   - 単純なひらがな置換では形態素解析が壊れる
   - UserDictを使えばOpenJTalk辞書に正しく登録され、アクセント・イントネーションが正常

3. **実装パターン**
   ```python
   user_dict = UserDict()
   user_dict.add_word(UserDictWord(
       surface="Bubble Tea",
       pronunciation="バブルティー",  # カタカナ必須
       accent_type=5,                # 0=自動推定
       word_type="PROPER_NOUN",
       priority=10
   ))
   open_jtalk = OpenJtalk(dict_dir)
   open_jtalk.use_user_dict(user_dict)
   ```

4. **辞書の永続化**
   - `user_dict.save("dict.json")` でJSON保存
   - `user_dict.load("dict.json")` で読み込み
