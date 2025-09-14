# Camera Multi-Viewer React App - Planning Document

## 📋 Project Overview

A React.js web application that provides a unified multi-camera viewing interface for the Kerberos.io multi-agent system. The app will display all configured cameras in a grid layout with RTMP stream playback and interactive fullscreen capabilities.

## 🎯 Project Goals

### Primary Objectives
- **Mobile-first responsive design** - Optimized for phones and tablets first
- **Multi-camera grid view** - Display all cameras simultaneously in responsive grid
- **RTMP stream integration** - Live video feeds from Kerberos agents  
- **Touch-based fullscreen** - Double-tap to expand, double-tap to exit
- **Docker containerization** - Easy deployment alongside Kerberos agents
- **Configuration-driven** - Automatically detect cameras from `config.yml`
- **Cross-device compatibility** - Seamless experience on mobile, tablet, desktop

### User Experience Goals
- **Touch-optimized interface** - Designed primarily for touch interactions
- **Real-time monitoring** - Live feeds with minimal latency on all devices
- **Intuitive touch gestures** - Double-tap fullscreen, pinch-to-zoom support
- **Responsive grid layouts** - Auto-adjust based on screen size and orientation
- **Fast touch responses** - Immediate feedback for all touch interactions
- **Offline resilience** - Graceful handling of network interruptions
- **Battery optimization** - Efficient streaming for mobile devices

## 🏗️ Technical Architecture

### Technology Stack
```
Frontend (Mobile-First):
├── React 18+ (Create React App or Vite)
├── TypeScript (for type safety)
├── CSS Modules / Tailwind CSS (mobile-first responsive)
├── Video.js / HLS.js (for RTMP playback with touch controls)
├── React Router (for navigation)
├── PWA capabilities (offline support, app-like experience)
└── Touch gesture libraries (react-spring for animations)

Mobile Optimizations:
├── Intersection Observer (lazy loading streams)
├── Service Workers (caching and offline support)
├── WebRTC (low-latency streaming where possible)
└── Responsive breakpoints (phone/tablet/desktop)

Backend/API:
├── Node.js Express API (lightweight for mobile)
├── YAML parser (to read config.yml)
└── WebSocket (for real-time updates with reconnection)

Deployment:
├── Docker containerization
├── Nginx (reverse proxy with mobile optimization)
├── Docker Compose integration
└── HTTPS support (required for PWA features)
```

### Application Structure
```
camera-viewer/
├── public/
│   ├── manifest.json (PWA configuration)
│   └── icons/ (various sizes for mobile)
├── src/
│   ├── components/
│   │   ├── CameraGrid/ (responsive grid layouts)
│   │   ├── CameraTile/ (touch-optimized tiles)
│   │   ├── FullscreenViewer/ (mobile fullscreen with gestures)
│   │   ├── StatusBar/ (mobile-friendly status)
│   │   ├── TouchControls/ (mobile video controls)
│   │   └── ResponsiveLayout/ (breakpoint management)
│   ├── hooks/
│   │   ├── useConfig.js
│   │   ├── useStreamStatus.js
│   │   ├── useFullscreen.js
│   │   ├── useTouchGestures.js
│   │   ├── useResponsiveLayout.js
│   │   └── useDeviceOrientation.js
│   ├── services/
│   │   ├── configLoader.js
│   │   ├── streamManager.js
│   │   ├── touchManager.js
│   │   └── api.js
│   ├── styles/
│   │   ├── responsive.css (mobile-first breakpoints)
│   │   └── touch.css (touch-specific styles)
│   ├── types/
│   └── utils/
├── Dockerfile
├── docker-compose.yml
├── nginx.conf (mobile-optimized)
└── sw.js (service worker for PWA)
```

## 🎨 User Interface Design

