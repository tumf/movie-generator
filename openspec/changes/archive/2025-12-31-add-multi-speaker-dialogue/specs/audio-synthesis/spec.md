# Audio Synthesis - Delta Specification

## ADDED Requirements

### Requirement: 音声合成エンジンの抽象化

システムは、複数の音声合成エンジンに対応できる抽象化インターフェースを提供しなければならない（SHALL）。

#### Scenario: VOICEVOX音声合成
- **GIVEN** ペルソナの`synthesizer.engine`が`"voicevox"`である
- **WHEN** フレーズの音声合成が要求される
- **THEN** VOICEVOXエンジンを使用して音声が生成される
- **AND** `speaker_id`と`speed_scale`が適用される

#### Scenario: サポートされていないエンジン
- **GIVEN** ペルソナの`synthesizer.engine`が未対応のエンジン（例: `"coefont"`）である
- **WHEN** 音声合成が初期化される
- **THEN** エラーが発生する
- **AND** エラーメッセージに「サポートされていないエンジン」と表示される

#### Scenario: エンジン固有パラメータ
- **GIVEN** ペルソナの`synthesizer`に任意のパラメータが含まれている
- **WHEN** 対応するエンジンが実装されている
- **THEN** そのパラメータが音声合成に適用される

### Requirement: ペルソナごとの音声合成

システムは、各フレーズに割り当てられたペルソナに応じて音声を合成しなければならない（SHALL）。

#### Scenario: 複数ペルソナの音声合成
- **GIVEN** フレーズリスト
  ```
  Phrase(text="やっほー！", persona_id="zundamon")
  Phrase(text="こんにちは", persona_id="metan")
  ```
- **AND** ペルソナ設定
  ```yaml
  personas:
    - id: "zundamon"
      synthesizer: {engine: "voicevox", speaker_id: 3}
    - id: "metan"
      synthesizer: {engine: "voicevox", speaker_id: 2}
  ```
- **WHEN** `synthesize_phrases()`が呼び出される
- **THEN** フレーズ0はspeaker_id=3で合成される
- **AND** フレーズ1はspeaker_id=2で合成される

#### Scenario: 不明なペルソナIDのエラー
- **GIVEN** フレーズに`persona_id="unknown"`が設定されている
- **AND** `unknown`というIDのペルソナが定義されていない
- **WHEN** 音声合成が実行される
- **THEN** エラーが発生する
- **AND** エラーメッセージに不明なペルソナIDが表示される

### Requirement: ペルソナごとの発音辞書

各ペルソナは、独立した発音辞書を持つことができなければならない（SHALL support、ただし現バージョンではオプション）。

#### Scenario: ペルソナ共通の発音辞書
- **GIVEN** グローバル発音辞書に`"ENGINE" -> "エンジン"`が登録されている
- **WHEN** 任意のペルソナで音声合成が実行される
- **THEN** すべてのペルソナでこの辞書が使用される

#### Scenario: ペルソナ固有の発音辞書（将来拡張）
- **GIVEN** ペルソナAに`"東京" -> "トーキョー"`が登録されている
- **AND** ペルソナBに`"東京" -> "とうきょう"`が登録されている
- **WHEN** 各ペルソナで音声合成が実行される
- **THEN** ペルソナごとに異なる読みが適用される

### Requirement: 音声ファイルの命名規則

生成された音声ファイルは、フレーズの`original_index`を使用して命名されなければならない（SHALL）。

#### Scenario: 音声ファイル名
- **GIVEN** フレーズの`original_index`が5である
- **WHEN** 音声合成が実行される
- **THEN** ファイル名は`phrase_0005.wav`となる
- **AND** ペルソナIDは含まれない（original_indexで一意）

### Requirement: 音声合成のキャッシュ

既存の音声ファイルがある場合、再合成をスキップしなければならない（SHALL）。

#### Scenario: 既存音声のスキップ
- **GIVEN** `phrase_0000.wav`が既に存在する
- **AND** ファイルサイズが0バイトより大きい
- **WHEN** `synthesize_phrases()`が呼び出される
- **THEN** そのフレーズの音声合成はスキップされる
- **AND** "Skipping existing audio"メッセージが表示される

#### Scenario: 破損ファイルの再生成
- **GIVEN** `phrase_0000.wav`が存在するがサイズが0バイトである
- **WHEN** `synthesize_phrases()`が呼び出される
- **THEN** 音声が再生成される

## API Reference

### SynthesizerFactory

```python
class SynthesizerFactory:
    """音声合成エンジンのファクトリ."""

    @staticmethod
    def create(persona_config: PersonaConfig) -> AudioSynthesizer:
        """ペルソナ設定から適切なSynthesizerインスタンスを生成."""
```

### AudioSynthesizer (抽象基底クラス)

```python
class AudioSynthesizer(ABC):
    """音声合成エンジンの抽象基底クラス."""

    @abstractmethod
    def initialize(self, ...) -> None:
        """エンジンを初期化."""

    @abstractmethod
    def synthesize_phrase(
        self,
        phrase: Phrase,
        output_path: Path
    ) -> AudioMetadata:
        """1フレーズを音声合成."""
```

### VoicevoxSynthesizer (実装クラス)

```python
class VoicevoxSynthesizer(AudioSynthesizer):
    """VOICEVOX音声合成エンジンの実装."""

    def __init__(
        self,
        speaker_id: int = 3,
        speed_scale: float = 1.0,
        dictionary: PronunciationDictionary | None = None,
        enable_furigana: bool = True,
    ):
        """初期化."""

    def initialize(
        self,
        dict_dir: Path,
        model_path: Path,
        onnxruntime_path: Path | None = None,
    ) -> None:
        """VOICEVOX Coreを初期化."""
```

## Dependencies

- `voicevox_core` (optional): VOICEVOX音声合成
- 将来的に他エンジンのライブラリを追加可能
