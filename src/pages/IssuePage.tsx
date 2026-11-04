import { SampleTag, StoryArt } from '../components/library';
import { MediaView } from '../components/MediaView';
import { Crumbs, SitePage } from '../components/SitePage';
import type { Archive } from '../data/load';
import { byline, issueById, latestIssue, realPaper, roleLabel, storiesOf, storyById, trustLabel } from '../lib/library';
import { appHref, feedHref, issueHref, paperHref } from '../lib/routes';
import type { LibraryStory } from '../types';

const kindLabel = { paper: 'Paper', blog: 'Blog', classic: 'Classic' } as const;

function Toc({ stories }: { stories: LibraryStory[] }) {
  return (
    <ol className="is-toc">
      {stories.map((s, i) => (
        <li key={s.id}>
          <b className="is-num">{String(i + 1).padStart(2, '0')}</b>
          <span className="is-entry">
            <span className="label">{[roleLabel[s.role], kindLabel[s.kind], trustLabel(s.trust)].filter(Boolean).join(' · ')}{s.sample && ' · Sample'}</span>
            <a href={paperHref(s.id)}>{s.headline}{s.accent ? ` ${s.accent}` : ''}</a>
            <span className="is-by">{byline(s)}</span>
          </span>
          <span className="is-min">{s.minutes} min{s.note ? ` · ${s.note}` : ''}</span>
        </li>
      ))}
    </ol>
  );
}

export function IssuePage({ archive, id }: { archive: Archive; id?: string }) {
  const { library } = archive;
  const issue = issueById(library, id ?? latestIssue(library).id);
  if (!issue) throw new Error(`There is no issue called “${id}”.`);
  const idx = library.issues.indexOf(issue);
  const prev = library.issues[idx + 1];
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
      <Crumbs items={[{ href: appHref('issues'), label: 'Editions' }, `Volume ${issue.volume}`, `Issue ${issue.number}`]} />
      <section className="is-hero">
        <div className="is-cover" style={{ background: issue.color }}>
          <div className="label-ink is-cover-top"><span>The Geeky Times</span><span>Vol. {issue.volume} · {issue.volume === 'I' ? `No. ${issue.number}` : issue.number}</span></div>
          {coverPaper && <div className="is-cover-art"><MediaView media={coverPaper.cover.media} /></div>}
          <div className="is-cover-foot"><b>{issue.title}</b>{cover && <span>Cover: “{cover.headline} {cover.accent}”</span>}</div>
        </div>
        <div className="is-intro">
          <span className="label">Volume {issue.volume} · Issue {issue.number}{issue.published ? ` · Published ${issue.published}` : ''}{issue.sample && ' · Sample'}</span>
          <h1>{words.join(' ')} <em>{last}</em></h1>
          {stories.length > 0 ? (
            <>
              <div className="is-stats"><span>{stories.length} stories</span><span>{mix}</span><span>About {Math.round(total / 5) * 5} minutes</span></div>
              <div className="is-actions">
                <a className="btn-solid" href="#toc">Start with the lead →</a>
                <a className="btn-line" href={feedHref()}>Swipe this issue ▶</a>
              </div>
            </>
          ) : <p className="is-note">This special issue is a sample: it will collect {issue.classics} classic papers on one theme, explained for the first time.</p>}
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
                    <span className="label">{String(i + 1).padStart(2, '0')} · {roleLabel[s.role]}{s.sample && ' · Sample'}</span>
                    <h4>{s.headline}{s.accent ? ` ${s.accent}` : ''}</h4>
                    {s.real && <p>{s.dek.split('. ')[0]}.</p>}
                  </div>
                </a>
              ))}
            </div>
          </section>
        </>
      )}

      <nav className="is-pn" aria-label="Other issues">
        {prev ? <a className="card" href={issueHref(prev.id)}><span className="label">← Previous · Vol. {prev.volume} · {prev.number}</span><b>{prev.title}{prev.sample && ' (sample)'}</b></a> : <span />}
        <div className="card is-next"><span className="label">Next · Issue {String(Number(latestIssue(library).number) + 1).padStart(3, '0')}</span><b>Out next Friday</b><SampleTag story={{ sample: true } as LibraryStory} /></div>
      </nav>
    </SitePage>
  );
}
