// Read-only guard (cloud-only V1 gate): the browser runtime must never import or fetch local story/editorial JSON.
// Story and editorial data come from Supabase views; data/seed/ is recovery input for the import CLIs only.
//
// Scans:
//   1. src/**/*.{ts,tsx} for imports/fetches/URLs that name a .json file, or a data/seed or public/data path.
//      Comment-only lines are skipped (comments may mention seed files).
//   2. dist/ (if built) for the same tokens in *.js and *.html. Skipped with a notice when dist/ is absent.
//   3. public/data/ must not contain files (the runtime folder is empty by design).
// Exits 1 on any hit, 0 when clean. Never touches the network, the database or any env value.
//
// Run: node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/check-runtime-sources.ts
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, extname } from 'node:path';

const ROOT = join(import.meta.dirname, '..');

// Source-level patterns: a string or import that resolves to a JSON file, or to the seed/public data folders.
const SOURCE_PATTERNS: RegExp[] = [
  /(?:from|import|require|fetch)\s*\(?\s*['"`][^'"`\n]*\.json['"`]/,
  /['"`][^'"`\n]*(?:data\/seed|public\/data)[^'"`\n]*['"`]/,
  /['"`]\/?data\/[^'"`\n]*\.json['"`]/,
  /import\.meta\.glob\([^)]*\.json/,
];

// Built-output patterns: the same paths as they appear after bundling (no import statements survive).
const DIST_PATTERNS: RegExp[] = [
  /data\/seed\//,
  /public\/data\//,
  /\/data\/[A-Za-z0-9_\-/]+\.json/,
];

interface Hit { file: string; line: number; text: string }

function walk(dir: string, accept: (file: string) => boolean, out: string[] = []): string[] {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walk(full, accept, out);
    else if (accept(full)) out.push(full);
  }
  return out;
}

function scan(files: string[], patterns: RegExp[], skipComments: boolean): Hit[] {
  const hits: Hit[] = [];
  for (const file of files) {
    const lines = readFileSync(file, 'utf8').split('\n');
    lines.forEach((text, i) => {
      const trimmed = text.trim();
      if (skipComments && (trimmed.startsWith('//') || trimmed.startsWith('*') || trimmed.startsWith('/*'))) return;
      if (patterns.some(p => p.test(text))) {
        hits.push({ file: relative(ROOT, file), line: i + 1, text: trimmed.slice(0, 160) });
      }
    });
  }
  return hits;
}

const hits: Hit[] = [];

const srcFiles = walk(join(ROOT, 'src'), f => ['.ts', '.tsx'].includes(extname(f)));
const srcHits = scan(srcFiles, SOURCE_PATTERNS, true);
hits.push(...srcHits);
console.log(`src: scanned ${srcFiles.length} files, ${srcHits.length} hit(s).`);

const distDir = join(ROOT, 'dist');
if (existsSync(distDir)) {
  const distFiles = walk(distDir, f => ['.js', '.html'].includes(extname(f)));
  const distHits = scan(distFiles, DIST_PATTERNS, false);
  hits.push(...distHits);
  console.log(`dist: scanned ${distFiles.length} files, ${distHits.length} hit(s).`);
} else {
  console.log('dist: not built, skipped (run npm run build first to scan the bundle).');
}

const publicData = join(ROOT, 'public', 'data');
if (existsSync(publicData)) {
  const leftovers = walk(publicData, () => true);
  if (leftovers.length) {
    for (const f of leftovers) hits.push({ file: relative(ROOT, f), line: 0, text: 'file present in public/data/ (must stay empty)' });
  }
  console.log(`public/data: ${leftovers.length} file(s).`);
} else {
  console.log('public/data: absent (ok).');
}

if (hits.length) {
  console.error('\nForbidden runtime source reads found:');
  for (const h of hits) console.error(`  ${h.file}:${h.line}: ${h.text}`);
  process.exitCode = 1;
} else {
  console.log('\nOK: no runtime path reads or fetches local story/editorial JSON.');
}
