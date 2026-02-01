"""LLM-based script generation for YouTube videos.

Generates video scripts from source content using LLM providers.
"""

import random
from typing import Any

import httpx
from pydantic import BaseModel

from ..constants import TimeoutConstants
from .phrases import split_into_phrases


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
    background: dict[str, Any] | None = None  # Optional section-level background override


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
    role_assignments: list[RoleAssignment] | None = None


SCRIPT_GENERATION_PROMPT_JA = """
あなたはYouTube動画の台本作成の専門家です。
以下のコンテンツから、視聴者を引き込み、深く理解させる動画台本を作成してください。

【基本要件】
- ナレーションは自然な話し言葉で、「{character}」のキャラクターで話してください
- スタイル: {style}
- 各セクションは3-6文程度で構成してください
- **重要**: 各ナレーションは40文字程度を目安に分割してください。句読点（。、！？）で区切り、長い文は自然な位置で分けてください
- 専門用語は避けるか、わかりやすく説明してください
- 視覚的な説明を含めてください
- **重要**: slide_promptは英語で記述しますが、スライドに表示するテキストは日本語で指定してください
  - 例: "A slide with text 'データベース設計' in the center, modern design"

【ストーリーテリング構造 - 起承転結を意識】
台本は以下の流れで構成してください：

**1. Hook（掴み）- 最初の15秒が勝負**
- 驚きの事実、問題提起、視聴者の「知りたい！」を引き出す一言から始める
- 例: 「実は○○の97%が知らない事実があるんです」「なぜ△△が失敗するのか、その理由は...」
- このセクションで視聴者の離脱を防ぐ

**2. Context（背景・なぜ重要か）- 動機付け**
- なぜこのトピックが視聴者にとって重要なのかを説明
- 「こんな悩みありませんか？」「実はこれ、皆さんの○○に直結します」
- 視聴者が「自分ごと」として捉えられるよう工夫する

**3. Core Content（本編）- 3〜5のメインポイント**
- 各ポイントは論理的につながるよう構成（原因→結果、問題→解決策など）
- セクション間の接続を意識し、「では次に...」「これに関連して...」などのつなぎ言葉を使う
- 抽象的な説明だけでなく、**必ず具体例・比喩・実例**を含める
  - 悪い例: 「効率が上がります」
  - 良い例: 「例えば、従来1時間かかった作業が10分で終わります」

**4. Conclusion（まとめ・次のアクション）**
- 要点を3つ以内で再確認
- 視聴者が次に何をすべきか明確にする（「まずは○○から始めてみましょう」）

【内容理解の深化 - 視聴者視点を最優先】
- **初めて聞く人が疑問に思うこと**を先回りして答える
  - 「○○って何？」「なぜそうなるの？」「自分には関係ある？」
- **段階的な説明**: 概要→詳細→応用の順で説明
  - まず全体像を示してから、細かい話に入る
- **具体例必須**: 抽象的な概念には必ず身近な例や比喩を添える
  - 例: 「データベースは図書館のようなもの。本を整理して、必要な時にすぐ取り出せるようにします」

【台本構成の必須ルール】
- 論理的な構成で最後まで完成させてください
- 最低6セクション以上を目安に構成してください
  - Hook（1セクション）
  - Context（1セクション）
  - Core Content（3〜5セクション）
  - Conclusion（1セクション）
- 最後のセクションは必ず「まとめ」「結論」「次のステップ」のいずれかを含めてください
- 途中で終わらせず、視聴者に結論を伝えてください

【自己評価チェックリスト】
台本作成後、以下を自己確認してください：
✓ 最初の15秒で視聴者の興味を引けるか？
✓ 専門知識ゼロの人でも理解できるか？
✓ 各セクションが論理的につながっているか？
✓ 抽象的な説明に具体例が添えられているか？
✓ 視聴者が「見てよかった」と思える結論があるか？
✓ すべてのreadingフィールドで促音が正しく使われているか？（「ツッテ」×、「ッテ」○）
✓ 助詞の発音ルールが適用されているか？（は→ワ、へ→エ）

【元コンテンツ】
タイトル: {title}
説明: {description}

{content}

{images_section}

【CRITICAL REQUIREMENT - 最重要】
reading フィールドの品質はシステムの成否を左右します。以下を必ず守ってください：
1. 促音（小さい「ッ」）を正確に使用
2. 助詞の発音ルールを適用（は→ワ、へ→エ）
3. アルファベット略語の音引きルール適用

これらのルールを破ると、音声合成が失敗します。

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
  ]
}}

【reading フィールドについて - CRITICAL】
- **必須フィールド**: 各ナレーションには必ず reading フィールドを含めてください
- **カタカナ形式**: すべてカタカナで記述してください（ひらがな不可）

**助詞の発音ルール**:
  - 「は」→「ワ」（例: 「これは」→「コレワ」）
  - 「へ」→「エ」（例: 「東京へ」→「トウキョウエ」）

**アルファベット略語の音引き**:
英字1文字ごとにカタカナで表記し、最後に長音「ー」を付けます
  - 「ESP」→「イーエスピー」（×イーエスピージ）
  - 「API」→「エーピーアイ」
  - 「CPU」→「シーピーユー」
  - 「USB」→「ユーエスビー」

**促音の表記（CRITICAL - 最重要）**:
小さい「ッ」を正しく使用してください。「ツッテ」は誤りです。
  ✅ 正しい例:
    - 「って」→「ッテ」
      - 「聞いたって」→「キイタッテ」
      - 「APIって何？」→「エーピーアイッテナニ？」
      - 「Web3って難しい」→「ウェブスリーッテムズカシイ」
    - 「った」→「ッタ」
      - 「言った」→「イッタ」
      - 「使った」→「ツカッタ」
    - 「っぱ」→「ッパ」
      - 「やっぱり」→「ヤッパリ」
    - 「っと」→「ット」
      - 「ちょっと」→「チョット」
    - 「っか」→「ッカ」
      - 「せっかく」→「セッカク」
    - 「っこ」→「ッコ」
      - 「びっくり」→「ビックリ」
    - 「っち」→「ッチ」
      - 「もっと」→「モット」
    - 「っぷ」→「ップ」
      - 「アップ」→「アップ」
    - 「っき」→「ッキ」
      - 「すっきり」→「スッキリ」
  ❌ 誤った例:
    - 「って」→「ツッテ」（×「ツ」が大きい）
    - 「って」→「テ」（×促音なし）

**スペース**: スペースは入れないでください。すべて詰めて書いてください。

**数字の表記**: アラビア数字はそのまま残してください（カタカナに変換しない）

**例**:
  - text: "明日は晴れです" → reading: "アシタワハレデス"
  - text: "97個あります" → reading: "97コアリマス"
  - text: "2026年はヤバい" → reading: "2026ネンワヤバイ"
  - text: "ESPが次の章" → reading: "イーエスピーガツギノショウ"
  - text: "APIって何？" → reading: "エーピーアイッテナニ？"
  - text: "Web3って難しいのに。操作できるの！？" → reading: "ウェブ3ッテムズカシイノニ。ソウサデキルノ！？"

【スライド画像について - 重要な選択基準】
- 各セクションには、source_image_urlまたはslide_promptのどちらか一方を指定してください
- source_image_url: 元記事の画像リストから適切な画像を選択する場合に使用
- slide_prompt: AI生成する場合に使用

**画像採用の判断基準（必ず従ってください）:**
- 画像リストに含まれる各画像の「Alt」「Title」「Description」を**総合的に判断**してください
- **採用すべき場合**: 画像の説明テキストが、そのセクションで説明する内容と**直接的に関連**している場合のみ
  - 例: セクションが「助成金の実績」を説明 → 画像altが「2024年の助成金配分グラフ」→ 採用OK
  - 例: セクションが「Commit-Boost」を説明 → 画像altが「Commit-Boost architecture diagram」→ 採用OK
- **採用すべきでない場合**:
  - 画像の説明が「背景」「バナー」「ロゴ」「アイコン」「装飾」などの汎用的・装飾的な内容
  - 画像の説明がセクション内容と無関係または曖昧
  - 例: セクションが「ESPの概要」を説明 → 画像altが「ETH上部背景開始画像」→ 採用NG（AI生成を使用）
- **迷った場合はAI生成を優先**: 関連性が不明確な場合は、source_image_urlを指定せずslide_promptでAI生成してください
"""

