// Seeds the editorial tables from data/seed/library.json and the facet/tag vocabulary from data/seed/tags.json.
// Idempotent: upserts by slug/key, so re-running is safe. Runs in one pg transaction — any failure rolls back.
//
// Also inserts PLACEHOLDER `story` rows for every slug referenced by the editorial joins (issue_story,
// company_post, storyline_step, node, front_placement). Those placeholders carry `sample = true` and no
// live_version_id — only the three real stories get `published_version` rows via `npm run publish:supabase`.
//
// Run with: npm run seed:editorial
//
// Needs SUPABASE_DB_URL. Never reads VITE_SUPABASE_URL or the service-role key.

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import pg from 'pg';

interface LibStory { id: string; kind: string; sample?: boolean }
interface LibVolume { id: string; title: string; kind: 'regular' | 'special' }
interface LibIssue { id: string; number: string; volume: string; title: string; color?: string; published?: string; stories?: string[]; covers?: string; sample?: boolean }
interface LibCompany { id: string; name: string; sector?: string; blurb?: string; postsFollowed?: number; posts?: string[]; builtOn?: string[]; coming?: unknown; sample?: boolean }
interface LibStoryline { id: string; title: string; sample?: boolean; steps?: { year?: string; label?: string; current?: boolean; story?: string }[] }
interface LibField { id: string; label: string; color?: string; cluster?: unknown }
interface LibNode { id: string; title: string; authors?: string; year?: number; field?: string; type?: string; x?: number; y?: number; story?: string; sample?: boolean }
interface LibRelation { from: string; to: string; kind: string; note?: string; cited?: boolean; sample?: boolean }
interface LibFront { lead: string; aside: string[]; more: string[]; topics: { field: string; label: string; stories: string[] }[]; real: string[]; storylines: string[]; vault: string; onThisDay: { year: string; text: string; story: string } | null }
interface Library {
  stories: LibStory[]; volumes: LibVolume[]; issues: LibIssue[]; companies: LibCompany[];
  storylines: LibStoryline[]; fields: LibField[]; nodes: LibNode[]; relations: LibRelation[]; front: LibFront;
}
interface Vocab {
  // tags.json uses `id` as the public key on both facets and tags.
  facets: { id: string; label: string; description?: string }[];
  tags: { id: string; facet: string; label: string; aliases?: string[] }[];
}

function die(msg: string): never { console.error(msg); process.exit(1); }

const dbUrl = process.env.SUPABASE_DB_URL?.trim();
if (!dbUrl) die('SUPABASE_DB_URL is not set. See .env.example.');
console.log(`Target: ${new URL(dbUrl).hostname}`);

const library = JSON.parse(await readFile(resolve('data/seed/library.json'), 'utf8')) as Library;
const vocab = JSON.parse(await readFile(resolve('data/seed/tags.json'), 'utf8')) as Vocab;

// Mapping from kind values in library to the story.kind CHECK (paper|blog|classic).
const kindOf = (k: string | undefined): string => (k === 'blog' || k === 'classic' ? k : 'paper');
const nodeKindOf = (k: string | undefined): string => (k === 'blog' ? 'blog' : 'paper');

