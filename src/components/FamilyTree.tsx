import type { Archive } from '../data/load';

// "Papers before and after this one" stays closed until enough relations are verified (decisions 15 and 24).
// Until then it renders an honest empty state only: no demo nodes, links, badges or sample copy.
export function FamilyTree(_props: { archive: Archive; nodeId: string }) {
  return (
    <section id="tree" className="ft">
      <p className="empty">Family tree opens once enough verified relations are mapped.</p>
    </section>
  );
}