SCRIPT_GENERATION_PROMPT_EN = """
You are an expert YouTube video script writer.
Create a video script that captivates viewers and ensures deep understanding from the following content.

[Basic Requirements]
- Write narration in natural spoken language with the character of "{character}"
- Style: {style}
- Each section should be 3-6 sentences
- **IMPORTANT**: Split each narration into approximately 40 characters. Use punctuation (. , ! ?) as natural break points
- Avoid or clearly explain technical terms
- Include visual descriptions
- **IMPORTANT**: Write slide_prompt in English, and specify text to display on slides in English
  - Example: "A slide with text 'Database Design' in the center, modern design"

[Storytelling Structure - Follow Narrative Arc]
Structure your script with the following flow:

**1. Hook - The First 15 Seconds Are Critical**
- Start with a surprising fact, problem statement, or question that sparks curiosity
- Examples: "Did you know 97% of people don't know this fact about X?" "Why do Y fail? The reason is..."
- Prevent viewer drop-off at this crucial moment

**2. Context - Why This Matters**
- Explain why this topic is important to the viewer
- "Ever had this problem?" "This actually impacts your X directly"
- Help viewers see this as personally relevant

**3. Core Content - 3 to 5 Main Points**
- Structure points logically (cause→effect, problem→solution, etc.)
- Use transitional phrases between sections: "Next, let's look at...", "Related to this..."
- **Always include concrete examples, analogies, or real-world cases**, not just abstract explanations
  - Bad: "This improves efficiency"
  - Good: "For example, tasks that took 1 hour now finish in 10 minutes"

**4. Conclusion - Summary & Next Actions**
- Recap key points (max 3)
- Give viewers clear next steps ("Start by trying X first")

[Deepening Understanding - Viewer Perspective First]
- **Anticipate first-time viewer questions**: Answer "What is X?", "Why does this happen?", "How does this apply to me?"
- **Progressive explanation**: Overview → Details → Application
  - Show the big picture first, then dive into specifics
- **Examples are mandatory**: Always pair abstract concepts with relatable examples or analogies
  - Example: "A database is like a library. It organizes information so you can retrieve it instantly when needed"

[Script Structure Rules - MANDATORY]
- **Complete the script with a logical structure**
- Create at least 6 sections minimum:
  - Hook (1 section)
  - Context (1 section)
  - Core Content (3-5 sections)
  - Conclusion (1 section)
- The final section MUST include "Summary", "Conclusion", or "Next Steps"
- Do NOT end the script abruptly. Always provide viewers with a conclusion

[Self-Evaluation Checklist]
After creating the script, verify:
✓ Does the first 15 seconds grab viewer attention?
✓ Can someone with zero background knowledge understand this?
✓ Are sections logically connected?
✓ Are abstract explanations supported with concrete examples?
✓ Will viewers feel satisfied with the conclusion?
✓ Does every narration have a reading field?

[Source Content]
Title: {title}
Description: {description}

{content}

{images_section}

[CRITICAL REQUIREMENT]
The reading field quality is critical to system success. You MUST:
1. Include a reading field for EVERY narration
2. For English scripts, copy the text field to reading field

Failure to include reading fields will cause audio synthesis to fail.

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
  ]
}}

[Reading Field - CRITICAL]
- **Required field**: Each narration MUST include a reading field
- For English narration, simply copy the text field to reading field (no special pronunciation rules)
- Example: text: "Hello world" → reading: "Hello world"

[About Slide Images - Critical Selection Criteria]
- For each section, specify either source_image_url OR slide_prompt (not both)
- source_image_url: Use when selecting an appropriate image from the blog's image list
- slide_prompt: Use when generating a new slide with AI

**Image Adoption Criteria (MUST follow):**
- Evaluate each image's "Alt", "Title", and "Description" **holistically**
- **ADOPT only when**: The image description is **directly relevant** to what the section is explaining
  - Example: Section explains "grant achievements" → Image alt is "2024 grant allocation chart" → ADOPT
  - Example: Section explains "Commit-Boost" → Image alt is "Commit-Boost architecture diagram" → ADOPT
- **DO NOT ADOPT when**:
  - Image description contains generic/decorative terms like "background", "banner", "logo", "icon", "decoration"
  - Image description is unrelated or ambiguous to the section content
  - Example: Section explains "ESP overview" → Image alt is "ETH top background start image" → DO NOT ADOPT (use AI generation)
- **When in doubt, prefer AI generation**: If relevance is unclear, do NOT set source_image_url and use slide_prompt instead
"""

