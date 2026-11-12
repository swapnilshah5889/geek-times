// Reconciles an export snapshot (scripts/export-supabase.ts) against the Git seed in data/seed/ (decisions 35, 37).
// Reads files only: no database connection. Compares stable keys (slugs, tag keys, node/relation pairs), the
// fields the seed carries, ordered references, the front-page placement, and each live story document against
// data/seed/papers/<slug>.json.
//
//   node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/reconcile-export.ts --export <dir>
//
// Exit codes: 0 = reconciled, 1 = mismatches (each printed with its section and key), 2 = usage or unreadable input.

import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

type Row = Record<string, unknown>;

const REPO = resolve(import.meta.dirname, '..');
const SEED = join(REPO, 'data', 'seed');

const problems: string[] = [];
const notes: string[] = [];
const checked: string[] = [];

function die(msg: string, code = 2): never {
  console.error(msg);
  process.exit(code);
}

function fail(section: string, msg: string): void {
  problems.push(`[${section}] ${msg}`);
}

function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value) ?? 'null';
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  const obj = value as Record<string, unknown>;
  return `{${Object.keys(obj).filter(k => obj[k] !== undefined).sort()
    .map(k => `${JSON.stringify(k)}:${canonical(obj[k])}`).join(',')}}`;
}

/** Short printable form: big values are shown as a hash so the output stays readable. */
function show(value: unknown): string {
  const s = canonical(value ?? null);
  if (s.length <= 120) return s;
  return `sha256:${createHash('sha256').update(s).digest('hex').slice(0, 16)} (${s.length} bytes)`;
}

function parseArgs(argv: string[]): { exportDir: string } {
  let exportDir: string | null = null;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--export') {
      const v = argv[++i];
      if (!v || v.startsWith('--')) die('--export needs the snapshot directory');
      exportDir = resolve(v);
    } else {
      die(`unknown argument "${argv[i]}"\nusage: reconcile-export.ts --export <dir>`);
    }
  }
  if (!exportDir) die('usage: reconcile-export.ts --export <dir>');
  return { exportDir };
}

async function readJsonFile<T>(path: string, what: string): Promise<T> {
  try {
    return JSON.parse(await readFile(path, 'utf8')) as T;
  } catch (err) {
    die(`cannot read ${what} at ${path}: ${(err as Error).message}`);
  }
}

/** Loads one export section and verifies its sha256 against the manifest. */
async function section(dir: string, manifest: Manifest, name: string): Promise<Row[]> {
  const entry = manifest.sections[name];
  if (!entry) die(`export manifest has no "${name}" section; the export is incomplete or from an older format`);
  const text = await readFile(join(dir, entry.file), 'utf8').catch(() => die(`missing ${entry.file} in the export`));
  if (createHash('sha256').update(text).digest('hex') !== entry.sha256) {
    die(`${entry.file} does not match its sha256 in manifest.json; the export was edited or damaged`);
  }
  const rows = JSON.parse(text) as Row[];
  if (rows.length !== entry.rows) die(`${entry.file} has ${rows.length} rows; manifest says ${entry.rows}`);
  checked.push(name);
  return rows;
}

interface Manifest {
  format: string;
  formatVersion: number;
  sourceHost: string;
  sections: Record<string, { rows: number; file: string; sha256: string }>;
}

/** Builds a key -> row map and reports duplicate keys, which would otherwise hide a row. */
function keyed(sectionName: string, rows: Row[], keyOf: (r: Row) => string): Map<string, Row> {
  const map = new Map<string, Row>();
  for (const r of rows) {
    const k = keyOf(r);
    if (map.has(k)) fail(sectionName, `"${k}" appears more than once in the export`);
    map.set(k, r);
  }
  return map;
}

/** Compares two keyed maps field by field. Missing and extra keys are reported by name. */
function compareMaps(sectionName: string, expected: Map<string, Row>, actual: Map<string, Row>): void {
  for (const [k, e] of expected) {
    const a = actual.get(k);
    if (!a) {
      fail(sectionName, `"${k}" is in the seed but missing from the export`);
      continue;
    }
    // Only the fields the seed carries are compared. Extra export columns (position, ids, timestamps) are ignored.
    for (const f of Object.keys(e)) {
      if (canonical(e[f] ?? null) !== canonical(a[f] ?? null)) {
        fail(sectionName, `"${k}" field "${f}": seed ${show(e[f])} != export ${show(a[f])}`);
      }
    }
  }
  for (const k of actual.keys()) {
    if (!expected.has(k)) fail(sectionName, `"${k}" is in the export but not in the seed`);
  }
}

