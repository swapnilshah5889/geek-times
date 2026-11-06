import { useContext } from 'react';
import type { ClaimKind, Provenance, SourceKind, StoryDoc } from '../types';
import { SourceTrustContext, sourceOf } from '../lib/source';
import { SourceKindContext, claimLabel, claimOf, stampClass, type Trust } from '../lib/claimLabel';

/** Section label; " / " in the data becomes the spaced newspaper separator. */
export function Kicker({ text }: { text: string }) {
  return <div className="label">{text.replaceAll(' / ', '  /  ')}</div>;
}

/**
 * The claim label for a number, strip or chapter. `trust` and `source` default to the story page's context
 * (SourceTrustContext, SourceKindContext); pass them explicitly anywhere outside a story page.
 */
export function ClaimStamp({ claim, trust, source }: { claim?: ClaimKind; trust?: Trust; source?: SourceKind }) {
  const contextTrust = useContext(SourceTrustContext);
  const contextKind = useContext(SourceKindContext);
  if (!claim) return null;
  return <span className={`label stamp ${stampClass(claim)}`}>{claimLabel(claim, trust ?? contextTrust, source ?? contextKind)}</span>;
}

/** A stamp from a strip's or chapter's `provenance` (its intent). Same props as before, plus an optional source kind. */
export function Stamp({ kind, trust, source }: { kind?: Provenance; trust?: Trust; source?: SourceKind }) {
  return <ClaimStamp claim={claimOf(kind)} trust={trust} source={source} />;
}

/** The story's "The paper" / "The engineering post" line under the headline. */
export function SourceByline({ doc }: { doc: StoryDoc }) {
  const source = sourceOf(doc);
  return (
    <div className="byline">
      <b>{source.kind === 'blog' ? 'The engineering post' : 'The paper'}</b>{` · ${source.title}`}<i>{`${source.by}, ${source.dated}`}</i>
    </div>
  );
}
