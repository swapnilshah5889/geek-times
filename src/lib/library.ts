import type { Archive } from '../data/load';
import type { GraphNode, LibraryVolume, Media, GraphRelation, Library, LibraryCompany, LibraryField, LibraryIssue, LibraryStory, SearchEntry, StoryRole } from '../types';

// Helpers over the library (the editorial layer: stories, issues, companies and the idea graph).

export const sampleMedia = (kind: string): Media => ({
  type: 'svg', src: `samples/${kind}.svg`, width: 400, height: 250, alt: `Sample art (${kind}).`,
});

export const roleLabel: Record<StoryRole, string> = {
  lead: 'Lead', feature: 'Feature', brief: 'Brief', vault: 'From the vault', real_world: 'In the real world',
};

export const trustLabel = (t?: LibraryStory['trust']) =>
  t === 'peer_reviewed' ? 'Peer-reviewed paper' : t === 'company_reported' ? 'Company-reported' : t === 'preprint' ? 'Preprint' : '';

export const storyById = (lib: Library, id: string): LibraryStory | undefined => lib.stories.find(s => s.id === id);
export const storiesOf = (lib: Library, ids: string[]): LibraryStory[] =>
  ids.map(id => storyById(lib, id)).filter((s): s is LibraryStory => !!s);
export const fieldOf = (lib: Library, id: string): LibraryField | undefined => lib.fields.find(f => f.id === id);
export const issueById = (lib: Library, id: string): LibraryIssue | undefined => lib.issues.find(i => i.id === id);
export const companyById = (lib: Library, id: string): LibraryCompany | undefined => lib.companies.find(c => c.id === id);
/** Issues are collections of already-published stories; a story can appear in more than one. */
export const issuesWith = (lib: Library, storyId: string): LibraryIssue[] => lib.issues.filter(i => i.stories?.includes(storyId));
export const volumeOf = (lib: Library, issue: LibraryIssue): LibraryVolume | undefined => lib.volumes.find(v => v.id === issue.volume);
export const latestIssue = (lib: Library): LibraryIssue => lib.issues.find(i => !i.sample) ?? lib.issues[0];
export const realPaper = (archive: Archive, story: LibraryStory): SearchEntry | undefined =>
  story.real ? archive.index.papers.find(p => p.slug === story.id) : undefined;

/** The full headline, joining the accent phrase when a story has one ("One word," + "two worlds."). */
export const headlineOf = (s: LibraryStory) => (s.accent ? `${s.headline} ${s.accent}` : s.headline);

export const byline = (s: LibraryStory) => (s.authors ? `${s.title} · ${s.authors}, ${s.year}` : s.title);

/** Everything that led to `id` (oldest first) and what grew directly from it. */
export function familyOf(lib: Library, id: string): { before: GraphNode[]; after: GraphNode[]; links: GraphRelation[] } {
  const node = (n: string) => lib.nodes.find(x => x.id === n);
  const before: GraphNode[] = [];
  const seen = new Set<string>([id]);
  let frontier = [id];
  while (frontier.length) {
    const next: string[] = [];
    for (const rel of lib.relations) {
      if (frontier.includes(rel.to) && !seen.has(rel.from)) {
        seen.add(rel.from); next.push(rel.from);
        const n = node(rel.from); if (n) before.push(n);
      }
    }
    frontier = next;
  }
  const after = lib.relations.filter(r => r.from === id).map(r => node(r.to)).filter((n): n is GraphNode => !!n);
  const ids = new Set([id, ...before.map(n => n.id), ...after.map(n => n.id)]);
  return {
    before: before.sort((a, b) => a.year - b.year),
    after: after.sort((a, b) => a.year - b.year),
    links: lib.relations.filter(r => ids.has(r.from) && ids.has(r.to)),
  };
}

/** Reads left to right along an arrow that points forward in time (earlier idea → later work). */
export const relationForward = { builds_on: 'built on by', improves_on: 'improved on by', uses_method: 'method used by' } as const;

export const relationLabel = { builds_on: 'builds on', improves_on: 'improves on', uses_method: 'uses the method of' } as const;
