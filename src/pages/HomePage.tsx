import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { Masthead } from '../components/Masthead';
import { MediaView } from '../components/MediaView';
import { MotionButton, MotionGroup } from '../components/motion';
import { SampleTag, StoryArt } from '../components/library';
import { mediaBaseFor, type Archive } from '../data/load';
import { headlineOf, issueById, issuesWith, latestIssue, realPaper, roleLabel, storiesOf, storyById, trustLabel } from '../lib/library';
import { MediaBaseContext } from '../lib/mediaBase';
import { appHref, feedHref, issueHref, paperHref } from '../lib/routes';
import { searchHref } from '../lib/tags';
import type { LibraryStory, Moment, SearchEntry } from '../types';

const today = () => new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

const CLAIM_LABEL = { model_design: 'model design', measured_result: 'measured result', illustration: 'illustration' } as const;
const sectionOf = (m: Moment) => m.sourceLabel?.replace(/^Paper\s*/, '');

function SectionHead({ id, title, hint, link }: { id: string; title: string; hint?: string; link?: { href: string; label: string } }) {
  return (
    <div className="f-sechead">
      <div className="f-sechead-row">
        <h3 id={id}>{title}</h3>
        {link && <a className="f-more" href={link.href}>{link.label}</a>}
      </div>
      {hint && <p className="f-hint">{hint}</p>}
    </div>
  );
}

function Lead({ archive }: { archive: Archive }) {
  const { library } = archive;
  const lead = storyById(library, library.front.lead);
  const paper = lead && realPaper(archive, lead);
  const aside = storiesOf(library, library.front.aside);
  // The front page is the current issue, so it may say which issue the lead belongs to. Story pages never do.
  const leadIssue = lead && issuesWith(library, lead.id)[0];
  if (!lead || !paper) return null;
  return (
    <section id="lead" className="f-lead" aria-label="Top stories">
      <article className="f-lead-main">
        <div className="label">{leadIssue ? `Issue ${leadIssue.number} · ` : ''}Lead story · {lead.desk}</div>
        <a className="f-lead-art" href={paperHref(lead.id)} aria-label={`Open the story: ${paper.cover.headline.text} ${paper.cover.headline.accent ?? ''}`}>
          <MediaView media={paper.cover.media} />
        </a>
        <h2><a href={paperHref(lead.id)}>{paper.cover.headline.text} <em>{paper.cover.headline.accent}</em></a></h2>
        <p className="f-lead-dek">{paper.summary}</p>
        <div className="f-lead-foot">
          <p><b>{paper.title}</b> · <i>{paper.authors}, {paper.year}</i> · <span className="f-trust" title={lead.trust === 'peer_reviewed' ? 'Checked by other scientists before it was published' : undefined}>{trustLabel(lead.trust)}</span>{' '}
            {lead.trust === 'peer_reviewed' && <small>(checked by other scientists)</small>}{lead.trust === 'preprint' && <small>(shared publicly, not yet checked by other scientists)</small>}</p>
          <a className="f-more" href={paperHref(lead.id)}>Read the illustrated story →</a>
        </div>
      </article>
      <aside className="f-aside">
        {aside.map((s, i) => (
          <article key={s.id} className={i === 0 ? 'f-aside-first' : undefined}>
            {i === 0 && <a href={paperHref(s.id)} className="f-aside-art"><StoryArt story={s} archive={archive} /></a>}
            <div className="f-tags label"><span>{roleLabel[s.role]} · {s.desk}</span><SampleTag story={s} /></div>
            <h3><a href={paperHref(s.id)}>{s.headline}</a></h3>
            <p>{s.dek}</p>
          </article>
        ))}
      </aside>
    </section>
  );
}

function StoryCard({ story, archive, kicker }: { story: LibraryStory; archive: Archive; kicker?: string }) {
  return (
    <a className="card f-card" href={paperHref(story.id)}>
      <StoryArt story={story} archive={archive} />
      <div className="f-card-body">
        <span className="label">{kicker ?? `${roleLabel[story.role]} · ${story.desk}`}{story.sample && ' · Sample'}</span>
        <h4>{headlineOf(story)}</h4>
        <p>{story.dek}</p>
      </div>
    </a>
  );
}

