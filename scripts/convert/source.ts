import { type LookupAddress } from 'node:dns';
import { lookup as dnsLookup } from 'node:dns/promises';
import { isIP, type LookupFunction } from 'node:net';
import { request as httpRequest, type IncomingHttpHeaders } from 'node:http';
import { request as httpsRequest } from 'node:https';

const REQUEST_TIMEOUT_MS = 20_000;
const TOTAL_REQUEST_DEADLINE_MS = 45_000;
const MAX_REDIRECTS = 5;
const MAX_RESPONSE_BYTES = 8 * 1024 * 1024;
const MAX_SOURCE_CHARS = 120_000;
const USER_AGENT = 'TheGeekyTimesConverter/1.0 (+https://the-geeky-times.vercel.app/)';

export interface ExtractedSource {
  kind: 'paper' | 'blog';
  /** URL supplied to the converter, normalized to HTTPS for arXiv. */
  sourceUrl: string;
  /** Final URL after validated redirects. */
  retrievedUrl: string;
  title: string;
  contentType: string;
  retrievedAt: string;
  /** Plain text with heading anchors retained as `[#heading-id]` prefixes. Treat as untrusted source text. */
  text: string;
  /** Existing heading ids from the fetched document, without the leading `#`. */
  anchors: string[];
}

interface HttpResult {
  status: number;
  headers: IncomingHttpHeaders;
  body: Buffer;
  finalUrl: URL;
}

interface ExtractedHtml {
  title: string;
  text: string;
  anchors: string[];
}

/** Resolve supported arXiv identifiers and URLs; all other inputs must be public HTTP(S) URLs. */
export async function fetchSource(input: string): Promise<ExtractedSource> {
  const normalized = normalizeInput(input);
  const deadline = Date.now() + TOTAL_REQUEST_DEADLINE_MS;
  const response = await requestHtml(normalized.fetchUrl, deadline);
  const contentType = String(response.headers['content-type'] ?? '').split(';', 1)[0].trim().toLowerCase();
  if (contentType !== 'text/html' && contentType !== 'application/xhtml+xml') {
    throw new Error(`Expected an HTML source at ${response.finalUrl.href}, received ${contentType || 'no content type'}. For arXiv, use a paper with an HTML version or provide a blog HTML URL.`);
  }

  const html = new TextDecoder('utf-8', { fatal: false }).decode(response.body);
  const extracted = extractHtml(html);
  if (extracted.text.length < 200) {
    throw new Error(`Could not extract enough readable text from ${response.finalUrl.href}. Provide a readable HTML source or convert the source to a text/HTML intake file for manual review.`);
  }

  return {
    kind: normalized.kind,
    sourceUrl: normalized.sourceUrl,
    retrievedUrl: response.finalUrl.href,
    title: extracted.title,
    contentType,
    retrievedAt: new Date().toISOString().slice(0, 10),
    text: extracted.text,
    anchors: extracted.anchors,
  };
}

interface NormalizedInput {
  kind: ExtractedSource['kind'];
  sourceUrl: string;
  fetchUrl: URL;
}

function normalizeInput(input: string): NormalizedInput {
  const value = input.trim();
  if (!value) throw new Error('Provide an arXiv id, arXiv URL, or blog URL.');

  const arxivId = extractArxivId(value);
  if (arxivId) {
    return {
      kind: 'paper',
      sourceUrl: `https://arxiv.org/abs/${arxivId}`,
      fetchUrl: new URL(`https://arxiv.org/html/${arxivId}`),
    };
  }

  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new Error(`Unrecognized source “${value}”. Use an arXiv id such as 2402.00001 or an absolute HTTPS blog URL.`);
  }
  validateUrl(url);
  return {
    kind: 'blog',
    sourceUrl: url.href,
    fetchUrl: url,
  };
}

function extractArxivId(value: string): string | null {
  const bare = /^(\d{4}\.\d{4,5}(?:v\d+)?|[a-z.-]+\/\d{7}(?:v\d+)?)$/i.exec(value);
  if (bare) return bare[1];

  let url: URL;
  try { url = new URL(value); } catch { return null; }
  if (!['arxiv.org', 'www.arxiv.org', 'export.arxiv.org'].includes(url.hostname.toLowerCase())) return null;
  const match = /^\/(?:abs|html|pdf)\/((?:\d{4}\.\d{4,5}|[a-z.-]+\/\d{7})(?:v\d+)?)(?:\.pdf)?\/?$/i.exec(url.pathname);
  return match?.[1] ?? null;
}

