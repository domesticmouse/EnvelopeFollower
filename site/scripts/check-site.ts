import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Window } from 'happy-dom';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST_DIR = path.join(SITE_DIR, 'dist');

interface ExpectedPage {
  file: string;
  checklistItems: number;
  expectedChecked: number;
  expectedCalloutTitleCode?: string;
  expectedProgress: string;
  expectedPrevHref?: string;
  expectedNextHref?: string;
  expectedPromptStrips: number;
  expectedCodeConsoles: number;
  expectBreadcrumbs?: boolean;
  expectMath: boolean;
  expectDisplayMath?: boolean;
  expectMermaid: boolean;
  expectFaceplateSvg?: boolean;
  expectedFigures?: number;
  expectedPriorityFigures?: number;
}

const EXPECTED_PAGES: ExpectedPage[] = [
  {
    file: path.join(DIST_DIR, 'index.html'),
    checklistItems: 0,
    expectedChecked: 0,
    expectedProgress: 'PROGRESS · STAGE 00 / 09',
    expectedPrevHref: undefined,
    expectedNextHref: '/EnvelopeFollower/stages/01-hardware-agent-skills/',
    expectedPromptStrips: 0,
    expectedCodeConsoles: 0,
    expectBreadcrumbs: false,
    expectMath: true,
    expectDisplayMath: false,
    expectMermaid: true,
    expectFaceplateSvg: true,
    expectedFigures: 3,
    expectedPriorityFigures: 3,
  },
  {
    file: path.join(DIST_DIR, 'stages/01-hardware-agent-skills/index.html'),
    checklistItems: 0,
    expectedChecked: 0,
    expectedProgress: 'PROGRESS · STAGE 01 / 09',
    expectedPrevHref: '/EnvelopeFollower/',
    expectedNextHref: '/EnvelopeFollower/stages/02-sketch-extraction-and-critique/',
    expectedPromptStrips: 1,
    expectedCodeConsoles: 5,
    expectMath: false,
    expectMermaid: false,
  },
  {
    file: path.join(DIST_DIR, 'optional/ac-dc-input-coupling/index.html'),
    checklistItems: 0,
    expectedChecked: 0,
    expectedCalloutTitleCode: 'ENV / SKEW',
    expectedProgress: 'PROGRESS · OPT',
    expectedPrevHref: '/EnvelopeFollower/stages/09-companion-site-delivery/',
    expectedNextHref: '/EnvelopeFollower/appendix/netlist-and-bom/',
    expectedPromptStrips: 0,
    expectedCodeConsoles: 0,
    expectMath: true,
    expectDisplayMath: true,
    expectMermaid: true,
  },
  {
    file: path.join(DIST_DIR, 'appendix/netlist-and-bom/index.html'),
    checklistItems: 9,
    expectedChecked: 0,
    expectedCalloutTitleCode: 'manufacturing/orders/tayda-1000489380.md',
    expectedProgress: 'PROGRESS · APP',
    expectedPrevHref: '/EnvelopeFollower/optional/ac-dc-input-coupling/',
    expectedNextHref: '/EnvelopeFollower/appendix/engineering-sign-off-checklist/',
    expectedPromptStrips: 0,
    expectedCodeConsoles: 1,
    expectMath: false,
    expectMermaid: false,
  },
  {
    file: path.join(DIST_DIR, 'appendix/engineering-sign-off-checklist/index.html'),
    checklistItems: 66,
    expectedChecked: 58,
    expectedProgress: 'PROGRESS · APP',
    expectedPrevHref: '/EnvelopeFollower/appendix/netlist-and-bom/',
    expectedNextHref: undefined,
    expectedPromptStrips: 0,
    expectedCodeConsoles: 0,
    expectMath: false,
    expectMermaid: false,
  },
];

const FORBIDDEN_PAGE_PATTERNS = [
  'fonts.googleapis.com',
  'fonts.gstatic.com',
  'unpkg.com',
  'cdn.jsdelivr.net',
  'prototype-switcher',
  'prototype-theme',
  'data-proto-variant',
  'role="tablist"',
];

function fail(message: string): never {
  console.error(`FAIL: ${message}`);
  process.exit(1);
}