const client = new pg.Client({ connectionString: dbUrl });
await client.connect();
try {
  await client.query('begin');

  // 1. facet + tag vocabulary.
  for (const [i, f] of vocab.facets.entries()) {
    await client.query(
      `insert into facet (key, label, position) values ($1, $2, $3)
       on conflict (key) do update set label = excluded.label, position = excluded.position`,
      [f.id, f.label, i],
    );
  }
  for (const t of vocab.tags) {
    await client.query(
      `insert into tag (key, facet_id, label, aliases)
       values ($1, (select id from facet where key = $2), $3, $4)
       on conflict (key) do update set facet_id = excluded.facet_id, label = excluded.label, aliases = excluded.aliases`,
      [t.id, t.facet, t.label, t.aliases ?? []],
    );
  }
  console.log(`facet: ${vocab.facets.length}, tag: ${vocab.tags.length}`);

  // 2. field.
  for (const f of library.fields) {
    await client.query(
      `insert into field (slug, label, color, cluster) values ($1, $2, $3, $4)
       on conflict (slug) do update set label = excluded.label, color = excluded.color, cluster = excluded.cluster`,
      [f.id, f.label, f.color ?? null, f.cluster ? JSON.stringify(f.cluster) : null],
    );
  }
  console.log(`field: ${library.fields.length}`);

  // 3. Placeholder story rows for every library story slug that is NOT already in the story table (the real
  //    three were inserted by publish-to-supabase). The samples get sample=true; no live_version_id.
  let placeholderCount = 0;
  for (const s of library.stories) {
    const kind = kindOf(s.kind);
    const sample = s.sample !== false; // default to sample=true for safety; real stories will be re-upserted by publish
    const r = await client.query(
      `insert into story (slug, kind, sample) values ($1, $2, $3)
       on conflict (slug) do nothing returning id`,
      [s.id, kind, sample],
    );
    if (r.rowCount && r.rowCount > 0) placeholderCount++;
  }
  console.log(`story placeholders inserted: ${placeholderCount}`);

  // Also insert placeholder rows for any slug referenced by editorial joins but not in library.stories[].
  const referencedSlugs = new Set<string>();
  for (const i of library.issues) { if (i.covers) referencedSlugs.add(i.covers); for (const sid of i.stories ?? []) referencedSlugs.add(sid); }
  for (const c of library.companies) for (const p of c.posts ?? []) referencedSlugs.add(p);
  for (const sl of library.storylines) for (const st of sl.steps ?? []) if (st.story) referencedSlugs.add(st.story);
  for (const n of library.nodes) if (n.story) referencedSlugs.add(n.story);
  const knownStorySlugs = new Set(library.stories.map(s => s.id));
  for (const slug of referencedSlugs) {
    if (knownStorySlugs.has(slug)) continue;
    const r = await client.query(
      `insert into story (slug, kind, sample) values ($1, $2, true) on conflict (slug) do nothing`,
      [slug, 'paper'],
    );
    if (r.rowCount && r.rowCount > 0) console.log(`  extra placeholder: ${slug}`);
  }

  // 4. volume.
  for (const v of library.volumes) {
    await client.query(
      `insert into volume (slug, title, kind) values ($1, $2, $3)
       on conflict (slug) do update set title = excluded.title, kind = excluded.kind`,
      [v.id, v.title, v.kind],
    );
  }

  // 5. issue (+ issue_story). Rebuild issue_story fresh per issue (delete + insert) so reordering works.
  for (const [i, iss] of library.issues.entries()) {
    const coverId = iss.covers
      ? (await client.query('select id from story where slug = $1', [iss.covers])).rows[0]?.id ?? null
      : null;
    const v = (await client.query('select id from volume where slug = $1', [iss.volume])).rows[0];
    if (!v) throw new Error(`issue ${iss.id} references unknown volume ${iss.volume}`);
    const insR = await client.query(
      `insert into issue (slug, number, volume_id, title, color, published, cover_story_id, sample, position)
       values ($1, $2, $3, $4, $5, $6, $7, $8, $9)
       on conflict (slug) do update set number = excluded.number, volume_id = excluded.volume_id,
         title = excluded.title, color = excluded.color, published = excluded.published,
         cover_story_id = excluded.cover_story_id, sample = excluded.sample, position = excluded.position
       returning id`,
      [iss.id, iss.number, v.id, iss.title, iss.color ?? null, iss.published ?? null, coverId, iss.sample === true, i],
    );
    const issueId = insR.rows[0].id;
    await client.query('delete from issue_story where issue_id = $1', [issueId]);
    for (const [pos, sid] of (iss.stories ?? []).entries()) {
      const s = (await client.query('select id from story where slug = $1', [sid])).rows[0];
      if (!s) throw new Error(`issue ${iss.id} references unknown story ${sid}`);
      await client.query(
        `insert into issue_story (issue_id, story_id, position) values ($1, $2, $3)`,
        [issueId, s.id, pos],
      );
    }
  }
  console.log(`issue: ${library.issues.length}`);

  // 6. company (+ company_post + company_built_on).
  for (const c of library.companies) {
    const insR = await client.query(
      `insert into company (slug, name, sector, blurb, posts_followed, coming, sample)
       values ($1, $2, $3, $4, $5, $6, $7)
       on conflict (slug) do update set name = excluded.name, sector = excluded.sector,
         blurb = excluded.blurb, posts_followed = excluded.posts_followed, coming = excluded.coming,
         sample = excluded.sample
       returning id`,
      [c.id, c.name, c.sector ?? null, c.blurb ?? null, c.postsFollowed ?? null,
       c.coming ? JSON.stringify(c.coming) : null, c.sample === true],
    );
    const companyId = insR.rows[0].id;
    await client.query('delete from company_post where company_id = $1', [companyId]);
    for (const [pos, pid] of (c.posts ?? []).entries()) {
      const s = (await client.query('select id from story where slug = $1', [pid])).rows[0];
      if (!s) throw new Error(`company ${c.id} references unknown story ${pid}`);
      await client.query(`insert into company_post (company_id, story_id, position) values ($1, $2, $3)`,
        [companyId, s.id, pos]);
    }
    // builtOn references node slugs, not story slugs. We insert nodes below; this delete + insert runs after.
  }
  console.log(`company: ${library.companies.length}`);

  // 7. storyline + storyline_step.
  for (const sl of library.storylines) {
    const insR = await client.query(
      `insert into storyline (slug, title, sample) values ($1, $2, $3)
       on conflict (slug) do update set title = excluded.title, sample = excluded.sample returning id`,
      [sl.id, sl.title, sl.sample === true],
    );
    const slId = insR.rows[0].id;
    await client.query('delete from storyline_step where storyline_id = $1', [slId]);
    for (const [pos, st] of (sl.steps ?? []).entries()) {
      const sid = st.story
        ? (await client.query('select id from story where slug = $1', [st.story])).rows[0]?.id ?? null
        : null;
      await client.query(
        `insert into storyline_step (storyline_id, position, year, label, current, story_id)
         values ($1, $2, $3, $4, $5, $6)`,
        [slId, pos, st.year ?? null, st.label ?? null, st.current === true, sid],
      );
    }
  }
  console.log(`storyline: ${library.storylines.length}`);

  // 8. node.
  for (const n of library.nodes) {
    const fieldId = n.field
      ? (await client.query('select id from field where slug = $1', [n.field])).rows[0]?.id ?? null
      : null;
    const storyId = n.story
      ? (await client.query('select id from story where slug = $1', [n.story])).rows[0]?.id ?? null
      : null;
    await client.query(
      `insert into node (slug, title, authors, year, field_id, kind, x, y, story_id, sample)
       values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
       on conflict (slug) do update set title = excluded.title, authors = excluded.authors,
         year = excluded.year, field_id = excluded.field_id, kind = excluded.kind,
         x = excluded.x, y = excluded.y, story_id = excluded.story_id, sample = excluded.sample`,
      [n.id, n.title, n.authors ?? null, n.year ?? null, fieldId, nodeKindOf(n.type),
       n.x ?? 0, n.y ?? 0, storyId, n.sample === true],
    );
  }
  console.log(`node: ${library.nodes.length}`);

  // 9. company_built_on (needs nodes in place).
  for (const c of library.companies) {
    const cid = (await client.query('select id from company where slug = $1', [c.id])).rows[0].id;
    await client.query('delete from company_built_on where company_id = $1', [cid]);
    for (const [pos, nid] of (c.builtOn ?? []).entries()) {
      const n = (await client.query('select id from node where slug = $1', [nid])).rows[0];
      if (!n) { console.warn(`  company ${c.id}: node ${nid} not in map; skipping`); continue; }
      await client.query(`insert into company_built_on (company_id, node_id, position) values ($1, $2, $3)`,
        [cid, n.id, pos]);
    }
  }

  // 10. relation (+ default unverified).
  await client.query('delete from relation'); // wipe-and-reinsert: relations don't have their own slugs
  for (const r of library.relations) {
    const src = (await client.query('select id from node where slug = $1', [r.from])).rows[0];
    const dst = (await client.query('select id from node where slug = $1', [r.to])).rows[0];
    if (!src || !dst) throw new Error(`relation ${r.from}->${r.to} references unknown node`);
    await client.query(
      `insert into relation (source_node_id, target_node_id, kind, note, verified, sample)
       values ($1, $2, $3, $4, false, $5)`,
      [src.id, dst.id, r.kind, r.note ?? null, r.sample === true],
    );
  }
  console.log(`relation: ${library.relations.length} (all unverified by default)`);

  // 11. front_placement (one row, keyed 'current').
  await client.query(
    `insert into front_placement (key, data) values ('current', $1)
     on conflict (key) do update set data = excluded.data`,
    [JSON.stringify(library.front)],
  );

  await client.query('commit');
  console.log('Seed committed.');
} catch (err) {
  await client.query('rollback').catch(() => {});
  console.error('Seed failed, rolled back:', (err as Error).message);
  process.exit(1);
} finally {
  await client.end();
}
