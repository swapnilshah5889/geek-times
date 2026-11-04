import { useEffect, useRef, type CSSProperties } from 'react';
import { useEdition } from '../edition';
import type { Media } from '../types';
import { useInView, useMotion } from '../lib/motion';

// Renders one media entry. `src` is resolved against mediaBaseUrl, so moving files to a CDN or S3
// is a config change. Types:
//   svg    animated SVG, fetched into a shadow root so the page can pause it and its styles stay private;
//          falls back to <img> if the fetch fails (for example, no CORS on the CDN)
//   image  still or animated image (gif, webp, png, jpg)
//   video  short looping clip (mp4/webm), muted and inline, like a GIF

const HOST_CSS = ':host{display:block}svg,img{display:block;width:100%;height:auto}' +
  ':host(.paused) *{animation-play-state:paused!important}';
const svgCache = new Map<string, Promise<string>>();

function fetchSvg(url: string): Promise<string> {
  let text = svgCache.get(url);
  if (!text) {
    text = fetch(url).then(r => {
      if (!r.ok) throw new Error(`${r.status} ${url}`);
      return r.text();
    });
    svgCache.set(url, text);
  }
  return text;
}

// Media files are ours, but they will live on another host, so strip anything executable anyway.
function safeSvg(text: string): SVGSVGElement {
  const svg = new DOMParser().parseFromString(text, 'image/svg+xml').documentElement;
  if (!(svg instanceof SVGSVGElement)) throw new Error('not an SVG file');
  svg.querySelectorAll('script,foreignObject').forEach(n => n.remove());
  for (const el of [svg, ...svg.querySelectorAll('*')]) {
    for (const { name, value } of [...el.attributes]) {
      if (/^on/i.test(name) || (/href$/i.test(name) && !value.startsWith('#'))) el.removeAttribute(name);
    }
  }
  svg.removeAttribute('role');
  svg.setAttribute('aria-hidden', 'true');
  return document.importNode(svg, true);
}

function InlineSvg({ url, paused }: { url: string; paused: boolean }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = host.current!;
    const root = el.shadowRoot ?? el.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = HOST_CSS;
    root.replaceChildren(style);
    const done = new AbortController();
    fetchSvg(url)
      .then(text => { if (!done.signal.aborted) root.append(safeSvg(text)); })
      .catch((err: Error) => {
        if (done.signal.aborted) return;
        console.warn('SVG inline failed, using <img>:', err.message);
        root.append(Object.assign(new Image(), { src: url, alt: '' }));
      });
    return () => done.abort();
  }, [url]);
  return <div ref={host} className={paused ? 'paused' : undefined} />;
}

function Video({ url, poster, paused }: { url: string; poster?: string; paused: boolean }) {
  const video = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const v = video.current!;
    if (paused) v.pause(); else v.play().catch(() => {});
  }, [paused]);
  return <video ref={video} src={url} poster={poster} muted loop playsInline preload="metadata" />;
}

export function MediaView({ media }: { media: Media }) {
  const { mediaBaseUrl } = useEdition();
  const { held } = useMotion();
  const box = useRef<HTMLDivElement>(null);
  const inView = useInView(box);
  const paused = held || !inView;
  const url = new URL(media.src, mediaBaseUrl).href;
  const poster = media.poster ? new URL(media.poster, mediaBaseUrl).href : undefined;
  const style = media.width && media.height ? ({ '--ar': `${media.width} / ${media.height}` } as CSSProperties) : undefined;
  const a11y = media.alt ? { role: 'img', 'aria-label': media.alt } : { 'aria-hidden': true };

  let content;
  switch (media.type) {
    case 'svg':
      content = <InlineSvg url={url} paused={paused} />;
      break;
    case 'image':
      // A GIF cannot be paused; if the data gives a still poster, show that while paused.
      content = <img src={paused && poster ? poster : url} alt="" loading="lazy" decoding="async" />;
      break;
    case 'video':
      content = <Video url={url} poster={poster} paused={paused} />;
      break;
    default:
      console.warn('Unknown media type:', (media as { type: string }).type);
  }
  return (
    <div ref={box} className={`media media-${media.type}`} style={style} {...a11y}>
      {content}
    </div>
  );
}