SCRIPT_GENERATION_PROMPT_DIALOGUE_JA = """
あなたはYouTube動画の台本作成の専門家です。
以下のコンテンツから、複数のキャラクターが自然な掛け合いで視聴者を引き込み、深く理解させる動画台本を作成してください。

【登場キャラクター】
{personas_description}

【役割割り当てと個性の引き出し方】
各キャラクターに明確で具体的な役割を割り当て、その個性を最大限活かしてください。

**推奨役割パターン（2話者の場合）**:
1. **解説役 × 質問役**: 解説役が説明し、質問役が視聴者目線で疑問を投げかける
   - 質問役の例: 「ちょっと待って！それって○○ってこと？」「具体的にはどう使うの？」
2. **解説役 × リアクション役**: 解説役が説明し、リアクション役が驚きや感想で盛り上げる
   - リアクション役の例: 「えー！すごい！」「なるほど、そういうことか！」
3. **共同解説役**: 2人で補完し合いながら説明（一方が概要、もう一方が詳細など）

**3話者以上の拡張パターン**:
- 解説役 + 質問役 + ツッコミ役
- メイン解説役 + サブ解説役 + 聞き役

**キャラクター個性の活かし方**:
- 各キャラの口調・語尾を一貫させる（「〜だよ」「〜です」「〜なのだ」など）
- 性格に合った反応をさせる（元気系→「わー！」、冷静系→「なるほど」）
- 得意分野を活かす（技術系キャラは詳細説明、初心者系キャラは基本質問）

【会話リズムとテンポ】
単調な交互発言を避け、自然な会話の流れを作ってください：

- **短い相槌を活用**: 「うん」「そうそう」「えー！」などで会話を活性化
- **連続発言もOK**: 重要な説明は1人が2〜3ターン連続で話してもよい
- **割り込みや補足**: 「あ、それ言おうと思ってた！」「補足すると...」など自然な流れ
- **感情の起伏**: 驚き→理解→納得の流れで視聴者も引き込む

【基本要件】
- 各キャラクターの個性を活かした自然な会話形式で台本を作成してください
- スタイル: {style}
- 各セクションは5-10ターン程度の対話で構成してください
- **重要**: 各セリフは40文字程度を目安に分割してください。句読点（。、！？）で区切り、長い文は自然な位置で分けてください
- 専門用語は避けるか、わかりやすく説明してください
- 視覚的な説明を含めてください
- **重要**: slide_promptは英語で記述しますが、スライドに表示するテキストは日本語で指定してください
  - 例: "A slide with text 'データベース設計' in the center, modern design"

【ストーリーテリング構造 - 対話形式での起承転結】

**1. Hook（掴み）- 会話で視聴者を引き込む**
- 驚きの事実を共有したり、問題を提起したりする掛け合いから始める
- 例:
  - A: 「ねえねえ、○○って知ってる？」
  - B: 「何それ！気になる！」
  - A: 「実は97%の人が知らないんだけど...」

**2. Context（背景）- なぜ重要か対話で動機付け**
- 視聴者の「自分ごと」として捉えさせる会話
- 例:
  - A: 「こんな悩み、ない？」
  - B: 「あるある！いつも困ってたんだよね」
  - A: 「実はそれ、今日の話で解決できるかも」

**3. Core Content（本編）- 対話で深く理解**
- 解説役が説明→質問役が確認→解説役が具体例、のサイクルを回す
- **視聴者視点の疑問を質問役に代弁させる**
  - 質問役: 「待って、それって○○ってこと？」「初心者でもできる？」
- **具体例・比喩を必ず含める**
  - 解説役: 「例えばね、これは図書館みたいなもので...」
  - 質問役: 「なるほど！わかりやすい！」

**4. Conclusion（まとめ）- 対話で振り返り**
- 2人で要点を確認し合う
- 視聴者への次のアクションを提案
- 例:
  - A: 「じゃあまとめると、ポイントは3つだね」
  - B: 「まずは○○から試してみよう！」

【台本構成の必須ルール】
- 論理的な構成で最後まで完成させてください
- 最低6セクション以上を目安に構成してください
  - Hook（1セクション）
  - Context（1セクション）
  - Core Content（3〜5セクション）
  - Conclusion（1セクション）
- 最後のセクションは必ず「まとめ」「結論」「次のステップ」のいずれかを含めてください
- 途中で終わらせず、視聴者に結論を伝えてください

【自己評価チェックリスト】
台本作成後、以下を自己確認してください：
✓ 会話が棒読みでなく、自然な掛け合いになっているか？
✓ 各キャラクターの個性と役割が明確か？
✓ 視聴者の疑問を先回りして質問役が聞いているか？
✓ 単調な交互発言になっていないか？（リズムに変化があるか）
✓ 最初の15秒で興味を引けるか？
✓ 最後まで視聴者を飽きさせない展開か？
✓ すべてのreadingフィールドで促音が正しく使われているか？（「ツッテ」×、「ッテ」○）
✓ 助詞の発音ルールが適用されているか？（は→ワ、へ→エ）

【元コンテンツ】
タイトル: {title}
説明: {description}

{content}

{images_section}

【CRITICAL REQUIREMENT - 最重要】
reading フィールドの品質はシステムの成否を左右します。以下を必ず守ってください：
1. 促音（小さい「ッ」）を正確に使用
2. 助詞の発音ルールを適用（は→ワ、へ→エ）
3. アルファベット略語の音引きルール適用

これらのルールを破ると、音声合成が失敗します。

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
          "reading": "セリフ ノ カタカナ ヨミ"
        }}
      ],
      "slide_prompt": "このセクションのスライド画像生成用プロンプト（英語で記述、ただしスライド内の表示テキストは日本語で指定）",
      "source_image_url": "元記事の画像URL（該当する場合のみ。画像リストから選択）"
    }}
  ]
}}

【reading フィールドについて - CRITICAL】
各ナレーションには必ず reading フィールドを含めてください。これは音声合成で正しい発音を実現するために必須です。

- **必須フィールド**: 各セリフには必ず reading フィールドを含める
- **カタカナ形式**: すべてカタカナで記述（ひらがな不可）

**助詞の発音ルール**:
  - 「は」→「ワ」（例: 「これは」→「コレワ」）
  - 「へ」→「エ」（例: 「東京へ」→「トウキョウエ」）

**アルファベット略語の音引き**:
英字1文字ごとにカタカナで表記し、最後に長音「ー」を付けます
  - 「ESP」→「イーエスピー」（×イーエスピージ）
  - 「API」→「エーピーアイ」
  - 「CPU」→「シーピーユー」
  - 「USB」→「ユーエスビー」

**促音の表記（CRITICAL - 最重要）**:
小さい「ッ」を正しく使用してください。「ツッテ」は誤りです。
  ✅ 正しい例:
    - 「って」→「ッテ」
      - 「聞いたって」→「キイタッテ」
      - 「RAGって何？」→「ラグッテナニ？」
      - 「APIって何？」→「エーピーアイッテナニ？」
    - 「った」→「ッタ」
      - 「言った」→「イッタ」
      - 「使った」→「ツカッタ」
    - 「っぱ」→「ッパ」
      - 「やっぱり」→「ヤッパリ」
    - 「っと」→「ット」
      - 「ちょっと」→「チョット」
    - 「っか」→「ッカ」
      - 「せっかく」→「セッカク」
    - 「っこ」→「ッコ」
      - 「びっくり」→「ビックリ」
    - 「っち」→「ッチ」
      - 「もっと」→「モット」
    - 「っぷ」→「ップ」
      - 「アップ」→「アップ」
    - 「っき」→「ッキ」
      - 「すっきり」→「スッキリ」
  ❌ 誤った例:
    - 「って」→「ツッテ」（×「ツ」が大きい）
    - 「って」→「テ」（×促音なし）

**スペース**: スペースは入れないでください。すべて詰めて書いてください。

**数字の表記**: アラビア数字はそのまま残してください（カタカナに変換しない）

**例**:
  - text: "ねえねえ！" → reading: "ネエネエ！"
  - text: "これは便利だね" → reading: "コレワベンリダネ"
  - text: "東京へ行こう" → reading: "トウキョウエイコウ"
  - text: "2026年はヤバい" → reading: "2026ネンワヤバイ"
  - text: "ESPが次の章って聞いた！" → reading: "イーエスピーガツギノショウッテキイタ！"
  - text: "RAGって何？" → reading: "ラグッテナニ？"
  - text: "97%削減！" → reading: "97パーセントサクゲン！"

【スライド画像について - 重要な選択基準】
- 各セクションには、source_image_urlまたはslide_promptのどちらか一方を指定してください
- source_image_url: 元記事の画像リストから適切な画像を選択する場合に使用
- slide_prompt: AI生成する場合に使用

**画像採用の判断基準（必ず従ってください）:**
- 画像リストに含まれる各画像の「Alt」「Title」「Description」を**総合的に判断**してください
- **採用すべき場合**: 画像の説明テキストが、そのセクションで説明する内容と**直接的に関連**している場合のみ
  - 例: セクションが「助成金の実績」を説明 → 画像altが「2024年の助成金配分グラフ」→ 採用OK
  - 例: セクションが「Commit-Boost」を説明 → 画像altが「Commit-Boost architecture diagram」→ 採用OK
- **採用すべきでない場合**:
  - 画像の説明が「背景」「バナー」「ロゴ」「アイコン」「装飾」などの汎用的・装飾的な内容
  - 画像の説明がセクション内容と無関係または曖昧
  - 例: セクションが「ESPの概要」を説明 → 画像altが「ETH上部背景開始画像」→ 採用NG（AI生成を使用）
- **迷った場合はAI生成を優先**: 関連性が不明確な場合は、source_image_urlを指定せずslide_promptでAI生成してください
"""

