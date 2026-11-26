import fs from 'node:fs';
import path from 'node:path';

/** Configuration options for Build Tutorial vs. Companion Site parity verification. */
export interface VerifyCompanionParityOptions {
  repoRoot: string;
  referenceDir?: string;
  requireReference?: boolean;
}

/** Parity check errors and warnings prefixed with `[Group 7]`. */
export interface CompanionParityResult {
  errors: string[];
  warnings: string[];
}

/** Shared infrastructure files that must remain byte-identical between `site/` and `reference/site/`. */
export const SHARED_BYTE_IDENTICAL_FILES = [
  'src/components/MermaidHydrator.astro',
  'tsconfig.json',
  'vitest.config.ts',
  'src/styles/fonts.css',
  'src/lib/dialog-chrome.ts',
  'src/lib/mermaid-client.ts',
  'src/plugins/remark-double-dollar-math.ts',
  'tests/dialog-chrome.test.ts',
  'tests/mermaid-client.test.ts',
] as const;

/** Core `:root` design tokens locked across both repositories. */
export const LOCKED_CORE_TOKENS = [
  'color-scheme',
  '--bg-void',
  '--bg-canvas',
  '--bg-surface',
  '--bg-surface-elevated',
  '--bg-code',
  '--bg-code-elevated',
  '--ink-primary',
  '--ink-silk',
  '--ink-muted',
  '--accent-gold',
  '--accent-gold-bright',
  '--accent-gold-ink',
  '--accent-gold-tint',
  '--border-ui',
  '--border-subtle',
  '--border-grid',
  '--led-green',
  '--led-green-bg',
  '--led-red',
  '--led-red-bg',
  '--led-amber',
  '--led-amber-bg',
  '--scrollbar-thumb',
  '--scrollbar-track',
  '--font-slab',
  '--font-display',
  '--font-body',
  '--font-mono',
  '--focus-ring',
  'accent-color',
  'scrollbar-color',
] as const;

/** Intentional site-specific `:root` tokens allowed to differ between sites. */
export const ALLOWED_SITE_SPECIFIC_TOKENS = [
  '--led-dark',
  '--led-dark-bg',
  '--accent-gold-link',
  '--page-max-inline',
] as const;

interface PackageJsonManifest {
  engines?: { node?: unknown };
  dependencies?: Record<string, unknown>;
  devDependencies?: Record<string, unknown>;
}

const ALLOWED_SITE_ONLY_PACKAGES = new Set(['@astrojs/mdx']);

function isAllowedReferenceOnlyPackage(pkgName: string): boolean {
  return pkgName === 'unified' || pkgName.startsWith('remark-') || pkgName.startsWith('rehype-');
}

function readPackageJson(filePath: string, label: string, errors: string[]): PackageJsonManifest | null {
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    errors.push(`[Group 7] Missing ${label}`);
    return null;
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf8')) as unknown;
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      errors.push(`[Group 7] Invalid JSON object in ${label}`);
      return null;
    }
    return parsed as PackageJsonManifest;
  } catch {
    errors.push(`[Group 7] Failed to parse JSON in ${label}`);
    return null;
  }
}

function toStringRecord(value: unknown): Record<string, string> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {};
  }
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(value)) {
    if (typeof v === 'string') {
      out[k] = v;
    }
  }
  return out;
}

function checkPackageSection(
  section: 'dependencies' | 'devDependencies',
  siteMap: Record<string, string>,
  siteOtherMap: Record<string, string>,
  refMap: Record<string, string>,
  refOtherMap: Record<string, string>,
  errors: string[],
): void {
  const allNames = new Set([...Object.keys(siteMap), ...Object.keys(refMap)]);
  for (const name of [...allNames].sort()) {
    const siteRange = siteMap[name];
    const refRange = refMap[name];

    if (siteRange !== undefined && refRange !== undefined) {
      if (siteRange !== refRange) {
        errors.push(
          `[Group 7] package.json ${section}.${name} mismatch: site has ${JSON.stringify(siteRange)}, reference/site has ${JSON.stringify(refRange)}`,
        );
      }
      continue;
    }

    if (siteRange !== undefined) {
      if (refOtherMap[name] !== undefined) {
        errors.push(
          `[Group 7] package.json ${name} section mismatch: in site/${section} but in reference/site/${section === 'dependencies' ? 'devDependencies' : 'dependencies'}`,
        );
      } else if (!ALLOWED_SITE_ONLY_PACKAGES.has(name)) {
        errors.push(
          `[Group 7] package.json ${section}.${name} exists in site/ but is missing from reference/site/`,
        );
      }
      continue;
    }

    if (refRange !== undefined) {
      if (siteOtherMap[name] !== undefined) {
        // Already reported when scanning the other section
        continue;
      }
      if (!isAllowedReferenceOnlyPackage(name)) {
        errors.push(
          `[Group 7] package.json ${section}.${name} exists in reference/site/ but is missing from site/`,
        );
      }
    }
  }
}