function MoreFromIssue({ archive }: { archive: Archive }) {
  const { library } = archive;
  const issue = issueById(library, library.front.moreIssue ?? latestIssue(library).id) ?? latestIssue(library);
  const stories = storiesOf(library, library.front.more);
  return (
    <section aria-labelledby="s-more" className="f-section">
      <SectionHead id="s-more" title={`More from Issue ${issue.number}`} link={{ href: issueHref(issue.id), label: 'Whole issue →' }} />
      <div className="f-grid f-grid-3">{stories.map(s => <StoryCard key={s.id} story={s} archive={archive} />)}</div>
    </section>
  );
}

function Snacks({ archive }: { archive: Archive }) {
  // Snacks mix every paper: comic panels and numbers in turn, then one story card.
  const all = archive.index.papers.flatMap(p => p.moments);
  const perPaper = archive.index.papers.map(p => p.moments.filter(m => m.kind === 'strip' && m.media));
  const strips = [...perPaper.map(q => q[0]), ...perPaper.map(q => q[1])].filter(Boolean).slice(0, 2);
  const fact = all.find(m => m.kind === 'fact' && m.claim === 'model_design') ?? all.find(m => m.kind === 'fact');
  const sample = archive.library.stories.find(s => s.art);
  const count = archive.index.papers.reduce((n, p) => n + p.moments.length, 0);
  return (
    <section id="snacks" aria-labelledby="s-snacks" className="f-snacks">
      <div className="f-snacks-intro">
        <span className="label">Snack mode · {count} snacks</span>
        <h3 id="s-snacks">Swipe the snacks</h3>
        <p>One picture, one idea, one swipe. Each card opens the full story.</p>
        <a className="f-pill" href={feedHref()}>Start swiping ▶</a>
      </div>
      <div className="f-snack-row">
        {strips.map(m => (
          <a key={m.id} className="f-snack" href={appHref(m.href)}>
            <MediaView media={m.media!} />
            <span><span className="label">{m.provenance === 'model_design' ? 'From the paper · model design' : 'Illustration · numbers invented'}</span><b>{m.title}</b><br />{m.text}</span>
          </a>
        ))}
        {fact && (
          <a className="f-snack f-snack-fact" href={appHref(fact.href)}>
            <span className="label">From the paper · {CLAIM_LABEL[fact.claim ?? 'model_design']}</span>
            <b className="f-figure">{fact.figure}</b>
            <span>{fact.text}</span>
          </a>
        )}
        {sample && (
          <a className="f-snack" href={paperHref(sample.id)}>
            <StoryArt story={sample} archive={archive} />
            <span><span className="label">Sample snack</span><b>{sample.headline}</b></span>
          </a>
        )}
      </div>
    </section>
  );
}

function Topics({ archive }: { archive: Archive }) {
  const { library } = archive;
  return (
    <section id="topics" aria-label="Topics" className="f-section">
      {library.front.topics.map(row => {
        const shown = storiesOf(library, row.stories);
        const more = library.stories.filter(s => s.fields.includes(row.field) && !row.stories.includes(s.id)).length;
        return (
          <div key={row.field} className="f-topic-row">
            <SectionHead id={`t-${row.field}`} title={row.label} link={{ href: searchHref(), label: 'See all →' }} />
            <div className="f-grid f-grid-4">
              {shown.map(s => (
                <a key={s.id} className="card f-mini" href={paperHref(s.id)}>
                  <StoryArt story={s} archive={archive} />
                  <span>{headlineOf(s)}{s.sample && <small className="sample-tag">Sample</small>}</span>
                </a>
              ))}
              <a className="f-mini f-mini-more" href={searchHref()}>
                <b>{more > 0 ? `+${more}` : '→'}</b>
                <span>{more > 0 ? 'more stories' : 'Browse this topic'}</span>
                <span className="label">See all →</span>
              </a>
            </div>
          </div>
        );
      })}
    </section>
  );
}

