import { useEffect, useState, type ReactNode } from 'react';
import { loadArchive, loadEdition, type Archive, type Edition } from './data/load';
import { FeedPage } from './pages/FeedPage';
import { HomePage } from './pages/HomePage';
import { PaperPage } from './pages/PaperPage';
import { SearchPage } from './pages/SearchPage';
import { currentPath, paperHref } from './lib/routes';

type ArchivePage = 'home' | 'feed' | 'search';
type Route = { page: ArchivePage } | { page: 'paper'; slug: string };
type View = { page: ArchivePage; archive: Archive } | { page: 'paper'; edition: Edition };

// /              front page (bento of covers and bite-size moments)
// /papers/<slug> one issue (old ?paper=<slug> links are redirected here)
// ?feed          snack mode: swipe through moments
// ?search        the archive, with optional q= and tag=
function currentRoute(): Route {
  const params = new URLSearchParams(window.location.search);
  const legacy = params.get('paper');
  if (legacy) {
    window.history.replaceState(null, '', paperHref(legacy) + window.location.hash);
    return { page: 'paper', slug: legacy };
  }
  const path = currentPath();
  const paper = path.match(/^papers\/([^/]+)$/);
  if (paper) return { page: 'paper', slug: paper[1] };
  if (path) throw new Error(`There is no page at “/${path}”.`);
  if (params.has('feed')) return { page: 'feed' };
  if (params.has('search') || params.has('q') || params.has('tag')) return { page: 'search' };
  return { page: 'home' };
}

async function load(route: Route): Promise<View> {
  return route.page === 'paper'
    ? { page: 'paper', edition: await loadEdition(route.slug) }
    : { page: route.page, archive: await loadArchive() };
}

export function App() {
  const [view, setView] = useState<View | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.resolve().then(() => load(currentRoute())).then(setView).catch((err: Error) => {
      console.error(err);
      setError(err.message);
    });
  }, []);

  let content: ReactNode;
  if (error) content = <main><p className="load-error">Sorry, this page could not be loaded. {error}</p></main>;
  else if (!view) content = <main aria-busy="true"><p className="loading">Setting the type…</p></main>;
  else if (view.page === 'paper') content = <PaperPage edition={view.edition} />;
  else if (view.page === 'feed') content = <FeedPage archive={view.archive} />;
  else if (view.page === 'search') content = <SearchPage archive={view.archive} />;
  else content = <HomePage archive={view.archive} />;
  return content;
}
