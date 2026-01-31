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


def test_parse_script_response_single_speaker():
    """Test _parse_script_response with single-speaker format."""
    from movie_generator.script.generator import _parse_script_response

    # Fixture: LLM response for single-speaker mode
    script_data = {
        "title": "テスト動画",
        "description": "シングルスピーカーのテスト",
        "sections": [
            {
                "title": "イントロ",
                "narrations": [
                    {"text": "やっほー！", "reading": "ヤッホー！"},
                    {"text": "ずんだもんなのだ。", "reading": "ズンダモンナノダ。"},
                ],
                "slide_prompt": "A slide with title 'イントロ'",
            },
            {
                "title": "本編",
                "narrations": [
                    {"text": "今日は説明するのだ。", "reading": "キョウワセツメイスルノダ。"},
                ],
                "slide_prompt": "A slide with title '本編'",
                "source_image_url": "https://example.com/image.jpg",
            },
        ],
    }

    script = _parse_script_response(script_data)

    assert script.title == "テスト動画"
    assert script.description == "シングルスピーカーのテスト"
    assert len(script.sections) == 2

    # Check first section
    assert script.sections[0].title == "イントロ"
    assert len(script.sections[0].narrations) == 2
    assert script.sections[0].narrations[0].text == "やっほー！"
    assert script.sections[0].narrations[0].reading == "ヤッホー！"
    assert script.sections[0].narrations[0].persona_id is None  # Single speaker
    assert script.sections[0].narrations[1].text == "ずんだもんなのだ。"
    assert script.sections[0].narrations[1].reading == "ズンダモンナノダ。"
    assert script.sections[0].slide_prompt == "A slide with title 'イントロ'"

    # Check second section
    assert script.sections[1].title == "本編"
    assert len(script.sections[1].narrations) == 1
    assert script.sections[1].narrations[0].text == "今日は説明するのだ。"
    assert script.sections[1].narrations[0].reading == "キョウワセツメイスルノダ。"
    assert script.sections[1].slide_prompt == "A slide with title '本編'"
    assert script.sections[1].source_image_url == "https://example.com/image.jpg"


def test_parse_script_response_multi_speaker():
    """Test _parse_script_response with multi-speaker format."""
    from movie_generator.script.generator import _parse_script_response

    # Fixture: LLM response for multi-speaker mode
    script_data = {
        "title": "対話動画",
        "description": "マルチスピーカーのテスト",
        "sections": [
            {
                "title": "対話開始",
                "narrations": [
                    {"text": "やっほー！", "reading": "ヤッホー！", "persona_id": "zundamon"},
                    {"text": "こんにちは！", "reading": "コンニチワ！", "persona_id": "metan"},
                ],
                "slide_prompt": "A slide with title '対話開始'",
            },
        ],
        "role_assignments": [
            {"persona_id": "zundamon", "role": "解説役", "description": "技術的な説明を担当"},
            {"persona_id": "metan", "role": "質問役", "description": "視聴者の疑問を代弁"},
        ],
    }

    script = _parse_script_response(script_data)

    assert script.title == "対話動画"
    assert script.description == "マルチスピーカーのテスト"
    assert len(script.sections) == 1

    # Check multi-speaker narrations
    assert script.sections[0].title == "対話開始"
    assert len(script.sections[0].narrations) == 2
    assert script.sections[0].narrations[0].text == "やっほー！"
    assert script.sections[0].narrations[0].reading == "ヤッホー！"
    assert script.sections[0].narrations[0].persona_id == "zundamon"
    assert script.sections[0].narrations[1].text == "こんにちは！"
    assert script.sections[0].narrations[1].reading == "コンニチワ！"
    assert script.sections[0].narrations[1].persona_id == "metan"

    # Check role assignments
    assert script.role_assignments is not None
    assert len(script.role_assignments) == 2
    assert script.role_assignments[0].persona_id == "zundamon"
    assert script.role_assignments[0].role == "解説役"
    assert script.role_assignments[1].persona_id == "metan"
    assert script.role_assignments[1].role == "質問役"


def test_parse_script_response_missing_reading_field():
    """Test _parse_script_response raises error when reading field is missing."""
    import pytest
    from movie_generator.script.generator import _parse_script_response

    # Fixture: Invalid response with missing reading field
    script_data = {
        "title": "テスト動画",
        "description": "不正なレスポンス",
        "sections": [
            {
                "title": "イントロ",
                "narrations": [
                    {"text": "やっほー！"},  # Missing 'reading' field
                ],
                "slide_prompt": "A test slide",
            },
        ],
    }

    with pytest.raises(ValueError, match="Missing or empty 'reading' field"):
        _parse_script_response(script_data)


def test_parse_script_response_legacy_single_narration_format():
    """Test _parse_script_response with legacy single narration format."""
    from movie_generator.script.generator import _parse_script_response

    # Fixture: Legacy format with single narration field
    script_data = {
        "title": "レガシー動画",
        "description": "旧フォーマット",
        "sections": [
            {
                "title": "セクション",
                "narration": "これはレガシーフォーマットです。",  # Legacy field
                "slide_prompt": "A test slide",
            },
        ],
    }

    script = _parse_script_response(script_data)

    assert script.title == "レガシー動画"
    assert len(script.sections) == 1
    assert script.sections[0].title == "セクション"
    assert len(script.sections[0].narrations) == 1
    assert script.sections[0].narrations[0].text == "これはレガシーフォーマットです。"
    assert script.sections[0].narrations[0].reading == "これはレガシーフォーマットです。"
    assert script.sections[0].narrations[0].persona_id is None


def test_validate_script_completeness_success():
    """Test _validate_script_completeness with valid script."""
    from movie_generator.script.generator import _validate_script_completeness

    script = VideoScript(
        title="完全なスクリプト",
        description="有効なスクリプト",
        sections=[
            ScriptSection(
                title="セクション1",
                narrations=[Narration(text="テスト", reading="テスト")],
                slide_prompt="A test slide",
            ),
            ScriptSection(
                title="セクション2",
                narrations=[Narration(text="最後の文", reading="サイゴノブン")],
                slide_prompt="Another slide",
            ),
        ],
    )

    # Should not raise any exception
    _validate_script_completeness(script)


def test_validate_script_completeness_no_sections():
    """Test _validate_script_completeness raises error for empty sections."""
    import pytest
    from movie_generator.script.generator import _validate_script_completeness

    script = VideoScript(title="空のスクリプト", description="セクションなし", sections=[])

    with pytest.raises(ValueError, match="no sections were generated"):
        _validate_script_completeness(script)


def test_validate_script_completeness_last_section_empty():
    """Test _validate_script_completeness raises error for incomplete last section."""
    import pytest
    from movie_generator.script.generator import _validate_script_completeness

    script = VideoScript(
        title="不完全なスクリプト",
        description="最後のセクションが空",
        sections=[
            ScriptSection(
                title="セクション1",
                narrations=[Narration(text="テスト", reading="テスト")],
                slide_prompt="A test slide",
            ),
            ScriptSection(
                title="最後のセクション",
                narrations=[],  # Empty narrations
                slide_prompt="Empty slide",
            ),
        ],
    )

    with pytest.raises(ValueError, match="Script generation incomplete"):
        _validate_script_completeness(script)
