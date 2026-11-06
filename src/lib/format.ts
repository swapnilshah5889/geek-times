import { useEffect, useState } from 'react';

export const pad = (n: number) => String(n).padStart(2, '0');

const formatToday = () => new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

/** Blank for the first render so prerender and hydration agree; populated after mount. */
export function useTodayLabel(): string {
  const [label, setLabel] = useState('');
  useEffect(() => setLabel(formatToday()), []);
  return label;
}