### Mobile Grid View (Primary Focus)
```
┌─────────────────────────────────┐ Phone (Portrait)
│ 🏠 Kerberos Cameras      [⚙️ ] │
├─────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ │ 2x Grid (Portrait)
│ │ Front Door  │ │ Living Room │ │
│ │ 🟢 LIVE     │ │ 🟢 LIVE     │ │
│ │  [VIDEO]    │ │  [VIDEO]    │ │
│ │             │ │             │ │ 
│ └─────────────┘ └─────────────┘ │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Kitchen     │ │ Garage      │ │
│ │ 🟡 CONN     │ │ 🔴 OFF      │ │
│ │  [LOAD...]  │ │  [ERROR]    │ │
│ │             │ │             │ │
│ └─────────────┘ └─────────────┘ │
│ ┌─────────────┐                 │
│ │ Backyard    │     (scroll)    │
│ │ 🟢 LIVE     │                 │
│ │  [VIDEO]    │                 │
│ └─────────────┘                 │
└─────────────────────────────────┘
```

### Tablet Grid View (Landscape/Portrait)
```
┌─────────────────────────────────────────────────┐ Tablet (Landscape)
│ 🏠 Kerberos Multi-Camera Viewer          [⚙️ ] │
├─────────────────────────────────────────────────┤
│ ┌────────────┐ ┌────────────┐ ┌────────────┐   │ 3x Grid
│ │ Front Door │ │Living Room │ │  Kitchen   │   │
│ │ 🟢 LIVE    │ │ 🟢 LIVE    │ │ � CONN    │   │
│ │  [VIDEO]   │ │  [VIDEO]   │ │ [LOADING]  │   │
│ └────────────┘ └────────────┘ └────────────┘   │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│ │  Garage    │ │  Backyard  │ │  Basement  │   │
│ │ 🔴 OFF     │ │ 🟢 LIVE    │ │ 🟢 LIVE    │   │
│ │  [ERROR]   │ │  [VIDEO]   │ │  [VIDEO]   │   │
│ └────────────┘ └────────────┘ └────────────┘   │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│ │Side Yard   │ │   Porch    │ │  Driveway  │   │
│ │ 🟢 LIVE    │ │ � LIVE    │ │ 🟢 LIVE    │   │
│ │  [VIDEO]   │ │  [VIDEO]   │ │  [VIDEO]   │   │
│ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────┘
```

### Mobile Fullscreen View (Touch Optimized)
```
┌─────────────────────────────────┐ Phone (Landscape)
│ Front Door Camera         [×] │ (Auto-rotate)
├─────────────────────────────────┤
│                                 │
│                                 │
│        [FULL VIDEO FEED]        │
│     (Double-tap to exit)        │
│                                 │
│                                 │
├─────────────────────────────────┤
│ ●🔴 REC  [🔊] [⚙️]    🟢 LIVE │ Touch Controls
└─────────────────────────────────┘
```

