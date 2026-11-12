import { StrictMode } from 'react';
import { createRoot, hydrateRoot } from 'react-dom/client';
import { App } from './App';
import { readInitialData } from './data/initial-snapshot';
import './styles/edition.css';
import './styles/site.css';

// Decision 50: hydrate when the prerendered HTML carries a matching initial-data snapshot;
// otherwise the page was not prerendered or the snapshot is incompatible — createRoot instead.
const container = document.getElementById('root')!;
// During prerender puppeteer sets __gt_prerender__ before our scripts run. Skip hydration there
// so the renderer always produces a fresh tree (stale snapshots on disk otherwise mismatch).
const initial = window.__gt_prerender__ ? null : readInitialData();
const tree = (
  <StrictMode>
    <App initial={initial ?? undefined} />
  </StrictMode>
);

if (initial) {
  window.__mount_mode__ = 'hydrated';
  hydrateRoot(container, tree, {
    onRecoverableError: (error, errorInfo) => {
      console.warn('Hydration mismatch:', (error as Error).message);
      if (errorInfo.componentStack) console.warn('Component stack:', errorInfo.componentStack);
    },
  });
} else {
  window.__mount_mode__ = 'created';
  createRoot(container).render(tree);
}