function RealWorld({ archive }: { archive: Archive }) {
  const { library } = archive;
  const posts = storiesOf(library, library.front.real);
  return (
    <section id="real" aria-labelledby="s-real" className="f-section">
      <SectionHead id="s-real" title="In the real world" hint="From company engineering blogs. “Company-reported” means the company measured it itself."
        link={{ href: appHref('companies'), label: 'All companies →' }} />
      <div className="f-grid f-grid-3">
        {posts.map(s => {
          const builtOn = s.builtOn ? storyById(library, s.builtOn) : undefined;
          return (
            <a key={s.id} className="card f-post" href={paperHref(s.id)}>
              <span className="f-company">{s.title}</span>
              <h4>{headlineOf(s)}</h4>
              <p>{s.dek}</p>
              <span className="f-chips">
                <span className="chip chip-warm">{trustLabel(s.trust)}</span>
                {builtOn && <span className="chip chip-green">Puts into practice: {builtOn.title}</span>}
              </span>
            </a>
          );
        })}
      </div>
    </section>
  );
}

function Numbers({ archive }: { archive: Archive }) {
  const { library, index } = archive;
  // One number at a time from each paper in turn, so the row can mix papers as the library grows.
  const queues = index.papers.map(p => ({ paper: p, facts: p.moments.filter(m => m.kind === 'fact' && m.claim && m.figure && m.figure.length < 9) }));
  const picks: { paper: SearchEntry; m: Moment }[] = [];
  for (let i = 0; picks.length < 4 && queues.some(q => q.facts[i]); i++) {
    for (const q of queues) if (q.facts[i] && picks.length < 4) picks.push({ paper: q.paper, m: q.facts[i] });
  }
  if (!picks.length) return null;
  return (
    <section aria-labelledby="s-numbers" className="f-section">
      <SectionHead id="s-numbers" title="Numbers from the papers" />
      <div className="f-grid f-grid-4">
        {picks.map(({ paper, m }) => {
          const trust = trustLabel(storyById(library, paper.slug)?.trust).split(' ')[0].toLowerCase();
          return (
            <a key={paper.slug + m.id} className="f-number" href={appHref(m.href)}>
              <span className="label">
                {paper.title} · {m.claim === 'measured_result' ? `measured result${trust ? ` · ${trust}` : ''}` : CLAIM_LABEL[m.claim!]} · {sectionOf(m)}
              </span>
              <b>{m.figure}</b>
              <span className="f-number-text">{m.text}</span>
            </a>
          );
        })}
      </div>
    </section>
  );
}

function Storylines({ archive }: { archive: Archive }) {
  const { library } = archive;
  const lines = library.front.storylines.map(id => library.storylines.find(s => s.id === id)).filter(Boolean) as typeof library.storylines;
  return (
    <section aria-labelledby="s-lines" className="f-section">
      <SectionHead id="s-lines" title="Storylines" hint="Guided paths showing how an idea grew, step by step." />
      <div className="f-grid f-grid-2">
        {lines.map(l => (
          <a key={l.id} className="card f-line" href={appHref('map')}>
            <span className="label">Storyline · {l.sample ? 'Sample' : `${l.steps.length} steps`}</span>
            <h4>{l.title}</h4>
            <ol className="f-steps" style={{ gridTemplateColumns: `repeat(${l.steps.length}, minmax(0, 1fr))` }}>
              {l.steps.map(st => <li key={st.year + st.label} className={st.current ? 'is-now' : undefined}><b>{st.year}</b>{st.label}</li>)}
            </ol>
          </a>
        ))}
      </div>
    </section>
  );
}

