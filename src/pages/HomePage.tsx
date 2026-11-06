import { useMemo, useState, type FormEvent } from 'react';
import { useHead } from '../components/head';
import { Masthead } from '../components/Masthead';
import { MediaView } from '../components/MediaView';
import { ClaimStamp, Stamp } from '../components/common';
import { sourceKindOf } from '../lib/claimLabel';
import { MotionButton, MotionGroup } from '../components/motion';
import { SampleTag, StoryArt } from '../components/library';
import { mediaBaseFor, type Archive } from '../data/load';
import { headlineOf, latestIssue, realPaper, roleLabel, storiesOf, storyById, trustLabel } from '../lib/library';
import { MediaBaseContext } from '../lib/mediaBase';
import { appHref, feedHref, issueHref, paperHref } from '../lib/routes';
import { searchHref } from '../lib/tags';
import { useTodayLabel } from '../lib/format';
import type { LibraryIssue, LibraryStory, Moment, SearchEntry } from '../types';

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

/** The weekly edition: a small hand-assembled extra, never the focus (decision 32). */
function useEdition(archive: Archive) {
  const issue = latestIssue(archive.library);
  const stories = storiesOf(archive.library, issue.stories ?? []);
  const minutes = Math.round(stories.reduce((n, s) => n + s.minutes, 0) / 5) * 5;
  return { issue, count: stories.length, minutes };
}

function EditionCover({ issue }: { issue: LibraryIssue }) {
  return (
    <span className="ed-cover" style={{ background: issue.color }} aria-hidden="true">
      <span>{`No. ${issue.number}`}</span><b>{issue.title}</b>
    </span>
  );
}

function EditionCard({ archive }: { archive: Archive }) {
  const { issue } = useEdition(archive);
  return (
    <a className="card ed-card" href={issueHref(issue.id)}>
      <EditionCover issue={issue} />
      <span className="ed-text">
        <span className="label">This week’s edition</span>
        <span>Our hand-picked stories for the week.</span>
        <span className="label">Read the edition →</span>
      </span>
    </a>
  );
}

function EditionBand({ archive }: { archive: Archive }) {
  const { issue, count, minutes } = useEdition(archive);
  return (
    <section aria-label="This week’s edition" className="card ed-band">
      <EditionCover issue={issue} />
      <div className="ed-text">
        <span className="label">This week’s edition · hand-picked</span>
        <b>{issue.title}</b>
        <span>{`${count} ${count === 1 ? 'story' : 'stories'} · about ${minutes} minutes`}</span>
      </div>
      <div className="ed-links">
        <a className="f-more" href={issueHref(issue.id)}>Read the edition →</a>
        <a className="label" href={appHref('issues')}>Past editions</a>
      </div>
    </section>
  );
}

