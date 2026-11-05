import { useEffect, useMemo, useRef, useState } from 'react';
import { MediaView } from '../components/MediaView';
import { MotionGroup } from '../components/motion';
import { Stamp } from '../components/common';
import { appUrl, mediaBaseFor, type Archive } from '../data/load';
import { feedItems } from '../lib/feed';
import { storyById } from '../lib/library';
import { MediaBaseContext } from '../lib/mediaBase';
import { appHref, homeHref, paperHref } from '../lib/routes';
import { searchHref } from '../lib/tags';

// Snack mode: one full-screen card per swipe, like a short-video feed, but each card is a piece of research.

function ShareButton({ title, href }: { title: string; href: string }) {
  const [copied, setCopied] = useState(false);
  async function share() {
    const url = appUrl(href);
    try {
      if (navigator.share) await navigator.share({ title, url });
      else {
        await navigator.clipboard.writeText(url);
        setCopied(true);
        window.setTimeout(() => setCopied(false), 1800);
      }
    } catch { /* the reader closed the share sheet */ }
  }
  return <button type="button" className="feed-btn" onClick={share}>{copied ? 'Link copied ✓' : 'Share ↗'}</button>;
}

export function FeedPage({ archive }: { archive: Archive }) {
  const { site, index, library } = archive;
  const items = useMemo(() => feedItems(index), [index]);
  const [current, setCurrent] = useState(0);
  const scroller = useRef<HTMLDivElement>(null);

  useEffect(() => { document.title = `${site.name} — Snacks`; }, [site]);

  // Track which card fills the screen, for the counter.
  useEffect(() => {
    const cards = scroller.current?.querySelectorAll<HTMLElement>('.feed-card');
    if (!cards) return;
    const io = new IntersectionObserver(entries => {
      for (const e of entries) if (e.isIntersecting) setCurrent(Number((e.target as HTMLElement).dataset.index));
    }, { root: scroller.current, threshold: 0.6 });
    cards.forEach(c => io.observe(c));
    return () => io.disconnect();
  }, [items]);

  return (
    <MediaBaseContext.Provider value={mediaBaseFor(site)}>
      <MotionGroup>
        <div className="feed">
          <header className="feed-bar">
            <a href={homeHref()} className="feed-brand">{site.name}</a>
            <span className="feed-count">{Math.min(current + 1, items.length)} / {items.length}</span>
            <a href={homeHref()} className="feed-close" aria-label="Back to the front page">✕</a>
          </header>
          <div className="feed-scroller" ref={scroller} tabIndex={0} aria-label="Snack feed: scroll or swipe for the next card">
            {items.map((item, i) => {
              const { paper } = item;
              if (item.kind === 'cover') {
                return (
                  <article className="feed-card feed-cover" key={`c-${paper.slug}`} data-index={i}>
                    <span className="label">{paper.desk} &nbsp;/&nbsp; {paper.title}</span>
                    <div className="feed-media"><MediaView media={paper.cover.media} /></div>
                    <h2>{paper.cover.headline.text} <em>{paper.cover.headline.accent}</em></h2>
                    <p>{paper.summary}</p>
                    <div className="feed-actions">
                      <a className="feed-btn feed-btn-main" href={paperHref(paper.slug)}>Read the story →</a>
                      <ShareButton title={paper.pageTitle} href={paperHref(paper.slug)} />
                    </div>
                    {i === 0 && <p className="feed-hint" aria-hidden="true">Swipe up ↑</p>}
                  </article>
                );
              }
              const { moment } = item;
              return (
                <article className={`feed-card moment-${moment.kind}`} key={moment.id + paper.slug} data-index={i}>
                  <span className="label">
                    {moment.kicker} &nbsp;/&nbsp; {paper.cover.headline.text} {paper.cover.headline.accent}
                    {moment.provenance && <Stamp kind={moment.provenance} trust={storyById(library, paper.slug)?.trust} />}
                  </span>
                  {moment.kind === 'fact' ? (
                    <div className="feed-fact"><b>{moment.figure}</b>{moment.media && <MediaView media={moment.media} />}</div>
                  ) : (
                    moment.media && <div className="feed-media"><MediaView media={moment.media} /></div>
                  )}
                  {moment.kind !== 'fact' && <h2>{moment.title}</h2>}
                  <p>{moment.text}</p>
                  <div className="feed-actions">
                    <a className="feed-btn feed-btn-main" href={appHref(moment.href)}>{moment.kind === 'fact' ? 'See the source →' : 'Read it in the story →'}</a>
                    <ShareButton title={`${moment.title} · ${site.name}`} href={appHref(moment.href)} />
                  </div>
                </article>
              );
            })}
            <article className="feed-card feed-end" data-index={items.length}>
              <h2>You’re all caught up</h2>
              <p>New stories are on the way. Until then, dig into the archive.</p>
              <div className="feed-actions">
                <a className="feed-btn feed-btn-main" href={homeHref()}>Front page</a>
                <a className="feed-btn" href={searchHref()}>Search</a>
              </div>
            </article>
          </div>
        </div>
      </MotionGroup>
    </MediaBaseContext.Provider>
  );
}
