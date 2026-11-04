import { useEffect, useMemo } from 'react';
import { Masthead } from '../components/Masthead';
import { MediaView } from '../components/MediaView';
import { MotionButton, MotionGroup } from '../components/motion';
import { useMotion } from '../lib/motion';
import { mediaBaseFor, type Archive } from '../data/load';
import { frontPage } from '../lib/front';
import { MediaBaseContext } from '../lib/mediaBase';
import { feedHref, paperHref } from '../lib/routes';
import { searchHref, tagCounts, tagLookup } from '../lib/tags';
import type { SearchEntry, TagVocabulary } from '../types';

const today = () => new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

/** The cover art: flips between frames with a shout on each, so the tile moves before anyone reads it. */
function CoverArt({ cover }: { cover: SearchEntry['cover'] }) {
  const { held } = useMotion();
  const frames = cover.hook?.frames;
  if (!frames) return <div className="tile-media"><MediaView media={cover.media} /></div>;
  return (
    <div className={`tile-media cover-flip${held ? ' cover-held' : ''}`}>
      {frames.map((f, i) => (
        <div key={f.tag} className="cover-frame" style={{ animationDelay: `${i * 2.4}s` }} aria-hidden={i > 0}>
          <MediaView media={f.media} />
          <span className="cover-shout" style={{ animationDelay: `${i * 2.4}s` }}>{f.tag}</span>
        </div>
      ))}
    </div>
  );
}

function CoverTile({ paper, hero }: { paper: SearchEntry; hero: boolean }) {
  const { cover } = paper;
  const { hook } = cover;
  return (
    <a className={`tile tile-cover ${hero ? 'tile-hero' : 'tile-wide'}${hook ? ' tile-hooked' : ''}`} href={paperHref(paper.slug)}>
      <span className="label cover-kicker">
        <span className="cover-new">{hero ? 'New today' : `Issue ${paper.issue}`}</span>
        {hook && <span>{hook.readMinutes} min · {paper.moments.length} snacks</span>}
      </span>
      <div className="cover-stage">
        <CoverArt cover={cover} />
        {hook && <span className="cover-sticker" aria-hidden="true">{hook.sticker}</span>}
        {hook?.stat && (
          <span className="cover-stat">
            <b>{hook.stat.figure}</b>
            <small>{hook.stat.text}</small>
          </span>
        )}
      </div>
      <div className="tile-body">
        <h2>{cover.headline.text} {cover.headline.accent && <em>{cover.headline.accent}</em>}</h2>
        <p className="dek">{hook ? <mark>{hook.teaser}</mark> : hero ? paper.summary : cover.dek}</p>
        <p className="tile-byline"><b>{paper.title}</b> · {paper.authors}, {paper.year}</p>
        <span className="cover-cta">{hook?.cta ?? 'Read the issue'} <i aria-hidden="true">→</i></span>
      </div>
    </a>
  );
}

function FeedTile({ count }: { count: number }) {
  return (
    <a className="tile tile-feed tile-tall" href={feedHref()}>
      <span className="label">New &nbsp;/&nbsp; Snack mode</span>
      <div className="feed-stack" aria-hidden="true"><span /><span /><span /></div>
      <h3>Swipe the snacks</h3>
      <p>{count} bite-size pictures from the research, one swipe at a time.</p>
      <span className="cta">Start swiping ↓</span>
    </a>
  );
}

function TopicsTile({ archive }: { archive: { vocab: TagVocabulary; index: Archive['index'] } }) {
  const topics = useMemo(() => {
    const lookup = tagLookup(archive.vocab);
    const counts = tagCounts(archive.index, lookup);
    return archive.vocab.tags.filter(t => ['everyday', 'area', 'use'].includes(t.facet) && counts.has(t.id)).slice(0, 12);
  }, [archive]);
  return (
    <div className="tile tile-topics tile-wide">
      <span className="label">Explore by topic</span>
      <h3>What are you curious about?</h3>
      <p className="topic-chips">
        {topics.map(t => <a key={t.id} className="tag" href={searchHref({ tags: [t.id] })}>{t.label}</a>)}
      </p>
      <a className="cta" href={searchHref()}>Search everything →</a>
    </div>
  );
}

export function HomePage({ archive }: { archive: Archive }) {
  const { site, index } = archive;
  const tiles = useMemo(() => frontPage(index), [index]);
  useEffect(() => { document.title = `${site.name} — ${site.motto}`; }, [site]);
  const featured = index.papers.find(p => p.slug === index.featured);

  return (
    <MediaBaseContext.Provider value={mediaBaseFor(site)}>
      <MotionGroup>
        <main>
          <Masthead site={site} meta={[today(), featured ? `Issue ${featured.issue}` : '']}
            links={[{ href: feedHref(), label: 'Swipe the snacks ▶' }]} />
          <div className="front-head">
            <span className="label">The front page &nbsp;/&nbsp; Big science, in pictures anyone can read</span>
            <MotionButton noun="animations" />
          </div>
          <section className="bento" aria-label="Front page">
            {tiles.map((tile, i) => {
              switch (tile.kind) {
                case 'cover': return <CoverTile key={`c-${tile.paper.slug}`} paper={tile.paper} hero={tile.size === 'hero'} />;
                case 'feed': return <FeedTile key="feed" count={tile.count} />;
                case 'topics': return <TopicsTile key={`t-${i}`} archive={archive} />;
              }
            })}
          </section>
          <footer>
            <span>{site.name} &nbsp; ✦ &nbsp; {site.motto}</span>
            <a href={searchHref()}>The archive →</a>
          </footer>
        </main>
      </MotionGroup>
    </MediaBaseContext.Provider>
  );
}
