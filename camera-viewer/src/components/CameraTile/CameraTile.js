import React from 'react';
import { useTouchGestures } from '../../hooks/useTouchGestures';
import './CameraTile.css';

const CameraTile = ({ camera, onDoubleClick }) => {
  const tileRef = React.useRef(null);

  // Add debugging for double-click
  const handleDoubleClick = () => {
    console.log('Double-click detected on camera:', camera.name);
    onDoubleClick && onDoubleClick();
  };

  useTouchGestures(tileRef, handleDoubleClick);

  const getStatusIcon = () => {
    switch (camera.status) {
      case 'live':
        return '🟢';
      case 'connecting':
        return '🟡';
      case 'offline':
        return '🔴';
      case 'error':
        return '⚠️';
      default:
        return '⚫';
    }
  };

  const getStatusText = () => {
    switch (camera.status) {
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
      ref={tileRef}
      className={`camera-tile ${camera.status}`}
      onDoubleClick={handleDoubleClick}
      style={{ cursor: 'pointer' }}
      title="Double-click to view fullscreen"
    >
      <div className="camera-header">
        <span className="camera-name">{camera.name}</span>
        <span className="camera-status">
          {getStatusIcon()} {getStatusText()}
        </span>
      </div>
      
      <div className="camera-video">
        {camera.status === 'live' && (camera.hlsUrl || camera.streamUrl) ? (
          <video
            autoPlay
            muted
            playsInline
            className="video-element"
            onError={(e) => {
              console.error(`Video error for ${camera.name}:`, e);
              // Could implement retry logic or status updates here
            }}
          >
            {/* Try HLS stream first for better mobile support */}
            {camera.hlsUrl && <source src={camera.hlsUrl} type="application/x-mpegURL" />}
            {camera.streamUrl && <source src={camera.streamUrl} type="video/mp4" />}
            {/* Fallback RTMP for direct stream if available */}
            {camera.rtmpUrl && <source src={camera.rtmpUrl} type="rtmp/mp4" />}
            Your browser does not support the video tag.
          </video>
        ) : camera.status === 'connecting' ? (
          <div className="loading-placeholder">
            <div className="loading-spinner"></div>
          </div>
        ) : (
          <div className="offline-placeholder">
            <div className="offline-icon">📹</div>
          </div>
        )}
      </div>
      
      <div className="camera-info">
        <span className="double-tap-hint">Double tap for fullscreen</span>
      </div>
    </div>
  );
};

export default CameraTile;
