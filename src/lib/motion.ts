import { createContext, useContext, useEffect, useState, type RefObject } from 'react';

// Media moves only while it is on screen and its section is not paused.
// Readers who ask for reduced motion start paused (each SVG also turns its own animations off).

const reducedQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(reducedQuery.matches);
  useEffect(() => {
    const onChange = () => setReduced(reducedQuery.matches);
    reducedQuery.addEventListener('change', onChange);
    return () => reducedQuery.removeEventListener('change', onChange);
  }, []);
  return reduced;
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
