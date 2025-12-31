"""Tests for TypeScript template generation with transitions."""

from movie_generator.video.templates import get_video_generator_tsx


def test_template_includes_transition_imports():
    """Test that the template includes all required transition imports."""
    template = get_video_generator_tsx()

    # Check for TransitionSeries import
    assert (
        "import { TransitionSeries, springTiming, linearTiming } from '@remotion/transitions'"
        in template
    )

    # Check for transition presentation imports
    assert "import { fade } from '@remotion/transitions/fade'" in template
    assert "import { slide } from '@remotion/transitions/slide'" in template
    assert "import { wipe } from '@remotion/transitions/wipe'" in template
    assert "import { flip } from '@remotion/transitions/flip'" in template
    assert "import { clockWipe } from '@remotion/transitions/clock-wipe'" in template
    assert "import { none } from '@remotion/transitions/none'" in template


def test_template_includes_composition_data_import():
    """Test that the template imports composition data for config."""
    template = get_video_generator_tsx()
    assert "import compositionData from '../composition.json'" in template


def test_template_includes_transition_helper_functions():
    """Test that helper functions for transitions are defined."""
    template = get_video_generator_tsx()

    assert "getTransitionPresentation" in template
    assert "getTransitionTiming" in template
    assert "case 'fade':" in template
    assert "case 'slide':" in template
    assert "case 'wipe':" in template
    assert "case 'flip':" in template
    assert "case 'clockWipe':" in template
    assert "case 'none':" in template


def test_template_uses_transition_series():
    """Test that the VideoGenerator uses TransitionSeries."""
    template = get_video_generator_tsx()

    assert "<TransitionSeries>" in template
    assert "<TransitionSeries.Sequence" in template
    assert "<TransitionSeries.Transition" in template
    assert "presentation={presentation}" in template
    assert "timing={timing}" in template


def test_template_reads_config_from_composition_json():
    """Test that the template reads transition config from composition.json."""
    template = get_video_generator_tsx()

    assert "compositionData as any).transition?.type" in template
    assert "compositionData as any).transition?.duration_frames" in template
    assert "compositionData as any).transition?.timing" in template


def test_calculate_total_frames_uses_audio_duration():
    """Test that calculateTotalFrames uses audio duration for complete playback."""
    template = get_video_generator_tsx()

    # Check that the function uses the last scene's end frame (audio duration)
    # This ensures all audio plays completely, even when slides overlap during transitions
    assert "const scenes = getScenesWithTiming(phrases)" in template
    assert "return scenes[scenes.length - 1].endFrame" in template
    # Verify the comment explains the reasoning
    assert "total duration must match the audio duration" in template


def test_template_parameters_are_documented():
    """Test that template function parameters are properly documented."""
    # The function signature should still accept parameters even though config comes from JSON
    import inspect

    from movie_generator.video.templates import get_video_generator_tsx

    sig = inspect.signature(get_video_generator_tsx)
    params = list(sig.parameters.keys())

    assert "transition_type" in params
    assert "transition_duration" in params
    assert "transition_timing" in params
