import type { Moment, SearchEntry, SearchIndex } from '../types';

// Lays out the front page from the index: which cards appear, in what order and at what size.
// Everything is derived from paper data, so the page fills itself as papers are added.

export type TileSize = 'hero' | 'wide' | 'tall' | 'square';

export type Tile =
  | { kind: 'cover'; size: TileSize; paper: SearchEntry }
  | { kind: 'moment'; size: TileSize; moment: Moment; paper: SearchEntry }
  | { kind: 'feed'; size: TileSize; count: number }
  | { kind: 'topics'; size: TileSize };

/** Mixes kinds so neighbors differ: strip, fact, strip, chapter, … then whatever is left. */
function interleave(moments: Moment[]): Moment[] {
  const queues = {
    strip: moments.filter(m => m.kind === 'strip'),
    fact: moments.filter(m => m.kind === 'fact'),
    chapter: moments.filter(m => m.kind === 'chapter'),
  };
  const pattern: Moment['kind'][] = ['strip', 'fact', 'strip', 'chapter'];
  const out: Moment[] = [];
  for (let i = 0; out.length < moments.length; i++) {
    const kind = pattern[i % pattern.length];
    const next = queues[kind].shift() ?? queues.strip.shift() ?? queues.chapter.shift() ?? queues.fact.shift();
    if (next) out.push(next);
  }
  return out;
}

/** Story panels are wide drawings; strips and facts fit a square. */
const sizeFor = (m: Moment): TileSize => (m.kind === 'chapter' ? 'wide' : 'square');

export function frontPage(index: SearchIndex): Tile[] {
  const featured = index.papers.find(p => p.slug === index.featured) ?? index.papers[0];
  if (!featured) return [];
  const others = index.papers.filter(p => p !== featured).sort((a, b) => Number(b.issue) - Number(a.issue));
  const moments = interleave(featured.moments);
  const allMoments = index.papers.reduce((n, p) => n + p.moments.length, 0);

  const tiles: Tile[] = [
    { kind: 'cover', size: 'hero', paper: featured },
    { kind: 'feed', size: 'tall', count: allMoments },
  ];
  moments.forEach((moment, i) => {
    tiles.push({ kind: 'moment', size: sizeFor(moment), moment, paper: featured });
    if (i === 5) tiles.push({ kind: 'topics', size: 'wide' });
  });
  // Older issues get a cover each, with their best strip beside it.
  for (const paper of others) {
    tiles.push({ kind: 'cover', size: 'wide', paper });
    const best = paper.moments.find(m => m.kind === 'strip');
    if (best) tiles.push({ kind: 'moment', size: 'square', moment: best, paper });
  }
  return tiles;
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
