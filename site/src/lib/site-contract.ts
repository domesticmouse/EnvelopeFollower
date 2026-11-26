import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { Window } from 'happy-dom';
import {
  CANONICAL_ROUTES,
  SITE_BASE,
  SITE_ORIGIN,
  normalizeRoutePath,
} from './routes.ts';

/** Configuration options for built-site and repository contract verification. */
export interface VerifyBuiltSiteOptions {
  distDir: string;
  repoRoot: string;
  mdxDir?: string;
  assetsImagesDir?: string;
  referenceDir?: string;
  requireReference?: boolean;
  requirePagefind?: boolean;
}

/** Summary report returned by verifyBuiltSite. */
export interface SiteContractResult {
  checkedHtmlRoutes: string[];
  verifiedImages: number;
  verifiedLinks: number;
  verifiedFigures: number;
  verifiedPrompts: number;
  errors: string[];
  warnings: string[];
}

const EXCLUDED_SITE_DIRS = ['agents', 'adr', 'research'] as const;
const CANONICAL_ROUTE_SET = new Set<string>(CANONICAL_ROUTES);
const POSITIVE_INT_RE = /^[1-9]\d*$/;
const EXTERNAL_PROTO_RE = /^(?:https?:|mailto:|tel:|data:|blob:|javascript:)/i;
const EXTERNAL_CDN_DOMAINS = [
  'fonts.googleapis.com',
  'fonts.gstatic.com',
  'unpkg.com',
  'cdn.jsdelivr.net',
] as const;
const REQUIRED_FONT_FAMILIES = [
  'barlow-condensed',
  'space-grotesk',
  'ibm-plex-sans',
  'ibm-plex-mono',
] as const;

const BASE_RENDERS = [
  'EnvelopeFollower.webp',
  'schematic.png',
  'pcb_front.png',
  'pcb_back.png',
  'panel_front.png',
  'panel_back.png',
  'panel_preview_clean.png',
  'panel_preview_keepouts.png',
] as const;

const CHECKLIST_PNGS = [
  'checklists/pcba_alignment_U1.png',
  'checklists/hand_assembly_J_PWR.png',
  'checklists/board_bringup_00_test_point_map.png',
] as const;

const SITE_WEBPS = [
  'site/patch-workbench.webp',
  'site/hardware-panel-inspector.webp',
  'site/landing-showcase.webp',
] as const;

const CHECKLIST_MAX_BYTES = 500 * 1024;
const SITE_WEBP_MAX_BYTES = 250 * 1024;
const EXPECTED_TOTAL_FIGURES = 17;

const BASE_RENDER_STEMS = new Set(BASE_RENDERS.map((rel) => path.posix.parse(rel).name));
const FRAMED_CAPTURE_STEMS = new Set(
  [...CHECKLIST_PNGS, ...SITE_WEBPS].map((rel) => path.posix.parse(rel).name),
);
const ALL_IMAGE_STEMS = new Set([...BASE_RENDER_STEMS, ...FRAMED_CAPTURE_STEMS]);

interface ExpectedPromptSpec {
  title: string;
  spine: string;
  inChain: boolean;
  hasConnectorBefore: boolean;
}

