"""Tests for script generator."""

from movie_generator.script.generator import (
    Narration,
    RoleAssignment,
    ScriptSection,
    VideoScript,
)


def test_script_section_with_source_image_url():
    """Test ScriptSection with source_image_url."""
    section = ScriptSection(
        title="Test Section",
        narrations=[
            Narration(text="This is a test narration.", reading="This is a test narration.")
        ],
        slide_prompt=None,
        source_image_url="https://example.com/image.jpg",
    )
    assert section.title == "Test Section"
    assert len(section.narrations) == 1
    assert section.narrations[0].text == "This is a test narration."
    assert section.narrations[0].reading == "This is a test narration."
    assert section.slide_prompt is None
    assert section.source_image_url == "https://example.com/image.jpg"


def test_script_section_with_slide_prompt():
    """Test ScriptSection with slide_prompt."""
    section = ScriptSection(
        title="Test Section",
        narrations=[
            Narration(text="This is a test narration.", reading="This is a test narration.")
        ],
        slide_prompt="A beautiful landscape",
        source_image_url=None,
    )
    assert section.title == "Test Section"
    assert section.narrations[0].text == "This is a test narration."
    assert section.narrations[0].reading == "This is a test narration."
    assert section.slide_prompt == "A beautiful landscape"
    assert section.source_image_url is None


def test_script_section_with_both():
    """Test ScriptSection with both slide_prompt and source_image_url."""
    section = ScriptSection(
        title="Test Section",
        narrations=[
            Narration(text="This is a test narration.", reading="This is a test narration.")
        ],
        slide_prompt="A beautiful landscape",
        source_image_url="https://example.com/image.jpg",
    )
    assert section.title == "Test Section"
    assert section.slide_prompt == "A beautiful landscape"
    assert section.source_image_url == "https://example.com/image.jpg"


def test_script_section_with_multi_speaker():
    """Test ScriptSection with multiple narrations (multi-speaker)."""
    section = ScriptSection(
        title="Test Section",
        narrations=[
            Narration(text="Hello!", reading="Hello!", persona_id="alice"),
            Narration(text="Hi there!", reading="Hi there!", persona_id="bob"),
            Narration(text="How are you?", reading="How are you?", persona_id="alice"),
        ],
        slide_prompt="A conversation between two people",
    )
    assert section.title == "Test Section"
    assert len(section.narrations) == 3
    assert section.narrations[0].persona_id == "alice"
    assert section.narrations[1].persona_id == "bob"
    assert section.narrations[2].persona_id == "alice"


def test_narration_without_persona():
    """Test Narration without persona_id (single speaker)."""
    narration = Narration(
        text="This is a single speaker narration.", reading="This is a single speaker narration."
    )
    assert narration.text == "This is a single speaker narration."
    assert narration.reading == "This is a single speaker narration."
    assert narration.persona_id is None


def test_narration_with_reading_field():
    """Test Narration with different text and reading (Japanese example)."""
    narration = Narration(text="明日は晴れです", reading="アシタワハレデス")
    assert narration.text == "明日は晴れです"
    assert narration.reading == "アシタワハレデス"
    assert narration.persona_id is None


def test_video_script_basic():
    """Test creating a basic VideoScript."""
    script = VideoScript(
        title="テスト動画",
        description="テストの説明",
        sections=[
            ScriptSection(
                title="セクション1",
                narrations=[Narration(text="こんにちは！", reading="コンニチワ！")],
                slide_prompt="A test slide",
            )
        ],
    )
    assert script.title == "テスト動画"
    assert len(script.sections) == 1
    assert script.sections[0].narrations[0].text == "こんにちは！"
    assert script.sections[0].narrations[0].reading == "コンニチワ！"


def test_role_assignment_basic():
    """Test RoleAssignment basic creation."""
    role = RoleAssignment(
        persona_id="zundamon", role="解説役", description="主に技術的な説明を担当するキャラクター"
    )
    assert role.persona_id == "zundamon"
    assert role.role == "解説役"
    assert role.description == "主に技術的な説明を担当するキャラクター"


def test_video_script_with_role_assignments():
    """Test VideoScript with role_assignments."""
    script = VideoScript(
        title="テスト動画",
        description="テストの説明",
        sections=[
            ScriptSection(
                title="セクション1",
                narrations=[
                    Narration(text="こんにちは！", reading="コンニチワ！", persona_id="zundamon"),
                    Narration(text="よろしく！", reading="ヨロシク！", persona_id="metan"),
                ],
                slide_prompt="A test slide",
            )
        ],
        role_assignments=[
            RoleAssignment(persona_id="zundamon", role="解説役", description="技術的な説明を担当"),
            RoleAssignment(persona_id="metan", role="質問役", description="視聴者の疑問を代弁"),
        ],
    )
    assert script.title == "テスト動画"
    assert len(script.sections) == 1
    assert script.role_assignments is not None
    assert len(script.role_assignments) == 2
    assert script.role_assignments[0].persona_id == "zundamon"
    assert script.role_assignments[0].role == "解説役"
    assert script.role_assignments[1].persona_id == "metan"
    assert script.role_assignments[1].role == "質問役"


def test_video_script_without_role_assignments():
    """Test VideoScript without role_assignments (backward compatibility)."""
    script = VideoScript(
        title="テスト動画",
        description="テストの説明",
        sections=[
            ScriptSection(
                title="セクション1",
                narrations=[Narration(text="こんにちは！", reading="コンニチワ！")],
                slide_prompt="A test slide",
            )
        ],
    )
    assert script.title == "テスト動画"
    assert len(script.sections) == 1
    assert script.role_assignments is None
