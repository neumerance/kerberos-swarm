import { useState, useEffect } from 'react';

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
