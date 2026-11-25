import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { detectContentFeatures } from '../src/lib/content-features.ts';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const STAGES_DIR = path.join(SITE_DIR, 'src/content/tutorial/stages');

function readMdx(filename: string): { frontmatterRaw: string; body: string } {
  const full = fs.readFileSync(path.join(STAGES_DIR, filename), 'utf8');
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(full);
  if (!match) {
    throw new Error(`Missing YAML frontmatter in ${filename}`);
  }
  return { frontmatterRaw: match[1] ?? '', body: match[2] ?? '' };
}

function stripCodeFences(body: string): string {
  return body.replace(/^```[\s\S]*?^```\s*$/gm, '');
}

describe('Stage 6 MDX migration contract', () => {
  it('migrates 06-front-panel-and-artwork.mdx with editorial blockquote, two FigureGrids, Mermaid, and canonical links', () => {
    const { frontmatterRaw, body } = readMdx('06-front-panel-and-artwork.mdx');

    expect(frontmatterRaw).toContain('order: 6');
    expect(frontmatterRaw).toContain('section: "hardware"');
    expect(frontmatterRaw).toContain('badge: "06"');
    expect(frontmatterRaw).toContain('stage: 6');

    expect(stripCodeFences(body)).not.toMatch(/^#\s+/m);
    expect(detectContentFeatures(body)).toEqual({ hasMath: false, hasMermaid: true });

    // Editorial blockquote preserved, not converted to PromptBlock
    expect(body).toMatch(/^>\s+\*\(The `switch_submini` matcher/m);
    expect(body).not.toContain('<PromptBlock');

    // Warning callout & two 2-column unframed FigureGrids
    expect(body).toContain('<Callout type="warning"');
    expect(body.match(/<FigureGrid cols=\{2\}>/g)).toHaveLength(2);
    expect(body).toContain('panel_preview_clean.png');
    expect(body).toContain('panel_preview_keepouts.png');
    expect(body).toContain('panel_front.png');
    expect(body).toContain('panel_back.png');
    expect(body.match(/framed=\{false\}/g)).toHaveLength(4);

    // Internal links rewritten to canonical /EnvelopeFollower/.../ paths
    expect(body).toContain('/EnvelopeFollower/stages/04-skidl-and-schematic/');
    expect(body).toContain('/EnvelopeFollower/stages/07-fabrication-checklists-and-patches/');
    expect(body).not.toMatch(/\]\([^)]*(?:stage-\d|reference\/)[^)]*\.md/);
  });
});

describe('Stage 7 MDX migration contract', () => {
  it('migrates 07-fabrication-checklists-and-patches.mdx with safe <img src>, framed checklist figures, Mermaid, and canonical links', () => {
    const { frontmatterRaw, body } = readMdx('07-fabrication-checklists-and-patches.mdx');

    expect(frontmatterRaw).toContain('order: 7');
    expect(frontmatterRaw).toContain('section: "hardware"');
    expect(frontmatterRaw).toContain('badge: "07"');
    expect(frontmatterRaw).toContain('stage: 7');

    expect(stripCodeFences(body)).not.toMatch(/^#\s+/m);
    expect(detectContentFeatures(body)).toEqual({ hasMath: false, hasMermaid: true });

    // Prose `<img src>` remains safely backticked
    expect(body).toContain('`<img src>`');

    // Warning and note callouts
    expect(body).toContain('<Callout type="warning"');
    expect(body).toContain('<Callout type="note"');

    // 3 framed checklist figures (2 in FigureGrid + 1 standalone with maxWidth={520})
    expect(body).toContain('<FigureGrid cols={2}>');
    expect(body).toContain('checklists/pcba_alignment_U1.png');
    expect(body).toContain('checklists/hand_assembly_J_PWR.png');
    expect(body).toContain('checklists/board_bringup_00_test_point_map.png');
    expect(body.match(/framed=\{true\}/g)).toHaveLength(3);
    expect(body).toContain('maxWidth={520}');

    // Internal links rewritten to canonical /EnvelopeFollower/.../ paths including exact github-slugger anchor
    expect(body).toContain(
      '/EnvelopeFollower/stages/04-skidl-and-schematic/#step-43-anatomy-of-envelope_followerpy--multi-layer-netlist-verification',
    );
    expect(body).toContain('/EnvelopeFollower/stages/08-wayfinder-site-planning/');
    expect(body).toContain('/EnvelopeFollower/appendix/netlist-and-bom/');
    expect(body).toContain('/EnvelopeFollower/appendix/engineering-sign-off-checklist/');
    expect(body).not.toMatch(/\]\([^)]*(?:stage-\d|reference\/)[^)]*\.md/);
  });
});
