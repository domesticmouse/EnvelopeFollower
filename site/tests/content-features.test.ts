import { describe, expect, it } from 'vitest';
import { detectContentFeatures, hasMath, hasMermaid } from '../src/lib/content-features.ts';

describe('content feature detection (hasMath / hasMermaid)', () => {
  it('detects inline $...$ and display $$...$$ math in prose', () => {
    expect(hasMath('Inline voltage $V_{\\text{os}}$ threshold.')).toBe(true);
    expect(hasMath('Accepts digits like $0\\,\\text{V}$ and $10\\times$.')).toBe(true);
    expect(
      hasMath('$$\nf_{\\text{c,in}} = \\frac{1}{2\\pi \\cdot R \\cdot C}\n$$'),
    ).toBe(true);
    expect(hasMath('Single-line display $$x = a + b$$ in paragraph.')).toBe(true);
  });

  it('ignores currency and template variables inside inline code or fenced code blocks', () => {
    const appendixLike = [
      '| **PCBA** | `14` Basic (`$0` fees) + `3` Extended (`$9` fees) |',
      '',
      'Register `${KIPRJMOD}/footprints` in `fp-lib-table`.',
      '',
      '```bash',
      'echo "$HOME" && echo "$10"',
      '```',
      '',
      'Price is `$4` per board, or $5 in prose without a closing dollar.',
    ].join('\n');

    expect(hasMath(appendixLike)).toBe(false);
  });

  it('detects fenced mermaid blocks and ignores non-mermaid fences', () => {
    expect(hasMermaid('```mermaid\nflowchart LR\n  A --> B\n```')).toBe(true);
    expect(hasMermaid('```bash\necho "mermaid"\n```')).toBe(false);
    expect(hasMermaid('Use `mermaid` for diagrams.')).toBe(false);
  });

  it('ignores ```mermaid mentioned inside a non-mermaid fenced block', () => {
    const body = [
      '````markdown',
      '```mermaid',
      'flowchart TD',
      '```',
      '````',
    ].join('\n');

    expect(hasMermaid(body)).toBe(false);
  });

  it('returns combined feature flags via detectContentFeatures', () => {
    const optionalBody = [
      'Inline $V_{\\text{os}}$ and display:',
      '$$',
      'f_c = 3.39\\text{ Hz}',
      '$$',
      '',
      '```mermaid',
      'flowchart LR',
      '  J1 --> RV1',
      '```',
    ].join('\n');

    expect(detectContentFeatures(optionalBody)).toEqual({
      hasMath: true,
      hasMermaid: true,
    });
    expect(detectContentFeatures('Plain text checklist - [x] done')).toEqual({
      hasMath: false,
      hasMermaid: false,
    });
  });
});
