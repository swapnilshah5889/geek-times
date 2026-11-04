import { useEffect, useState } from 'react';
import { Kicker } from '../components/common';
import { pad } from '../lib/format';
import { MediaView } from '../components/MediaView';
import { MotionButton, MotionGroup } from '../components/motion';
import { useMotion } from '../lib/motion';
import { Rich } from '../components/Rich';
import { useEdition } from '../edition';
import type { LeadBlock as LeadData } from '../types';

function Slideshow({ slideshow }: { slideshow: LeadData['slideshow'] }) {
  const { slides, intervalMs = 5500 } = slideshow;
  const { held } = useMotion();
  const [index, setIndex] = useState(0);
  const next = () => setIndex(i => (i + 1) % slides.length);

  // Restarts whenever the slide changes, so a manual "Next" gets a full interval too.
  useEffect(() => {
    if (held || slides.length < 2) return;
    const id = window.setTimeout(() => setIndex((index + 1) % slides.length), intervalMs);
    return () => window.clearTimeout(id);
  }, [held, index, intervalMs, slides.length]);

  const slide = slides[index];
  return (
    <figure>
      <div className="plate slides">
        {slides.map((s, i) => (
          <div key={s.media.src} className={i === index ? 'slide show' : 'slide'} inert={i !== index}>
            <MediaView media={s.media} />
          </div>
        ))}
      </div>
      <div className="controls">
        <span>{`${pad(index + 1)} / ${pad(slides.length)} · ${slide.label}`}</span>
        <div className="buttons">
          <MotionButton />
          {slides.length > 1 && <button type="button" onClick={next}>Next scene →</button>}
        </div>
      </div>
      <figcaption className="caption" aria-live="polite"><Rich text={slide.caption} /></figcaption>
    </figure>
  );
}

export function LeadBlock({ block }: { block: LeadData }) {
  const { doc } = useEdition();
  return (
    <section className="lead" id={block.id}>
      <div>
        <Kicker text={block.kicker} />
        <h1>{block.headline.text}<br /><em>{block.headline.accent}</em></h1>
        <p className="deck">{block.deck}</p>
        <div className="byline"><b>The paper</b> · {doc.paper.title}<i>{doc.paper.authors}, {doc.paper.year}</i></div>
      </div>
      <MotionGroup><Slideshow slideshow={block.slideshow} /></MotionGroup>
    </section>
  );
}
