import type { Moment, SearchEntry, SearchIndex } from '../types';

/** The swipe feed: each paper's cover, then its moments in reading order (story, comic, facts). */
export function feedItems(index: SearchIndex): ({ kind: 'cover'; paper: SearchEntry } | { kind: 'moment'; paper: SearchEntry; moment: Moment })[] {
  const order: Moment['kind'][] = ['chapter', 'strip', 'fact'];
  const papers = [...index.papers].sort((a, b) => (a.slug === index.featured ? -1 : b.slug === index.featured ? 1 : 0));
  return papers.flatMap(paper => [
    { kind: 'cover' as const, paper },
    ...[...paper.moments]
      .sort((a, b) => order.indexOf(a.kind) - order.indexOf(b.kind))
      .map(moment => ({ kind: 'moment' as const, paper, moment })),
  ]);
}
