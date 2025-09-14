import React, { useState, useEffect } from 'react';
import CameraGrid from './components/CameraGrid/CameraGrid';
import { loadKerberosConfig } from './services/configLoader';
import { startStatusMonitoring } from './services/statusChecker';
import './App.css';

function App() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    let statusCleanup = null;
    
    const loadCameras = async () => {
      try {
        const cameraData = await loadKerberosConfig();
        setCameras(cameraData);
        
        // Start monitoring camera status
        statusCleanup = startStatusMonitoring(cameraData, (updatedCameras) => {
          setCameras(updatedCameras);
        });
        
      } catch (error) {
        console.error('Failed to load camera configuration:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadCameras();
    
    // Cleanup status monitoring when component unmounts
    return () => {
      if (statusCleanup) {
        statusCleanup();
      }
    };
  }, []);
  
  if (loading) {
    return (
      <div className="App">
        <main className="app-main loading">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading cameras...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      <main className="app-main">
        <CameraGrid cameras={cameras} />
      </main>
    </div>
  );
}

export default App;
