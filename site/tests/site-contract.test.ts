// @vitest-environment node
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { CANONICAL_ROUTES, SITE_BASE } from '../src/lib/routes.ts';
import { verifyBuiltSite } from '../src/lib/site-contract.ts';

const tempDirs: string[] = [];

const ROUTE_TO_MDX: Record<string, string> = {
  '/': 'index.mdx',
  '/stages/01-hardware-agent-skills/': 'stages/01-hardware-agent-skills.mdx',
  '/stages/02-sketch-extraction-and-critique/': 'stages/02-sketch-extraction-and-critique.mdx',
  '/stages/03-design-spec-and-dft/': 'stages/03-design-spec-and-dft.mdx',
  '/stages/04-skidl-and-schematic/': 'stages/04-skidl-and-schematic.mdx',
  '/stages/05-main-pcb-and-silkscreen/': 'stages/05-main-pcb-and-silkscreen.mdx',
  '/stages/06-front-panel-and-artwork/': 'stages/06-front-panel-and-artwork.mdx',
  '/stages/07-fabrication-checklists-and-patches/': 'stages/07-fabrication-checklists-and-patches.mdx',
  '/stages/08-wayfinder-site-planning/': 'stages/08-wayfinder-site-planning.mdx',
  '/stages/09-companion-site-delivery/': 'stages/09-companion-site-delivery.mdx',
  '/optional/ac-dc-input-coupling/': 'optional/ac-dc-input-coupling.mdx',
  '/appendix/netlist-and-bom/': 'appendix/netlist-and-bom.mdx',
  '/appendix/engineering-sign-off-checklist/': 'appendix/engineering-sign-off-checklist.mdx',
};

const SOURCE_IMAGES: readonly string[] = [
  'EnvelopeFollower.webp',
  'schematic.png',
  'pcb_front.png',
  'pcb_back.png',
  'panel_front.png',
  'panel_back.png',
  'panel_preview_clean.png',
  'panel_preview_keepouts.png',
  'checklists/pcba_alignment_U1.png',
  'checklists/hand_assembly_J_PWR.png',
  'checklists/board_bringup_00_test_point_map.png',
  'site/patch-workbench.webp',
  'site/hardware-panel-inspector.webp',
  'site/landing-showcase.webp',
];

const FIGURES_BY_ROUTE: Record<
  string,
  readonly { stem: string; framed: boolean; priority?: boolean }[]
> = {
  '/': [
    { stem: 'panel_front', framed: false, priority: true },
    { stem: 'pcb_front', framed: false, priority: true },
    { stem: 'pcb_back', framed: false, priority: true },
  ],
  '/stages/02-sketch-extraction-and-critique/': [
    { stem: 'EnvelopeFollower', framed: false },
  ],
  '/stages/04-skidl-and-schematic/': [
    { stem: 'schematic', framed: false },
  ],
  '/stages/05-main-pcb-and-silkscreen/': [
    { stem: 'pcb_front', framed: false },
    { stem: 'pcb_back', framed: false },
  ],
  '/stages/06-front-panel-and-artwork/': [
    { stem: 'panel_preview_clean', framed: false },
    { stem: 'panel_preview_keepouts', framed: false },
    { stem: 'panel_front', framed: false },
    { stem: 'panel_back', framed: false },
  ],
  '/stages/07-fabrication-checklists-and-patches/': [
    { stem: 'pcba_alignment_U1', framed: true },
    { stem: 'hand_assembly_J_PWR', framed: true },
    { stem: 'board_bringup_00_test_point_map', framed: true },
  ],
  '/stages/09-companion-site-delivery/': [
    { stem: 'patch-workbench', framed: true },
    { stem: 'hardware-panel-inspector', framed: true },
    { stem: 'landing-showcase', framed: true },
  ],
};

const PROMPTS_BY_ROUTE: Record<
  string,
  readonly { title: string; turn?: number }[]
> = {
  '/stages/01-hardware-agent-skills/': [
    { title: 'AI Agent Prompt — Living Context Map Bootstrap' },
  ],
  '/stages/02-sketch-extraction-and-critique/': [
    { title: 'AI Agent Prompt — Sketch Extraction' },
    { title: 'AI Agent Prompt — Quantitative Circuit Critique' },
  ],
  '/stages/03-design-spec-and-dft/': [
    { title: 'AI Agent Prompt — Interactive Design Q&A' },
    { title: 'Turn 1 — Test-Point Options', turn: 1 },
    { title: 'Turn 2 — Lock All 12 Test Points', turn: 2 },
  ],
  '/stages/04-skidl-and-schematic/': [
    { title: 'AI Agent Prompt — SKiDL Circuit Capture' },
    { title: 'Turn 1 — Generate KiCad Schematic', turn: 1 },
    { title: 'Turn 2 — Export PDF & Commit', turn: 2 },
  ],
  '/stages/05-main-pcb-and-silkscreen/': [
    { title: 'AI Agent Prompt — Generate 6 HP Main PCB' },
    { title: 'Turn 1 — Declarative Silkscreen Strategy', turn: 1 },
    { title: 'Turn 2 — Extract silk_layout.json', turn: 2 },
  ],
  '/stages/08-wayfinder-site-planning/': [
    { title: 'AI Agent Prompt — Chart Wayfinder Map' },
  ],
};

const MATH_ROUTES = new Set([
  '/',
  '/stages/02-sketch-extraction-and-critique/',
  '/stages/03-design-spec-and-dft/',
  '/optional/ac-dc-input-coupling/',
]);

const MERMAID_COUNTS: Record<string, number> = {
  '/': 1,
  '/stages/03-design-spec-and-dft/': 1,
  '/stages/06-front-panel-and-artwork/': 1,
  '/stages/07-fabrication-checklists-and-patches/': 1,
  '/stages/08-wayfinder-site-planning/': 1,
  '/stages/09-companion-site-delivery/': 2,
  '/optional/ac-dc-input-coupling/': 1,
};

