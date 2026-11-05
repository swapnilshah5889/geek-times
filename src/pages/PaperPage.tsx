import { useEffect } from 'react';
import { BlockView } from '../blocks';
import { Masthead } from '../components/Masthead';
import { TagShelf } from '../components/TagShelf';
import { FamilyTree } from '../components/FamilyTree';
import type { Archive, Edition } from '../data/load';
import { EditionContext } from '../edition';
import { MediaBaseContext } from '../lib/mediaBase';

export function PaperPage({ edition, archive }: { edition: Edition; archive: Archive }) {
  const { site, doc, vocab } = edition;

  useEffect(() => {
    document.title = `${site.name} — ${doc.pageTitle}`;
    if (window.location.hash) document.getElementById(window.location.hash.slice(1))?.scrollIntoView();
  }, [site, doc]);

  // Story tabs (decision 18): the same five sections on every story, linking to the matching part of the page.
  const idOf = (type: string) => doc.blocks.find(b => b.type === type)?.id;
  const node = archive.library.nodes.find(n => n.story === doc.slug);
  const links = [
    { href: `#${idOf('lead') ?? 'lead'}`, label: 'The big idea' },
    idOf('comic') && { href: `#${idOf('comic')}`, label: 'How it works' },
    node && { href: '#tree', label: 'Family tree' },
    idOf('facts') && { href: `#${idOf('facts')}`, label: 'Evidence' },
    { href: '#related', label: 'Explore related ideas' },
  ].filter((l): l is { href: string; label: string } => !!l);
  return (
    <EditionContext.Provider value={edition}>
      <MediaBaseContext.Provider value={edition.mediaBaseUrl}>
        <main>
          <Masthead site={site} meta={[doc.desk, `Paper from ${doc.paper.year}`]} links={links} />
          {doc.blocks.map((block, i) => <BlockView block={block} key={block.id ?? i} />)}
          {node && <FamilyTree archive={archive} nodeId={node.id} />}
          <div id="related"><TagShelf tags={doc.tags} vocab={vocab} /></div>
          <footer>
            <span>{site.name} &nbsp; ✦ &nbsp; {doc.desk}</span>
            <a href={doc.paper.url}>Read the original paper ↗</a>
          </footer>
        </main>
      </MediaBaseContext.Provider>
    </EditionContext.Provider>
  );
}