SCRIPT_GENERATION_PROMPT_DIALOGUE_EN = """
You are an expert YouTube video script writer.
Create a video script with multiple characters having natural, engaging dialogue that captivates viewers and ensures deep understanding.

[Characters]
{personas_description}

[Role Assignment and Character Development]
Assign clear, specific roles to each character and leverage their unique personalities to the fullest.

**Recommended Role Patterns (2 characters)**:
1. **Explainer × Questioner**: Explainer provides information, Questioner asks from viewer's perspective
   - Questioner examples: "Wait, does that mean X?", "How exactly do you use it?"
2. **Explainer × Reactor**: Explainer teaches, Reactor responds with surprise and enthusiasm
   - Reactor examples: "Wow! Amazing!", "Oh, I see what you mean!"
3. **Co-Explainers**: Both complement each other (one covers overview, other handles details)

**Extended Patterns (3+ characters)**:
- Explainer + Questioner + Commentator
- Main Explainer + Sub Explainer + Listener

**Bringing Out Character Personalities**:
- Maintain consistent speech patterns for each character ("you know", "indeed", "like", etc.)
- Give personality-appropriate reactions (energetic→"Whoa!", calm→"I see")
- Leverage expertise (tech character gives details, beginner character asks basics)

[Conversation Rhythm and Pacing]
Avoid monotonous turn-taking and create natural conversational flow:

- **Use short acknowledgments**: "Yeah", "Right", "Wow!" to energize dialogue
- **Consecutive turns OK**: Important explanations can have 2-3 consecutive lines from one character
- **Interruptions and additions**: "Oh, I was about to say that!", "To add to that..." for natural flow
- **Emotional arc**: Surprise → Understanding → Conviction to pull viewers along

[Basic Requirements]
- Create natural dialogue that leverages each character's personality
- Style: {style}
- Each section should have 5-10 dialogue turns
- **IMPORTANT**: Split each dialogue line into approximately 40 characters. Use punctuation (. , ! ?) as natural break points
- Avoid or clearly explain technical terms
- Include visual descriptions
- **IMPORTANT**: Write slide_prompt in English, and specify text to display on slides in English
  - Example: "A slide with text 'Database Design' in the center, modern design"

[Storytelling Structure - Narrative Arc in Dialogue]

**1. Hook - Engage Through Conversation**
- Start with dialogue sharing surprising facts or raising problems
- Example:
  - A: "Hey, do you know about X?"
  - B: "What's that? Now I'm curious!"
  - A: "97% of people don't know this, but..."

**2. Context - Motivate Through Dialogue**
- Make it personally relevant through conversation
- Example:
  - A: "Ever had this problem?"
  - B: "All the time! It's so frustrating"
  - A: "Well, today's topic might just solve that"

**3. Core Content - Deepen Understanding Through Dialogue**
- Cycle: Explainer explains → Questioner confirms → Explainer gives examples
- **Have Questioner voice viewer questions**
  - Questioner: "Wait, does that mean X?", "Can beginners do this?"
- **Always include concrete examples and analogies**
  - Explainer: "Think of it like a library..."
  - Questioner: "Oh! That makes sense!"

**4. Conclusion - Recap Through Dialogue**
- Characters review key points together
- Suggest next actions to viewers
- Example:
  - A: "So in summary, there are 3 key points"
  - B: "Let's start by trying X first!"

[Script Structure Rules - MANDATORY]
- **Complete the script with a logical structure**
- Create at least 6 sections minimum:
  - Hook (1 section)
  - Context (1 section)
  - Core Content (3-5 sections)
  - Conclusion (1 section)
- The final section MUST include "Summary", "Conclusion", or "Next Steps"
- Do NOT end the script abruptly. Always provide viewers with a conclusion

[Self-Evaluation Checklist]
After creating the script, verify:
✓ Does dialogue sound natural, not robotic?
✓ Are character roles and personalities clear?
✓ Does Questioner anticipate viewer questions?
✓ Is there rhythm variation (not just alternating turns)?
✓ Does the first 15 seconds grab attention?
✓ Will viewers stay engaged until the end?
✓ Does every narration have a reading field?

[Source Content]
Title: {title}
Description: {description}

{content}

{images_section}

[CRITICAL REQUIREMENT]
The reading field quality is critical to system success. You MUST:
1. Include a reading field for EVERY narration
2. For Japanese dialogue, follow all pronunciation rules (particles, sokuon, spacing)
3. For English dialogue, copy the text to reading field

Failure to include reading fields will cause audio synthesis to fail.

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
  ]
}}

[Reading Field - CRITICAL]
Each narration MUST include a reading field. This is essential for accurate audio synthesis.

- **Required field**: Every dialogue line must have a reading field
- **Katakana format**: Write in katakana (not hiragana or romaji)
- **Particle pronunciation**: Convert particles to their spoken form:
  - "は" → "ワ" (e.g., "これは" → "コレワ")
  - "へ" → "エ" (e.g., "東京へ" → "トウキョウエ")
- **Examples**:
  - text: "Hello there!" → reading: "ハローゼアー！"
  - text: "Let's go to Tokyo" → reading: "レッツゴートゥートウキョウ"
  - text: "What is RAG?" → reading: "ホワットイズラグ？"
  - text: "97% reduction!" → reading: "ナインティセブンパーセントリダクション！"

[About Slide Images - Critical Selection Criteria]
- For each section, specify either source_image_url OR slide_prompt (not both)
- source_image_url: Use when selecting an appropriate image from the blog's image list
- slide_prompt: Use when generating a new slide with AI

**Image Adoption Criteria (MUST follow):**
- Evaluate each image's "Alt", "Title", and "Description" **holistically**
- **ADOPT only when**: The image description is **directly relevant** to what the section is explaining
  - Example: Section explains "grant achievements" → Image alt is "2024 grant allocation chart" → ADOPT
  - Example: Section explains "Commit-Boost" → Image alt is "Commit-Boost architecture diagram" → ADOPT
- **DO NOT ADOPT when**:
  - Image description contains generic/decorative terms like "background", "banner", "logo", "icon", "decoration"
  - Image description is unrelated or ambiguous to the section content
  - Example: Section explains "ESP overview" → Image alt is "ETH top background start image" → DO NOT ADOPT (use AI generation)
- **When in doubt, prefer AI generation**: If relevance is unclear, do NOT set source_image_url and use slide_prompt instead
"""