### Responsive Breakpoints
```css
/* Mobile First Approach */
.camera-grid {
  /* Phone Portrait: 1 column */
  grid-template-columns: 1fr;
}

@media (min-width: 480px) {
  /* Phone Landscape / Small Tablet: 2 columns */
  .camera-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 768px) {
  /* Tablet Portrait: 2x2 or 2x3 */
  .camera-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  /* Tablet Landscape / Desktop: 3x3 */
  .camera-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1440px) {
  /* Large Desktop: 4x3 or 3x4 */
  .camera-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### Touch Interaction Patterns
- **Single Tap**: Show/hide camera controls and status
- **Double Tap**: Enter/exit fullscreen mode
- **Pinch Zoom**: Zoom into video feed (in fullscreen)
- **Swipe Left/Right**: Switch between cameras (in fullscreen)
- **Long Press**: Show camera options menu

### Status Indicators
- 🟢 **LIVE** - Stream active and healthy
- 🟡 **CONNECTING** - Attempting to connect  
- 🔴 **OFFLINE** - Camera/stream unavailable
- ⚠️ **ERROR** - Connection or playback error

## 🔧 Core Features

### Phase 1: Mobile-First Foundation (MVP)
- [x] **Responsive Grid Layout Engine**
  - Mobile-first CSS Grid with responsive breakpoints
  - Auto-sizing: 1 col (phone), 2 col (tablet), 3+ col (desktop)
  - Touch-optimized spacing and sizing

- [x] **Touch-Based Fullscreen System** 
  - Double-tap to enter fullscreen mode
  - Double-tap again to exit to multi-view
  - Auto-rotation support for mobile landscape
  - Touch-friendly exit controls

- [x] **Mobile-Optimized Video Players**
  - Video.js with touch controls
  - Lazy loading for better mobile performance
  - Adaptive bitrate for mobile networks
  - Battery-efficient streaming

- [x] **Configuration Auto-Loading**
  - Read Kerberos `config.yml` on mobile
  - Parse IP ranges and generate mobile URLs
  - Auto-detect device capabilities
  - Offline configuration caching

- [x] **Progressive Web App (PWA)**
  - App-like experience on mobile
  - Home screen installation
  - Offline capability with service workers
  - Push notifications for alerts

### Phase 2: Enhanced Mobile Features
- [ ] **Advanced Touch Gestures**
  - Pinch-to-zoom in fullscreen mode
  - Swipe navigation between cameras
  - Long-press for context menus
  - Pull-to-refresh functionality

- [ ] **Mobile Stream Controls**
  - Touch-friendly play/pause controls
  - Volume control with haptic feedback
  - Stream quality selection for data saving
  - Picture-in-picture mode support

- [ ] **Responsive Status Dashboard**
  - Mobile-optimized connection indicators
  - Swipeable status cards
  - Network quality indicators
  - Battery usage optimization

- [ ] **Device Orientation Support**
  - Auto-rotate for optimal viewing
  - Lock orientation in fullscreen
  - Adaptive layouts for portrait/landscape
  - Gesture-based rotation override

### Phase 3: Advanced Mobile Features  
- [ ] **Multi-Touch Support**
  - Multi-finger gestures for multiple cameras
  - Split-screen viewing on tablets
  - Gesture customization settings
  - Accessibility touch options

- [ ] **Mobile Performance Optimization**
  - Background video pausing for battery
  - Network-aware streaming quality
  - Memory management for low-end devices
  - CPU usage optimization

- [ ] **Cross-Device Synchronization**
  - Layout sync between devices
  - Shared viewing sessions
  - Multi-device notifications
  - Cloud preference storage

- [ ] **Advanced PWA Features**
  - Offline video caching
  - Background sync for alerts
  - Push notification management
  - App shortcuts and widgets

## 🐳 Docker Integration

### Container Strategy
```yaml
# docker-compose.yml addition
services:
  camera-viewer:
    build: ./camera-viewer
    ports:
      - "3000:80"
    volumes:
      - ./config.yml:/app/config.yml:ro
    environment:
      - NODE_ENV=production
      - CONFIG_PATH=/app/config.yml
    depends_on:
      - camera-10-19-19-30
      - camera-10-19-19-31
    networks:
      - kerberos-network
```

### Dockerfile Strategy
```dockerfile
# Multi-stage build
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📊 Data Flow Architecture

### Configuration Flow
```
config.yml 
    ↓ (parsed by backend API)
Camera List → Stream URLs → React State
    ↓
Grid Component → Camera Tiles → Video Players
```

### Stream Data Flow  
```
Kerberos Agent (RTMP) → 
    nginx-rtmp (HLS conversion) → 
        Browser (HLS.js) → 
            Video Element
```

### State Management
```javascript
// Global State Structure
{
  cameras: [
    {
      id: "camera-10-19-19-30",
      name: "Front Door",
      ip: "10.19.19.30",
      rtmpUrl: "rtmp://localhost:1935/live",
      hlsUrl: "http://localhost:8080/hls/stream.m3u8",
      status: "live|connecting|offline|error",
      lastSeen: "2024-01-15T10:30:00Z"
    }
  ],
  layout: {
    gridSize: "3x3",
    fullscreenCamera: null,
    customPositions: {}
  },
  settings: {
    autoReconnect: true,
    volumeLevel: 0.7,
    showLabels: true
  }
}
```

## 🔌 API Endpoints

