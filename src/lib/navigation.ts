let clientNavigation = false;

/** Push an in-app URL and ask App to resolve the newly active route. */
export function navigate(url: string): void {
  const next = new URL(url, window.location.href);
  if (next.href === window.location.href) return;
  window.history.pushState(null, '', next.href);
  clientNavigation = true;
  window.dispatchEvent(new CustomEvent('geekytimes:navigate'));
}

/** Install the document-wide same-origin link handler. */
export function installInternalLinkInterceptor(): () => void {
  const onClick = (event: MouseEvent) => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    const anchor = target.closest<HTMLAnchorElement>('a[href]');
    if (!anchor || (anchor.target && anchor.target !== '_self') || anchor.hasAttribute('download')) return;

    let next: URL;
    try { next = new URL(anchor.href, window.location.href); }
    catch { return; }
    if (!['http:', 'https:'].includes(next.protocol) || next.origin !== window.location.origin) return;
    if (next.pathname === window.location.pathname && next.search === window.location.search && next.hash) return;

    event.preventDefault();
    // Same-URL activations still notify App to apply its navigation focus rules.
    clientNavigation = true;
    if (next.href === window.location.href) {
      window.dispatchEvent(new CustomEvent('geekytimes:navigate'));
    } else navigate(next.href);
  };
  document.addEventListener('click', onClick);
  return () => document.removeEventListener('click', onClick);
}

/** Mark a history traversal as client navigation (used by route state handling). */
export function markPopNavigation(): void {
  clientNavigation = true;
}

/** True after a route has changed in this document, until a full reload. */
export function wasClientNavigation(): boolean {
  return clientNavigation;
}
