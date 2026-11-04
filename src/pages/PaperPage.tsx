import { useEffect } from 'react';
import { BlockView } from '../blocks';
import { Masthead } from '../components/Masthead';
import { TagShelf } from '../components/TagShelf';
import type { Edition } from '../data/load';
import { EditionContext } from '../edition';
import { MediaBaseContext } from '../lib/mediaBase';

export function PaperPage({ edition }: { edition: Edition }) {
  const { site, doc, vocab } = edition;

  useEffect(() => {
    document.title = `${site.name} — ${doc.pageTitle}`;
    if (window.location.hash) document.getElementById(window.location.hash.slice(1))?.scrollIntoView();
  }, [site, doc]);

  const links = doc.blocks.filter(b => b.nav && b.id).map(b => ({ href: `#${b.id}`, label: b.nav! }));
  return (
    <EditionContext.Provider value={edition}>
      <MediaBaseContext.Provider value={edition.mediaBaseUrl}>
        <main>
          <Masthead site={site} meta={[`Vol. ${doc.issue.volume}  ·  No. ${doc.issue.number}`, doc.issue.desk]} links={links} />
          {doc.blocks.map((block, i) => <BlockView block={block} key={block.id ?? i} />)}
          <TagShelf tags={doc.tags} vocab={vocab} />
          <footer>
            <span>{site.name} &nbsp; ✦ &nbsp; Issue {doc.issue.number}</span>
            <a href={doc.paper.url}>Read the original paper ↗</a>
          </footer>
        </main>
      </MediaBaseContext.Provider>
    </EditionContext.Provider>
  );
}
