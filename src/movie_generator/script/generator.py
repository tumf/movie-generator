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
    source_image_url: str | None = None


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


SCRIPT_GENERATION_PROMPT_JA = """
あなたはYouTube動画の台本作成の専門家です。
以下のコンテンツから、視聴者にわかりやすく説明するための動画台本を作成してください。

【要件】
- ナレーションは自然な話し言葉で、「{character}」のキャラクターで話してください
- スタイル: {style}
- 各セクションは3-6文程度で構成してください
- 専門用語は避けるか、わかりやすく説明してください
- 視覚的な説明を含めてください
- **重要**: slide_promptは英語で記述しますが、スライドに表示するテキストは日本語で指定してください
  - 例: "A slide with text 'データベース設計' in the center, modern design"

【元コンテンツ】
タイトル: {title}
説明: {description}

{content}

{images_section}

【出力形式】
JSON形式で以下を出力してください：
{{
  "title": "動画タイトル",
  "description": "動画の説明",
  "sections": [
    {{
      "title": "セクションタイトル",
      "narration": "ナレーション文",
      "slide_prompt": "このセクションのスライド画像生成用プロンプト（英語で記述、ただしスライド内の表示テキストは日本語で指定）",
      "source_image_url": "元記事の画像URL（該当する場合のみ。画像リストから選択）"
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

【スライド画像について】
- 各セクションには、source_image_urlまたはslide_promptのどちらか一方を指定してください
- source_image_url: 元記事の画像リストから適切な画像を選択する場合に使用
- slide_prompt: AI生成する場合に使用
- 元記事に適切な図解やスクリーンショットがある場合は、source_image_urlを優先してください

【読み方辞書（pronunciations）について】
- ナレーション中に登場する英単語、固有名詞、専門用語で、音声合成エンジンが誤読する可能性のある単語をリストアップしてください
- 各単語について、正しいカタカナ読みを指定してください
- **重要**: カタカナ読みにはスペースを含めないでください（例: "カイジュウエンジン" ○、"カイジュウ エンジン" ×）
- word_typeは以下から選択: PROPER_NOUN（固有名詞）, COMMON_NOUN（普通名詞）, VERB（動詞）, ADJECTIVE（形容詞）
- accentは0（自動）または1-N（アクセント位置）を指定
- 例: "API" → "エーピーアイ", "GitHub" → "ギットハブ", "Unity" → "ユニティ", "Kaiju Engine" → "カイジュウエンジン"
"""

SCRIPT_GENERATION_PROMPT_EN = """
You are an expert YouTube video script writer.
Create a video script from the following content that explains clearly to viewers.

[Requirements]
- Write narration in natural spoken language with the character of "{character}"
- Style: {style}
- Each section should be 3-6 sentences
- Avoid or clearly explain technical terms
- Include visual descriptions
- **IMPORTANT**: Write slide_prompt in English, but specify text to display on slides in English
  - Example: "A slide with text 'Database Design' in the center, modern design"

[Source Content]
Title: {title}
Description: {description}

{content}

{images_section}

[Output Format]
Output in JSON format:
{{
  "title": "Video Title",
  "description": "Video Description",
  "sections": [
    {{
      "title": "Section Title",
      "narration": "Narration text",
      "slide_prompt": "Slide image generation prompt for this section (write in English, but text to display on slide should be in English)",
      "source_image_url": "Source image URL from blog content (if applicable, select from image list)"
    }}
  ],
  "pronunciations": []
}}

[About Slide Images]
- For each section, specify either source_image_url OR slide_prompt (not both)
- source_image_url: Use when selecting an appropriate image from the blog's image list
- slide_prompt: Use when generating a new slide with AI
- Prefer source_image_url if the blog contains suitable diagrams or screenshots

Note: For English narration, pronunciations dictionary is not needed, so return an empty array.
"""

SCRIPT_GENERATION_PROMPTS = {
    "ja": SCRIPT_GENERATION_PROMPT_JA,
    "en": SCRIPT_GENERATION_PROMPT_EN,
}


async def generate_script(
    content: str,
    title: str | None = None,
    description: str | None = None,
    character: str = "ずんだもん",
    style: str = "casual",
    language: str = "ja",
    api_key: str | None = None,
    model: str = "openai/gpt-5.2",
    base_url: str = "https://openrouter.ai/api/v1",
    images: list[dict[str, str]] | None = None,
) -> VideoScript:
    """Generate video script from content using LLM.

    Args:
        content: Source content (markdown or text).
        title: Content title.
        description: Content description.
        character: Character name for narration.
        style: Narration style (casual, formal, educational).
        language: Language code for script generation (ja, en).
        api_key: OpenRouter API key.
        model: Model identifier.
        base_url: API base URL.
        images: List of image metadata dicts with 'src', 'alt', 'title' keys.

    Returns:
        Generated video script.

    Raises:
        httpx.HTTPError: If API request fails.
        ValueError: If response parsing fails.
    """
    # Format images section for prompt
    images_section = ""
    if images:
        if language == "ja":
            images_section = "【利用可能な画像】\n以下の画像がブログ記事内で利用可能です。適切なセクションに割り当ててください：\n"
        else:
            images_section = "[Available Images]\nThe following images are available from the blog content. Assign them to appropriate sections:\n"

        for idx, img in enumerate(images, 1):
            alt_text = img.get("alt", "")
            title_text = img.get("title", "")
            aria_text = img.get("aria_describedby", "")
            description_parts = []
            if alt_text:
                description_parts.append(f"Alt: {alt_text}")
            if title_text:
                description_parts.append(f"Title: {title_text}")
            if aria_text:
                description_parts.append(f"Description: {aria_text}")
            description = ", ".join(description_parts) if description_parts else "No description"

            images_section += f"{idx}. URL: {img['src']}\n   {description}\n"

    prompt_template = SCRIPT_GENERATION_PROMPTS.get(language, SCRIPT_GENERATION_PROMPT_JA)
    prompt = prompt_template.format(
        character=character,
        style=style,
        title=title or "Unknown",
        description=description or "",
        content=content,
        images_section=images_section,
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
            source_image_url=section.get("source_image_url"),
        )
        for section in script_data["sections"]
    ]

    # Parse pronunciations if provided
    pronunciations = None
    if "pronunciations" in script_data and script_data["pronunciations"]:
        pronunciations = [
            PronunciationEntry(
                word=entry["word"],
                # Remove spaces from reading (VOICEVOX requires katakana-only)
                reading=entry["reading"].replace(" ", "").replace("　", ""),
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