### Configuration API
```javascript
GET /api/config
// Returns: { cameras: [...], settings: {...} }

GET /api/cameras
// Returns: [{ id, name, ip, streamUrl, status }]

GET /api/camera/:id/status  
// Returns: { status, lastSeen, streamHealth }

POST /api/camera/:id/restart
// Restart specific camera stream
```

### WebSocket Events
```javascript
// Real-time updates
ws.on('camera-status', (data) => {
  // { cameraId, status, timestamp }
});

ws.on('stream-health', (data) => {
  // { cameraId, bitrate, fps, errors }
});
```

## 🎬 Stream Handling Strategy

### RTMP to HLS Conversion
```bash
# nginx-rtmp configuration
rtmp {
  server {
    listen 1935;
    application live {
      live on;
      hls on;
      hls_path /tmp/hls;
      hls_fragment 3;
      hls_playlist_length 60;
    }
  }
}
```

### Video Player Implementation
```javascript
// Mobile-Optimized Video Player with Touch Gestures
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const MobileCameraPlayer = ({ streamUrl, onDoubleClick, onError, onReady }) => {
  const [tapCount, setTapCount] = useState(0);
  const tapTimeoutRef = useRef(null);

  const handleTouchEnd = (e) => {
    // Prevent default to avoid zoom on double-tap
    e.preventDefault();
    
    setTapCount(prev => prev + 1);
    
    // Clear existing timeout
    if (tapTimeoutRef.current) {
      clearTimeout(tapTimeoutRef.current);
    }
    
    // Set new timeout for double-tap detection
    tapTimeoutRef.current = setTimeout(() => {
      if (tapCount === 1) {
        // Single tap - show/hide controls
        toggleControls();
      } else if (tapCount === 2) {
        // Double tap - enter/exit fullscreen
        onDoubleClick();
      }
      setTapCount(0);
    }, 300); // 300ms window for double-tap
  };

  useEffect(() => {
    const player = videojs('video-element', {
      controls: false, // Hide default controls initially
      autoplay: true,
      muted: true, // Required for autoplay on mobile
      preload: 'metadata',
      fluid: true, // Responsive sizing
      responsive: true,
      playsinline: true, // Prevent fullscreen on iOS
      sources: [{
        src: streamUrl,
        type: 'application/x-mpegURL'
      }],
      // Mobile-specific options
      techOrder: ['html5'], // Prefer HTML5 for mobile
      html5: {
        hlsjsConfig: {
          // Optimize for mobile networks
          maxBufferLength: 10,
          maxBufferSize: 60 * 1000 * 1000,
          liveSyncDurationCount: 1
        }
      }
    });

    player.on('error', onError);
    player.on('ready', onReady);
    
    // Add touch event listeners
    const videoElement = player.el().querySelector('video');
    videoElement.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    return () => {
      videoElement.removeEventListener('touchend', handleTouchEnd);
      player.dispose();
    };
  }, [streamUrl, tapCount, onDoubleClick]);

  return (
    <div className="mobile-video-container">
      <video 
        id="video-element" 
        className="video-player mobile-optimized"
        playsInline // Essential for iOS
      />
    </div>
  );
};
```

## 📱 Mobile-First Implementation Strategy

### Responsive Grid System
```css
/* Mobile-First CSS Grid Implementation */
.camera-grid {
  display: grid;
  gap: 8px;
  padding: 8px;
  width: 100%;
  height: 100vh;
  
  /* Phone Portrait - Single column, scrollable */
  grid-template-columns: 1fr;
  grid-auto-rows: minmax(200px, 1fr);
  overflow-y: auto;
}

/* Phone Landscape */
@media (orientation: landscape) and (max-width: 767px) {
  .camera-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: minmax(150px, 1fr);
    overflow-y: auto;
  }
}

/* Tablet Portrait */
@media (min-width: 768px) and (orientation: portrait) {
  .camera-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: minmax(180px, 1fr);
  }
}

/* Tablet Landscape */
@media (min-width: 768px) and (orientation: landscape) {
  .camera-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: minmax(160px, 1fr);
  }
}

/* Large Tablet/Desktop */
@media (min-width: 1024px) {
  .camera-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    grid-auto-rows: minmax(200px, 1fr);
  }
}

/* Mobile Fullscreen */
.fullscreen-mobile {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  background: black;
  
  .video-player {
    width: 100%;
    height: 100%;
    object-fit: contain; /* Preserve aspect ratio */
  }
  
  /* Hide address bar on mobile */
  @supports (-webkit-touch-callout: none) {
    height: -webkit-fill-available;
  }
}
```

