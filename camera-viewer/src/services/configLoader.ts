import yaml from 'js-yaml';
import { KerberosConfig, Camera } from '../types';

export const loadKerberosConfig = async (): Promise<Camera[]> => {
  try {
    // In development, we'll read from the public folder
    // In production, this should come from an API endpoint
    const response = await fetch('/config.yml');
    
    if (!response.ok) {
      throw new Error('Failed to load configuration file');
    }
    
    const configText = await response.text();
    const config = yaml.load(configText) as KerberosConfig;
    
    return generateCameraList(config);
  } catch (error) {
    console.error('Error loading configuration:', error);
    // Fallback to mock data for development
    return generateMockCameras();
  }
};

const generateCameraList = (config: KerberosConfig): Camera[] => {
  const cameras: Camera[] = [];
  const startIp = config.cameras.ip_range.start;
  const endIp = config.cameras.ip_range.end;
  const webPortStart = config.docker.web_port_start;
  const rtmpPortStart = config.docker.rtmp_port_start;

  // Parse IP range
  const startParts = startIp.split('.').map(Number);
  const endParts = endIp.split('.').map(Number);
  
  // Generate IP addresses (assuming last octet changes)
  const startLastOctet = startParts[3];
  const endLastOctet = endParts[3];
  
  for (let i = startLastOctet; i <= endLastOctet; i++) {
    const ip = `${startParts[0]}.${startParts[1]}.${startParts[2]}.${i}`;
    const index = i - startLastOctet;
    const webPort = webPortStart + index;
    const rtmpPort = rtmpPortStart + index;
    
    cameras.push({
      id: `camera-${ip.replace(/\./g, '-')}`,
      name: `Camera ${ip}`,
      ip,
      webPort,
      rtmpPort,
      rtmpUrl: `rtmp://localhost:${rtmpPort}/live`,
      hlsUrl: `http://localhost:${webPort}/hls/stream.m3u8`,
      status: 'offline', // Will be updated by status checker
      lastSeen: null
    });
  }

  return cameras;
};

const generateMockCameras = (): Camera[] => {
  // Mock data for development
  const cameras: Camera[] = [];
  
  for (let i = 0; i < 9; i++) {
    const ip = `10.19.19.${30 + i}`;
    const webPort = 8080 + i;
    const rtmpPort = 1935 + i;
    
    cameras.push({
      id: `camera-${ip.replace(/\./g, '-')}`,
      name: getCameraName(i),
      ip,
      webPort,
      rtmpPort,
      rtmpUrl: `rtmp://localhost:${rtmpPort}/live`,
      hlsUrl: `http://localhost:${webPort}/hls/stream.m3u8`,
      status: i % 3 === 0 ? 'live' : i % 3 === 1 ? 'connecting' : 'offline',
      lastSeen: i % 3 === 0 ? new Date().toISOString() : null
    });
  }
  
  return cameras;
};

const getCameraName = (index: number): string => {
  const names = [
    'Front Door',
    'Living Room', 
    'Kitchen',
    'Garage',
    'Backyard',
    'Basement',
    'Side Yard',
    'Porch',
    'Driveway'
  ];
  
  return names[index] || `Camera ${index + 1}`;
};

export const checkCameraStatus = async (camera: Camera): Promise<'live' | 'offline'> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`http://localhost:${camera.webPort}/api/status`, {
      signal: controller.signal,
      mode: 'cors'
    });
    
    clearTimeout(timeoutId);
    return response.ok ? 'live' : 'offline';
  } catch {
    return 'offline';
  }
};

export const checkAllCamerasStatus = async (cameras: Camera[]): Promise<Camera[]> => {
  const promises = cameras.map(async (camera) => {
    const status = await checkCameraStatus(camera);
    return {
      ...camera,
      status,
      lastSeen: status === 'live' ? new Date().toISOString() : camera.lastSeen
    };
  });
  
  return Promise.all(promises);
};
