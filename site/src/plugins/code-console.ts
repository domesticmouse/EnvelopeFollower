import type { Element, ElementContent, Root } from 'hast';
import { visit } from 'unist-util-visit';
import { COPY_ICON_DEFS } from '../lib/copy-icons.ts';
import { readClassNames } from './hast-utils.ts';

function extractLanguage(preNode: Element): string | null {
  const dataLang = preNode.properties?.dataLanguage ?? preNode.properties?.['data-language'];
  if (typeof dataLang === 'string' && dataLang.trim().length > 0) {
    return dataLang.trim();
  }

  const codeChild = preNode.children.find(
    (child): child is Element => child.type === 'element' && child.tagName === 'code',
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
 * Rehype plugin that wraps Shiki fenced code blocks (excluding `mermaid`)
 * inside a `.code-console` frame with an in-flow `.code-console-head` bar and
 * an Invoker Commands Copy button (`command="--copy"`).
 */
export function rehypeCodeConsole(): (tree: Root) => void {
  return (tree) => {
    let blockIndex = 0;

    visit(tree, 'element', (node, index, parent) => {
      if (!parent || index === undefined || node.tagName !== 'pre') {
        return;
      }

      if (
        parent.type === 'element' &&
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

      const preClone: Element = {
        ...node,
        properties: {
          ...(node.properties ?? {}),
          id: codeId,
          tabIndex: 0,
        },
      };

      const header: Element = {
        type: 'element',
        tagName: 'div',
        properties: {
          className: ['code-console-head'],
          dataPagefindIgnore: '',
        },
        children: [
          {
            type: 'element',
            tagName: 'span',
            properties: { className: ['code-console-lang'] },
            children: [{ type: 'text', value: lang.toUpperCase() }],
          },
          {
            type: 'element',
            tagName: 'span',
            properties: { className: ['prompt-copy-wrap'] },
            children: [
              {
                type: 'element',
                tagName: 'button',
                properties: {
                  type: 'button',
                  className: ['prompt-copy-btn', 'code-copy-btn'],
                  command: '--copy',
                  commandfor: codeId,
                  ariaLabel: `Copy ${lang} code`,
                },
                children: [
                  ...COPY_ICON_DEFS.map(
                    (icon): ElementContent => ({
                      type: 'element',
                      tagName: 'svg',
                      properties: {
                        className: icon.className.split(' '),
                        viewBox: '0 0 24 24',
                        ariaHidden: 'true',
                        focusable: 'false',
                      },
                      children: [
                        {
                          type: 'element',
                          tagName: 'path',
                          properties: { d: icon.pathD },
                          children: [],
                        },
                      ],
                    }),
                  ),
                  {
                    type: 'element',
                    tagName: 'span',
                    properties: {},
                    children: [{ type: 'text', value: 'Copy' }],
                  },
                ],
              },
              {
                type: 'element',
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

      parent.children[index] = {
        type: 'element',
        tagName: 'div',
        properties: { className: ['code-console'] },
        children: [header, preClone],
      };
    });
  };
}
