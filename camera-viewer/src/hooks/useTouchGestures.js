import { useState, useRef, useEffect, useCallback } from 'react';

export const useTouchGestures = (ref, onDoubleClick) => {
  const [tapCount, setTapCount] = useState(0);
  const tapTimeoutRef = useRef(null);

  const handleTouchEnd = useCallback((e) => {
    e.preventDefault();
    
    setTapCount(prev => {
      const newCount = prev + 1;
      
      // Clear existing timeout
      if (tapTimeoutRef.current) {
        clearTimeout(tapTimeoutRef.current);
      }
      
      // Set new timeout for double-tap detection
      tapTimeoutRef.current = setTimeout(() => {
        if (newCount === 2) {
          // Double tap detected
          onDoubleClick && onDoubleClick();
        }
        setTapCount(0);
      }, 300); // 300ms window for double-tap
      
      return newCount;
    });
  }, [onDoubleClick]);

  // Add touch event listener
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    element.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    return () => {
      element.removeEventListener('touchend', handleTouchEnd);
      if (tapTimeoutRef.current) {
        clearTimeout(tapTimeoutRef.current);
      }
    };
  }, [ref, handleTouchEnd]);

  return tapCount;
};
