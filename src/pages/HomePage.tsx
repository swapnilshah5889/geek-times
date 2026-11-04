import { useEffect, useMemo } from 'react';
import { Masthead } from '../components/Masthead';
import { MediaView } from '../components/MediaView';
import { MotionButton, MotionGroup } from '../components/motion';
import { mediaBaseFor, type Archive } from '../data/load';
import { frontPage, type Tile } from '../lib/front';
import { MediaBaseContext } from '../lib/mediaBase';
import { searchHref, tagCounts, tagLookup } from '../lib/tags';
import type { Moment, SearchEntry, TagVocabulary } from '../types';

const today = () => new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

function CoverTile({ paper, hero }: { paper: SearchEntry; hero: boolean }) {
  const { cover } = paper;
  return (
    <a className={`tile tile-cover ${hero ? 'tile-hero' : 'tile-wide'}`} href={`?paper=${paper.slug}`}>
      <div className="tile-media"><MediaView media={cover.media} /></div>
      <div className="tile-body">
        <span className="label">{hero ? `Today’s issue · No. ${paper.issue}` : `Issue ${paper.issue}`} &nbsp;/&nbsp; {cover.kicker.split(' / ')[0]}</span>
        <h2>{cover.headline.text} {cover.headline.accent && <em>{cover.headline.accent}</em>}</h2>
        <p className="dek">{hero ? paper.summary : cover.dek}</p>
        <p className="tile-byline"><b>{paper.title}</b> · {paper.authors}, {paper.year}</p>
        <span className="cta">Read the issue →</span>
      </div>
    </a>
  );
}

function MomentTile({ moment, size }: { moment: Moment; size: Tile['size'] }) {
  const isFact = moment.kind === 'fact';
  return (
    <a className={`tile tile-moment tile-${size} moment-${moment.kind}`} href={moment.href}>
      <span className="tile-kicker label">
        {moment.kicker}
        {moment.provenance === 'evidence' && <span className="stamp stamp-evidence">Real result</span>}
      </span>
      {isFact ? (
        <>
          <b className="tile-figure">{moment.figure}</b>
          {moment.media && <div className="tile-icon"><MediaView media={moment.media} /></div>}
        </>
      ) : (
        <>
          {moment.media && <div className="tile-media"><MediaView media={moment.media} /></div>}
          <h3>{moment.title}</h3>
        </>
      )}
      <p className="tile-text">{moment.text}</p>
      <span className="cta">{isFact ? 'See the source →' : 'Read this part →'}</span>
    </a>
  );
}

function FeedTile({ count }: { count: number }) {
  return (
    <a className="tile tile-feed tile-tall" href="?feed">
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
            links={[{ href: '?feed', label: 'Swipe the snacks ▶' }]} />
          <div className="front-head">
            <span className="label">The front page &nbsp;/&nbsp; Big science, in pictures anyone can read</span>
            <MotionButton noun="animations" />
          </div>
          <section className="bento" aria-label="Front page">
            {tiles.map((tile, i) => {
              switch (tile.kind) {
                case 'cover': return <CoverTile key={`c-${tile.paper.slug}`} paper={tile.paper} hero={tile.size === 'hero'} />;
                case 'moment': return <MomentTile key={tile.moment.id + tile.paper.slug} moment={tile.moment} size={tile.size} />;
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
