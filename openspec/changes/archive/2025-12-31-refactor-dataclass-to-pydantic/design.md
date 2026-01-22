# Design: dataclass から Pydantic への移行

## Context

Movie Generator プロジェクトでは、現在2種類のデータモデルパターンが混在しています：
- **Pydantic BaseModel**: 設定クラス（`config.py`）
- **dataclass**: ドメインモデル（script, content, video, audio モジュール）

このリファクタリングでは、全てのモデルクラスを Pydantic に統一します。

## Goals / Non-Goals

### Goals
- 全ての dataclass を Pydantic BaseModel に移行
- API 互換性を維持（既存コードの破壊的変更なし）
- 型安全性とランタイムバリデーションの強化
- JSON/YAML シリアライゼーションの簡素化

### Non-Goals
- 新機能の追加（純粋なリファクタリング）
- パフォーマンス最適化
- 外部 API の変更

## Decisions

### 1. 移行対象クラス

以下の dataclass を BaseModel に移行します：

| モジュール | クラス | 備考 |
|-----------|--------|------|
| `script/generator.py` | `Narration`, `ScriptSection`, `PronunciationEntry`, `VideoScript` | LLM レスポンスパース時のバリデーション強化 |
| `script/phrases.py` | `Phrase` | メソッド `get_subtitle_text()` を維持 |
| `content/parser.py` | `ContentMetadata`, `ImageInfo`, `ParsedContent` | HTML パース結果のバリデーション |
| `video/renderer.py` | `CompositionData` | 既存の `asdict()` を `model_dump()` に置換 |
| `video/remotion_renderer.py` | `RemotionPhrase` | Remotion 連携データ |
| `audio/dictionary.py` | `DictionaryEntry` | 辞書エントリのバリデーション |
| `audio/voicevox.py` | `AudioMetadata` | オーディオメタデータ |
| `audio/furigana.py` | `MorphemeReading` | 形態素解析結果 |

### 2. 移行パターン

```python
# Before (dataclass)
@dataclass
class Phrase:
    text: str
    duration: float = 0.0
    section_index: int = 0

    def get_subtitle_text(self) -> str:
        ...

# After (Pydantic)
class Phrase(BaseModel):
    text: str
    duration: float = 0.0
    section_index: int = 0

    model_config = ConfigDict(frozen=False)  # mutable を維持

    def get_subtitle_text(self) -> str:
        ...
```

### 3. 互換性維持の方針

- **asdict() の置換**: `dataclasses.asdict()` → `model.model_dump()`
- **フィールドアクセス**: 属性アクセスは同じ（互換性あり）
- **デフォルト値**: Pydantic の `Field()` で同等に表現
- **mutable オブジェクト**: `model_config = ConfigDict(frozen=False)` で mutable を維持

### 4. Pydantic v2 の機能活用

- `model_validate()`: 辞書からのモデル生成
- `model_dump()`: 辞書へのシリアライズ
- `model_dump_json()`: JSON 文字列へのシリアライズ
- `Field(default=...)`: デフォルト値とバリデーション

## Risks / Trade-offs

### リスク
- **パフォーマンス**: Pydantic のバリデーションにより若干のオーバーヘッド
  - 緩和策: 大量データ処理時は `model_construct()` でバリデーションスキップ可能

### トレードオフ
- **依存関係の増加**: pydantic は既に config.py で使用中のため影響なし
- **学習コスト**: チームは既に Pydantic を使用しているため低い

## Migration Plan

### Phase 1: audio モジュール
1. `audio/furigana.py` - `MorphemeReading`
2. `audio/dictionary.py` - `DictionaryEntry`
3. `audio/voicevox.py` - `AudioMetadata`

### Phase 2: content モジュール
4. `content/parser.py` - `ContentMetadata`, `ImageInfo`, `ParsedContent`

### Phase 3: script モジュール
5. `script/phrases.py` - `Phrase`
6. `script/generator.py` - `Narration`, `ScriptSection`, `PronunciationEntry`, `VideoScript`

### Phase 4: video モジュール
7. `video/renderer.py` - `CompositionData`
8. `video/remotion_renderer.py` - `RemotionPhrase`

### Phase 5: 検証
9. 全テスト実行
10. mypy 型チェック

## Open Questions

- なし（純粋なリファクタリングのため）
