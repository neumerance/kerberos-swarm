import React, { useRef, useEffect } from 'react';
import { Camera } from '../types';
import { useTouchGestures } from '../hooks/useTouchGestures';
import './CameraTile.css';

interface CameraTileProps {
  camera: Camera;
  onDoubleClick: (camera: Camera) => void;
  className?: string;
}

export const CameraTile: React.FC<CameraTileProps> = ({
  camera,
  onDoubleClick,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useTouchGestures(containerRef, {
    onDoubleClick: () => onDoubleClick(camera)
  });

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // Configure video for mobile optimization
    video.muted = true; // Required for autoplay on mobile
    video.playsInline = true; // Prevent fullscreen on iOS
    video.preload = 'metadata';

    const loadStream = async () => {
      try {
        if (camera.status === 'live') {
          // In a real implementation, you would load the HLS stream here
          // For now, we'll use a placeholder
          video.poster = `data:image/svg+xml;base64,${btoa(generatePlaceholder(camera))}`;
        }
      } catch (error) {
        console.error(`Failed to load stream for ${camera.name}:`, error);
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

  const getStatusText = (status: Camera['status']) => {
    switch (status) {
      case 'live':
        return 'LIVE';
      case 'connecting':
        return 'CONNECTING';
      case 'offline':
        return 'OFFLINE';
      case 'error':
        return 'ERROR';
      default:
        return 'UNKNOWN';
    }
  };

  return (
    <div
      ref={containerRef}
      className={`camera-tile ${className}`}
      data-camera-id={camera.id}
    >
      <div className="camera-header">
        <h3 className="camera-name">{camera.name}</h3>
        <div className={`status status-${camera.status}`}>
          <span className="status-icon">{getStatusIcon(camera.status)}</span>
          <span className="status-text">{getStatusText(camera.status)}</span>
        </div>
      </div>

      <div className="video-container">
        {camera.status === 'live' ? (
          <video
            ref={videoRef}
            className="camera-video"
            autoPlay
            muted
            playsInline
            loop
          >
            <source src={camera.hlsUrl} type="application/x-mpegURL" />
            Your browser does not support video playback.
          </video>
        ) : (
          <div className={`placeholder placeholder-${camera.status}`}>
            <div className="placeholder-icon">
              {camera.status === 'connecting' ? (
                <div className="spinner"></div>
              ) : (
                <span>{getStatusIcon(camera.status)}</span>
              )}
            </div>
            <div className="placeholder-text">
              {camera.status === 'connecting' ? 'Connecting...' : getStatusText(camera.status)}
            </div>
          </div>
        )}
      </div>

      <div className="camera-info">
        <span className="camera-ip">{camera.ip}</span>
        {camera.lastSeen && (
          <span className="last-seen">
            Last seen: {new Date(camera.lastSeen).toLocaleTimeString()}
          </span>
        )}
      </div>

      <div className="touch-hint">
        <span>Double-tap for fullscreen</span>
      </div>
    </div>
  );
};

const generatePlaceholder = (camera: Camera): string => {
  return `
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
      <rect width="400" height="300" fill="#1a1a1a"/>
      <text x="200" y="150" font-family="Arial, sans-serif" font-size="18" 
            fill="#ffffff" text-anchor="middle" dominant-baseline="middle">
        ${camera.name}
      </text>
      <text x="200" y="180" font-family="Arial, sans-serif" font-size="14" 
            fill="#666666" text-anchor="middle" dominant-baseline="middle">
        ${camera.ip}
      </text>
    </svg>
  `;
};
