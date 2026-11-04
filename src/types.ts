// The content model. These shapes are the contract between the data (JSON files today, a database
// later) and the UI. Bump schemaVersion when a change is not backwards compatible.

export interface SiteConfig {
  schemaVersion: 1;
  name: string;
  motto: string;
  tagline: string;
  navLabel: string;
  /** Where media `src` paths are resolved: a relative path, or a CDN / S3 URL. */
  mediaBaseUrl: string;
  defaultPaper: string;
  papers: PaperEntry[];
}

export interface PaperEntry {
  slug: string;
  title: string;
  /** URL of the paper document: a static JSON file now, an API endpoint later. */
  dataUrl: string;
}

export interface PaperDoc {
  schemaVersion: 1;
  slug: string;
  pageTitle: string;
  /** One or two plain-language sentences; shown on the home page and in search results. */
  summary: string;
  /** How the paper appears on the home page. Optional: without it, the lead block is used. */
  cover?: Cover;
  issue: { volume: string; number: string; desk: string };
  paper: { title: string; authors: string; year: number; url: string };
  tags: PaperTag[];
  blocks: Block[];
}

// ---------- Tags ----------
// Tags come from a shared vocabulary (public/data/tags.json, a `tags` table later) so the same idea has
// one id across every paper. Each paper links to tags with a relevance score and a note on where the
// tag comes from, just like evidence facts.

/** Groups of tags. Each answers a different question a reader might search by. */
export type TagFacet =
  | 'field'        // broad science: Computer science, Biology
  | 'area'         // narrower area: Machine learning, Natural language processing
  | 'concept'      // ideas the paper explains or depends on: Attention, Embeddings
  | 'technique'    // named methods and models: Transformer, Adam optimizer
  | 'task'         // the job being solved: Machine translation
  | 'dataset'      // data used: WMT 2014 English–German
  | 'metric'       // how results are scored: BLEU
  | 'use'          // real-world uses today: Translation apps, Chatbots
  | 'impact'       // what the work led to: Large language models
  | 'organization' // where the authors worked
  | 'author'
  | 'venue'        // where it was published
  | 'everyday';    // kid-friendly themes: Language and words

export interface FacetDef {
  id: TagFacet;
  label: string;
  description: string;
}

export interface TagDef {
  /** "<facet>/<slug>", e.g. "concept/self-attention". Never changes once published. */
  id: string;
  facet: TagFacet;
  label: string;
  /** Broader tag in the same facet; searching the parent also finds its children. */
  parent?: string;
  /** Other names people search for: abbreviations, older terms, spellings. */
  aliases?: string[];
  description?: string;
}

export interface TagVocabulary {
  schemaVersion: 1;
  facets: FacetDef[];
  tags: TagDef[];
}

/**
 * Where a tag's claim comes from:
 * - paper: stated in the paper (give `evidence`, a link to the section)
 * - background: well-known context not in the paper, e.g. what it later led to
 * - editorial: our framing for readers, e.g. kid-friendly themes
 */
export type TagBasis = 'paper' | 'background' | 'editorial';

export interface PaperTag {
  /** A TagDef id. If it isn't in the vocabulary yet, `proposed` describes the new tag. */
  tag: string;
  /** 0–1: how central this tag is to the paper. 1 = what the paper is about; 0.3 = mentioned detail. */
  relevance: number;
  basis: TagBasis;
  evidence?: string;
  source: 'ai' | 'editor';
  /** Only approved tags are shown and searchable. AI output starts as suggested. */
  status: 'suggested' | 'approved';
  proposed?: Omit<TagDef, 'id' | 'facet'>;
}

export interface Cover {
  kicker: string;
  headline: { text: string; accent?: string };
  dek: string;
  media: Media;
}

/**
 * A bite-size piece of a paper (one comic strip, story chapter or fact) for home page cards and the
 * swipe feed. Derived from the paper's blocks by scripts/build-index.ts; `href` deep-links into the issue
 * (a path relative to the site base, e.g. "papers/<slug>#<anchor>"; resolve it with appHref).
 */
export interface Moment {
  id: string;
  paper: string;
  kind: 'strip' | 'chapter' | 'fact';
  kicker: string;
  title: string;
  /** Plain text (markup removed), so cards can be links. */
  text: string;
  media?: Media;
  /** Big number for fact cards, e.g. "512". */
  figure?: string;
  provenance?: Provenance;
  href: string;
}

/** Built from all papers by scripts/build-index.ts (queries against the database later). */
export interface SearchIndex {
  schemaVersion: 1;
  /** The paper the home page leads with. */
  featured: string;
  papers: SearchEntry[];
}

export interface SearchEntry {
  slug: string;
  title: string;
  pageTitle: string;
  summary: string;
  authors: string;
  year: number;
  issue: string;
  cover: Cover;
  moments: Moment[];
  tags: { id: string; relevance: number }[];
}

export type MediaType = 'svg' | 'image' | 'video';

export interface Media {
  type: MediaType;
  /** Path relative to mediaBaseUrl, or an absolute URL. */
  src: string;
  width?: number;
  height?: number;
  /** Read by screen readers. Empty for decorative graphics. */
  alt?: string;
  /** Still frame shown while an image or video is paused. */
  poster?: string;
}

/** Keeps made-up teaching numbers visibly apart from real results. */
export type Provenance = 'illustration' | 'evidence';

/** Inline markup allowed in captions: <b> <strong> <i> <em> <a href> <sub> <sup> <br>. */
export type RichText = string;

interface BlockBase {
  id?: string;
  /** If set, the block gets a link in the masthead nav. */
  nav?: string;
}

export interface LeadBlock extends BlockBase {
  type: 'lead';
  kicker: string;
  headline: { text: string; accent?: string };
  deck: string;
  slideshow: { intervalMs?: number; slides: Slide[] };
}

export interface Slide {
  label: string;
  caption: RichText;
  media: Media;
}

export interface StoryBlock extends BlockBase {
  type: 'story';
  kicker: string;
  title: string;
  chapters: Chapter[];
}

export interface Chapter {
  part: string;
  title: string;
  provenance?: Provenance;
  caption: RichText;
  media: Media;
}

export interface ComicBlock extends BlockBase {
  type: 'comic';
  kicker: string;
  title: string;
  deck?: RichText;
  howTo?: RichText;
  strips: Strip[];
}

export interface Strip {
  /** Anchor for deep links (home page cards). Defaults to "<block id>-<n>". */
  id?: string;
  /** Which panel represents the strip on the home page and in the feed (0-based). Defaults to the last one. */
  coverPanel?: number;
  title: string;
  kicker?: string;
  provenance?: Provenance;
  grownUpWords?: string;
  panels: Panel[];
}

export interface Panel {
  caption: RichText;
  media: Media;
}

export interface FactsBlock extends BlockBase {
  type: 'facts';
  kicker: string;
  facts: Fact[];
}

export interface Fact {
  figure: string;
  text: RichText;
  source?: { label: string; url: string };
  media?: Media;
}

export type Block = LeadBlock | StoryBlock | ComicBlock | FactsBlock;
export type BlockType = Block['type'];
