import type { Root } from 'hast';
import { describe, expect, it } from 'vitest';
import { extractText, readClassNames } from '../src/plugins/hast-utils.ts';

describe('hast-utils', () => {
  it('normalizes array and string className values while ignoring empty or invalid entries', () => {
    expect(readClassNames(['language-bash', 'highlight', ''])).toEqual([
      'language-bash',
      'highlight',
    ]);
    expect(readClassNames('  code-console   is-ready  ')).toEqual(['code-console', 'is-ready']);
    expect(readClassNames([42, null, undefined, 'active'])).toEqual(['42', 'active']);
    expect(readClassNames(undefined)).toEqual([]);
    expect(readClassNames(false)).toEqual([]);
  });

  it('extracts plain text recursively from HAST trees and leaf nodes', () => {
    const tree: Root = {
      type: 'root',
      children: [
        {
          type: 'element',
          tagName: 'p',
          properties: {},
          children: [
            { type: 'text', value: 'Run ' },
            {
              type: 'element',
              tagName: 'code',
              properties: { className: ['chip-skill'] },
              children: [{ type: 'text', value: '/wayfinder' }],
            },
            { type: 'text', value: ' now.' },
          ],
        },
      ],
    };

    expect(extractText(tree)).toBe('Run /wayfinder now.');
    expect(extractText({ type: 'comment', value: 'ignored' })).toBe('');
  });
});
