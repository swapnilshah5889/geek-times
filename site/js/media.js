// Renders one media entry from the data ({type, src, width, height, alt, poster}) into an element.
// `src` is resolved against the site's mediaBaseUrl, so moving files to a CDN or S3 is a config change.
//
// Types:
//   svg    animated SVG; fetched and placed in a shadow root so the page can pause it and its styles
//          stay private. Falls back to a plain <img> if the fetch fails (for example, no CORS on the CDN).
//   image  any still or animated image (gif, webp, png, jpg).
//   video  a short looping clip (mp4/webm), muted and inline, like a GIF.
// Every renderer returns a handle with setPaused(), which the motion controller calls.

const HOST_CSS = ':host{display:block}svg,img{display:block;width:100%;height:auto}' +
  ':host(.paused) *{animation-play-state:paused!important}';
const svgCache = new Map();

export function mediaUrl(src, base) {
  return new URL(src, new URL(base, document.baseURI)).href;
}

function fetchSvg(url) {
  if (!svgCache.has(url)) {
    svgCache.set(url, fetch(url).then(r => {
      if (!r.ok) throw new Error(`${r.status} ${url}`);
      return r.text();
    }));
  }
  return svgCache.get(url);
}

// Media files are ours, but they will live on another host, so strip anything executable anyway.
function safeSvg(text) {
  const svg = new DOMParser().parseFromString(text, 'image/svg+xml').documentElement;
  if (svg.nodeName !== 'svg') throw new Error('not an SVG file');
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

function image(url, alt = '') {
  const img = new Image();
  img.src = url;
  img.alt = alt;
  img.loading = 'lazy';
  img.decoding = 'async';
  return img;
}

const RENDERERS = {
  svg(host, url) {
    const root = host.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = HOST_CSS;
    root.append(style);
    fetchSvg(url).then(text => root.append(safeSvg(text)))
      .catch(err => { console.warn('SVG inline failed, using <img>:', err.message); root.append(image(url)); });
    return paused => host.classList.toggle('paused', paused);
  },
  image(host, url, media) {
    const img = image(url);
    host.append(img);
    // A GIF cannot be paused; if the data gives a still poster, show that while paused.
    return paused => { if (media.poster) img.src = paused ? mediaUrl(media.poster, host.dataset.base) : url; };
  },
  video(host, url, media) {
    const video = Object.assign(document.createElement('video'), { src: url, muted: true, loop: true, playsInline: true, preload: 'metadata' });
    video.setAttribute('muted', '');
    if (media.poster) video.poster = mediaUrl(media.poster, host.dataset.base);
    host.append(video);
    return paused => { if (paused) video.pause(); else video.play().catch(() => {}); };
  },
};

export function renderMedia(media, { mediaBaseUrl, motion }) {
  const host = document.createElement('div');
  host.className = `media media-${media.type}`;
  host.dataset.base = mediaBaseUrl;
  if (media.width && media.height) host.style.setProperty('--ar', `${media.width} / ${media.height}`);
  if (media.alt) {
    host.setAttribute('role', 'img');
    host.setAttribute('aria-label', media.alt);
  } else {
    host.setAttribute('aria-hidden', 'true');
  }
  const render = RENDERERS[media.type];
  if (!render) {
    console.warn('Unknown media type:', media.type);
    return host;
  }
  const setPaused = render(host, mediaUrl(media.src, mediaBaseUrl), media);
  motion?.add({ el: host, setPaused });
  return host;
}
