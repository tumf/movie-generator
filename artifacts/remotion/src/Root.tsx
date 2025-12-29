import React from 'react';
import { Composition } from 'remotion';
import { VideoGenerator, calculateTotalFrames } from './VideoGenerator';

// Sample data for development - will be replaced by Python-generated data
const samplePhrases = [
  {
    id: "001",
    subtitle: "Sample subtitle text",
    slide: "sample.png",
    audioFile: "sample.wav",
    duration: 3.0,
    section: "intro"
  }
];

export const RemotionRoot: React.FC = () => {
  const totalFrames = calculateTotalFrames(samplePhrases);

  return (
    <>
      <Composition
        id="Sample"
        component={VideoGenerator}
        durationInFrames={totalFrames}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          projectName: "sample",
          phrases: samplePhrases
        }}
      />
    </>
  );
};
