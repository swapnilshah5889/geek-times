import type { Archive } from '../data/load';
import { realPaper, sampleMedia } from '../lib/library';
import type { LibraryStory } from '../types';
import { MediaView } from './MediaView';

/** The picture for a story: the real cover for explained papers, sample art for layout-only ones. */
export function StoryArt({ story, archive }: { story: LibraryStory; archive: Archive }) {
  const paper = realPaper(archive, story);
  const media = paper?.cover.media ?? (story.art ? sampleMedia(story.art) : undefined);
  return media ? <div className="art"><MediaView media={media} /></div> : null;
}

export const SampleTag = ({ story }: { story: LibraryStory }) =>
  story.sample ? <span className="sample-tag">Sample</span> : null;
