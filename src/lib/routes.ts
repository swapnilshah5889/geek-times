// Every link the app builds goes through here, so URLs stay correct on any page depth and under any
// deploy base (import.meta.env.BASE_URL). Paths in the data (Moment.href) are relative to that base.
const BASE = import.meta.env.BASE_URL;

/** Turns a base-relative path from the data, e.g. "papers/x#y", into a link. */
export const appHref = (path = '') => `${BASE}${path.replace(/^\//, '')}`;

export const homeHref = () => appHref();
export const feedHref = () => appHref('?feed');
export const paperHref = (slug: string, anchor?: string) =>
  appHref(`papers/${encodeURIComponent(slug)}${anchor ? `#${anchor}` : ''}`);

/** The current path without the deploy base, e.g. "papers/1706.03762". */
export function currentPath(): string {
  const path = window.location.pathname;
  const rest = path.startsWith(BASE) ? path.slice(BASE.length) : path.replace(/^\//, '');
  return decodeURIComponent(rest).replace(/\/$/, '');
}

export const issueHref = (id: string) => appHref(`issues/${encodeURIComponent(id)}`);
export const companyHref = (id: string) => appHref(`companies/${encodeURIComponent(id)}`);
export const mapHref = (focus?: string) => appHref(`map${focus ? `?focus=${encodeURIComponent(focus)}` : ''}`);
