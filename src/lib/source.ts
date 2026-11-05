import { createContext } from 'react';
import type { LibraryStory, StoryDoc } from '../types';

// What a story is based on (a paper or a company blog post), read the same way on every page.

/**
 * The trust level of the story's source. The story page provides it, so claim labels (Stamp) can say
 * "Measured result · company-reported" without every block having to pass it down.
 */
export const SourceTrustContext = createContext<LibraryStory['trust']>(undefined);

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

/** "2026-03-04" becomes "4 March 2026". */
export function formatDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number);
  return `${day} ${MONTHS[month - 1]} ${year}`;
}

export interface SourceView {
  kind: 'paper' | 'blog';
  title: string;
  /** Authors for a paper, the organization for a blog. */
  by: string;
  year: number;
  /** A paper shows its year; a blog shows its full date. */
  dated: string;
  url: string;
  archivedUrl?: string;
}

export function sourceOf(doc: StoryDoc): SourceView {
  if (doc.kind === 'blog') {
    const b = doc.blog;
    return {
      kind: 'blog', title: b.title, by: b.organization, year: Number(b.published.slice(0, 4)),
      dated: formatDate(b.published), url: b.url, archivedUrl: b.archivedUrl,
    };
  }
  const p = doc.paper;
  return { kind: 'paper', title: p.title, by: p.authors, year: p.year, dated: String(p.year), url: p.url };
}
