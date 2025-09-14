import { useState, useEffect } from 'react';
import { Layout } from '../types';

export const useResponsiveLayout = (): Layout => {
  const [layout, setLayout] = useState<Layout>({
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
        // Phone: 1 column portrait, 2 columns landscape
        columns = isPortrait ? 1 : 2;
      } else if (isTablet) {
        // Tablet: 2 columns portrait, 3 columns landscape
        columns = isPortrait ? 2 : 3;
      } else {
        // Desktop: 3+ columns
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

    // Update on resize and orientation change
    window.addEventListener('resize', updateLayout);
    window.addEventListener('orientationchange', () => {
      // Small delay to ensure orientation change is complete
      setTimeout(updateLayout, 100);
    });

    return () => {
      window.removeEventListener('resize', updateLayout);
      window.removeEventListener('orientationchange', updateLayout);
    };
  }, []);

  return layout;
};
