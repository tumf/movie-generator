"""Tests for persona pool random selection functionality."""

import pytest

from movie_generator.config import (
    Config,
    PersonaConfig,
    PersonaPoolConfig,
    VoicevoxSynthesizerConfig,
)
from movie_generator.script.generator import select_personas_from_pool


class TestSelectPersonasFromPool:
    """Test persona pool selection logic."""

    @pytest.fixture
    def personas(self) -> list[dict[str, str]]:
        """Sample persona list for testing."""
        return [
            {"id": "zundamon", "name": "ずんだもん", "character": "元気で明るい東北の妖精"},
            {"id": "metan", "name": "四国めたん", "character": "優しくて落ち着いた四国の妖精"},
            {
                "id": "tsumugi",
                "name": "春日部つむぎ",
                "character": "明るく元気な春日部出身の女の子",
            },
        ]

    def test_pool_disabled_returns_all_personas(self, personas: list[dict[str, str]]) -> None:
        """Test that disabled pool returns all personas unchanged."""
        pool_config = {"enabled": False, "count": 2}
        result = select_personas_from_pool(personas, pool_config)
        assert result == personas
        assert len(result) == 3

    def test_pool_none_returns_all_personas(self, personas: list[dict[str, str]]) -> None:
        """Test that None pool config returns all personas."""
        result = select_personas_from_pool(personas, None)
        assert result == personas
        assert len(result) == 3

    def test_random_selection_with_seed(self, personas: list[dict[str, str]]) -> None:
        """Test reproducible random selection with seed."""
        pool_config = {"enabled": True, "count": 2, "seed": 42}
        result1 = select_personas_from_pool(personas, pool_config)

        # Same seed should produce same result
        pool_config2 = {"enabled": True, "count": 2, "seed": 42}
        result2 = select_personas_from_pool(personas, pool_config2)

        assert len(result1) == 2
        assert len(result2) == 2
        assert result1 == result2
        assert all(p in personas for p in result1)

    def test_random_selection_without_seed(self, personas: list[dict[str, str]]) -> None:
        """Test random selection produces valid results."""
        pool_config = {"enabled": True, "count": 2, "seed": None}
        result = select_personas_from_pool(personas, pool_config)

        assert len(result) == 2
        assert all(p in personas for p in result)
        # Ensure no duplicates
        assert len(set(p["id"] for p in result)) == 2

    def test_selection_count_validation(self, personas: list[dict[str, str]]) -> None:
        """Test that count > len(personas) raises ValueError."""
        pool_config = {"enabled": True, "count": 5}  # More than 3 personas

        with pytest.raises(ValueError, match="Cannot select 5 personas from pool of 3"):
            select_personas_from_pool(personas, pool_config)

    def test_selection_count_equals_pool_size(self, personas: list[dict[str, str]]) -> None:
        """Test selection when count equals pool size."""
        pool_config = {"enabled": True, "count": 3, "seed": 42}
        result = select_personas_from_pool(personas, pool_config)

        assert len(result) == 3
        # Should contain all personas (order may differ)
        assert set(p["id"] for p in result) == {"zundamon", "metan", "tsumugi"}

    def test_selection_single_persona(self, personas: list[dict[str, str]]) -> None:
        """Test selection of single persona."""
        pool_config = {"enabled": True, "count": 1, "seed": 42}
        result = select_personas_from_pool(personas, pool_config)

        assert len(result) == 1
        assert result[0] in personas

    def test_different_seeds_produce_different_results(
        self, personas: list[dict[str, str]]
    ) -> None:
        """Test that different seeds can produce different selections."""
        # Run multiple times to increase chance of different results
        results = []
        for seed in range(10):
            pool_config = {"enabled": True, "count": 2, "seed": seed}
            result = select_personas_from_pool(personas, pool_config)
            results.append(frozenset(p["id"] for p in result))

        # At least one different combination should exist
        assert len(set(results)) > 1, "All seeds produced same result (unlikely but possible)"

    def test_backward_compatibility_empty_pool_config(self, personas: list[dict[str, str]]) -> None:
        """Test backward compatibility with empty pool config dict."""
        pool_config = {}  # Empty dict
        result = select_personas_from_pool(personas, pool_config)

        # Should return all personas (enabled defaults to False)
        assert result == personas


