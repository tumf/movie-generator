import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

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
    startFrame: number;
    endFrame: number;
  }> = [];

  let currentSlide: string | undefined = undefined;
  let currentStart = 0;

  scenes.forEach((scene, index) => {
    if (scene.slideFile !== currentSlide) {
      // Slide changed, save previous group
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
    
    // Last scene
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
  slideFile?: string;
  startFrame: number;
  durationFrames: number;
}> = ({ slideFile, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in/out animation only at slide boundaries
  const fadeInDuration = fps * 0.5; // 0.5 seconds
  const fadeOutDuration = fps * 0.5;
  const opacity = Math.min(
    1,
    frame / fadeInDuration,
    (durationFrames - frame) / fadeOutDuration
  );

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
          opacity,
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
        opacity,
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
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            fontSize: '36px',
            fontFamily: 'Arial, sans-serif',
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

export const VideoGenerator: React.FC<VideoGeneratorProps> = ({ phrases }) => {
  const scenes = getScenesWithTiming(phrases);
  const slideGroups = getSlideGroups(scenes);

  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a1a' }}>
      {/* Slide layer - only changes when slide actually changes */}
      {slideGroups.map((group, index) => (
        <Sequence
          key={`slide-${index}`}
          from={group.startFrame}
          durationInFrames={group.endFrame - group.startFrame}
        >
          <SlideLayer
            slideFile={group.slideFile}
            startFrame={group.startFrame}
            durationFrames={group.endFrame - group.startFrame}
          />
        </Sequence>
      ))}

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
  const totalDuration = phrases.reduce((sum, phrase) => sum + phrase.duration, 0);
  return Math.round(totalDuration * fps);
};
