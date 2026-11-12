const BASE = new URL(import.meta.env.BASE_URL, window.location.origin);

/** Resolves a path against the app's base URL (absolute URLs pass through). */
export function appUrl(path: string): string {
  return new URL(path, BASE).href;
}
