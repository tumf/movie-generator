import React from 'react';
import { Composition } from 'remotion';
import { VideoGenerator, calculateTotalFrames } from './VideoGenerator';

// Sample data for development - will be replaced by Python-generated data
const samplePhrases = [
  {
    text: "Sample subtitle",
    audioFile: "sample.wav",
    slideFile: "slide1.png",
    duration: 3.0
  }
];

export const RemotionRoot: React.FC = () => {
  const totalFrames = calculateTotalFrames(samplePhrases);

  return (
    <>
      <Composition
        id="VideoGenerator"
        component={VideoGenerator}
        durationInFrames={totalFrames}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          phrases: samplePhrases
        }}
      />
    </>
  );
};
