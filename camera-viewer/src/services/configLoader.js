import { generateMockCameras } from './mockData';

export const loadKerberosConfig = async () => {
  try {
    // In development, we'll use the config from the parent directory
    // In production, this should come from an API endpoint
    const response = await fetch('/config.yml');
    
    if (!response.ok) {
      console.warn('Could not load config.yml, falling back to real camera config');
      return generateRealCameras();
    }
    
    const configText = await response.text();
    const config = parseYamlBasic(configText);
    
    return generateCameraList(config);
  } catch (error) {
    console.error('Error loading configuration:', error);
    // Fallback to real camera setup based on your config
    return generateRealCameras();
  }
};

// Simple YAML parser for our basic needs
const parseYamlBasic = (yamlText) => {
  const lines = yamlText.split('\n');
  const config = {
    cameras: {
      ip_range: {},
      connection: {}
    },
    docker: {}
  };
  
  let currentSection = '';
  let currentSubsection = '';
  
  for (let line of lines) {
    line = line.trim();
    if (line.startsWith('#') || !line) continue;
    
    if (line.includes(':') && !line.startsWith(' ')) {
      if (line.includes('cameras:')) currentSection = 'cameras';
      else if (line.includes('docker:')) currentSection = 'docker';
    } else if (line.startsWith('  ') && line.includes(':') && currentSection) {
      if (line.includes('ip_range:')) currentSubsection = 'ip_range';
      else if (line.includes('connection:')) currentSubsection = 'connection';
      else if (currentSubsection && line.includes(': ')) {
        const [key, value] = line.split(': ');
        const cleanKey = key.trim();
        const cleanValue = value.replace(/"/g, '').trim();
        
        if (currentSection === 'cameras' && currentSubsection) {
          config.cameras[currentSubsection][cleanKey] = isNaN(cleanValue) ? cleanValue : parseInt(cleanValue);
        } else if (currentSection === 'docker') {
          config.docker[cleanKey] = isNaN(cleanValue) ? cleanValue : parseInt(cleanValue);
        }
      }
    }
  }
  
  return config;
};

const generateCameraList = (config) => {
  const cameras = [];
  const startIp = config.cameras?.ip_range?.start || "10.19.19.30";
  const endIp = config.cameras?.ip_range?.end || "10.19.19.38";
  const webPortStart = config.docker?.web_port_start || 8080;
  const rtmpPortStart = config.docker?.rtmp_port_start || 1935;
  
  const startParts = startIp.split('.').map(Number);
  const endParts = endIp.split('.').map(Number);
  const startLastOctet = startParts[3];
  const endLastOctet = endParts[3];
  
  for (let i = startLastOctet; i <= endLastOctet; i++) {
    const index = i - startLastOctet;
    const ip = `${startParts[0]}.${startParts[1]}.${startParts[2]}.${i}`;
    const webPort = webPortStart + index;
    const rtmpPort = rtmpPortStart + index;
    // Display shortened IP format: 10.x.x.30
    const displayName = `${startParts[0]}.x.x.${i}`;
    
    cameras.push({
      id: `camera-${ip.replace(/\./g, '-')}`,
      name: displayName,
      ip: ip,
      webPort: webPort,
      rtmpPort: rtmpPort,
      // Live stream URLs from Kerberos agents
      streamUrl: `http://localhost:${webPort}/api/stream`,
      hlsUrl: `http://localhost:${webPort}/hls/stream.m3u8`,
      rtmpUrl: `rtmp://localhost:${rtmpPort}/live`,
      // Status will be checked dynamically by pinging the agent
      status: 'connecting', // Default to connecting, will be updated by status checker
      lastSeen: null
    });
  }
  
  return cameras;
};

// Fallback based on your actual config
const generateRealCameras = () => {
  return [
    {
      id: 'camera-10-19-19-30',
      name: '10.x.x.30',
      ip: '10.19.19.30',
      webPort: 8080,
      rtmpPort: 1935,
      streamUrl: 'http://localhost:8080/api/stream',
      hlsUrl: 'http://localhost:8080/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1935/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-31',
      name: '10.x.x.31',
      ip: '10.19.19.31',
      webPort: 8081,
      rtmpPort: 1936,
      streamUrl: 'http://localhost:8081/api/stream',
      hlsUrl: 'http://localhost:8081/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1936/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-32',
      name: '10.x.x.32',
      ip: '10.19.19.32',
      webPort: 8082,
      rtmpPort: 1937,
      streamUrl: 'http://localhost:8082/api/stream',
      hlsUrl: 'http://localhost:8082/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1937/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-33',
      name: '10.x.x.33',
      ip: '10.19.19.33',
      webPort: 8083,
      rtmpPort: 1938,
      streamUrl: 'http://localhost:8083/api/stream',
      hlsUrl: 'http://localhost:8083/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1938/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-34',
      name: '10.x.x.34',
      ip: '10.19.19.34',
      webPort: 8084,
      rtmpPort: 1939,
      streamUrl: 'http://localhost:8084/api/stream',
      hlsUrl: 'http://localhost:8084/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1939/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-35',
      name: '10.x.x.35',
      ip: '10.19.19.35',
      webPort: 8085,
      rtmpPort: 1940,
      streamUrl: 'http://localhost:8085/api/stream',
      hlsUrl: 'http://localhost:8085/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1940/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-36',
      name: '10.x.x.36',
      ip: '10.19.19.36',
      webPort: 8086,
      rtmpPort: 1941,
      streamUrl: 'http://localhost:8086/api/stream',
      hlsUrl: 'http://localhost:8086/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1941/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-37',
      name: '10.x.x.37',
      ip: '10.19.19.37',
      webPort: 8087,
      rtmpPort: 1942,
      streamUrl: 'http://localhost:8087/api/stream',
      hlsUrl: 'http://localhost:8087/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1942/live',
      status: 'connecting',
      lastSeen: null
    },
    {
      id: 'camera-10-19-19-38',
      name: '10.x.x.38',
      ip: '10.19.19.38',
      webPort: 8088,
      rtmpPort: 1943,
      streamUrl: 'http://localhost:8088/api/stream',
      hlsUrl: 'http://localhost:8088/hls/stream.m3u8',
      rtmpUrl: 'rtmp://localhost:1943/live',
      status: 'connecting',
      lastSeen: null
    }
  ];
};
