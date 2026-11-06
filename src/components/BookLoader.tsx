import { useEffect, type ReactNode } from 'react';
import './BookLoader.css';

export type BookLoaderPhase = 'pending' | 'reveal' | 'idle';

type BookLoaderProps = {
  phase: BookLoaderPhase;
  onComplete?: () => void;
  children: ReactNode;
};

/**
 * Wraps the page with a loading overlay (decision 50 handles the hydration path; this is the
 * post-mount loading experience). While `phase` is `pending` or `reveal` the overlay covers
 * the children. On `reveal` the loader lifts up and out while the page rises in from below.
 * Rotating captions and the eight floating field icons live in CSS so there is no timer churn.
 */
export function BookLoader({ phase, onComplete, children }: BookLoaderProps) {
  useEffect(() => {
    if (phase !== 'reveal') return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      onComplete?.();
      return;
    }
    const timer = window.setTimeout(() => onComplete?.(), 900);
    return () => window.clearTimeout(timer);
  }, [phase, onComplete]);

  return (
    <div className={`book-transition book-transition--${phase}`} aria-busy={phase !== 'idle'} suppressHydrationWarning>
      <div className="book-transition__content" suppressHydrationWarning>{children}</div>
      {phase !== 'idle' && (
        <div className="book-loader" role="status" aria-live="polite">
          <div className="book-loader__scene" aria-hidden="true">
            <AtomIcon className="curio c1" />
            <DnaIcon className="curio c2" />
            <HexIcon className="curio c3" />
            <PlanetIcon className="curio c4" />
            <CodeIcon className="curio c5" />
            <LeafIcon className="curio c6" />
            <NoteIcon className="curio c7" />
            <PawnIcon className="curio c8" />

            <div className="book-loader__book">
              <svg viewBox="0 0 240 150" aria-hidden="true">
                <ellipse cx="120" cy="142" rx="108" ry="6" fill="rgba(39,37,30,.18)" />
                <path d="M120 18 L120 134 L20 128 L24 28 Z" fill="#f6f0df" stroke="#27251e" strokeWidth="3" strokeLinejoin="round" />
                <path d="M120 18 L120 134 L220 128 L216 28 Z" fill="#f6f0df" stroke="#27251e" strokeWidth="3" strokeLinejoin="round" />
                <path d="M120 18 L120 134" stroke="#27251e" strokeWidth="3.2" />
                <g stroke="#948b77" strokeWidth="2.4" strokeLinecap="round" fill="none">
                  <path d="M34 44 L108 44" /><path d="M34 58 L104 58" /><path d="M34 72 L108 72" />
                  <path d="M34 86 L100 86" /><path d="M34 100 L106 100" /><path d="M34 114 L96 114" />
                </g>
                <g stroke="#948b77" strokeWidth="2.4" strokeLinecap="round" fill="none">
                  <path d="M132 44 L206 44" /><path d="M132 58 L202 58" /><path d="M132 72 L206 72" />
                  <path d="M132 86 L198 86" /><path d="M132 100 L204 100" /><path d="M132 114 L194 114" />
                </g>
                <g stroke="#a13324" strokeWidth="2.4" fill="none" strokeLinecap="round">
                  <path d="M114 44 L114 58" /><circle cx="212" cy="72" r="2.2" />
                </g>
              </svg>
            </div>
          </div>

          <p className="book-loader__caption" aria-label="Loading">
            <span className="s1">Peer-reviewing the pixels&hellip;</span>
            <span className="s2">Chasing down a reference&hellip;</span>
            <span className="s3">Teaching the AI to pronounce &ldquo;hyperbolic&rdquo;&hellip;</span>
            <span className="s4">Translating jargon into English&hellip;</span>
            <span className="s5">Asking the editor for a hot take&hellip;</span>
            <span className="s6">Alphabetising the citations&hellip;</span>
            <span className="s7">Converting coffee into curiosity&hellip;</span>
            <span className="s8">Finding a better metaphor&hellip;</span>
            <span className="s9">Measuring in whatever units make sense&hellip;</span>
            <span className="s10">Reading between the lines&hellip;</span>
          </p>
        </div>
      )}
    </div>
  );
}

function AtomIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <g fill="none" stroke="#a13324" strokeWidth="2.5">
        <ellipse cx="20" cy="20" rx="16" ry="6" />
        <ellipse cx="20" cy="20" rx="16" ry="6" transform="rotate(60 20 20)" />
        <ellipse cx="20" cy="20" rx="16" ry="6" transform="rotate(-60 20 20)" />
      </g>
      <circle cx="20" cy="20" r="3" fill="#27251e" />
    </svg></span>
  );
}
function DnaIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <g fill="none" strokeWidth="2.5" strokeLinecap="round">
        <path d="M12 4 Q20 12 28 20 Q36 28 28 36" stroke="#a13324" />
        <path d="M28 4 Q20 12 12 20 Q4 28 12 36" stroke="#b5835a" />
        <path d="M14 10 L26 10 M12 20 L28 20 M14 30 L26 30" stroke="#27251e" strokeWidth="2" />
      </g>
    </svg></span>
  );
}
function HexIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <g fill="none" stroke="#27251e" strokeWidth="2.5" strokeLinejoin="round">
        <path d="M20 4 L34 12 L34 28 L20 36 L6 28 L6 12 Z" />
        <path d="M20 4 L20 36 M6 12 L34 28 M34 12 L6 28" stroke="#a13324" strokeWidth="2" />
      </g>
    </svg></span>
  );
}
function PlanetIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="10" fill="#8aa7b9" stroke="#27251e" strokeWidth="2.5" />
      <ellipse cx="20" cy="20" rx="18" ry="4" transform="rotate(-18 20 20)" fill="none" stroke="#a13324" strokeWidth="2.5" />
    </svg></span>
  );
}
function CodeIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <g fill="none" stroke="#27251e" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round">
        <path d="M14 8 Q6 8 6 14 L6 18 Q6 20 4 20 Q6 20 6 22 L6 26 Q6 32 14 32" />
        <path d="M26 8 Q34 8 34 14 L34 18 Q34 20 36 20 Q34 20 34 22 L34 26 Q34 32 26 32" />
      </g>
    </svg></span>
  );
}
function LeafIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <path d="M34 6 Q10 8 8 24 Q8 34 18 34 Q32 34 34 6 Z" fill="#b9c4a0" stroke="#27251e" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M32 10 Q22 20 14 32" fill="none" stroke="#27251e" strokeWidth="2" />
    </svg></span>
  );
}
function NoteIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <g stroke="#27251e" strokeWidth="2.5" fill="none" strokeLinejoin="round" strokeLinecap="round">
        <path d="M16 30 L16 8 L30 10 L30 14 L16 12" fill="#a13324" />
        <ellipse cx="12" cy="30" rx="6" ry="4.5" fill="#27251e" />
        <ellipse cx="26" cy="32" rx="6" ry="4.5" fill="#27251e" />
      </g>
    </svg></span>
  );
}
function PawnIcon({ className }: { className: string }) {
  return (
    <span className={className}><svg viewBox="0 0 40 40">
      <g fill="#b5835a" stroke="#27251e" strokeWidth="2.5" strokeLinejoin="round">
        <circle cx="20" cy="10" r="6" />
        <path d="M12 20 Q20 12 28 20 L26 24 L14 24 Z" />
        <path d="M10 34 Q10 24 20 24 Q30 24 30 34 Z" />
      </g>
    </svg></span>
  );
}
