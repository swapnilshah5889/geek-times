import { useEffect, useRef } from 'react';
import { appHref, feedHref, homeHref, mapHref } from '../lib/routes';
import { searchHref } from '../lib/tags';
import type { SiteConfig } from '../types';

export type NavSection = 'front' | 'issues' | 'real' | 'snacks' | 'search' | 'explore';

interface Props {
  site: SiteConfig;
  /** Left and right of the top rule, e.g. issue number and desk. */
  meta?: [string, string];
  /** Show the quiet "Weekly edition →" link in the top right instead of meta[1]. */
  edition?: boolean;
  /** Page-local tabs (a story's sections), shown under the site navigation. */
  links?: { href: string; label: string }[];
  /** Which site section this page belongs to. */
  active?: NavSection;
}

// The site navigation is identical on every page (decisions 19 and 32): Front page · Explore · Real world ·
// Snacks · Editions · Search. Explore opens a small menu; it closes on outside click or Escape.
export function Masthead({ site, meta = ['', ''], links = [], active, edition }: Props) {
  const menu = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    const close = (e: Event) => {
      const el = menu.current;
      if (!el?.open) return;
      if (e instanceof KeyboardEvent ? e.key === 'Escape' : !el.contains(e.target as Node)) el.open = false;
    };
    document.addEventListener('click', close);
    document.addEventListener('keydown', close);
    return () => { document.removeEventListener('click', close); document.removeEventListener('keydown', close); };
  }, []);
  const cur = (s: NavSection) => (active === s ? 'page' as const : undefined);

  return (
    <header className="site-head">
      <div className="meta">
        <span>{meta[0]}</span>
        <span>{site.tagline}</span>
        <span>{edition ? <a href={appHref('issues')}>Weekly edition →</a> : meta[1]}</span>
      </div>
      <div className="mast"><a href={homeHref()} className="mast-link">{site.name}</a></div>
      <div className="motto">{site.motto}</div>
      <nav className="sitenav" aria-label="Sections">
        <span className="links">
          <a href={homeHref()} aria-current={cur('front')}>Front page</a>
          <details className="explore" ref={menu}>
            <summary aria-current={cur('explore')}>Explore ▾</summary>
            <span className="explore-pop">
              <a href={searchHref()}>Topics and search</a>
              <a href={mapHref()}>Map of ideas</a>
            </span>
          </details>
          <a href={appHref('companies')} aria-current={cur('real')}>Real world</a>
          <a href={feedHref()} aria-current={cur('snacks')}>Snacks ▶</a>
          <a href={appHref('issues')} aria-current={cur('issues')}>Editions</a>
        </span>
        <a href={searchHref()} aria-current={cur('search')}>Search ⌕</a>
      </nav>
      {links.length > 0 && (
        <div className="story-tabs" role="navigation" aria-label="Story sections">
          {links.map(l => <a key={l.href} href={l.href}>{l.label}</a>)}
        </div>
      )}
    </header>
  );
}
