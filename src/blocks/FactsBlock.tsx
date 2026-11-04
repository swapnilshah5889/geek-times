import { Kicker } from '../components/common';
import { MediaView } from '../components/MediaView';
import { MotionGroup } from '../components/motion';
import { Rich } from '../components/Rich';
import type { FactsBlock as FactsData } from '../types';

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
              <p><Rich text={f.text} /></p>
              {f.source && <a href={f.source.url}>{f.source.label} ↗</a>}
            </li>
          ))}
        </ul>
      </section>
    </MotionGroup>
  );
}
