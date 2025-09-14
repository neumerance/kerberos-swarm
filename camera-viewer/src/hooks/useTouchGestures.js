import { useRef, useEffect, useCallback } from 'react';

export const useTouchGestures = (ref, onDoubleClick) => {
  const lastTapRef = useRef(0);

  const handleTouchEnd = useCallback((e) => {
    const now = Date.now();
    const timeDiff = now - lastTapRef.current;
    
    if (timeDiff < 300 && timeDiff > 0) {
      // Double tap detected
      e.preventDefault();
      console.log('Touch double-tap detected');
      onDoubleClick && onDoubleClick();
      lastTapRef.current = 0; // Reset
    } else {
      // First tap or too long
      lastTapRef.current = now;
    }
  }, [onDoubleClick]);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    // Only add touch handler, let the regular onDoubleClick handle mouse events
    element.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    return () => {
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [ref, handleTouchEnd]);
};
