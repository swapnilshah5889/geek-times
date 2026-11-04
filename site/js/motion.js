// Decides when media should move: only while on screen, not while its section is paused,
// and never by default for readers who ask for reduced motion.
export const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

const groups = new Set();
const visible = new WeakSet();
const owners = new WeakMap();
const observer = new IntersectionObserver(entries => {
  for (const { target, isIntersecting } of entries) {
    if (isIntersecting) visible.add(target); else visible.delete(target);
    owners.get(target)?.sync();
  }
}, { rootMargin: '80px' });

export class MotionGroup {
  constructor() {
    this.items = [];
    this.held = reducedMotion.matches;
    this.listeners = [];
    groups.add(this);
  }

  add(item) {
    this.items.push(item);
    owners.set(item.el, this);
    observer.observe(item.el);
    item.setPaused(true);
  }

  setHeld(held) {
    this.held = held;
    this.sync();
    this.listeners.forEach(fn => fn(held));
  }

  onChange(fn) {
    this.listeners.push(fn);
    fn(this.held);
  }

  sync() {
    for (const item of this.items) item.setPaused(this.held || !visible.has(item.el));
  }
}

reducedMotion.addEventListener('change', () => groups.forEach(g => g.setHeld(reducedMotion.matches)));