function checkPackageJsonParity(
  siteDir: string,
  refSiteDir: string,
  errors: string[],
): void {
  const sitePkg = readPackageJson(path.join(siteDir, 'package.json'), 'site/package.json', errors);
  const refPkg = readPackageJson(
    path.join(refSiteDir, 'package.json'),
    'reference/site/package.json',
    errors,
  );
  if (!sitePkg || !refPkg) {
    return;
  }

  const siteNode = typeof sitePkg.engines?.node === 'string' ? sitePkg.engines.node : undefined;
  const refNode = typeof refPkg.engines?.node === 'string' ? refPkg.engines.node : undefined;
  if (!siteNode || !refNode || siteNode !== refNode) {
    errors.push(
      `[Group 7] package.json engines.node mismatch: site has ${JSON.stringify(siteNode ?? null)}, reference/site has ${JSON.stringify(refNode ?? null)}`,
    );
  }

  const siteDeps = toStringRecord(sitePkg.dependencies);
  const siteDevDeps = toStringRecord(sitePkg.devDependencies);
  const refDeps = toStringRecord(refPkg.dependencies);
  const refDevDeps = toStringRecord(refPkg.devDependencies);

  checkPackageSection('dependencies', siteDeps, siteDevDeps, refDeps, refDevDeps, errors);
  checkPackageSection('devDependencies', siteDevDeps, siteDeps, refDevDeps, refDeps, errors);
}

const LOCKED_CORE_TOKEN_SET = new Set<string>(LOCKED_CORE_TOKENS);
const ALLOWED_SITE_SPECIFIC_TOKEN_SET = new Set<string>(ALLOWED_SITE_SPECIFIC_TOKENS);

function stripCssComments(css: string): string {
  return css.replace(
    /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\/\*[\s\S]*?\*\//g,
    (_match, quoted: string | undefined) => quoted ?? '',
  );
}

function parseRootTokens(
  filePath: string,
  label: string,
  errors: string[],
): Map<string, string> | null {
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    errors.push(`[Group 7] Missing ${label}`);
    return null;
  }

  const stripped = stripCssComments(fs.readFileSync(filePath, 'utf8'));
  const rootMatches = [...stripped.matchAll(/:root\s*\{([^}]*)\}/g)];
  if (rootMatches.length === 0) {
    errors.push(`[Group 7] Missing :root declaration block in ${label}`);
    return null;
  }

  const tokens = new Map<string, string>();
  for (const match of rootMatches) {
    const body = match[1] ?? '';
    for (const rawDecl of body.split(';')) {
      const decl = rawDecl.trim();
      if (!decl) continue;
      const colonIdx = decl.indexOf(':');
      if (colonIdx === -1) {
        errors.push(`[Group 7] Malformed CSS declaration in ${label}: ${decl}`);
        continue;
      }
      const prop = decl.slice(0, colonIdx).replace(/\s+/g, ' ').trim();
      const val = decl.slice(colonIdx + 1).replace(/\s+/g, ' ').trim();
      if (prop) {
        tokens.set(prop, val);
      }
    }
  }
  return tokens;
}

function checkUnknownRootTokens(
  tokens: ReadonlyMap<string, string>,
  label: string,
  errors: string[],
): void {
  for (const key of tokens.keys()) {
    if (!LOCKED_CORE_TOKEN_SET.has(key) && !ALLOWED_SITE_SPECIFIC_TOKEN_SET.has(key)) {
      errors.push(`[Group 7] Unexpected :root token in ${label}: ${key}`);
    }
  }
}

