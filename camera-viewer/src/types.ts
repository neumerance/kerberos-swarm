import React from 'react';

export interface Camera {
  id: string;
  name: string;
  ip: string;
  webPort: number;
  rtmpPort: number;
  rtmpUrl: string;
  hlsUrl: string;
  status: 'live' | 'connecting' | 'offline' | 'error';
  lastSeen: string | null;
}

export interface KerberosConfig {
  cameras: {
    ip_range: {
      start: string;
      end: string;
    };
    connection: {
      protocol: string;
      port: number;
      username: string;
      password: string;
      stream_path: string;
    };
  };
  docker: {
    web_port_start: number;
    rtmp_port_start: number;
  };
  custom_environment?: {
    TZ?: string;
  };
}

export interface Layout {
  columns: number;
  rows: 'auto' | number;
  isPortrait: boolean;
  isMobile: boolean;
  isTablet: boolean;
}

export interface AppState {
  cameras: Camera[];
  layout: Layout;
  fullscreenCamera: string | null;
  isLoading: boolean;
  error: string | null;
  settings: {
    autoReconnect: boolean;
    showLabels: boolean;
    volumeLevel: number;
  };
}

export interface TouchGestureProps {
  onDoubleClick?: (event: React.TouchEvent) => void;
  onPinch?: (scale: number) => void;
  onSwipe?: (direction: 'left' | 'right' | 'up' | 'down') => void;
  onLongPress?: (event: React.TouchEvent) => void;
}