class TestPersonaPoolConfig:
    """Test PersonaPoolConfig model."""

    def test_persona_pool_config_creation(self) -> None:
        """Test creating a valid PersonaPoolConfig."""
        pool_config = PersonaPoolConfig(enabled=True, count=2, seed=42)
        assert pool_config.enabled is True
        assert pool_config.count == 2
        assert pool_config.seed == 42

    def test_persona_pool_config_defaults(self) -> None:
        """Test PersonaPoolConfig default values."""
        pool_config = PersonaPoolConfig()
        assert pool_config.enabled is False
        assert pool_config.count == 2
        assert pool_config.seed is None

    def test_persona_pool_config_count_validation(self) -> None:
        """Test that count must be >= 1."""
        with pytest.raises(Exception):  # ValidationError
            PersonaPoolConfig(count=0)


class TestConfigWithPersonaPool:
    """Test Config with persona_pool field."""

    def test_config_with_persona_pool(self) -> None:
        """Test Config with persona pool enabled."""
        config = Config(
            personas=[
                PersonaConfig(
                    id="zundamon",
                    name="ずんだもん",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
                ),
                PersonaConfig(
                    id="metan",
                    name="四国めたん",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=2),
                ),
                PersonaConfig(
                    id="tsumugi",
                    name="春日部つむぎ",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=8),
                ),
            ],
            persona_pool=PersonaPoolConfig(enabled=True, count=2),
        )
        assert config.persona_pool is not None
        assert config.persona_pool.enabled is True
        assert config.persona_pool.count == 2
        assert len(config.personas) == 3

    def test_config_without_persona_pool(self) -> None:
        """Test Config without persona_pool (backward compatible)."""
        config = Config(
            personas=[
                PersonaConfig(
                    id="alice",
                    name="Alice",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
                ),
            ]
        )
        assert config.persona_pool is None

    def test_config_persona_pool_disabled(self) -> None:
        """Test Config with persona_pool explicitly disabled."""
        config = Config(
            personas=[
                PersonaConfig(
                    id="alice",
                    name="Alice",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
                ),
            ],
            persona_pool=PersonaPoolConfig(enabled=False),
        )
        assert config.persona_pool is not None
        assert config.persona_pool.enabled is False


class TestPersonaPoolE2E:
    """E2E tests for persona pool functionality."""

    def test_web_ui_config_loads_with_persona_pool(self) -> None:
        """Test that Web UI config with persona pool loads correctly."""
        from pathlib import Path

        from movie_generator.config import load_config

        config_path = Path("web/config/config.yaml")
        if not config_path.exists():
            pytest.skip("Web UI config not found")

        config = load_config(config_path)

        # Verify persona pool is configured
        assert config.persona_pool is not None
        assert config.persona_pool.enabled is True
        assert config.persona_pool.count == 2
        assert config.persona_pool.seed is None

        # Verify 3 personas are defined
        assert len(config.personas) == 3
        persona_ids = {p.id for p in config.personas}
        assert persona_ids == {"zundamon", "metan", "tsumugi"}

    def test_persona_pool_integration_with_selection(self) -> None:
        """Test full integration: config -> persona selection."""
        config = Config(
            personas=[
                PersonaConfig(
                    id="alice",
                    name="Alice",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
                ),
                PersonaConfig(
                    id="bob",
                    name="Bob",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=2),
                ),
                PersonaConfig(
                    id="charlie",
                    name="Charlie",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
                ),
            ],
            persona_pool=PersonaPoolConfig(enabled=True, count=2, seed=42),
        )

        # Convert personas for selection
        personas_for_script = [
            p.model_dump(include={"id", "name", "character"}) for p in config.personas
        ]

        # Perform selection
        assert config.persona_pool is not None
        pool_config = config.persona_pool.model_dump()
        selected = select_personas_from_pool(personas_for_script, pool_config)

        assert len(selected) == 2
        assert all(p["id"] in {"alice", "bob", "charlie"} for p in selected)