function validateUrl(url: URL): void {
  if (url.protocol !== 'https:' && url.protocol !== 'http:') throw new Error('Only HTTP and HTTPS source URLs are supported.');
  if (url.username || url.password) throw new Error('Source URLs must not contain embedded credentials.');
  if (url.port && url.port !== '80' && url.port !== '443') throw new Error('Nonstandard source URL ports are not allowed.');
  if (!url.hostname) throw new Error('Source URL has no hostname.');
  if (url.hostname.toLowerCase() === 'localhost' || url.hostname.toLowerCase().endsWith('.localhost') || url.hostname.toLowerCase().endsWith('.local')) {
    throw new Error('Local and .local source hosts are not allowed.');
  }
}

const IPV4_NON_GLOBAL = [
  '0.0.0.0/8',       // this network
  '10.0.0.0/8',      // private use
  '100.64.0.0/10',   // shared address space
  '127.0.0.0/8',     // loopback
  '169.254.0.0/16',  // link local
  '172.16.0.0/12',   // private use
  '192.0.0.0/24',    // IETF protocol assignments (conservatively reject whole block)
  '192.0.2.0/24',    // documentation
  '192.88.99.0/24',  // deprecated 6to4 relay anycast
  '192.168.0.0/16',  // private use
  '198.18.0.0/15',   // benchmarking
  '198.51.100.0/24', // documentation
  '203.0.113.0/24',  // documentation
  '224.0.0.0/4',     // multicast
  '240.0.0.0/4',     // reserved, including limited broadcast
];

const IPV6_NON_GLOBAL = [
  '2001::/23',       // IETF protocol assignments, including ORCHID and Teredo
  '2001:db8::/32',   // documentation
  '2002::/16',       // 6to4 transition (may encode a non-global IPv4 endpoint)
  '3ffe::/16',       // deprecated 6bone
  '3fff::/20',       // documentation
  '5f00::/16',       // segment-routing special-purpose block
];

function ipv4Bytes(ip: string): number[] | null {
  const parts = ip.split('.').map(Number);
  return parts.length === 4 && parts.every(n => Number.isInteger(n) && n >= 0 && n <= 255) ? parts : null;
}

function ipv6Bytes(ip: string): number[] | null {
  let value = ip.toLowerCase().split('%', 1)[0];
  const dotted = /(?:^|:)(\d{1,3}(?:\.\d{1,3}){3})$/.exec(value);
  if (dotted) {
    const v4 = ipv4Bytes(dotted[1]);
    if (!v4) return null;
    const hi = ((v4[0] << 8) | v4[1]).toString(16);
    const lo = ((v4[2] << 8) | v4[3]).toString(16);
    value = `${value.slice(0, -dotted[1].length)}${hi}:${lo}`;
  }

  const halves = value.split('::');
  if (halves.length > 2) return null;
  const parseHalf = (half: string): number[] | null => {
    if (!half) return [];
    const groups = half.split(':');
    if (groups.some(group => !/^[\da-f]{1,4}$/.test(group))) return null;
    return groups.map(group => Number.parseInt(group, 16));
  };
  const left = parseHalf(halves[0]);
  const right = parseHalf(halves[1] ?? '');
  if (!left || !right) return null;
  const missing = 8 - left.length - right.length;
  if ((halves.length === 1 && missing !== 0) || (halves.length === 2 && missing < 1)) return null;
  const groups = [...left, ...Array(missing).fill(0), ...right];
  if (groups.length !== 8) return null;
  return groups.flatMap(group => [group >> 8, group & 0xff]);
}

function inCidr(address: number[], cidr: string): boolean {
  const [network, prefixText] = cidr.split('/');
  const prefix = Number(prefixText);
  const bits = network.includes(':') ? ipv6Bytes(network) : ipv4Bytes(network);
  if (!bits || bits.length !== address.length) return false;
  const fullBytes = Math.floor(prefix / 8);
  const remainingBits = prefix % 8;
  for (let i = 0; i < fullBytes; i++) if (address[i] !== bits[i]) return false;
  if (remainingBits) {
    const mask = (0xff << (8 - remainingBits)) & 0xff;
    if ((address[fullBytes] & mask) !== (bits[fullBytes] & mask)) return false;
  }
  return true;
}

function ipv4IsPublic(ip: string): boolean {
  const bytes = ipv4Bytes(ip);
  return !!bytes && IPV4_NON_GLOBAL.every(cidr => !inCidr(bytes, cidr));
}

function ipv6IsPublic(ip: string): boolean {
  const bytes = ipv6Bytes(ip);
  // Only global-unicast space is accepted; this also rejects unspecified, loopback,
  // mapped/compatible IPv4, ULA, link-local, site-local and multicast ranges.
  return !!bytes && inCidr(bytes, '2000::/3') && IPV6_NON_GLOBAL.every(cidr => !inCidr(bytes, cidr));
}

