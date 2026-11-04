// One renderer per block type in a paper's data. Each takes (block, ctx) and returns an element.
// To change how a kind of content looks, change its renderer here; the data stays the same.
// Unknown types are skipped, so newer data keeps working with an older page.
import { renderMedia } from './media.js';
import { MotionGroup } from './motion.js';
import { rich } from './rich.js';

export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === 'class') el.className = value;
    else if (key.startsWith('on')) el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value);
  }
  el.append(...children.flat().filter(c => c != null && c !== false));
  return el;
}

const kicker = text => h('div', { class: 'label' }, text.replaceAll(' / ', '  /  '));
const pad = n => String(n).padStart(2, '0');
const PROVENANCE = {
  illustration: 'Illustration · numbers invented',
  evidence: 'Evidence · real results',
};
const stamp = kind => (PROVENANCE[kind] ? h('span', { class: `label stamp stamp-${kind}` }, PROVENANCE[kind]) : null);

function motionButton(group, noun) {
  const button = h('button', { type: 'button', onclick: () => group.setHeld(!group.held) });
  group.onChange(held => { button.textContent = [held ? 'Play' : 'Pause', noun].filter(Boolean).join(' '); });
  return button;
}

function lead(block, ctx) {
  const motion = new MotionGroup();
  const { slides, intervalMs = 5500 } = block.slideshow;
  const frames = slides.map(s => h('div', { class: 'slide' }, renderMedia(s.media, { ...ctx, motion })));
  const counter = h('span');
  const caption = h('figcaption', { class: 'caption', 'aria-live': 'polite' });
  let index = 0;
  let timer;

  function show(i) {
    index = (i + slides.length) % slides.length;
    frames.forEach((f, n) => {
      f.classList.toggle('show', n === index);
      f.inert = n !== index;
    });
    counter.textContent = `${pad(index + 1)} / ${pad(slides.length)} · ${slides[index].label}`;
    caption.replaceChildren(rich(slides[index].caption));
  }
  function schedule() {
    clearInterval(timer);
    if (!motion.held && slides.length > 1) timer = setInterval(() => show(index + 1), intervalMs);
  }
  motion.onChange(schedule);
  show(0);

  const { paper } = ctx;
  return h('section', { class: 'lead', id: block.id },
    h('div', {},
      kicker(block.kicker),
      h('h1', {}, block.headline.text, h('br'), h('em', {}, block.headline.accent)),
      h('p', { class: 'deck' }, block.deck),
      h('div', { class: 'byline' }, h('b', {}, 'The paper'), ` · ${paper.title}`, h('i', {}, `${paper.authors}, ${paper.year}`))),
    h('figure', {},
      h('div', { class: 'plate slides' }, frames),
      h('div', { class: 'controls' }, counter,
        h('div', { class: 'buttons' },
          motionButton(motion, ''),
          slides.length > 1 && h('button', { type: 'button', onclick: () => { show(index + 1); schedule(); } }, 'Next scene →'))),
      caption));
}

function story(block, ctx) {
  const motion = new MotionGroup();
  return h('section', { class: 'section', id: block.id },
    kicker(block.kicker),
    h('div', { class: 'story-intro' }, h('h2', {}, block.title), motionButton(motion, 'picture story')),
    h('div', { class: 'chapters' }, block.chapters.map((c, i) =>
      h('article', { class: 'chapter' },
        h('header', {}, h('span', { class: 'chapnum' }, pad(i + 1)), h('span', { class: 'label' }, c.part), stamp(c.provenance)),
        h('h3', {}, c.title),
        h('figure', {}, renderMedia(c.media, { ...ctx, motion }), h('figcaption', {}, h('p', {}, rich(c.caption))))))));
}

function comic(block, ctx) {
  const motion = new MotionGroup();
  return h('section', { class: 'section comic-section', id: block.id },
    kicker(block.kicker),
    h('div', { class: 'story-intro' }, h('h2', {}, block.title), motionButton(motion, 'the comics')),
    block.deck && h('p', { class: 'comic-deck' }, rich(block.deck)),
    block.howTo && h('p', { class: 'howto' }, h('span', { class: 'label' }, 'How to read it'), ' ', rich(block.howTo)),
    block.strips.map((s, i) =>
      h('article', { class: 'strip' },
        h('header', {},
          h('span', { class: 'chapnum' }, pad(i + 1)),
          h('div', {}, h('h3', {}, s.title), s.kicker && h('span', { class: 'kicker' }, s.kicker)),
          stamp(s.provenance)),
        h('div', { class: 'comic' }, s.panels.map(p =>
          h('figure', { class: 'panel' }, h('figcaption', {}, rich(p.caption)), renderMedia(p.media, { ...ctx, motion })))),
        s.grownUpWords && h('p', { class: 'gw' }, `Grown-up words: ${s.grownUpWords}`))));
}

function facts(block, ctx) {
  const motion = new MotionGroup();
  return h('section', { class: 'facts', id: block.id },
    kicker(block.kicker),
    h('ul', {}, block.facts.map(f =>
      h('li', {},
        f.media && renderMedia(f.media, { ...ctx, motion }),
        h('b', { class: 'fig' }, f.figure),
        h('p', {}, rich(f.text)),
        f.source && h('a', { href: f.source.url }, `${f.source.label} ↗`)))));
}

export const BLOCKS = { lead, story, comic, facts };
