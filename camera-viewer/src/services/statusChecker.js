// Service to check the actual status of Kerberos camera agents
export const checkCameraStatus = async (camera) => {
  try {
    // Try to reach the Kerberos agent's health endpoint
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`http://localhost:${camera.webPort}/api/health`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      }
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json().catch(() => ({}));
      return {
        status: 'live',
        lastSeen: new Date().toISOString(),
        // Could include additional info from the health check
        info: data
      };
    } else if (response.status === 404) {
      // Agent is running but health endpoint might not exist
      // Try alternative endpoint or assume it's connecting
      return {
        status: 'connecting',
        lastSeen: new Date().toISOString()
      };
    } else {
      return {
        status: 'error',
        lastSeen: null,
        error: `HTTP ${response.status}`
      };
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      return {
        status: 'offline',
        lastSeen: null,
        error: 'Connection timeout'
      };
    }
    
    // Network error, agent not running, etc.
    return {
      status: 'offline',
      lastSeen: null,
      error: error.message
    };
  }
};

// Check status of multiple cameras in parallel
export const checkAllCameraStatus = async (cameras) => {
  const statusChecks = cameras.map(async (camera) => {
    const statusResult = await checkCameraStatus(camera);
    return {
      ...camera,
      ...statusResult
    };
  });
  
  return Promise.all(statusChecks);
};

// Alternative status check using the stream endpoint
export const checkStreamStatus = async (camera) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    // Try to access the stream endpoint
    const response = await fetch(camera.streamUrl, {
      method: 'HEAD', // Just check if endpoint exists
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      return { status: 'live', lastSeen: new Date().toISOString() };
    } else {
      return { status: 'error', lastSeen: null };
    }
  } catch (error) {
    return { status: 'offline', lastSeen: null };
  }
};

// Periodic status checker that updates camera status every 30 seconds
export const startStatusMonitoring = (cameras, updateCallback, interval = 30000) => {
  const checkStatus = async () => {
    try {
      const updatedCameras = await checkAllCameraStatus(cameras);
      updateCallback(updatedCameras);
    } catch (error) {
      console.error('Error checking camera status:', error);
    }
  };
  
  // Initial check
  checkStatus();
  
  // Set up periodic checks
  const intervalId = setInterval(checkStatus, interval);
  
  // Return cleanup function
  return () => clearInterval(intervalId);
};
