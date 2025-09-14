import React, { useRef, useEffect } from 'react';
import { Camera } from '../types';
import { useTouchGestures } from '../hooks/useTouchGestures';
import './FullscreenViewer.css';

interface FullscreenViewerProps {
  camera: Camera;
  onExit: () => void;
}

export const FullscreenViewer: React.FC<FullscreenViewerProps> = ({
  camera,
  onExit
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useTouchGestures(containerRef, {
    onDoubleClick: onExit
  });

  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onExit();
      }
    };

    // Lock screen orientation on mobile if possible
    const lockOrientation = async () => {
      try {
        if (screen.orientation && screen.orientation.lock) {
          await screen.orientation.lock('landscape');
        }
      } catch (error) {
        // Orientation lock not supported or failed
        console.log('Could not lock orientation:', error);
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    lockOrientation();

    // Prevent scrolling on the body
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
      document.body.style.overflow = '';
      
      // Unlock orientation
      try {
        if (screen.orientation && screen.orientation.unlock) {
          screen.orientation.unlock();
        }
      } catch (error) {
        // Orientation unlock not supported
      }
    };
  }, [onExit]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const loadStream = async () => {
      try {
        if (camera.status === 'live') {
          // Load HLS stream for fullscreen viewing
          video.src = camera.hlsUrl;
          await video.play();
        }
      } catch (error) {
        console.error(`Failed to load fullscreen stream for ${camera.name}:`, error);
      }
    };

    loadStream();
  }, [camera]);

  const getStatusIcon = (status: Camera['status']) => {
    switch (status) {
      case 'live':
        return '🟢';
      case 'connecting':
        return '🟡';
      case 'offline':
        return '🔴';
      case 'error':
        return '⚠️';
      default:
        return '⚪';
    }
  };

  return (
    <div ref={containerRef} className="fullscreen-viewer">
      {/* Header */}
      <div className="fullscreen-header">
        <div className="camera-info">
          <h1 className="camera-title">{camera.name}</h1>
          <span className="camera-ip">{camera.ip}</span>
        </div>
        <button 
          className="exit-button"
          onClick={onExit}
          aria-label="Exit fullscreen"
        >
          ×
        </button>
      </div>

      {/* Video Content */}
      <div className="fullscreen-content">
        {camera.status === 'live' ? (
          <video
            ref={videoRef}
            className="fullscreen-video"
            autoPlay
            muted
            playsInline
            controls
          >
            <source src={camera.hlsUrl} type="application/x-mpegURL" />
            Your browser does not support video playback.
          </video>
        ) : (
          <div className={`fullscreen-placeholder placeholder-${camera.status}`}>
            <div className="placeholder-content">
              <div className="placeholder-icon">
                {camera.status === 'connecting' ? (
                  <div className="spinner"></div>
                ) : (
                  <span>{getStatusIcon(camera.status)}</span>
                )}
              </div>
              <div className="placeholder-text">
                {camera.status === 'connecting' ? 'Connecting to camera...' : 
                 camera.status === 'offline' ? 'Camera offline' :
                 camera.status === 'error' ? 'Connection error' : 'Unknown status'}
              </div>
              <div className="placeholder-hint">
                Double-tap to return to grid view
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="fullscreen-footer">
        <div className="status-info">
          <span className={`status-indicator status-${camera.status}`}>
            {getStatusIcon(camera.status)} {camera.status.toUpperCase()}
          </span>
          {camera.lastSeen && (
            <span className="last-seen">
              Last seen: {new Date(camera.lastSeen).toLocaleTimeString()}
            </span>
          )}
        </div>
        
        <div className="controls">
          {/* Volume, settings, etc. could go here */}
          <span className="exit-hint">Double-tap to exit</span>
        </div>
      </div>

      {/* Touch instructions overlay */}
      <div className="touch-instructions">
        <div className="instruction-text">Double-tap to exit fullscreen</div>
      </div>
    </div>
  );
};
