// Publish one story version to Supabase in a single pg transaction (contract: docs/handoffs/v1-schema-contract.md,
// "Importer / publish transaction"; decisions 42, 46, 48). Server-side only. It connects with SUPABASE_DB_URL and
// never calls the Supabase HTTP API. Run with:
//
//   npm run publish:supabase -- <slug>
//
// Reads public/data/papers/<slug>.json, its entry in public/data/library.json and the vocabulary in tags.json.
// Pure checks run before the connection opens. Checks that need the database run inside the transaction. Any
// failure rolls back, so the previous live version stays authoritative. A document that matches the live
// version exits 0 and writes nothing.

import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import pg from 'pg';
import { STORY_SCHEMA_VERSION, storyVersionMessage } from '../src/types.ts';
import type {
  BlockType, BlogSource, ClaimKind, Library, LibraryStory, Media, Provenance, SourceKind, StoryDoc, StoryRole,
  TagBasis, TagVocabulary,
} from '../src/types.ts';

type Trust = NonNullable<LibraryStory['trust']>;
type MomentKind = 'lead' | 'hook' | 'chapter' | 'strip_panel' | 'fact';

const PUBLIC = join(import.meta.dirname, '..', 'public');
const TRUSTS: readonly Trust[] = ['peer_reviewed', 'preprint', 'company_reported'];
const ROLES: readonly StoryRole[] = ['lead', 'feature', 'brief', 'vault', 'real_world'];
const CLAIMS: readonly ClaimKind[] = ['illustration', 'model_design', 'measured_result'];
const BASES: readonly TagBasis[] = ['paper', 'background', 'editorial'];
const PROVENANCES: readonly Provenance[] = ['illustration', 'evidence', 'model_design'];
const BLOCK_TYPES: readonly BlockType[] = ['lead', 'story', 'comic', 'facts'];
const MEDIA_TYPES: readonly Media['type'][] = ['svg', 'image', 'video'];
/** Strip and chapter provenance (decision 47) becomes the moment's claim. `evidence` is the measured-result kind. */
const CLAIM_OF: Record<Provenance, ClaimKind> = {
  illustration: 'illustration', model_design: 'model_design', evidence: 'measured_result',
};

/** A check that failed. Thrown, caught in main(), printed, and the transaction is rolled back. */
class Abort extends Error {}
function abort(msg: string): never {
  throw new Abort(msg);
}
function die(msg: string): never {
  console.error(msg);
  process.exit(1);
}

// ---------- Small helpers ----------

const isNonEmpty = (s: unknown): s is string => typeof s === 'string' && s.trim().length > 0;
const isUrl = (s: unknown): s is string => typeof s === 'string' && /^https?:\/\/\S+$/.test(s);
const isPositiveInt = (n: unknown): n is number => Number.isInteger(n) && (n as number) > 0;

/** A real calendar date written as YYYY-MM-DD (rejects 2026-02-30). */
function isIsoDate(s: unknown): s is string {
  const m = typeof s === 'string' ? /^(\d{4})-(\d{2})-(\d{2})$/.exec(s) : null;
  if (!m) return false;
  const [y, mo, d] = [+m[1], +m[2] - 1, +m[3]];
  const t = new Date(Date.UTC(y, mo, d));
  return t.getUTCFullYear() === y && t.getUTCMonth() === mo && t.getUTCDate() === d;
}

function needText(v: unknown, what: string): string {
  if (!isNonEmpty(v)) abort(`${what} is empty`);
  return v;
}

function oneOf<T extends string>(list: readonly T[], v: unknown, what: string): T {
  if (typeof v !== 'string' || !(list as readonly string[]).includes(v)) {
    abort(`${what} must be one of ${list.join(', ')}; found "${String(v)}"`);
  }
  return v as T;
}

/** Captions may hold inline markup. Moments and cards get plain text (same rule as scripts/build-index.ts). */
const plain = (rich: string) => rich.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();

/** The URL without its #fragment. Source identity is the URL without the fragment. */
const stripHash = (url: string) => url.split('#')[0];
/** The fragment as an anchor ("#S3.SS2"), or null when the link has none. */
const anchorOf = (url: string) => {
  const i = url.indexOf('#');
  return i >= 0 ? url.slice(i) : null;
};

/** Deterministic JSON: object keys sorted at every level, undefined dropped. Used for every hash. */
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value) ?? 'null';
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).filter(k => obj[k] !== undefined).sort();
  return `{${keys.map(k => `${JSON.stringify(k)}:${canonical(obj[k])}`).join(',')}}`;
}
const sha256 = (s: string) => createHash('sha256').update(s).digest('hex');

