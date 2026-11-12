import { createContext, useContext, useEffect, useState, useSyncExternalStore, type RefObject } from 'react';

// Media moves only while it is on screen and its section is not paused.
// Readers who ask for reduced motion start paused (each SVG also turns its own animations off).

const reducedQuery = () => typeof window === 'undefined' ? null : window.matchMedia('(prefers-reduced-motion: reduce)');

const subscribeReduced = (onChange: () => void) => {
  const query = reducedQuery();
  if (!query) return () => {};
  query.addEventListener('change', onChange);
  return () => query.removeEventListener('change', onChange);
};
const getReduced = () => reducedQuery()?.matches ?? false;

export function useReducedMotion(): boolean {
  return useSyncExternalStore(subscribeReduced, getReduced, () => false);
}

export interface MotionState {
  held: boolean;
  setHeld: (held: boolean) => void;
}

export const MotionContext = createContext<MotionState>({ held: false, setHeld: () => {} });

export function useMotion(): MotionState {
  return useContext(MotionContext);
}

export function useInView(ref: RefObject<Element | null>, rootMargin = '80px'): boolean {
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { rootMargin });
    io.observe(el);
    return () => io.disconnect();
  }, [ref, rootMargin]);
  return inView;
}
