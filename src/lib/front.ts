import type { Moment, SearchEntry, SearchIndex } from '../types';

// Lays out the front page from the index: one tile per paper, in what order and at what size.
// Everything is derived from paper data, so the page fills itself as papers are added.

export type TileSize = 'hero' | 'wide' | 'tall';

export type Tile =
  | { kind: 'cover'; size: TileSize; paper: SearchEntry }
  | { kind: 'feed'; size: TileSize; count: number }
  | { kind: 'topics'; size: TileSize };

/** The front page has one tile per paper; bite-size moments live in snack mode (?feed), not here. */
export function frontPage(index: SearchIndex): Tile[] {
  const featured = index.papers.find(p => p.slug === index.featured) ?? index.papers[0];
  if (!featured) return [];
  const others = index.papers.filter(p => p !== featured).sort((a, b) => Number(b.issue) - Number(a.issue));
  const allMoments = index.papers.reduce((n, p) => n + p.moments.length, 0);

  return [
    { kind: 'cover', size: 'hero', paper: featured },
    { kind: 'feed', size: 'tall', count: allMoments },
    { kind: 'topics', size: 'wide' },
    ...others.map((paper): Tile => ({ kind: 'cover', size: 'wide', paper })),
  ];
}

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
