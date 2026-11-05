import { Kicker, Stamp } from '../components/common';
import { MediaView } from '../components/MediaView';
import { MotionGroup } from '../components/motion';
import { Rich } from '../components/Rich';
import type { ClaimKind, FactsBlock as FactsData, Provenance } from '../types';

// Facts carry a ClaimKind (illustration | model_design | measured_result); Stamp speaks
// Provenance (illustration | evidence | model_design). measured_result maps to evidence so
// the shared stamp renders "Measured result · <trust>" (decision 18 + 42).
const CLAIM_TO_PROVENANCE: Record<ClaimKind, Provenance> = {
  illustration: 'illustration',
  model_design: 'model_design',
  measured_result: 'evidence',
};

export function FactsBlock({ block }: { block: FactsData }) {
  return (
    <MotionGroup>
      <section className="facts" id={block.id}>
        <Kicker text={block.kicker} />
        <ul>
          {block.facts.map(f => (
            <li key={f.figure}>
              {f.media && <MediaView media={f.media} />}
              <b className="fig">{f.figure}</b>
              {f.claim && <Stamp kind={CLAIM_TO_PROVENANCE[f.claim]} />}
              <p><Rich text={f.text} /></p>
              {f.source && <a href={f.source.url}>{f.source.label} ↗</a>}
            </li>
          ))}
        </ul>
      </section>
    </MotionGroup>
  );
}
