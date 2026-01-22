# Change: dataclass から Pydantic への移行

## Why

現在のコードベースでは、設定クラス（`config.py`）は Pydantic を使用していますが、
ドメインモデルクラスは `@dataclass` を使用しています。この不統一により以下の問題があります：

- **バリデーションの欠如**: dataclass はデータ検証機能がなく、不正なデータが混入するリスクがある
- **シリアライゼーション**: JSON/YAML との相互変換で追加コードが必要
- **型強制の欠如**: 型ヒントがあっても実行時には強制されない
- **一貫性の欠如**: 設定とドメインモデルで異なるパターンを使用している

Pydantic に統一することで、型安全性、自動バリデーション、シリアライゼーションサポートを
全モデルクラスで利用可能になります。

## What Changes

以下のファイルの dataclass を Pydantic `BaseModel` に移行します：

### script モジュール
- `script/generator.py`: `Narration`, `ScriptSection`, `PronunciationEntry`, `VideoScript`
- `script/phrases.py`: `Phrase`

### content モジュール
- `content/parser.py`: `ContentMetadata`, `ImageInfo`, `ParsedContent`

### video モジュール
- `video/renderer.py`: `CompositionData`
- `video/remotion_renderer.py`: `RemotionPhrase`

### audio モジュール
- `audio/dictionary.py`: `DictionaryEntry`
- `audio/voicevox.py`: `AudioMetadata`
- `audio/furigana.py`: `MorphemeReading`

**BREAKING**: なし（内部実装の変更のみ、外部APIは維持）

## Impact

- 影響する specs: なし（新規 capability の追加）
- 影響するコード:
  - `src/movie_generator/script/generator.py`
  - `src/movie_generator/script/phrases.py`
  - `src/movie_generator/content/parser.py`
  - `src/movie_generator/video/renderer.py`
  - `src/movie_generator/video/remotion_renderer.py`
  - `src/movie_generator/audio/dictionary.py`
  - `src/movie_generator/audio/voicevox.py`
  - `src/movie_generator/audio/furigana.py`
- テスト: 既存テストが通ることを確認（API互換性維持）
