import { createContext, useContext } from 'react';

/** Where media `src` paths resolve (local folder now, CDN later). Provided once per page. */
export const MediaBaseContext = createContext<string>(new URL(import.meta.env.BASE_URL, window.location.origin).href);

export const useMediaBase = () => useContext(MediaBaseContext);

/** Public raster artwork used in crawler-generated Open Graph previews. */
export function shareCardUrl(mediaBaseUrl: string): string {
  return new URL('brand/social-card.png', mediaBaseUrl).href;
}
