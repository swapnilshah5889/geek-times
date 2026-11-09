import { randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { link, lstat, mkdir, open, realpath, rename, rm, unlink } from 'node:fs/promises';
import { dirname, join, relative, resolve, sep } from 'node:path';

/** A generated SVG and the media metadata that will be referenced by a story document. */
export interface SvgArtifactInput {
  /** Repository-relative path. Must be public/media/<slug>/<safe-name>.svg. */
  relativePath: string;
  svg: string;
  alt: string;
  width: number;
  height: number;
}

export interface SvgArtifactResult {
  relativePath: string;
  absolutePath: string;
  alt: string;
  width: number;
  height: number;
  bytes: number;
  title: string;
  viewBox: string;
}

export interface WriteSvgArtifactsOptions {
  /**
   * Regeneration may replace existing files, but is opt-in. A failed overwrite batch may leave earlier replacements
   * from this invocation in place; atomic rollback is intentionally unsupported when prior reviewed files exist.
   */
  overwrite?: boolean;
}

const REPO_ROOT = resolve(import.meta.dirname, '../..');
const MAX_ARTIFACTS = 80;
const MAX_FILE_BYTES = 512 * 1024;
const MAX_BATCH_BYTES = 12 * 1024 * 1024;
const MAX_DIMENSION = 4096;
const VALIDATOR_TIMEOUT_MS = 5_000;

// This fixed Python program only parses the SVG passed as JSON on stdin. Generated Python or shell code is never run.
// Python's stdlib XML parser is available in this repo's documented drawing environment and avoids a new dependency.
const SVG_VALIDATOR = [
  'import json, math, re, sys',
  'from xml.etree import ElementTree',
  '',
  'svg = json.load(sys.stdin)',
  "if not isinstance(svg, str): raise ValueError('SVG input must be a string')",
  "if re.search(r'<!\\s*(?:DOCTYPE|ENTITY)\\b', svg, re.I): raise ValueError('DOCTYPE and ENTITY declarations are not allowed')",
  "if re.search(r'<\\?xml-stylesheet\\b', svg, re.I): raise ValueError('external XML stylesheets are not allowed')",
  '',
  'root = ElementTree.fromstring(svg)',
  "svg_ns = '{http://www.w3.org/2000/svg}'",
  "if root.tag != svg_ns + 'svg': raise ValueError('root element must be an SVG-namespace <svg>')",
  '',
  "forbidden = {'script', 'foreignobject', 'iframe', 'object', 'embed', 'animate', 'animatemotion', 'animatetransform', 'set'}",
  "external_url = re.compile(r'url\\s*\\(\\s*([^)]+?)\\s*\\)', re.I)",
  "bad_css = re.compile(r'@import\\b|expression\\s*\\(|-moz-binding\\s*:', re.I)",
  'nodes = 0',
  'titles = []',
  '',
  'def check_css(value):',
  "    if bad_css.search(value): raise ValueError('unsafe CSS construct')",
  "    if '\\\\' in value: raise ValueError('CSS escapes are not allowed in generated SVG')",
  '    for match in external_url.finditer(value):',
  "        target = match.group(1).strip().strip('\"\\'')",
  "        if not re.fullmatch(r'#[A-Za-z_][A-Za-z0-9_.:-]*', target): raise ValueError('only local fragment url(#id) references are allowed')",
  "    if re.search(r'(?i)(?:javascript|vbscript|data|https?):|//', value): raise ValueError('external or executable URL in CSS')",
  '',
  'def walk(node, depth):',
  '    global nodes',
  '    nodes += 1',
  "    if nodes > 10000 or depth > 100: raise ValueError('SVG structure is too large or deeply nested')",
  "    name = node.tag.rsplit('}', 1)[-1].lower() if isinstance(node.tag, str) else ''",
  "    if name in forbidden: raise ValueError('forbidden SVG element: ' + name)",
  "    if name == 'title' and (node.text or '').strip(): titles.append(' '.join((node.text or '').split()))",
  "    if name == 'style': check_css(node.text or '')",
  '    for key, value in node.attrib.items():',
  "        attr = key.rsplit('}', 1)[-1].lower()",
  "        if attr.startswith('on'): raise ValueError('event-handler attributes are not allowed')",
  "        if attr == 'base': raise ValueError('xml:base is not allowed')",
  "        if attr in {'href', 'src'} and value.strip() and not re.fullmatch(r'#[A-Za-z_][A-Za-z0-9_.:-]*', value.strip()): raise ValueError('only local fragment href references are allowed')",
  "        if attr == 'style': check_css(value)",
  "        elif re.search(r'url\\s*\\(', value, re.I): check_css(value)",
  '    for child in list(node): walk(child, depth + 1)',
  '',
  'walk(root, 1)',
  "if not titles: raise ValueError('SVG needs a non-empty <title>')",
  "parts = re.split(r'[\\s,]+', root.attrib.get('viewBox', '').strip())",
  "if len(parts) != 4: raise ValueError('SVG needs a four-number viewBox')",
  'try: coords = [float(part) for part in parts]',
  "except ValueError: raise ValueError('viewBox values must be numbers')",
  "if not all(math.isfinite(value) for value in coords) or coords[2] <= 0 or coords[3] <= 0: raise ValueError('viewBox must be finite with positive width and height')",
  "print(json.dumps({'title': titles[0], 'viewBox': ' '.join(parts)}))",
].join('\n');

function validateSlug(slug: string): void {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    throw new Error('Invalid story slug "' + slug + '"; use lowercase letters, digits, and single hyphens.');
  }
}

