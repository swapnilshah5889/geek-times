import { createElement, Fragment, useMemo, type ReactNode } from 'react';
import type { RichText } from '../types';

// Captions may come from a database, so they are parsed and rebuilt as React elements
// from a short allowlist instead of being injected as HTML.
const ALLOWED = new Set(['b', 'strong', 'i', 'em', 'sub', 'sup', 'a', 'br']);

function toReact(node: Node, key: number): ReactNode {
  if (node.nodeType === Node.TEXT_NODE) return node.textContent;
  if (node.nodeType !== Node.ELEMENT_NODE) return null;
  const el = node as Element;
  const tag = el.tagName.toLowerCase();
  const children = [...el.childNodes].map(toReact);
  if (!ALLOWED.has(tag)) return <Fragment key={key}>{children}</Fragment>;
  const props: Record<string, unknown> = { key };
  if (tag === 'a') {
    const href = el.getAttribute('href') ?? '';
    if (/^(https?:|#)/.test(href)) props.href = href;
  }
  return createElement(tag, props, ...(tag === 'br' ? [] : children));
}

export function Rich({ text }: { text?: RichText }) {
  const nodes = useMemo(() => {
    if (!text) return null;
    const tpl = document.createElement('template');
    tpl.innerHTML = text;
    return [...tpl.content.childNodes].map(toReact);
  }, [text]);
  return <>{nodes}</>;
}
