import { useEffect } from 'react';
import { BlockView } from '../blocks';
import { Masthead } from '../components/Masthead';
import { TagShelf } from '../components/TagShelf';
import { FamilyTree } from '../components/FamilyTree';
import type { Archive, Edition } from '../data/load';
import { EditionContext } from '../edition';
import { MediaBaseContext } from '../lib/mediaBase';
import { SourceTrustContext, sourceOf } from '../lib/source';
import { SourceKindContext } from '../lib/claimLabel';
import { useHead } from '../components/head';

export function PaperPage({ edition, archive }: { edition: Edition; archive: Archive }) {
  const { site, doc, vocab } = edition;
  const source = sourceOf(doc);
  // A blog's trust is in its own block; a paper's comes from its library entry (peer-reviewed, preprint).
  const trust = doc.kind === 'blog' ? doc.blog.trust : archive.library.stories.find(s => s.id === doc.slug)?.trust;

  // No og:image: the lead art is SVG, which social platforms do not render as a preview (raster OG is a later batch).
  useHead({
    title: `${doc.pageTitle} — ${site.name}`,
    description: doc.summary,
    type: 'article',
  });

  useEffect(() => {
    if (window.location.hash) document.getElementById(window.location.hash.slice(1))?.scrollIntoView();
  }, []);

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
  const isBlog = source.kind === 'blog';
  return (
    <EditionContext.Provider value={edition}>
      <MediaBaseContext.Provider value={edition.mediaBaseUrl}>
        <SourceTrustContext.Provider value={trust}>
         <SourceKindContext.Provider value={source.kind}>
          <main>
            <Masthead site={site} meta={[doc.desk, isBlog ? `Engineering post from ${source.year}` : `Paper from ${source.year}`]} links={links} />
            {doc.blocks.map((block, i) => <BlockView block={block} key={block.id ?? i} />)}
            {node && <FamilyTree archive={archive} nodeId={node.id} />}
            <div id="related"><TagShelf tags={doc.tags} vocab={vocab} kind={source.kind} /></div>
            <footer>
              <span>{`${site.name}  ✦  ${doc.desk}`}</span>
              <a href={source.url}>{isBlog ? 'Read the original post ↗' : 'Read the original paper ↗'}</a>
              {source.archivedUrl && <a href={source.archivedUrl}>Archived copy ↗</a>}
              {isBlog && <span>{`Real claims come from ${source.by}’s own writeup. Each one is labelled with what kind of claim it is; illustration numbers are invented.`}</span>}
            </footer>
          </main>
         </SourceKindContext.Provider>
        </SourceTrustContext.Provider>
      </MediaBaseContext.Provider>
    </EditionContext.Provider>
  );
}
