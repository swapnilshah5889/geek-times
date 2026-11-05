import { createContext } from 'react';
import type { ClaimKind, Library, LibraryStory, Provenance, SourceKind } from '../types';

// One source of wording for claim labels (decision 18). Rendered by ClaimStamp in components/common.tsx;
// used by every page so a claim reads the same everywhere.

export type Trust = NonNullable<LibraryStory['trust']>;

/** The kind of source the story is about. PaperPage provides it; a paper is the default. */
export const SourceKindContext = createContext<SourceKind>('paper');

const TRUST: Record<Trust, string> = {
  peer_reviewed: 'peer-reviewed',
  preprint: 'preprint',
  company_reported: 'company-reported',
};

const CLAIM_OF_PROVENANCE: Record<Provenance, ClaimKind> = {
  illustration: 'illustration', model_design: 'model_design', evidence: 'measured_result',
};

/** The claim a strip or chapter's `provenance` stands for. */
export const claimOf = (p?: Provenance): ClaimKind | undefined => (p ? CLAIM_OF_PROVENANCE[p] : undefined);

/** The CSS class for a stamp (edition.css keeps the older `stamp-evidence` name for measured results). */
export const stampClass = (claim: ClaimKind): string =>
  ({ illustration: 'stamp-illustration', model_design: 'stamp-model_design', measured_result: 'stamp-evidence' })[claim];

/**
 * The wording for a claim. Every sourced claim carries its source's trust when it is known (a model design too).
 * Illustrations have no source, so they never take a trust. "Company-reported" describes the source: it never
 * turns a model design into a measured result.
 */
export function claimLabel(claim: ClaimKind, trust?: Trust, source: SourceKind = 'paper'): string {
  if (claim === 'illustration') return 'Illustration · numbers invented';
  const suffix = trust ? ` · ${TRUST[trust]}` : '';
  if (claim === 'model_design') return `${source === 'blog' ? 'From the post' : 'From the paper'} · model design${suffix}`;
  return `Measured result${suffix}`;
}

/** A paper or a company post, read from the library entry (a story's id is its slug). */
export function sourceKindOf(library: Library, slug: string): SourceKind {
  return library.stories.find(s => s.id === slug)?.kind === 'blog' ? 'blog' : 'paper';
}
