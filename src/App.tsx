import { useEffect, useState, type ReactNode } from 'react';
import { loadArchive, loadEdition, type Archive, type Edition } from './data/load';
import { PaperPage } from './pages/PaperPage';
import { SearchPage } from './pages/SearchPage';

type Route = { page: 'search' } | { page: 'paper'; slug: string | null };
type View = { page: 'search'; archive: Archive } | { page: 'paper'; edition: Edition };

// ?search (with optional q= and tag=) opens the archive search; ?paper=<slug> (or nothing) opens an issue.
function currentRoute(): Route {
  const params = new URLSearchParams(window.location.search);
  if (params.has('search') || params.has('q') || params.has('tag')) return { page: 'search' };
  return { page: 'paper', slug: params.get('paper') };
}

async function load(route: Route): Promise<View> {
  return route.page === 'search'
    ? { page: 'search', archive: await loadArchive() }
    : { page: 'paper', edition: await loadEdition(route.slug) };
}

export function App() {
  const [view, setView] = useState<View | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    load(currentRoute()).then(setView).catch((err: Error) => {
      console.error(err);
      setError(err.message);
    });
  }, []);

  let content: ReactNode;
  if (error) content = <main><p className="load-error">Sorry, this page could not be loaded. {error}</p></main>;
  else if (!view) content = <main aria-busy="true"><p className="loading">Setting the type…</p></main>;
  else if (view.page === 'search') content = <SearchPage archive={view.archive} />;
  else content = <PaperPage edition={view.edition} />;
  return content;
}
