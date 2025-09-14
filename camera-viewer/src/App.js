import React from 'react';
import CameraGrid from './components/CameraGrid/CameraGrid';
import { mockCameras } from './services/mockData';
import './App.css';

function App() {
  return (
    <div className="App">
      <main className="app-main">
        <CameraGrid cameras={mockCameras} />
      </main>
    </div>
  );
}

export default App;
