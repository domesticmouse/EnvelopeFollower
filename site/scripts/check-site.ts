import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Window } from 'happy-dom';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST_DIR = path.join(SITE_DIR, 'dist');

const EXPECTED_PAGES = [
  {
    file: path.join(DIST_DIR, 'appendix/netlist-and-bom/index.html'),
    checklistItems: 9,
    expectedChecked: 0,
    expectedCalloutTitleCode: 'manufacturing/orders/tayda-1000489380.md',
    expectedProgress: 'PROGRESS · APP',
    expectedPrevHref: '/EnvelopeFollower/optional/ac-dc-input-coupling/',
    expectedNextHref: '/EnvelopeFollower/appendix/engineering-sign-off-checklist/',
  },
  {
    file: path.join(DIST_DIR, 'appendix/engineering-sign-off-checklist/index.html'),
    checklistItems: 66,
    expectedChecked: 58,
    expectedProgress: 'PROGRESS · APP',
    expectedPrevHref: '/EnvelopeFollower/appendix/netlist-and-bom/',
    expectedNextHref: undefined,
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

const woff2Files: string[] = [];
const cssFiles: string[] = [];
const jsFiles: string[] = [];
function walk(dir: string): void {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
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
    'nav.breadcrumbs[data-pagefind-ignore]',
    'aside.right-toc[data-pagefind-ignore]',
    'nav.prev-next-nav[data-pagefind-ignore]',
    'footer.site-footer[data-pagefind-ignore]',
    'dialog#site-search-dialog[data-pagefind-ignore]',
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
  `OK: Verified ${EXPECTED_PAGES.length} built Tutorial Appendix routes, ${woff2Files.length} self-hosted .woff2 assets, and 0 external CSS URLs.`,
);
