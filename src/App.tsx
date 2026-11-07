import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { BookLoader, LOADER_GRACE_MS, type BookLoaderPhase } from './components/BookLoader';
import { loadArchive, loadEdition, loadSite, type Archive, type Edition } from './data/load';
import { editionFromInitial, makeInitialData, routeKeyFromLocation, type InitialData } from './data/initial-snapshot';
import { Masthead } from './components/Masthead';
import { storyById } from './lib/library';
import { useTodayLabel } from './lib/format';
import { currentPath, paperHref } from './lib/routes';
import { installInternalLinkInterceptor, markPopNavigation } from './lib/navigation';
import type { SiteConfig } from './types';
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
    const story = storyById(archive.library, route.slug);
    if (story && !story.real) return { page: 'sample', archive, slug: route.slug };
    return { page: 'paper', edition: await loadEdition(route.slug), archive };
  }
  return { ...route, archive } as View;
}

function viewFromInitial(initial: InitialData): View {
  const route = currentRoute();
  const archive = initial.archive;
  if (route.page === 'paper') {
    const story = storyById(archive.library, route.slug);
    if (story && !story.real) return { page: 'sample', archive, slug: route.slug };
    const edition = editionFromInitial(initial);
    if (!edition) throw new Error(`Prerender data is missing the story “${route.slug}”.`);
    return { page: 'paper', edition, archive };
  }
  return { ...route, archive } as View;
}

type NavigationCommit = { kind: 'push' | 'pop'; url: string; sequence: number };

// A navigation that has already shown the book lifts it out; a fast one only raises the new page.
function settleNavigation(phase: BookLoaderPhase): BookLoaderPhase {
  return phase === 'pending' || phase === 'nav-slow' ? 'reveal' : 'nav-reveal';
}

