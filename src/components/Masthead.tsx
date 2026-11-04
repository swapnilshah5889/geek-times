import { searchHref } from '../lib/tags';
import { homeHref } from '../lib/routes';
import type { SiteConfig } from '../types';

interface Props {
  site: SiteConfig;
  /** Left and right of the top rule, e.g. issue number and desk. */
  meta?: [string, string];
  links?: { href: string; label: string }[];
}

export function Masthead({ site, meta = ['', ''], links = [] }: Props) {
  return (
    <header>
      <div className="meta">
        <span>{meta[0]}</span>
        <span>{site.tagline}</span>
        <span>{meta[1]}</span>
      </div>
      <div className="mast"><a href={homeHref()} className="mast-link">{site.name}</a></div>
      <div className="motto">{site.motto}</div>
      <nav>
        <span>{site.navLabel}</span>
        <span className="links">
          {links.map(l => <a key={l.href} href={l.href}>{l.label}</a>)}
          <a href={searchHref()}>Search ⌕</a>
        </span>
      </nav>
    </header>
  );
}