SCRIPT_GENERATION_PROMPTS = {
    "ja": SCRIPT_GENERATION_PROMPT_JA,
    "en": SCRIPT_GENERATION_PROMPT_EN,
}

SCRIPT_GENERATION_PROMPTS_DIALOGUE = {
    "ja": SCRIPT_GENERATION_PROMPT_DIALOGUE_JA,
    "en": SCRIPT_GENERATION_PROMPT_DIALOGUE_EN,
}


def select_personas_from_pool(
    personas: list[dict[str, Any]],
    pool_config: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Select personas from pool based on configuration.

    Args:
        personas: List of persona dictionaries with 'id', 'name', 'character' keys.
        pool_config: PersonaPoolConfig dictionary with 'enabled', 'count', 'seed' keys.
                     If None or disabled, returns all personas unchanged.

    Returns:
        Selected personas (all personas if pool disabled, random subset if enabled).

    Raises:
        ValueError: If count > len(personas) when pool is enabled.
    """
    # If no pool config or disabled, return all personas
    if not pool_config or not pool_config.get("enabled", False):
        return personas

    count = pool_config.get("count", 2)
    seed = pool_config.get("seed")

    # Validate count
    if count > len(personas):
        raise ValueError(
            f"Cannot select {count} personas from pool of {len(personas)}. "
            f"Available personas: {', '.join(p['id'] for p in personas)}"
        )

    # Set seed for reproducibility if provided
    if seed is not None:
        random.seed(seed)
    else:
        # Ensure true randomness by reseeding with system time
        # This prevents the global random state from being reused
        random.seed()

    # Random selection without replacement
    selected = random.sample(personas, k=count)

    return selected


def _format_images_section(images: list[dict[str, str]] | None, language: str) -> str:
    """Format images section for prompt.

    Args:
        images: List of image metadata dicts with 'src', 'alt', 'title' keys.
        language: Language code ('ja' or 'en').

    Returns:
        Formatted images section string.
    """
    if not images:
        return ""

    if language == "ja":
        section = "【利用可能な画像】\n以下の画像がブログ記事内で利用可能です。適切なセクションに割り当ててください：\n"
    else:
        section = "[Available Images]\nThe following images are available from the blog content. Assign them to appropriate sections:\n"

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

        section += f"{idx}. URL: {img['src']}\n   {description}\n"

    return section


def _build_prompt(
    content: str,
    title: str | None,
    description: str | None,
    character: str,
    style: str,
    language: str,
    images_section: str,
    personas: list[dict[str, str]] | None,
) -> str:
    """Build prompt for LLM script generation.

    Args:
        content: Source content (markdown or text).
        title: Content title.
        description: Content description.
        character: Character name for narration (used when no personas defined).
        style: Narration style (casual, formal, educational).
        language: Language code for script generation (ja, en).
        images_section: Formatted images section string.
        personas: List of persona dicts with 'id', 'name', 'character' keys.

    Returns:
        Formatted prompt string.
    """
    if personas and len(personas) >= 2:
        # Multi-speaker dialogue mode: use dialogue prompt
        prompt_template = SCRIPT_GENERATION_PROMPTS_DIALOGUE.get(
            language, SCRIPT_GENERATION_PROMPT_DIALOGUE_JA
        )
        # Format personas description
        personas_description = ""
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
    else:
        # Single-speaker mode: use traditional single-speaker prompt
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
    return prompt


def _parse_script_response(
    script_data: dict[str, Any], personas: list[dict[str, str]] | None = None
) -> VideoScript:
    """Parse LLM response into VideoScript.

    Args:
        script_data: Parsed JSON response from LLM.
        personas: Optional list of persona dicts. If provided and length is 1,
                  assigns that persona_id to all narrations without persona_id.

    Returns:
        VideoScript object.

    Raises:
        ValueError: If response format is invalid or missing required fields.
    """
    # Parse sections - unified format with narrations list
    # Determine default persona_id for single-speaker mode
    default_persona_id = None
    if personas and len(personas) == 1:
        default_persona_id = personas[0]["id"]

    sections = []
    for section in script_data["sections"]:
        narrations: list[Narration] = []

        if "narrations" in section and section["narrations"]:
            # New unified format
            for n in section["narrations"]:
                if isinstance(n, str):
                    # Simple string format (single speaker) - legacy, use text as reading
                    narrations.append(Narration(text=n, reading=n, persona_id=default_persona_id))
                else:
                    # Object format with required reading field
                    if "reading" not in n or not n["reading"]:
                        raise ValueError(
                            f"Missing or empty 'reading' field in narration: {n.get('text', 'N/A')[:50]}...\n"
                            f"The LLM did not generate the required 'reading' field. "
                            f"This is a critical error in script generation."
                        )
                    # Use persona_id from response, or default for single-speaker mode
                    persona_id = n.get("persona_id") or default_persona_id
                    narrations.append(
                        Narration(text=n["text"], reading=n["reading"], persona_id=persona_id)
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
            # Split into phrases per spec requirement
            narration_text = section["narration"]
            phrases = split_into_phrases(narration_text)
            for phrase in phrases:
                narrations.append(
                    Narration(
                        text=phrase.text,
                        reading=phrase.text,  # Use phrase text as reading
                        persona_id=default_persona_id,
                    )
                )

        sections.append(
            ScriptSection(
                title=section["title"],
                narrations=narrations,
                slide_prompt=section.get("slide_prompt"),
                source_image_url=section.get("source_image_url"),
            )
        )

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

    return VideoScript(
        title=script_data["title"],
        description=script_data["description"],
        sections=sections,
        role_assignments=role_assignments,
    )


def _validate_script_completeness(script: VideoScript) -> None:
    """Validate script completeness.

    Args:
        script: VideoScript to validate.

    Raises:
        ValueError: If script is incomplete.
    """
    if not script.sections:
        raise ValueError("Script generation failed: no sections were generated")
    if not script.sections[-1].narrations:
        raise ValueError(
            f"Script generation incomplete: last section '{script.sections[-1].title}' has no narrations. "
            "The LLM response may have been truncated. Try regenerating the script."
        )


async def _call_llm_api(prompt: str, model: str, api_key: str, base_url: str) -> dict[str, Any]:
    """Call LLM API for script generation.

    Args:
        prompt: Formatted prompt string.
        model: Model identifier.
        api_key: API key for authentication.
        base_url: API base URL.

    Returns:
        Parsed JSON response from LLM.

    Raises:
        RuntimeError: If API request fails.
        ValueError: If response format is invalid.
    """
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

    async with httpx.AsyncClient(timeout=TimeoutConstants.HTTP_EXTENDED) as client:
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
    return json.loads(message_content)


async def generate_script(
    content: str,
    model: str,
    title: str | None = None,
    description: str | None = None,
    character: str = "ずんだもん",
    style: str = "casual",
    language: str = "ja",
    api_key: str | None = None,
    base_url: str = "https://openrouter.ai/api/v1",
    images: list[dict[str, str]] | None = None,
    personas: list[dict[str, str]] | None = None,
    pool_config: dict[str, Any] | None = None,
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
        pool_config: PersonaPoolConfig dict for random persona selection.
                     If enabled, randomly selects subset of personas.

    Returns:
        Generated video script.

    Raises:
        httpx.HTTPError: If API request fails.
        ValueError: If response parsing fails.
    """
    # Apply persona pool selection if configured
    if personas and pool_config:
        import logging

        logger = logging.getLogger(__name__)
        original_count = len(personas)
        personas = select_personas_from_pool(personas, pool_config)
        selected_ids = [p["id"] for p in personas]
        ids_str = ", ".join(selected_ids)
        logger.info(f"Persona pool: selected {len(personas)}/{original_count} personas: {ids_str}")

    # Format images section for prompt
    images_section = _format_images_section(images, language)

    # Build prompt
    prompt = _build_prompt(
        content=content,
        title=title,
        description=description,
        character=character,
        style=style,
        language=language,
        images_section=images_section,
        personas=personas,
    )

    # Call LLM API
    script_data = await _call_llm_api(
        prompt=prompt,
        model=model,
        api_key=api_key or "",
        base_url=base_url,
    )

    # Parse response (pass personas for single-speaker mode persona_id assignment)
    script = _parse_script_response(script_data, personas=personas)

    # Validate completeness
    _validate_script_completeness(script)

    return script


class ScriptValidationResult:
    """Result of script validation."""

    def __init__(self) -> None:
        """Initialize validation result."""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.section_count: int = 0
        self.narration_count: int = 0

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0


def validate_script(
    script_path: Any, config_personas: list[dict[str, Any]] | None = None
) -> ScriptValidationResult:
    """Validate script file.

    Performs the following checks:
    1. YAML syntax validation
    2. Required fields (title, description, sections)
    3. Narrations format validation
    4. Persona ID reference validation (if config provided)

    Args:
        script_path: Path to script file to validate.
        config_personas: List of persona configs for ID validation (optional).

    Returns:
        ScriptValidationResult with errors, warnings, and statistics.
    """
    from pathlib import Path

    import yaml

    result = ScriptValidationResult()

    # Convert to Path if needed
    if not isinstance(script_path, Path):
        script_path = Path(script_path)

    # Check if file exists
    if not script_path.exists():
        result.add_error(f"File not found: {script_path}")
        return result

    # Step 1: YAML syntax check
    try:
        with script_path.open("r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)
    except yaml.YAMLError as e:
        error_msg = f"YAML parse error: {e}"
        # Try to include line number if available
        if hasattr(e, "problem_mark"):
            mark = getattr(e, "problem_mark")
            if mark and hasattr(mark, "line") and hasattr(mark, "column"):
                error_msg += f" (line {mark.line + 1}, column {mark.column + 1})"
        result.add_error(error_msg)
        return result
    except Exception as e:
        result.add_error(f"Failed to read file: {e}")
        return result

    if data is None:
        result.add_error("Script file is empty")
        return result

    # Step 2: Required fields validation
    if "title" not in data:
        result.add_error("Missing required field: title")
    if "description" not in data:
        result.add_error("Missing required field: description")
    if "sections" not in data:
        result.add_error("Missing required field: sections")
        return result

    sections = data["sections"]
    if not isinstance(sections, list):
        result.add_error("Field 'sections' must be a list")
        return result

    if len(sections) == 0:
        result.add_warning("Script has no sections")

    result.section_count = len(sections)

    # Step 3: Validate each section
    used_persona_ids: set[str] = set()

    for i, section in enumerate(sections):
        section_num = i + 1

        # Check section has title
        if "title" not in section:
            result.add_error(f"Section {section_num}: missing 'title' field")

        # Check narrations format
        has_narrations = "narrations" in section and section["narrations"]
        has_dialogues = "dialogues" in section and section["dialogues"]
        has_narration = "narration" in section

        if not has_narrations and not has_dialogues and not has_narration:
            result.add_error(
                f"Section {section_num} ('{section.get('title', 'N/A')}'): "
                f"missing narrations/dialogues/narration field"
            )
            continue

        # Validate narrations array format
        if has_narrations:
            narrations = section["narrations"]
            if not isinstance(narrations, list):
                result.add_error(
                    f"Section {section_num}: 'narrations' must be a list, got {type(narrations).__name__}"
                )
                continue

            for j, narration in enumerate(narrations):
                # Count narrations
                result.narration_count += 1

                # Skip string format (legacy)
                if isinstance(narration, str):
                    continue

                # Validate object format
                if not isinstance(narration, dict):
                    result.add_error(
                        f"Section {section_num}, narration {j + 1}: "
                        f"must be string or object, got {type(narration).__name__}"
                    )
                    continue

                if "text" not in narration:
                    result.add_error(
                        f"Section {section_num}, narration {j + 1}: missing 'text' field"
                    )

                # Collect persona IDs
                if "persona_id" in narration and narration["persona_id"]:
                    used_persona_ids.add(narration["persona_id"])

        # Validate dialogues array format (legacy)
        elif has_dialogues:
            dialogues = section["dialogues"]
            if not isinstance(dialogues, list):
                result.add_error(
                    f"Section {section_num}: 'dialogues' must be a list, got {type(dialogues).__name__}"
                )
                continue

            for j, dialogue in enumerate(dialogues):
                result.narration_count += 1

                if not isinstance(dialogue, dict):
                    result.add_error(f"Section {section_num}, dialogue {j + 1}: must be an object")
                    continue

                if "narration" not in dialogue:
                    result.add_error(
                        f"Section {section_num}, dialogue {j + 1}: missing 'narration' field"
                    )

                if "persona_id" in dialogue and dialogue["persona_id"]:
                    used_persona_ids.add(dialogue["persona_id"])

        else:
            # Single narration (legacy)
            result.narration_count += 1

    # Step 4: Persona ID reference validation (if config provided)
    if config_personas and used_persona_ids:
        defined_persona_ids = {p["id"] for p in config_personas}

        for persona_id in used_persona_ids:
            if persona_id not in defined_persona_ids:
                result.add_warning(
                    f"Unknown persona_id: {persona_id} "
                    f"(defined: {', '.join(sorted(defined_persona_ids))})"
                )

    return result
