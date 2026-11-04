import { useEffect, useState } from 'react';
import { BlockView } from './blocks';
import { loadEdition, type Edition } from './data/load';
import { EditionContext } from './edition';

function Masthead({ site, doc }: Pick<Edition, 'site' | 'doc'>) {
  const links = doc.blocks.filter(b => b.nav && b.id);
  return (
    <header>
      <div className="meta">
        <span>Vol. {doc.issue.volume} &nbsp;·&nbsp; No. {doc.issue.number}</span>
        <span>{site.tagline}</span>
        <span>{doc.issue.desk}</span>
      </div>
      <div className="mast">{site.name}</div>
      <div className="motto">{site.motto}</div>
      <nav>
        <span>{site.navLabel}</span>
        <span className="links">{links.map(b => <a key={b.id} href={`#${b.id}`}>{b.nav}</a>)}</span>
      </nav>
    </header>
  );
}

type State = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; edition: Edition };

export function App() {
  const [state, setState] = useState<State>({ status: 'loading' });

  useEffect(() => {
    const slug = new URLSearchParams(window.location.search).get('paper');
    loadEdition(slug)
      .then(edition => setState({ status: 'ready', edition }))
      .catch((err: Error) => {
        console.error(err);
        setState({ status: 'error', message: err.message });
      });
  }, []);

  useEffect(() => {
    if (state.status !== 'ready') return;
    const { site, doc } = state.edition;
    document.title = `${site.name} — ${doc.pageTitle}`;
    if (window.location.hash) document.getElementById(window.location.hash.slice(1))?.scrollIntoView();
  }, [state]);

  if (state.status === 'loading') return <main aria-busy="true"><p className="loading">Setting the type…</p></main>;
  if (state.status === 'error') return <main><p className="load-error">Sorry, this edition could not be loaded. {state.message}</p></main>;

  const { edition } = state;
  const { site, doc } = edition;
  return (
    <EditionContext.Provider value={edition}>
      <main>
        <Masthead site={site} doc={doc} />
        {doc.blocks.map((block, i) => <BlockView block={block} key={block.id ?? i} />)}
        <footer>
          <span>{site.name} &nbsp; ✦ &nbsp; Issue {doc.issue.number}</span>
          <a href={doc.paper.url}>Read the original paper ↗</a>
        </footer>
      </main>
    </EditionContext.Provider>
  );
}
