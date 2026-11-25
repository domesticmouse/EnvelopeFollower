import type { SatteriProcessorOptions } from '@astrojs/markdown-satteri';

export type PromptChipClass = 'chip-skill' | 'chip-file';
export type SatteriHastPlugin = NonNullable<SatteriProcessorOptions['hastPlugins']>[number];

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

function normalizeClassList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.filter((item): item is string => typeof item === 'string' && item.length > 0);
  }
  if (typeof value === 'string') {
    return value.split(/\s+/).filter(Boolean);
  }
  return [];
}

/**
 * Sätteri HAST plugin that styles `/skill` and `@[file]` inline `<code>` elements
 * inside `<PromptBlock>` MDX JSX nodes without modifying their copied text content.
 */
export function promptChipsPlugin(): SatteriHastPlugin {
  return {
    name: 'prompt-chips',
    element: {
      filter: ['code'],
      visit(node, ctx) {
        let ancestor: ReturnType<typeof ctx.parent> | undefined = ctx.parent(node);
        let insidePre = false;
        let insidePromptBlock = false;

        while (ancestor) {
          if (ancestor.type === 'element' && ancestor.tagName === 'pre') {
            insidePre = true;
            break;
          }
          if (
            (ancestor.type === 'mdxJsxFlowElement' || ancestor.type === 'mdxJsxTextElement') &&
            ancestor.name === 'PromptBlock'
          ) {
            insidePromptBlock = true;
            break;
          }
          ancestor = ctx.parent(ancestor);
        }

        if (!insidePromptBlock || insidePre) {
          return;
        }

        const chipClass = classifyPromptChip(ctx.textContent(node));
        if (!chipClass) {
          return;
        }

        const existing = normalizeClassList(node.properties?.className ?? node.properties?.class);
        if (!existing.includes(chipClass)) {
          ctx.setProperty(node, 'className', [...existing, chipClass]);
        }
      },
    },
  };
}
