// Loads the site settings and one paper's data, then builds the page from it.
// Pick a paper with ?paper=<slug>; without it the site's defaultPaper is shown.
import { BLOCKS, h } from './blocks.js';

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Could not load ${url} (${res.status})`);
  return res.json();
}

function masthead(site, data) {
  const { issue } = data;
  const links = data.blocks.filter(b => b.nav && b.id).map(b => h('a', { href: `#${b.id}` }, b.nav));
  return h('header', {},
    h('div', { class: 'meta' },
      h('span', {}, `Vol. ${issue.volume}  ·  No. ${issue.number}`),
      h('span', {}, site.tagline),
      h('span', {}, issue.desk)),
    h('div', { class: 'mast' }, site.name),
    h('div', { class: 'motto' }, site.motto),
    h('nav', {}, h('span', {}, site.navLabel), h('span', { class: 'links' }, links)));
}

function footer(site, data) {
  return h('footer', {},
    h('span', {}, `${site.name}   ✦   Issue ${data.issue.number}`),
    h('a', { href: data.paper.url }, 'Read the original paper ↗'));
}

async function boot() {
  const app = document.getElementById('app');
  try {
    const site = await getJson('data/site.json');
    const slug = new URLSearchParams(location.search).get('paper') || site.defaultPaper;
    const entry = site.papers.find(p => p.slug === slug);
    if (!entry) throw new Error(`No paper called “${slug}”.`);
    const data = await getJson(entry.dataUrl);

    document.title = `${site.name} — ${data.pageTitle}`;
    const ctx = { site, paper: data.paper, mediaBaseUrl: site.mediaBaseUrl };
    const sections = data.blocks.map(block => {
      const render = BLOCKS[block.type];
      if (!render) console.warn('Skipping unknown block type:', block.type);
      return render?.(block, ctx);
    });
    app.replaceChildren(masthead(site, data), ...sections.filter(Boolean), footer(site, data));
    if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView();
  } catch (err) {
    app.replaceChildren(h('p', { class: 'load-error' }, `Sorry, this edition could not be loaded. ${err.message}`));
    console.error(err);
  } finally {
    app.removeAttribute('aria-busy');
  }
}

boot();