function checkTokensCssParity(
  siteDir: string,
  refSiteDir: string,
  errors: string[],
): void {
  const siteTokens = parseRootTokens(
    path.join(siteDir, 'src/styles/tokens.css'),
    'site/src/styles/tokens.css',
    errors,
  );
  const refTokens = parseRootTokens(
    path.join(refSiteDir, 'src/styles/tokens.css'),
    'reference/site/src/styles/tokens.css',
    errors,
  );
  if (!siteTokens || !refTokens) {
    return;
  }

  checkUnknownRootTokens(siteTokens, 'site/src/styles/tokens.css', errors);
  checkUnknownRootTokens(refTokens, 'reference/site/src/styles/tokens.css', errors);

  for (const key of LOCKED_CORE_TOKENS) {
    const siteVal = siteTokens.get(key);
    const refVal = refTokens.get(key);
    if (siteVal === undefined) {
      errors.push(`[Group 7] Missing locked :root token in site/src/styles/tokens.css: ${key}`);
    }
    if (refVal === undefined) {
      errors.push(
        `[Group 7] Missing locked :root token in reference/site/src/styles/tokens.css: ${key}`,
      );
    }
    if (siteVal !== undefined && refVal !== undefined && siteVal !== refVal) {
      errors.push(
        `[Group 7] Locked :root token mismatch for ${key}: site has ${JSON.stringify(siteVal)}, reference/site has ${JSON.stringify(refVal)}`,
      );
    }
  }
}

interface WorkflowSettings {
  nodeVersion: string | null;
  astroTelemetryDisabled: string | null;
}

const EXPECTED_CI_NODE_VERSION = '24';
const EXPECTED_ASTRO_TELEMETRY = '1';

function stripYamlComment(line: string): string {
  let quote: '"' | "'" | null = null;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i]!;
    if (quote) {
      if (ch === quote && line[i - 1] !== '\\') {
        quote = null;
      }
      continue;
    }
    if (ch === '"' || ch === "'") {
      quote = ch;
      continue;
    }
    if (ch === '#' && (i === 0 || /\s/.test(line[i - 1]!))) {
      return line.slice(0, i);
    }
  }
  return line;
}

function unquoteYamlScalar(raw: string): string {
  const trimmed = raw.trim();
  if (
    (trimmed.startsWith("'") && trimmed.endsWith("'") && trimmed.length >= 2) ||
    (trimmed.startsWith('"') && trimmed.endsWith('"') && trimmed.length >= 2)
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function readWorkflowSettings(
  filePath: string,
  label: string,
  errors: string[],
): WorkflowSettings | null {
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    errors.push(`[Group 7] Missing CI workflow: ${label}`);
    return null;
  }

  let nodeVersion: string | null = null;
  let astroTelemetryDisabled: string | null = null;
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);

  for (const rawLine of lines) {
    const clean = stripYamlComment(rawLine);
    const nodeMatch = /^\s*node-version\s*:\s*(.+?)\s*$/.exec(clean);
    if (nodeMatch?.[1]) {
      nodeVersion = unquoteYamlScalar(nodeMatch[1]);
    }
    const telemetryMatch = /^\s*ASTRO_TELEMETRY_DISABLED\s*:\s*(.+?)\s*$/.exec(clean);
    if (telemetryMatch?.[1]) {
      astroTelemetryDisabled = unquoteYamlScalar(telemetryMatch[1]);
    }
  }

  return { nodeVersion, astroTelemetryDisabled };
}

