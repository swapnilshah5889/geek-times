import { Kicker, Stamp } from '../components/common';
import { pad } from '../lib/format';
import { MediaView } from '../components/MediaView';
import { MotionButton, MotionGroup } from '../components/motion';
import { Rich } from '../components/Rich';
import type { StoryBlock as StoryData } from '../types';

export function StoryBlock({ block }: { block: StoryData }) {
  return (
    <MotionGroup>
      <section className="section" id={block.id}>
        <Kicker text={block.kicker} />
        <div className="story-intro"><h2>{block.title}</h2><MotionButton noun="picture story" /></div>
        <div className="chapters">
          {block.chapters.map((c, i) => (
            <article className="chapter" key={c.title}>
              <header><span className="chapnum">{pad(i + 1)}</span><span className="label">{c.part}</span><Stamp kind={c.provenance} /></header>
              <h3>{c.title}</h3>
              <figure>
                <MediaView media={c.media} />
                <figcaption><p><Rich text={c.caption} /></p></figcaption>
              </figure>
            </article>
          ))}
        </div>
      </section>
    </MotionGroup>
  );
}
