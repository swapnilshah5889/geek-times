import { Fragment, useState } from 'react';
import type { Archive } from '../data/load';
import { familyOf, relationForward, relationLabel } from '../lib/library';
import { mapHref, paperHref } from '../lib/routes';
import type { GraphNode } from '../types';

// "Papers before and after this one": the oldest idea on the left, arrows forward in time, what grew
// from it on the right. Every link is a reviewed relation; until reviewed they are marked as samples.
export function FamilyTree({ archive, nodeId }: { archive: Archive; nodeId: string }) {
  const { library } = archive;
  const { before, after, links } = familyOf(library, nodeId);
  const here = library.nodes.find(n => n.id === nodeId);
  const [pickedId, setPicked] = useState<string | null>(null);
  if (!here || (!before.length && !after.length)) return null;
  const picked = library.nodes.find(n => n.id === pickedId) ?? before[before.length - 1] ?? after[0];
  const link = (a: string, b: string) => links.find(l => l.from === a && l.to === b);

  const box = (n: GraphNode, now = false) => {
    const explained = !!n.story;
    return (
      <button key={n.id} type="button" className={`ft-node${now ? ' is-now' : ''}${explained ? '' : ' is-open'}${picked?.id === n.id ? ' is-picked' : ''}`}
        aria-pressed={picked?.id === n.id} onClick={() => setPicked(n.id)}>
        <span className="ft-year">{n.year || 'Blog'}</span>
        <b>{n.title}</b>
        <span>{n.authors}</span>
        <i>{now ? 'You are here' : explained ? 'Explained in The Geeky Times' : 'Not explained yet'}</i>
      </button>
    );
  };

  const chain = [...before, here];
  const pickedLink = picked && (links.find(l => l.to === picked.id && (before.includes(picked) || l.from === nodeId)) ?? links.find(l => l.from === picked.id));
  return (
    <section id="tree" className="ft" aria-labelledby="tree-title">
      <div className="ft-head">
        <div><span className="label">Family tree · Papers before and after this one</span><h2 id="tree-title">Before and after {here.short ?? here.title}</h2></div>
        <span className="chip chip-warm">Sample links · to be fact-checked</span>
      </div>
      <div className="ft-board">
        <ol className="ft-chain" aria-label="Ideas that led here, oldest first">
          {chain.map((n, i) => (
            <Fragment key={n.id}>
              {i > 0 && <li className="ft-arrow" aria-hidden="true"><span>{link(chain[i - 1].id, n.id) ? relationForward[link(chain[i - 1].id, n.id)!.kind] : ''}</span>→</li>}
              <li>{box(n, n.id === nodeId)}</li>
            </Fragment>
          ))}
        </ol>
        {after.length > 0 && (
          <ul className="ft-after" aria-label="Work that grew from it">
            {after.map(n => (
              <li key={n.id}>
                <span className="ft-arrow" aria-hidden="true"><span>{relationForward[link(nodeId, n.id)?.kind ?? 'uses_method']}</span>→</span>
                {box(n)}
              </li>
            ))}
          </ul>
        )}
      </div>
      <p className="ft-key">Arrows point forward in time, from an idea to the work that grew from it. Dashed boxes are not explained yet.</p>
      {picked && (
        <div className="ft-detail" aria-live="polite">
          <div>
            <span className="label">Tap a paper to see how it connects</span>
            <h3>{picked.title} · {picked.year || 'blog post'}</h3>
            <p>{picked.blurb ?? pickedLink?.note ?? 'How this idea connects to the story.'}</p>
            {pickedLink && <p className="ft-link">{library.nodes.find(n => n.id === pickedLink.to)?.title} {relationLabel[pickedLink.kind]} {library.nodes.find(n => n.id === pickedLink.from)?.title}{pickedLink.cited ? ' · Cited in the paper' : ''}</p>}
          </div>
          <div className="ft-ask">
            {picked.story
              ? <a className="f-more" href={paperHref(picked.story)}>Read this story →</a>
              : <><span className="label">Not explained yet</span><p>Want this one drawn next? Papers with the most links go first. Requests open soon.</p></>}
            <a className="f-more" href={mapHref(picked.id)}>Open on the map →</a>
          </div>
        </div>
      )}
    </section>
  );
}
