// Checks every story's data (a paper or a company blog post) against the tag vocabulary, then writes
// public/data/search-index.json. Runs before `dev` and `build`; exits with an error if anything is wrong,
// so bad data never ships. These checks are structure and link checks only: they do not verify that a
// claim is true. That is the fact-check step (skills/fact-check). Later the database enforces the same
// rules and search runs as a query, but the checks stay useful for reviewing AI-generated issues before import.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Cover, Library, Moment, PaperTag, SearchIndex, SiteConfig, SourceKind, StoryDoc, TagBasis, TagVocabulary } from '../src/types.ts';

const PUBLIC = join(import.meta.dirname, '..', 'public');
const read = <T>(path: string): T => JSON.parse(readFileSync(join(PUBLIC, path), 'utf8')) as T;

const errors: string[] = [];
const warnings: string[] = [];
const BASES: TagBasis[] = ['paper', 'background', 'editorial'];

const isUrl = (s: unknown) => typeof s === 'string' && /^https?:\/\/\S+$/.test(s);
/** A real calendar date written as YYYY-MM-DD (rejects 2026-02-30). */
function isIsoDate(s: unknown): boolean {
  const m = typeof s === 'string' ? /^(\d{4})-(\d{2})-(\d{2})$/.exec(s) : null;
  if (!m) return false;
  const [y, mo, d] = [+m[1], +m[2] - 1, +m[3]];
  const t = new Date(Date.UTC(y, mo, d));
  return t.getUTCFullYear() === y && t.getUTCMonth() === mo && t.getUTCDate() === d;
}

/** What a story is based on, in the shape the search index uses. */
interface Source { kind: SourceKind; title: string; authors: string; year: number; urls: string[] }

/**
 * Checks the story's source block: `paper` (the default when `kind` is missing) or `blog`, never both.
 * Returns undefined when the block is unusable; the errors say why.
 */
function checkSource(doc: StoryDoc): Source | undefined {
  const where = `${doc.slug}.json`;
  const kind = (doc.kind ?? 'paper') as SourceKind;
  if (kind !== 'paper' && kind !== 'blog') {
    errors.push(`${where}: kind must be "paper" or "blog", not "${String(doc.kind)}"`);
    return undefined;
  }

  if (kind === 'paper') {
    if (doc.blog) errors.push(`${where}: a paper story must not have a "blog" block (set "kind": "blog" or remove the block)`);
    const p = doc.paper;
    if (!p) { errors.push(`${where}: a paper story needs a "paper" block (title, authors, year, url)`); return undefined; }
    if (!p.title?.trim() || !p.authors?.trim()) errors.push(`${where}: paper.title and paper.authors are required`);
    if (!Number.isInteger(p.year)) errors.push(`${where}: paper.year must be a whole number`);
    if (!isUrl(p.url)) errors.push(`${where}: paper.url must be an http(s) link to the paper`);
    return { kind, title: p.title, authors: p.authors, year: p.year, urls: [p.url] };
  }

  if (doc.paper) errors.push(`${where}: a blog story must not have a "paper" block (use "blog")`);
  const b = doc.blog;
  if (!b) { errors.push(`${where}: kind "blog" needs a "blog" block (title, organization, published, url, trust)`); return undefined; }
  if (!b.title?.trim()) errors.push(`${where}: blog.title is required`);
  if (!b.organization?.trim()) errors.push(`${where}: blog.organization is required (the company or team that wrote the post)`);
  if (!isIsoDate(b.published)) errors.push(`${where}: blog.published is required as a real date, YYYY-MM-DD`);
  if (!isUrl(b.url)) errors.push(`${where}: blog.url is required (the live post, as an http(s) link)`);
  if (b.archivedUrl !== undefined && !isUrl(b.archivedUrl)) errors.push(`${where}: blog.archivedUrl must be an http(s) link when given`);
  if (b.trust !== 'company_reported') {
    errors.push(`${where}: blog.trust must be "company_reported": a company's own post is never independently verified`);
  }
  return {
    kind, title: b.title, authors: b.organization, year: Number(String(b.published).slice(0, 4)),
    urls: [b.url, b.archivedUrl].filter((u): u is string => !!u),
  };
}

/**
 * A measured result needs a link to where it was measured. For a blog, the result is the company's own
 * measurement: the reminder is a warning, because the check cannot tell whether the number is right.
 */
function checkMeasuredResults(doc: StoryDoc, source?: Source) {
  const where = `${doc.slug}.json`;
  for (const block of doc.blocks) {
    if (block.type !== 'facts') continue;
    for (const f of block.facts) {
      if (f.claim !== 'measured_result') continue;
      if (!f.source?.url) errors.push(`${where}: measured result "${f.figure}" needs a source.url (the section or post where it was measured)`);
      if (source?.kind === 'blog') {
        warnings.push(`${where}: measured result "${f.figure}" is company-reported (the company's own measurement, not independently verified)`);
      }
    }
  }
}

