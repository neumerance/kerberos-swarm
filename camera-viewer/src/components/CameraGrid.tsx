import React from 'react';
import { Camera, Layout } from '../types';
import { CameraTile } from './CameraTile';
import './CameraGrid.css';

interface CameraGridProps {
  cameras: Camera[];
  layout: Layout;
  onCameraDoubleClick: (camera: Camera) => void;
}

export const CameraGrid: React.FC<CameraGridProps> = ({
  cameras,
  layout,
  onCameraDoubleClick
}) => {
  const gridStyle = {
    '--grid-columns': layout.columns,
    '--is-mobile': layout.isMobile ? '1' : '0',
    '--is-portrait': layout.isPortrait ? '1' : '0'
  } as React.CSSProperties;

  return (
    <div className="camera-grid-container">
      <div className="camera-grid" style={gridStyle}>
        {cameras.map((camera) => (
          <CameraTile
            key={camera.id}
            camera={camera}
            onDoubleClick={onCameraDoubleClick}
            className={`grid-item grid-${layout.columns}-col`}
          />
        ))}
      </div>
      
      {cameras.length === 0 && (
        <div className="empty-grid">
          <div className="empty-icon">📹</div>
          <div className="empty-text">No cameras configured</div>
          <div className="empty-hint">
            Check your configuration file and ensure cameras are accessible
          </div>
        </div>
      )}
    </div>
  );
};