### Touch Gesture Handler
```javascript
// Advanced Touch Gesture Management
export const useTouchGestures = (ref, onDoubleClick, onPinch, onSwipe) => {
  const [lastTap, setLastTap] = useState(0);
  const [touches, setTouches] = useState([]);
  
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    
    const handleTouchStart = (e) => {
      setTouches(Array.from(e.touches));
    };
    
    const handleTouchMove = (e) => {
      if (e.touches.length === 2) {
        // Pinch gesture detection
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.sqrt(
          Math.pow(touch2.clientX - touch1.clientX, 2) +
          Math.pow(touch2.clientY - touch1.clientY, 2)
        );
        onPinch?.(distance);
      }
    };
    
    const handleTouchEnd = (e) => {
      const now = Date.now();
      const timeDiff = now - lastTap;
      
      if (timeDiff < 300 && timeDiff > 0) {
        // Double tap detected
        e.preventDefault();
        onDoubleClick?.(e);
      }
      
      setLastTap(now);
      setTouches([]);
    };
    
    // Add event listeners with passive: false for preventDefault
    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: false });
    element.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [ref, lastTap, onDoubleClick, onPinch, onSwipe]);
};
```

### Mobile Layout Hook
```javascript
// Responsive Layout Management
export const useResponsiveLayout = () => {
  const [layout, setLayout] = useState({
    columns: 1,
    rows: 'auto',
    isPortrait: true,
    isMobile: false,
    isTablet: false
  });
  
  useEffect(() => {
    const updateLayout = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const isPortrait = height > width;
      const isMobile = width < 768;
      const isTablet = width >= 768 && width < 1024;
      
      let columns = 1;
      
      if (isMobile) {
        columns = isPortrait ? 1 : 2;
      } else if (isTablet) {
        columns = isPortrait ? 2 : 3;
      } else {
        // Desktop
        columns = 3;
      }
      
      setLayout({
        columns,
        rows: 'auto',
        isPortrait,
        isMobile,
        isTablet
      });
    };
    
    // Update on mount
    updateLayout();
    
    // Update on resize/orientation change
    window.addEventListener('resize', updateLayout);
    window.addEventListener('orientationchange', updateLayout);
    
    return () => {
      window.removeEventListener('resize', updateLayout);
      window.removeEventListener('orientationchange', updateLayout);
    };
  }, []);
  
  return layout;
};
```

## 🚀 Development Roadmap

### Sprint 1: Foundation (Week 1-2)
- [ ] Project setup with Create React App + TypeScript
- [ ] Docker containerization basics
- [ ] Configuration parser for `config.yml`
- [ ] Basic grid layout component
- [ ] Simple video player integration

### Sprint 2: Core Features (Week 3-4)
- [ ] RTMP stream integration with HLS.js
- [ ] Fullscreen functionality
- [ ] Status indicators and error handling
- [ ] Responsive grid layouts
- [ ] Docker Compose integration

### Sprint 3: Polish & Testing (Week 5-6)
- [ ] Stream reconnection logic
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Error boundary components
- [ ] Integration testing with Kerberos

### Sprint 4: Advanced Features (Week 7-8)
- [ ] Stream controls (play/pause/volume)
- [ ] Layout customization
- [ ] Settings persistence
- [ ] WebSocket real-time updates
- [ ] Production deployment optimization

## 📝 Configuration Integration

### Reading Kerberos Config
```javascript
// services/configLoader.js
export const loadKerberosConfig = async () => {
  const response = await fetch('/api/kerberos-config');
  const config = await response.json();
  
  const cameras = generateCameraList(
    config.cameras.ip_range.start,
    config.cameras.ip_range.end,
    config.docker.web_port_start,
    config.docker.rtmp_port_start
  );
  
  return cameras;
};

const generateCameraList = (startIp, endIp, webPortStart, rtmpPortStart) => {
  const cameras = [];
  // Convert IP range to array of cameras with ports
  // Return formatted camera objects
  return cameras;
};
```

