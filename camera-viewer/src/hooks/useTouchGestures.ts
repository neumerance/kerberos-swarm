import { useRef, useEffect, useState } from 'react';

interface TouchGestureOptions {
  onDoubleClick?: (event: TouchEvent) => void;
  onPinch?: (scale: number) => void;
  onSwipe?: (direction: 'left' | 'right' | 'up' | 'down') => void;
  onLongPress?: (event: TouchEvent) => void;
}

export const useTouchGestures = (
  ref: React.RefObject<HTMLElement>,
  options: TouchGestureOptions = {}
) => {
  const [lastTap, setLastTap] = useState(0);
  const [touches, setTouches] = useState<Touch[]>([]);
  const longPressTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const initialDistance = useRef<number | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleTouchStart = (e: TouchEvent) => {
      const touchList = Array.from(e.touches);
      setTouches(touchList);

      // Long press detection
      if (touchList.length === 1) {
        longPressTimeoutRef.current = setTimeout(() => {
          options.onLongPress?.(e);
        }, 500); // 500ms for long press
      }

      // Pinch gesture initialization
      if (touchList.length === 2) {
        const touch1 = touchList[0];
        const touch2 = touchList[1];
        initialDistance.current = Math.sqrt(
          Math.pow(touch2.clientX - touch1.clientX, 2) +
          Math.pow(touch2.clientY - touch1.clientY, 2)
        );
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      // Cancel long press on move
      if (longPressTimeoutRef.current) {
        clearTimeout(longPressTimeoutRef.current);
        longPressTimeoutRef.current = null;
      }

      // Pinch gesture detection
      if (e.touches.length === 2 && initialDistance.current) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const currentDistance = Math.sqrt(
          Math.pow(touch2.clientX - touch1.clientX, 2) +
          Math.pow(touch2.clientY - touch1.clientY, 2)
        );
        const scale = currentDistance / initialDistance.current;
        options.onPinch?.(scale);
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      // Clear long press timeout
      if (longPressTimeoutRef.current) {
        clearTimeout(longPressTimeoutRef.current);
        longPressTimeoutRef.current = null;
      }

      // Double tap detection
      if (e.changedTouches.length === 1) {
        const now = Date.now();
        const timeDiff = now - lastTap;

        if (timeDiff < 300 && timeDiff > 0) {
          // Double tap detected
          e.preventDefault();
          options.onDoubleClick?.(e);
        }

        setLastTap(now);
      }

      setTouches([]);
      initialDistance.current = null;
    };

    // Add event listeners
    element.addEventListener('touchstart', handleTouchStart, { passive: false });
    element.addEventListener('touchmove', handleTouchMove, { passive: false });
    element.addEventListener('touchend', handleTouchEnd, { passive: false });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
      
      if (longPressTimeoutRef.current) {
        clearTimeout(longPressTimeoutRef.current);
      }
    };
  }, [ref, lastTap, options]);

  return { touches };
};