/** Every value in the tree with its dotted/indexed path, in document order. */
function* walk(value: unknown, path: string): Generator<[string, unknown]> {
  yield [path, value];
  if (Array.isArray(value)) {
    for (const [i, item] of value.entries()) yield* walk(item, `${path}[${i}]`);
  } else if (value !== null && typeof value === 'object') {
    for (const [k, item] of Object.entries(value)) yield* walk(item, path ? `${path}.${k}` : k);
  }
}

// ---------- Plan: everything the transaction will write, checked before the connection opens ----------

interface SourcePlan {
  kind: SourceKind; url: string; title: string; authors: string; year: number;
  organization: string | null; trust: Trust;
}
interface MediaPlan { path: string; kind: Media['type']; width: number; height: number; alt: string | null }
interface TagPlan {
  tagKey: string; relevance: number; basis: TagBasis; evidence: string | null;
  source: 'ai' | 'editor';
}
interface MomentPlan {
  key: string; kind: MomentKind; position: number; claim: ClaimKind | null; trust: Trust | null;
  sourceLabel: string | null; sourceUrl: string | null; mediaSrc: string | null;
  headline: string | null; text: string | null; ref: string;
}
type MomentInput = Omit<MomentPlan, 'position' | 'trust'>;
interface FactPlan {
  blockId: string; position: number; figure: string; claim: ClaimKind; text: string;
  sourceLabel: string | null; sourceUrl: string | null; mediaSrc: string | null;
}
interface CitationPlan { url: string; anchor: string | null; label: string; context: string }

interface Plan {
  slug: string;
  kind: SourceKind;
  source: SourcePlan;
  snapshot: { archivedUrl: string; retrievedOn: string } | null;
  meta: {
    headline: string; accent: string | null; dek: string; summary: string; pageTitle: string; desk: string;
    authors: string; year: number; trust: Trust; minutes: number; role: StoryRole; note: string | null;
    sourceUrl: string; sourceArchivedUrl: string | null;
  };
  sample: boolean;
  fieldSlugs: string[];
  tags: TagPlan[];
  media: MediaPlan[];
  moments: MomentPlan[];
  facts: FactPlan[];
  citations: CitationPlan[];
  documentJson: string;
  libraryJson: string;
  documentHash: string;
  payloadHash: string;
}

/**
 * Pure checks, in order. Each one aborts with a message that names the field. Nothing here touches the database.
 * The order is the contract's step 2, minus the checks that need a row (story exists, live hash): those run in publish().
 */
