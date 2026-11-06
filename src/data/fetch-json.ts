const BASE = new URL(import.meta.env.BASE_URL, window.location.origin);

/** Resolves a path against the app's base URL (absolute URLs pass through). */
export function appUrl(path: string): string {
  return new URL(path, BASE).href;
}

const cache = new Map<string, Promise<unknown>>();

/**
 * Fetches a versioned JSON document once per page load. A document at any other schemaVersion is rejected, never
 * upgraded. `mismatch` builds the message for a document that needs a migration (defaults to a plain version error).
 */
export function getJson<T extends { schemaVersion?: number }>(
  url: string,
  required = 1,
  mismatch?: (found: unknown) => string,
): Promise<T> {
  if (!cache.has(url)) {
    cache.set(url, fetch(appUrl(url)).then(async res => {
      if (!res.ok) throw new Error(`Could not load ${url} (${res.status})`);
      const doc = (await res.json()) as T;
      if (doc.schemaVersion !== required) {
        throw new Error(mismatch?.(doc.schemaVersion) ?? `${url} uses schema version ${doc.schemaVersion}; this page reads version ${required}.`);
      }
      return doc;
    }));
  }
  return cache.get(url) as Promise<T>;
}
