import React from 'react';
import { Composition } from 'remotion';
import { Main } from './Main';
import defaultProps from './props.json';

export const Root = () => {
  return (
    <Composition
      id="LocosMaterosCommercial"
      component={Main}
      durationInFrames={defaultProps.format.duration_in_frames || 700}
      fps={defaultProps.format.fps || 24}
      width={defaultProps.format.width || 720}
      height={defaultProps.format.height || 1280}
      defaultProps={defaultProps}
    />
  );
};
