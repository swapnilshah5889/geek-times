import { useMemo } from 'react';
import { searchHref, tagLookup } from '../lib/tags';
import type { PaperTag, TagDef, TagVocabulary } from '../types';

/** Below this relevance a tag is a detail; those sit behind "more tags". */
const MAIN = 0.5;

/** "Filed under": a story's approved tags grouped by facet, each linking to search. `kind` names the source in the copy. */
export function TagShelf({ tags, vocab, kind = 'paper' }: { tags: PaperTag[]; vocab: TagVocabulary; kind?: 'paper' | 'blog' }) {
  const where = kind === 'blog' ? 'post' : 'paper';
  const groups = useMemo(() => {
    const lookup = tagLookup(vocab);
    const shown = tags
      .filter(t => t.status === 'approved')
      .map(t => ({ ...t, def: lookup.get(t.tag) }))
      .filter((t): t is PaperTag & { def: TagDef } => Boolean(t.def))
      .sort((a, b) => b.relevance - a.relevance);
    return vocab.facets
      .map(facet => ({ facet, items: shown.filter(t => t.def.facet === facet.id) }))
      .filter(g => g.items.length);
  }, [tags, vocab]);

  if (!groups.length) return null;
  const chip = (t: PaperTag & { def: TagDef }) => (
    <a key={t.tag} className={`tag tag-${t.basis}`} href={searchHref({ tags: [t.tag] })}
      title={t.basis === 'paper' ? `Stated in the ${where}` : t.basis === 'background' ? `Background: not in the ${where} itself` : 'Our reading guide'}>
      {t.def.label}
    </a>
  );

  return (
    <section className="tag-shelf" id="tags" aria-labelledby="tags-title">
      <div className="label" id="tags-title">Filed under &nbsp; / &nbsp; Tap a tag to find more stories like this</div>
      <dl>
        {groups.map(({ facet, items }) => {
          const main = items.filter(t => t.relevance >= MAIN);
          const more = items.filter(t => t.relevance < MAIN);
          return (
            <div className="tag-group" key={facet.id}>
              <dt>{facet.label}</dt>
              <dd>
                {main.map(chip)}
                {more.length > 0 && (
                  main.length ? <details><summary>+{more.length} more</summary>{more.map(chip)}</details> : more.map(chip)
                )}
              </dd>
            </div>
          );
        })}
      </dl>
      <p className="tag-key">
        <span className="tag tag-paper">In the {where}</span>
        <span className="tag tag-background">Background</span>
        <span className="tag tag-editorial">Reading guide</span>
      </p>
    </section>
  );
}