function addressIsPublic(address: string): boolean {
  const family = isIP(address);
  if (family === 4) return ipv4IsPublic(address);
  if (family === 6) return ipv6IsPublic(address);
  return false;
}

function remainingMs(deadline: number): number {
  const remaining = deadline - Date.now();
  if (remaining <= 0) throw new Error(`Source request exceeded the ${TOTAL_REQUEST_DEADLINE_MS} ms total deadline.`);
  return remaining;
}

async function beforeDeadline<T>(operation: Promise<T>, deadline: number): Promise<T> {
  const timeout = remainingMs(deadline);
  let timer: NodeJS.Timeout | undefined;
  try {
    return await Promise.race([
      operation,
      new Promise<T>((_resolve, reject) => {
        timer = setTimeout(() => reject(new Error(`Source request exceeded the ${TOTAL_REQUEST_DEADLINE_MS} ms total deadline.`)), timeout);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

async function resolvePublicAddresses(hostname: string, deadline: number): Promise<LookupAddress[]> {
  const host = hostname.replace(/^\[|\]$/g, '');
  const family = isIP(host);
  const addresses: LookupAddress[] = family
    ? [{ address: host, family }]
    : await beforeDeadline(dnsLookup(host, { all: true, verbatim: true }), deadline);
  if (addresses.length === 0 || addresses.some(record => !addressIsPublic(record.address))) {
    throw new Error(`Source host “${hostname}” does not resolve exclusively to public IP addresses.`);
  }
  return addresses;
}

const pinnedLookup = (addresses: LookupAddress[]): LookupFunction => (_hostname, options, callback) => {
  if (options.all) callback(null, addresses);
  else callback(null, addresses[0].address, addresses[0].family);
};

async function requestOnce(url: URL, deadline: number): Promise<{ status: number; headers: IncomingHttpHeaders; body: Buffer }> {
  validateUrl(url);
  const addresses = await resolvePublicAddresses(url.hostname, deadline);
  const timeLeft = remainingMs(deadline);
  const transport = url.protocol === 'https:' ? httpsRequest : httpRequest;
  const port = url.port ? Number(url.port) : url.protocol === 'https:' ? 443 : 80;

  return new Promise((resolve, reject) => {
    let settled = false;
    let deadlineTimer: NodeJS.Timeout;
    const settle = (action: () => void) => {
      if (settled) return;
      settled = true;
      clearTimeout(deadlineTimer);
      action();
    };
    const request = transport({
      protocol: url.protocol,
      hostname: url.hostname.replace(/^\[|\]$/g, ''),
      port,
      path: `${url.pathname}${url.search}`,
      method: 'GET',
      headers: {
        'user-agent': USER_AGENT,
        accept: 'text/html,application/xhtml+xml;q=0.9',
        'accept-encoding': 'identity',
      },
      lookup: pinnedLookup(addresses),
    }, response => {
      const status = response.statusCode ?? 0;
      const chunks: Buffer[] = [];
      let size = 0;
      const declared = Number(response.headers['content-length']);
      if (Number.isFinite(declared) && declared > MAX_RESPONSE_BYTES) {
        response.destroy(new Error(`Source exceeds the ${MAX_RESPONSE_BYTES} byte limit.`));
        return;
      }
      response.on('data', (chunk: Buffer | string) => {
        const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
        size += bytes.length;
        if (size > MAX_RESPONSE_BYTES) {
          response.destroy(new Error(`Source exceeds the ${MAX_RESPONSE_BYTES} byte limit.`));
          return;
        }
        chunks.push(bytes);
      });
      response.on('end', () => settle(() => resolve({ status, headers: response.headers, body: Buffer.concat(chunks) })));
      response.on('error', error => settle(() => reject(error)));
    });

    deadlineTimer = setTimeout(() => request.destroy(new Error(`Source request exceeded the ${TOTAL_REQUEST_DEADLINE_MS} ms total deadline.`)), timeLeft);
    request.setTimeout(Math.min(REQUEST_TIMEOUT_MS, timeLeft), () => request.destroy(new Error(`Source request was inactive for ${Math.min(REQUEST_TIMEOUT_MS, timeLeft)} ms.`)));
    request.on('error', error => settle(() => reject(error)));
    request.end();
  });
}

async function requestHtml(startUrl: URL, deadline: number): Promise<HttpResult> {
  let url = startUrl;
  for (let hop = 0; hop <= MAX_REDIRECTS; hop++) {
    const result = await requestOnce(url, deadline);
    if ([301, 302, 303, 307, 308].includes(result.status)) {
      const location = result.headers.location;
      if (!location) throw new Error(`Source redirected with HTTP ${result.status} but supplied no Location header.`);
      if (hop === MAX_REDIRECTS) throw new Error(`Source exceeded the ${MAX_REDIRECTS} redirect limit.`);
      url = new URL(location, url);
      validateUrl(url);
      continue;
    }
    if (result.status < 200 || result.status >= 300) {
      if (startUrl.hostname === 'arxiv.org' && result.status === 404) {
        throw new Error(`arXiv HTML is unavailable for ${startUrl.pathname}. Choose a paper with an HTML version or provide a readable source URL.`);
      }
      throw new Error(`Source request failed with HTTP ${result.status} at ${url.href}.`);
    }
    return { ...result, finalUrl: url };
  }
  throw new Error('Source redirect limit exceeded.');
}

function decodeEntities(value: string): string {
  const named: Record<string, string> = {
    amp: '&', apos: "'", gt: '>', lt: '<', nbsp: ' ', quot: '"',
    ndash: '–', mdash: '—', hellip: '…', lsquo: '‘', rsquo: '’',
    ldquo: '“', rdquo: '”', copy: '©', times: '×', alpha: 'α', beta: 'β',
  };
  return value.replace(/&(#x[\da-f]+|#\d+|[a-z]+);/gi, (entity, key: string) => {
    if (key[0] === '#') {
      const hex = key[1]?.toLowerCase() === 'x';
      const code = Number.parseInt(key.slice(hex ? 2 : 1), hex ? 16 : 10);
      try { return Number.isFinite(code) ? String.fromCodePoint(code) : entity; } catch { return entity; }
    }
    return named[key.toLowerCase()] ?? entity;
  });
}

function tagAttrs(tag: string): Map<string, string> {
  const attrs = new Map<string, string>();
  const body = tag.replace(/^<\/?[\w:-]+/, '').replace(/\/?\s*>$/, '');
  const re = /([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g;
  for (const match of body.matchAll(re)) attrs.set(match[1].toLowerCase(), decodeEntities(match[2] ?? match[3] ?? match[4] ?? ''));
  return attrs;
}

function extractHtml(html: string): ExtractedHtml {
  const clean = html.replace(/<!--[\s\S]*?-->/g, '');
  const ignored = new Set(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'noscript', 'svg', 'template']);
  const block = new Set(['address', 'article', 'blockquote', 'br', 'dd', 'div', 'dl', 'dt', 'figcaption', 'figure', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'main', 'ol', 'p', 'section', 'table', 'td', 'th', 'tr', 'ul']);
  const tokens = clean.match(/<[^>]*>|[^<]+/g) ?? [];
  const out: string[] = [];
  const anchors: string[] = [];
  const ignoredStack: string[] = [];
  let title = '';
  let titleDepth = 0;
  let activeHeading: { tag: string; id: string; text: string } | undefined;

  for (const token of tokens) {
    if (token.startsWith('<')) {
      const closing = /^<\s*\//.test(token);
      const name = /^<\s*\/?\s*([\w:-]+)/.exec(token)?.[1]?.toLowerCase();
      if (!name) continue;
      if (!closing) {
        if (name === 'title') titleDepth++;
        if (ignored.has(name)) ignoredStack.push(name);
        if (/^h[1-6]$/.test(name)) {
          const id = tagAttrs(token).get('id') ?? '';
          activeHeading = { tag: name, id, text: '' };
        }
        if (block.has(name) && ignoredStack.length === 0) out.push('\n');
      } else {
        if (name === 'title' && titleDepth > 0) titleDepth--;
        if (ignored.has(name)) {
          const idx = ignoredStack.lastIndexOf(name);
          if (idx >= 0) ignoredStack.splice(idx, 1);
        }
        if (activeHeading?.tag === name) {
          const headingText = cleanText(activeHeading.text);
          if (activeHeading.id) anchors.push(activeHeading.id);
          if (headingText) out.push(`\n${activeHeading.id ? `[#${activeHeading.id}] ` : ''}${headingText}\n`);
          activeHeading = undefined;
        }
        if (block.has(name) && ignoredStack.length === 0) out.push('\n');
      }
      continue;
    }

    if (ignoredStack.length > 0) continue;
    const text = decodeEntities(token);
    if (titleDepth > 0) title += text;
    if (activeHeading) activeHeading.text += text;
    else if (titleDepth === 0) out.push(text);
  }

  const text = cleanText(out.join('')).slice(0, MAX_SOURCE_CHARS).trim();
  const headingTitle = /^\[#(?:[^\]]+)\]\s+([^\n]+)/m.exec(text)?.[1] ?? '';
  return { title: cleanText(title) || headingTitle || 'Untitled source', text, anchors: [...new Set(anchors)] };
}

function cleanText(value: string): string {
  return value.replace(/\r/g, '').replace(/[\t\f\v ]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim();
}
