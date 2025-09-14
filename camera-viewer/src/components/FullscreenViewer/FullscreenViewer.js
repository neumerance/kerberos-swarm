import React from 'react';
import { useTouchGestures } from '../../hooks/useTouchGestures';
import './FullscreenViewer.css';

const FullscreenViewer = ({ camera, onExit }) => {
  const viewerRef = React.useRef(null);

  useTouchGestures(viewerRef, onExit);

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

  return (
    <div className="fullscreen-viewer" ref={viewerRef}>
      <div className="fullscreen-header">
        <div className="camera-info">
          <h2>{camera.name}</h2>
          <span className="camera-ip">{camera.ip}</span>
        </div>
        <button className="exit-button" onClick={onExit}>
          ✕
        </button>
      </div>
      
      <div className="fullscreen-video">
        {camera.status === 'live' && camera.hlsUrl ? (
          <video
            src={camera.hlsUrl}
            autoPlay
            muted
            playsInline
            loop
            className="fullscreen-video-element"
          />
        ) : camera.status === 'connecting' ? (
          <div className="fullscreen-placeholder">
            <div className="loading-spinner large"></div>
            <p>Connecting to camera...</p>
          </div>
        ) : (
          <div className="fullscreen-placeholder">
            <div className="offline-icon large">📹</div>
            <p>{camera.status === 'offline' ? 'Camera Offline' : 'Connection Error'}</p>
          </div>
        )}
      </div>
      
      <div className="fullscreen-controls">
        <div className="control-group">
          <button className="control-button">🔊</button>
          <button className="control-button">⚙️</button>
        </div>
        <div className="status-indicator">
          {getStatusIcon()} {camera.status.toUpperCase()}
        </div>
        <div className="fullscreen-hint">
          Double tap to exit fullscreen
        </div>
      </div>
    </div>
  );
};

export default FullscreenViewer;
