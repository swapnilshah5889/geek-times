import type { ComponentType } from 'react';
import type { Block, BlockType } from '../types';
import { ComicBlock } from './ComicBlock';
import { FactsBlock } from './FactsBlock';
import { LeadBlock } from './LeadBlock';
import { StoryBlock } from './StoryBlock';

// One component per block type. To change how a kind of content looks, change its component;
// the data stays the same. Adding a type: extend `Block` in types.ts and register it here.
type Registry = { [K in BlockType]: ComponentType<{ block: Extract<Block, { type: K }> }> };

const BLOCKS: Registry = {
  lead: LeadBlock,
  story: StoryBlock,
  comic: ComicBlock,
  facts: FactsBlock,
};

/** Renders a block, skipping types this build doesn't know so newer data can't break an older page. */
export function BlockView({ block }: { block: Block }) {
  const Component = BLOCKS[block.type] as ComponentType<{ block: Block }> | undefined;
  if (!Component) {
    console.warn('Skipping unknown block type:', block.type);
    return null;
  }
  return <Component block={block} />;
}
