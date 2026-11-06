import { useHead } from '../components/head';
import { Crumbs, SitePage } from '../components/SitePage';
import type { Archive } from '../data/load';
import { companyById, storiesOf, storyById, trustLabel } from '../lib/library';
import { appHref, companyHref, mapHref, paperHref } from '../lib/routes';

export function CompanyPage({ archive, id }: { archive: Archive; id?: string }) {
  const { library } = archive;
  const company = companyById(library, id ?? library.companies[0]?.id);
  useHead({
    title: company ? `${company.name}: ${company.sector} — ${archive.site.name}` : archive.site.name,
    description: company?.blurb ?? '',
    type: 'website',
  });
  if (!company) throw new Error(`There is no company called “${id}”.`);
  const posts = storiesOf(library, company.posts);
  const base = library.nodes.filter(n => company.builtOn.includes(n.id));
  const words = company.name.split(' ');
  // Only placeholder companies (sample: true) show sample wording and [year] placeholders.
  const sample = company.sample === true;

  return (
    <SitePage archive={archive} title={`${company.name}: ${company.sector}`} active="real">
      <Crumbs items={[{ href: appHref('companies'), label: 'In the real world' }, { href: appHref('companies'), label: 'Companies' }, company.name]} />
      <section className="co-hero">
        <div>
          <span className="label">{`Company · ${company.sector}${sample ? ' · Sample page' : ''}`}</span>
          <h1>{`${words[0]} ${words.slice(1).join(' ')}`}</h1>
          <p className="f-lead-dek">{company.blurb}</p>
        </div>
        <div className="co-stats">
          <div><b>{posts.length}</b><span>stories explained</span></div>
          <div><b>{company.postsFollowed}</b><span>posts followed</span></div>
          <div><b>{base.length}</b><span>papers it builds on</span></div>
        </div>
      </section>
      <p className="co-howto"><b className="label">How to read this page</b>{`   Claims here come from ${company.name}’s own writeup; each one is labelled with what kind of claim it is. We link every original post and use plain names, never logos.`}</p>

      <section aria-labelledby="explained" className="f-section">
        <div className="f-sechead"><h2 id="explained">Explained posts</h2><span className="label">{`Newest first${sample ? ' · Sample' : ''}`}</span></div>
        <div className="f-grid f-grid-3">
          {posts.map(s => {
            const on = s.builtOn ? storyById(library, s.builtOn) : undefined;
            return (
              <a key={s.id} className="card f-post" href={paperHref(s.id)}>
                <span className="label">{sample ? 'Blog · [year] · Sample' : `Engineering blog · ${s.year}`}</span>
                <h4>{s.headline}</h4>
                <p>{s.dek}</p>
                <span className="f-chips">
                  <span className="chip chip-warm">{trustLabel(s.trust)}</span>
                  {on && <span className="chip chip-green">{`Puts into practice: ${on.title}`}</span>}
                </span>
              </a>
            );
          })}
        </div>
      </section>

      <section className="co-lower f-section">
        <div className="co-graph">
          <span className="label">From the graph</span>
          <h2>Research these posts put into practice</h2>
          <div className="co-chips">
            {base.map(n => n.story
              ? <a key={n.id} className="co-chip" href={paperHref(n.story)}>{`${n.title} · ${n.year}`}</a>
              : <a key={n.id} className="co-chip is-open" href={mapHref(n.id)}>{`${n.title} · ${n.year} · not explained yet`}</a>)}
          </div>
          <a className="f-more" href={mapHref(base[0]?.id)}>See this company on the map →</a>
        </div>
        <div className="card co-next">
          <span className="label">Coming up</span>
          <h2>Posts we’re explaining next</h2>
          {company.coming.map((c, i) => <p key={i}>{c}</p>)}
          <span className="co-foot">Found automatically from the company’s public RSS feed.</span>
        </div>
      </section>

      {library.companies.length > 1 && (
        <section className="f-section">
          <div className="f-sechead"><h3>More companies</h3></div>
          <div className="f-chips">
            {library.companies.filter(c => c.id !== company.id).map(c => <a key={c.id} className="co-chip" href={companyHref(c.id)}>{`${c.name} · ${c.sector}`}</a>)}
          </div>
        </section>
      )}
    </SitePage>
  );
}
