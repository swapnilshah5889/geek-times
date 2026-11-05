import { useEffect } from 'react';

export interface HeadInfo {
  title: string;
  description: string;
  /** Absolute URL of a preview image. Omitted: no og:image tag is written. */
  image?: string;
  type?: string;
}

// Sets the document title and the description / Open Graph / Twitter tags for the current page. The
// prerender script (scripts/prerender.ts) captures the DOM after this runs, so each route's HTML carries its own
// tags. On unmount nothing is removed: the next page's useHead overwrites the same tags.
function upsertMeta(attr: 'name' | 'property', key: string, content: string) {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, key);
    document.head.append(el);
  }
  el.content = content;
}

export function useHead({ title, description, image, type = 'article' }: HeadInfo) {
  useEffect(() => {
    document.title = title;
    upsertMeta('name', 'description', description);
    upsertMeta('property', 'og:title', title);
    upsertMeta('property', 'og:description', description);
    upsertMeta('property', 'og:type', type);
    if (image) upsertMeta('property', 'og:image', image);
    upsertMeta('name', 'twitter:card', 'summary_large_image');
  }, [title, description, image, type]);
}
