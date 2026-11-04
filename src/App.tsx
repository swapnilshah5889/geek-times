import { useEffect, useState, type ReactNode } from 'react';
import { loadArchive, loadEdition, type Archive, type Edition } from './data/load';
import { storyById } from './lib/library';
import { currentPath, paperHref } from './lib/routes';
import { CompanyPage } from './pages/CompanyPage';
import { FeedPage } from './pages/FeedPage';
import { HomePage } from './pages/HomePage';
import { IssuePage } from './pages/IssuePage';
import { MapPage } from './pages/MapPage';
import { PaperPage } from './pages/PaperPage';
import { SamplePage } from './pages/SamplePage';
import { SearchPage } from './pages/SearchPage';

type Route =
  | { page: 'home' | 'feed' | 'search' | 'map' }
  | { page: 'paper'; slug: string }
  | { page: 'issue'; id?: string }
  | { page: 'company'; id?: string };

type View =
  | { page: 'home' | 'feed' | 'search' | 'map'; archive: Archive }
  | { page: 'issue' | 'company'; archive: Archive; id?: string }
  | { page: 'paper'; edition: Edition; archive: Archive }
  | { page: 'sample'; archive: Archive; slug: string };

// /                 front page (design D)
// /papers/<slug>    one story (a real paper, or a labelled sample); old ?paper=<slug> links redirect here
// /issues[/<id>]    an issue (no id: the latest)
// /companies[/<id>] a company's explained engineering posts (no id: the first)
// /map              the map of ideas
// ?feed             snack mode: swipe through moments
// ?search           the archive, with optional q= and tag=
function currentRoute(): Route {
  const params = new URLSearchParams(window.location.search);
  const legacy = params.get('paper');
  if (legacy) {
    window.history.replaceState(null, '', paperHref(legacy) + window.location.hash);
    return { page: 'paper', slug: legacy };
  }
  const path = currentPath();
  const [head, second] = path.split('/');
  if (head === 'papers' && second) return { page: 'paper', slug: second };
  if (head === 'issues') return { page: 'issue', id: second };
  if (head === 'companies') return { page: 'company', id: second };
  if (head === 'map' && !second) return { page: 'map' };
  if (path) throw new Error(`There is no page at “/${path}”.`);
  if (params.has('feed')) return { page: 'feed' };
  if (params.has('search') || params.has('q') || params.has('tag')) return { page: 'search' };
  return { page: 'home' };
}

async function load(route: Route): Promise<View> {
  const archive = await loadArchive();
  if (route.page === 'paper') {
    const asked = route.slug;
    const entry = archive.site.papers.find(p => p.slug === asked || p.aliases?.includes(asked));
    if (entry && entry.slug !== asked) {
      window.history.replaceState(null, '', paperHref(entry.slug) + window.location.hash);
      route = { page: 'paper', slug: entry.slug };
    }
    const story = storyById(archive.library, route.slug);
    if (story && !story.real) return { page: 'sample', archive, slug: route.slug };
    return { page: 'paper', edition: await loadEdition(route.slug), archive };
  }
  return { ...route, archive } as View;
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
  else switch (view.page) {
    case 'paper': content = <PaperPage edition={view.edition} archive={view.archive} />; break;
    case 'sample': content = <SamplePage archive={view.archive} slug={view.slug} />; break;
    case 'feed': content = <FeedPage archive={view.archive} />; break;
    case 'search': content = <SearchPage archive={view.archive} />; break;
    case 'issue': content = <IssuePage archive={view.archive} id={view.id} />; break;
    case 'company': content = <CompanyPage archive={view.archive} id={view.id} />; break;
    case 'map': content = <MapPage archive={view.archive} />; break;
    default: content = <HomePage archive={view.archive} />;
  }
  return content;
}