function checkVocabulary(vocab: TagVocabulary) {
  const facets = new Set(vocab.facets.map(f => f.id));
  const byId = new Map(vocab.tags.map(t => [t.id, t]));
  if (byId.size !== vocab.tags.length) errors.push('tags.json: duplicate tag ids');
  for (const tag of vocab.tags) {
    if (!facets.has(tag.facet)) errors.push(`tags.json: ${tag.id} has unknown facet "${tag.facet}"`);
    if (!/^[a-z]+\/[a-z0-9-]+$/.test(tag.id) || !tag.id.startsWith(`${tag.facet}/`)) {
      errors.push(`tags.json: ${tag.id} must look like "${tag.facet}/lowercase-slug"`);
    }
    if (tag.parent) {
      const parent = byId.get(tag.parent);
      if (!parent) errors.push(`tags.json: ${tag.id} has missing parent ${tag.parent}`);
      else if (parent.facet !== tag.facet) errors.push(`tags.json: ${tag.id} and its parent are in different facets`);
    }
    // Walk up the parents to catch loops.
    const seen = new Set<string>();
    for (let t = tag; t?.parent; t = byId.get(t.parent)!) {
      if (seen.has(t.id)) { errors.push(`tags.json: parent loop at ${tag.id}`); break; }
      seen.add(t.id);
    }
  }
  return byId;
}

function checkPaperTags(doc: StoryDoc, known: Set<string>, sourceUrls: string[]): PaperTag[] {
  const where = `${doc.slug}.json`;
  if (!doc.summary?.trim()) errors.push(`${where}: missing summary`);
  if (!Array.isArray(doc.tags) || doc.tags.length === 0) errors.push(`${where}: no tags`);
  const seen = new Set<string>();
  for (const t of doc.tags ?? []) {
    const label = `${where}: tag ${t.tag}`;
    if (seen.has(t.tag)) errors.push(`${label} is listed twice`);
    seen.add(t.tag);
    if (!(t.relevance >= 0 && t.relevance <= 1)) errors.push(`${label}: relevance must be between 0 and 1`);
    if (!BASES.includes(t.basis)) errors.push(`${label}: basis must be one of ${BASES.join(', ')}`);
    // The evidence must link into the story's own source (the paper, or the blog post or its archive copy).
    if (t.basis === 'paper' && sourceUrls.length && !sourceUrls.some(u => t.evidence?.startsWith(u))) {
      errors.push(`${label}: basis "paper" needs an evidence link into ${sourceUrls.join(' or ')}`);
    }
    if (!known.has(t.tag)) {
      if (!t.proposed) errors.push(`${label} is not in tags.json (add it, or describe it under "proposed")`);
      else warnings.push(`${label} is a proposed new tag: "${t.proposed.label}" (add it to tags.json to use it)`);
      if (t.status === 'approved') errors.push(`${label} is approved but not in tags.json`);
    }
    if (t.status === 'suggested') warnings.push(`${label} is waiting for review`);
  }
  // Only reviewed tags that exist in the vocabulary reach readers.
  return (doc.tags ?? []).filter(t => t.status === 'approved' && known.has(t.tag));
}

/** Captions may hold inline markup; cards are links themselves, so they get plain text. */
const plain = (rich: string) => rich.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();

/** The paper's home page cover: its own `cover`, or else built from the lead block. */
function coverOf(doc: StoryDoc): Cover | undefined {
  const lead = doc.blocks.find(b => b.type === 'lead');
  const base = doc.cover ?? (lead && { kicker: lead.kicker, headline: lead.headline, dek: lead.deck, media: lead.slideshow.slides[0].media });
  if (!base) return undefined;
  const hook = doc.hook ?? base.hook;
  if (hook) {
    for (const key of ['sticker', 'teaser', 'cta'] as const) {
      if (!hook[key]?.trim()) errors.push(`${doc.slug}.json: hook.${key} is empty`);
    }
    if (!(hook.readMinutes > 0)) errors.push(`${doc.slug}.json: hook.readMinutes must be a positive number`);
    if (hook.frames && hook.frames.length < 2) errors.push(`${doc.slug}.json: hook.frames needs at least two frames`);
  } else warnings.push(`${doc.slug}.json: no hook, so its front-page tile will be plain`);
  return { ...base, hook };
}

/** Bite-size cards for the home page and feed: every comic strip, story chapter and fact. */
function momentsOf(doc: StoryDoc): Moment[] {
  const where = `${doc.slug}.json`;
  const link = (anchor?: string) => `papers/${doc.slug}${anchor ? `#${anchor}` : ''}`;
  const out: Moment[] = [];
  for (const block of doc.blocks) {
    if (block.type === 'comic') {
      block.strips.forEach((strip, i) => {
        const pick = strip.coverPanel ?? strip.panels.length - 1;
        const panel = strip.panels[pick];
        if (!panel) { errors.push(`${where}: strip "${strip.title}" coverPanel ${pick} does not exist`); return; }
        const id = strip.id ?? `${block.id}-${i + 1}`;
        out.push({ id, paper: doc.slug, kind: 'strip', kicker: `How it works · ${String(i + 1).padStart(2, '0')}`,
          title: strip.title, text: plain(panel.caption), media: panel.media, provenance: strip.provenance, href: link(id) });
      });
    } else if (block.type === 'story') {
      block.chapters.forEach((ch, i) => {
        const id = `${block.id}-${i + 1}`;
        out.push({ id, paper: doc.slug, kind: 'chapter', kicker: ch.part, title: ch.title, text: plain(ch.caption),
          media: ch.media, provenance: ch.provenance, href: link(id) });
      });
    } else if (block.type === 'facts') {
      block.facts.forEach((f, i) => {
        out.push({ id: `${block.id}-${i + 1}`, paper: doc.slug, kind: 'fact', kicker: 'From the paper', title: f.figure,
          figure: f.figure, text: plain(f.text), media: f.media, provenance: 'evidence', claim: f.claim, sourceLabel: f.source?.label, href: link(block.id) });
      });
    }
  }
  return out;
}