### Auto-Discovery
```javascript
// Automatically detect active cameras
export const discoverActiveCameras = async (cameras) => {
  const promises = cameras.map(async (camera) => {
    try {
      const response = await fetch(`http://localhost:${camera.webPort}/api/status`);
      return { ...camera, status: response.ok ? 'live' : 'offline' };
    } catch {
      return { ...camera, status: 'offline' };
    }
  });
  
  return Promise.all(promises);
};
```

## 🧪 Testing Strategy

### Unit Testing
- Component rendering tests
- Configuration parsing tests
- Stream URL generation tests
- Error handling tests

### Integration Testing
- End-to-end camera viewing
- Fullscreen functionality
- Stream switching
- Configuration loading

### Performance Testing
- Multiple stream playback
- Memory usage monitoring
- CPU impact assessment
- Network bandwidth optimization

## 📦 Deployment Strategy

### Development Environment
```bash
# In camera-viewer directory
npm start  # React dev server on :3000

# In main project
kerberos start  # Start cameras on :8080+
```

### Production Deployment
```bash
# Build and deploy with main system
docker-compose up -d

# Access viewer at http://localhost:3000
# Cameras accessible via embedded streams
```

### Integration with Existing System
```yaml
# Add to main docker-compose.yml
version: '3.8'
services:
  # ... existing Kerberos agents ...
  
  camera-viewer:
    build: ./camera-viewer
    ports:
      - "3000:80"
    volumes:
      - ./config.yml:/app/config.yml:ro
    depends_on:
      - camera-10-19-19-30
      - camera-10-19-19-31
      # ... all camera services
    networks:
      - kerberos-network
```

## 🎯 Success Metrics

### Technical Metrics
- **Stream Latency**: < 2 seconds on mobile networks
- **Touch Response**: < 100ms for double-tap recognition
- **Concurrent Streams**: Support 9+ on modern mobile devices  
- **Memory Usage**: < 256MB on mobile, < 512MB on tablet
- **Battery Impact**: < 20% additional drain per hour
- **Startup Time**: < 5 seconds on 4G networks
- **Network Efficiency**: Adaptive bitrate based on connection

### Mobile Experience Metrics
- **First Paint**: < 1.5 seconds on mobile
- **Stream Load Time**: < 3 seconds per camera on 4G
- **Fullscreen Transition**: < 300ms smooth animation
- **Touch Accuracy**: 95%+ double-tap recognition rate
- **Orientation Change**: < 500ms layout adaptation
- **Offline Resilience**: 30-second network interruption tolerance

## 🔮 Future Enhancements

### Advanced Video Features
- **Multi-angle sync** - Synchronized playback across cameras
- **Timeline scrubbing** - Scrub through recorded footage
- **Motion tracking** - Highlight detected motion areas
- **Zoom and pan** - PTZ camera control integration

### Analytics Integration
- **Activity dashboard** - Motion detection statistics
- **Historical playback** - Browse recordings by date/time
- **Export functionality** - Download clips and snapshots
- **Alert management** - Configure and view motion alerts

### Enterprise Features
- **Multi-tenant support** - Multiple camera systems
- **User management** - Role-based access control
- **API integration** - RESTful API for external systems  
- **Cloud streaming** - Remote access capabilities

---

## 📋 Next Steps

1. **Create project structure** - Set up React app with TypeScript
2. **Docker setup** - Create Dockerfile and compose integration
3. **Configuration parsing** - Read and process `config.yml`
4. **Basic grid layout** - Implement responsive camera grid
5. **Stream integration** - Add RTMP/HLS video playback
6. **Fullscreen functionality** - Double-click fullscreen feature

This planning document provides a comprehensive roadmap for building a professional camera multi-viewer that integrates seamlessly with the existing Kerberos.io multi-agent system.

**Ready to start development!** 🚀📹
