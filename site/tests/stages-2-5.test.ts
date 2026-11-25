// @vitest-environment node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { detectContentFeatures } from '../src/lib/content-features.ts';
import { tutorialSchema } from '../src/lib/tutorial-schema.ts';

const STAGES_DIR = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../src/content/tutorial/stages',
);

const AVOIDED_TERMS_RE =
  /\b(?:codelab|docs site|documentation portal|module website|base sketch|original diagram|reference schematic|reference section|reference docs|technical references|master build checklist|fabrication checklist|prompt card|blockquote prompt|raw prompt|motivating prompt|conversation log|chat log|prompt log|build session|tracker log|github history|issue trail|decision log|context anchor|agent readme|workspace index|github front door|compact readme|landing readme)\b/i;

function splitMdx(fileName: string): { frontmatter: Record<string, unknown>; body: string } {
  const raw = fs.readFileSync(path.join(STAGES_DIR, fileName), 'utf8');
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(raw);
  if (!match) {
    throw new Error(`Missing YAML frontmatter in ${fileName}`);
  }
  const fmLines = match[1]!.split(/\r?\n/);
  const frontmatter: Record<string, unknown> = {};
  let currentHeroMeta: Array<{ label: string; value: string }> | null = null;
  let pendingItem: Partial<{ label: string; value: string }> | null = null;

  for (const line of fmLines) {
    if (!line.trim()) continue;
    if (line.startsWith('heroMeta:')) {
      currentHeroMeta = [];
      frontmatter.heroMeta = currentHeroMeta;
      continue;
    }
    if (currentHeroMeta && /^\s*-\s+label:\s*(.+)$/.test(line)) {
      const val = line.replace(/^\s*-\s+label:\s*/, '').trim();
      pendingItem = { label: unquote(val) };
      currentHeroMeta.push(pendingItem as { label: string; value: string });
      continue;
    }
    if (currentHeroMeta && pendingItem && /^\s+value:\s*(.+)$/.test(line)) {
      const val = line.replace(/^\s+value:\s*/, '').trim();
      pendingItem.value = unquote(val);
      pendingItem = null;
      continue;
    }
    currentHeroMeta = null;
    const kv = /^([A-Za-z0-9_]+):\s*(.+)$/.exec(line);
    if (kv) {
      const key = kv[1]!;
      const rawVal = kv[2]!.trim();
      if (/^\d+$/.test(rawVal) && !rawVal.startsWith('"') && !rawVal.startsWith("'")) {
        frontmatter[key] = Number(rawVal);
      } else {
        frontmatter[key] = unquote(rawVal);
      }
    }
  }

  return { frontmatter, body: match[2]! };
}