function routeToHtmlRel(route: string): string {
  return route === '/' ? 'index.html' : `${route.slice(1)}index.html`;
}

function buildPromptHtml(prompts: readonly { title: string; turn?: number }[]): string {
  const singles = prompts.filter((p) => p.turn === undefined);
  const turns = prompts.filter((p) => p.turn !== undefined);

  const renderStrip = (p: { title: string; turn?: number }) => `
    ${p.turn && p.turn > 1 ? '<div class="c-patch-connector">PATCHED TO TURN 2</div>' : ''}
    <div class="c-patch-strip">
      <div class="c-patch-spine" data-pagefind-ignore>
        <span class="c-patch-label">${p.turn ? `T${p.turn}` : 'PROMPT'}</span>
      </div>
      <div class="c-patch-payload">
        <div class="c-patch-title"><span>${p.title}</span></div>
        <div class="c-patch-text"><p>Run the verification check.</p></div>
      </div>
    </div>`;

  const singlesHtml = singles.map(renderStrip).join('\n');
  const chainHtml = turns.length
    ? `<div class="c-patch-chain">${turns.map(renderStrip).join('\n')}</div>`
    : '';
  return `${singlesHtml}\n${chainHtml}`;
}

function buildChecklistHtml(topCount: number, totalCount: number, checkedCount: number): string {
  const extraPerItem = totalCount - topCount;
  const items: string[] = [];
  let rendered = 0;
  for (let i = 0; i < topCount; i += 1) {
    const topChecked = rendered < checkedCount ? ' checked' : '';
    rendered += 1;
    let nested = '';
    if (i === 0 && extraPerItem > 0) {
      const subItems: string[] = [];
      for (let j = 0; j < extraPerItem; j += 1) {
        const subChecked = rendered < checkedCount ? ' checked' : '';
        rendered += 1;
        subItems.push(`<li class="task-list-item"><input type="checkbox"${subChecked} disabled /> Sub ${j + 1}</li>`);
      }
      nested = `<ul class="contains-task-list">${subItems.join('')}</ul>`;
    }
    items.push(`<li class="task-list-item"><input type="checkbox"${topChecked} disabled /> Item ${i + 1}${nested}</li>`);
  }
  return `<ul class="contains-task-list">${items.join('')}</ul>`;
}

function writeFile(filePath: string, content: string | Buffer): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
}

function runGit(cwd: string, args: string[]): string {
  return execFileSync('git', ['-C', cwd, ...args], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    env: {
      ...process.env,
      GIT_AUTHOR_NAME: 'Test Author',
      GIT_AUTHOR_EMAIL: 'test@example.com',
      GIT_COMMITTER_NAME: 'Test Committer',
      GIT_COMMITTER_EMAIL: 'test@example.com',
    },
  }).trim();
}

function replacePinShaInFixture(fixture: FixturePaths, oldSha: string, newSha: string): void {
  const readmePath = path.join(fixture.repoRoot, 'README.md');
  fs.writeFileSync(readmePath, fs.readFileSync(readmePath, 'utf8').replaceAll(oldSha, newSha));
  for (const mdxRel of Object.values(ROUTE_TO_MDX)) {
    const mdxPath = path.join(fixture.mdxDir, mdxRel);
    fs.writeFileSync(mdxPath, fs.readFileSync(mdxPath, 'utf8').replaceAll(oldSha, newSha));
  }
}

interface FixturePaths {
  repoRoot: string;
  distDir: string;
  mdxDir: string;
  assetsImagesDir: string;
  referenceDir: string;
}

