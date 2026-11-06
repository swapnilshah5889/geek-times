import { useMemo, useState, type KeyboardEvent } from 'react';
import { useHead } from '../components/head';
import { Crumbs, SitePage } from '../components/SitePage';
import type { Archive } from '../data/load';
import { familyOf } from '../lib/library';
import { paperHref } from '../lib/routes';
import type { GraphNode } from '../types';

// The map of ideas: every paper and blog post we know of, grouped by field, with lines between related
// ones. It always has a list view too, so it works with a keyboard or screen reader (decision 24).
export function MapPage({ archive }: { archive: Archive }) {
  const { library, site } = archive;
  // The description states the counts from the data. The links are unverified, and the page says so, so the preview does too.
  useHead({
    title: `The map of ideas — ${site.name}`,
    description: `${library.nodes.length} papers and engineering posts in ${library.fields.length} fields, with lines between related ideas. The links are still being fact-checked.`,
    type: 'website',
  });
  const first = new URLSearchParams(window.location.search).get('focus');
  const [view, setView] = useState<'map' | 'list'>('map');
  const [query, setQuery] = useState('');
  const [fields, setFields] = useState<string[]>(library.fields.map(f => f.id));
  const [show, setShow] = useState({ paper: true, blog: true, open: true });
  const [from, setFrom] = useState(1900);
  const [pickedId, setPicked] = useState<string>(first && library.nodes.some(n => n.id === first) ? first : (library.nodes.find(n => n.story === library.front.lead) ?? library.nodes[0]).id);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return library.nodes.filter(n =>
      fields.includes(n.field)
      && (n.type === 'blog' ? show.blog : show.paper)
      && (n.story || show.open)
      && (!n.year || n.year >= from)
      && (!q || `${n.title} ${n.authors}`.toLowerCase().includes(q)));
  }, [library.nodes, fields, show, from, query]);
  const ids = new Set(visible.map(n => n.id));
  const picked = library.nodes.find(n => n.id === pickedId) ?? library.nodes[0];
  const fam = familyOf(library, picked.id);
  const color = (n: GraphNode) => library.fields.find(f => f.id === n.field)?.color ?? '#4f4a3e';
  const toggleField = (id: string) => setFields(f => (f.includes(id) ? f.filter(x => x !== id) : [...f, id]));
  const onKey = (n: GraphNode) => (e: KeyboardEvent) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPicked(n.id); } };
  const toggle = (k: keyof typeof show) => setShow(s => ({ ...s, [k]: !s[k] }));
  const pressed = (key: string, on: boolean, label: string, onClick: () => void) => (
    <button key={key} type="button" className="mp-chip" aria-pressed={on} onClick={onClick}>{`${on ? '✓ ' : ''}${label}`}</button>
  );

  return (
    <SitePage archive={archive} title="The map of ideas" active="explore" motion={false}>
      <Crumbs items={['The map of ideas']} />
      <div className="mp-head">
        <div className="mp-title">
          <h1>The map of ideas</h1>
          <div role="group" aria-label="View" className="mp-toggle">
            <button type="button" aria-pressed={view === 'map'} onClick={() => setView('map')}>Map</button>
            <button type="button" aria-pressed={view === 'list'} onClick={() => setView('list')}>List view</button>
          </div>
        </div>
        <span className="chip chip-warm">Sample layout · links to be fact-checked</span>
      </div>

      <div className="mp-body">
        <aside aria-label="Filters" className="mp-filters">
          <label>Find a paper or idea<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Title or author" /></label>
          <div><span className="label">Fields</span>{library.fields.map(f => pressed(f.id, fields.includes(f.id), f.label, () => toggleField(f.id)))}</div>
          <div><span className="label">Show</span>
            {pressed('show-paper', show.paper, 'Papers', () => toggle('paper'))}
            {pressed('show-blog', show.blog, 'Engineering blogs', () => toggle('blog'))}
            {pressed('show-open', show.open, 'Not explained yet', () => toggle('open'))}
          </div>
          <div><span className="label">Years</span>
            <label>From year<input type="range" min={1900} max={2026} step={1} value={from} onChange={e => setFrom(Number(e.target.value))} aria-valuetext={`${from}`} /></label>
            <span className="mp-years">{`${from} – 2026`}</span>
          </div>
        </aside>

        {view === 'map' && (
          <div className="mp-canvas">
            <svg viewBox="0 0 800 600" role="group" aria-label="A map of research grouped into fields, with lines linking related papers. Use the list view for the same content as text.">
              <rect width="800" height="600" fill="#fbf3dc" />
              {library.fields.map(f => <ellipse key={f.id} cx={f.cluster.cx} cy={f.cluster.cy} rx={f.cluster.rx} ry={f.cluster.ry} fill={f.color} opacity={0.2} />)}
              <g fontFamily="Courier New, monospace" fontWeight={700} fontSize={13} letterSpacing={1.5} fill="#4f4a3e">
                {library.fields.map(f => <text key={f.id} x={f.cluster.labelX} y={f.cluster.labelY}>{f.label.toUpperCase()}</text>)}
              </g>
              <g stroke="#948b77" strokeWidth={1.5} fill="none">
                {library.relations.filter(r => ids.has(r.from) && ids.has(r.to)).map(r => {
                  const a = library.nodes.find(n => n.id === r.from)!; const b = library.nodes.find(n => n.id === r.to)!;
                  const hot = r.from === picked.id || r.to === picked.id;
                  return <path key={r.from + r.to} d={`M${a.x} ${a.y}L${b.x} ${b.y}`} strokeDasharray={r.crossField ? '4 5' : undefined} stroke={hot ? '#a13324' : '#948b77'} strokeWidth={hot ? 2.5 : 1.5} />;
                })}
              </g>
              <g stroke="#322e24" strokeWidth={2}>
                {visible.map(n => {
                  const explained = !!n.story; const sel = n.id === picked.id;
                  const common = { role: 'button', tabIndex: 0, 'aria-label': `${n.title}, ${n.year || 'blog post'}, ${explained ? 'explained' : 'not explained yet'}`, 'aria-pressed': sel, onClick: () => setPicked(n.id), onKeyDown: onKey(n), style: { cursor: 'pointer' } };
                  return (
                    <g key={n.id} {...common}>
                      {n.type === 'blog'
                        ? <rect x={n.x - 9} y={n.y - 9} width={18} height={18} rx={3} fill="#f7d79b" stroke={sel ? '#a13324' : '#322e24'} strokeWidth={sel ? 3 : 2} />
                        : <circle cx={n.x} cy={n.y} r={sel ? 15 : explained ? 11 : 9} fill={sel ? '#f6e3a1' : explained ? color(n) : '#ece6d6'} strokeDasharray={explained ? undefined : '3 3'} stroke={sel ? '#a13324' : '#322e24'} strokeWidth={sel ? 3 : 2} />}
                      <circle cx={n.x} cy={n.y} r={22} fill="transparent" stroke="none" />
                    </g>
                  );
                })}
              </g>
              <g fontFamily="Georgia, serif" fontSize={14} fill="#27251e">
                {visible.filter(n => n.story || n.id === picked.id).map(n => <text key={n.id} x={n.x} y={n.y + 30} textAnchor="middle" fontWeight={700} stroke="#fbf3dc" strokeWidth={4} paintOrder="stroke">{n.short ?? (n.title.length > 22 ? `${n.title.slice(0, 20)}…` : n.title)}</text>)}
              </g>
            </svg>
          </div>
        )}
        {view === 'list' && (
          <ul className="mp-list" aria-label="All papers and posts">
            {visible.map(n => <li key={n.id}><button type="button" onClick={() => setPicked(n.id)} aria-pressed={n.id === picked.id}><b>{n.title}</b>{` · ${n.year || 'blog'} · ${library.fields.find(f => f.id === n.field)?.label} · ${n.story ? 'explained' : 'not explained yet'}`}</button></li>)}
            {!visible.length && <li>Nothing matches these filters.</li>}
          </ul>
        )}

        <aside aria-label="Selected" className="mp-selected" aria-live="polite">
          <span className="label">{`Selected · ${picked.type === 'blog' ? 'Engineering blog' : 'Paper'} · ${picked.year || 'blog'}`}</span>
          <h2>{picked.title}</h2>
          <p>{picked.story ? 'We have explained this one.' : 'Not explained yet. Papers with the most links get drawn first.'} {picked.authors}</p>
          <div className="mp-counts"><div><b>{fam.before.length}</b><span>ideas it built on</span></div><div><b>{fam.after.length}</b><span>works that grew from it</span></div></div>
          {picked.story && <a className="f-more" href={paperHref(picked.story)}>Read the story →</a>}
          <ul className="mp-key"><li><i style={{ background: '#377675' }} /> Explained paper (colour = field)</li><li><i className="is-open" /> Not explained yet</li><li><i className="is-blog" /> Engineering blog post</li><li>Dashed lines link ideas across fields.</li></ul>
        </aside>
      </div>

      <section aria-labelledby="map-list" className="f-section mp-textlist">
        <h2 id="map-list">Every paper on the map, as a list</h2>
        <p>The same nodes and links, readable with a keyboard or screen reader.</p>
        <ul>
          {library.nodes.map(n => {
            const f = familyOf(library, n.id);
            return <li key={n.id}><b>{n.title}</b>{` · ${n.year || 'blog'} · ${library.fields.find(x => x.id === n.field)?.label} · ${n.story ? 'explained' : 'not explained yet'}${(f.before.length || f.after.length) ? ` · ${f.before.length} before, ${f.after.length} after` : ''}`}</li>;
          })}
        </ul>
      </section>
    </SitePage>
  );
}
