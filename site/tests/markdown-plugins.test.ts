import type { Element, Root as HastRoot } from 'hast';
import type { Root as MdastRoot } from 'mdast';
import { describe, expect, it } from 'vitest';
import { rehypeMermaidBlocks } from '../src/plugins/rehype-mermaid.ts';
import { remarkPromoteDoubleDollarMath } from '../src/plugins/remark-double-dollar-math.ts';

describe('remarkPromoteDoubleDollarMath', () => {
  it('promotes single-line $$...$$ inlineMath nodes to math-display while leaving $...$ inline', () => {
    const source = 'Inline $V_{\\text{os}}$ and display $$f_c = 3.39\\text{ Hz}$$ end.';
    const inlineStart = source.indexOf('$V');
    const inlineEnd = inlineStart + '$V_{\\text{os}}$'.length;
    const doubleStart = source.indexOf('$$f_c');
    const doubleEnd = doubleStart + '$$f_c = 3.39\\text{ Hz}$$'.length;

    const tree = {
      type: 'root',
      children: [
        {
          type: 'paragraph',
          children: [
            {
              type: 'inlineMath',
              value: 'V_{\\text{os}}',
              position: { start: { offset: inlineStart }, end: { offset: inlineEnd } },
            },
            {
              type: 'inlineMath',
              value: 'f_c = 3.39\\text{ Hz}',
              position: { start: { offset: doubleStart }, end: { offset: doubleEnd } },
            },
          ],
        },
      ],
    } as unknown as MdastRoot;

    const transform = remarkPromoteDoubleDollarMath();
    expect(transform).toBeTypeOf('function');
    (transform as (tree: MdastRoot, file: { value: string }) => void)(tree, { value: source });

    const paragraph = tree.children[0] as unknown as {
      children: Array<{ data?: { hProperties?: { className?: string[] } } }>;
    };
    expect(paragraph.children[0]?.data?.hProperties?.className).toBeUndefined();
    expect(paragraph.children[1]?.data?.hProperties?.className).toEqual([
      'language-math',
      'math-display',
    ]);
  });

  it('handles empty file value or missing position offsets gracefully', () => {
    const tree = {
      type: 'root',
      children: [
        {
          type: 'paragraph',
          children: [{ type: 'inlineMath', value: 'x' }],
        },
      ],
    } as unknown as MdastRoot;

    const transform = remarkPromoteDoubleDollarMath() as (
      tree: MdastRoot,
      file: { value: string },
    ) => void;
    expect(() => transform(tree, { value: '' })).not.toThrow();
    expect(() => transform(tree, { value: '$$x$$' })).not.toThrow();
  });
});

describe('rehypeMermaidBlocks', () => {
  it('wraps mermaid code fences with data-pagefind-ignore and leaves other fences & MDX JSX intact', () => {
    const tree: HastRoot = {
      type: 'root',
      children: [
        {
          type: 'element',
          tagName: 'pre',
          properties: {},
          children: [
            {
              type: 'element',
              tagName: 'code',
              properties: { className: ['language-mermaid'] },
              children: [{ type: 'text', value: 'flowchart LR\n  J1 --> RV1\n' }],
            },
          ],
        },
        {
          type: 'element',
          tagName: 'pre',
          properties: { dataLanguage: 'bash' },
          children: [
            {
              type: 'element',
              tagName: 'code',
              properties: { className: ['language-bash'] },
              children: [{ type: 'text', value: 'npm test\n' }],
            },
          ],
        },
        {
          type: 'mdxJsxFlowElement',
          name: 'Callout',
          attributes: [],
          children: [],
        } as unknown as Element,
      ],
    };

    const transform = rehypeMermaidBlocks() as (tree: HastRoot) => void;
    transform(tree);

    const figure = tree.children[0] as Element;
    expect(figure.tagName).toBe('figure');
    expect(figure.properties?.className).toEqual(['mermaid-card']);
    expect(figure.properties?.dataMermaidCard).toBe(true);
    expect(figure.properties?.dataPagefindIgnore).toBe(true);

    const scroll = figure.children[0] as Element;
    expect(scroll.tagName).toBe('div');
    expect(scroll.properties?.className).toEqual(['mermaid-scroll']);
    expect(scroll.properties?.tabIndex).toBe(0);
    expect(scroll.properties?.role).toBe('region');

    const pre = scroll.children[0] as Element;
    expect(pre.tagName).toBe('pre');
    expect(pre.properties?.className).toEqual(['mermaid']);
    expect(pre.children[0]).toEqual({ type: 'text', value: 'flowchart LR\n  J1 --> RV1' });

    // Running a second pass must not double-wrap
    transform(tree);
    expect((tree.children[0] as Element).tagName).toBe('figure');
    expect(((tree.children[0] as Element).children[0] as Element).tagName).toBe('div');

    // Non-mermaid pre and MDX JSX element remain untouched
    const bashPre = tree.children[1] as Element;
    expect(bashPre.tagName).toBe('pre');
    expect(bashPre.properties?.dataLanguage).toBe('bash');
    expect((tree.children[2] as unknown as { type: string }).type).toBe('mdxJsxFlowElement');
  });
});
