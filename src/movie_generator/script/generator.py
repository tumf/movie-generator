"""LLM-based script generation for YouTube videos.

Generates video scripts from source content using LLM providers.
"""

import httpx
from pydantic import BaseModel

from ..utils.text import clean_katakana_reading  # type: ignore[import]


class Narration(BaseModel):
    """A single narration line, optionally with persona information."""

    text: str
    reading: str  # Katakana pronunciation for audio synthesis
    persona_id: str | None = None  # None for single-speaker mode


class ScriptSection(BaseModel):
    """A section of the video script."""

    title: str
    narrations: list[Narration]  # Unified format: always a list
    slide_prompt: str | None = None
    source_image_url: str | None = None


class PronunciationEntry(BaseModel):
    """Pronunciation dictionary entry."""

    word: str
    reading: str
    word_type: str = "COMMON_NOUN"  # PROPER_NOUN, COMMON_NOUN, VERB, ADJECTIVE, SUFFIX
    accent: int = 0  # 0=auto


class RoleAssignment(BaseModel):
    """Role assignment for a persona in the video script."""

    persona_id: str
    role: str
    description: str


class VideoScript(BaseModel):
    """Complete video script with multiple sections."""

    title: str
    description: str
    sections: list[ScriptSection]
    pronunciations: list[PronunciationEntry] | None = None
    role_assignments: list[RoleAssignment] | None = None


SCRIPT_GENERATION_PROMPT_JA = """
あなたはYouTube動画の台本作成の専門家です。
以下のコンテンツから、視聴者にわかりやすく説明するための動画台本を作成してください。

【要件】
- ナレーションは自然な話し言葉で、「{character}」のキャラクターで話してください
- スタイル: {style}
- 各セクションは3-6文程度で構成してください
- **重要**: 各ナレーションは40文字程度を目安に分割してください。句読点（。、！？）で区切り、長い文は自然な位置で分けてください
- 専門用語は避けるか、わかりやすく説明してください
- 視覚的な説明を含めてください
- **重要**: slide_promptは英語で記述しますが、スライドに表示するテキストは日本語で指定してください
  - 例: "A slide with text 'データベース設計' in the center, modern design"

【台本構成の必須ルール】
- 論理的な構成で最後まで完成させてください
- 最低6セクション以上を目安に構成してください
- 最後のセクションは必ず「まとめ」「結論」「次のステップ」のいずれかを含めてください
- 途中で終わらせず、視聴者に結論を伝えてください

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
      "narrations": [
        {{
          "text": "ナレーション文",
          "reading": "ナレーションブン"
        }}
      ],
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

【reading フィールドについて】
- **必須フィールド**: 各ナレーションには必ず reading フィールドを含めてください
- **カタカナ形式**: すべてカタカナで記述してください（ひらがな不可）
- **助詞の発音**: 助詞は発音通りに変換してください
  - 「は」→「ワ」（例: 「これは」→「コレワ」）
  - 「へ」→「エ」（例: 「東京へ」→「トウキョウエ」）
  - 「を」→「オ」（例: 「本を」→「ホンオ」）
- **スペース不要**: カタカナにスペースを含めないでください
- **例**:
  - text: "明日は晴れです" → reading: "アシタワハレデス"
  - text: "道案内図を見る" → reading: "ミチアンナイズオミル"
  - text: "97個あります" → reading: "キュウジュウナナコアリマス"

【スライド画像について】
- 各セクションには、source_image_urlまたはslide_promptのどちらか一方を指定してください
- source_image_url: 元記事の画像リストから適切な画像を選択する場合に使用
- slide_prompt: AI生成する場合に使用
- 元記事に適切な図解やスクリーンショットがある場合は、source_image_urlを優先してください

【読み方辞書（pronunciations）について】
- ナレーション中に登場する英単語、固有名詞、専門用語で、音声合成エンジンが誤読する可能性のある単語をリストアップしてください
- **数字は登録しないでください**（音声合成エンジンが正しく読めます）
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
- **IMPORTANT**: Split each narration into approximately 40 characters. Use punctuation (. , ! ?) as natural break points
- Avoid or clearly explain technical terms
- Include visual descriptions
- **IMPORTANT**: Write slide_prompt in English, but specify text to display on slides in English
  - Example: "A slide with text 'Database Design' in the center, modern design"

[Script Structure Rules - MANDATORY]
- **Complete the script with a logical structure**
- Create at least 6 sections minimum
- The final section MUST include "Summary", "Conclusion", or "Next Steps"
- Do NOT end the script abruptly. Always provide viewers with a conclusion

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
      "narrations": [
        {{
          "text": "Narration text",
          "reading": "Narration text"
        }}
      ],
      "slide_prompt": "Slide image generation prompt for this section (write in English, but text to display on slide should be in English)",
      "source_image_url": "Source image URL from blog content (if applicable, select from image list)"
    }}
  ],
  "pronunciations": []
}}

[Reading Field]
- **Required field**: Each narration must include a reading field
- For English narration, simply copy the text field to reading field (no special pronunciation rules)
- Example: text: "Hello world" → reading: "Hello world"

[About Slide Images]
- For each section, specify either source_image_url OR slide_prompt (not both)
- source_image_url: Use when selecting an appropriate image from the blog's image list
- slide_prompt: Use when generating a new slide with AI
- Prefer source_image_url if the blog contains suitable diagrams or screenshots

Note: For English narration, pronunciations dictionary is not needed, so return an empty array.
"""