if (!fs.existsSync(DIST_DIR)) {
  fail(`Missing dist directory at ${DIST_DIR}. Run "npm run build" first.`);
}

for (const pagefindArtifact of [
  path.join(DIST_DIR, 'pagefind/pagefind.js'),
  path.join(DIST_DIR, 'pagefind/pagefind-entry.json'),
]) {
  if (!fs.existsSync(pagefindArtifact) || fs.statSync(pagefindArtifact).size === 0) {
    fail(`Missing or empty Pagefind index artifact: ${pagefindArtifact}`);
  }
}

const woff2Files: string[] = [];
const cssFiles: string[] = [];
const jsFiles: string[] = [];
function walk(dir: string): void {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'pagefind') {
        continue;
      }
      walk(full);
    } else if (entry.name.endsWith('.woff2')) {
      woff2Files.push(entry.name);
    } else if (entry.name.endsWith('.css')) {
      cssFiles.push(full);
    } else if (entry.name.endsWith('.js')) {
      jsFiles.push(full);
    }
  }
}
walk(DIST_DIR);

for (const jsFile of jsFiles) {
  const js = fs.readFileSync(jsFile, 'utf8');
  if (js.includes('localStorage')) {
    fail(`Forbidden localStorage usage found in built JS bundle ${jsFile}`);
  }
}

for (const family of ['barlow-condensed', 'space-grotesk', 'ibm-plex-sans', 'ibm-plex-mono']) {
  if (!woff2Files.some((f) => f.includes(family))) {
    fail(`Missing self-hosted .woff2 font asset for ${family} in dist/`);
  }
}

for (const cssFile of cssFiles) {
  const css = fs.readFileSync(cssFile, 'utf8');
  if (/https?:\/\//i.test(css)) {
    fail(`External URL found in built CSS ${cssFile}`);
  }
}