function validateMediaPath(relativePath: string, slug: string): string {
  const prefix = 'public/media/' + slug + '/';
  if (!relativePath.startsWith(prefix)) {
    throw new Error('Media path must be under ' + prefix + ': ' + relativePath);
  }
  const parts = relativePath.slice(prefix.length).split('/');
  const directories = parts.slice(0, -1);
  const filename = parts.at(-1) ?? '';
  if (directories.some(part => !/^[a-z0-9][a-z0-9_-]*$/.test(part)) ||
      !/^[a-z0-9][a-z0-9_-]*\.svg$/.test(filename)) {
    throw new Error('Media path must use safe lowercase directories and a simple .svg filename: ' + relativePath);
  }
  const absolutePath = resolve(REPO_ROOT, relativePath);
  const mediaRoot = resolve(REPO_ROOT, prefix);
  if (!absolutePath.startsWith(mediaRoot + sep)) {
    throw new Error('Media path escapes its story directory: ' + relativePath);
  }
  return absolutePath;
}

function inspectSvg(svg: string): { title: string; viewBox: string } {
  const parsed = spawnSync('python3', ['-c', SVG_VALIDATOR], {
    input: JSON.stringify(svg),
    encoding: 'utf8',
    timeout: VALIDATOR_TIMEOUT_MS,
    maxBuffer: 256 * 1024,
  });
  if (parsed.error) throw new Error('Could not run the fixed SVG XML validator: ' + parsed.error.message);
  if (parsed.status !== 0) {
    const detail = parsed.stderr.trim() || 'validator exited with status ' + String(parsed.status);
    throw new Error('Invalid or unsafe SVG: ' + detail);
  }
  try {
    return JSON.parse(parsed.stdout) as { title: string; viewBox: string };
  } catch {
    throw new Error('SVG validator returned an invalid response.');
  }
}

function normalizeAccessibleText(value: string): string {
  return value.trim().replace(/\s+/g, ' ');
}

/** Creates parent directories one component at a time and refuses symlinked or non-directory components. */
async function ensureSafeParent(absolutePath: string): Promise<void> {
  const repository = await realpath(REPO_ROOT);
  const relativeParent = relative(repository, dirname(absolutePath));
  if (relativeParent.startsWith('..' + sep) || relativeParent === '..' || resolve(repository, relativeParent) === repository) {
    throw new Error('SVG output parent must be inside the repository media directory.');
  }

  let current = repository;
  for (const part of relativeParent.split(sep)) {
    current = join(current, part);
    try {
      const info = await lstat(current);
      if (info.isSymbolicLink()) throw new Error('Refusing to write through symlinked directory: ' + current);
      if (!info.isDirectory()) throw new Error('Expected a directory in SVG output path: ' + current);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
      await mkdir(current);
    }
  }

  const actualParent = await realpath(dirname(absolutePath));
  if (actualParent !== resolve(repository, relativeParent)) {
    throw new Error('SVG output parent resolved outside its expected repository path.');
  }
}