function Vault({ archive }: { archive: Archive }) {
  const { library } = archive;
  const vault = storyById(library, library.front.vault);
  const day = library.front.onThisDay;
  return (
    <section aria-labelledby="s-vault" className="f-vault">
      {vault && (
        <a className="card f-vault-main" href={paperHref(vault.id)}>
          <StoryArt story={vault} archive={archive} />
          <div className="f-vault-body">
            <span className="label">From the vault{vault.sample && ' · Sample'}</span>
            <h3 id="s-vault">{vault.headline}</h3>
            <p>{vault.vaultNote ?? vault.dek}</p>
            <span className="f-more">Read the classic →</span>
          </div>
        </a>
      )}
      <div className="card f-day">
        <span className="label">On this day · Sample</span>
        <b>{day.year}</b>
        <p>{day.text}</p>
        <a className="f-more" href={paperHref(day.story)}>Open its family tree →</a>
      </div>
    </section>
  );
}

function BackIssues({ archive }: { archive: Archive }) {
  const { library } = archive;
  const current = latestIssue(library);
  return (
    <section id="issues" aria-labelledby="s-issues" className="f-section">
      <SectionHead id="s-issues" title="Back issues" link={{ href: appHref('issues'), label: 'All volumes →' }} />
      <div className="f-grid f-grid-5">
        {library.issues.map(i => (
          <a key={i.id} className="f-cover" style={{ background: i.color }} href={issueHref(i.id)}>
            <span className="label-ink">Vol. {i.volume} · {i.volume === 'I' ? `No. ${i.number}` : i.number}</span>
            <b>{i.title}</b>
            <span>{i.sample ? `Sample · ${i.classics} classics` : `${i.stories?.length} stories · this week`}</span>
          </a>
        ))}
        <a className="f-cover f-cover-all" href={issueHref(current.id)}>
          <b>Every issue</b><span className="label">Browse volumes →</span>
        </a>
      </div>
    </section>
  );
}

function Newsletter() {
  const [sent, setSent] = useState(false);
  const submit = (e: FormEvent) => { e.preventDefault(); setSent(true); };
  return (
    <section aria-labelledby="s-news" className="f-news">
      <div><span className="label">Every Friday</span><h3 id="s-news">Get each new issue</h3><p>Big science, in pictures, in your inbox once a week.</p></div>
      <form onSubmit={submit}>
        <label htmlFor="news-email" className="sr-only">Email address</label>
        <input id="news-email" type="email" placeholder="you@example.com" required disabled={sent} />
        <button type="submit" disabled={sent}>Notify me</button>
        <p role="status" className="f-news-note">{sent ? 'The newsletter is not live yet, so nothing was saved. Thanks for the interest!' : 'Sign-ups open soon.'}</p>
      </form>
    </section>
  );
}

export function HomePage({ archive }: { archive: Archive }) {
  const { site, library } = archive;
  const issue = latestIssue(library);
  useEffect(() => { document.title = `${site.name} — ${site.motto}`; }, [site]);
  const mediaBase = useMemo(() => mediaBaseFor(site), [site]);

  return (
    <MediaBaseContext.Provider value={mediaBase}>
      <MotionGroup>
        <main className="site-main">
          <Masthead site={site} meta={[today(), issue ? `Vol. ${issue.volume} · No. ${issue.number}` : '']} active="front" />
          <div className="f-motion"><MotionButton noun="animations" /></div>
          <Lead archive={archive} />
          <div className="f-explore-head">
            <h2>Keep exploring</h2>
            <span className="label">Sample stories are marked</span>
          </div>
          <MoreFromIssue archive={archive} />
          <Snacks archive={archive} />
          <Topics archive={archive} />
          <RealWorld archive={archive} />
          <Numbers archive={archive} />
          <Storylines archive={archive} />
          <Vault archive={archive} />
          <BackIssues archive={archive} />
          <Newsletter />
          <footer>
            <span>{site.name} &nbsp; ✦ &nbsp; Vol. {issue?.volume} · Issue {issue?.number}</span>
            <a href={searchHref()}>The archive →</a>
          </footer>
        </main>
      </MotionGroup>
    </MediaBaseContext.Provider>
  );
}