function Lead({ archive }: { archive: Archive }) {
  const { library } = archive;
  const lead = storyById(library, library.front.lead);
  const paper = lead && realPaper(archive, lead);
  const aside = storiesOf(library, library.front.aside);
  if (!lead || !paper) return null;
  return (
    <section id="lead" className="f-lead" aria-label="Top stories">
      <article className="f-lead-main">
        <div className="label">{`Lead story · ${lead.desk}`}</div>
        <a className="f-lead-art" href={paperHref(lead.id)} aria-label={`Open the story: ${paper.cover.headline.text} ${paper.cover.headline.accent ?? ''}`}>
          <MediaView media={paper.cover.media} />
        </a>
        <h2><a href={paperHref(lead.id)}>{`${paper.cover.headline.text} `}<em>{paper.cover.headline.accent}</em></a></h2>
        <p className="f-lead-dek">{paper.summary}</p>
        <div className="f-lead-foot">
          <p><b>{paper.title}</b>{' · '}<i>{`${paper.authors}, ${paper.year}`}</i>{' · '}<span className="f-trust" title={lead.trust === 'peer_reviewed' ? 'Checked by other scientists before it was published' : undefined}>{trustLabel(lead.trust)}</span>{lead.trust === 'peer_reviewed' && <small>{' (checked by other scientists)'}</small>}{lead.trust === 'preprint' && <small>{' (shared publicly, not yet checked by other scientists)'}</small>}</p>
          <a className="f-more" href={paperHref(lead.id)}>Read the illustrated story →</a>
        </div>
      </article>
      <aside className="f-aside">
        {aside.map((s, i) => (
          <article key={s.id} className={i === 0 ? 'f-aside-first' : undefined}>
            {i === 0 && <a href={paperHref(s.id)} className="f-aside-art"><StoryArt story={s} archive={archive} /></a>}
            <div className="f-tags label"><span>{`${roleLabel[s.role]} · ${s.desk}`}</span><SampleTag story={s} /></div>
            <h3><a href={paperHref(s.id)}>{s.headline}</a></h3>
            <p>{s.dek}</p>
          </article>
        ))}
        <EditionCard archive={archive} />
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

function MoreStories({ archive }: { archive: Archive }) {
  const { library } = archive;
  const stories = storiesOf(library, library.front.more);
  return (
    <section aria-labelledby="s-more" className="f-section">
      <SectionHead id="s-more" title="More top stories" />
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
          <a key={m.href} className="f-snack" href={appHref(m.href)}>
            <MediaView media={m.media!} />
            <span><Stamp kind={m.provenance} trust={m.trust} source={sourceKindOf(archive.library, m.paper)} /><b>{m.title}</b><br />{m.text}</span>
          </a>
        ))}
        {fact && (
          <a className="f-snack f-snack-fact" href={appHref(fact.href)}>
            <ClaimStamp claim={fact.claim} trust={fact.trust} source={sourceKindOf(archive.library, fact.paper)} />
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
      <SectionHead id="s-real" title="In the real world" hint="From company engineering blogs. Claims come from the company’s own post, each labelled with what kind of claim it is. “Company-reported” means no outside group checked them."
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
      <SectionHead id="s-numbers" title="Numbers from the stories" />
      <div className="f-grid f-grid-4">
        {picks.map(({ paper, m }) => (
          <a key={paper.slug + m.id} className="f-number" href={appHref(m.href)}>
            <span className="label">
              {`${paper.title} · `}<ClaimStamp claim={m.claim} trust={m.trust} source={sourceKindOf(library, paper.slug)} />{` · ${sectionOf(m)}`}
            </span>
            <b>{m.figure}</b>
            <span className="f-number-text">{m.text}</span>
          </a>
        ))}
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

function Newsletter() {
  const [sent, setSent] = useState(false);
  const submit = (e: FormEvent) => { e.preventDefault(); setSent(true); };
  return (
    <section aria-labelledby="s-news" className="f-news">
      <div><span className="label">Every Friday</span><h3 id="s-news">Get the weekly edition</h3><p>Big science, in pictures, in your inbox once a week.</p></div>
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
  const today = useTodayLabel();
  const { site } = archive;
  // The home page keeps the site's own title (it is the generic one by design); the description says what the site is.
  useHead({
    title: `${site.name} — ${site.motto}`,
    description: `${site.tagline}. Research papers and engineering posts, explained for anyone.`,
    type: 'website',
  });
  const mediaBase = useMemo(() => mediaBaseFor(site), [site]);

  return (
    <MediaBaseContext.Provider value={mediaBase}>
      <MotionGroup>
        <main className="site-main">
          <Masthead site={site} meta={[today, '']} edition active="front" />
          <div className="f-motion"><MotionButton noun="animations" /></div>
          <Lead archive={archive} />
          <div className="f-explore-head">
            <h2>Keep exploring</h2>
            <span className="label">Sample stories are marked</span>
          </div>
          <MoreStories archive={archive} />
          <Snacks archive={archive} />
          <Topics archive={archive} />
          <RealWorld archive={archive} />
          <Numbers archive={archive} />
          <Storylines archive={archive} />
          <Vault archive={archive} />
          <EditionBand archive={archive} />
          <Newsletter />
          <footer>
            <span>{`${site.name}   ✦   ${site.motto}`}</span>
            <span className="foot-links"><a href={appHref('issues')}>Editions</a><a href={appHref('issues')}>Past editions</a><a href={searchHref()}>The archive →</a></span>
          </footer>
        </main>
      </MotionGroup>
    </MediaBaseContext.Provider>
  );
}