/** Validates every SVG before writing. Generated Python or shell code is never executed. */
export async function writeSvgArtifacts(
  slug: string,
  artifacts: SvgArtifactInput[],
  options: WriteSvgArtifactsOptions = {},
): Promise<SvgArtifactResult[]> {
  validateSlug(slug);
  if (!Array.isArray(artifacts) || artifacts.length === 0 || artifacts.length > MAX_ARTIFACTS) {
    throw new Error('Provide between 1 and ' + MAX_ARTIFACTS + ' SVG artifacts.');
  }

  const seen = new Set<string>();
  let totalBytes = 0;
  const planned = artifacts.map((artifact): SvgArtifactResult => {
    if (!artifact || typeof artifact !== 'object') throw new Error('Each SVG artifact must be an object.');
    const absolutePath = validateMediaPath(artifact.relativePath, slug);
    if (seen.has(absolutePath)) throw new Error('Duplicate SVG output path: ' + artifact.relativePath);
    seen.add(absolutePath);
    if (typeof artifact.alt !== 'string' || !normalizeAccessibleText(artifact.alt) || artifact.alt.length > 500) {
      throw new Error(artifact.relativePath + ': alt text must contain 1–500 characters.');
    }
    for (const [name, value] of [['width', artifact.width], ['height', artifact.height]] as const) {
      if (!Number.isInteger(value) || value <= 0 || value > MAX_DIMENSION) {
        throw new Error(artifact.relativePath + ': ' + name + ' must be an integer from 1 to ' + MAX_DIMENSION + '.');
      }
    }
    if (typeof artifact.svg !== 'string' || !artifact.svg.trim()) {
      throw new Error(artifact.relativePath + ': SVG content is empty.');
    }
    const bytes = Buffer.byteLength(artifact.svg, 'utf8');
    if (bytes > MAX_FILE_BYTES) throw new Error(artifact.relativePath + ': SVG exceeds ' + MAX_FILE_BYTES + ' bytes.');
    totalBytes += bytes;
    if (totalBytes > MAX_BATCH_BYTES) throw new Error('SVG batch exceeds ' + MAX_BATCH_BYTES + ' bytes.');
    const { title, viewBox } = inspectSvg(artifact.svg);
    const alt = normalizeAccessibleText(artifact.alt);
    if (normalizeAccessibleText(title) !== alt) {
      throw new Error(artifact.relativePath + ': SVG <title> must match the supplied alt text after whitespace normalization.');
    }
    return {
      relativePath: artifact.relativePath, absolutePath, alt,
      width: artifact.width, height: artifact.height, bytes, title, viewBox,
    };
  });

  for (const item of planned) {
    await ensureSafeParent(item.absolutePath);
    try {
      const info = await lstat(item.absolutePath);
      if (info.isSymbolicLink()) throw new Error('Refusing to write through a symlink: ' + item.relativePath);
      if (!options.overwrite) {
        throw new Error('Refusing to overwrite existing art: ' + item.relativePath + '. Pass { overwrite: true } to replace it.');
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
    }
  }

  const staged: Array<{ temporary: string; destination: string }> = [];
  const committed: string[] = [];
  try {
    for (const [index, item] of planned.entries()) {
      const temporary = join(dirname(item.absolutePath), '.' + randomUUID() + '.tmp');
      staged.push({ temporary, destination: item.absolutePath });
      const handle = await open(temporary, 'wx', 0o644);
      try {
        await handle.writeFile(artifacts[index].svg, 'utf8');
      } finally {
        await handle.close();
      }
    }
    for (const file of staged) {
      if (options.overwrite) {
        await rename(file.temporary, file.destination);
        committed.push(file.destination);
      } else {
        // link() creates the destination only if it does not exist, avoiding a race that could clobber reviewed art.
        await link(file.temporary, file.destination);
        committed.push(file.destination);
        await unlink(file.temporary);
      }
    }
  } catch (error) {
    await Promise.all(staged.map(file => rm(file.temporary, { force: true }).catch(() => undefined)));
    if (!options.overwrite) {
      await Promise.all(committed.map(file => rm(file, { force: true }).catch(() => undefined)));
    }
    throw error;
  }

  return planned;
}
