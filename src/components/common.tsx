import { useContext } from 'react';
import type { LibraryStory, Provenance, StoryDoc } from '../types';
import { SourceTrustContext, sourceOf } from '../lib/source';

/** Section label; " / " in the data becomes the spaced newspaper separator. */
export function Kicker({ text }: { text: string }) {
  return <div className="label">{text.replaceAll(' / ', '  /  ')}</div>;
}

const PROVENANCE: Record<Provenance, string> = {
  illustration: 'Illustration · numbers invented',
  evidence: 'Measured result',
  model_design: 'From the paper · model design',
};

const TRUST: Record<NonNullable<LibraryStory['trust']>, string> = {
  peer_reviewed: 'peer-reviewed',
  preprint: 'preprint',
  company_reported: 'company-reported',
};

/** The claim label. Measured results show their source's trust: an explicit `trust`, else the story's (SourceTrustContext). */
export function Stamp({ kind, trust }: { kind?: Provenance; trust?: LibraryStory['trust'] }) {
  const storyTrust = useContext(SourceTrustContext);
  if (!kind) return null;
  const level = trust ?? storyTrust;
  const source = kind === 'evidence' && level ? ` · ${TRUST[level]}` : '';
  return <span className={`label stamp stamp-${kind}`}>{PROVENANCE[kind]}{source}</span>;
}

/** The story's "The paper" / "The engineering post" line under the headline. */
export function SourceByline({ doc }: { doc: StoryDoc }) {
  const source = sourceOf(doc);
  return (
    <div className="byline">
      <b>{source.kind === 'blog' ? 'The engineering post' : 'The paper'}</b> · {source.title}<i>{source.by}, {source.dated}</i>
    </div>
  );
}
