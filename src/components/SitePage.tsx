import { useEffect, useMemo, type ReactNode } from 'react';
import { mediaBaseFor, type Archive } from '../data/load';
import { latestIssue } from '../lib/library';
import { MediaBaseContext } from '../lib/mediaBase';
import { searchHref } from '../lib/tags';
import { Masthead, type NavSection } from './Masthead';
import { MotionButton, MotionGroup } from './motion';

/** The frame every site page shares: motion switch, media base, masthead with the same navigation, footer. */
export function SitePage({ archive, title, active, meta, motion = true, children }: {
  archive: Archive; title: string; active?: NavSection; meta?: [string, string]; motion?: boolean; children: ReactNode;
}) {
  const { site, library } = archive;
  const issue = latestIssue(library);
  const base = useMemo(() => mediaBaseFor(site), [site]);
  useEffect(() => { document.title = `${site.name} — ${title}`; window.scrollTo(0, 0); }, [site, title]);
  return (
    <MediaBaseContext.Provider value={base}>
      <MotionGroup>
        <main className="site-main">
          <Masthead site={site} active={active} meta={meta ?? [`Vol. ${issue.volume}`, `No. ${issue.number}`]} />
          {motion && <div className="f-motion"><MotionButton noun="animations" /></div>}
          {children}
          <footer>
            <span>{site.name} &nbsp; ✦ &nbsp; {site.motto}</span>
            <a href={searchHref()}>The archive →</a>
          </footer>
        </main>
      </MotionGroup>
    </MediaBaseContext.Provider>
  );
}

export function Crumbs({ items }: { items: ({ href: string; label: string } | string)[] }) {
  return (
    <p className="crumbs label">
      {items.map((it, i) => (
        <span key={i}>
          {i > 0 && '  /  '}
          {typeof it === 'string' ? <span className="crumb-now">{it}</span> : <a href={it.href}>{it.label}</a>}
        </span>
      ))}
    </p>
  );
}