function checkWorkflowParity(
  repoRoot: string,
  referenceDir: string,
  errors: string[],
): void {
  const siteWorkflow = readWorkflowSettings(
    path.join(repoRoot, '.github/workflows/docs.yml'),
    '.github/workflows/docs.yml',
    errors,
  );
  const refWorkflow = readWorkflowSettings(
    path.join(referenceDir, '.github/workflows/deploy-pages.yml'),
    'reference/.github/workflows/deploy-pages.yml',
    errors,
  );
  if (!siteWorkflow || !refWorkflow) {
    return;
  }

  for (const [_siteLabel, workflowPath, workflow] of [
    ['Build Tutorial', '.github/workflows/docs.yml', siteWorkflow],
    ['Companion Site', 'reference/.github/workflows/deploy-pages.yml', refWorkflow],
  ] as const) {
    if (workflow.nodeVersion !== EXPECTED_CI_NODE_VERSION) {
      errors.push(
        `[Group 7] ${workflowPath} node-version must be ${JSON.stringify(EXPECTED_CI_NODE_VERSION)}, got ${JSON.stringify(workflow.nodeVersion)}`,
      );
    }
    if (workflow.astroTelemetryDisabled !== EXPECTED_ASTRO_TELEMETRY) {
      errors.push(
        `[Group 7] ${workflowPath} ASTRO_TELEMETRY_DISABLED must be ${JSON.stringify(EXPECTED_ASTRO_TELEMETRY)}, got ${JSON.stringify(workflow.astroTelemetryDisabled)}`,
      );
    }
  }

  if (
    siteWorkflow.nodeVersion &&
    refWorkflow.nodeVersion &&
    siteWorkflow.nodeVersion !== refWorkflow.nodeVersion
  ) {
    errors.push(
      `[Group 7] CI workflow node-version mismatch: docs.yml has ${JSON.stringify(siteWorkflow.nodeVersion)}, deploy-pages.yml has ${JSON.stringify(refWorkflow.nodeVersion)}`,
    );
  }
}

/** Return true if `dirPath` exists on disk as a non-empty directory. */
export function isPopulatedDir(dirPath: string): boolean {
  return (
    fs.existsSync(dirPath) &&
    fs.statSync(dirPath).isDirectory() &&
    fs.readdirSync(dirPath).length > 0
  );
}

function checkSharedByteIdenticalFiles(
  siteDir: string,
  refSiteDir: string,
  errors: string[],
): void {
  for (const relPath of SHARED_BYTE_IDENTICAL_FILES) {
    const siteFile = path.join(siteDir, relPath);
    const refFile = path.join(refSiteDir, relPath);
    const siteExists = fs.existsSync(siteFile) && fs.statSync(siteFile).isFile();
    const refExists = fs.existsSync(refFile) && fs.statSync(refFile).isFile();

    if (!siteExists) {
      errors.push(`[Group 7] Missing shared file in site/: ${relPath}`);
      continue;
    }
    if (!refExists) {
      errors.push(`[Group 7] Missing shared file in reference/site/: ${relPath}`);
      continue;
    }

    const siteBytes = fs.readFileSync(siteFile);
    const refBytes = fs.readFileSync(refFile);
    if (!siteBytes.equals(refBytes)) {
      errors.push(`[Group 7] Shared file drifted from reference/site/: ${relPath}`);
    }
  }
}

/** Verify copy-aligned parity between `site/`, `.github/workflows/docs.yml`, and `reference/`. */
export function verifyCompanionParity(
  options: VerifyCompanionParityOptions,
): CompanionParityResult {
  const repoRoot = path.resolve(options.repoRoot);
  const siteDir = path.join(repoRoot, 'site');
  const referenceDir = path.resolve(options.referenceDir ?? path.join(repoRoot, 'reference'));
  const refSiteDir = path.join(referenceDir, 'site');
  const requireReference = options.requireReference ?? process.env.GITHUB_ACTIONS === 'true';

  const errors: string[] = [];
  const warnings: string[] = [];

  if (!isPopulatedDir(referenceDir) || !isPopulatedDir(refSiteDir)) {
    const msg = `Reference companion site directory is uninitialized/empty (${refSiteDir}); skipping companion parity checks.`;
    if (requireReference) {
      errors.push(`[Group 7] ${msg} (--require-reference / GITHUB_ACTIONS=true)`);
    } else {
      warnings.push(`[Group 7] ${msg}`);
    }
    return { errors, warnings };
  }

  checkPackageJsonParity(siteDir, refSiteDir, errors);
  checkSharedByteIdenticalFiles(siteDir, refSiteDir, errors);
  checkTokensCssParity(siteDir, refSiteDir, errors);
  checkWorkflowParity(repoRoot, referenceDir, errors);

  return { errors, warnings };
}
