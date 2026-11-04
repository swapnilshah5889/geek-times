import { FamilyTree } from '../components/FamilyTree';
import { SampleTag, StoryArt } from '../components/library';
import { Crumbs, SitePage } from '../components/SitePage';
import type { Archive } from '../data/load';
import { byline, fieldOf, headlineOf, issueById, roleLabel, storyById, trustLabel } from '../lib/library';
import { issueHref, paperHref } from '../lib/routes';
import { appHref } from '../lib/routes';

// A story the library lists but nobody has written yet. It stays a labelled placeholder: no invented findings.
export function SamplePage({ archive, slug }: { archive: Archive; slug: string }) {
  const { library } = archive;
  const story = storyById(library, slug);
  if (!story) return null;
  const issue = story.issue ? issueById(library, story.issue) : undefined;
  const field = fieldOf(library, story.fields[0]);
  const node = library.nodes.find(n => n.story === story.id);
  return (
    <SitePage archive={archive} title={story.headline} active={story.role === 'real_world' ? 'real' : undefined}>
      <Crumbs items={[
        issue ? { href: issueHref(issue.id), label: `Vol. ${issue.volume} · Issue ${issue.number}` } : { href: appHref(''), label: 'Front page' },
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
