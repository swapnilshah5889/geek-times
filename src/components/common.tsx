import type { LibraryStory, Provenance } from '../types';

/** Section label; " / " in the data becomes the spaced newspaper separator. */
export function Kicker({ text }: { text: string }) {
  return <div className="label">{text.replaceAll(' / ', '  /  ')}</div>;
}

const PROVENANCE: Record<Provenance, string> = {
  illustration: 'Illustration · numbers invented',
  evidence: 'Evidence · real results',
  model_design: 'From the paper · model design',
};

const TRUST: Record<NonNullable<LibraryStory['trust']>, string> = {
  peer_reviewed: 'Peer-reviewed paper',
  preprint: 'Preprint',
  company_reported: 'Company-reported',
};

export function Stamp({ kind, trust }: { kind?: Provenance; trust?: LibraryStory['trust'] }) {
  if (!kind) return null;
  const source = kind === 'evidence' && trust ? ` · ${TRUST[trust]}` : '';
  return <span className={`label stamp stamp-${kind}`}>{PROVENANCE[kind]}{source}</span>;
}