const site = read<SiteConfig>('data/site.json');
const vocab = read<TagVocabulary>('data/tags.json');
const known = new Set(checkVocabulary(vocab).keys());

const index: SearchIndex = { schemaVersion: 1, featured: site.defaultPaper, papers: [] };
const storyKind = new Map<string, SourceKind>();
for (const entry of site.papers) {
  const doc = read<StoryDoc>(entry.dataUrl);
  if (doc.slug !== entry.slug) errors.push(`${entry.dataUrl}: slug "${doc.slug}" does not match site.json "${entry.slug}"`);
  const source = checkSource(doc);
  storyKind.set(doc.slug, (doc.kind ?? 'paper') as SourceKind);
  checkMeasuredResults(doc, source);
  const tags = checkPaperTags(doc, known, source?.urls ?? []);
  const cover = coverOf(doc);
  if (!cover) { errors.push(`${entry.dataUrl}: needs a "cover" or a lead block`); continue; }
  if (!source) continue;
  index.papers.push({
    slug: doc.slug,
    title: source.title,
    pageTitle: doc.pageTitle,
    summary: doc.summary,
    authors: source.authors,
    year: source.year,
    desk: doc.desk,
    cover,
    moments: momentsOf(doc),
    tags: tags.map(t => ({ id: t.tag, relevance: t.relevance })).sort((a, b) => b.relevance - a.relevance),
  });
}

// The library (front page, issues, companies, map) must only point at things that exist.
const library = read<Library>('data/library.json');
const storyIds = new Set(library.stories.map(s => s.id));
const nodeIds = new Set(library.nodes.map(n => n.id));
const need = (ok: boolean, msg: string) => { if (!ok) errors.push(`library.json: ${msg}`); };
for (const s of library.stories) {
  if (s.real) {
    const kind = storyKind.get(s.id);
    need(kind !== undefined, `story "${s.id}" is real but has no story file in site.json`);
    // A real library entry must say the same kind of source as its file, so a blog is never listed as a paper.
    if (kind) need(s.kind === kind, `story "${s.id}" is "${s.kind}" in the library but its file is a ${kind} story`);
  } else need(s.kind === 'blog' || !!s.art, `sample story "${s.id}" needs an "art" kind`);
  need(s.fields.every(f => library.fields.some(x => x.id === f)), `story "${s.id}" has an unknown field`);
}
const refs: [string, string[]][] = [
  ['front.aside', library.front.aside], ['front.more', library.front.more], ['front.real', library.front.real],
  ['front.lead', [library.front.lead]], ['front.vault', [library.front.vault]],
  ...library.front.topics.map((t): [string, string[]] => [`front.topics.${t.field}`, t.stories]),
  ...library.issues.map((i): [string, string[]] => [`issue ${i.id}`, i.stories ?? []]),
  ...library.companies.map((c): [string, string[]] => [`company ${c.id} posts`, c.posts]),
];
for (const [where, ids] of refs) for (const id of ids) need(storyIds.has(id), `${where} points at unknown story "${id}"`);
for (const i of library.issues) need(library.volumes.some(v => v.id === i.volume), `issue ${i.id} is in unknown volume "${i.volume}"`);
for (const c of library.companies) for (const id of c.builtOn) need(nodeIds.has(id), `company ${c.id} builds on unknown node "${id}"`);
for (const n of library.nodes) if (n.story) need(storyIds.has(n.story), `node "${n.id}" points at unknown story "${n.story}"`);
for (const r of library.relations) need(nodeIds.has(r.from) && nodeIds.has(r.to), `relation ${r.from} → ${r.to} points at an unknown node`);
for (const sl of library.front.storylines) need(library.storylines.some(x => x.id === sl), `front.storylines has unknown "${sl}"`);

warnings.forEach(w => console.warn(`warning: ${w}`));
if (errors.length) {
  errors.forEach(e => console.error(`error: ${e}`));
  console.error(`\n${errors.length} problem(s) in the data. Nothing was written.`);
  process.exit(1);
}
writeFileSync(join(PUBLIC, 'data', 'search-index.json'), JSON.stringify(index, null, 2) + '\n');
const moments = index.papers.reduce((n, p) => n + p.moments.length, 0);
console.log(`search index: ${index.papers.length} paper(s), ${moments} moments, ${vocab.tags.length} tags in vocabulary`);
