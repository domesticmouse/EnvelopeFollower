import type { Element, Root, RootContent } from 'hast';
import { extractText, readClassNames } from './hast-utils.ts';

export type PromptChipClass = 'chip-skill' | 'chip-file';

const SKILL_CHIP_PATTERN = /^\/[a-z0-9-]+$/i;
const FILE_CHIP_PATTERN = /^@\[[^\]]+\]$/;

/** Classify inline `<code>` text inside `<PromptBlock>` into skill or file chip classes. */
export function classifyPromptChip(text: string): PromptChipClass | null {
  const trimmed = text.trim();
  if (!trimmed) {
    return null;
  }
  if (SKILL_CHIP_PATTERN.test(trimmed)) {
    return 'chip-skill';
  }
  if (FILE_CHIP_PATTERN.test(trimmed)) {
    return 'chip-file';
  }
  return null;
}

interface MdxJsxLike {
  type?: string;
  name?: string;
  children?: RootContent[];
}

function walkHast(
  node: Root | RootContent,
  insidePromptBlock: boolean,
  insidePre: boolean,
): void {
  const mdxNode = node as unknown as MdxJsxLike;
  const isPromptBlock =
    (mdxNode.type === 'mdxJsxFlowElement' || mdxNode.type === 'mdxJsxTextElement') &&
    mdxNode.name === 'PromptBlock';
  const nextPromptBlock = insidePromptBlock || isPromptBlock;
  const nextPre =
    insidePre || (node.type === 'element' && (node as Element).tagName === 'pre');

  if (
    node.type === 'element' &&
    node.tagName === 'code' &&
    nextPromptBlock &&
    !nextPre
  ) {
    const chipClass = classifyPromptChip(extractText(node));
    if (chipClass) {
      const existing = readClassNames(node.properties?.className ?? node.properties?.class);
      if (!existing.includes(chipClass)) {
        node.properties = {
          ...(node.properties ?? {}),
          className: [...existing, chipClass],
        };
      }
    }
  }

  if ('children' in node && Array.isArray(node.children)) {
    for (const child of node.children as RootContent[]) {
      walkHast(child, nextPromptBlock, nextPre);
    }
  }
}

/**
 * Rehype plugin that styles `/skill` and `@[file]` inline `<code>` elements
 * inside `<PromptBlock>` MDX JSX nodes without modifying their copied text content.
 */
export function rehypePromptChips(): (tree: Root) => void {
  return (tree) => {
    walkHast(tree, false, false);
  };
}