for (const page of EXPECTED_PAGES) {
  if (!fs.existsSync(page.file)) {
    fail(`Missing built HTML route: ${page.file}`);
  }
  const html = fs.readFileSync(page.file, 'utf8');

  for (const pattern of FORBIDDEN_PAGE_PATTERNS) {
    if (html.includes(pattern)) {
      fail(`Forbidden pattern "${pattern}" found in ${page.file}`);
    }
  }

  const win = new Window({ url: 'https://domesticmouse.github.io/EnvelopeFollower/' });
  win.document.write(html);

  const h1s = win.document.querySelectorAll('h1');
  if (h1s.length !== 1) {
    fail(`Expected exactly 1 <h1> in ${page.file}, found ${h1s.length}`);
  }

  if (!win.document.querySelector('h1[data-pagefind-body]')) {
    fail(`Missing h1[data-pagefind-body] indexing boundary in ${page.file}`);
  }
  if (!win.document.querySelector('article[data-pagefind-body]')) {
    fail(`Missing article[data-pagefind-body] indexing boundary in ${page.file}`);
  }
  for (const selector of [
    'header.c-header[data-pagefind-ignore]',
    'dialog#mobile-nav-drawer[data-pagefind-ignore]',
    'aside.left-rail[data-pagefind-ignore]',
    ...(page.expectBreadcrumbs !== false ? ['nav.breadcrumbs[data-pagefind-ignore]'] : []),
    'aside.right-toc[data-pagefind-ignore]',
    'nav.prev-next-nav[data-pagefind-ignore]',
    'footer.site-footer[data-pagefind-ignore]',
    'dialog#site-search-dialog[data-pagefind-ignore]',
    'dialog#figure-lightbox[data-pagefind-ignore]',
  ]) {
    if (!win.document.querySelector(selector)) {
      fail(`Missing expected indexing exclusion "${selector}" in ${page.file}`);
    }
  }

  if (!win.document.querySelector('[data-search-trigger]')) {
    fail(`Missing [data-search-trigger] header button in ${page.file}`);
  }
  if (!win.document.querySelector('dialog[data-search-dialog][closedby="any"]')) {
    fail(`Missing native <dialog data-search-dialog closedby="any"> in ${page.file}`);
  }
  if (!win.document.querySelector('dialog[data-figure-lightbox][closedby="any"]')) {
    fail(`Missing native <dialog data-figure-lightbox closedby="any"> in ${page.file}`);
  }

  for (const script of Array.from(win.document.querySelectorAll('script'))) {
    if ((script.textContent ?? '').includes('localStorage')) {
      fail(`Forbidden localStorage usage found in inline <script> in ${page.file}`);
    }
  }

  for (const svg of Array.from(win.document.querySelectorAll('svg'))) {
    const markup = svg.outerHTML;
    if (markup.includes('_03_Registration_Frame') || markup.includes('registration_frame')) {
      fail(`Registration frame leaked into rendered <svg> in ${page.file}`);
    }
  }

  if (page.expectFaceplateSvg && !win.document.querySelector('svg.faceplate-svg')) {
    fail(`Expected assembled 6 HP faceplate SVG (svg.faceplate-svg) in ${page.file}`);
  }

  if (page.expectedFigures !== undefined) {
    const figures = win.document.querySelectorAll('article figure.tutorial-figure');
    if (figures.length !== page.expectedFigures) {
      fail(
        `Expected ${page.expectedFigures} <Figure> elements in ${page.file}, found ${figures.length}`,
      );
    }
    const imgs = Array.from(win.document.querySelectorAll('article figure.tutorial-figure img'));
    if (imgs.length !== page.expectedFigures) {
      fail(`Expected ${page.expectedFigures} figure <img> tags in ${page.file}, found ${imgs.length}`);
    }
    let priorityCount = 0;
    for (const img of imgs) {
      const width = Number(img.getAttribute('width'));
      const height = Number(img.getAttribute('height'));
      if (!Number.isInteger(width) || width <= 0 || !Number.isInteger(height) || height <= 0) {
        fail(`Figure <img> missing positive integer width/height in ${page.file}`);
      }
      const src = img.getAttribute('src') ?? '';
      if (!src.startsWith('/EnvelopeFollower/_astro/')) {
        fail(`Expected Astro-bundled figure src in ${page.file}, got "${src}"`);
      }
      const relAsset = src.slice('/EnvelopeFollower/'.length);
      if (!fs.existsSync(path.join(DIST_DIR, relAsset))) {
        fail(`Missing built figure image asset ${relAsset} in dist/`);
      }
      if (img.getAttribute('fetchpriority') === 'high') {
        if (img.getAttribute('loading') === 'lazy') {
          fail(`Priority figure must never pair fetchpriority="high" with loading="lazy" in ${page.file}`);
        }
        priorityCount += 1;
      }
    }
    if (
      page.expectedPriorityFigures !== undefined &&
      priorityCount !== page.expectedPriorityFigures
    ) {
      fail(
        `Expected ${page.expectedPriorityFigures} priority figures in ${page.file}, found ${priorityCount}`,
      );
    }
  }

  const progressText = win.document.querySelector('.c-progress-module')?.textContent ?? '';
  if (!progressText.includes(page.expectedProgress)) {
    fail(`Expected progress "${page.expectedProgress}" in ${page.file}, got "${progressText}"`);
  }

  const railLinks = win.document.querySelectorAll('.c-rack-link');
  if (railLinks.length !== 13) {
    fail(`Expected 13 left-rail curriculum links in ${page.file}, found ${railLinks.length}`);
  }

  const tocLinks = win.document.querySelectorAll('.right-toc .toc-link');
  if (tocLinks.length < 2) {
    fail(`Expected right-rail TOC links in ${page.file}, found ${tocLinks.length}`);
  }

  const prevLink = win.document.querySelector('.prev-next-card[data-dir="prev"]');
  if (prevLink?.getAttribute('href') !== page.expectedPrevHref) {
    fail(
      `Expected prev href "${page.expectedPrevHref}" in ${page.file}, got "${prevLink?.getAttribute('href')}"`,
    );
  }

  const nextLink = win.document.querySelector('.prev-next-card[data-dir="next"]');
  if (nextLink?.getAttribute('href') !== page.expectedNextHref) {
    fail(
      `Expected next href "${page.expectedNextHref}" in ${page.file}, got "${nextLink?.getAttribute('href')}"`,
    );
  }

  if (page.expectedCalloutTitleCode) {
    const calloutCode = win.document.querySelector('.callout-title code');
    if (calloutCode?.textContent !== page.expectedCalloutTitleCode) {
      fail(
        `Expected callout title code "${page.expectedCalloutTitleCode}" in ${page.file}, got "${calloutCode?.textContent}"`,
      );
    }
  }

  const promptStrips = win.document.querySelectorAll('.c-patch-strip');
  if (promptStrips.length !== page.expectedPromptStrips) {
    fail(
      `Expected ${page.expectedPromptStrips} .c-patch-strip blocks in ${page.file}, found ${promptStrips.length}`,
    );
  }

  const codeConsoles = win.document.querySelectorAll('.code-console');
  if (codeConsoles.length !== page.expectedCodeConsoles) {
    fail(
      `Expected ${page.expectedCodeConsoles} .code-console blocks in ${page.file}, found ${codeConsoles.length}`,
    );
  }

  if (win.document.querySelectorAll('.katex-error').length > 0) {
    fail(`Rendered KaTeX parse error (.katex-error) detected in ${page.file}`);
  }

  const stylesheetLinks = Array.from(
    win.document.querySelectorAll('link[rel="stylesheet"]'),
  ).map((el) => el.getAttribute('href') ?? '');
  const hasKatexCssLink = stylesheetLinks.some((href) => /katex/i.test(href));
  const scriptSrcs = Array.from(win.document.querySelectorAll('script[src]')).map(
    (el) => el.getAttribute('src') ?? '',
  );
  const hasMermaidScript = scriptSrcs.some((src) => /mermaid/i.test(src));

  if (page.expectMath) {
    if (!hasKatexCssLink) {
      fail(`Expected self-hosted KaTeX CSS link on math route ${page.file}`);
    }
    if (win.document.querySelectorAll('.katex').length === 0) {
      fail(`Expected rendered .katex math nodes in ${page.file}`);
    }
    if (page.expectDisplayMath && win.document.querySelectorAll('.katex-display').length === 0) {
      fail(`Expected rendered .katex-display block in ${page.file}`);
    }
  } else {
    if (hasKatexCssLink) {
      fail(`Unexpected KaTeX CSS link on non-math route ${page.file}`);
    }
    if (win.document.querySelectorAll('.katex').length > 0) {
      fail(`Unexpected .katex nodes on non-math route ${page.file}`);
    }
  }

  if (page.expectMermaid) {
    if (!hasMermaidScript) {
      fail(`Expected Mermaid hydrator script on diagram route ${page.file}`);
    }
    if (win.document.querySelectorAll('.mermaid-card[data-pagefind-ignore] pre.mermaid').length === 0) {
      fail(`Expected .mermaid-card[data-pagefind-ignore] pre.mermaid block in ${page.file}`);
    }
  } else {
    if (hasMermaidScript) {
      fail(`Unexpected Mermaid script on non-diagram route ${page.file}`);
    }
    if (win.document.querySelectorAll('.mermaid').length > 0) {
      fail(`Unexpected .mermaid block on non-diagram route ${page.file}`);
    }
  }

  const checkboxes = Array.from(win.document.querySelectorAll('article input[type="checkbox"]'));
  if (checkboxes.length !== page.checklistItems) {
    fail(`Expected ${page.checklistItems} checkboxes in ${page.file}, found ${checkboxes.length}`);
  }
  for (const cb of checkboxes) {
    if (!cb.hasAttribute('disabled')) {
      fail(`Appendix checklist checkbox must be read-only (disabled) in ${page.file}`);
    }
  }
  const checkedCount = checkboxes.filter((cb) => cb.hasAttribute('checked')).length;
  if (checkedCount !== page.expectedChecked) {
    fail(`Expected ${page.expectedChecked} checked items in ${page.file}, found ${checkedCount}`);
  }

  win.close();
}

console.log(
  `OK: Verified ${EXPECTED_PAGES.length} built routes, ${woff2Files.length} self-hosted .woff2 assets, Pagefind index, and 0 external CSS URLs.`,
);
