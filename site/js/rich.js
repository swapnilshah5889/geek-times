// Turns a caption string from the data into DOM nodes, keeping only a small set of inline tags.
// Content may come from a database later, so nothing else (scripts, styles, event handlers) gets through.
const ALLOWED = new Set(['B', 'STRONG', 'I', 'EM', 'SUB', 'SUP', 'A', 'BR']);

function clean(node) {
  for (const child of [...node.childNodes]) {
    if (child.nodeType === Node.TEXT_NODE) continue;
    if (child.nodeType !== Node.ELEMENT_NODE || !ALLOWED.has(child.tagName)) {
      child.replaceWith(...(child.nodeType === Node.ELEMENT_NODE ? cleanChildren(child) : []));
      continue;
    }
    const href = child.tagName === 'A' ? child.getAttribute('href') || '' : null;
    for (const attr of [...child.attributes]) child.removeAttribute(attr.name);
    if (href !== null && /^(https?:|#)/.test(href)) child.setAttribute('href', href);
    clean(child);
  }
  return node;
}

function cleanChildren(el) {
  return [...clean(el).childNodes];
}

export function rich(text = '') {
  const tpl = document.createElement('template');
  tpl.innerHTML = text;
  return clean(tpl.content);
}
