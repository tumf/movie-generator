"""TypeScript/React templates for Remotion video generation.

This module contains template strings for generating Remotion project files.
Each template is a Python string that can be formatted with project-specific data.
"""

from typing import Any


def get_video_generator_tsx(
    transition_type: str = "fade",
    transition_duration: int = 15,
    transition_timing: str = "linear",
) -> str:
    """Generate VideoGenerator.tsx component template with TransitionSeries.

    This component handles:
    - Phrase timing calculation
    - Slide grouping (consecutive phrases with same slide)
    - Transitions between slides using @remotion/transitions
    - Audio and subtitle synchronization

    Args:
        transition_type: Type of transition (fade, slide, wipe, flip, clockWipe, none).
        transition_duration: Transition duration in frames.
        transition_timing: Timing function (linear, spring).

    Note:
        Uses TransitionSeries from @remotion/transitions for smooth transitions.
        Configuration is read from composition.json at runtime.
    """
    return """import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { TransitionSeries, springTiming, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';
import { wipe } from '@remotion/transitions/wipe';
import { flip } from '@remotion/transitions/flip';
import { clockWipe } from '@remotion/transitions/clock-wipe';
import { none } from '@remotion/transitions/none';
import compositionData from '../composition.json';

// Type definition for phrase metadata
export interface PhraseData {
  text: string;
  audioFile: string;
  slideFile?: string;
  duration: number;
}

// Props interface
export interface VideoGeneratorProps {
  phrases: PhraseData[];
}

// Calculate timing for each phrase
const getScenesWithTiming = (phrases: PhraseData[]) => {
  let currentFrame = 0;
  const fps = 30;
  
  return phrases.map((phrase, index) => {
    const durationFrames = Math.round(phrase.duration * fps);
    const scene = {
      id: `phrase-${index}`,
      audioFile: phrase.audioFile,
      subtitle: phrase.text,
      slideFile: phrase.slideFile,
      startFrame: currentFrame,
      durationFrames,
      endFrame: currentFrame + durationFrames,
    };
    currentFrame += durationFrames;
    return scene;
  });
};

// Helper to group consecutive scenes with the same slide
const getSlideGroups = (scenes: ReturnType<typeof getScenesWithTiming>) => {
  const groups: Array<{
    slideFile?: string;
    scenes: ReturnType<typeof getScenesWithTiming>;
    durationFrames: number;
  }> = [];

  let currentSlide: string | undefined = undefined;
  let currentScenes: typeof scenes = [];

  scenes.forEach((scene, index) => {
    if (scene.slideFile !== currentSlide) {
      // Slide changed, save previous group
      if (index > 0 && currentScenes.length > 0) {
        const duration = currentScenes.reduce((sum, s) => sum + s.durationFrames, 0);
        groups.push({
          slideFile: currentSlide,
          scenes: currentScenes,
          durationFrames: duration,
        });
        currentScenes = [];
      }
      currentSlide = scene.slideFile;
    }
    currentScenes.push(scene);
    
    // Last scene
    if (index === scenes.length - 1) {
      const duration = currentScenes.reduce((sum, s) => sum + s.durationFrames, 0);
      groups.push({
        slideFile: currentSlide,
        scenes: currentScenes,
        durationFrames: duration,
      });
    }
  });

  return groups;
};

// Get transition presentation based on type
const getTransitionPresentation = (type: string) => {
  switch (type) {
    case 'fade':
      return fade();
    case 'slide':
      return slide();
    case 'wipe':
      return wipe();
    case 'flip':
      return flip();
    case 'clockWipe':
      return clockWipe();
    case 'none':
      return none();
    default:
      return fade();
  }
};

// Get transition timing based on configuration
const getTransitionTiming = (timing: string, durationInFrames: number) => {
  if (timing === 'spring') {
    return springTiming({ config: { damping: 200 } });
  }
  return linearTiming({ durationInFrames });
};

const SlideLayer: React.FC<{
  slideFile?: string;
}> = ({ slideFile }) => {
  if (!slideFile) {
    return (
      <AbsoluteFill
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '48px',
          fontFamily: 'Arial, sans-serif',
        }}
      >
        <div>Movie Generator</div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div style={{ width: '80%', height: '80%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Img
          src={staticFile(slideFile)}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

const AudioSubtitleLayer: React.FC<{
  audioFile: string;
  subtitle?: string;
}> = ({ audioFile, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Subtle fade for subtitles only
  const fadeInDuration = fps * 0.3;
  const opacity = Math.min(1, frame / fadeInDuration);

  return (
    <>
      <Audio src={staticFile(audioFile)} />
      
      {subtitle && (
        <div
          style={{
            position: 'absolute',
            bottom: '30px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            color: 'white',
            fontSize: '36px',
            fontFamily: 'Arial, sans-serif',
            fontWeight: 'bold',
            padding: '20px 40px',
            borderRadius: '10px',
            width: '80%',
            textAlign: 'center',
            lineHeight: '1.4',
            opacity,
            WebkitTextStroke: '1.5px #8FCF4F',
            textShadow: '0 0 10px rgba(0, 0, 0, 0.8)',
          }}
        >
          {subtitle}
        </div>
      )}
    </>
  );
};

export const VideoGenerator: React.FC<VideoGeneratorProps> = ({ phrases }) => {
  const scenes = getScenesWithTiming(phrases);
  const slideGroups = getSlideGroups(scenes);
  const { fps } = useVideoConfig();

  // Get transition configuration from composition data
  const transitionType = (compositionData as any).transition?.type || 'fade';
  const transitionDuration = (compositionData as any).transition?.duration_frames || 15;
  const transitionTiming = (compositionData as any).transition?.timing || 'linear';

  const presentation = getTransitionPresentation(transitionType);
  const timing = getTransitionTiming(transitionTiming, transitionDuration);

  // Calculate actual transition duration for slide sequences
  const transitionDurationFrames = timing.getDurationInFrames({ fps });

  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a1a' }}>
      {/* TransitionSeries for slides */}
      <TransitionSeries>
        {slideGroups.map((group, index) => (
          <React.Fragment key={`slide-${index}`}>
            <TransitionSeries.Sequence durationInFrames={group.durationFrames}>
              <SlideLayer slideFile={group.slideFile} />
            </TransitionSeries.Sequence>
            {/* Add transition between slides, but not after the last slide */}
            {index < slideGroups.length - 1 && (
              <TransitionSeries.Transition
                presentation={presentation}
                timing={timing}
              />
            )}
          </React.Fragment>
        ))}
      </TransitionSeries>

      {/* Audio and subtitle layer - changes with each phrase */}
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          <AudioSubtitleLayer
            audioFile={scene.audioFile}
            subtitle={scene.subtitle}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

// Calculate total frames for the composition
export const calculateTotalFrames = (phrases: PhraseData[]): number => {
  const fps = 30;
  const scenes = getScenesWithTiming(phrases);
  const slideGroups = getSlideGroups(scenes);
  
  // Get transition configuration
  const transitionTiming = (compositionData as any).transition?.timing || 'linear';
  const transitionDuration = (compositionData as any).transition?.duration_frames || 15;
  const timing = getTransitionTiming(transitionTiming, transitionDuration);
  const transitionDurationFrames = timing.getDurationInFrames({ fps });
  
  // Calculate total: sum of all slide durations minus transition overlaps
  const totalSlideFrames = slideGroups.reduce((sum, group) => sum + group.durationFrames, 0);
  const numTransitions = Math.max(0, slideGroups.length - 1);
  const totalTransitionOverlap = numTransitions * transitionDurationFrames;
  
  return totalSlideFrames - totalTransitionOverlap;
};
"""


