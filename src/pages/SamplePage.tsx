import { FamilyTree } from '../components/FamilyTree';
import { SampleTag, StoryArt } from '../components/library';
import { Crumbs, SitePage } from '../components/SitePage';
import type { Archive } from '../data/load';
import { byline, fieldOf, headlineOf, roleLabel, storyById, trustLabel } from '../lib/library';
import { paperHref } from '../lib/routes';
import { appHref } from '../lib/routes';

// A story the library lists but nobody has written yet. It stays a labelled placeholder: no invented findings.
export function SamplePage({ archive, slug }: { archive: Archive; slug: string }) {
  const { library } = archive;
  const story = storyById(library, slug);
  if (!story) return null;
  const field = fieldOf(library, story.fields[0]);
  const node = library.nodes.find(n => n.story === story.id);
  return (
    <SitePage archive={archive} title={story.headline} active={story.role === 'real_world' ? 'real' : undefined}
      meta={[story.desk, story.year ? `Paper from ${story.year}` : 'Engineering blog']} motion={false}>
      <Crumbs items={[
        { href: appHref(''), label: 'Front page' },
        { href: appHref(''), label: field?.label ?? story.desk }, story.headline]} />
      <article className="sp">
        <div className="sp-art"><StoryArt story={story} archive={archive} /></div>
        <div className="sp-body">
          <span className="label">{roleLabel[story.role]} · {story.desk} <SampleTag story={story} /></span>
          <h1>{headlineOf(story)}</h1>
          <p className="f-lead-dek">{story.dek}</p>
          <p className="byline"><b>{byline(story)}</b>{story.trust && <> · <span className="f-trust">{trustLabel(story.trust)}</span></>}</p>
          <p className="sp-note"><b className="label">Sample story</b> This page shows where the story will live. It has not been written or fact-checked yet, so it has no findings or numbers. See <a href={paperHref(archive.library.front.lead)}>the finished example</a> to know what a full story looks like.</p>
        </div>
      </article>
      {node && <FamilyTree archive={archive} nodeId={node.id} />}
    </SitePage>
  );
}
