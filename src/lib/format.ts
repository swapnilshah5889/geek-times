import { useEffect, useState } from 'react';

export const pad = (n: number) => String(n).padStart(2, '0');

const formatToday = () => new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

/**
 * Blank for the first render so hydration matches. Also blank throughout prerender, otherwise the
 * captured HTML would hold today's date while a next-day visitor's hydration starts empty.
 */
export function useTodayLabel(): string {
  const [label, setLabel] = useState('');
  useEffect(() => {
    if (window.__gt_prerender__) return;
    setLabel(formatToday());
  }, []);
  return label;
}
