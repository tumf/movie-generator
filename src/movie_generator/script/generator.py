"""LLM-based script generation for YouTube videos.

Generates video scripts from source content using LLM providers.
"""

from dataclasses import dataclass

import httpx


@dataclass
class ScriptSection:
    """A section of the video script."""

    title: str
    narration: str
    slide_prompt: str | None = None


@dataclass
class PronunciationEntry:
    """Pronunciation dictionary entry."""

    word: str
    reading: str
    word_type: str = "COMMON_NOUN"  # PROPER_NOUN, COMMON_NOUN, VERB, ADJECTIVE, SUFFIX
    accent: int = 0  # 0=auto


@dataclass
class VideoScript:
    """Complete video script with multiple sections."""

    title: str
    description: str
    sections: list[ScriptSection]
    pronunciations: list[PronunciationEntry] | None = None


SCRIPT_GENERATION_PROMPT = """
あなたはYouTube動画の台本作成の専門家です。
以下のコンテンツから、視聴者にわかりやすく説明するための動画台本を作成してください。

【要件】
- ナレーションは自然な話し言葉で、「{character}」のキャラクターで話してください
- スタイル: {style}
- 各セクションは3-6文程度で構成してください
- 専門用語は避けるか、わかりやすく説明してください
- 視覚的な説明を含めてください

【元コンテンツ】
タイトル: {title}
説明: {description}

{content}

【出力形式】
JSON形式で以下を出力してください：
{{
  "title": "動画タイトル",
  "description": "動画の説明",
  "sections": [
    {{
      "title": "セクションタイトル",
      "narration": "ナレーション文",
      "slide_prompt": "このセクションのスライド画像生成用プロンプト（英語）"
    }}
  ],
  "pronunciations": [
    {{
      "word": "ENGINE",
      "reading": "エンジン",
      "word_type": "COMMON_NOUN",
      "accent": 1
    }}
  ]
}}

【読み方辞書（pronunciations）について】
- ナレーション中に登場する英単語、固有名詞、専門用語で、音声合成エンジンが誤読する可能性のある単語をリストアップしてください
- 各単語について、正しいカタカナ読みを指定してください
- word_typeは以下から選択: PROPER_NOUN（固有名詞）, COMMON_NOUN（普通名詞）, VERB（動詞）, ADJECTIVE（形容詞）
- accentは0（自動）または1-N（アクセント位置）を指定
- 例: "API" → "エーピーアイ", "GitHub" → "ギットハブ", "Unity" → "ユニティ"
"""


async def generate_script(
    content: str,
    title: str | None = None,
    description: str | None = None,
    character: str = "ずんだもん",
    style: str = "casual",
    api_key: str | None = None,
    model: str = "openai/gpt-5.2",
    base_url: str = "https://openrouter.ai/api/v1",
) -> VideoScript:
    """Generate video script from content using LLM.

    Args:
        content: Source content (markdown or text).
        title: Content title.
        description: Content description.
        character: Character name for narration.
        style: Narration style (casual, formal, educational).
        api_key: OpenRouter API key.
        model: Model identifier.
        base_url: API base URL.

    Returns:
        Generated video script.

    Raises:
        httpx.HTTPError: If API request fails.
        ValueError: If response parsing fails.
    """
    prompt = SCRIPT_GENERATION_PROMPT.format(
        character=character,
        style=style,
        title=title or "Unknown",
        description=description or "",
        content=content,
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    # Parse response
    import json

    message_content = data["choices"][0]["message"]["content"]
    script_data = json.loads(message_content)

    sections = [
        ScriptSection(
            title=section["title"],
            narration=section["narration"],
            slide_prompt=section.get("slide_prompt"),
        )
        for section in script_data["sections"]
    ]

    # Parse pronunciations if provided
    pronunciations = None
    if "pronunciations" in script_data and script_data["pronunciations"]:
        pronunciations = [
            PronunciationEntry(
                word=entry["word"],
                reading=entry["reading"],
                word_type=entry.get("word_type", "COMMON_NOUN"),
                accent=entry.get("accent", 0),
            )
            for entry in script_data["pronunciations"]
        ]

    return VideoScript(
        title=script_data["title"],
        description=script_data["description"],
        sections=sections,
        pronunciations=pronunciations,
    )
