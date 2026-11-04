// Checks every paper's data against the tag vocabulary, then writes public/data/search-index.json.
// Runs before `dev` and `build`; exits with an error if anything is wrong, so bad data never ships.
// Later the database enforces the same rules and search runs as a query, but the checks stay useful
// for reviewing AI-generated issues before they are imported.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Cover, Moment, PaperDoc, PaperTag, SearchIndex, SiteConfig, TagBasis, TagVocabulary } from '../src/types.ts';

const PUBLIC = join(import.meta.dirname, '..', 'public');
const read = <T>(path: string): T => JSON.parse(readFileSync(join(PUBLIC, path), 'utf8')) as T;

const errors: string[] = [];
const warnings: string[] = [];
const BASES: TagBasis[] = ['paper', 'background', 'editorial'];

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

function checkPaperTags(doc: PaperDoc, known: Set<string>): PaperTag[] {
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
    if (t.basis === 'paper' && !t.evidence?.startsWith(doc.paper.url)) {
      errors.push(`${label}: basis "paper" needs an evidence link into ${doc.paper.url}`);
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
function coverOf(doc: PaperDoc): Cover | undefined {
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
function momentsOf(doc: PaperDoc): Moment[] {
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
          figure: f.figure, text: plain(f.text), media: f.media, provenance: 'evidence', href: link(block.id) });
      });
    }
  }
  return out;
}

const site = read<SiteConfig>('data/site.json');
const vocab = read<TagVocabulary>('data/tags.json');
const known = new Set(checkVocabulary(vocab).keys());

const index: SearchIndex = { schemaVersion: 1, featured: site.defaultPaper, papers: [] };
for (const entry of site.papers) {
  const doc = read<PaperDoc>(entry.dataUrl);
  if (doc.slug !== entry.slug) errors.push(`${entry.dataUrl}: slug "${doc.slug}" does not match site.json "${entry.slug}"`);
  const tags = checkPaperTags(doc, known);
  const cover = coverOf(doc);
  if (!cover) { errors.push(`${entry.dataUrl}: needs a "cover" or a lead block`); continue; }
  index.papers.push({
    slug: doc.slug,
    title: doc.paper.title,
    pageTitle: doc.pageTitle,
    summary: doc.summary,
    authors: doc.paper.authors,
    year: doc.paper.year,
    issue: doc.issue.number,
    cover,
    moments: momentsOf(doc),
    tags: tags.map(t => ({ id: t.tag, relevance: t.relevance })).sort((a, b) => b.relevance - a.relevance),
  });
}

warnings.forEach(w => console.warn(`warning: ${w}`));
if (errors.length) {
  errors.forEach(e => console.error(`error: ${e}`));
  console.error(`\n${errors.length} problem(s) in the data. Nothing was written.`);
  process.exit(1);
}
writeFileSync(join(PUBLIC, 'data', 'search-index.json'), JSON.stringify(index, null, 2) + '\n');
const moments = index.papers.reduce((n, p) => n + p.moments.length, 0);
console.log(`search index: ${index.papers.length} paper(s), ${moments} moments, ${vocab.tags.length} tags in vocabulary`);
