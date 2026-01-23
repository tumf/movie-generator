"""VOICEVOX audio synthesis integration.

Integrates with VOICEVOX Core for text-to-speech generation.
"""

import wave
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ..constants import ProjectPaths
from ..exceptions import AudioGenerationError, ConfigurationError
from ..script.phrases import Phrase
from ..utils.filesystem import is_valid_file
from .dictionary import PronunciationDictionary

try:
    from . import voicevox_impl  # type: ignore

    VOICEVOX_AVAILABLE = True
except ImportError:
    VOICEVOX_AVAILABLE = False
    voicevox_impl = None


class AudioMetadata(BaseModel):
    """Metadata for generated audio."""

    duration: float  # Duration in seconds
    sample_rate: int = 24000
    channels: int = 1


class VoicevoxSynthesizer:
    """VOICEVOX synthesizer wrapper.

    Integrates VOICEVOX Core with user dictionary support.
    Falls back to placeholder mode if voicevox_core is not available.
    """

    def __init__(
        self,
        speaker_id: int = 3,
        speed_scale: float = 1.0,
        dictionary: PronunciationDictionary | None = None,
        enable_furigana: bool = True,
        pronunciation_model: str = "openai/gpt-4o-mini",
    ) -> None:
        """Initialize synthesizer.

        Args:
            speaker_id: VOICEVOX speaker ID (3=Zundamon).
            speed_scale: Speech speed scale.
            dictionary: Pronunciation dictionary.
            enable_furigana: Enable automatic furigana generation using morphological analysis.
            pronunciation_model: LLM model for pronunciation generation.

        Raises:
            ImportError: If voicevox_core is not installed.
        """
        if not VOICEVOX_AVAILABLE:
            raise ConfigurationError(
                "VOICEVOX Core is not installed and is required for audio synthesis.\n"
                "Please install voicevox_core or see docs/VOICEVOX_SETUP.md for instructions."
            )

        self.speaker_id = speaker_id
        self.speed_scale = speed_scale
        self.dictionary = dictionary or PronunciationDictionary()
        self.enable_furigana = enable_furigana
        self.pronunciation_model = pronunciation_model

        self._synthesizer: Any = None
        self._initialized = False
        self._furigana_generator: Any = None

    def _get_furigana_generator(self) -> Any:
        """Get or create FuriganaGenerator instance.

        Returns:
            FuriganaGenerator instance, or None if furigana is disabled.
        """
        if not self.enable_furigana:
            return None

        if self._furigana_generator is None:
            try:
                from .furigana import FuriganaGenerator

                self._furigana_generator = FuriganaGenerator()
            except ImportError:
                # fugashi not installed, disable furigana
                print("Warning: fugashi not installed, furigana generation disabled.")
                self.enable_furigana = False
                return None

        return self._furigana_generator

    def prepare_phrases(self, phrases: list[Phrase]) -> int:
        """Prepare dictionary entries for all phrases using morphological analysis.

        Should be called before initialize() to ensure all auto-generated
        readings are included in the user dictionary.

        Note: This method does NOT use LLM for unknown words. Use
        prepare_phrases_with_llm() for LLM-based pronunciation generation.

        Args:
            phrases: List of phrases to analyze.

        Returns:
            Number of dictionary entries added.
        """
        generator = self._get_furigana_generator()
        if generator is None:
            return 0

        # Collect all texts
        texts = [p.text for p in phrases if p.text and p.text.strip()]

        # Analyze all texts and get combined readings
        readings = generator.analyze_texts(texts)

        # Add to dictionary (manual entries take precedence due to lower priority)
        added = self.dictionary.add_from_morphemes(readings)

        if added > 0:
            print(f"  📚 Added {added} auto-generated pronunciation entries")

        return added

    async def prepare_phrases_with_llm(
        self,
        phrases: list[Phrase],
        model: str,
        api_key: str | None = None,
    ) -> dict[str, str]:
        """Prepare dictionary entries using morphological analysis and LLM.

        First uses morphological analysis to get readings for known words,
        then uses LLM to generate readings for unknown English words.

        Should be called before initialize() to ensure all readings are
        included in the user dictionary.

        Args:
            phrases: List of phrases to analyze.
            api_key: OpenRouter API key (uses env var if not provided).
            model: LLM model to use for pronunciation generation (uses self.pronunciation_model if None).

        Returns:
            Dictionary of {word: reading} pairs that were added.
        """
        generator = self._get_furigana_generator()
        if generator is None:
            return {}

        # Collect all texts
        texts = [p.text for p in phrases if p.text and p.text.strip()]

        return await self._prepare_texts_with_llm_internal(texts, model, api_key)

    def prepare_texts(self, texts: list[str]) -> int:
        """Prepare dictionary entries from texts using morphological analysis.

        Similar to prepare_phrases() but accepts raw text strings instead of Phrase objects.
        Useful for adding pronunciations before phrase splitting.

        Note: This method does NOT use LLM for unknown words. Use
        prepare_texts_with_llm() for LLM-based pronunciation generation.

        Args:
            texts: List of text strings to analyze.

        Returns:
            Number of dictionary entries added.
        """
        generator = self._get_furigana_generator()
        if generator is None:
            return 0

        try:
            # Analyze all texts and get combined readings
            readings = generator.analyze_texts(texts)

            # Add to dictionary (manual entries take precedence due to lower priority)
            added = self.dictionary.add_from_morphemes(readings)

            return added
        except Exception as e:
            # If morphological analysis fails (e.g., MeCab not configured),
            # silently skip and return 0
            print(f"Warning: Morphological analysis failed: {e}")
            return 0

    async def prepare_texts_with_llm(
        self,
        texts: list[str],
        model: str,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> dict[str, str]:
        """Prepare dictionary entries using morphological analysis and LLM.

        First uses morphological analysis to get readings for known words,
        then uses LLM to generate readings for unknown English words.

        Args:
            texts: List of text strings to analyze.
            api_key: OpenRouter API key (uses env var if not provided).
            model: LLM model to use for pronunciation generation (uses self.pronunciation_model if None).
            base_url: LLM API base URL.

        Returns:
            Dictionary of {word: reading} pairs that were added.
        """
        generator = self._get_furigana_generator()
        if generator is None:
            return {}

        return await self._prepare_texts_with_llm_internal(texts, model, api_key, base_url)

    async def _prepare_texts_with_llm_internal(
        self,
        texts: list[str],
        model: str,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> dict[str, str]:
        """Internal implementation for LLM-based pronunciation preparation.

        All words containing non-kana characters (kanji, ASCII letters, etc.)
        are sent to LLM for pronunciation verification/generation with full
        context for accurate reading determination.

        Args:
            texts: List of text strings to analyze.
            api_key: OpenRouter API key.
            model: LLM model to use.

        Returns:
            Dictionary of {word: reading} pairs that were added to the dictionary.
        """
        generator = self._get_furigana_generator()
        if generator is None:
            return {}

        try:
            # Step 1: Get all words needing pronunciation (non-kana words with suggested readings)
            words_needing_pronunciation = generator.get_words_needing_pronunciation(texts)

            if not words_needing_pronunciation:
                return {}

            # Step 2: Use LLM to verify/generate readings with full context
            from .furigana import generate_readings_with_llm

            # Combine all texts as context for LLM
            context = "\n".join(texts)

            print(f"  🔍 Found {len(words_needing_pronunciation)} words needing pronunciation")
            llm_readings = await generate_readings_with_llm(
                words=words_needing_pronunciation,
                context=context,
                model=model,
                api_key=api_key,
                base_url=base_url,
            )

            if not llm_readings:
                # Fallback to morphological analysis readings if LLM fails
                llm_readings = words_needing_pronunciation

            print(f"  🤖 LLM verified/generated readings for {len(llm_readings)} words")

            # Step 3: Add all readings to dictionary and track what was added
            added_readings: dict[str, str] = {}
            for word, reading in llm_readings.items():
                if word not in self.dictionary.entries:
                    success = self.dictionary.add_word(
                        word=word,
                        reading=reading,
                        word_type="COMMON_NOUN",
                        priority=5,
                    )
                    if success:
                        added_readings[word] = reading

            if added_readings:
                print(f"  📚 Added {len(added_readings)} pronunciation entries total")

            return added_readings

        except Exception as e:
            print(f"Warning: Pronunciation preparation failed: {e}")
            return {}

    def initialize(
        self,
        dict_dir: Path,
        model_path: Path,
        onnxruntime_path: Path | None = None,
    ) -> None:
        """Initialize VOICEVOX Core.

        Args:
            dict_dir: Path to OpenJTalk dictionary directory.
            model_path: Path to VOICEVOX model file (.vvm).
            onnxruntime_path: Path to ONNX Runtime library (optional).

        Raises:
            ImportError: If voicevox_core is not available.
            FileNotFoundError: If required files don't exist.
        """
        if not VOICEVOX_AVAILABLE:
            raise ImportError(
                "voicevox_core is not installed. Install it manually or run in placeholder mode."
            )

        # Create user dictionary if we have entries
        user_dict = None
        if self.dictionary.entries:
            user_dict = voicevox_impl.create_user_dict(self.dictionary.entries)  # type: ignore

        # Initialize synthesizer
        self._synthesizer = voicevox_impl.initialize_voicevox(  # type: ignore
            dict_dir=dict_dir,
            model_path=model_path,
            user_dict=user_dict,
            onnxruntime_path=onnxruntime_path,
        )

        self._initialized = True

    def synthesize_phrase(self, phrase: Phrase, output_path: Path) -> AudioMetadata:
        """Synthesize audio for a single phrase.

        Args:
            phrase: Phrase to synthesize.
            output_path: Path to save audio file.

        Returns:
            Audio metadata with duration.

        Raises:
            AudioGenerationError: If synthesizer not initialized or synthesis fails.
        """
        if not self._initialized:
            raise AudioGenerationError("Synthesizer not initialized. Call initialize() first.")

        if not VOICEVOX_AVAILABLE or self._synthesizer is None:
            raise AudioGenerationError("VOICEVOX is not available. Cannot synthesize audio.")

        # Skip empty or whitespace-only text
        if not phrase.text or not phrase.text.strip():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"")
            return AudioMetadata(duration=0.0)

        # Use reading field for synthesis if available, otherwise fallback to text
        synthesis_text = phrase.reading if phrase.reading else phrase.text

        # Synthesize with VOICEVOX
        try:
            duration = voicevox_impl.synthesize_to_file(  # type: ignore
                synthesizer=self._synthesizer,
                text=synthesis_text,
                speaker_id=self.speaker_id,
                output_path=output_path,
                speed_scale=self.speed_scale,
            )
        except Exception as e:
            raise AudioGenerationError(
                f"Failed to synthesize phrase '{phrase.text[:50]}...': {e}"
            ) from e

        return AudioMetadata(duration=duration)

    def synthesize_phrases(
        self, phrases: list[Phrase], output_dir: Path
    ) -> tuple[list[Path], list[AudioMetadata]]:
        """Synthesize audio for multiple phrases.

        Args:
            phrases: List of phrases to synthesize.
            output_dir: Directory to save audio files.

        Returns:
            Tuple of (audio file paths, metadata list).
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_paths: list[Path] = []
        metadata_list: list[AudioMetadata] = []

        for phrase in phrases:
            output_path = output_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
                index=phrase.original_index
            )

            # Skip if audio file already exists and is not empty
            if is_valid_file(output_path):
                try:
                    # Read existing metadata
                    with wave.open(str(output_path), "rb") as wf:
                        frames = wf.getnframes()
                        rate = wf.getframerate()
                        duration = frames / float(rate)
                    metadata = AudioMetadata(duration=duration, sample_rate=rate)
                    phrase.duration = duration
                    print(f"  ↷ Skipping existing audio: {output_path.name}")
                except Exception:
                    # If file is corrupt, regenerate
                    metadata = self.synthesize_phrase(phrase, output_path)
                    phrase.duration = metadata.duration
            else:
                metadata = self.synthesize_phrase(phrase, output_path)
                # Update phrase duration
                phrase.duration = metadata.duration

            audio_paths.append(output_path)
            metadata_list.append(metadata)

        return audio_paths, metadata_list


def create_synthesizer_from_config(config: Any) -> VoicevoxSynthesizer:
    """Create synthesizer from configuration.

    Args:
        config: Configuration object.

    Returns:
        Initialized synthesizer.
    """
    dictionary = PronunciationDictionary()
    if hasattr(config, "pronunciation") and config.pronunciation.custom:
        dictionary.add_from_config(config.pronunciation.custom)

    # Get enable_furigana from config, default to True
    enable_furigana = True
    if hasattr(config, "audio") and hasattr(config.audio, "enable_furigana"):
        enable_furigana = config.audio.enable_furigana

    # Get pronunciation_model from config, default to "openai/gpt-4o-mini"
    pronunciation_model = "openai/gpt-4o-mini"
    if hasattr(config, "audio") and hasattr(config.audio, "pronunciation_model"):
        pronunciation_model = config.audio.pronunciation_model

    return VoicevoxSynthesizer(
        speaker_id=config.audio.speaker_id,
        speed_scale=config.audio.speed_scale,
        dictionary=dictionary,
        enable_furigana=enable_furigana,
        pronunciation_model=pronunciation_model,
    )