/** Groups child rows under their parent key, ordered by position. Used for ordered references. */
function ordered(rows: Row[], parent: string, child: string): Map<string, string[]> {
  const byParent = new Map<string, Row[]>();
  for (const r of rows) {
    const p = String(r[parent]);
    byParent.set(p, [...(byParent.get(p) ?? []), r]);
  }
  const out = new Map<string, string[]>();
  for (const [p, list] of byParent) {
    out.set(p, list.sort((a, b) => Number(a.position) - Number(b.position)).map(r => String(r[child] ?? 'null')));
  }
  return out;
}

function withItems(base: Map<string, Row>, items: Map<string, string[]>, field: string): Map<string, Row> {
  const out = new Map<string, Row>();
  for (const [k, row] of base) out.set(k, { ...row, [field]: items.get(k) ?? [] });
  return out;
}

async function main(): Promise<void> {
  const { exportDir } = parseArgs(process.argv.slice(2));
  const manifest = await readJsonFile<Manifest>(join(exportDir, 'manifest.json'), 'export manifest');
  if (manifest.format !== 'geek-times-export') die(`${exportDir} is not a geek-times export`);

  // Seed side.
  interface LibStory { id: string; kind: string; sample?: boolean; [k: string]: unknown }
  interface Library {
    fields: { id: string; label: string; color?: string; cluster?: unknown }[];
    volumes: { id: string; title: string; kind: string }[];
    stories: LibStory[];
    issues: { id: string; number: string; volume: string; title: string; color?: string; published?: string; stories?: string[]; covers?: string }[];
    companies: { id: string; name: string; sector?: string; blurb?: string; postsFollowed?: number; posts?: string[]; builtOn?: string[]; coming?: unknown }[];
    storylines: { id: string; title: string; steps?: { year?: string; label?: string; current?: boolean; story?: string }[] }[];
    nodes: { id: string; title: string; authors?: string; year?: number; field?: string; type?: string; story?: string }[];
    relations: { from: string; to: string; kind: string; note?: string }[];
    front: unknown;
  }
  interface Vocab { facets: { id: string; label: string; description?: string }[]; tags: { id: string; facet: string; label: string; aliases?: string[] }[] }
  interface SeedSite { name: string; motto?: string; tagline?: string; navLabel?: string; mediaBaseUrl?: string; defaultPaper?: string; schemaVersion?: number }

  const library = await readJsonFile<Library>(join(SEED, 'library.json'), 'data/seed/library.json');
  const vocab = await readJsonFile<Vocab>(join(SEED, 'tags.json'), 'data/seed/tags.json');
  const site = await readJsonFile<SeedSite>(join(SEED, 'site.json'), 'data/seed/site.json');

  // 1. Site: one singleton row, mapped from site.json names to column names.
  {
    const name = 'site';
    const rows = await section(exportDir, manifest, name);
    const expected = new Map<string, Row>([['site', {
      site_name: site.name, motto: site.motto, tagline: site.tagline, nav_label: site.navLabel,
      media_base_url: site.mediaBaseUrl, default_story_slug: site.defaultPaper, schema_version: site.schemaVersion,
    }]]);
    if (rows.length !== 1) fail(name, `expected one site row, found ${rows.length}`);
    compareMaps(name, expected, keyed(name, rows.slice(0, 1), () => 'site'));
    notes.push('site.json "papers" list is not restored by the seed and is not reconciled (the runtime does not read it).');
  }

  // 2. Facets and tags (vocabulary). Facet position is not compared: see the report on seed/publish position numbering.
  {
    const facets = await section(exportDir, manifest, 'facets');
    compareMaps('facets',
      keyed('facets', vocab.facets.map(f => ({ key: f.id, label: f.label, description: f.description ?? null })), r => String(r.key)),
      keyed('facets', facets, r => String(r.key)));

    const tags = await section(exportDir, manifest, 'tags');
    compareMaps('tags',
      keyed('tags', vocab.tags.map(t => ({ key: t.id, label: t.label, facet_key: t.facet, aliases: t.aliases ?? [] })), r => String(r.key)),
      keyed('tags', tags.map(t => ({ ...t, aliases: t.aliases ?? [] })), r => String(r.key)));
  }

  // 3. Fields, volumes.
  {
    const fields = await section(exportDir, manifest, 'fields');
    compareMaps('fields',
      keyed('fields', library.fields.map(f => ({ slug: f.id, label: f.label, color: f.color ?? null, cluster: f.cluster ?? null })), r => String(r.slug)),
      keyed('fields', fields, r => String(r.slug)));

    const volumes = await section(exportDir, manifest, 'volumes');
    compareMaps('volumes',
      keyed('volumes', library.volumes.map(v => ({ slug: v.id, title: v.title, kind: v.kind })), r => String(r.slug)),
      keyed('volumes', volumes, r => String(r.slug)));
  }

  // 4. Issues with their ordered stories.
  {
    const issues = await section(exportDir, manifest, 'issues');
    const issueStories = ordered(await section(exportDir, manifest, 'issue_stories'), 'issue_slug', 'story_slug');
    compareMaps('issues',
      keyed('issues', library.issues.map(i => ({
        slug: i.id, number: i.number, volume_slug: i.volume, title: i.title, color: i.color ?? null,
        published: i.published ?? null, cover_story_slug: i.covers ?? null, stories: i.stories ?? [],
      })), r => String(r.slug)),
      withItems(keyed('issues', issues.map(i => ({ ...i, stories: undefined })), r => String(r.slug)), issueStories, 'stories'));
  }

  // 5. Companies with ordered posts and built-on nodes.
  {
    const companies = await section(exportDir, manifest, 'companies');
    const posts = ordered(await section(exportDir, manifest, 'company_posts'), 'company_slug', 'story_slug');
    const builtOn = ordered(await section(exportDir, manifest, 'company_built_on'), 'company_slug', 'node_slug');
    const base = keyed('companies', companies.map(c => ({ ...c, posts: undefined, built_on: undefined })), r => String(r.slug));
    compareMaps('companies',
      keyed('companies', library.companies.map(c => ({
        slug: c.id, name: c.name, sector: c.sector ?? null, blurb: c.blurb ?? null,
        posts_followed: c.postsFollowed ?? null, coming: c.coming ?? null, posts: c.posts ?? [], built_on: c.builtOn ?? [],
      })), r => String(r.slug)),
      withItems(withItems(base, posts, 'posts'), builtOn, 'built_on'));
  }

  // 6. Storylines with ordered steps (a step with no story keeps its place as null).
  {
    const storylines = await section(exportDir, manifest, 'storylines');
    const steps = await section(exportDir, manifest, 'storyline_steps');
    const byStoryline = new Map<string, Row[]>();
    for (const s of steps) {
      const k = String(s.storyline_slug);
      byStoryline.set(k, [...(byStoryline.get(k) ?? []), s]);
    }
    const exportSteps = new Map<string, Row[]>();
    for (const [k, list] of byStoryline) {
      exportSteps.set(k, list.sort((a, b) => Number(a.position) - Number(b.position)).map(s => ({
        year: s.year ?? null, label: s.label ?? null, current: s.current === true, story: s.story_slug ?? null,
      })));
    }
    const base = keyed('storylines', storylines.map(s => ({ slug: s.slug, title: s.title })), r => String(r.slug));
    const withSteps = new Map<string, Row>();
    for (const [k, row] of base) withSteps.set(k, { ...row, steps: exportSteps.get(k) ?? [] });
    compareMaps('storylines',
      keyed('storylines', library.storylines.map(s => ({
        slug: s.id, title: s.title,
        steps: (s.steps ?? []).map(st => ({ year: st.year ?? null, label: st.label ?? null, current: st.current === true, story: st.story ?? null })),
      })), r => String(r.slug)),
      withSteps);
  }

  // 7. Nodes (the map). x and y are not compared: the view returns them as stored numbers and the seed defaults them to 0.
  {
    const nodes = await section(exportDir, manifest, 'nodes');
    compareMaps('nodes',
      keyed('nodes', library.nodes.map(n => ({
        slug: n.id, title: n.title, authors: n.authors ?? null, year: n.year ?? null,
        kind: n.type === 'blog' ? 'blog' : 'paper', field_slug: n.field ?? null, story_slug: n.story ?? null,
      })), r => String(r.slug)),
      keyed('nodes', nodes.map(n => ({
        slug: n.slug, title: n.title, authors: n.authors ?? null, year: n.year ?? null,
        kind: n.kind, field_slug: n.field_slug ?? null, story_slug: n.story_slug ?? null,
      })), r => String(r.slug)));
  }

  // 8. Relations. Keyed by from|to|kind; the seed keeps only the note. Unverified edges are included on purpose.
  {
    const relations = await section(exportDir, manifest, 'relations');
    const key = (from: unknown, to: unknown, kind: unknown) => `${String(from)} -> ${String(to)} (${String(kind)})`;
    compareMaps('relations',
      keyed('relations', library.relations.map(r => ({ key: key(r.from, r.to, r.kind), note: r.note ?? null })), r => String(r.key)),
      keyed('relations', relations.map(r => ({
        key: key(r.source_node_slug, r.target_node_slug, r.kind), note: r.note ?? null,
      })), r => String(r.key)));
    const unverified = relations.filter(r => r.verified !== true).length;
    if (unverified > 0) notes.push(`${unverified} relation(s) are verified = false, as the seed imports them. The public v_relation view hides them; this check reads the base table.`);
  }

  // 9. Front placement: the seed's front object must equal the stored front_placement data.
  {
    const front = await section(exportDir, manifest, 'front_placement');
    if (front.length !== 1 || front[0].key !== 'current') {
      fail('front_placement', `expected exactly one row with key "current", found ${front.length}`);
    } else {
      compareMaps('front_placement', new Map([['current', { data: library.front }]]),
        new Map([['current', { data: front[0].data }]]));
    }
  }

  // 10. Stories: live, non-sample set must equal the seed's non-sample stories. Each document and library entry must
  //     equal its seed file. The library entry is the front-page card.
  {
    const live = await section(exportDir, manifest, 'stories');
    const seedStories = library.stories.filter(s => s.sample !== true);
    const expected = new Map<string, Row>();
    for (const s of seedStories) {
      const path = join(SEED, 'papers', `${s.id}.json`);
      let doc: unknown;
      try {
        doc = JSON.parse(await readFile(path, 'utf8'));
      } catch {
        fail('stories', `"${s.id}": no readable seed file data/seed/papers/${s.id}.json`);
        continue;
      }
      expected.set(s.id, { kind: s.kind, document: doc, library_entry: s });
    }
    const actual = keyed('stories', live.map(r => ({ story_slug: r.story_slug, kind: r.kind, document: r.document, library_entry: r.library_entry })),
      r => String(r.story_slug));
    compareMaps('stories', expected, new Map([...actual].map(([k, r]) => [k, { kind: r.kind, document: r.document, library_entry: r.library_entry }])));

    // Ordered tags and fields per live story, against the document (tags) and the library entry (fields).
    const tagRows = await section(exportDir, manifest, 'story_tags');
    const dbTagsByStory = new Map<string, string[]>();
    for (const r of tagRows) {
      const k = String(r.story_slug);
      dbTagsByStory.set(k, [...(dbTagsByStory.get(k) ?? []), String(r.tag_key)]);
    }
    const fieldsByStory = ordered(await section(exportDir, manifest, 'story_fields'), 'story_slug', 'field_slug');
    for (const s of seedStories) {
      const doc = expected.get(s.id)?.document as { tags?: { tag: string }[] } | undefined;
      if (!doc) continue;
      const seedTags = [...new Set((doc.tags ?? []).map(t => t.tag))].sort();
      const dbTags = [...new Set(dbTagsByStory.get(s.id) ?? [])].sort();
      if (canonical(seedTags) !== canonical(dbTags)) {
        fail('story_tags', `"${s.id}": seed tags ${show(seedTags)} != export ${show(dbTags)}`);
      }
      const seedFields = Array.isArray(s.fields) ? (s.fields as unknown[]).map(String) : [];
      const dbFields = fieldsByStory.get(s.id) ?? [];
      if (canonical(seedFields) !== canonical(dbFields)) {
        fail('story_fields', `"${s.id}": seed fields ${show(seedFields)} != export ${show(dbFields)}`);
      }
    }
  }

  // 11. Counts, reported (not failed): moments, facts, media and citations depend on the publish transform, which
  //     this read-only check does not re-run. Their presence per story is a sanity signal.
  {
    const counts = new Map<string, number>();
    for (const name of ['moments', 'facts', 'media_assets', 'citations']) {
      for (const r of await section(exportDir, manifest, name)) {
        const k = `${name}:${String(r.story_slug)}`;
        counts.set(k, (counts.get(k) ?? 0) + 1);
      }
    }
    const liveSlugs = (await section(exportDir, manifest, 'stories')).map(r => String(r.story_slug));
    for (const slug of liveSlugs) {
      if (!(counts.get(`moments:${slug}`) ?? 0)) fail('moments', `live story "${slug}" has no moments rows`);
    }
    const evidence = (await section(exportDir, manifest, 'relation_evidence')).length;
    if (evidence > 0) {
      notes.push(`${evidence} relation_evidence row(s) exist in the database but the seed has no evidence data: a seed-only restore would lose them.`);
    }
  }

  // Report.
  console.log(`Export: ${exportDir} (source ${manifest.sourceHost}, format ${manifest.formatVersion})`);
  console.log(`Sections read and integrity-checked: ${checked.length}`);
  for (const n of notes) console.log(`note: ${n}`);
  if (problems.length) {
    console.error(`\nRECONCILE FAILED: ${problems.length} mismatch(es)`);
    for (const p of problems) console.error(`  ${p}`);
    process.exit(1);
  }
  console.log('RECONCILE OK: the export matches data/seed/ on every checked key, count and field.');
}

main().catch((err: unknown) => die(`reconcile failed: ${(err as Error).message}`));
