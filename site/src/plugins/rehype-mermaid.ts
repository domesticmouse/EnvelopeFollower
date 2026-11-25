import type { Element, ElementContent, Properties, Root, RootContent } from 'hast';
import { visit } from 'unist-util-visit';

function getClasses(el: Element): string[] {
  const raw: unknown = el.properties?.className;
  if (Array.isArray(raw)) {
    return raw.map((item) => String(item));
  }
  if (typeof raw === 'string') {
    return raw.split(/\s+/).filter(Boolean);
  }
  return [];
}

function hasClass(el: Element, className: string): boolean {
  return getClasses(el).includes(className);
}

function extractText(node: Root | RootContent): string {
  if (node.type === 'text') {
    return node.value;
  }
  if ('children' in node && Array.isArray(node.children)) {
    return node.children.map((child) => extractText(child)).join('');
  }
  return '';
}

function h(tagName: string, properties: Properties, children: ElementContent[]): Element {
  return {
    type: 'element',
    tagName,
    properties,
    children,
  };
}

function isMermaidPre(node: Element): { isMermaid: boolean; codeChild: Element | undefined } {
  if (node.tagName !== 'pre') {
    return { isMermaid: false, codeChild: undefined };
  }
  const codeChild = node.children.find(
    (child): child is Element => child.type === 'element' && child.tagName === 'code',
  );
  const dataLang =
    typeof node.properties?.dataLanguage === 'string' ? node.properties.dataLanguage : undefined;
  const classLang = codeChild
    ? getClasses(codeChild)
        .find((cls) => cls.startsWith('language-'))
        ?.slice('language-'.length)
    : undefined;
  const lang = dataLang ?? classLang ?? (hasClass(node, 'mermaid') ? 'mermaid' : undefined);
  return { isMermaid: lang === 'mermaid', codeChild };
}

/**
 * Wrap Shiki-excluded `mermaid` code fences in a `data-pagefind-ignore` scroll container
 * with `<pre class="mermaid">` ready for lazy client-side SVG hydration, without touching MDX JSX.
 */
export function rehypeMermaidBlocks(): (tree: Root) => void {
  return (tree) => {
    visit(tree, 'element', (node, index, parent) => {
      if (!parent || index === undefined) {
        return;
      }
      const { isMermaid, codeChild } = isMermaidPre(node);
      if (!isMermaid) {
        return;
      }
      if (parent.type === 'element' && hasClass(parent, 'mermaid-scroll')) {
        return;
      }

      const diagramSource = extractText(codeChild ?? node).replace(/\n$/, '');
      parent.children[index] = h(
        'figure',
        { className: ['mermaid-card'], dataMermaidCard: true, dataPagefindIgnore: true },
        [
          h(
            'div',
            {
              className: ['mermaid-scroll'],
              tabIndex: 0,
              role: 'region',
              ariaLabel: 'Signal flow diagram',
            },
            [h('pre', { className: ['mermaid'] }, [{ type: 'text', value: diagramSource }])],
          ),
        ],
      );
    });
  };
}
