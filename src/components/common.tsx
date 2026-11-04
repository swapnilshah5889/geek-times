import type { Provenance } from '../types';

/** Section label; " / " in the data becomes the spaced newspaper separator. */
export function Kicker({ text }: { text: string }) {
  return <div className="label">{text.replaceAll(' / ', '  /  ')}</div>;
}

const PROVENANCE: Record<Provenance, string> = {
  illustration: 'Illustration · numbers invented',
  evidence: 'Evidence · real results',
};

export function Stamp({ kind }: { kind?: Provenance }) {
  if (!kind) return null;
  return <span className={`label stamp stamp-${kind}`}>{PROVENANCE[kind]}</span>;
}
