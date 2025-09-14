import React from 'react';
import { useTouchGestures } from '../../hooks/useTouchGestures';
import './CameraTile.css';

const CameraTile = ({ camera, onDoubleClick }) => {
  const tileRef = React.useRef(null);

  useTouchGestures(tileRef, onDoubleClick);

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
    >
      <div className="camera-header">
        <span className="camera-name">{camera.name}</span>
        <span className="camera-status">
          {getStatusIcon()} {getStatusText()}
        </span>
      </div>
      
      <div className="camera-video">
        {camera.status === 'live' && camera.hlsUrl ? (
          <video
            src={camera.hlsUrl}
            autoPlay
            muted
            playsInline
            loop
            className="video-element"
          />
        ) : camera.status === 'connecting' ? (
          <div className="loading-placeholder">
            <div className="loading-spinner"></div>
            <p>Connecting...</p>
          </div>
        ) : (
          <div className="offline-placeholder">
            <div className="offline-icon">📹</div>
            <p>{camera.status === 'offline' ? 'Camera Offline' : 'Connection Error'}</p>
          </div>
        )}
      </div>
      
      <div className="camera-info">
        <span className="camera-ip">{camera.ip}</span>
        <span className="double-tap-hint">Double tap for fullscreen</span>
      </div>
    </div>
  );
};

export default CameraTile;