const EXPECTED_PROMPTS_BY_ROUTE: Readonly<Record<string, readonly ExpectedPromptSpec[]>> = {
  '/stages/01-hardware-agent-skills/': [
    {
      title: 'AI Agent Prompt — Living Context Map Bootstrap',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
  ],
  '/stages/02-sketch-extraction-and-critique/': [
    {
      title: 'AI Agent Prompt — Sketch Extraction',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
    {
      title: 'AI Agent Prompt — Quantitative Circuit Critique',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
  ],
  '/stages/03-design-spec-and-dft/': [
    {
      title: 'AI Agent Prompt — Interactive Design Q&A',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
    {
      title: 'Turn 1 — Test-Point Options',
      spine: 'T1',
      inChain: true,
      hasConnectorBefore: false,
    },
    {
      title: 'Turn 2 — Lock All 12 Test Points',
      spine: 'T2',
      inChain: true,
      hasConnectorBefore: true,
    },
  ],
  '/stages/04-skidl-and-schematic/': [
    {
      title: 'AI Agent Prompt — SKiDL Circuit Capture',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
    {
      title: 'Turn 1 — Generate KiCad Schematic',
      spine: 'T1',
      inChain: true,
      hasConnectorBefore: false,
    },
    {
      title: 'Turn 2 — Export PDF & Commit',
      spine: 'T2',
      inChain: true,
      hasConnectorBefore: true,
    },
  ],
  '/stages/05-main-pcb-and-silkscreen/': [
    {
      title: 'AI Agent Prompt — Generate 6 HP Main PCB',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
    {
      title: 'Turn 1 — Declarative Silkscreen Strategy',
      spine: 'T1',
      inChain: true,
      hasConnectorBefore: false,
    },
    {
      title: 'Turn 2 — Extract silk_layout.json',
      spine: 'T2',
      inChain: true,
      hasConnectorBefore: true,
    },
  ],
  '/stages/08-wayfinder-site-planning/': [
    {
      title: 'AI Agent Prompt — Chart Wayfinder Map',
      spine: 'PROMPT',
      inChain: false,
      hasConnectorBefore: false,
    },
  ],
};

const FORBIDDEN_PROMPT_HEADING_RE =
  /^#{1,6}\s+(?:AI\s+Agent\s+Prompts?|Motivating\s+Prompts?)\b/m;
const PROTOTYPE_LEFTOVERS = [
  'prototype-switcher',
  'prototype-theme',
  'prototype-variants',
  'data-proto-variant',
] as const;
const TABLIST_RE =
  /(?:role\s*=\s*["']tablist["']|setAttribute\(\s*["']role["']\s*,\s*["']tablist["'])/;

function stripFencedCodeBlocks(source: string): string {
  return source.replace(/^(`{3,}|~{3,})[^\n]*\r?\n[\s\S]*?^\1[ \t]*$/gm, '');
}

const EXPECTED_MERMAID_BY_MDX: Readonly<Record<string, number>> = {
  'index.mdx': 1,
  'stages/03-design-spec-and-dft.mdx': 1,
  'stages/06-front-panel-and-artwork.mdx': 1,
  'stages/07-fabrication-checklists-and-patches.mdx': 1,
  'stages/08-wayfinder-site-planning.mdx': 1,
  'stages/09-companion-site-delivery.mdx': 2,
  'optional/ac-dc-input-coupling.mdx': 1,
};

const EXPECTED_MERMAID_BY_ROUTE: Readonly<Record<string, number>> = {
  '/': 1,
  '/stages/03-design-spec-and-dft/': 1,
  '/stages/06-front-panel-and-artwork/': 1,
  '/stages/07-fabrication-checklists-and-patches/': 1,
  '/stages/08-wayfinder-site-planning/': 1,
  '/stages/09-companion-site-delivery/': 2,
  '/optional/ac-dc-input-coupling/': 1,
};

const MATH_ROUTES = new Set<string>([
  '/',
  '/stages/02-sketch-extraction-and-critique/',
  '/stages/03-design-spec-and-dft/',
  '/optional/ac-dc-input-coupling/',
]);

const MERMAID_BLOCK_RE = /```mermaid[ \t]*\r?\n([\s\S]*?)```/g;
const MERMAID_HEX_STYLE_RE = /^\s*(?:style|classDef)\b[^\n]*#[0-9a-fA-F]{3,8}\b/m;
const MERMAID_EDGE_ARROW_RE = /\s*(?:<[-.=]+|[-.=]+>|--+|==+|\.-\.)(?:\|[^|]*\|)?\s*/;
const MERMAID_NODE_ID_RE = /^\s*([A-Za-z_][A-Za-z0-9_-]*)/;
const MERMAID_KEYWORDS = new Set([
  'flowchart',
  'graph',
  'subgraph',
  'direction',
  'style',
  'classDef',
]);

function hasMixedLrSubgraphCrossEdges(diagram: string): boolean {
  const subgraphStack: { hasLr: boolean; nodes: Set<string> }[] = [];
  const lrSubgraphs: Set<string>[] = [];
  const edges: [string, string][] = [];

  for (const rawLine of diagram.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('%%')) {
      continue;
    }
    if (line.startsWith('subgraph ')) {
      subgraphStack.push({ hasLr: false, nodes: new Set<string>() });
      continue;
    }
    if (line === 'end' && subgraphStack.length > 0) {
      const finished = subgraphStack.pop()!;
      if (finished.hasLr) {
        lrSubgraphs.push(finished.nodes);
      }
      continue;
    }
    if (/^direction\s+LR\b/i.test(line) && subgraphStack.length > 0) {
      subgraphStack[subgraphStack.length - 1]!.hasLr = true;
      continue;
    }

    const parts = line.split(MERMAID_EDGE_ARROW_RE);
    const lineNodes: string[] = [];
    for (const part of parts) {
      const match = MERMAID_NODE_ID_RE.exec(part);
      if (match?.[1] && !MERMAID_KEYWORDS.has(match[1])) {
        const nodeId = match[1];
        lineNodes.push(nodeId);
        for (const sg of subgraphStack) {
          sg.nodes.add(nodeId);
        }
      }
    }

    if (parts.length > 1 && lineNodes.length >= 2) {
      for (let i = 0; i < lineNodes.length - 1; i += 1) {
        edges.push([lineNodes[i]!, lineNodes[i + 1]!]);
      }
    }
  }

  for (const sgNodes of lrSubgraphs) {
    for (const [src, dst] of edges) {
      if (sgNodes.has(src) !== sgNodes.has(dst)) {
        return true;
      }
    }
  }
  return false;
}

const UNPINNED_MAIN_RE =
  /EnvelopeFollowerWithSkewLimiter\/(?:blob|tree)\/(?:main|HEAD)(?:\/|(?=["')\s>#?]|$))/;
const PINNED_REF_SHA_RE =
  /https:\/\/github\.com\/domesticmouse\/EnvelopeFollowerWithSkewLimiter\/(blob|tree)\/([0-9a-f]{7,40})(?:\/([^\s)"'>]*))?(?=["')\s>#?]|$)/g;
const LOCAL_MAIN_RE =
  /https:\/\/github\.com\/domesticmouse\/EnvelopeFollower\/(blob|tree)\/main\/([^\s)"'>]+)/g;
const MD_LINK_RE = /!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
const HTML_ATTR_LINK_RE = /\b(?:href|src)\s*=\s*["']([^"']+)["']/gi;
const COMPANION_SPECS_URL =
  'https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/specs/';

export const AVOIDED_GLOSSARY_PATTERNS: readonly [string, RegExp][] = [
  ['codelab', /\bcodelabs?\b/i],
  ['docs site', /\bdocs\s+sites?\b/i],
  ['documentation portal', /\bdocumentation\s+portals?\b/i],
  ['module website', /\bmodule\s+websites?\b/i],
  ['base sketch', /\bbase\s+sketch(?:es)?\b/i],
  ['original diagram', /\boriginal\s+diagrams?\b/i],
  ['reference schematic', /\breference\s+schematics?\b/i],
  ['reference section', /\breference\s+sections?\b/i],
  ['reference docs', /\breference\s+docs\b/i],
  ['technical references', /\btechnical\s+references?\b/i],
  ['master build checklist', /\bmaster\s+build\s+checklists?\b/i],
  ['fabrication checklist', /\bfabrication\s+checklists?\b/i],
  ['prompt card', /\bprompt\s+cards?\b/i],
  ['blockquote prompt', /\bblockquote\s+prompts?\b/i],
  ['raw prompt', /\braw\s+prompts?\b/i],
  ['motivating prompt', /\bmotivating\s+prompts?\b/i],
  ['conversation log', /\bconversation\s+logs?\b/i],
  ['chat log', /\bchat\s+logs?\b/i],
  ['prompt log', /\bprompt\s+logs?\b/i],
  ['build session', /\bbuild\s+sessions?\b/i],
  ['tracker log', /\btracker\s+logs?\b/i],
  ['github history', /\bgithub\s+history\b/i],
  ['issue trail', /\bissue\s+trails?\b/i],
  ['decision log', /\bdecision\s+logs?\b/i],
  ['context anchor', /\bcontext\s+anchors?\b/i],
  ['agent readme', /\bagent\s+readme\b/i],
  ['workspace index', /\bworkspace\s+index\b/i],
  ['github front door', /\bgithub\s+front\s+door\b/i],
  ['compact readme', /\bcompact\s+readme\b/i],
  ['landing readme', /\blanding\s+readme\b/i],
  ['Optional Branch', /\bOptional\s+Branch(?:es)?\b/i],
  ['EnvFollower', /\bEnvFollower\b/i],
  ['EFSL', /\bEFSL\b/i],
  ['SkewFollower', /\bSkewFollower\b/i],
];

function safeDecodeURIComponent(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function resolveDistFile(distDir: string, sitePathname: string): string | null {
  const withoutQuery = (sitePathname.split('?')[0] ?? '').split('#')[0] ?? '';
  if (!withoutQuery.startsWith(`${SITE_BASE}/`)) {
    return null;
  }
  const rel = safeDecodeURIComponent(withoutQuery.slice(SITE_BASE.length + 1));
  if (!rel) {
    return null;
  }
  const abs = path.resolve(distDir, rel);
  const relFromDist = path.relative(distDir, abs);
  if (relFromDist.startsWith('..') || path.isAbsolute(relFromDist)) {
    return null;
  }
  if (fs.existsSync(abs) && fs.statSync(abs).isFile()) {
    return abs;
  }
  return null;
}

function routeToHtmlRelPath(route: string): string {
  const normalized = normalizeRoutePath(route);
  return normalized === '/' ? 'index.html' : `${normalized.slice(1)}index.html`;
}

function walkFiles(dirAbs: string, baseDir: string, skipPagefind = false): string[] {
  const out: string[] = [];
  if (!fs.existsSync(dirAbs)) {
    return out;
  }
  const stack: string[] = [dirAbs];
  while (stack.length > 0) {
    const current = stack.pop()!;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const absPath = path.join(current, entry.name);
      const relPath = path.relative(baseDir, absPath).replaceAll('\\', '/');
      if (skipPagefind && (relPath === 'pagefind' || relPath.startsWith('pagefind/'))) {
        continue;
      }
      if (entry.isDirectory()) {
        stack.push(absPath);
      } else if (entry.isFile()) {
        out.push(relPath);
      }
    }
  }
  return out.sort();
}

function checkRoutesExclusionsAndPagefind(
  distDir: string,
  allDistFilesNoPagefind: readonly string[],
  requirePagefind: boolean,
  errors: string[],
): void {
  const expectedHtmlSet = new Set(CANONICAL_ROUTES.map(routeToHtmlRelPath));

  for (const route of CANONICAL_ROUTES) {
    const relHtml = routeToHtmlRelPath(route);
    const fullPath = path.join(distDir, relHtml);
    if (!fs.existsSync(fullPath) || !fs.statSync(fullPath).isFile()) {
      errors.push(`[Group 1] Missing canonical built route: ${route} (${relHtml})`);
    }
  }

  for (const excluded of EXCLUDED_SITE_DIRS) {
    if (fs.existsSync(path.join(distDir, excluded)) || fs.existsSync(path.join(distDir, 'docs', excluded))) {
      errors.push(`[Group 1] Excluded directory leaked into built site: ${excluded}`);
    }
  }

  for (const relFile of allDistFilesNoPagefind) {
    for (const excluded of EXCLUDED_SITE_DIRS) {
      if (
        relFile === excluded ||
        relFile.startsWith(`${excluded}/`) ||
        relFile.startsWith(`docs/${excluded}/`)
      ) {
        errors.push(`[Group 1] Excluded file leaked into built site: ${relFile}`);
      }
    }
    if (relFile.endsWith('.html') && !expectedHtmlSet.has(relFile)) {
      errors.push(`[Group 1] Unexpected HTML route outside the 13 canonical routes: ${relFile}`);
    }
  }

  if (requirePagefind) {
    for (const artifact of ['pagefind/pagefind.js', 'pagefind/pagefind-entry.json']) {
      const fullPath = path.join(distDir, artifact);
      if (!fs.existsSync(fullPath) || fs.statSync(fullPath).size === 0) {
        errors.push(`[Group 1] Missing or empty Pagefind artifact: dist/${artifact}`);
      }
    }
  }
}

function checkPagefindBoundariesAndDialogs(
  route: string,
  doc: Document,
  errors: string[],
): void {
  if (!doc.querySelector('head meta[name="color-scheme"][content="dark"]')) {
    errors.push(`[Group 1] ${route}: missing <meta name="color-scheme" content="dark"> in <head>`);
  }
  const h1Count = doc.querySelectorAll('h1').length;
  if (h1Count !== 1) {
    errors.push(`[Group 1] ${route}: expected exactly 1 <h1>, found ${h1Count}`);
  }
  if (!doc.querySelector('h1[data-pagefind-body]')) {
    errors.push(`[Group 1] ${route}: missing h1[data-pagefind-body] indexing boundary`);
  }
  if (!doc.querySelector('article[data-pagefind-body]')) {
    errors.push(`[Group 1] ${route}: missing article[data-pagefind-body] indexing boundary`);
  }

  const ignoreSelectors = [
    'header.c-header[data-pagefind-ignore]',
    'dialog#mobile-nav-drawer[data-pagefind-ignore]',
    'aside.left-rail[data-pagefind-ignore]',
    ...(route !== '/' ? ['nav.breadcrumbs[data-pagefind-ignore]'] : []),
    'aside.right-toc[data-pagefind-ignore]',
    'nav.prev-next-nav[data-pagefind-ignore]',
    'footer.site-footer[data-pagefind-ignore]',
    'dialog#site-search-dialog[data-pagefind-ignore]',
    'dialog#figure-lightbox[data-pagefind-ignore]',
  ];
  for (const selector of ignoreSelectors) {
    if (!doc.querySelector(selector)) {
      errors.push(`[Group 1] ${route}: missing indexing exclusion "${selector}"`);
    }
  }

  if (!doc.querySelector('[data-search-trigger]')) {
    errors.push(`[Group 1] ${route}: missing [data-search-trigger] header button`);
  }
  if (!doc.querySelector('dialog[data-search-dialog][closedby="any"]')) {
    errors.push(`[Group 1] ${route}: missing native <dialog data-search-dialog closedby="any">`);
  }
  if (!doc.querySelector('dialog[data-figure-lightbox][closedby="any"]')) {
    errors.push(`[Group 1] ${route}: missing native <dialog data-figure-lightbox closedby="any">`);
  }
}

function checkTypographyAndCssBundles(
  distDir: string,
  allDistFilesNoPagefind: readonly string[],
  errors: string[],
): void {
  const woff2Files = allDistFilesNoPagefind.filter((f) => f.endsWith('.woff2'));
  for (const family of REQUIRED_FONT_FAMILIES) {
    if (!woff2Files.some((f) => path.posix.basename(f).includes(family))) {
      errors.push(`[Group 2] Missing self-hosted .woff2 bundle for font family: ${family}`);
    }
  }

  for (const relFile of allDistFilesNoPagefind) {
    if (relFile.endsWith('.css')) {
      const css = fs.readFileSync(path.join(distDir, relFile), 'utf8');
      if (/https?:\/\//i.test(css)) {
        errors.push(`[Group 2] External URL found in built CSS ${relFile}`);
      }
      for (const domain of EXTERNAL_CDN_DOMAINS) {
        if (css.toLowerCase().includes(domain)) {
          errors.push(`[Group 2] External CDN reference (${domain}) in built CSS ${relFile}`);
        }
      }
    } else if (relFile.endsWith('.js')) {
      const js = fs.readFileSync(path.join(distDir, relFile), 'utf8');
      for (const domain of EXTERNAL_CDN_DOMAINS) {
        if (js.toLowerCase().includes(domain)) {
          errors.push(`[Group 2] External CDN reference (${domain}) in built JS ${relFile}`);
        }
      }
    }
  }
}

function checkRouteLinksAssetsAndScripts(
  route: string,
  rawHtml: string,
  doc: Document,
  distDir: string,
  parsedDocs: ReadonlyMap<string, { win: Window; doc: Document }>,
  errors: string[],
): { verifiedImages: number; verifiedLinks: number } {
  let verifiedImages = 0;
  let verifiedLinks = 0;

  const lowerHtml = rawHtml.toLowerCase();
  for (const domain of EXTERNAL_CDN_DOMAINS) {
    if (lowerHtml.includes(domain)) {
      errors.push(`[Group 2] ${route}: disallowed external CDN/font reference (${domain})`);
    }
  }

  for (const el of doc.querySelectorAll('script[src], link[href]')) {
    const attr = el.hasAttribute('src') ? 'src' : 'href';
    const ref = el.getAttribute(attr)?.trim() ?? '';
    if (!ref) continue;
    if (
      el.tagName.toLowerCase() === 'link' &&
      el.getAttribute('rel') === 'canonical' &&
      ref.startsWith(`${SITE_ORIGIN}${SITE_BASE}/`)
    ) {
      continue;
    }
    if (/^(?:https?:)?\/\//i.test(ref)) {
      errors.push(`[Group 2] ${route}: external asset reference in <${el.tagName.toLowerCase()} ${attr}> (${ref})`);
    }
  }

  for (const script of doc.querySelectorAll('script:not([src])')) {
    const inlineCode = script.textContent ?? '';
    if (/^\s*import\s+(?:[\w*{]|['"])/m.test(inlineCode)) {
      errors.push(`[Group 2] ${route}: unbundled inline ESM import in <script> without src`);
    }
  }

  const mainScripts = doc.querySelectorAll('main script');
  if (mainScripts.length > 0) {
    errors.push(
      `[Group 2] ${route}: found ${mainScripts.length} <script> element(s) inside <main>`,
    );
  }

  for (const img of doc.querySelectorAll('img')) {
    if (img.hasAttribute('data-figure-lightbox-img') && img.closest('dialog[data-figure-lightbox]')) {
      continue;
    }
    const src = img.getAttribute('src')?.trim() ?? '';
    const width = img.getAttribute('width')?.trim() ?? '';
    const height = img.getAttribute('height')?.trim() ?? '';
    if (!POSITIVE_INT_RE.test(width) || !POSITIVE_INT_RE.test(height)) {
      errors.push(`[Group 2] ${route}: <img> missing positive integer width/height (${src || 'unnamed'})`);
    }
    if (!src || !resolveDistFile(distDir, src)) {
      errors.push(`[Group 2] ${route}: <img> src does not resolve inside dist (${src || 'empty'})`);
    } else {
      verifiedImages += 1;
    }
  }

  for (const anchor of doc.querySelectorAll('a[href]')) {
    const href = anchor.getAttribute('href')?.trim() ?? '';
    if (!href) {
      errors.push(`[Group 2] ${route}: empty <a href>`);
      continue;
    }
    if (EXTERNAL_PROTO_RE.test(href)) {
      verifiedLinks += 1;
      continue;
    }
    if (href.startsWith('#')) {
      const fragment = safeDecodeURIComponent(href.slice(1));
      if (!fragment || !doc.getElementById(fragment)) {
        errors.push(`[Group 2] ${route}: broken in-page fragment anchor ${href}`);
      } else {
        verifiedLinks += 1;
      }
      continue;
    }
    if (href !== SITE_BASE && !href.startsWith(`${SITE_BASE}/`)) {
      errors.push(`[Group 2] ${route}: internal link missing ${SITE_BASE}/ prefix (${href})`);
      continue;
    }

    const hashIdx = href.indexOf('#');
    const pathname = hashIdx === -1 ? href : href.slice(0, hashIdx);
    const fragment = hashIdx === -1 ? '' : safeDecodeURIComponent(href.slice(hashIdx + 1));
    const normalizedTarget = normalizeRoutePath(pathname);

    if (CANONICAL_ROUTE_SET.has(normalizedTarget)) {
      if (fragment) {
        const targetDoc = parsedDocs.get(normalizedTarget)?.doc;
        if (!targetDoc?.getElementById(fragment)) {
          errors.push(`[Group 2] ${route}: broken cross-page fragment anchor ${href}`);
          continue;
        }
      }
      verifiedLinks += 1;
      continue;
    }

    if (!resolveDistFile(distDir, pathname)) {
      errors.push(`[Group 2] ${route}: internal link targets missing route or file (${href})`);
      continue;
    }
    verifiedLinks += 1;
  }

  return { verifiedImages, verifiedLinks };
}

function checkSourceImages(assetsImagesDir: string, errors: string[]): void {
  for (const rel of BASE_RENDERS) {
    const fullPath = path.join(assetsImagesDir, rel);
    if (!fs.existsSync(fullPath) || !fs.statSync(fullPath).isFile()) {
      errors.push(`[Group 3] Missing base render source image: ${rel}`);
    }
  }
  for (const rel of CHECKLIST_PNGS) {
    const fullPath = path.join(assetsImagesDir, rel);
    if (!fs.existsSync(fullPath) || !fs.statSync(fullPath).isFile()) {
      errors.push(`[Group 3] Missing checklist PNG source image: ${rel}`);
    } else if (fs.statSync(fullPath).size > CHECKLIST_MAX_BYTES) {
      errors.push(
        `[Group 3] Checklist PNG exceeds 500 KiB (${fs.statSync(fullPath).size} B): ${rel}`,
      );
    }
  }
  for (const rel of SITE_WEBPS) {
    const fullPath = path.join(assetsImagesDir, rel);
    if (!fs.existsSync(fullPath) || !fs.statSync(fullPath).isFile()) {
      errors.push(`[Group 3] Missing Companion Site WebP source image: ${rel}`);
    } else if (fs.statSync(fullPath).size > SITE_WEBP_MAX_BYTES) {
      errors.push(
        `[Group 3] Companion Site WebP exceeds 250 KiB (${fs.statSync(fullPath).size} B): ${rel}`,
      );
    }
  }
}

function checkVisualFiguresAndSvg(
  parsedDocs: ReadonlyMap<string, { win: Window; doc: Document; rawHtml: string }>,
  distDir: string,
  errors: string[],
): number {
  let totalFigures = 0;
  const seenStems = new Set<string>();

  for (const [route, { doc }] of parsedDocs) {
    for (const svg of doc.querySelectorAll('svg')) {
      const markup = svg.outerHTML;
      if (markup.includes('_03_Registration_Frame') || markup.includes('registration_frame')) {
        errors.push(`[Group 3] ${route}: registration frame leaked into rendered <svg>`);
      }
    }
    if (route === '/' && !doc.querySelector('svg.faceplate-svg')) {
      errors.push('[Group 3] /: missing assembled 6 HP faceplate SVG (svg.faceplate-svg)');
    }

    for (const img of doc.querySelectorAll('img')) {
      if (img.getAttribute('fetchpriority') === 'high' && img.getAttribute('loading') === 'lazy') {
        errors.push(
          `[Group 3] ${route}: priority image must never pair fetchpriority="high" with loading="lazy"`,
        );
      }
    }

    const figures = [...doc.querySelectorAll('article figure.tutorial-figure')];
    totalFigures += figures.length;

    for (const figure of figures) {
      const img = figure.querySelector('img');
      if (!img) {
        errors.push(`[Group 3] ${route}: <figure.tutorial-figure> missing <img>`);
        continue;
      }

      const trigger = figure.querySelector('button[data-lightbox-trigger]');
      const lightboxSrc = trigger?.getAttribute('data-lightbox-src')?.trim() ?? '';
      if (!trigger || !lightboxSrc || !resolveDistFile(distDir, lightboxSrc)) {
        errors.push(
          `[Group 3] ${route}: zoomable <Figure> missing valid [data-lightbox-trigger] / data-lightbox-src`,
        );
      }

      const src = img.getAttribute('src')?.trim() ?? '';
      const basename = path.posix.basename((src.split('?')[0] ?? '').split('#')[0] ?? '');
      const stem = basename.split('.')[0] ?? '';
      if (!ALL_IMAGE_STEMS.has(stem)) {
        errors.push(`[Group 3] ${route}: <Figure> image stem "${stem}" is not in the 14-image catalog`);
        continue;
      }
      seenStems.add(stem);

      const isFramed = figure.classList.contains('is-framed');
      if (BASE_RENDER_STEMS.has(stem) && isFramed) {
        errors.push(
          `[Group 3] ${route}: transparent base render "${stem}" must remain unframed (no .is-framed)`,
        );
      } else if (FRAMED_CAPTURE_STEMS.has(stem) && !isFramed) {
        errors.push(
          `[Group 3] ${route}: checklist/site capture "${stem}" must be framed (.is-framed)`,
        );
      }
    }
  }

  if (totalFigures !== EXPECTED_TOTAL_FIGURES) {
    errors.push(
      `[Group 3] Expected ${EXPECTED_TOTAL_FIGURES} <Figure> instances across built site, found ${totalFigures}`,
    );
  }
  for (const stem of ALL_IMAGE_STEMS) {
    if (!seenStems.has(stem)) {
      errors.push(`[Group 3] Source image "${stem}" is never rendered in any <Figure>`);
    }
  }

  return totalFigures;
}

function checkPromptBlocksAndEditorialFidelity(
  parsedDocs: ReadonlyMap<string, { win: Window; doc: Document; rawHtml: string }>,
  distDir: string,
  allDistFilesNoPagefind: readonly string[],
  mdxFiles: readonly { relPath: string; content: string }[],
  errors: string[],
): number {
  let totalPrompts = 0;
  let totalChains = 0;
  let totalConnectors = 0;

  for (const [route, { doc }] of parsedDocs) {
    const expected = EXPECTED_PROMPTS_BY_ROUTE[route] ?? [];
    const strips = [...doc.querySelectorAll('.c-patch-strip')];
    totalPrompts += strips.length;
    totalChains += doc.querySelectorAll('.c-patch-chain').length;
    totalConnectors += doc.querySelectorAll('.c-patch-connector').length;

    if (strips.length !== expected.length) {
      errors.push(
        `[Group 4] ${route}: expected ${expected.length} <PromptBlock> (.c-patch-strip) elements, found ${strips.length}`,
      );
    } else {
      for (let i = 0; i < strips.length; i += 1) {
        const strip = strips[i]!;
        const spec = expected[i]!;
        const title = strip.querySelector('.c-patch-title span')?.textContent?.trim() ?? '';
        const spine = strip.querySelector('.c-patch-label')?.textContent?.trim() ?? '';
        const inChain = Boolean(strip.closest('.c-patch-chain'));
        const hasConnectorBefore = Boolean(
          strip.previousElementSibling?.classList.contains('c-patch-connector'),
        );

        if (title !== spec.title) {
          errors.push(
            `[Group 4] ${route} prompt #${i + 1}: expected title ${JSON.stringify(spec.title)}, found ${JSON.stringify(title)}`,
          );
        }
        if (spine !== spec.spine) {
          errors.push(
            `[Group 4] ${route} prompt #${i + 1}: expected spine ${JSON.stringify(spec.spine)}, found ${JSON.stringify(spine)}`,
          );
        }
        if (inChain !== spec.inChain) {
          errors.push(
            `[Group 4] ${route} prompt #${i + 1} (${title}): expected in .c-patch-chain=${spec.inChain}, got ${inChain}`,
          );
        }
        if (hasConnectorBefore !== spec.hasConnectorBefore) {
          errors.push(
            `[Group 4] ${route} prompt #${i + 1} (${title}): expected preceding .c-patch-connector=${spec.hasConnectorBefore}, got ${hasConnectorBefore}`,
          );
        }

        const bodyText = strip.querySelector('.c-patch-text')?.textContent?.trim() ?? '';
        if (
          (bodyText.startsWith('"') && bodyText.endsWith('"')) ||
          (bodyText.startsWith('“') && bodyText.endsWith('”')) ||
          (bodyText.startsWith('*"') && bodyText.endsWith('"*'))
        ) {
          errors.push(
            `[Group 4] ${route} prompt #${i + 1} (${title}): retains outer quote wrapper`,
          );
        }
      }
    }
  }

  if (totalPrompts !== 13) {
    errors.push(`[Group 4] Expected 13 total <PromptBlock> outputs across built site, found ${totalPrompts}`);
  }
  if (totalChains !== 3) {
    errors.push(`[Group 4] Expected 3 <PromptGroup> (.c-patch-chain) containers, found ${totalChains}`);
  }
  if (totalConnectors !== 3) {
    errors.push(`[Group 4] Expected 3 .c-patch-connector elements, found ${totalConnectors}`);
  }

  const stage6Doc = parsedDocs.get('/stages/06-front-panel-and-artwork/')?.doc;
  if (stage6Doc && stage6Doc.querySelectorAll('article blockquote').length < 1) {
    errors.push('[Group 4] /stages/06-front-panel-and-artwork/: lost its editorial <blockquote>');
  }

  for (const { relPath, content } of mdxFiles) {
    const withoutFences = stripFencedCodeBlocks(content);
    if (FORBIDDEN_PROMPT_HEADING_RE.test(withoutFences)) {
      errors.push(`[Group 4] Forbidden standalone prompt heading in ${relPath}`);
    }
  }

  for (const relFile of allDistFilesNoPagefind) {
    if (!relFile.endsWith('.html') && !relFile.endsWith('.css') && !relFile.endsWith('.js')) {
      continue;
    }
    const text = fs.readFileSync(path.join(distDir, relFile), 'utf8');
    for (const token of PROTOTYPE_LEFTOVERS) {
      if (text.includes(token)) {
        errors.push(`[Group 4] Prototype leftover ${JSON.stringify(token)} found in dist/${relFile}`);
      }
    }
    if (TABLIST_RE.test(text)) {
      errors.push(`[Group 4] Prototype leftover role="tablist" found in dist/${relFile}`);
    }
  }

  return totalPrompts;
}

function checkKatexMermaidAndAppendix(
  parsedDocs: ReadonlyMap<string, { win: Window; doc: Document; rawHtml: string }>,
  distDir: string,
  allDistFilesNoPagefind: readonly string[],
  mdxFiles: readonly { relPath: string; content: string }[],
  errors: string[],
): void {
  // 1. MDX Mermaid guardrails (exact 8 blocks across 7 files, 0 hex style/classDef, 0 mixed LR cross-edges)
  let totalMermaidBlocks = 0;
  for (const { relPath, content } of mdxFiles) {
    const blocks = [...content.matchAll(MERMAID_BLOCK_RE)].map((m) => m[1] ?? '');
    const expected = EXPECTED_MERMAID_BY_MDX[relPath] ?? 0;
    totalMermaidBlocks += blocks.length;
    if (blocks.length !== expected) {
      errors.push(
        `[Group 5] ${relPath}: expected ${expected} mermaid block(s), found ${blocks.length}`,
      );
    }
    for (let i = 0; i < blocks.length; i += 1) {
      const block = blocks[i]!;
      if (MERMAID_HEX_STYLE_RE.test(block)) {
        errors.push(
          `[Group 5] ${relPath} mermaid block #${i + 1}: hardcoded inline style/classDef hex fill is forbidden`,
        );
      }
      if (hasMixedLrSubgraphCrossEdges(block)) {
        errors.push(
          `[Group 5] ${relPath} mermaid block #${i + 1}: mixed \`direction LR\` inside subgraph with cross-subgraph edge`,
        );
      }
    }
  }
  if (totalMermaidBlocks !== 8) {
    errors.push(`[Group 5] Expected 8 total mermaid blocks across MDX sources, found ${totalMermaidBlocks}`);
  }

  // 2. Built JS bundles must never use localStorage
  for (const relFile of allDistFilesNoPagefind) {
    if (!relFile.endsWith('.js')) continue;
    const js = fs.readFileSync(path.join(distDir, relFile), 'utf8');
    if (js.includes('localStorage')) {
      errors.push(`[Group 5] Forbidden localStorage usage in built JS bundle dist/${relFile}`);
    }
  }

  // 3. Per-route Mermaid isolation, KaTeX CSS/render checks, and Appendix static checklists
  for (const [route, { doc }] of parsedDocs) {
    const expectedMermaid = EXPECTED_MERMAID_BY_ROUTE[route] ?? 0;
    const mermaidCards = doc.querySelectorAll('.mermaid-card[data-pagefind-ignore] pre.mermaid');
    const mermaidEls = doc.querySelectorAll('.mermaid');

    if (expectedMermaid > 0) {
      if (mermaidCards.length !== expectedMermaid) {
        errors.push(
          `[Group 5] ${route}: expected ${expectedMermaid} .mermaid-card[data-pagefind-ignore] pre.mermaid block(s), found ${mermaidCards.length}`,
        );
      }
      const hasMermaidScript = [...doc.querySelectorAll('script[src]')].some((s) =>
        /mermaid/i.test(s.getAttribute('src') ?? ''),
      );
      if (!hasMermaidScript) {
        errors.push(`[Group 5] ${route}: missing Mermaid hydrator script on diagram route`);
      }
    } else {
      if (mermaidEls.length > 0) {
        errors.push(`[Group 5] ${route}: unexpected .mermaid block on non-diagram route`);
      }
      for (const script of doc.querySelectorAll('script')) {
        const src = script.getAttribute('src')?.trim() ?? '';
        if (!src) {
          if (/mermaid/i.test(script.textContent ?? '')) {
            errors.push(`[Group 5] ${route}: unexpected inline Mermaid script on non-diagram route`);
          }
          continue;
        }
        if (/mermaid/i.test(src)) {
          errors.push(`[Group 5] ${route}: unexpected Mermaid script bundle (${src}) on non-diagram route`);
          continue;
        }
        const resolved = resolveDistFile(distDir, src);
        if (resolved && /mermaid/i.test(fs.readFileSync(resolved, 'utf8'))) {
          errors.push(`[Group 5] ${route}: referenced script imports or mentions Mermaid (${src})`);
        }
      }
    }

    if (doc.querySelectorAll('.katex-error').length > 0) {
      errors.push(`[Group 5] ${route}: rendered .katex-error detected`);
    }
    const hasKatexCss = [...doc.querySelectorAll('link[rel="stylesheet"]')].some((l) =>
      /katex/i.test(l.getAttribute('href') ?? ''),
    );
    const katexCount = doc.querySelectorAll('.katex').length;
    if (MATH_ROUTES.has(route)) {
      if (!hasKatexCss) {
        errors.push(`[Group 5] ${route}: missing self-hosted KaTeX CSS stylesheet on math route`);
      }
      if (katexCount === 0) {
        errors.push(`[Group 5] ${route}: expected rendered .katex math expressions`);
      }
      if (route === '/optional/ac-dc-input-coupling/' && doc.querySelectorAll('.katex-display').length === 0) {
        errors.push(`[Group 5] ${route}: expected rendered .katex-display equation`);
      }
    } else {
      if (hasKatexCss) {
        errors.push(`[Group 5] ${route}: unexpected KaTeX CSS stylesheet on non-math route`);
      }
      if (katexCount > 0) {
        errors.push(`[Group 5] ${route}: unexpected .katex nodes on non-math route`);
      }
    }

    for (const script of doc.querySelectorAll('script')) {
      if ((script.textContent ?? '').includes('localStorage')) {
        errors.push(`[Group 5] ${route}: forbidden localStorage usage in inline <script>`);
      }
    }

    const checkboxes = [...doc.querySelectorAll('article input[type="checkbox"]')];
    const topLevelCheckboxes = checkboxes.filter(
      (cb) => !cb.closest('li')?.parentElement?.closest('li'),
    );
    for (const cb of checkboxes) {
      if (!cb.hasAttribute('disabled')) {
        errors.push(`[Group 5] ${route}: checklist checkbox must be read-only (disabled)`);
      }
    }

    if (route === '/appendix/engineering-sign-off-checklist/') {
      if (topLevelCheckboxes.length !== 20 || checkboxes.length !== 66) {
        errors.push(
          `[Group 5] ${route}: expected 20 top-level / 66 total checklist items, found ${topLevelCheckboxes.length} / ${checkboxes.length}`,
        );
      }
    } else if (route === '/appendix/netlist-and-bom/') {
      if (topLevelCheckboxes.length !== 9 || checkboxes.length !== 9) {
        errors.push(
          `[Group 5] ${route}: expected 9 top-level / 9 total checklist items, found ${topLevelCheckboxes.length} / ${checkboxes.length}`,
        );
      }
    } else if (checkboxes.length > 0) {
      errors.push(`[Group 5] ${route}: unexpected interactive or checklist checkboxes (${checkboxes.length})`);
    }
  }
}

function normalizeGithubSubpath(rawSubpath: string): string {
  const withoutHash = rawSubpath.split('#')[0] ?? '';
  const withoutQuery = withoutHash.split('?')[0] ?? '';
  return safeDecodeURIComponent(withoutQuery).replace(/\/+$/, '');
}

function resolveSafeSubpath(
  baseRoot: string,
  kind: string,
  refLabel: string,
  rawSubpath: string,
  relSource: string,
  errors: string[],
): string | null {
  const subpath = normalizeGithubSubpath(rawSubpath);
  if (!subpath) {
    return '';
  }
  const target = path.resolve(baseRoot, subpath);
  const relFromBase = path.relative(baseRoot, target);
  if (
    subpath.startsWith('/') ||
    subpath.split('/').includes('..') ||
    relFromBase.startsWith('..') ||
    path.isAbsolute(relFromBase)
  ) {
    errors.push(`[Group 6] ${relSource}: ${kind}/${refLabel}/${rawSubpath} escapes target root`);
    return null;
  }
  return relFromBase.replaceAll('\\', '/');
}

function verifyGithubTarget(
  baseRoot: string,
  kind: string,
  rawSubpath: string,
  relSource: string,
  refLabel: string,
  errors: string[],
): void {
  const safeSubpath = resolveSafeSubpath(baseRoot, kind, refLabel, rawSubpath, relSource, errors);
  if (safeSubpath === null) {
    return;
  }
  if (!safeSubpath) {
    if (kind === 'tree' && fs.existsSync(baseRoot) && fs.statSync(baseRoot).isDirectory()) {
      return;
    }
    errors.push(`[Group 6] ${relSource}: missing target for ${kind}/${refLabel}/${rawSubpath}`);
    return;
  }
  const target = path.resolve(baseRoot, safeSubpath);
  const exists =
    fs.existsSync(target) &&
    (kind === 'blob' ? fs.statSync(target).isFile() : fs.statSync(target).isDirectory());
  if (!exists) {
    errors.push(`[Group 6] ${relSource}: missing target for ${kind}/${refLabel}/${rawSubpath}`);
  }
}

function isGitCheckout(referenceDir: string): boolean {
  return fs.existsSync(path.join(referenceDir, '.git'));
}

function createGitReferenceVerifier(referenceDir: string) {
  const gitCheckout = isGitCheckout(referenceDir);
  const objectTypeCache = new Map<string, string | null>();
  let shallowCache: boolean | null = null;

  const runGit = (args: string[]): string | null => {
    try {
      return execFileSync('git', ['-C', referenceDir, ...args], {
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'pipe'],
      }).trim();
    } catch {
      return null;
    }
  };

  const catFileType = (objectSpec: string): string | null => {
    if (objectTypeCache.has(objectSpec)) {
      return objectTypeCache.get(objectSpec) ?? null;
    }
    const result = runGit(['cat-file', '-t', objectSpec]);
    objectTypeCache.set(objectSpec, result);
    return result;
  };

  const isShallow = (): boolean => {
    if (shallowCache === null) {
      shallowCache = runGit(['rev-parse', '--is-shallow-repository']) === 'true';
    }
    return shallowCache;
  };

  return {
    isGitCheckout: gitCheckout,
    headShortSha: (): string | null => (gitCheckout ? runGit(['rev-parse', '--short=7', 'HEAD']) : null),
    verifyPinnedTarget: (
      kind: string,
      sha: string,
      rawSubpath: string,
      relSource: string,
      errors: string[],
    ): void => {
      const safeSubpath = resolveSafeSubpath(
        referenceDir,
        kind,
        sha,
        rawSubpath,
        relSource,
        errors,
      );
      if (safeSubpath === null) {
        return;
      }
      if (!safeSubpath && kind === 'blob') {
        errors.push(`[Group 6] ${relSource}: blob/${sha} requires a file subpath`);
        return;
      }
      if (gitCheckout) {
        const shaType = catFileType(sha);
        if (shaType === 'commit') {
          if (!safeSubpath) {
            if (kind !== 'tree') {
              errors.push(`[Group 6] ${relSource}: ${kind}/${sha} requires a subpath`);
            }
            return;
          }
          const entryType = catFileType(`${sha}:${safeSubpath}`);
          if (entryType !== kind) {
            errors.push(
              `[Group 6] ${relSource}: missing or mismatched ${kind} target for ${kind}/${sha}/${rawSubpath} (git object type: ${entryType ?? 'missing'})`,
            );
          }
          return;
        }
        if (!isShallow()) {
          errors.push(
            `[Group 6] ${relSource}: unresolvable commit SHA ${sha} for ${kind}/${sha}${rawSubpath ? `/${rawSubpath}` : ''}`,
          );
          return;
        }
      }
      verifyGithubTarget(referenceDir, kind, safeSubpath, relSource, sha, errors);
    },
  };
}

function checkRootDocLinks(
  repoRoot: string,
  docPath: string,
  distDir: string,
  parsedDocs: ReadonlyMap<string, { win: Window; doc: Document; rawHtml: string }>,
  errors: string[],
): void {
  const relDoc = path.relative(repoRoot, docPath).replaceAll('\\', '/');
  const raw = fs.readFileSync(docPath, 'utf8');
  const stripped = stripFencedCodeBlocks(raw).replace(/`[^`\n]*`/g, '');
  const candidates: string[] = [];

  for (const match of stripped.matchAll(MD_LINK_RE)) {
    if (match[1]) candidates.push(match[1]);
  }
  for (const match of stripped.matchAll(HTML_ATTR_LINK_RE)) {
    if (match[1]) candidates.push(match[1]);
  }

  const pagesOriginPrefix = `${SITE_ORIGIN}${SITE_BASE}`;
  for (const rawTarget of candidates) {
    const target = rawTarget.trim();
    if (!target || target.startsWith('#') || /^(?:mailto|tel|data):/i.test(target)) {
      continue;
    }

    if (target.startsWith('http://') || target.startsWith('https://')) {
      if (target === pagesOriginPrefix || target.startsWith(`${pagesOriginPrefix}/`)) {
        const sitePath = target.slice(SITE_ORIGIN.length);
        const hashIdx = sitePath.indexOf('#');
        const pathname = hashIdx === -1 ? sitePath : sitePath.slice(0, hashIdx);
        const fragment = hashIdx === -1 ? '' : safeDecodeURIComponent(sitePath.slice(hashIdx + 1));
        const normalizedRoute = normalizeRoutePath(pathname);
        if (CANONICAL_ROUTE_SET.has(normalizedRoute)) {
          if (fragment && parsedDocs.has(normalizedRoute)) {
            if (!parsedDocs.get(normalizedRoute)?.doc.getElementById(fragment)) {
              errors.push(`[Group 6] ${relDoc}: broken live tutorial anchor (${target})`);
            }
          }
          continue;
        }
        if (resolveDistFile(distDir, pathname)) {
          continue;
        }
        errors.push(`[Group 6] ${relDoc}: broken live tutorial Pages URL (${target})`);
      }
      continue;
    }

    const cleanRel = safeDecodeURIComponent((target.split('#')[0] ?? '').split('?')[0] ?? '');
    if (!cleanRel) continue;
    const absTarget = path.resolve(path.dirname(docPath), cleanRel);
    const relFromRoot = path.relative(repoRoot, absTarget);
    if (relFromRoot.startsWith('..') || path.isAbsolute(relFromRoot) || !fs.existsSync(absTarget)) {
      errors.push(`[Group 6] ${relDoc}: broken relative link (${target})`);
    }
  }
}

function checkOutboundPinningRepoLinksAndGlossary(
  repoRoot: string,
  distDir: string,
  referenceDir: string,
  requireReference: boolean,
  mdxFiles: readonly { relPath: string; absPath: string; content: string }[],
  parsedDocs: ReadonlyMap<string, { win: Window; doc: Document; rawHtml: string }>,
  errors: string[],
  warnings: string[],
): void {
  const readmePath = path.join(repoRoot, 'README.md');
  const potPath = path.join(repoRoot, 'PotentialImprovements.md');

  const scanDocs: { relPath: string; content: string }[] = [];
  for (const p of [readmePath, potPath]) {
    if (fs.existsSync(p) && fs.statSync(p).isFile()) {
      scanDocs.push({
        relPath: path.relative(repoRoot, p).replaceAll('\\', '/'),
        content: fs.readFileSync(p, 'utf8'),
      });
    }
  }
  for (const mdx of mdxFiles) {
    scanDocs.push({
      relPath: path.relative(repoRoot, mdx.absPath).replaceAll('\\', '/'),
      content: mdx.content,
    });
  }
  for (const subdir of ['docs/agents', 'docs/adr', 'docs/research']) {
    const absSubdir = path.join(repoRoot, subdir);
    for (const rel of walkFiles(absSubdir, repoRoot)) {
      if (rel.endsWith('.md')) {
        scanDocs.push({
          relPath: rel,
          content: fs.readFileSync(path.join(repoRoot, rel), 'utf8'),
        });
      }
    }
  }

  for (const doc of scanDocs) {
    if (UNPINNED_MAIN_RE.test(doc.content)) {
      errors.push(
        `[Group 6] ${doc.relPath}: contains unpinned EnvelopeFollowerWithSkewLimiter/{blob,tree}/{main,HEAD} link`,
      );
    }
    if (doc.content.includes('TutorialUpdateTodo.md')) {
      errors.push(`[Group 6] ${doc.relPath}: references deleted TutorialUpdateTodo.md`);
    }
    for (const match of doc.content.matchAll(LOCAL_MAIN_RE)) {
      if (match[1] && match[2]) {
        verifyGithubTarget(repoRoot, match[1], match[2], doc.relPath, 'main', errors);
      }
    }
  }

  const refVerifier = createGitReferenceVerifier(referenceDir);
  const refPopulated =
    fs.existsSync(referenceDir) &&
    fs.statSync(referenceDir).isDirectory() &&
    fs.readdirSync(referenceDir).length > 0;
  if (!refPopulated) {
    const msg = `Reference submodule directory is uninitialized/empty (${referenceDir}); skipping pinned target resolution.`;
    if (requireReference) {
      errors.push(`[Group 6] ${msg} (--require-reference / GITHUB_ACTIONS=true)`);
    } else {
      warnings.push(`[Group 6] ${msg}`);
    }
  } else {
    for (const doc of scanDocs) {
      for (const match of doc.content.matchAll(PINNED_REF_SHA_RE)) {
        if (match[1] && match[2]) {
          refVerifier.verifyPinnedTarget(match[1], match[2], match[3] ?? '', doc.relPath, errors);
        }
      }
    }
  }

  if (fs.existsSync(path.join(repoRoot, 'TutorialUpdateTodo.md'))) {
    errors.push('[Group 6] Superseded TutorialUpdateTodo.md still exists on disk');
  }

  if (!fs.existsSync(readmePath) || !fs.statSync(readmePath).isFile()) {
    errors.push('[Group 6] Missing root README.md');
  } else {
    const readmeContent = fs.readFileSync(readmePath, 'utf8');
    checkRootDocLinks(repoRoot, readmePath, distDir, parsedDocs, errors);
    if (readmeContent.includes('analysis/capability_mode.json')) {
      errors.push('[Group 6] README.md still references analysis/capability_mode.json');
    }
    if (refVerifier.isGitCheckout) {
      const headShortSha = refVerifier.headShortSha();
      if (!headShortSha) {
        errors.push(`[Group 6] Unable to resolve HEAD short SHA in ${referenceDir}`);
      } else if (!readmeContent.includes(headShortSha)) {
        errors.push(
          `[Group 6] README.md does not reference current reference/ HEAD SHA (${headShortSha})`,
        );
      }
    }
  }

  if (!fs.existsSync(potPath) || !fs.statSync(potPath).isFile()) {
    errors.push('[Group 6] Missing root PotentialImprovements.md');
  } else {
    checkRootDocLinks(repoRoot, potPath, distDir, parsedDocs, errors);
    const potText = fs.readFileSync(potPath, 'utf8');
    if (!potText.includes('Note for ENV / SKEW builders')) {
      errors.push("[Group 6] PotentialImprovements.md missing 'Note for ENV / SKEW builders' callout");
    }
    if (!potText.includes(COMPANION_SPECS_URL)) {
      errors.push(
        `[Group 6] PotentialImprovements.md missing live Companion Site link ${COMPANION_SPECS_URL}`,
      );
    }
  }

  const glossaryTargets: { relPath: string; content: string }[] = [
    ...mdxFiles.map((m) => ({
      relPath: path.relative(repoRoot, m.absPath).replaceAll('\\', '/'),
      content: m.content,
    })),
  ];
  if (fs.existsSync(readmePath) && fs.statSync(readmePath).isFile()) {
    glossaryTargets.push({ relPath: 'README.md', content: fs.readFileSync(readmePath, 'utf8') });
  }
  if (fs.existsSync(potPath) && fs.statSync(potPath).isFile()) {
    glossaryTargets.push({
      relPath: 'PotentialImprovements.md',
      content: fs.readFileSync(potPath, 'utf8'),
    });
  }

  for (const target of glossaryTargets) {
    const lines = target.content.split(/\r?\n/);
    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i]!;
      for (const [term, pattern] of AVOIDED_GLOSSARY_PATTERNS) {
        if (pattern.test(line)) {
          errors.push(
            `[Group 6] ${target.relPath}:${i + 1}: avoided GLOSSARY.md term ${JSON.stringify(term)}`,
          );
        }
      }
    }
  }
}

/** Verify built Astro output and repository contract invariants across all 6 contract groups. */
export function verifyBuiltSite(options: VerifyBuiltSiteOptions): SiteContractResult {
  const distDir = path.resolve(options.distDir);
  const repoRoot = path.resolve(options.repoRoot);
  const mdxDir = path.resolve(options.mdxDir ?? path.join(repoRoot, 'site/src/content/tutorial'));
  const assetsImagesDir = path.resolve(
    options.assetsImagesDir ?? path.join(repoRoot, 'site/src/assets/images'),
  );
  const referenceDir = path.resolve(options.referenceDir ?? path.join(repoRoot, 'reference'));
  const requireReference = options.requireReference ?? false;
  const requirePagefind = options.requirePagefind ?? true;

  const errors: string[] = [];
  const warnings: string[] = [];
  const checkedHtmlRoutes: string[] = [];
  let verifiedImages = 0;
  let verifiedLinks = 0;
  let verifiedFigures = 0;
  let verifiedPrompts = 0;

  checkSourceImages(assetsImagesDir, errors);
  const mdxFiles = walkFiles(mdxDir, mdxDir)
    .filter((rel) => rel.endsWith('.mdx'))
    .map((rel) => {
      const absPath = path.join(mdxDir, rel);
      return {
        relPath: rel,
        absPath,
        content: fs.readFileSync(absPath, 'utf8'),
      };
    });

  if (!fs.existsSync(distDir) || !fs.statSync(distDir).isDirectory()) {
    return {
      checkedHtmlRoutes,
      verifiedImages,
      verifiedLinks,
      verifiedFigures,
      verifiedPrompts,
      errors: [...errors, `[Group 1] Built site directory does not exist: ${distDir}`],
      warnings,
    };
  }

  const allDistFilesNoPagefind = walkFiles(distDir, distDir, true);
  checkRoutesExclusionsAndPagefind(distDir, allDistFilesNoPagefind, requirePagefind, errors);
  checkTypographyAndCssBundles(distDir, allDistFilesNoPagefind, errors);

  const parsedDocs = new Map<string, { win: Window; doc: Document; rawHtml: string }>();
  try {
    for (const route of CANONICAL_ROUTES) {
      const htmlPath = path.join(distDir, routeToHtmlRelPath(route));
      if (!fs.existsSync(htmlPath) || !fs.statSync(htmlPath).isFile()) {
        continue;
      }
      const rawHtml = fs.readFileSync(htmlPath, 'utf8');
      const win = new Window({ url: `${SITE_ORIGIN}${SITE_BASE}${route}` });
      win.document.write(rawHtml);
      const doc = win.document as unknown as Document;
      parsedDocs.set(route, { win, doc, rawHtml });
      checkedHtmlRoutes.push(route);
    }

    for (const [route, { doc, rawHtml }] of parsedDocs) {
      checkPagefindBoundariesAndDialogs(route, doc, errors);
      const counts = checkRouteLinksAssetsAndScripts(route, rawHtml, doc, distDir, parsedDocs, errors);
      verifiedImages += counts.verifiedImages;
      verifiedLinks += counts.verifiedLinks;
    }

    verifiedFigures = checkVisualFiguresAndSvg(parsedDocs, distDir, errors);
    verifiedPrompts = checkPromptBlocksAndEditorialFidelity(
      parsedDocs,
      distDir,
      allDistFilesNoPagefind,
      mdxFiles,
      errors,
    );
    checkKatexMermaidAndAppendix(
      parsedDocs,
      distDir,
      allDistFilesNoPagefind,
      mdxFiles,
      errors,
    );
    checkOutboundPinningRepoLinksAndGlossary(
      repoRoot,
      distDir,
      referenceDir,
      requireReference,
      mdxFiles,
      parsedDocs,
      errors,
      warnings,
    );
  } finally {
    for (const { win } of parsedDocs.values()) {
      win.close();
    }
  }

  return {
    checkedHtmlRoutes,
    verifiedImages,
    verifiedLinks,
    verifiedFigures,
    verifiedPrompts,
    errors,
    warnings,
  };
}
