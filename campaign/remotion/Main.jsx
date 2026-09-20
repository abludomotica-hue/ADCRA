import React from 'react';
import { Sequence, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

const SceneOverlay = ({ text, style, brand, isLastScene, logoUri }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const translateY = interpolate(frame, [0, 12], [25, 0], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: { damping: 12, mass: 0.5 } });

  if (isLastScene) {
    return (
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 720,
        height: 1280,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'radial-gradient(circle at center, rgba(13, 92, 58, 0.6) 0%, rgba(0, 0, 0, 0.88) 75%)',
        opacity,
        fontFamily: 'sans-serif',
        padding: 40,
        boxSizing: 'border-box'
      }}>
        {logoUri && (
          <div style={{
            width: 210,
            height: 210,
            borderRadius: '50%',
            overflow: 'hidden',
            border: `4px solid ${brand.accent_color}`,
            boxShadow: `0 0 35px ${brand.accent_color}88`,
            marginBottom: 35,
            backgroundColor: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `scale(${scale})`
          }}>
            <img src={logoUri} alt="Logo" style={{ width: '85%', height: '85%', objectFit: 'contain' }} />
          </div>
        )}
        <h1 style={{
          color: '#FFFFFF',
          fontSize: 38,
          fontWeight: 800,
          textAlign: 'center',
          lineHeight: 1.25,
          marginBottom: 25,
          textShadow: '0 4px 18px rgba(0,0,0,0.9)'
        }}>
          ¿Dónde estás tú? <span style={{ color: brand.accent_color }}>Está tu mate.</span>
        </h1>
        <div style={{
          backgroundColor: brand.accent_color,
          color: '#1A1A1A',
          fontSize: 22,
          fontWeight: 800,
          padding: '12px 34px',
          borderRadius: 30,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          boxShadow: '0 6px 20px rgba(0,0,0,0.4)'
        }}>
          {brand.cta_url}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'absolute',
      bottom: 230,
      left: 40,
      right: 40,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      pointerEvents: 'none'
    }}>
      <div style={{
        background: 'rgba(26, 26, 26, 0.85)',
        border: `2px solid ${brand.accent_color}`,
        borderRadius: 24,
        padding: '16px 28px',
        maxWidth: 620,
        textAlign: 'center',
        boxShadow: '0 8px 30px rgba(0,0,0,0.6)',
        opacity,
        transform: `translateY(${translateY}px)`
      }}>
        <span style={{
          color: '#FFFFFF',
          fontSize: 32,
          fontWeight: 600,
          fontFamily: 'sans-serif',
          lineHeight: 1.3,
          textShadow: '0 2px 8px rgba(0,0,0,0.8)'
        }}>
          {text}
        </span>
      </div>
    </div>
  );
};

export const Main = (props) => {
  const { scenes = [], brand = {}, logoUri } = props;

  return (
    <div style={{
      position: 'relative',
      width: 720,
      height: 1280,
      backgroundColor: '#000000',
      overflow: 'hidden'
    }}>
      {scenes.map((sc, index) => {
        const isLast = index === scenes.length - 1;
        return (
          <Sequence
            key={sc.scene_id}
            from={sc.start_frame}
            durationInFrames={sc.duration_frames}
          >
            {/* Background color placeholder simulating video frame */}
            <div style={{
              width: 720,
              height: 1280,
              backgroundColor: index % 2 === 0 ? '#111815' : '#0B1310',
              position: 'relative'
            }}>
              <SceneOverlay
                text={sc.text_overlay}
                style={sc.style}
                brand={brand}
                isLastScene={isLast}
                logoUri={logoUri}
              />
            </div>
          </Sequence>
        );
      })}
    </div>
  );
};
