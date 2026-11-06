import { Kicker, Stamp } from '../components/common';
import { pad } from '../lib/format';
import { MediaView } from '../components/MediaView';
import { MotionButton, MotionGroup } from '../components/motion';
import { Rich } from '../components/Rich';
import type { ComicBlock as ComicData, Strip } from '../types';

function ComicStrip({ strip, n, anchor }: { strip: Strip; n: number; anchor: string }) {
  return (
    <article className="strip" id={strip.id ?? anchor}>
      <header>
        <span className="chapnum">{pad(n)}</span>
        <div><h3>{strip.title}</h3>{strip.kicker && <span className="kicker">{strip.kicker}</span>}</div>
        <Stamp kind={strip.provenance} />
      </header>
      <div className="comic">
        {strip.panels.map(p => (
          <figure className="panel" key={p.media.src}>
            <figcaption><Rich text={p.caption} /></figcaption>
            <MediaView media={p.media} />
          </figure>
        ))}
      </div>
      {strip.grownUpWords && <p className="gw">{`Grown-up words: ${strip.grownUpWords}`}</p>}
    </article>
  );
}

export function ComicBlock({ block }: { block: ComicData }) {
  return (
    <MotionGroup>
      <section className="section comic-section" id={block.id}>
        <Kicker text={block.kicker} />
        <div className="story-intro"><h2>{block.title}</h2><MotionButton noun="the comics" /></div>
        {block.deck && <p className="comic-deck"><Rich text={block.deck} /></p>}
        {block.howTo && <p className="howto"><span className="label">How to read it </span><Rich text={block.howTo} /></p>}
        {block.strips.map((s, i) => <ComicStrip strip={s} n={i + 1} anchor={`${block.id}-${i + 1}`} key={s.title} />)}
      </section>
    </MotionGroup>
  );
}
