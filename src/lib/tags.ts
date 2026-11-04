import type { FacetDef, SearchEntry, SearchIndex, TagDef, TagVocabulary } from '../types';

// Tag lookups and paper search. This runs in the browser over the prebuilt index for now;
// with a database the same rules become a query (tag ids + ancestors, full-text on title and summary).

export interface TagLookup {
  facets: FacetDef[];
  get(id: string): TagDef | undefined;
  /** The tag and every broader tag above it, nearest first. */
  lineage(id: string): TagDef[];
}

export function tagLookup(vocab: TagVocabulary): TagLookup {
  const byId = new Map(vocab.tags.map(t => [t.id, t]));
  return {
    facets: vocab.facets,
    get: id => byId.get(id),
    lineage(id) {
      const out: TagDef[] = [];
      for (let t = byId.get(id); t && !out.includes(t); t = t.parent ? byId.get(t.parent) : undefined) out.push(t);
      return out;
    },
  };
}

/** Link to the search page, optionally filtered by tags and a query. */
export function searchHref({ q, tags = [] }: { q?: string; tags?: string[] } = {}): string {
  const params = new URLSearchParams({ search: '' });
  if (q) params.set('q', q);
  tags.forEach(t => params.append('tag', t));
  return `?${params.toString().replace('search=', 'search')}`;
}

const STOPWORDS = new Set('a an and are about do does for how in is it of on or the to what why with'.split(' '));

const normalize = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();

/** Trims common English endings so "translating", "translation" and "translations" meet. */
const stem = (w: string) => (w.length > 5 ? w.replace(/(ations?|ating|ions?|ings?|ers?|ed|es|s)$/, '') : w);

function words(s: string): string[] {
  return normalize(s).split(' ').filter(w => w && !STOPWORDS.has(w)).map(stem);
}

/** True when every query word starts one of the text's words ("attent" matches "self attention"). */
function matches(text: string, query: string[]): boolean {
  const have = normalize(text).split(' ').map(stem);
  return query.every(q => have.some(w => w.startsWith(q)));
}

export interface SearchResult {
  entry: SearchEntry;
  score: number;
  /** Tags that matched the query or the filters, most relevant first. */
  matched: TagDef[];
}

/**
 * Ranks papers for a text query and an AND-list of tag filters.
 * A filter on a broad tag also finds papers tagged with narrower ones (Attention finds Self-attention).
 */
export function searchPapers(index: SearchIndex, tags: TagLookup, query: string, filters: string[]): SearchResult[] {
  const q = words(query);
  const results: SearchResult[] = [];

  for (const entry of index.papers) {
    // Every tag on the paper, plus the broader tags above it, with the paper's relevance.
    const reach = new Map<string, number>();
    for (const { id, relevance } of entry.tags) {
      for (const t of tags.lineage(id)) reach.set(t.id, Math.max(reach.get(t.id) ?? 0, relevance));
    }
    if (!filters.every(f => reach.has(f))) continue;

    let score = filters.reduce((sum, f) => sum + (reach.get(f) ?? 0), 0);
    const matched = new Set(filters);
    if (q.length) {
      if (matches(entry.title, q)) score += 3;
      if (matches(entry.pageTitle, q)) score += 2;
      if (matches(entry.summary, q)) score += 1;
      for (const [id, relevance] of reach) {
        const tag = tags.get(id);
        if (tag && [tag.label, ...(tag.aliases ?? [])].some(name => matches(name, q))) {
          score += 2 * relevance;
          matched.add(id);
        }
      }
      if (score === 0) continue;
    }
    results.push({
      entry,
      score,
      matched: [...matched].map(id => tags.get(id)!).filter(Boolean).sort((a, b) => (reach.get(b.id) ?? 0) - (reach.get(a.id) ?? 0)),
    });
  }
  return results.sort((a, b) => b.score - a.score || b.entry.year - a.entry.year);
}

/** How many papers use each tag (directly or through a narrower tag), for the browse list. */
export function tagCounts(index: SearchIndex, tags: TagLookup): Map<string, number> {
  const counts = new Map<string, number>();
  for (const entry of index.papers) {
    const reach = new Set(entry.tags.flatMap(t => tags.lineage(t.id).map(d => d.id)));
    reach.forEach(id => counts.set(id, (counts.get(id) ?? 0) + 1));
  }
  return counts;
}