function validate(slug: string, raw: unknown, library: Library, vocab: TagVocabulary, warnings: string[]): Plan {
  // 1. Schema version (decision 46).
  const version = (raw as { schemaVersion?: unknown } | null)?.schemaVersion;
  if (version !== STORY_SCHEMA_VERSION) abort(storyVersionMessage(slug, version));
  const doc = raw as StoryDoc;
  if (doc.slug !== slug) abort(`the story file's slug is "${String(doc.slug)}", not "${slug}"`);

  // 2. Library entry must exist and agree on kind (the contract's "missing library entry" and "slug mismatch" cases).
  const entry = library.stories.find(s => s.id === slug);
  if (!entry) abort(`no library entry for "${slug}" in public/data/library.json (the front page needs one)`);
  const kind: SourceKind = doc.kind ?? 'paper';
  if (kind !== 'paper' && kind !== 'blog') abort(`kind must be "paper" or "blog", not "${String(doc.kind)}"`);
  if (entry.kind !== kind) abort(`library entry says kind "${entry.kind}" but the story is "${kind}"`);

  // 3. Explicit metadata columns (contract, published_version). Invalid enums abort.
  const trust = oneOf(TRUSTS, entry.trust, `library trust for "${slug}"`);
  const role = oneOf(ROLES, entry.role, `library role for "${slug}"`);
  const headline = needText(entry.headline, 'library headline');
  const dek = needText(entry.dek, 'library dek');
  const desk = needText(entry.desk, 'library desk');
  const authors = needText(entry.authors, 'library authors');
  const summary = needText(doc.summary, 'document summary');
  const pageTitle = needText(doc.pageTitle, 'document pageTitle');
  const docDesk = needText(doc.desk, 'document desk');
  if (docDesk !== desk) {
    warnings.push(`desk: the library says "${desk}" and the document says "${docDesk}"; the version stores the library desk`);
  }
  if (!Number.isInteger(entry.year)) abort('library year must be a whole number');
  if (!isPositiveInt(entry.minutes)) abort('library minutes must be a positive whole number');
  if (typeof entry.sample !== 'boolean') abort('library sample must be true or false');
  for (const f of entry.fields) {
    if (!library.fields.some(x => x.id === f)) abort(`library field "${String(f)}" is not in library.fields`);
  }

  // 4. Source (the paper, or the blog post). Its url is what citations and story_source point at.
  let source: SourcePlan;
  let archived: string | null = null;
  let snapshot: Plan['snapshot'] = null;
  if (kind === 'paper') {
    const p = doc.paper;
    if (doc.blog) abort('a paper story must not have a "blog" block');
    if (!p || !isNonEmpty(p.title) || !isNonEmpty(p.authors)) abort('a paper story needs a "paper" block with title and authors');
    if (!Number.isInteger(p.year)) abort('paper.year must be a whole number');
    if (!isUrl(p.url)) abort('paper.url must be an http(s) link to the paper');
    source = { kind, url: p.url, title: p.title, authors: p.authors, year: p.year, organization: null, trust };
  } else {
    const b = doc.blog;
    if (doc.paper) abort('a blog story must not have a "paper" block');
    if (!b || !isNonEmpty(b.title) || !isNonEmpty(b.organization)) abort('a blog story needs a "blog" block with title and organization');
    if (!isIsoDate(b.published)) abort('blog.published must be a real date, YYYY-MM-DD');
    if (!isUrl(b.url)) abort('blog.url must be the live post, as an http(s) link');
    if (b.trust !== 'company_reported') abort('blog.trust must be "company_reported"');
    if (trust !== b.trust) abort(`library trust "${trust}" disagrees with blog.trust "${b.trust}"`);
    if (b.archivedUrl !== undefined) {
      if (!isUrl(b.archivedUrl)) abort('blog.archivedUrl must be an http(s) link when given');
      archived = b.archivedUrl;
      // retrievedOn is not in the BlogSource type yet. Without it there is no date for source_snapshot.
      const retrievedOn = (b as BlogSource & { retrievedOn?: unknown }).retrievedOn;
      if (retrievedOn === undefined) {
        warnings.push('blog.archivedUrl has no retrievedOn date, so no source_snapshot row is written');
      } else if (isIsoDate(retrievedOn)) {
        snapshot = { archivedUrl: archived, retrievedOn };
      } else {
        abort('blog.retrievedOn must be a real date, YYYY-MM-DD');
      }
    }
    source = {
      kind, url: b.url, title: b.title, authors: b.organization, year: Number(b.published.slice(0, 4)),
      organization: b.organization, trust,
    };
  }
  const sourceBases = [stripHash(source.url), archived && stripHash(archived)].filter((u): u is string => !!u);

  // 5. Blocks: every block has a unique id (keys and deep links come from it).
  if (!Array.isArray(doc.blocks) || doc.blocks.length === 0) abort('the story has no blocks');
  const blockIds = new Set<string>();
  for (const [i, block] of doc.blocks.entries()) {
    oneOf(BLOCK_TYPES, block.type, `block ${i} type`);
    if (!isNonEmpty(block.id)) abort(`block ${i} (${block.type}) needs an id; moment keys are built from it`);
    if (blockIds.has(block.id)) abort(`block id "${block.id}" is used twice`);
    blockIds.add(block.id);
  }

  // 6. Hook (front-page tile).
  const hook = doc.hook ?? doc.cover?.hook;
  if (hook) {
    needText(hook.sticker, 'hook.sticker');
    needText(hook.teaser, 'hook.teaser');
    needText(hook.cta, 'hook.cta');
    if (!(hook.readMinutes > 0)) abort('hook.readMinutes must be a positive number');
    if (hook.frames && hook.frames.length < 2) abort('hook.frames needs at least two frames');
  }

  // 7. Tags: every tag approved, present in tags.json, with a valid basis and relevance (contract step 2).
  const facetIds = new Set(vocab.facets.map(f => f.id));
  const vocabTags = new Map(vocab.tags.map(t => [t.id, t] as const));
  for (const t of vocab.tags) {
    if (!facetIds.has(t.facet)) abort(`tags.json: ${t.id} has unknown facet "${t.facet}"`);
  }
  if (vocabTags.size !== vocab.tags.length) abort('tags.json has duplicate tag ids');
  if (!Array.isArray(doc.tags) || doc.tags.length === 0) abort('the story has no tags');
  const tagSeen = new Set<string>();
  const tags: TagPlan[] = doc.tags.map(t => {
    if (tagSeen.has(t.tag)) abort(`tag ${t.tag} is listed twice`);
    tagSeen.add(t.tag);
    if (t.status !== 'approved') abort(`tag ${t.tag} is "${String(t.status)}"; only approved tags can be published`);
    if (!vocabTags.has(t.tag)) abort(`tag ${t.tag} is not in public/data/tags.json`);
    const basis = oneOf(BASES, t.basis, `tag ${t.tag} basis`);
    if (!(t.relevance >= 0 && t.relevance <= 1)) abort(`tag ${t.tag} relevance must be between 0 and 1`);
    if (basis === 'paper' && !sourceBases.some(u => t.evidence?.startsWith(u))) {
      abort(`tag ${t.tag} has basis "paper" but its evidence does not link into the story's source`);
    }
    if (t.source !== 'ai' && t.source !== 'editor') abort(`tag ${t.tag} source must be "ai" or "editor"`);
    return { tagKey: t.tag, relevance: t.relevance, basis, evidence: t.evidence ?? null, source: t.source };
  });

  // 8. Media: one row per unique src across the whole document (lead, hook, chapters, panels, facts, covers).
  const mediaByPath = new Map<string, MediaPlan>();
  for (const [path, value] of walk(doc, '')) {
    if (!/(^|\.)media$/.test(path) || value === null || typeof value !== 'object') continue;
    const m = value as Partial<Media>;
    if (!isNonEmpty(m.src)) abort(`media at ${path} has no src`);
    const mediaKind = oneOf(MEDIA_TYPES, m.type, `media ${m.src} type`);
    if (!isPositiveInt(m.width) || !isPositiveInt(m.height)) {
      abort(`media ${m.src} at ${path} needs width and height (media_asset stores both)`);
    }
    const prev = mediaByPath.get(m.src);
    if (prev) {
      if (prev.kind !== mediaKind || prev.width !== m.width || prev.height !== m.height) {
        abort(`media ${m.src} is used with two different type or size; fix the document`);
      }
      if ((prev.alt ?? '') !== (m.alt ?? '')) warnings.push(`media ${m.src} has two different alt texts; the first one is stored`);
      continue;
    }
    mediaByPath.set(m.src, { path: m.src, kind: mediaKind, width: m.width, height: m.height, alt: m.alt ?? null });
  }

  // 9. Moments and facts. Keys match scripts/build-index.ts: chapter "<block>-<n>", fact "<block>-<n>", strip "<strip id or block>-<n>".
  //    Each comic panel is its own moment (strip_panel), keyed "<strip id>-p<n>".
  const claimOf = (p: Provenance | undefined): ClaimKind | null =>
    p === undefined ? null : CLAIM_OF[oneOf(PROVENANCES, p, 'provenance')];
  const sourceTrust = source.trust;
  const momentOf = (m: MomentInput): MomentPlan => ({
    ...m,
    position: 0,
    trust: m.claim === 'model_design' || m.claim === 'measured_result' ? sourceTrust : null,
  });
  const moments: MomentPlan[] = [];
  const facts: FactPlan[] = [];
  const citations: CitationPlan[] = [];

  const hookSrc = (hook?.frames?.[0]?.media ?? doc.cover?.media)?.src ?? null;
  if (hook) {
    moments.push(momentOf({
      key: 'hook', kind: 'hook', claim: null, headline: hook.sticker, text: hook.teaser, ref: 'hook',
      mediaSrc: hookSrc, sourceLabel: null, sourceUrl: null,
    }));
  }

  for (const [bi, block] of doc.blocks.entries()) {
    const id = block.id as string;
    if (block.type === 'lead') {
      const first = block.slideshow.slides[0];
      if (!first) abort(`lead "${id}" needs at least one slide`);
      moments.push(momentOf({
        key: id, kind: 'lead', claim: null,
        headline: [block.headline.text, block.headline.accent].filter(Boolean).join(' '),
        text: plain(block.deck), ref: id, mediaSrc: first.media.src, sourceLabel: null, sourceUrl: null,
      }));
    } else if (block.type === 'story') {
      block.chapters.forEach((ch, i) => {
        const key = `${id}-${i + 1}`;
        moments.push(momentOf({
          key, kind: 'chapter', claim: claimOf(ch.provenance), headline: ch.title, text: plain(ch.caption),
          ref: key, mediaSrc: ch.media.src, sourceLabel: null, sourceUrl: null,
        }));
      });
    } else if (block.type === 'comic') {
      block.strips.forEach((strip, si) => {
        const stripId = strip.id ?? `${id}-${si + 1}`;
        if (!strip.panels?.length) abort(`strip "${strip.title}" has no panels`);
        const claim = claimOf(strip.provenance);
        strip.panels.forEach((panel, pi) => moments.push(momentOf({
          key: `${stripId}-p${pi + 1}`, kind: 'strip_panel', claim, headline: strip.title,
          text: plain(panel.caption), ref: stripId, mediaSrc: panel.media.src, sourceLabel: null, sourceUrl: null,
        })));
      });
    } else {
      block.facts.forEach((f, fi) => {
        const where = `fact "${String(f.figure)}" in ${id}`;
        const claim = oneOf(CLAIMS, f.claim, `${where} claim`);
        needText(f.figure, `${where} figure`);
        needText(f.text, `${where} text`);
        if (claim === 'illustration' && f.source) abort(`${where} is an illustration and must not carry a source`);
        if (claim !== 'illustration' && !isUrl(f.source?.url)) abort(`${where} is ${claim} and needs source.url`);
        if (f.source) {
          needText(f.source.label, `${where} source.label`);
          if (!isUrl(f.source.url)) abort(`${where} source.url must be an http(s) link`);
          citations.push({
            url: f.source.url, anchor: anchorOf(f.source.url), label: f.source.label,
            context: `blocks[${bi}].facts[${fi}].source`,
          });
        }
        facts.push({
          blockId: id, position: facts.length + 1, figure: f.figure, claim, text: f.text,
          sourceLabel: f.source?.label ?? null, sourceUrl: f.source?.url ?? null, mediaSrc: f.media?.src ?? null,
        });
        moments.push(momentOf({
          key: `${id}-${fi + 1}`, kind: 'fact', claim, headline: f.figure, text: plain(f.text), ref: id,
          mediaSrc: f.media?.src ?? null, sourceLabel: f.source?.label ?? null, sourceUrl: f.source?.url ?? null,
        }));
      });
    }
  }

  const momentKeys = new Set<string>();
  for (const m of moments) {
    if (momentKeys.has(m.key)) abort(`moment key "${m.key}" appears twice in this version`);
    momentKeys.add(m.key);
    m.position = momentKeys.size;
  }
  for (const m of [...moments, ...facts]) {
    if (m.mediaSrc !== null && !mediaByPath.has(m.mediaSrc)) {
      abort(`a moment or fact points at media "${m.mediaSrc}", which is not in this version's media list`);
    }
  }

  // 10. Citations: every <a href> in the blocks (captions, decks, text) plus every fact source.
  const anchorPattern = /<a\s[^>]*?href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/g;
  for (const [path, value] of walk(doc.blocks, 'blocks')) {
    if (typeof value !== 'string' || !value.includes('<a')) continue;
    for (const m of value.matchAll(anchorPattern)) {
      const href = m[1];
      if (!isUrl(href)) abort(`${path} links to "${href}", which is not an http(s) URL`);
      citations.push({ url: href, anchor: anchorOf(href), label: plain(m[2]) || href, context: path });
    }
  }
  for (const c of citations) {
    if (!sourceBases.includes(stripHash(c.url))) {
      abort(`${c.context} links to ${c.url}, which is not this story's source (${source.url}); publish only links to the story's own source`);
    }
  }

  // 11. Fields (story_field) must exist in the library's field list.
  const fieldSlugs = entry.fields.map(String);

  const documentJson = JSON.stringify(doc);
  const libraryJson = JSON.stringify(entry);
  return {
    slug,
    kind,
    source,
    snapshot,
    meta: {
      headline, accent: entry.accent ?? null, dek, summary, pageTitle, desk, authors, year: entry.year,
      trust, minutes: entry.minutes, role, note: entry.note ?? null,
      sourceUrl: source.url, sourceArchivedUrl: archived,
    },
    sample: entry.sample,
    fieldSlugs,
    tags,
    media: [...mediaByPath.values()],
    moments,
    facts,
    citations,
    documentJson,
    libraryJson,
    documentHash: sha256(canonical(doc)),
    payloadHash: sha256(canonical({ document: doc, library_entry: entry })),
  };
}