function unquote(value: string): string {
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function stripFencedCodeBlocks(body: string): string {
  return body.replace(/^```[\s\S]*?^```\s*$/gm, '');
}

describe('Stages 2-5 MDX migration contracts', () => {
  it('Stage 2 matches Zod frontmatter, PromptBlock, KaTeX, Figure, and link contracts', () => {
    const { frontmatter, body } = splitMdx('02-sketch-extraction-and-critique.mdx');
    const parsed = tutorialSchema.parse(frontmatter);

    expect(parsed.order).toBe(2);
    expect(parsed.section).toBe('hardware');
    expect(parsed.badge).toBe('02');
    expect(parsed.stage).toBe(2);
    expect(parsed.heroMeta?.length).toBeGreaterThanOrEqual(2);
    expect(stripFencedCodeBlocks(body)).not.toMatch(/^#\s+/m);
    expect(detectContentFeatures(body)).toEqual({ hasMath: true, hasMermaid: false });
    expect(body.match(/<PromptBlock\b/g)).toHaveLength(2);
    expect(body).toContain("EnvelopeFollower.webp'");
    expect(body).toContain('<Figure');
    expect(body).not.toMatch(/\]\((?!https?:\/\/)[^)]*\.md(?:#[^)]*)?\)/);
    expect(body).not.toMatch(AVOIDED_TERMS_RE);
  });

  it('Stage 3 matches Zod frontmatter, PromptBlock, PromptGroup, KaTeX, Mermaid, and link contracts', () => {
    const { frontmatter, body } = splitMdx('03-design-spec-and-dft.mdx');
    const parsed = tutorialSchema.parse(frontmatter);

    expect(parsed.order).toBe(3);
    expect(parsed.section).toBe('hardware');
    expect(parsed.badge).toBe('03');
    expect(parsed.stage).toBe(3);
    expect(parsed.heroMeta?.length).toBeGreaterThanOrEqual(2);
    expect(stripFencedCodeBlocks(body)).not.toMatch(/^#\s+/m);
    expect(detectContentFeatures(body)).toEqual({ hasMath: true, hasMermaid: true });
    expect(body.match(/<PromptBlock\b/g)).toHaveLength(3);
    expect(body.match(/<PromptGroup\b/g)).toHaveLength(1);
    expect(body).toContain('turn={1}');
    expect(body).toContain('turn={2}');
    expect(body).not.toMatch(/\]\((?!https?:\/\/)[^)]*\.md(?:#[^)]*)?\)/);
    expect(body).not.toMatch(AVOIDED_TERMS_RE);
  });

  it('Stage 4 matches Zod frontmatter, PromptBlock, PromptGroup, Disclosure, Figure, no KaTeX/Mermaid, and link contracts', () => {
    const { frontmatter, body } = splitMdx('04-skidl-and-schematic.mdx');
    const parsed = tutorialSchema.parse(frontmatter);

    expect(parsed.order).toBe(4);
    expect(parsed.section).toBe('hardware');
    expect(parsed.badge).toBe('04');
    expect(parsed.stage).toBe(4);
    expect(parsed.heroMeta?.length).toBeGreaterThanOrEqual(2);
    expect(stripFencedCodeBlocks(body)).not.toMatch(/^#\s+/m);
    expect(detectContentFeatures(body)).toEqual({ hasMath: false, hasMermaid: false });
    expect(body.match(/<PromptBlock\b/g)).toHaveLength(3);
    expect(body.match(/<PromptGroup\b/g)).toHaveLength(1);
    expect(body).toContain('turn={1}');
    expect(body).toContain('turn={2}');
    expect(body).toContain('<Disclosure');
    expect(body).toContain("schematic.png'");
    expect(body).toContain('<Figure');
    expect(body).not.toMatch(/\]\((?!https?:\/\/)[^)]*\.md(?:#[^)]*)?\)/);
    expect(body).not.toMatch(AVOIDED_TERMS_RE);
  });

  it('Stage 5 matches Zod frontmatter, PromptBlock, PromptGroup, FigureGrid, no KaTeX/Mermaid, and link contracts', () => {
    const { frontmatter, body } = splitMdx('05-main-pcb-and-silkscreen.mdx');
    const parsed = tutorialSchema.parse(frontmatter);

    expect(parsed.order).toBe(5);
    expect(parsed.section).toBe('hardware');
    expect(parsed.badge).toBe('05');
    expect(parsed.stage).toBe(5);
    expect(parsed.heroMeta?.length).toBeGreaterThanOrEqual(2);
    expect(stripFencedCodeBlocks(body)).not.toMatch(/^#\s+/m);
    expect(detectContentFeatures(body)).toEqual({ hasMath: false, hasMermaid: false });
    expect(body.match(/<PromptBlock\b/g)).toHaveLength(3);
    expect(body.match(/<PromptGroup\b/g)).toHaveLength(1);
    expect(body).toContain('turn={1}');
    expect(body).toContain('turn={2}');
    expect(body).toContain('<FigureGrid cols={2}>');
    expect(body).toContain("pcb_front.png'");
    expect(body).toContain("pcb_back.png'");
    expect(body).toContain('maxWidth={240}');
    expect(body).not.toMatch(/\]\((?!https?:\/\/)[^)]*\.md(?:#[^)]*)?\)/);
    expect(body).not.toMatch(AVOIDED_TERMS_RE);
  });
});
