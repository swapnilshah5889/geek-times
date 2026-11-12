import { useHead } from '../components/head';
import { Crumbs, SitePage } from '../components/SitePage';
import type { Archive } from '../data/load';
import { homeHref } from '../lib/routes';

// The map of ideas stays closed until its relations are verified (V1 content rule; decisions 15 and 24).
// Until then it renders no nodes, links, counts or filters, only an honest empty state.
export function MapPage({ archive }: { archive: Archive }) {
  const { site } = archive;
  useHead({
    title: `The map of ideas — ${site.name}`,
    description: 'The map of ideas opens once verified relations are mapped.',
    type: 'website',
  });
  return (
    <SitePage archive={archive} title="The map of ideas" active="explore" motion={false}>
      <Crumbs items={['The map of ideas']} />
      <h1>The map of ideas</h1>
      <section className="f-section">
        <p className="empty">Explore map opens once verified relations are mapped.</p>
        <p><a className="f-more" href={homeHref()}>Back to the front page →</a></p>
      </section>
    </SitePage>
  );
}
