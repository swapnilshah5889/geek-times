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
  issue: { volume: string; number: string; desk: string };
  paper: { title: string; authors: string; year: number; url: string };
  blocks: Block[];
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
