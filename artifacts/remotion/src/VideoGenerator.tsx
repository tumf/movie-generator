import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

/**
 * Generic Video Generator Component
 * 
 * This component generates videos from structured phrase data.
 * It's designed to be reusable across multiple video projects.
 */

export interface PhraseData {
  id: string;
  subtitle: string;
  slide?: string;
  audioFile: string;
  duration: number;
  section?: string;
}

export interface VideoGeneratorProps {
  projectName: string;
  phrases: PhraseData[];
  style?: VideoStyle;
}

export interface VideoStyle {
  backgroundColor?: string;
  subtitlePosition?: 'top' | 'bottom' | 'middle';
  subtitleFontSize?: number;
  subtitleFontFamily?: string;
  subtitleColor?: string;
  slideTransitionDuration?: number;
  slideFit?: 'contain' | 'cover';
}

const DEFAULT_STYLE: Required<VideoStyle> = {
  backgroundColor: '#1a1a1a',
  subtitlePosition: 'bottom',
  subtitleFontSize: 36,
  subtitleFontFamily: 'Arial, sans-serif',
  subtitleColor: 'white',
  slideTransitionDuration: 0.5,
  slideFit: 'contain',
};

interface Scene {
  id: string;
  audioFile: string;
  subtitle?: string;
  slideFile?: string;
  section?: string;
  startFrame: number;
  durationFrames: number;
  endFrame: number;
}

interface SlideGroup {
  slideFile?: string;
  startFrame: number;
  endFrame: number;
}

const calculateScenes = (phrases: PhraseData[], fps: number): Scene[] => {
  let currentFrame = 0;
  
  return phrases.map(phrase => {
    const durationFrames = Math.round(phrase.duration * fps);
    const scene: Scene = {
      id: phrase.id,
      audioFile: phrase.audioFile,
      subtitle: phrase.subtitle,
      slideFile: phrase.slide,
      section: phrase.section,
      startFrame: currentFrame,
      durationFrames,
      endFrame: currentFrame + durationFrames,
    };
    currentFrame += durationFrames;
    return scene;
  });
};

const groupSlides = (scenes: Scene[]): SlideGroup[] => {
  const groups: SlideGroup[] = [];
  let currentSlide: string | undefined = undefined;
  let currentStart = 0;

  scenes.forEach((scene, index) => {
    if (scene.slideFile !== currentSlide) {
      if (index > 0) {
        groups.push({
          slideFile: currentSlide,
          startFrame: currentStart,
          endFrame: scene.startFrame,
        });
      }
      currentSlide = scene.slideFile;
      currentStart = scene.startFrame;
    }
    
    if (index === scenes.length - 1) {
      groups.push({
        slideFile: currentSlide,
        startFrame: currentStart,
        endFrame: scene.endFrame,
      });
    }
  });

  return groups;
};

const SlideLayer: React.FC<{
  projectName: string;
  slideFile?: string;
  durationFrames: number;
  style: Required<VideoStyle>;
}> = ({ projectName, slideFile, durationFrames, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeInDuration = fps * style.slideTransitionDuration;
  const fadeOutDuration = fps * style.slideTransitionDuration;
  const opacity = Math.min(
    1,
    frame / fadeInDuration,
    (durationFrames - frame) / fadeOutDuration
  );

  if (!slideFile) {
    return null;
  }

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        opacity,
      }}
    >
      <div style={{ width: '80%', height: '80%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Img
          src={staticFile(`projects/${projectName}/slides/${slideFile}`)}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: style.slideFit,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

const AudioSubtitleLayer: React.FC<{
  projectName: string;
  audioFile: string;
  subtitle?: string;
  style: Required<VideoStyle>;
}> = ({ projectName, audioFile, subtitle, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeInDuration = fps * 0.3;
  const opacity = Math.min(1, frame / fadeInDuration);

  const subtitlePositionStyle = (() => {
    switch (style.subtitlePosition) {
      case 'top':
        return { top: '30px' };
      case 'middle':
        return { top: '50%', transform: 'translate(-50%, -50%)' };
      case 'bottom':
      default:
        return { bottom: '30px', transform: 'translateX(-50%)' };
    }
  })();

  return (
    <>
      <Audio src={staticFile(`projects/${projectName}/audio/${audioFile}`)} />
      
      {subtitle && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            ...subtitlePositionStyle,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: style.subtitleColor,
            fontSize: `${style.subtitleFontSize}px`,
            fontFamily: style.subtitleFontFamily,
            padding: '20px 40px',
            borderRadius: '10px',
            maxWidth: '80%',
            textAlign: 'center',
            lineHeight: '1.4',
            opacity,
          }}
        >
          {subtitle}
        </div>
      )}
    </>
  );
};

export const VideoGenerator: React.FC<VideoGeneratorProps> = ({ 
  projectName, 
  phrases,
  style: customStyle = {}
}) => {
  const { fps } = useVideoConfig();
  const style = { ...DEFAULT_STYLE, ...customStyle };
  
  const scenes = calculateScenes(phrases, fps);
  const slideGroups = groupSlides(scenes);

  return (
    <AbsoluteFill style={{ backgroundColor: style.backgroundColor }}>
      {slideGroups.map((group, index) => (
        <Sequence
          key={`slide-${index}`}
          from={group.startFrame}
          durationInFrames={group.endFrame - group.startFrame}
        >
          <SlideLayer
            projectName={projectName}
            slideFile={group.slideFile}
            durationFrames={group.endFrame - group.startFrame}
            style={style}
          />
        </Sequence>
      ))}

      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          <AudioSubtitleLayer
            projectName={projectName}
            audioFile={scene.audioFile}
            subtitle={scene.subtitle}
            style={style}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const calculateTotalFrames = (phrases: PhraseData[], fps: number = 30): number => {
  const totalDuration = phrases.reduce((sum, phrase) => sum + phrase.duration, 0);
  return Math.round(totalDuration * fps);
};
