import { useEffect, useMemo, useState } from 'react';
import { Masthead } from '../components/Masthead';
import type { Archive } from '../data/load';
import { homeHref, paperHref } from '../lib/routes';
import { searchHref, searchPapers, tagCounts, tagLookup } from '../lib/tags';
import { wasClientNavigation } from '../lib/navigation';

function readUrl() {
  const params = new URLSearchParams(window.location.search);
  return { q: params.get('q') ?? '', tags: params.getAll('tag') };
}

export function SearchPage({ archive }: { archive: Archive }) {
  const { site, vocab, index } = archive;
  const lookup = useMemo(() => tagLookup(vocab), [vocab]);
  const counts = useMemo(() => tagCounts(index, lookup), [index, lookup]);
  const [{ q, tags }, setState] = useState(readUrl);
  const results = useMemo(() => searchPapers(index, lookup, q, tags), [index, lookup, q, tags]);

  // Keep the URL shareable: every search is a link.
  useEffect(() => {
    window.history.replaceState(null, '', searchHref({ q, tags }));
    document.title = `${site.name} — Search${q ? `: ${q}` : ''}`;
  }, [q, tags, site.name]);
  useEffect(() => {
    const onPop = () => setState(readUrl());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const setQuery = (next: string) => setState(s => ({ ...s, q: next }));
  const toggleTag = (id: string) =>
    setState(s => ({ ...s, tags: s.tags.includes(id) ? s.tags.filter(t => t !== id) : [...s.tags, id] }));

  return (
    <main>
      <h1 className="sr-only">{`${site.name} — Search`}</h1>
      <Masthead site={site} meta={['The archive', `${index.papers.length} stor${index.papers.length === 1 ? 'y' : 'ies'}`]} />
      <section className="search">
        <div className="label">The archive &nbsp; / &nbsp; Search every issue</div>
        <h2>Find a story</h2>
        <form className="search-box" role="search" onSubmit={e => e.preventDefault()}>
          <input type="search" value={q} onChange={e => setQuery(e.target.value)}
            placeholder="Search by topic, title, author or company" aria-label="Search stories" autoFocus={!wasClientNavigation()} />
        </form>
        {tags.length > 0 && (
          <p className="active-tags">
            <span className="label">Showing stories tagged</span>
            {tags.map(id => (
              <button type="button" key={id} className="tag tag-active" onClick={() => toggleTag(id)} aria-label={`Remove ${lookup.get(id)?.label ?? id}`}>
                {lookup.get(id)?.label ?? id} ✕
              </button>
            ))}
          </p>
        )}

        <div className="search-grid">
          <div aria-live="polite">
            <p className="label">{results.length} result{results.length === 1 ? '' : 's'}</p>
            {results.length === 0 && <p className="empty">No stories match. Try a broader word, or remove a tag.</p>}
            <ol className="results">
              {results.map(({ entry, matched }) => (
                <li key={entry.slug}>
                  <span className="label">{entry.desk} · {entry.year}</span>
                  <h3><a href={paperHref(entry.slug)}>{entry.pageTitle}</a></h3>
                  <p className="result-paper"><b>{entry.title}</b> · {entry.authors}</p>
                  <p>{entry.summary}</p>
                  {matched.length > 0 && (
                    <p className="result-tags">
                      {matched.slice(0, 8).map(t => <span key={t.id} className="tag">{t.label}</span>)}
                    </p>
                  )}
                </li>
              ))}
            </ol>
          </div>

          <aside className="browse" aria-label="Browse by tag">
            <p className="label">Browse by tag</p>
            {vocab.facets.map(facet => {
              const used = vocab.tags.filter(t => t.facet === facet.id && counts.has(t.id));
              if (!used.length) return null;
              return (
                <details key={facet.id} open={['area', 'concept', 'everyday', 'use'].includes(facet.id)}>
                  <summary>{facet.label}</summary>
                  <div>
                    {used.map(t => (
                      <button type="button" key={t.id} className={tags.includes(t.id) ? 'tag tag-active' : 'tag'}
                        aria-pressed={tags.includes(t.id)} onClick={() => toggleTag(t.id)}>
                        {t.label} <small>{counts.get(t.id)}</small>
                      </button>
                    ))}
                  </div>
                </details>
              );
            })}
          </aside>
        </div>
      </section>
      <footer>
        <span>{site.name} &nbsp; ✦ &nbsp; The archive</span>
        <a href={homeHref()}>Latest issue →</a>
      </footer>
    </main>
  );
}
