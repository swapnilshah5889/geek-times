import { useEffect } from 'react';

export interface HeadInfo {
  title: string;
  description: string;
  /** Absolute URL of a raster preview image. Omit it: SVG art is not a reliable social-card image (raster OG is later). */
  image?: string;
  /** Open Graph type: "website" for collections and index pages, "article" for one story. */
  type?: string;
}

// Sets the document title and the description / Open Graph / Twitter tags for the current page. The
// prerender script (scripts/prerender.ts) captures the DOM after this runs, so each route's HTML carries its own
// tags. Tags a page does not set (for example og:image) are removed, so a client-side visit cannot inherit the
// previous page's preview.
function upsertMeta(attr: 'name' | 'property', key: string, content: string) {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, key);
    document.head.append(el);
  }
  el.content = content;
}

function removeMeta(attr: 'name' | 'property', key: string) {
  document.head.querySelector(`meta[${attr}="${key}"]`)?.remove();
}

export function useHead({ title, description, image, type = 'website' }: HeadInfo) {
  useEffect(() => {
    document.title = title;
    upsertMeta('name', 'description', description);
    upsertMeta('property', 'og:title', title);
    upsertMeta('property', 'og:description', description);
    upsertMeta('property', 'og:type', type);
    if (image) upsertMeta('property', 'og:image', image);
    else removeMeta('property', 'og:image');
    upsertMeta('name', 'twitter:card', image ? 'summary_large_image' : 'summary');
  }, [title, description, image, type]);
}