SCRIPT_GENERATION_PROMPT_DIALOGUE_JA = """
あなたはYouTube動画の台本作成の専門家です。
以下のコンテンツから、複数のキャラクターが掛け合いで説明する動画台本を作成してください。

【登場キャラクター】
{personas_description}

【役割割り当て】
このスクリプトでは、各キャラクターに明確な役割を割り当ててください。
役割は対話の一貫性と視聴者の理解を助けるために重要です。
各キャラクターの役割（例: 解説役、質問役、ツッコミ役など）を自由に設定してください。

【要件】
- 各キャラクターの個性を活かした自然な会話形式で台本を作成してください
- スタイル: {style}
- 各セクションは5-10ターン程度の対話で構成してください
- **重要**: 各セリフは40文字程度を目安に分割してください。句読点（。、！？）で区切り、長い文は自然な位置で分けてください
- 専門用語は避けるか、わかりやすく説明してください
- 視覚的な説明を含めてください
- **重要**: slide_promptは英語で記述しますが、スライドに表示するテキストは日本語で指定してください
  - 例: "A slide with text 'データベース設計' in the center, modern design"

【台本構成の必須ルール】
- 論理的な構成で最後まで完成させてください
- 最低6セクション以上を目安に構成してください
- 最後のセクションは必ず「まとめ」「結論」「次のステップ」のいずれかを含めてください
- 途中で終わらせず、視聴者に結論を伝えてください

【元コンテンツ】
タイトル: {title}
説明: {description}

{content}

{images_section}

【重要：reading フィールドについて】
各ナレーションには必ず reading フィールドを含めてください。これは音声合成で正しい発音を実現するために必須です。

- **必須フィールド**: 各セリフには必ず reading フィールドを含める
- **カタカナ形式**: すべてカタカナで記述（ひらがな不可）
- **助詞の発音**: 助詞は発音通りに変換
  - 「は」→「ワ」（例: 「これは」→「コレワ」）
  - 「へ」→「エ」（例: 「東京へ」→「トウキョウエ」）
  - 「を」→「オ」（例: 「本を」→「ホンオ」）
- **スペース不要**: カタカナにスペースを含めない
- **例**:
  - text: "ねえねえ！" → reading: "ネエネエ！"
  - text: "これは便利だね" → reading: "コレワベンリダネ"
  - text: "東京へ行こう" → reading: "トウキョウエイコウ"
  - text: "RAGって何？" → reading: "ラグッテナニ？"
  - text: "97%削減！" → reading: "キュウジュウナナパーセントサクゲン！"

【出力形式】
JSON形式で以下を出力してください。**必ず各ナレーションに reading フィールドを含めること**：
{{
  "title": "動画タイトル",
  "description": "動画の説明",
  "role_assignments": [
    {{
      "persona_id": "キャラクターID（例: zundamon, metan）",
      "role": "役割（例: 解説役、質問役）",
      "description": "役割の詳細説明"
    }}
  ],
  "sections": [
    {{
      "title": "セクションタイトル",
      "narrations": [
        {{
          "persona_id": "キャラクターID（例: zundamon, metan）",
          "text": "セリフ",
          "reading": "セリフのカタカナ読み（必須）"
        }}
      ],
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
- **数字は登録しないでください**（音声合成エンジンが正しく読めます）
- 各単語について、正しいカタカナ読みを指定してください
- **重要**: カタカナ読みにはスペースを含めないでください（例: "カイジュウエンジン" ○、"カイジュウ エンジン" ×）
- word_typeは以下から選択: PROPER_NOUN（固有名詞）, COMMON_NOUN（普通名詞）, VERB（動詞）, ADJECTIVE（形容詞）
- accentは0（自動）または1-N（アクセント位置）を指定
- 例: "API" → "エーピーアイ", "GitHub" → "ギットハブ", "Unity" → "ユニティ", "Kaiju Engine" → "カイジュウエンジン"
"""

