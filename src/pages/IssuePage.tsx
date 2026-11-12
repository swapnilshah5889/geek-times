import { useHead } from '../components/head';
import { StoryArt } from '../components/library';
import { MediaView } from '../components/MediaView';
import { Crumbs, SitePage } from '../components/SitePage';
import { mediaBaseFor, type Archive } from '../data/load';
import { shareCardUrl } from '../lib/mediaBase';
import { byline, issueById, latestIssue, neighbours, volumeOf, realPaper, roleLabel, storiesOf, storyById, trustLabel } from '../lib/library';
import { appHref, feedHref, issueHref, paperHref } from '../lib/routes';
import type { LibraryIssue, LibraryStory } from '../types';

const numberLabel = (n: string) => (n.startsWith('Special') ? n : `No. ${n}`);
const kindLabel = { paper: 'Paper', blog: 'Blog', classic: 'Classic' } as const;

/** Page title and description, from the issue's own data (no invented copy). */
function issueHead(archive: Archive, issue: LibraryIssue) {
  const label = issue.number.startsWith('Special') ? issue.number : `Issue ${issue.number}`;
  const stories = storiesOf(archive.library, issue.stories ?? []);
  const minutes = Math.round(stories.reduce((n, s) => n + s.minutes, 0) / 5) * 5;
  const description = stories.length
    ? `${issue.title}: ${stories.length} ${stories.length === 1 ? 'story' : 'stories'}, about ${minutes} minutes, explained in plain language.`
    : `${issue.title}: no stories published yet.`;
  return { title: `${label}: ${issue.title} — ${archive.site.name}`, description };
}

function Toc({ stories }: { stories: LibraryStory[] }) {
  return (
    <ol className="is-toc">
      {stories.map((s, i) => (
        <li key={s.id}>
          <b className="is-num">{String(i + 1).padStart(2, '0')}</b>
          <span className="is-entry">
            <span className="label">{[roleLabel[s.role], kindLabel[s.kind], trustLabel(s.trust)].filter(Boolean).join(' · ')}</span>
            <a href={paperHref(s.id)}>{`${s.headline}${s.accent ? ` ${s.accent}` : ''}`}</a>
            <span className="is-by">{byline(s)}</span>
          </span>
          <span className="is-min">{`${s.minutes} min${s.note ? ` · ${s.note}` : ''}`}</span>
        </li>
      ))}
    </ol>
  );
}

export function IssuePage({ archive, id }: { archive: Archive; id?: string }) {
  const { library } = archive;
  const issue = issueById(library, id ?? latestIssue(library).id);
  const head = issue ? issueHead(archive, issue) : undefined;
  useHead({
    title: head?.title ?? archive.site.name,
    description: head?.description ?? '',
    image: shareCardUrl(mediaBaseFor(archive.site)),
    imageAlt: 'An open newspaper sends a red spark into connected symbols for life, mathematics, and space.',
    type: 'website',
  });
  if (!issue) throw new Error(`There is no issue called “${id}”.`);
  const vol = volumeOf(library, issue);
  const { prev, next } = neighbours(library, issue);
  const stories = storiesOf(library, issue.stories ?? []);
  const cover = issue.covers ? storyById(library, issue.covers) : undefined;
  const coverPaper = cover && realPaper(archive, cover);
  const kinds = (k: string) => stories.filter(s => s.kind === k).length;
  const mix = [kinds('paper') && `${kinds('paper')} papers`, kinds('blog') && `${kinds('blog')} blog`, kinds('classic') && `${kinds('classic')} classic`].filter(Boolean).join(' · ');
  const words = issue.title.split(' ');
  const last = words.pop();
  const total = stories.reduce((n, s) => n + s.minutes, 0);

  return (
    <SitePage archive={archive} title={`Issue ${issue.number}: ${issue.title}`} active="issues">
      <Crumbs items={[{ href: appHref('issues'), label: 'Editions' }, vol ? `Volume ${vol.id} · ${vol.title}` : `Volume ${issue.volume}`, issue.number.startsWith('Special') ? issue.number : `Issue ${issue.number}`]} />
      <section className="is-hero">
        <div className="is-cover" style={{ background: issue.color }}>
          <div className="label-ink is-cover-top"><span>The Geeky Times</span><span>{`Vol. ${issue.volume} · ${numberLabel(issue.number)}`}</span></div>
          {coverPaper && <div className="is-cover-art"><MediaView media={coverPaper.cover.media} /></div>}
          <div className="is-cover-foot"><b>{issue.title}</b>{cover && <span>{`Cover: “${cover.headline} ${cover.accent}”`}</span>}</div>
        </div>
        <div className="is-intro">
          <span className="label">{`Volume ${issue.volume}${vol ? ` (${vol.title})` : ''} · ${issue.number.startsWith('Special') ? issue.number : `Issue ${issue.number}`}${issue.published ? ` · Published ${issue.published}` : ''}`}</span>
          <h1>{`${words.join(' ')} `}<em>{last}</em></h1>
          {stories.length > 0 ? (
            <>
              <div className="is-stats"><span>{`${stories.length} stories`}</span><span>{mix}</span><span>{`About ${Math.round(total / 5) * 5} minutes`}</span></div>
              <div className="is-actions">
                <a className="btn-solid" href="#toc">Start with the lead →</a>
                <a className="btn-line" href={feedHref()}>Swipe all snacks ▶</a>
              </div>
            </>
          ) : <p className="is-note">No stories are published in this issue yet.</p>}
        </div>
      </section>

      {stories.length > 0 && (
        <>
          <section id="toc" aria-labelledby="toc-title" className="f-section">
            <div className="f-sechead"><h2 id="toc-title">In this issue</h2><span className="label">Lead = start here · Brief = a quick snack · Vault = a classic</span></div>
            <Toc stories={stories} />
          </section>
          <section aria-label="Stories in this issue" className="f-section">
            <div className="f-grid f-grid-3">
              {stories.map((s, i) => (
                <a key={s.id} className="card f-card" href={paperHref(s.id)}>
                  {(s.art || s.real) ? <StoryArt story={s} archive={archive} /> : <div className="is-textcard"><span className="f-company">{s.title}</span><span className="chip chip-warm">{trustLabel(s.trust)}</span></div>}
                  <div className="f-card-body">
                    <span className="label">{`${String(i + 1).padStart(2, '0')} · ${roleLabel[s.role]}`}</span>
                    <h3>{`${s.headline}${s.accent ? ` ${s.accent}` : ''}`}</h3>
                    {s.real && <p>{`${s.dek.split('. ')[0]}.`}</p>}
                  </div>
                </a>
              ))}
            </div>
          </section>
        </>
      )}

      <nav className="is-pn" aria-label="Other issues">
        {prev ? <a className="card" href={issueHref(prev.id)}><span className="label">{`← Previous · Vol. ${prev.volume} · ${numberLabel(prev.number)}`}</span><b>{prev.title}</b></a> : <span />}
        {next
          ? <a className="card is-next" href={issueHref(next.id)}><span className="label">{`Next → Vol. ${next.volume} · ${numberLabel(next.number)}`}</span><b>{next.title}</b></a>
          : <span />}
      </nav>
    </SitePage>
  );
}
