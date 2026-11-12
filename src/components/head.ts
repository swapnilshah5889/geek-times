import { useEffect } from 'react';

export interface HeadInfo {
  title: string;
  description: string;
  /** Absolute URL of a raster preview image used by social link previews. */
  image?: string;
  imageAlt?: string;
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

export function useHead({ title, description, image, imageAlt, type = 'website' }: HeadInfo) {
  useEffect(() => {
    document.title = title;
    upsertMeta('name', 'description', description);
    upsertMeta('property', 'og:title', title);
    upsertMeta('property', 'og:description', description);
    upsertMeta('property', 'og:type', type);
    if (image) {
      upsertMeta('property', 'og:image', image);
      upsertMeta('property', 'og:image:alt', imageAlt ?? 'The Geeky Times illustrated newspaper mark.');
      upsertMeta('property', 'og:image:type', 'image/png');
      upsertMeta('property', 'og:image:width', '1728');
      upsertMeta('property', 'og:image:height', '910');
      upsertMeta('name', 'twitter:image', image);
      if (imageAlt) upsertMeta('name', 'twitter:image:alt', imageAlt);
      else removeMeta('name', 'twitter:image:alt');
    } else {
      removeMeta('property', 'og:image');
      removeMeta('property', 'og:image:alt');
      removeMeta('property', 'og:image:type');
      removeMeta('property', 'og:image:width');
      removeMeta('property', 'og:image:height');
      removeMeta('name', 'twitter:image');
      removeMeta('name', 'twitter:image:alt');
    }
    upsertMeta('name', 'twitter:card', image ? 'summary_large_image' : 'summary');
  }, [title, description, image, imageAlt, type]);
}