function createValidBuiltFixture(): FixturePaths {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'env-skew-tutorial-contract-'));
  tempDirs.push(root);

  const repoRoot = path.join(root, 'repo');
  const siteDir = path.join(repoRoot, 'site');
  const distDir = path.join(siteDir, 'dist');
  const mdxDir = path.join(siteDir, 'src/content/tutorial');
  const assetsImagesDir = path.join(siteDir, 'src/assets/images');
  const referenceDir = path.join(repoRoot, 'reference');

  // Self-hosted font bundles (4 families) + site CSS + JS
  for (const family of ['barlow-condensed', 'space-grotesk', 'ibm-plex-sans', 'ibm-plex-mono']) {
    writeFile(path.join(distDir, `_astro/${family}-latin-400-normal.woff2`), Buffer.from('woff2'));
  }
  writeFile(path.join(distDir, '_astro/workbench.css'), 'body { background: #141518; }');
  writeFile(path.join(distDir, '_astro/katex.min.css'), '.katex { font-size: 1em; }');
  writeFile(path.join(distDir, '_astro/layout.js'), 'console.log("ok");');
  writeFile(path.join(distDir, '_astro/mermaid-hydrator.js'), 'import mermaid from "mermaid";');

  // Pagefind artifacts
  writeFile(path.join(distDir, 'pagefind/pagefind.js'), 'export async function search() {}');
  writeFile(path.join(distDir, 'pagefind/pagefind-entry.json'), '{"version":"1.0"}');

  // 14 source images + built _astro webps
  for (const relImg of SOURCE_IMAGES) {
    writeFile(path.join(assetsImagesDir, relImg), Buffer.from([0x89, 0x50, 0x4e, 0x47]));
    const stem = path.parse(relImg).name;
    writeFile(path.join(distDir, `_astro/${stem}.abc123_def.webp`), Buffer.from('webp'));
    writeFile(path.join(distDir, `_astro/${stem}.full.png`), Buffer.from('png'));
  }

  // Reference submodule pinned targets + repo root files
  writeFile(path.join(referenceDir, 'DesignSpec.md'), '# DesignSpec');
  writeFile(path.join(referenceDir, 'patches/README.md'), '# Patches');
  writeFile(path.join(repoRoot, 'GLOSSARY.md'), '# Glossary');
  writeFile(path.join(repoRoot, 'prompts/README.md'), '# Session Traces');
  writeFile(
    path.join(repoRoot, 'README.md'),
    `# ENV / SKEW Build Tutorial
<img src="site/src/assets/images/panel_front.png" alt="Panel" width="220" />
<img src="site/src/assets/images/pcb_front.png" alt="PCB Front" width="220" />
<img src="site/src/assets/images/pcb_back.png" alt="PCB Back" width="220" />
[Overview](site/src/content/tutorial/index.mdx)
[Optional](site/src/content/tutorial/optional/ac-dc-input-coupling.mdx)
[DesignSpec](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/DesignSpec.md)
[Traces](https://github.com/domesticmouse/EnvelopeFollower/tree/main/prompts)
[Live](https://domesticmouse.github.io/EnvelopeFollower/)
`,
  );
  writeFile(
    path.join(repoRoot, 'PotentialImprovements.md'),
    `# Potential Improvements
> **Note for ENV / SKEW builders:** See [Optional](site/src/content/tutorial/optional/ac-dc-input-coupling.mdx) and [live](https://domesticmouse.github.io/EnvelopeFollower/optional/ac-dc-input-coupling/) alongside [Companion Specs](https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/specs/).
`,
  );

  // Build all 13 canonical routes (HTML + MDX)
  for (const route of CANONICAL_ROUTES) {
    const figures = FIGURES_BY_ROUTE[route] ?? [];
    const figuresHtml = figures
      .map(
        (fig) => `<figure class="tutorial-figure${fig.framed ? ' is-framed' : ''}">
          <button type="button" class="figure-zoom-btn" data-lightbox-trigger data-lightbox-src="${SITE_BASE}/_astro/${fig.stem}.full.png" data-lightbox-alt="${fig.stem}">
            <img src="${SITE_BASE}/_astro/${fig.stem}.abc123_def.webp" alt="${fig.stem}" width="640" height="480" loading="${fig.priority ? 'eager' : 'lazy'}"${fig.priority ? ' fetchpriority="high"' : ''} />
          </button>
        </figure>`,
      )
      .join('\n');

    const promptsHtml = buildPromptHtml(PROMPTS_BY_ROUTE[route] ?? []);
    const mermaidCount = MERMAID_COUNTS[route] ?? 0;
    const mermaidHtml = Array.from({ length: mermaidCount }, () =>
      `<figure class="mermaid-card" data-pagefind-ignore><pre class="mermaid">flowchart TD\n  A --> B</pre></figure>`,
    ).join('\n');
    const hasMath = MATH_ROUTES.has(route);
    const mathHtml = hasMath
      ? route === '/optional/ac-dc-input-coupling/'
        ? '<span class="katex-display"><span class="katex">f</span></span><span class="katex">x</span>'
        : '<span class="katex">x</span>'
      : '';
    const extraBody =
      route === '/stages/06-front-panel-and-artwork/'
        ? '<blockquote><p>Editorial commentary quote.</p></blockquote>'
        : route === '/appendix/engineering-sign-off-checklist/'
          ? buildChecklistHtml(20, 66, 58)
          : route === '/appendix/netlist-and-bom/'
            ? buildChecklistHtml(9, 9, 0)
            : '';

    const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="color-scheme" content="dark" />
    <title>ENV / SKEW Build Tutorial</title>
    <link rel="canonical" href="https://domesticmouse.github.io${SITE_BASE}${route}" />
    <link rel="stylesheet" href="${SITE_BASE}/_astro/workbench.css" />
    ${hasMath ? `<link rel="stylesheet" href="${SITE_BASE}/_astro/katex.min.css" />` : ''}
  </head>
  <body>
    <header class="c-header" data-pagefind-ignore>
      <a href="${SITE_BASE}/">Overview</a>
      <button type="button" data-search-trigger>Search</button>
    </header>
    <dialog id="mobile-nav-drawer" data-pagefind-ignore></dialog>
    <aside class="left-rail" data-pagefind-ignore></aside>
    <main id="main-content">
      ${route !== '/' ? '<nav class="breadcrumbs" data-pagefind-ignore></nav>' : ''}
      <h1 id="page-top" data-pagefind-body>Title</h1>
      ${route === '/' ? '<svg class="faceplate-svg"></svg>' : ''}
      <article data-pagefind-body>
        <h2 id="section-1">Section 1</h2>
        <a href="#section-1">Jump</a>
        <a href="${SITE_BASE}/appendix/netlist-and-bom/#section-1">Appendix</a>
        ${figuresHtml}
        ${promptsHtml}
        ${mermaidHtml}
        ${mathHtml}
        ${extraBody}
      </article>
      <nav class="prev-next-nav" data-pagefind-ignore></nav>
    </main>
    <aside class="right-toc" data-pagefind-ignore></aside>
    <footer class="site-footer" data-pagefind-ignore></footer>
    <dialog id="site-search-dialog" data-search-dialog closedby="any" data-pagefind-ignore></dialog>
    <dialog id="figure-lightbox" data-figure-lightbox closedby="any" data-pagefind-ignore></dialog>
    <script type="module" src="${SITE_BASE}/_astro/layout.js"></script>
    ${mermaidCount > 0 ? `<script type="module" src="${SITE_BASE}/_astro/mermaid-hydrator.js"></script>` : ''}
  </body>
</html>`;

    writeFile(path.join(distDir, routeToHtmlRel(route)), html);

    const mdxMermaid = Array.from({ length: mermaidCount }, () =>
      '```mermaid\nflowchart TD\n  A["Step A"] --> B["Step B"]\n```',
    ).join('\n\n');
    const mdxRel = ROUTE_TO_MDX[route]!;
    writeFile(
      path.join(mdxDir, mdxRel),
      `---
title: "Route ${route}"
navTitle: "Route"
description: "Description"
section: "overview"
order: 0
---

Valid tutorial prose linking [DesignSpec](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/DesignSpec.md).

${mdxMermaid}
`,
    );
  }

  return { repoRoot, distDir, mdxDir, assetsImagesDir, referenceDir };
}

afterEach(() => {
  while (tempDirs.length > 0) {
    const dir = tempDirs.pop();
    if (dir) fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe('Build Tutorial site-contract verifier', () => {
  it('passes cleanly on a valid 13-route built-site and repository fixture', () => {
    const fixture = createValidBuiltFixture();
    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors).toEqual([]);
    expect(result.warnings).toEqual([]);
    expect(result.checkedHtmlRoutes).toEqual([...CANONICAL_ROUTES]);
    expect(result.verifiedImages).toBe(17);
    expect(result.verifiedLinks).toBeGreaterThanOrEqual(26);
    expect(result.verifiedFigures).toBe(17);
    expect(result.verifiedPrompts).toBe(13);
  });

  it('Contract Group 1: fails on missing canonical route, extra HTML route, leaked excluded dirs, or missing Pagefind artifacts', () => {
    const fixture = createValidBuiltFixture();
    fs.rmSync(path.join(fixture.distDir, 'stages/01-hardware-agent-skills/index.html'));
    writeFile(path.join(fixture.distDir, 'stages/index.html'), '<html><body>Hub</body></html>');
    writeFile(path.join(fixture.distDir, 'agents/issue-tracker/index.html'), '<html></html>');
    writeFile(path.join(fixture.distDir, 'adr/0001/index.html'), '<html></html>');
    writeFile(path.join(fixture.distDir, 'research/notes/index.html'), '<html></html>');
    fs.rmSync(path.join(fixture.distDir, 'pagefind/pagefind.js'));
    fs.writeFileSync(path.join(fixture.distDir, 'pagefind/pagefind-entry.json'), '');

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('01-hardware-agent-skills'))).toBe(true);
    expect(result.errors.some((e) => e.includes('stages/index.html'))).toBe(true);
    expect(result.errors.some((e) => e.includes('agents'))).toBe(true);
    expect(result.errors.some((e) => e.includes('adr'))).toBe(true);
    expect(result.errors.some((e) => e.includes('research'))).toBe(true);
    expect(result.errors.some((e) => e.includes('pagefind.js'))).toBe(true);
    expect(result.errors.some((e) => e.includes('pagefind-entry.json'))).toBe(true);
  });

  it('Contract Group 2: fails on unprefixed/broken links, broken #fragments, bad <img> dims/src, inline ESM import, external CDN/fonts, and missing .woff2', () => {
    const fixture = createValidBuiltFixture();
    const stage1HtmlPath = path.join(fixture.distDir, 'stages/01-hardware-agent-skills/index.html');
    const stage1Html = fs.readFileSync(stage1HtmlPath, 'utf8')
      .replace('href="#section-1"', 'href="#missing-local-id"')
      .replace(
        `href="${SITE_BASE}/appendix/netlist-and-bom/#section-1"`,
        `href="${SITE_BASE}/appendix/netlist-and-bom/#missing-remote-id"`,
      )
      .replace(
        '</article>',
        `<a href="/stages/02-sketch-extraction-and-critique/">MissingBase</a>
         <a href="${SITE_BASE}/does-not-exist/">MissingTarget</a>
         <img src="${SITE_BASE}/_astro/missing.webp" alt="Missing" />
        </article>`,
      )
      .replace(
        '</head>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk" /></head>',
      )
      .replace(
        '</body>',
        '<script type="module">import { foo } from "./bar.js";</script></body>',
      );
    fs.writeFileSync(stage1HtmlPath, stage1Html);
    fs.writeFileSync(
      path.join(fixture.distDir, '_astro/workbench.css'),
      '@import url("https://cdn.jsdelivr.net/npm/foo.css");',
    );
    fs.rmSync(path.join(fixture.distDir, '_astro/barlow-condensed-latin-400-normal.woff2'));

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('#missing-local-id'))).toBe(true);
    expect(result.errors.some((e) => e.includes('#missing-remote-id'))).toBe(true);
    expect(result.errors.some((e) => e.includes('/stages/02-sketch-extraction-and-critique/'))).toBe(true);
    expect(result.errors.some((e) => e.includes('does-not-exist'))).toBe(true);
    expect(result.errors.some((e) => e.includes('width/height'))).toBe(true);
    expect(result.errors.some((e) => e.includes('missing.webp'))).toBe(true);
    expect(result.errors.some((e) => e.includes('inline ESM import'))).toBe(true);
    expect(result.errors.some((e) => e.includes('fonts.googleapis.com'))).toBe(true);
    expect(result.errors.some((e) => e.includes('cdn.jsdelivr.net'))).toBe(true);
    expect(result.errors.some((e) => e.includes('barlow-condensed'))).toBe(true);
  });

  it('Contract Group 1/2: fails on missing <meta name="color-scheme" content="dark"> or <script> inside <main>', () => {
    const fixture = createValidBuiltFixture();
    const indexPath = path.join(fixture.distDir, 'index.html');
    fs.writeFileSync(
      indexPath,
      fs.readFileSync(indexPath, 'utf8').replace('<meta name="color-scheme" content="dark" />', ''),
    );

    const stage1Path = path.join(fixture.distDir, 'stages/01-hardware-agent-skills/index.html');
    fs.writeFileSync(
      stage1Path,
      fs.readFileSync(stage1Path, 'utf8').replace('</article>', '<script>console.log("bad");</script></article>'),
    );

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('color-scheme') && /\[Group [12]\]/.test(e))).toBe(true);
    expect(result.errors.some((e) => e.includes('<main>') && e.includes('<script>'))).toBe(true);
  });

  it('Contract Group 3: fails on missing/oversized source images, wrong figure framing, missing lightbox trigger, priority+lazy, and figure count mismatch', () => {
    const fixture = createValidBuiltFixture();
    // Oversize checklist PNG (> 500 KiB) and site WebP (> 250 KiB), delete one base render
    fs.writeFileSync(
      path.join(fixture.assetsImagesDir, 'checklists/pcba_alignment_U1.png'),
      Buffer.alloc(500 * 1024 + 1),
    );
    fs.writeFileSync(
      path.join(fixture.assetsImagesDir, 'site/landing-showcase.webp'),
      Buffer.alloc(250 * 1024 + 1),
    );
    fs.rmSync(path.join(fixture.assetsImagesDir, 'schematic.png'));

    // Overview: add loading="lazy" to fetchpriority="high" AND add .is-framed to base render
    const indexHtmlPath = path.join(fixture.distDir, 'index.html');
    fs.writeFileSync(
      indexHtmlPath,
      fs.readFileSync(indexHtmlPath, 'utf8')
        .replace('loading="eager" fetchpriority="high"', 'loading="lazy" fetchpriority="high"')
        .replace('<figure class="tutorial-figure">', '<figure class="tutorial-figure is-framed">'),
    );

    // Stage 7: remove .is-framed from checklist capture and drop lightbox trigger
    const stage7Path = path.join(fixture.distDir, 'stages/07-fabrication-checklists-and-patches/index.html');
    fs.writeFileSync(
      stage7Path,
      fs.readFileSync(stage7Path, 'utf8')
        .replace('figure class="tutorial-figure is-framed"', 'figure class="tutorial-figure"')
        .replace('data-lightbox-trigger', ''),
    );

    // Stage 4: drop the schematic figure so total figures != 17 and schematic isn't rendered
    const stage4Path = path.join(fixture.distDir, 'stages/04-skidl-and-schematic/index.html');
    fs.writeFileSync(
      stage4Path,
      fs.readFileSync(stage4Path, 'utf8').replace(/<figure class="tutorial-figure[\s\S]*?<\/figure>/, ''),
    );

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('500 KiB'))).toBe(true);
    expect(result.errors.some((e) => e.includes('250 KiB'))).toBe(true);
    expect(result.errors.some((e) => e.includes('schematic.png'))).toBe(true);
    expect(result.errors.some((e) => e.includes('loading="lazy"'))).toBe(true);
    expect(result.errors.some((e) => e.includes('unframed'))).toBe(true);
    expect(result.errors.some((e) => e.includes('framed'))).toBe(true);
    expect(result.errors.some((e) => e.includes('lightbox'))).toBe(true);
    expect(result.errors.some((e) => e.includes('17'))).toBe(true);
    expect(result.errors.some((e) => e.includes('schematic'))).toBe(true);
  });

  it('Contract Group 4: fails on PromptBlock count/title/connector mismatches, outer quotes, missing Stage 6 blockquote, forbidden prompt headings, and prototype leftovers', () => {
    const fixture = createValidBuiltFixture();
    // Stage 1: wrong prompt title + outer quote wrapper
    const stage1Path = path.join(fixture.distDir, 'stages/01-hardware-agent-skills/index.html');
    fs.writeFileSync(
      stage1Path,
      fs.readFileSync(stage1Path, 'utf8')
        .replace('AI Agent Prompt — Living Context Map Bootstrap', 'Wrong Prompt Title')
        .replace('<p>Run the verification check.</p>', '<p>"Quoted prompt text."</p>'),
    );

    // Stage 3: drop .c-patch-connector before Turn 2
    const stage3Path = path.join(fixture.distDir, 'stages/03-design-spec-and-dft/index.html');
    fs.writeFileSync(
      stage3Path,
      fs.readFileSync(stage3Path, 'utf8').replace('<div class="c-patch-connector">PATCHED TO TURN 2</div>', ''),
    );

    // Stage 6: drop editorial blockquote + inject prototype leftover
    const stage6Path = path.join(fixture.distDir, 'stages/06-front-panel-and-artwork/index.html');
    fs.writeFileSync(
      stage6Path,
      fs.readFileSync(stage6Path, 'utf8')
        .replace('<blockquote><p>Editorial commentary quote.</p></blockquote>', '')
        .replace('</article>', '<div data-proto-variant="b" role="tablist"></div></article>'),
    );

    // Stage 2 MDX: inject forbidden standalone prompt heading
    const stage2MdxPath = path.join(fixture.mdxDir, 'stages/02-sketch-extraction-and-critique.mdx');
    fs.appendFileSync(stage2MdxPath, '\n## AI Agent Prompt\n');

    // Built JS: inject prototype-switcher
    fs.appendFileSync(path.join(fixture.distDir, '_astro/layout.js'), '\nconst s = "prototype-switcher";');

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('Wrong Prompt Title'))).toBe(true);
    expect(result.errors.some((e) => e.includes('outer quote wrapper'))).toBe(true);
    expect(result.errors.some((e) => e.includes('c-patch-connector'))).toBe(true);
    expect(result.errors.some((e) => e.includes('blockquote'))).toBe(true);
    expect(result.errors.some((e) => e.includes('standalone prompt heading'))).toBe(true);
    expect(result.errors.some((e) => e.includes('data-proto-variant'))).toBe(true);
    expect(result.errors.some((e) => e.includes('role="tablist"') || e.includes('role=tablist'))).toBe(true);
    expect(result.errors.some((e) => e.includes('prototype-switcher'))).toBe(true);
  });

  it('Contract Group 5: fails on Mermaid count/hex/LR violations, Mermaid script on non-diagram route, .katex-error, wrong KaTeX CSS routes, appendix checklist counts, enabled checkbox, and localStorage JS', () => {
    const fixture = createValidBuiltFixture();

    // 1. MDX Mermaid violations: hardcoded hex style & mixed direction LR cross-edge + wrong count
    fs.appendFileSync(
      path.join(fixture.mdxDir, 'stages/01-hardware-agent-skills.mdx'),
      '\n```mermaid\nflowchart TD\n  subgraph G\n    direction LR\n    A --> B\n  end\n  B --> C\n  style A fill:#ff0000\n```\n',
    );

    // 2. Non-diagram route (Stage 1) leaks Mermaid script; math route (Overview) drops KaTeX CSS; non-math route (Stage 4) loads KaTeX CSS; Stage 2 has .katex-error
    const stage1Path = path.join(fixture.distDir, 'stages/01-hardware-agent-skills/index.html');
    fs.writeFileSync(
      stage1Path,
      fs.readFileSync(stage1Path, 'utf8').replace(
        '</body>',
        `<script type="module" src="${SITE_BASE}/_astro/mermaid-hydrator.js"></script></body>`,
      ),
    );
    const indexPath = path.join(fixture.distDir, 'index.html');
    fs.writeFileSync(
      indexPath,
      fs.readFileSync(indexPath, 'utf8').replace(`<link rel="stylesheet" href="${SITE_BASE}/_astro/katex.min.css" />`, ''),
    );
    const stage4Path = path.join(fixture.distDir, 'stages/04-skidl-and-schematic/index.html');
    fs.writeFileSync(
      stage4Path,
      fs.readFileSync(stage4Path, 'utf8').replace(
        '</head>',
        `<link rel="stylesheet" href="${SITE_BASE}/_astro/katex.min.css" /></head>`,
      ),
    );
    const stage2Path = path.join(fixture.distDir, 'stages/02-sketch-extraction-and-critique/index.html');
    fs.writeFileSync(
      stage2Path,
      fs.readFileSync(stage2Path, 'utf8').replace('</article>', '<span class="katex-error">err</span></article>'),
    );

    // 3. Tutorial Appendix violations + localStorage JS
    const signoffPath = path.join(fixture.distDir, 'appendix/engineering-sign-off-checklist/index.html');
    fs.writeFileSync(
      signoffPath,
      fs.readFileSync(signoffPath, 'utf8').replace('<input type="checkbox" checked disabled />', '<input type="checkbox" checked />'),
    );
    const bomPath = path.join(fixture.distDir, 'appendix/netlist-and-bom/index.html');
    fs.writeFileSync(
      bomPath,
      fs.readFileSync(bomPath, 'utf8').replace('<li class="task-list-item"><input type="checkbox" disabled /> Item 9</li>', ''),
    );
    fs.appendFileSync(path.join(fixture.distDir, '_astro/layout.js'), '\nwindow.localStorage.setItem("k","v");');

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('mermaid block'))).toBe(true);
    expect(result.errors.some((e) => e.includes('hex fill'))).toBe(true);
    expect(result.errors.some((e) => e.includes('direction LR'))).toBe(true);
    expect(result.errors.some((e) => e.includes('Mermaid') && e.includes('01-hardware-agent-skills'))).toBe(true);
    expect(result.errors.some((e) => e.includes('KaTeX CSS') && e.includes('/'))).toBe(true);
    expect(result.errors.some((e) => e.includes('KaTeX CSS') && e.includes('04-skidl-and-schematic'))).toBe(true);
    expect(result.errors.some((e) => e.includes('.katex-error'))).toBe(true);
    expect(result.errors.some((e) => e.includes('disabled'))).toBe(true);
    expect(result.errors.some((e) => e.includes('netlist-and-bom') && e.includes('9'))).toBe(true);
    expect(result.errors.some((e) => e.includes('localStorage'))).toBe(true);
  });

  it('Contract Group 6: fails on unpinned /main/ links, broken 8ad81d0 or local /main/ targets, README/PotentialImprovements sentinels, and GLOSSARY avoided terms', () => {
    const fixture = createValidBuiltFixture();

    // 1. Stage 8 MDX: unpinned link + broken 8ad81d0 + broken local main + GLOSSARY avoided term
    fs.appendFileSync(
      path.join(fixture.mdxDir, 'stages/08-wayfinder-site-planning.mdx'),
      `
[Unpinned](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/README.md)
[MissingPin](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/missing-file.md)
[MissingLocal](https://github.com/domesticmouse/EnvelopeFollower/blob/main/no-such-local.md)
This codelab also mentions motivating prompt.
`,
    );

    // 2. README.md: broken relative link, broken Pages URL, capability_mode.json, TutorialUpdateTodo.md, avoided term
    fs.writeFileSync(
      path.join(fixture.repoRoot, 'README.md'),
      `# ENV / SKEW
[Broken](docs/index.md)
[BadPages](https://domesticmouse.github.io/EnvelopeFollower/no-such-route/)
analysis/capability_mode.json
TutorialUpdateTodo.md
Uses context anchor wording.
`,
    );

    // 3. PotentialImprovements.md: missing builder note & specs url + avoided term
    fs.writeFileSync(
      path.join(fixture.repoRoot, 'PotentialImprovements.md'),
      `# Potential Improvements
[Broken](missing-note.md)
Refers to Optional Branch.
`,
    );

    const result = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });

    expect(result.errors.some((e) => e.includes('unpinned'))).toBe(true);
    expect(result.errors.some((e) => e.includes('missing-file.md'))).toBe(true);
    expect(result.errors.some((e) => e.includes('no-such-local.md'))).toBe(true);
    expect(result.errors.some((e) => e.includes('codelab'))).toBe(true);
    expect(result.errors.some((e) => e.includes('motivating prompt'))).toBe(true);
    expect(result.errors.some((e) => e.includes('docs/index.md'))).toBe(true);
    expect(result.errors.some((e) => e.includes('no-such-route'))).toBe(true);
    expect(result.errors.some((e) => e.includes('capability_mode.json'))).toBe(true);
    expect(result.errors.some((e) => e.includes('TutorialUpdateTodo.md'))).toBe(true);
    expect(result.errors.some((e) => e.includes('context anchor'))).toBe(true);
    expect(result.errors.some((e) => e.includes('Note for ENV / SKEW builders'))).toBe(true);
    expect(result.errors.some((e) => e.includes('EnvelopeFollowerWithSkewLimiter/specs/'))).toBe(true);
    expect(result.errors.some((e) => e.includes('missing-note.md'))).toBe(true);
    expect(result.errors.some((e) => e.includes('Optional Branch'))).toBe(true);
  });

  it('Contract Group 6: warns when reference/ is uninitialized locally and requireReference is false, but fails when requireReference is true', () => {
    const fixture = createValidBuiltFixture();
    fs.rmSync(fixture.referenceDir, { recursive: true, force: true });
    fs.mkdirSync(fixture.referenceDir, { recursive: true });

    const localWarn = verifyBuiltSite({
      ...fixture,
      requireReference: false,
      requirePagefind: true,
    });
    expect(localWarn.errors).toEqual([]);
    expect(localWarn.warnings.some((w) => w.includes('uninitialized'))).toBe(true);

    const ciFail = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(ciFail.errors.some((e) => e.includes('uninitialized'))).toBe(true);
  });

  it('Contract Group 6: rejects /HEAD/ and /main without subpath while ignoring branch prefixes like /mainline/', () => {
    for (const badUrl of [
      'https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/HEAD/README.md',
      'https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/HEAD',
      'https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/main',
    ]) {
      const fixture = createValidBuiltFixture();
      fs.appendFileSync(
        path.join(fixture.mdxDir, 'stages/08-wayfinder-site-planning.mdx'),
        `\n[Unpinned](${badUrl})\n`,
      );
      const result = verifyBuiltSite({
        ...fixture,
        requireReference: true,
        requirePagefind: true,
      });
      expect(result.errors.some((e) => e.includes('unpinned'))).toBe(true);
    }

    const okFixture = createValidBuiltFixture();
    fs.appendFileSync(
      path.join(okFixture.mdxDir, 'stages/08-wayfinder-site-planning.mdx'),
      '\n[Branch](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/mainline/foo)\n',
    );
    const okResult = verifyBuiltSite({
      ...okFixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(okResult.errors).toEqual([]);
  });

  it('Contract Group 6: verifies historical and HEAD pinned commit SHAs via git cat-file -t, rejects broken/mismatched/bogus/traversal/empty-blob pins, and enforces README HEAD SHA', () => {
    const fixture = createValidBuiltFixture();
    fs.rmSync(fixture.referenceDir, { recursive: true, force: true });
    fs.mkdirSync(fixture.referenceDir, { recursive: true });

    runGit(fixture.referenceDir, ['init', '-b', 'main']);
    writeFile(path.join(fixture.referenceDir, 'DesignSpec.md'), '# DesignSpec');
    writeFile(path.join(fixture.referenceDir, 'patches/README.md'), '# Patches');
    writeFile(path.join(fixture.referenceDir, 'old-only.md'), '# Historical');
    runGit(fixture.referenceDir, ['add', '.']);
    runGit(fixture.referenceDir, ['commit', '-m', 'commit A']);
    const shaA7 = runGit(fixture.referenceDir, ['rev-parse', '--short=7', 'HEAD']);
    const shaA40 = runGit(fixture.referenceDir, ['rev-parse', 'HEAD']);

    fs.rmSync(path.join(fixture.referenceDir, 'old-only.md'));
    writeFile(path.join(fixture.referenceDir, 'new-only.md'), '# Current');
    runGit(fixture.referenceDir, ['add', '-A']);
    runGit(fixture.referenceDir, ['commit', '-m', 'commit B']);
    const shaB7 = runGit(fixture.referenceDir, ['rev-parse', '--short=7', 'HEAD']);

    replacePinShaInFixture(fixture, '8ad81d0', shaB7);
    const stage8Mdx = path.join(fixture.mdxDir, 'stages/08-wayfinder-site-planning.mdx');
    fs.appendFileSync(
      stage8Mdx,
      `
[HistoricalFile](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaA7}/old-only.md)
[FullShaTree](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/${shaA40})
[HeadTree](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/${shaB7})
[PatchesDir](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/${shaB7}/patches/)
[QueryHash](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaB7}/new-only.md?plain=1#L1)
`,
    );

    const validResult = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(validResult.errors).toEqual([]);

    // Now inject failures: empty blob, deleted file in commitB, type mismatch, traversal, bogus SHA, stale README
    fs.appendFileSync(
      stage8Mdx,
      `
[EmptyBlob](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaB7})
[DeletedInB](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaB7}/old-only.md)
[WrongKind](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/${shaB7}/new-only.md)
[Traversal](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaB7}/../outside.txt)
[BogusSha](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/deadbee/DesignSpec.md)
`,
    );
    const readmePath = path.join(fixture.repoRoot, 'README.md');
    fs.writeFileSync(
      readmePath,
      fs.readFileSync(readmePath, 'utf8').replaceAll(shaB7, shaA7),
    );

    const failResult = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(failResult.errors.some((e) => e.includes(`blob/${shaB7}`))).toBe(true);
    expect(failResult.errors.some((e) => e.includes('old-only.md'))).toBe(true);
    expect(failResult.errors.some((e) => e.includes('new-only.md'))).toBe(true);
    expect(failResult.errors.some((e) => e.includes('outside.txt'))).toBe(true);
    expect(failResult.errors.some((e) => e.includes('deadbee'))).toBe(true);
    expect(failResult.errors.some((e) => e.includes('README.md') && e.includes(shaB7))).toBe(true);
  });

  it('Contract Group 6: falls back to working tree on shallow clones and synthetic non-git reference/, and detects submodule .git file', () => {
    // 1. Upstream repo with commitA (old-only.md) -> commitB (DesignSpec.md only)
    const fixture = createValidBuiltFixture();
    const upstreamDir = path.join(path.dirname(fixture.repoRoot), 'upstream');
    fs.mkdirSync(upstreamDir, { recursive: true });
    runGit(upstreamDir, ['init', '-b', 'main']);
    writeFile(path.join(upstreamDir, 'DesignSpec.md'), '# DesignSpec');
    writeFile(path.join(upstreamDir, 'patches/README.md'), '# Patches');
    writeFile(path.join(upstreamDir, 'old-only.md'), '# Historical');
    runGit(upstreamDir, ['add', '.']);
    runGit(upstreamDir, ['commit', '-m', 'commit A']);
    const shaA7 = runGit(upstreamDir, ['rev-parse', '--short=7', 'HEAD']);

    fs.rmSync(path.join(upstreamDir, 'old-only.md'));
    runGit(upstreamDir, ['add', '-A']);
    runGit(upstreamDir, ['commit', '-m', 'commit B']);
    const shaB7 = runGit(upstreamDir, ['rev-parse', '--short=7', 'HEAD']);

    // Shallow clone (--depth=1 via file://) into referenceDir
    fs.rmSync(fixture.referenceDir, { recursive: true, force: true });
    execFileSync('git', ['clone', '--depth=1', `file://${upstreamDir}`, fixture.referenceDir], {
      stdio: 'ignore',
    });
    expect(runGit(fixture.referenceDir, ['rev-parse', '--is-shallow-repository'])).toBe('true');

    replacePinShaInFixture(fixture, '8ad81d0', shaB7);
    const stage8Mdx = path.join(fixture.mdxDir, 'stages/08-wayfinder-site-planning.mdx');
    // shaA7 is unknown in shallow history, but DesignSpec.md exists in working tree & tree/<shaA7> is valid
    fs.appendFileSync(
      stage8Mdx,
      `
[ShallowFallbackFile](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaA7}/DesignSpec.md)
[ShallowFallbackTree](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/${shaA7})
`,
    );
    const shallowOk = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(shallowOk.errors).toEqual([]);
    expect(shallowOk.warnings).toEqual([]);

    // Unfetched historical SHA links whose targets are absent from shallow HEAD working tree produce [Group 6] shallow warnings, not errors
    fs.appendFileSync(
      stage8Mdx,
      `
[ShallowMissingFile](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaA7}/old-only.md)
[ShallowMissingDir](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/${shaA7}/prototype/visual-design-system)
`,
    );
    const shallowUnfetchedMissing = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(shallowUnfetchedMissing.errors).toEqual([]);
    expect(
      shallowUnfetchedMissing.warnings.some(
        (w) => w.includes('[Group 6]') && w.includes('shallow') && w.includes('old-only.md'),
      ),
    ).toBe(true);
    expect(
      shallowUnfetchedMissing.warnings.some(
        (w) =>
          w.includes('[Group 6]') &&
          w.includes('shallow') &&
          w.includes('prototype/visual-design-system'),
      ),
    ).toBe(true);

    // Broken link on shallow HEAD commit (commitB) still errors via git cat-file -t
    fs.appendFileSync(
      stage8Mdx,
      `\n[ShallowHeadBroken](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/${shaB7}/old-only.md)\n`,
    );
    const shallowHeadBroken = verifyBuiltSite({
      ...fixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(
      shallowHeadBroken.errors.some((e) => e.includes('[Group 6]') && e.includes('old-only.md')),
    ).toBe(true);

    // 2. Submodule-style .git file (gitdir: ...) is recognized as a git checkout
    const subFixture = createValidBuiltFixture();
    const realGitDir = path.join(path.dirname(subFixture.repoRoot), 'modules-ref-git');
    fs.rmSync(subFixture.referenceDir, { recursive: true, force: true });
    fs.mkdirSync(subFixture.referenceDir, { recursive: true });
    fs.renameSync(path.join(fixture.referenceDir, '.git'), realGitDir);
    fs.writeFileSync(path.join(subFixture.referenceDir, '.git'), `gitdir: ${realGitDir}\n`);
    writeFile(path.join(subFixture.referenceDir, 'DesignSpec.md'), '# DesignSpec');
    writeFile(path.join(subFixture.referenceDir, 'patches/README.md'), '# Patches');
    // Intentionally leave 8ad81d0 in README.md (not shaB7) to prove .git file triggers HEAD SHA check
    const subResult = verifyBuiltSite({
      ...subFixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(subResult.errors.some((e) => e.includes('README.md') && e.includes(shaB7))).toBe(true);

    // 3. Synthetic non-git reference/ allows tree/<sha> with empty subpath and rejects blob/<sha> with empty subpath
    const synthFixture = createValidBuiltFixture();
    const synthMdx = path.join(synthFixture.mdxDir, 'stages/08-wayfinder-site-planning.mdx');
    fs.appendFileSync(
      synthMdx,
      '\n[SynthTree](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/8ad81d0)\n',
    );
    expect(
      verifyBuiltSite({
        ...synthFixture,
        requireReference: true,
        requirePagefind: true,
      }).errors,
    ).toEqual([]);

    fs.appendFileSync(
      synthMdx,
      `
[SynthBlobEmpty](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0)
[SynthMissingFile](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/missing-target.md)
[SynthMissingDir](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/8ad81d0/missing-dir)
`,
    );
    const synthFail = verifyBuiltSite({
      ...synthFixture,
      requireReference: true,
      requirePagefind: true,
    });
    expect(synthFail.errors.some((e) => e.includes('blob/8ad81d0'))).toBe(true);
    expect(synthFail.errors.some((e) => e.includes('missing-target.md'))).toBe(true);
    expect(synthFail.errors.some((e) => e.includes('missing-dir'))).toBe(true);
    expect(synthFail.warnings).toEqual([]);
  });
});
