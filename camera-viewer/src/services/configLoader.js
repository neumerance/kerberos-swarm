// Configuration loader for Kerberos.io camera setup
// Uses values from root config.yml: IP range 10.19.19.30-38, ports 8080-8088/1935-1943

export const loadKerberosConfig = async () => {
  try {
    // In development: Read root config values directly
    // In production: This should be replaced with API call to read ../config.yml
    console.log('Loading camera configuration based on root config.yml structure');
    
    const rootConfig = {
      cameras: {
        ip_range: {
          start: "10.19.19.30",
          end: "10.19.19.38"
        }
      },
      docker: {
        web_port_start: 8080,
        rtmp_port_start: 1935
      }
    };
    
    return generateCameraList(rootConfig);
  } catch (error) {
    console.error('Error loading configuration:', error);
    throw new Error('Failed to load camera configuration. Please check config.yml file.');
  }
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
