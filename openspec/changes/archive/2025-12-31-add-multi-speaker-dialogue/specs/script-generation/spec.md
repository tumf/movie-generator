# Script Generation - Delta Specification

## ADDED Requirements

### Requirement: 対話形式プロンプト

システムは、複数ペルソナによる対話形式の台本を生成できなければならない（SHALL）。

#### Scenario: 対話形式台本の生成
- **GIVEN** ペルソナ設定
  ```yaml
  personas:
    - id: "zundamon"
      character: "元気で明るい東北の妖精"
    - id: "metan"
      character: "優しくて落ち着いた四国の妖精"
  ```
- **AND** `narration.mode: "dialogue"`が設定されている
- **WHEN** `generate_script()`が呼び出される
- **THEN** LLMに対話形式プロンプトが送信される
- **AND** 各ペルソナの`character`設定が含まれる

#### Scenario: 対話形式レスポンスのパース
- **GIVEN** LLMから以下のレスポンスが返される
  ```json
  {
    "sections": [
      {
        "title": "イントロ",
        "dialogues": [
          {
            "persona_id": "zundamon",
            "narration": "やっほー！"
          },
          {
            "persona_id": "metan",
            "narration": "こんにちは！"
          }
        ],
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **WHEN** レスポンスがパースされる
- **THEN** 2つのフレーズが生成される
- **AND** フレーズ0は`persona_id="zundamon"`となる
- **AND** フレーズ1は`persona_id="metan"`となる

### Requirement: 単一話者モードの維持

システムは、従来の単一話者モードもサポートしなければならない（SHALL）。

#### Scenario: 単一話者台本の生成
- **GIVEN** `narration.mode: "single"`が設定されている
- **AND** ペルソナが1つのみ定義されている
- **WHEN** `generate_script()`が呼び出される
- **THEN** 従来の単一話者プロンプトが使用される
- **AND** すべてのフレーズが同じペルソナに割り当てられる

#### Scenario: 単一話者レスポンスのパース
- **GIVEN** LLMから従来形式のレスポンスが返される
  ```json
  {
    "sections": [
      {
        "title": "イントロ",
        "narration": "やっほー！ずんだもんなのだ。",
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **WHEN** レスポンスがパースされる
- **THEN** フレーズ分割が実行される
- **AND** すべてのフレーズが`personas[0].id`に割り当てられる

### Requirement: ペルソナ役割の自動割り当て

対話形式プロンプトは、ペルソナに適切な役割を割り当てなければならない（SHALL）。

#### Scenario: 2ペルソナの役割
- **GIVEN** 2つのペルソナが定義されている
- **WHEN** 対話形式プロンプトが生成される
- **THEN** ペルソナ0が「説明役」として指定される
- **AND** ペルソナ1が「質問・感想役」として指定される

#### Scenario: 3ペルソナ以上の役割
- **GIVEN** 3つ以上のペルソナが定義されている
- **WHEN** 対話形式プロンプトが生成される
- **THEN** 各ペルソナのキャラクター性に応じた役割が割り当てられる
- **AND** LLMに自然な会話を生成するよう指示される

### Requirement: フレーズへの話者情報追加

生成されたフレーズには、話者情報が含まれなければならない（SHALL）。

#### Scenario: Phraseオブジェクトへの話者情報追加
- **GIVEN** 対話形式レスポンスがパースされる
- **WHEN** `Phrase`オブジェクトが作成される
- **THEN** `persona_id`フィールドが設定される
- **AND** `persona_name`フィールドが設定される

#### Scenario: 不明なペルソナIDのエラー
- **GIVEN** LLMレスポンスに`persona_id="unknown"`が含まれている
- **AND** `unknown`というIDのペルソナが定義されていない
- **WHEN** レスポンスがパースされる
- **THEN** エラーが発生する
- **AND** エラーメッセージに不明なペルソナIDが表示される

### Requirement: 言語別対話プロンプト

システムは、日本語と英語の対話形式プロンプトを提供しなければならない（SHALL）。

#### Scenario: 日本語対話プロンプト
- **GIVEN** `language="ja"`が設定されている
- **AND** `narration.mode="dialogue"`が設定されている
- **WHEN** プロンプトが生成される
- **THEN** `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA`が使用される

#### Scenario: 英語対話プロンプト
- **GIVEN** `language="en"`が設定されている
- **AND** `narration.mode="dialogue"`が設定されている
- **WHEN** プロンプトが生成される
- **THEN** `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN`が使用される

## Data Models

### VideoScript (拡張)

```python
@dataclass
class VideoScript:
    """Complete video script with multiple sections."""

    title: str
    description: str
    sections: list[ScriptSection]
    pronunciations: list[PronunciationEntry] | None = None
    mode: str = "single"  # "single" or "dialogue"
```

### ScriptSection (拡張)

```python
@dataclass
class ScriptSection:
    """A section of the video script."""

    title: str
    narration: str | None = None  # 単一話者モード用
    dialogues: list[Dialogue] | None = None  # 対話モード用
    slide_prompt: str | None = None
    source_image_url: str | None = None
```

### Dialogue (新規)

```python
@dataclass
class Dialogue:
    """A single dialogue line in conversation mode."""

    persona_id: str
    narration: str
```

## API Reference

### generate_script (拡張)

```python
async def generate_script(
    content: str,
    personas: list[PersonaConfig],
    mode: str = "single",
    style: str = "casual",
    language: str = "ja",
    api_key: str | None = None,
    model: str = "openai/gpt-5.2",
    base_url: str = "https://openrouter.ai/api/v1",
    images: list[dict[str, str]] | None = None,
) -> VideoScript:
    """Generate video script from content using LLM.

    Args:
        personas: List of persona configurations.
        mode: "single" or "dialogue".
        ...
    """
```

## Prompt Templates

### SCRIPT_GENERATION_PROMPT_DIALOGUE_JA

対話形式の日本語プロンプトテンプレート。以下を含む：
- 各ペルソナのキャラクター説明
- 掛け合いのガイドライン（交互に話す、自然な会話）
- フレーズの長さ指定（1-3文程度）
- JSON出力形式の指定（dialogues配列）

### SCRIPT_GENERATION_PROMPT_DIALOGUE_EN

対話形式の英語プロンプトテンプレート。日本語版と同等の内容。
