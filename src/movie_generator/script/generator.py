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
    source_image_url: str | None = None  # URL of image from source content to reuse


@dataclass
class PronunciationEntry:
    """Pronunciation dictionary entry."""

    word: str
    reading: str
    word_type: str = "COMMON_NOUN"  # PROPER_NOUN, COMMON_NOUN, VERB, ADJECTIVE, SUFFIX
    accent: int = 0  # 0=auto


@dataclass
class LogoAsset:
    """Product or company logo asset."""

    name: str
    url: str


@dataclass
class VideoScript:
    """Complete video script with multiple sections."""

    title: str
    description: str
    sections: list[ScriptSection]
    pronunciations: list[PronunciationEntry] | None = None
    logo_assets: list[LogoAsset] | None = None


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

【出力形式】
JSON形式で以下を出力してください：
{{
  "title": "動画タイトル",
  "description": "動画の説明",
  "logo_assets": [
    {{
      "name": "製品名またはサービス名",
      "url": "https://公式サイトの正確なロゴURL"
    }}
  ],
  "sections": [
    {{
      "title": "セクションタイトル",
      "narration": "ナレーション文",
      "slide_prompt": "このセクションのスライド画像生成用プロンプト（英語で記述、ただしスライド内の表示テキストは日本語で指定）"
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

【ロゴアセット（logo_assets）について】
- コンテンツ内で言及されている製品やサービスの公式ロゴURLを特定してください
- 製品・サービス・企業のロゴに限定し、スクリーンショットや図表は含めないでください
- 公式サイトから正確なロゴURLを推測してください（例: https://example.com/assets/logo.svg）
- ロゴが不要、またはURLを特定できない場合は空の配列を返してください
- 著作権的に問題のある画像は避け、公式に公開されているロゴのみを指定してください

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

[Output Format]
Output in JSON format:
{{
  "title": "Video Title",
  "description": "Video Description",
  "logo_assets": [
    {{
      "name": "Product or Service Name",
      "url": "https://official-site-exact-logo-url"
    }}
  ],
  "sections": [
    {{
      "title": "Section Title",
      "narration": "Narration text",
      "slide_prompt": "Slide image generation prompt for this section (write in English, but text to display on slide should be in English)"
    }}
  ],
  "pronunciations": []
}}

[About Logo Assets (logo_assets)]
- Identify official logo URLs for products or services mentioned in the content
- Limit to product/service/company logos only; exclude screenshots and diagrams
- Infer accurate logo URLs from official sites (e.g., https://example.com/assets/logo.svg)
- Return an empty array if no logos are needed or URLs cannot be determined
- Avoid copyrighted images; specify only officially published logos

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
    images: list | None = None,  # List of ImageInfo from parsed content
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
        images: List of ImageInfo objects from parsed content (optional).

    Returns:
        Generated video script.

    Raises:
        httpx.HTTPError: If API request fails.
        ValueError: If response parsing fails.
    """
    prompt_template = SCRIPT_GENERATION_PROMPTS.get(language, SCRIPT_GENERATION_PROMPT_JA)
    prompt = prompt_template.format(
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
