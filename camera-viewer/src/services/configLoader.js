// Configuration loader for Kerberos.io camera setup
// Loads configuration from root config.yml via symbolic link

import yaml from 'js-yaml';

export const loadKerberosConfig = async () => {
  try {
    console.log('Loading camera configuration from config.yml');
    
    // Fetch the config.yml file via the symbolic link in public directory
    const response = await fetch('/config.yml');
    if (!response.ok) {
      throw new Error(`Failed to fetch config.yml: ${response.status} ${response.statusText}`);
    }
    
    const configText = await response.text();
    const rootConfig = yaml.load(configText);
    
    console.log('Loaded configuration:', {
      ipRange: rootConfig.cameras.ip_range,
      webPortStart: rootConfig.docker.web_port_start,
      rtmpPortStart: rootConfig.docker.rtmp_port_start
    });
    
    return generateCameraList(rootConfig);
  } catch (error) {
    console.error('Error loading configuration:', error);
    throw new Error(`Failed to load camera configuration: ${error.message}`);
  }
};

const generateCameraList = (config) => {
  const cameras = [];
  const startIp = config.cameras.ip_range.start;
  const endIp = config.cameras.ip_range.end;
  const webPortStart = config.docker.web_port_start;
  const rtmpPortStart = config.docker.rtmp_port_start;
  
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
