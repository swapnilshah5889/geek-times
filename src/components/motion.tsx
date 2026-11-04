import { useState, type ReactNode } from 'react';
import { MotionContext, useMotion, useReducedMotion } from '../lib/motion';

/** One pause switch shared by every graphic inside it (usually one page section). */
export function MotionGroup({ children }: { children: ReactNode }) {
  const reduced = useReducedMotion();
  // A reader's choice holds until their reduced-motion setting changes; then the setting wins again.
  const [choice, setChoice] = useState<{ held: boolean; reduced: boolean } | null>(null);
  const held = choice && choice.reduced === reduced ? choice.held : reduced;
  const setHeld = (next: boolean) => setChoice({ held: next, reduced });
  return <MotionContext.Provider value={{ held, setHeld }}>{children}</MotionContext.Provider>;
}

export function MotionButton({ noun }: { noun?: string }) {
  const { held, setHeld } = useMotion();
  return (
    <button type="button" onClick={() => setHeld(!held)}>
      {[held ? 'Play' : 'Pause', noun].filter(Boolean).join(' ')}
    </button>
  );
}