def get_root_tsx() -> str:
    """Generate Root.tsx component template.

    This component reads composition.json and creates the Remotion composition.
    """
    return """import React from 'react';
import { Composition } from 'remotion';
import { VideoGenerator, calculateTotalFrames } from './VideoGenerator';
import compositionData from '../composition.json';

export const RemotionRoot: React.FC = () => {
  const totalFrames = calculateTotalFrames(compositionData.phrases);

  return (
    <>
      <Composition
        id="VideoGenerator"
        component={VideoGenerator}
        durationInFrames={totalFrames}
        fps={compositionData.fps}
        width={compositionData.width}
        height={compositionData.height}
        defaultProps={{
          phrases: compositionData.phrases
        }}
      />
    </>
  );
};
"""


def get_remotion_config_ts() -> str:
    """Generate remotion.config.ts template."""
    return """import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
"""


def get_package_json(project_name: str) -> dict[str, Any]:
    """Generate package.json for a Remotion project.

    Args:
        project_name: Name of the project (used for package name)

    Returns:
        Dictionary representing package.json content
    """
    return {
        "name": f"@projects/{project_name}",
        "version": "1.0.0",
        "private": True,
        "scripts": {"render": "remotion render VideoGenerator ../output.mp4"},
        "dependencies": {},
        "devDependencies": {},
    }


def get_index_ts() -> str:
    """Generate index.ts entry point."""
    return """import { registerRoot } from 'remotion';
import { RemotionRoot } from './Root';

registerRoot(RemotionRoot);
"""


def get_tsconfig_json() -> dict[str, Any]:
    """Generate tsconfig.json for TypeScript configuration."""
    return {
        "compilerOptions": {
            "target": "ES2022",
            "lib": ["DOM", "DOM.Iterable", "ES2022"],
            "jsx": "react-jsx",
            "module": "ES2022",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "allowJs": True,
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True,
        },
        "include": ["src/**/*"],
        "exclude": ["node_modules"],
    }