// ---------- Transaction ----------

/**
 * Steps 1, 3 to 8 of the contract, in one pg transaction. Returns the new live version id, or null when the
 * document is unchanged (nothing written).
 */
async function publish(plan: Plan, library: Library, vocab: TagVocabulary, dbUrl: string, force = false): Promise<string | null> {
  const client = new pg.Client({ connectionString: dbUrl });
  const counts = new Map<string, number>();
  const bump = (name: string, by = 1) => counts.set(name, (counts.get(name) ?? 0) + by);
  await client.connect();
  try {
    await client.query('begin');

    // Step 1: the story row, locked for the rest of the transaction.
    const found = await client.query<{ id: string; kind: string }>(
      'select id, kind from story where slug = $1 for update', [plan.slug]);
    let storyId: string;
    if (found.rows[0]) {
      if (found.rows[0].kind !== plan.kind) abort(`story "${plan.slug}" is stored as "${found.rows[0].kind}", not "${plan.kind}"`);
      storyId = found.rows[0].id;
      await client.query('update story set sample = $2 where id = $1', [storyId, plan.sample]);
    } else {
      storyId = (await client.query<{ id: string }>(
        'insert into story (slug, kind, sample) values ($1, $2, $3) returning id',
        [plan.slug, plan.kind, plan.sample])).rows[0].id;
      bump('story');
    }

    // No-change check: the hash covers the document and the library entry (the front-page card). A document-only
    // hash would skip a headline or dek edit made in library.json.
    const live = await client.query<{ id: string; document: unknown; library_entry: unknown }>(
      `select id, document, library_entry from published_version where story_id = $1 and status = 'live'`, [storyId]);
    const liveRow = live.rows[0];
    if (liveRow && sha256(canonical({ document: liveRow.document, library_entry: liveRow.library_entry })) === plan.payloadHash) {
      if (!force) {
        await client.query('rollback');
        console.log('No change (same document hash); nothing published. Pass --force to re-publish.');
        console.log(`  live version ${liveRow.id} already holds this document. document sha256 ${plan.documentHash}`);
        return null;
      }
      console.log(`Forced re-publish: live version ${liveRow.id} has the same hash; proceeding anyway.`);
    }

    // Vocabulary mirror (contract: tags.json and library fields are mirrored into their tables on import).
    const facetIdByKey = new Map<string, string>();
    for (const [i, f] of vocab.facets.entries()) {
      const r = await client.query<{ id: string }>(
        `insert into facet (key, label, position) values ($1, $2, $3)
         on conflict (key) do update set label = excluded.label, position = excluded.position returning id`,
        [f.id, f.label, i + 1]);
      facetIdByKey.set(f.id, r.rows[0].id);
      bump('facet');
    }
    const tagIdByKey = new Map<string, string>();
    for (const t of vocab.tags) {
      const r = await client.query<{ id: string }>(
        `insert into tag (key, facet_id, label, aliases) values ($1, $2, $3, $4::text[])
         on conflict (key) do update set facet_id = excluded.facet_id, label = excluded.label, aliases = excluded.aliases
         returning id`,
        [t.id, facetIdByKey.get(t.facet), t.label, t.aliases ?? []]);
      tagIdByKey.set(t.id, r.rows[0].id);
      bump('tag');
    }
    const fieldIdBySlug = new Map<string, string>();
    for (const f of library.fields) {
      const r = await client.query<{ id: string }>(
        `insert into field (slug, label, color, cluster) values ($1, $2, $3, $4::jsonb)
         on conflict (slug) do update set label = excluded.label, color = excluded.color, cluster = excluded.cluster
         returning id`,
        [f.id, f.label, f.color, JSON.stringify(f.cluster)]);
      fieldIdBySlug.set(f.id, r.rows[0].id);
      bump('field');
    }

    // Step 3: the source row (unique on kind + url), then its archived copy if one is dated.
    const src = plan.source;
    const sourced = await client.query<{ id: string; inserted: boolean }>(
      `insert into source (kind, title, authors, year, url, organization, trust)
       values ($1, $2, $3, $4, $5, $6, $7)
       on conflict (kind, url) do update set title = excluded.title, authors = excluded.authors,
         year = excluded.year, organization = excluded.organization, trust = excluded.trust
       returning id, (xmax = 0) as inserted`,
      [src.kind, src.title, src.authors, src.year, src.url, src.organization, src.trust]);
    const sourceId = sourced.rows[0].id;
    bump(sourced.rows[0].inserted ? 'source_inserted' : 'source_updated');
    if (plan.snapshot) {
      const snap = await client.query<{ id: string }>(
        'select id from source_snapshot where source_id = $1 and archived_url = $2 and retrieved_on = $3::date',
        [sourceId, plan.snapshot.archivedUrl, plan.snapshot.retrievedOn]);
      if (!snap.rows[0]) {
        await client.query(
          'insert into source_snapshot (source_id, archived_url, retrieved_on) values ($1, $2, $3::date)',
          [sourceId, plan.snapshot.archivedUrl, plan.snapshot.retrievedOn]);
        bump('source_snapshot');
      }
    }

    // Step 4: the version row, staging, with the full document and the explicit metadata columns.
    const m = plan.meta;
    const pvId = (await client.query<{ id: string }>(
      `insert into published_version
         (story_id, story_slug, schema_version, status, document, library_entry,
          headline, accent, dek, summary, page_title, desk, authors, year, trust, minutes, role, note,
          source_url, source_archived_url)
       values ($1, $2, $3, 'staging', $4::jsonb, $5::jsonb, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17,
          $18, $19)
       returning id`,
      [storyId, plan.slug, STORY_SCHEMA_VERSION, plan.documentJson, plan.libraryJson,
        m.headline, m.accent, m.dek, m.summary, m.pageTitle, m.desk, m.authors, m.year, m.trust, m.minutes,
        m.role, m.note, m.sourceUrl, m.sourceArchivedUrl])).rows[0].id;
    bump('published_version');

    // Step 5: every derived row, each carrying published_version_id.
    await client.query(
      `insert into story_source (published_version_id, source_id, role, position) values ($1, $2, 'primary', 1)`,
      [pvId, sourceId]);
    bump('story_source');

    const mediaIdByPath = new Map<string, string>();
    for (const med of plan.media) {
      const r = await client.query<{ id: string }>(
        `insert into media_asset (published_version_id, path, kind, width, height, alt)
         values ($1, $2, $3, $4, $5, $6) returning id`,
        [pvId, med.path, med.kind, med.width, med.height, med.alt]);
      mediaIdByPath.set(med.path, r.rows[0].id);
      bump('media_asset');
    }
    const mediaRef = (src: string | null, what: string): string | null => {
      if (src === null) return null;
      const id = mediaIdByPath.get(src);
      if (id === undefined) abort(`${what} points at media "${src}", which was not inserted in this transaction`);
      return id;
    };

    for (const c of plan.citations) {
      await client.query(
        `insert into citation (published_version_id, source_id, anchor, url, label, context)
         values ($1, $2, $3, $4, $5, $6)`,
        [pvId, sourceId, c.anchor, c.url, c.label, c.context]);
      bump('citation');
    }

    for (const t of plan.tags) {
      const tagId = tagIdByKey.get(t.tagKey);
      if (tagId === undefined) abort(`tag ${t.tagKey} did not resolve to a tag row`);
      await client.query(
        `insert into story_tag (published_version_id, tag_id, relevance, basis, evidence, source_kind, status)
         values ($1, $2, $3, $4, $5, $6, 'approved')`,
        [pvId, tagId, t.relevance, t.basis, t.evidence, t.source]);
      bump('story_tag');
    }

    for (const mo of plan.moments) {
      await client.query(
        `insert into moment (published_version_id, key, kind, position, claim, trust, source_label, source_url,
           media_asset_id, headline, text, ref)
         values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`,
        [pvId, mo.key, mo.kind, mo.position, mo.claim, mo.trust, mo.sourceLabel, mo.sourceUrl,
          mediaRef(mo.mediaSrc, `moment ${mo.key}`), mo.headline, mo.text, mo.ref]);
      bump('moment');
      bump(`moment:${mo.kind}`);
    }

    for (const f of plan.facts) {
      await client.query(
        `insert into fact (published_version_id, block_id, position, figure, claim, text, source_label, source_url,
           media_asset_id)
         values ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
        [pvId, f.blockId, f.position, f.figure, f.claim, f.text, f.sourceLabel, f.sourceUrl,
          mediaRef(f.mediaSrc, `fact ${f.figure}`)]);
      bump('fact');
    }

    for (const [i, slug] of plan.fieldSlugs.entries()) {
      const fieldId = fieldIdBySlug.get(slug);
      if (fieldId === undefined) abort(`field "${slug}" is not in the field table after the vocabulary mirror`);
      await client.query(
        'insert into story_field (published_version_id, field_id, position) values ($1, $2, $3)',
        [pvId, fieldId, i + 1]);
      bump('story_field');
    }

    // Step 6: orphan audit. Set-based queries over every row this transaction wrote; any hit prints table and id.
    const audits: [string, string, unknown[]][] = [
      ['published_version -> story',
        'select pv.id::text as id from published_version pv left join story s on s.id = pv.story_id where pv.id = $1 and s.id is null',
        [pvId]],
      ['story_source -> source',
        'select ss.id::text as id from story_source ss left join source s on s.id = ss.source_id where ss.published_version_id = $1 and s.id is null',
        [pvId]],
      ['citation -> source',
        'select c.id::text as id from citation c left join source s on s.id = c.source_id where c.published_version_id = $1 and s.id is null',
        [pvId]],
      ['story_tag -> tag',
        'select st.id::text as id from story_tag st left join tag t on t.id = st.tag_id where st.published_version_id = $1 and t.id is null',
        [pvId]],
      ['tag -> facet (upserted tags)',
        'select t.id::text as id from tag t left join facet f on f.id = t.facet_id where t.key = any($1::text[]) and f.id is null',
        [[...tagIdByKey.keys()]]],
      ['moment -> media_asset',
        'select mo.id::text as id from moment mo left join media_asset a on a.id = mo.media_asset_id where mo.published_version_id = $1 and mo.media_asset_id is not null and a.id is null',
        [pvId]],
      ['fact -> media_asset',
        'select f.id::text as id from fact f left join media_asset a on a.id = f.media_asset_id where f.published_version_id = $1 and f.media_asset_id is not null and a.id is null',
        [pvId]],
      ['story_field -> field',
        'select sf.id::text as id from story_field sf left join field f on f.id = sf.field_id where sf.published_version_id = $1 and f.id is null',
        [pvId]],
      ['source_snapshot -> source',
        'select ss.id::text as id from source_snapshot ss left join source s on s.id = ss.source_id where ss.source_id = $1::bigint and s.id is null',
        [sourceId]],
    ];
    for (const table of ['media_asset', 'citation', 'story_source', 'story_tag', 'moment', 'fact', 'story_field']) {
      audits.push([`${table} -> published_version`,
        `select t.id::text as id from ${table} t left join published_version pv on pv.id = t.published_version_id where t.published_version_id = $1 and pv.id is null`,
        [pvId]]);
    }
    for (const [name, sql, params] of audits) {
      const bad = await client.query<{ id: string }>(sql, params);
      if (bad.rows.length) abort(`orphan audit failed: ${name}: id ${bad.rows.map(r => r.id).join(', ')}`);
    }

    // Step 7: promote (publish_version retires the old live row, flips this one, updates story.live_version_id).
    await client.query('select publish_version($1::bigint)', [pvId]);
    const verify = await client.query<{ ok: boolean }>(
      `select (s.live_version_id = pv.id and pv.status = 'live') as ok
         from story s join published_version pv on pv.story_id = s.id where pv.id = $1::bigint`, [pvId]);
    if (verify.rows[0]?.ok !== true) abort(`promotion of version ${pvId} did not make it live`);

    // Step 8: commit, then the report.
    await client.query('commit');
    printReport(plan, pvId, counts, {
      facet: facetIdByKey.size, tag: tagIdByKey.size, field: fieldIdBySlug.size,
    });
    return pvId;
  } catch (err) {
    await client.query('rollback').catch(() => undefined);
    throw err;
  } finally {
    await client.end();
  }
}

/** The reconciliation report: what this publish wrote, and the hashes that identify the version. */
function printReport(plan: Plan, pvId: string, counts: Map<string, number>, vocab: { facet: number; tag: number; field: number }): void {
  const c = (name: string) => counts.get(name) ?? 0;
  const byKind = (['lead', 'hook', 'chapter', 'strip_panel', 'fact'] as const)
    .map(k => `${k} ${c(`moment:${k}`)}`).join(', ');
  console.log('');
  console.log(`Published ${plan.slug} (kind ${plan.kind}) as live version ${pvId}.`);
  console.log(`  document sha256: ${plan.documentHash}`);
  console.log(`  publish sha256 (document + library entry): ${plan.payloadHash}`);
  console.log(`  story_source=${c('story_source')} citation=${c('citation')} media_asset=${c('media_asset')} ` +
    `story_tag=${c('story_tag')} moment=${c('moment')} fact=${c('fact')} story_field=${c('story_field')}`);
  console.log(`  moment by kind: ${byKind}`);
  console.log(`  source: ${c('source_inserted')} inserted, ${c('source_updated')} updated; source_snapshot=${c('source_snapshot')}`);
  console.log(`  vocabulary mirror: facet=${vocab.facet} tag=${vocab.tag} field=${vocab.field}`);
}

// ---------- Entry point ----------

async function readJson<T>(rel: string): Promise<T> {
  return JSON.parse(await readFile(join(PUBLIC, rel), 'utf8')) as T;
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const force = args.includes('--force');
  const slug = args.find(a => !a.startsWith('-'))?.trim();
  if (!slug) die('usage: npm run publish:supabase -- <slug> [--force]');
  if (!/^[a-z0-9-]+$/.test(slug)) die(`"${slug}" is not a slug (lowercase letters, digits and hyphens only)`);

  const dbUrl = process.env.SUPABASE_DB_URL?.trim();
  if (!dbUrl) {
    die('SUPABASE_DB_URL is not set. Add the Postgres URI to .env (see .env.example).');
  }
  const target = new URL(dbUrl);
  console.log(`Target: ${target.hostname}${target.port ? `:${target.port}` : ''}`);

  const library = await readJson<Library>('data/library.json');
  const vocab = await readJson<TagVocabulary>('data/tags.json');
  const raw = await readJson<unknown>(`data/papers/${slug}.json`).catch(() => {
    abort(`no story file public/data/papers/${slug}.json`);
  });
  const warnings: string[] = [];
  const plan = validate(slug, raw, library, vocab, warnings);
  warnings.forEach(w => console.warn(`warning: ${w}`));
  console.log(`Checks passed for ${slug}: ${plan.moments.length} moments, ${plan.facts.length} facts, ${plan.media.length} media, ${plan.citations.length} citations, ${plan.tags.length} tags.`);

  await publish(plan, library, vocab, dbUrl, force);
}

main().catch((err: unknown) => {
  if (err instanceof Abort) {
    console.error(`Aborted, nothing published: ${err.message}`);
  } else {
    console.error(`Failed, rolled back; the previous live version is unchanged: ${(err as Error).message}`);
  }
  process.exitCode = 1;
});
