// @vitest-environment node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const STYLES_DIR = path.join(SITE_DIR, 'src', 'styles');

function readStylesheet(filename: string): string {
  return fs.readFileSync(path.join(STYLES_DIR, filename), 'utf8');
}

function extractRootBlock(css: string): string {
  const match = css.match(/:root\s*\{([\s\S]*?)\}/);
  if (!match) {
    throw new Error('Could not find :root block');
  }
  return match[1];
}

function extractPrintRootBlock(css: string): string {
  const printIdx = css.indexOf('@media print');
  if (printIdx === -1) {
    throw new Error('Could not find @media print block');
  }
  const printSlice = css.slice(printIdx);
  const match = printSlice.match(/:root,\s*html,\s*body\s*\{([\s\S]*?)\}/);
  if (!match) {
    throw new Error('Could not find :root, html, body block inside @media print');
  }
  return match[1];
}

describe('design tokens and print stylesheet (#62)', () => {
  it('defines --page-max-inline: 1380px; in :root and retains --accent-gold-link: #d8b154;', () => {
    const tokensCss = readStylesheet('tokens.css');
    const rootBlock = extractRootBlock(tokensCss);

    expect(rootBlock).toMatch(/--page-max-inline:\s*1380px;/);
    expect(rootBlock).toMatch(/--accent-gold-link:\s*#d8b154;/);
  });

  it('uses var(--page-max-inline) 4 times in workbench.css with zero hardcoded 1380px literals', () => {
    const workbenchCss = readStylesheet('workbench.css');

    expect(workbenchCss).not.toMatch(/1380px/);
    const matches = workbenchCss.match(/max-inline-size:\s*var\(--page-max-inline\);/g) ?? [];
    expect(matches).toHaveLength(4);
  });

  it('overrides --border-grid and --led-* tokens to black-on-white in @media print while keeping --accent-gold-link: #000000;', () => {
    const workbenchCss = readStylesheet('workbench.css');
    const printRootBlock = extractPrintRootBlock(workbenchCss);

    const expectedPrintTokens: ReadonlyArray<[string, string]> = [
      ['--accent-gold-link', '#000000'],
      ['--border-grid', '#888888'],
      ['--led-green', '#000000'],
      ['--led-green-bg', '#ffffff'],
      ['--led-red', '#000000'],
      ['--led-red-bg', '#ffffff'],
      ['--led-amber', '#000000'],
      ['--led-amber-bg', '#ffffff'],
    ];

    for (const [token, value] of expectedPrintTokens) {
      expect(printRootBlock).toMatch(new RegExp(`${token}:\\s*${value};`));
    }
  });
});
