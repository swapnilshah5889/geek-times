import type { PaperDoc } from '../types';
import { currentPath } from '../lib/routes';
import { mediaBaseFor, type Archive, type Edition } from './load';

/** Version of the prerender-to-hydration envelope, independent of story schemaVersion. */
export const SNAPSHOT_SCHEMA_VERSION = 1;

export interface InitialData {
  schemaVersion: typeof SNAPSHOT_SCHEMA_VERSION;
  route: string;
  source: 'supabase';
  hideSamples: boolean;
  archive: Archive;
  /** Present on a real paper/post route only. Sample story pages use the archive alone. */
  edition?: { doc: PaperDoc };
}

declare global {
  interface Window {
    __collect_initial_data__?: (data: InitialData) => void;
    __initial_data_json__?: string;
    __initial_route__?: string;
    __gt_prerender__?: boolean;
    __mount_mode__?: 'hydrated' | 'created';
  }
}

/** A null key means the URL selects a client-only view of a shared prerendered path. */
export function routeKeyFromLocation(): string | null {
  const path = currentPath();
  const query = new URLSearchParams(window.location.search);
  if (!path && ['feed', 'search', 'q', 'tag', 'paper'].some(key => query.has(key))) return null;
  if (path === 'map' && query.has('focus')) return null;
  return path ? `/${path}` : '/';
}

export function makeInitialData(route: string, archive: Archive, editionDoc?: PaperDoc): InitialData {
  return {
    schemaVersion: SNAPSHOT_SCHEMA_VERSION,
    route,
    source: 'supabase',
    hideSamples: import.meta.env.VITE_HIDE_SAMPLES === '1',
    archive,
    ...(editionDoc ? { edition: { doc: editionDoc } } : {}),
  };
}

export function editionFromInitial(initial: InitialData): Edition | null {
  if (!initial.edition) return null;
  const { site, vocab } = initial.archive;
  return { site, vocab, doc: initial.edition.doc, mediaBaseUrl: mediaBaseFor(site) };
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value);

/** Returns null when this document cannot be hydrated safely; the caller uses createRoot. */
export function readInitialData(): InitialData | null {
  const el = document.getElementById('__initial_data__');
  if (!el || el.tagName !== 'SCRIPT' || el.getAttribute('type') !== 'application/json') return null;
  let data: unknown;
  try { data = JSON.parse(el.textContent ?? ''); }
  catch (err) { console.warn('Ignoring invalid prerender data:', err); return null; }
  if (!isRecord(data) || data.schemaVersion !== SNAPSHOT_SCHEMA_VERSION) {
    console.warn('Ignoring incompatible prerender data version.');
    return null;
  }
  const route = routeKeyFromLocation();
  if (!route || data.route !== route || data.source !== 'supabase'
    || data.hideSamples !== (import.meta.env.VITE_HIDE_SAMPLES === '1')) return null;
  const archive = data.archive;
  if (!isRecord(archive) || !isRecord(archive.site) || !isRecord(archive.vocab)
    || !isRecord(archive.index) || !isRecord(archive.library)) return null;
  const root = document.getElementById('root');
  // Root should have exactly one wrapper child (either <main> directly, or the BookLoader
  // transition wrapper). Either way, there should be a <main> somewhere inside.
  if (!root || root.children.length !== 1 || !root.querySelector('main')) return null;
  if (route.startsWith('/papers/')) {
    const slug = route.slice('/papers/'.length);
    const edition = data.edition;
    const sample = Array.isArray(archive.library.stories)
      && archive.library.stories.some(story => isRecord(story) && story.id === slug && story.real === false);
    if (sample ? edition !== undefined : !isRecord(edition) || !isRecord(edition.doc) || edition.doc.slug !== slug) return null;
  } else if (data.edition !== undefined) return null;
  return data as unknown as InitialData;
}
