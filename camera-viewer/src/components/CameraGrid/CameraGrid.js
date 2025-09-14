import React, { useState } from 'react';
import CameraTile from '../CameraTile/CameraTile';
import FullscreenViewer from '../FullscreenViewer/FullscreenViewer';
import { useResponsiveLayout } from '../../hooks/useResponsiveLayout';
import './CameraGrid.css';

const CameraGrid = ({ cameras }) => {
  const [fullscreenCamera, setFullscreenCamera] = useState(null);
  const layout = useResponsiveLayout();

  const handleCameraDoubleClick = (camera) => {
    setFullscreenCamera(camera);
  };

  const handleExitFullscreen = () => {
    setFullscreenCamera(null);
  };

  if (fullscreenCamera) {
    return (
      <FullscreenViewer
        camera={fullscreenCamera}
        onExit={handleExitFullscreen}
      />
    );
  }

  return (
    <div 
      className="camera-grid"
      style={{
        gridTemplateColumns: `repeat(${layout.columns}, 1fr)`
      }}
    >
      {cameras.map((camera) => (
        <CameraTile
          key={camera.id}
          camera={camera}
          onDoubleClick={() => handleCameraDoubleClick(camera)}
        />
      ))}
    </div>
  );
};

export default CameraGrid;
