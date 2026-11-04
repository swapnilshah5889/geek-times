import { createContext, useContext } from 'react';

/** Where media `src` paths resolve (local folder now, CDN later). Provided once per page. */
export const MediaBaseContext = createContext<string>(new URL(import.meta.env.BASE_URL, window.location.origin).href);

export const useMediaBase = () => useContext(MediaBaseContext);