SCRIPT_GENERATION_PROMPT_DIALOGUE_EN = """
You are an expert YouTube video script writer.
Create a video script with multiple characters having a dialogue-style conversation to explain the content.

[Characters]
{personas_description}

[Role Assignments]
In this script, assign clear roles to each character.
Roles are important for dialogue consistency and viewer understanding.
Define each character's role freely (e.g., explainer, questioner, commentator, etc.).

[Requirements]
- Create natural dialogue that leverages each character's personality
- Style: {style}
- Each section should have 5-10 dialogue turns
- **IMPORTANT**: Split each dialogue line into approximately 40 characters. Use punctuation (. , ! ?) as natural break points
- Avoid or clearly explain technical terms
- Include visual descriptions
- **IMPORTANT**: Write slide_prompt in English, and specify text to display on slides in English
  - Example: "A slide with text 'Database Design' in the center, modern design"

[Script Structure Rules - MANDATORY]
- **Complete the script with a logical structure**
- Create at least 6 sections minimum
- The final section MUST include "Summary", "Conclusion", or "Next Steps"
- Do NOT end the script abruptly. Always provide viewers with a conclusion

[Source Content]
Title: {title}
Description: {description}

{content}

{images_section}

[IMPORTANT: About Reading Field]
Each narration MUST include a reading field. This is essential for accurate audio synthesis.

- **Required field**: Every dialogue line must have a reading field
- **Katakana format**: Write in katakana (not hiragana or romaji)
- **Particle pronunciation**: Convert particles to their spoken form:
  - "は" → "ワ" (e.g., "これは" → "コレワ")
  - "へ" → "エ" (e.g., "東京へ" → "トウキョウエ")
  - "を" → "オ" (e.g., "本を" → "ホンオ")
- **No spaces**: Do not include spaces in katakana
- **Examples**:
  - text: "Hello there!" → reading: "ハローゼアー！"
  - text: "Let's go to Tokyo" → reading: "レッツゴートゥートウキョウ"
  - text: "What is RAG?" → reading: "ホワットイズラグ？"
  - text: "97% reduction!" → reading: "ナインティセブンパーセントリダクション！"

[Output Format]
Output in JSON format. **MUST include reading field for each narration**:
{{
  "title": "Video Title",
  "description": "Video Description",
  "role_assignments": [
    {{
      "persona_id": "Character ID (e.g., zundamon, metan)",
      "role": "Role (e.g., explainer, questioner)",
      "description": "Detailed role description"
    }}
  ],
  "sections": [
    {{
      "title": "Section Title",
      "narrations": [
        {{
          "persona_id": "Character ID (e.g., zundamon, metan)",
          "text": "Dialogue line",
          "reading": "Katakana reading (REQUIRED)"
        }}
      ],
      "slide_prompt": "Slide image generation prompt for this section (write in English, text on slide should be in English)",
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

SCRIPT_GENERATION_PROMPTS_DIALOGUE = {
    "ja": SCRIPT_GENERATION_PROMPT_DIALOGUE_JA,
    "en": SCRIPT_GENERATION_PROMPT_DIALOGUE_EN,
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
    personas: list[dict[str, str]] | None = None,
) -> VideoScript:
    """Generate video script from content using LLM.

    Args:
        content: Source content (markdown or text).
        title: Content title.
        description: Content description.
        character: Character name for narration (used when no personas defined).
        style: Narration style (casual, formal, educational).
        language: Language code for script generation (ja, en).
        api_key: OpenRouter API key.
        model: Model identifier.
        base_url: API base URL.
        images: List of image metadata dicts with 'src', 'alt', 'title' keys.
        personas: List of persona dicts with 'id', 'name', 'character' keys.
                  If provided, multi-speaker dialogue mode is used.

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

    # Select prompt template based on personas presence
    if personas:
        prompt_template = SCRIPT_GENERATION_PROMPTS_DIALOGUE.get(
            language, SCRIPT_GENERATION_PROMPT_DIALOGUE_JA
        )
        # Format personas description
        personas_description = ""
        if personas:
            for persona in personas:
                personas_description += (
                    f"- {persona['name']} (ID: {persona['id']}): {persona.get('character', '')}\n"
                )
        prompt = prompt_template.format(
            personas_description=personas_description,
            style=style,
            title=title or "Unknown",
            description=description or "",
            content=content,
            images_section=images_section,
        )
        # Add critical reminder at the end
        prompt += "\n\n**CRITICAL REMINDER**: Ensure EVERY narration has both 'text' and 'reading' fields. Do not skip the 'reading' field for any narration."
    else:
        prompt_template = SCRIPT_GENERATION_PROMPTS.get(language, SCRIPT_GENERATION_PROMPT_JA)
        prompt = prompt_template.format(
            character=character,
            style=style,
            title=title or "Unknown",
            description=description or "",
            content=content,
            images_section=images_section,
        )
        # Add critical reminder at the end
        prompt += "\n\n**CRITICAL REMINDER**: Ensure EVERY narration has both 'text' and 'reading' fields. Do not skip the 'reading' field for any narration."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # System prompt to enforce reading field generation
    system_prompt = (
        "You are a script generator for video narration. "
        "CRITICAL REQUIREMENT: Every single narration MUST include a 'reading' field in katakana. "
        "This is not optional. Missing 'reading' field will cause system failure. "
        "Always generate both 'text' and 'reading' for each narration."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 16000,  # Ensure sufficient output for complete scripts
    }

    async with httpx.AsyncClient(timeout=180.0) as client:  # Extended for long articles
        url = f"{base_url}/chat/completions"
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            error_detail = response.text[:500] if response.text else "No response body"
            raise RuntimeError(
                f"LLM API request failed: {response.status_code} for {url}\n"
                f"Model: {model}\n"
                f"Response: {error_detail}"
            )
        data = response.json()

    # Parse response
    import json

    message_content = data["choices"][0]["message"]["content"]
    script_data = json.loads(message_content)

    # Parse sections - unified format with narrations list
    sections = []
    for section in script_data["sections"]:
        narrations: list[Narration] = []

        if "narrations" in section and section["narrations"]:
            # New unified format
            for n in section["narrations"]:
                if isinstance(n, str):
                    # Simple string format (single speaker) - legacy, use text as reading
                    narrations.append(Narration(text=n, reading=n))
                else:
                    # Object format with required reading field
                    if "reading" not in n or not n["reading"]:
                        raise ValueError(
                            f"Missing or empty 'reading' field in narration: {n.get('text', 'N/A')[:50]}...\n"
                            f"The LLM did not generate the required 'reading' field. "
                            f"This is a critical error in script generation."
                        )
                    narrations.append(
                        Narration(
                            text=n["text"], reading=n["reading"], persona_id=n.get("persona_id")
                        )
                    )
        elif "dialogues" in section and section["dialogues"]:
            # Legacy dialogue format (backward compatibility)
            for d in section["dialogues"]:
                if "reading" not in d or not d["reading"]:
                    raise ValueError(
                        f"Missing or empty 'reading' field in dialogue: {d.get('narration', 'N/A')[:50]}...\n"
                        f"The LLM did not generate the required 'reading' field."
                    )
                narrations.append(
                    Narration(text=d["narration"], reading=d["reading"], persona_id=d["persona_id"])
                )
        elif "narration" in section:
            # Legacy single narration format (backward compatibility)
            narrations.append(Narration(text=section["narration"], reading=section["narration"]))

        sections.append(
            ScriptSection(
                title=section["title"],
                narrations=narrations,
                slide_prompt=section.get("slide_prompt"),
                source_image_url=section.get("source_image_url"),
            )
        )

    # Parse pronunciations if provided
    pronunciations = None
    if "pronunciations" in script_data and script_data["pronunciations"]:
        pronunciations = [
            PronunciationEntry(
                word=entry["word"],
                # Remove spaces from reading (VOICEVOX requires katakana-only)
                reading=clean_katakana_reading(entry["reading"]),
                word_type=entry.get("word_type", "COMMON_NOUN"),
                accent=entry.get("accent", 0),
            )
            for entry in script_data["pronunciations"]
        ]

    # Parse role_assignments if provided (for backward compatibility)
    role_assignments = None
    if "role_assignments" in script_data and script_data["role_assignments"]:
        role_assignments = [
            RoleAssignment(
                persona_id=entry["persona_id"],
                role=entry["role"],
                description=entry["description"],
            )
            for entry in script_data["role_assignments"]
        ]

    # Validate script completeness
    if not sections:
        raise ValueError("Script generation failed: no sections were generated")
    if not sections[-1].narrations:
        raise ValueError(
            f"Script generation incomplete: last section '{sections[-1].title}' has no narrations. "
            "The LLM response may have been truncated. Try regenerating the script."
        )

    return VideoScript(
        title=script_data["title"],
        description=script_data["description"],
        sections=sections,
        pronunciations=pronunciations,
        role_assignments=role_assignments,
    )
