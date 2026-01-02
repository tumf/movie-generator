import React from 'react';
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
