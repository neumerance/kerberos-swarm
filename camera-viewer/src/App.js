import React, { useState, useEffect } from 'react';
import CameraGrid from './components/CameraGrid/CameraGrid';
import { loadKerberosConfig } from './services/configLoader';
import { startStatusMonitoring } from './services/statusChecker';
import './App.css';

function App() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let statusCleanup = null;
    
    const loadCameras = async () => {
      try {
        const cameraData = await loadKerberosConfig();
        setCameras(cameraData);
        setError(null);
        
        // Start monitoring camera status
        statusCleanup = startStatusMonitoring(cameraData, (updatedCameras) => {
          setCameras(updatedCameras);
        });
        
      } catch (error) {
        console.error('Failed to load camera configuration:', error);
        setError(error.message);
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

  if (error) {
    return (
      <div className="App">
        <main className="app-main loading">
          <div className="error-container">
            <div className="error-icon">⚠️</div>
            <h2>Configuration Error</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>
              Retry
            </button>
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
