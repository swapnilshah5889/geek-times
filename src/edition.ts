import { createContext, useContext } from 'react';
import type { Edition } from './data/load';

export const EditionContext = createContext<Edition | null>(null);

export function useEdition(): Edition {
  const edition = useContext(EditionContext);
  if (!edition) throw new Error('useEdition must be used inside <EditionContext.Provider>');
  return edition;
}
