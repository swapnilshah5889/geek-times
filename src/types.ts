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
  /** Scroll-stopper for the front-page tile; merged into the cover. */
  hook?: CoverHook;
  /** The science desk the story belongs to, e.g. "Machine learning". Stories never name an issue or a date of ours. */
  desk: string;
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
  hook?: CoverHook;
}

/**
 * The scroll-stopper on a paper's front-page tile. Written by the converter, and every line must stay
 * true: a curiosity gap is fine, a false promise is not (see skills/explain-source, "Cover hook").
 */
export interface CoverHook {
  /** Loud two-or-three-word sticker, e.g. "Wait, what?". */
  sticker: string;
  /** One question or surprising claim in kid words that the paper answers. */
  teaser: string;
  /** Button text, a promise of the payoff, e.g. "Crack the bat puzzle". */
  cta: string;
  /** Minutes to read the whole story. */
  readMinutes: number;
  /** One real number from the paper's facts, shown as a badge. */
  stat?: { figure: string; text: string };
  /** The cover art flips between these (the first should match `cover.media`); `tag` is the shout on each. */
  frames?: { media: Media; tag: string }[];
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
  claim?: ClaimKind;
  /** Where in the paper a fact comes from, e.g. "Paper §3.1". */
  sourceLabel?: string;
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
  desk: string;
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
export type Provenance = 'illustration' | 'evidence' | 'model_design';

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

/** What kind of claim a number is: how the thing was built, or what the tests found. Never both. */
export type ClaimKind = 'illustration' | 'model_design' | 'measured_result';

export interface Fact {
  figure: string;
  claim?: ClaimKind;
  text: RichText;
  source?: { label: string; url: string };
  media?: Media;
}

export type Block = LeadBlock | StoryBlock | ComicBlock | FactsBlock;
export type BlockType = Block['type'];

// ---- Library: the editorial layer around papers (front page, issues, companies, map) ----

/** Where a field's cloud sits on the 800 × 600 map. */
export interface LibraryField {
  id: string; label: string; color: string;
  cluster: { cx: number; cy: number; rx: number; ry: number; labelX: number; labelY: number };
}
export type SampleArtKind = 'dna' | 'protein' | 'waves' | 'stairs' | 'particle' | 'mold';
export type StoryRole = 'lead' | 'feature' | 'brief' | 'vault' | 'real_world';

export interface LibraryStory {
  id: string;
  /** True for the one story that has a real page; everything else is layout-only and labelled Sample. */
  sample: boolean;
  real?: boolean;
  headline: string;
  accent?: string;
  dek: string;
  desk: string;
  fields: string[];
  role: StoryRole;
  kind: 'paper' | 'blog' | 'classic';
  title: string;
  authors: string;
  year: number;
  trust?: 'peer_reviewed' | 'preprint' | 'company_reported';
  art?: SampleArtKind;
  minutes: number;
  note?: string;
  company?: string;
  builtOn?: string;
  vaultNote?: string;
}

export interface LibraryIssue {
  id: string;
  volume: string;
  number: string;
  title: string;
  color: string;
  sample: boolean;
  published?: string;
  stories?: string[];
  covers?: string;
  classics?: number;
}

export interface LibraryCompany {
  id: string;
  name: string;
  sector: string;
  blurb: string;
  postsFollowed: number;
  posts: string[];
  builtOn: string[];
  coming: string[];
}

export interface Storyline {
  id: string;
  title: string;
  sample: boolean;
  steps: { year: string; label: string; current?: boolean }[];
}

export interface GraphNode {
  id: string;
  title: string;
  authors: string;
  year: number;
  field: string;
  type: 'paper' | 'blog';
  x: number;
  y: number;
  /** Story id when we have explained it. */
  story?: string;
  /** Short label for the map. */
  short?: string;
  blurb?: string;
}

export interface GraphRelation {
  from: string;
  to: string;
  kind: 'builds_on' | 'improves_on' | 'uses_method';
  note: string;
  cited?: boolean;
  crossField?: boolean;
}

export interface Library {
  schemaVersion: 1;
  fields: LibraryField[];
  stories: LibraryStory[];
  front: {
    lead: string; aside: string[]; more: string[];
    topics: { field: string; label: string; stories: string[] }[];
    real: string[]; storylines: string[]; vault: string;
    onThisDay: { year: string; text: string; story: string };
  };
  issues: LibraryIssue[];
  companies: LibraryCompany[];
  storylines: Storyline[];
  nodes: GraphNode[];
  relations: GraphRelation[];
}
