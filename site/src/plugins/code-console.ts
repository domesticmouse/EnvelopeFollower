import { COPY_ICON_DEFS } from '../lib/copy-icons.ts';
import type { SatteriHastPlugin } from './prompt-chips.ts';

function readClassNames(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.filter((item): item is string => typeof item === 'string');
  }
  if (typeof value === 'string') {
    return value.split(/\s+/).filter(Boolean);
  }
  return [];
}

function extractLanguage(preNode: {
  properties?: Record<string, unknown>;
  children?: readonly { type?: string; tagName?: string; properties?: Record<string, unknown> }[];
}): string | null {
  const dataLang = preNode.properties?.dataLanguage ?? preNode.properties?.['data-language'];
  if (typeof dataLang === 'string' && dataLang.trim().length > 0) {
    return dataLang.trim();
  }

  const codeChild = preNode.children?.find(
    (child) => child.type === 'element' && child.tagName === 'code',
  );
  const codeClasses = readClassNames(codeChild?.properties?.className ?? codeChild?.properties?.class);
  const langClass = codeClasses.find((cls) => cls.startsWith('language-'));
  if (langClass) {
    return langClass.slice('language-'.length);
  }

  const preClasses = readClassNames(preNode.properties?.className ?? preNode.properties?.class);
  if (preClasses.includes('astro-code')) {
    return 'text';
  }

  return null;
}

/**
 * Sätteri HAST plugin that wraps Shiki fenced code blocks (excluding `mermaid`)
 * inside a `.code-console` frame with an in-flow `.code-console-head` bar and
 * an Invoker Commands Copy button (`command="--copy"`).
 */
export function codeConsolePlugin(): SatteriHastPlugin {
  return () => {
    let blockIndex = 0;

    return {
      name: 'code-console',
      element: {
        filter: ['pre'],
        visit(node, ctx) {
          const parent = ctx.parent(node);
          if (
            parent?.type === 'element' &&
            parent.tagName === 'div' &&
            readClassNames(parent.properties?.className ?? parent.properties?.class).includes(
              'code-console',
            )
          ) {
            return;
          }

          const lang = extractLanguage(node);
          if (!lang || lang.toLowerCase() === 'mermaid') {
            return;
          }

          const existingId = node.properties?.id;
          const codeId =
            typeof existingId === 'string' && existingId.length > 0
              ? existingId
              : `code-well-${++blockIndex}`;

          const preClone = {
            ...node,
            properties: {
              ...(node.properties ?? {}),
              id: codeId,
              tabindex: '0',
            },
          };

          const header = {
            type: 'element' as const,
            tagName: 'div',
            properties: {
              className: ['code-console-head'],
              dataPagefindIgnore: '',
            },
            children: [
              {
                type: 'element' as const,
                tagName: 'span',
                properties: { className: ['code-console-lang'] },
                children: [{ type: 'text' as const, value: lang.toUpperCase() }],
              },
              {
                type: 'element' as const,
                tagName: 'span',
                properties: { className: ['prompt-copy-wrap'] },
                children: [
                  {
                    type: 'element' as const,
                    tagName: 'button',
                    properties: {
                      type: 'button',
                      className: ['prompt-copy-btn', 'code-copy-btn'],
                      command: '--copy',
                      commandfor: codeId,
                      ariaLabel: `Copy ${lang} code`,
                    },
                    children: [
                      ...COPY_ICON_DEFS.map((icon) => ({
                        type: 'element' as const,
                        tagName: 'svg',
                        properties: {
                          className: icon.className.split(' '),
                          viewBox: '0 0 24 24',
                          ariaHidden: 'true',
                          focusable: 'false',
                        },
                        children: [
                          {
                            type: 'element' as const,
                            tagName: 'path',
                            properties: { d: icon.pathD },
                            children: [],
                          },
                        ],
                      })),
                      {
                        type: 'element' as const,
                        tagName: 'span',
                        properties: {},
                        children: [{ type: 'text' as const, value: 'Copy' }],
                      },
                    ],
                  },
                  {
                    type: 'element' as const,
                    tagName: 'span',
                    properties: {
                      className: ['prompt-copy-tip'],
                      role: 'status',
                    },
                    children: [],
                  },
                ],
              },
            ],
          };

          ctx.replaceNode(node, {
            type: 'element',
            tagName: 'div',
            properties: { className: ['code-console'] },
            children: [header, preClone],
          });
        },
      },
    };
  };
}
