import { ClaimStamp, Kicker } from '../components/common';
import { MediaView } from '../components/MediaView';
import { MotionGroup } from '../components/motion';
import { Rich } from '../components/Rich';
import type { FactsBlock as FactsData } from '../types';

// Each fact carries its own claim kind (illustration | model_design | measured_result). The story page
// provides the source's trust and kind, so ClaimStamp can say e.g. "Measured result · company-reported".

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
              <ClaimStamp claim={f.claim} />
              <p><Rich text={f.text} /></p>
              {f.source && <a href={f.source.url}>{`${f.source.label} ↗`}</a>}
            </li>
          ))}
        </ul>
      </section>
    </MotionGroup>
  );
}