export function App({ initial }: { initial?: InitialData } = {}) {
  const [view, setView] = useState<View | null>(() => initial ? viewFromInitial(initial) : null);
  const [phase, setPhase] = useState<BookLoaderPhase>(() => initial ? 'idle' : 'pending');
  useEffect(() => { if (view && phase === 'pending') setPhase('reveal'); }, [view, phase]);
  const finishReveal = useCallback(() => setPhase('idle'), []);
  const navTimer = useRef<number | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);
  const [site, setSite] = useState<SiteConfig | null>(initial?.archive.site ?? null);
  const [navCommit, setNavCommit] = useState<NavigationCommit | null>(null);
  const sequence = useRef(0);
  const displayedUrl = useRef(window.location.href);
  const displayedRoute = useRef(window.location.pathname + window.location.search);
  const savedScroll = useRef(new Map<string, number>());
  const today = useTodayLabel();

  useEffect(() => {
    const previousRestoration = window.history.scrollRestoration;
    window.history.scrollRestoration = 'manual';
    const uninstallLinks = installInternalLinkInterceptor();

    function runRoute(kind: 'push' | 'pop') {
      const urlBeforeRedirect = window.location.href;
      savedScroll.current.set(displayedUrl.current, window.scrollY);
      const routeKey = window.location.pathname + window.location.search;
      if (routeKey === displayedRoute.current) {
        // Hash-only history traversal leaves the current React page in place.
        if (window.location.hash) document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView();
        else if (kind === 'pop') window.scrollTo(0, savedScroll.current.get(window.location.href) ?? 0);
        return;
      }
      const token = ++sequence.current;
      setError(null);
      setLiveError(null);
      // The book appears only if the load outlasts the grace period; a cold load already shows it.
      window.clearTimeout(navTimer.current);
      setPhase(p => p === 'pending' || p === 'nav-slow' ? p : 'nav-pending');
      navTimer.current = window.setTimeout(() => setPhase(p => p === 'nav-pending' ? 'nav-slow' : p), LOADER_GRACE_MS);
      Promise.resolve().then(() => load(currentRoute())).then(next => {
        if (token !== sequence.current) return;
        window.clearTimeout(navTimer.current);
        setView(next);
        setSite(next.archive.site);
        setPhase(settleNavigation);
        setNavCommit({ kind, url: window.location.href, sequence: token });
      }).catch((err: Error) => {
        if (token !== sequence.current) return;
        console.error(err);
        window.clearTimeout(navTimer.current);
        setError(err.message);
        setPhase(settleNavigation);
        setNavCommit({ kind, url: window.location.href || urlBeforeRedirect, sequence: token });
      });
    }

    const onPush = () => runRoute('push');
    const onPop = () => { markPopNavigation(); runRoute('pop'); };
    window.addEventListener('geekytimes:navigate', onPush);
    window.addEventListener('popstate', onPop);

    if (initial) {
      // The embedded snapshot exists only to reproduce the prerendered first paint. A fresh
      // Supabase read still decides what is live after hydration; failures remain visible.
      if (initial.source === 'supabase') {
        const token = ++sequence.current;
        Promise.resolve().then(() => load(currentRoute())).then(next => {
          if (token !== sequence.current) return;
          setView(previous => JSON.stringify(previous) === JSON.stringify(next) ? previous : next);
          setSite(next.archive.site);
          setLiveError(null);
        }).catch((err: Error) => {
          if (token !== sequence.current) return;
          console.error(err);
          setLiveError('Could not check for updates. This saved page may be out of date. Reload to try again.');
        });
      }
    } else {
      const token = ++sequence.current;
      Promise.resolve().then(() => load(currentRoute())).then(next => {
        if (token !== sequence.current) return;
        setView(next);
        setSite(next.archive.site);
      }).catch((err: Error) => {
        if (token !== sequence.current) return;
        console.error(err);
        setError(err.message);
        // Lift the book so the error is not hidden behind it.
        setPhase(settleNavigation);
      });
    }

    return () => {
      sequence.current++;
      uninstallLinks();
      window.removeEventListener('geekytimes:navigate', onPush);
      window.removeEventListener('popstate', onPop);
      window.history.scrollRestoration = previousRestoration;
    };
  }, [initial]);

  // site.json is the same cached request loadArchive uses, so the masthead can appear before the rest of the archive.
  // A failure here is reported by load() above, so it is ignored.
  useEffect(() => {
    if (!initial) loadSite().then(setSite, () => undefined);
  }, [initial]);

  // During prerender, the puppeteer script installs a receiver at window.__collect_initial_data__.
  // When the view is ready, hand it the snapshot so the renderer can embed it in the HTML.
  useEffect(() => {
    if (!view) return;
    if (!window.__gt_prerender__) return;
    const route = routeKeyFromLocation();
    if (!route) return;
    const data = makeInitialData(route, view.archive, view.page === 'paper' ? view.edition.doc : undefined);
    window.__collect_initial_data__?.(data);
  }, [view]);

  useEffect(() => {
    if (!navCommit) return;
    displayedUrl.current = navCommit.url;
    displayedRoute.current = new URL(navCommit.url).pathname + new URL(navCommit.url).search;
    if (navCommit.kind === 'push') {
      if (window.location.hash) document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView();
      else window.scrollTo(0, 0);
      const main = document.querySelector<HTMLElement>('main');
      main?.setAttribute('tabindex', '-1');
      main?.focus({ preventScroll: true });
    } else if (window.location.hash) {
      document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView();
    } else {
      window.scrollTo(0, savedScroll.current.get(navCommit.url) ?? 0);
    }
    setNavCommit(null);
  }, [navCommit]);

  // Native direct links with hashes are already scrolled by the browser, but client-only
  // first loads may resolve the target only after the async page arrives.
  useEffect(() => {
    if (!initial && view && window.location.hash && !navCommit) {
      document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView();
    }
  }, [initial, view, navCommit]);

  let content: ReactNode;
  if (error) content = <main className="site-main" tabIndex={-1}>
    {site && <Masthead site={site} meta={['', '']} />}
    <p className="load-error">Sorry, this page could not be loaded. {error}</p>
    <p><a href="/">Back to the front page →</a></p>
  </main>;
  else if (!view) content = (
    <main className="site-main" aria-busy="true" tabIndex={-1}>
      {site && <Masthead site={site} meta={[today, '']} edition />}
    </main>
  );
  else switch (view.page) {
    case 'paper': content = <PaperPage edition={view.edition} archive={view.archive} />; break;
    case 'sample': content = <SamplePage archive={view.archive} slug={view.slug} />; break;
    case 'feed': content = <FeedPage archive={view.archive} />; break;
    case 'search': content = <SearchPage archive={view.archive} key={window.location.search} />; break;
    case 'issue': content = <IssuePage archive={view.archive} id={view.id} />; break;
    case 'company': content = <CompanyPage archive={view.archive} id={view.id} />; break;
    case 'map': content = <MapPage archive={view.archive} key={window.location.search} />; break;
    default: content = <HomePage archive={view.archive} />;
  }
  return <>
    <BookLoader phase={phase} onComplete={finishReveal}>
      {content}
    </BookLoader>
    {liveError && <div className="live-error" role="status">{liveError}</div>}
  </>;
}
