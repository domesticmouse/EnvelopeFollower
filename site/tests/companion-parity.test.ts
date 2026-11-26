// @vitest-environment node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import {
  ALLOWED_SITE_SPECIFIC_TOKENS,
  LOCKED_CORE_TOKENS,
  SHARED_BYTE_IDENTICAL_FILES,
  verifyCompanionParity,
} from '../src/lib/companion-parity.ts';

const tempDirs: string[] = [];

function writeFile(filePath: string, content: string | Buffer): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
}

const SHARED_DEPENDENCIES: Record<string, string> = {
  '@astrojs/markdown-remark': '^7.3.10',
  '@fontsource/barlow-condensed': '^5.3.0',
  '@fontsource/ibm-plex-mono': '^5.3.0',
  '@fontsource/ibm-plex-sans': '^5.3.0',
  '@fontsource/space-grotesk': '^5.3.0',
  astro: '^7.4.13',
  'github-slugger': '^2.0.0',
  'invokers-polyfill': '^1.0.5',
  katex: '^0.19.1',
  mermaid: '^12.3.0',
  'rehype-katex': '^7.0.1',
  'remark-math': '^6.0.0',
  'unist-util-visit': '^5.2.0',
};

const SHARED_DEV_DEPENDENCIES: Record<string, string> = {
  '@astrojs/check': '^0.9.12',
  '@types/hast': '^3.0.5',
  '@types/mdast': '^4.0.4',
  '@types/node': '^24.0.0',
  'happy-dom': '^21.0.4',
  pagefind: '^1.6.0',
  typescript: '^5.9.3',
  vitest: '^5.1.1',
};

const CORE_TOKENS_BODY = `  color-scheme: dark;
  --bg-void: #0d0e11;
  --bg-canvas: #141518;
  --bg-surface: #1b1d22;
  --bg-surface-elevated: #1d2028;
  --bg-code: #090a0d;
  --bg-code-elevated: #101216;
  --ink-primary: #e8eaef;
  --ink-silk: #f4f5f7;
  --ink-muted: #a6acb8;
  --accent-gold: #d8b154;
  --accent-gold-bright: #e2be66;
  --accent-gold-ink: #141518;
  --accent-gold-tint: #262013;
  --border-ui: #6e7485;
  --border-subtle: #2b2f3b;
  --border-grid: #323642;
  --led-green: #4ade80;
  --led-green-bg: #102819;
  --led-red: #f87171;
  --led-red-bg: #2c1416;
  --led-amber: #fbbf24;
  --led-amber-bg: #291e09;
  --scrollbar-thumb: #7b8294;
  --scrollbar-track: #141518;
  --font-slab: 'Barlow Condensed', 'DIN Condensed', 'Arial Narrow', system-ui, sans-serif;
  --font-display: 'Space Grotesk', system-ui, -apple-system, sans-serif;
  --font-body: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --focus-ring: 2px solid var(--accent-gold-bright);
  accent-color: var(--accent-gold);
  scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);`;

function createValidParityFixture(): { repoRoot: string; referenceDir: string } {
  const { repoRoot, referenceDir } = createTempRepo();
  const siteDir = path.join(repoRoot, 'site');
  const refSiteDir = path.join(referenceDir, 'site');

  writeFile(
    path.join(siteDir, 'package.json'),
    JSON.stringify(
      {
        name: 'env-skew-build-tutorial',
        private: true,
        engines: { node: '>=24.0.0' },
        dependencies: { ...SHARED_DEPENDENCIES, '@astrojs/mdx': '^8.1.6' },
        devDependencies: { ...SHARED_DEV_DEPENDENCIES },
      },
      null,
      2,
    ),
  );
  writeFile(
    path.join(refSiteDir, 'package.json'),
    JSON.stringify(
      {
        name: 'env-skew-site',
        private: true,
        engines: { node: '>=24.0.0' },
        dependencies: { ...SHARED_DEPENDENCIES },
        devDependencies: {
          ...SHARED_DEV_DEPENDENCIES,
          'rehype-raw': '^7.0.0',
          'rehype-stringify': '^10.0.1',
          'remark-gfm': '^4.0.1',
          'remark-parse': '^11.0.0',
          'remark-rehype': '^11.1.2',
          unified: '^11.0.5',
        },
      },
      null,
      2,
    ),
  );

  for (const relPath of SHARED_BYTE_IDENTICAL_FILES) {
    const content = `// shared file: ${relPath}\n`;
    writeFile(path.join(siteDir, relPath), content);
    writeFile(path.join(refSiteDir, relPath), content);
  }

  writeFile(
    path.join(siteDir, 'src/styles/tokens.css'),
    `/* Build Tutorial tokens */\n:root {\n${CORE_TOKENS_BODY}\n  --accent-gold-link: #d8b154;\n  --page-max-inline: 1380px;\n}\n`,
  );
  writeFile(
    path.join(refSiteDir, 'src/styles/tokens.css'),
    `/* Companion Site tokens */\n:root {\n${CORE_TOKENS_BODY}\n  --led-dark: #c5cad4;\n  --led-dark-bg: #1e2128;\n  --page-max-inline: 1200px;\n}\n`,
  );

  writeFile(
    path.join(repoRoot, '.github/workflows/docs.yml'),
    `jobs:\n  build:\n    env:\n      ASTRO_TELEMETRY_DISABLED: '1'\n    steps:\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '24'\n`,
  );
  writeFile(
    path.join(referenceDir, '.github/workflows/deploy-pages.yml'),
    `jobs:\n  build:\n    env:\n      ASTRO_TELEMETRY_DISABLED: '1'\n    steps:\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '24'\n`,
  );

  return { repoRoot, referenceDir };
}

function createTempRepo(): { repoRoot: string; referenceDir: string } {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'env-skew-companion-parity-'));
  tempDirs.push(root);
  const repoRoot = path.join(root, 'repo');
  const referenceDir = path.join(repoRoot, 'reference');
  fs.mkdirSync(path.join(repoRoot, 'site'), { recursive: true });
  return { repoRoot, referenceDir };
}

afterEach(() => {
  while (tempDirs.length > 0) {
    const dir = tempDirs.pop();
    if (dir) fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe('companion-parity verifier', () => {
  it('exports the expected shared files, locked tokens, and site-specific token allowlist', () => {
    expect(SHARED_BYTE_IDENTICAL_FILES).toHaveLength(9);
    expect(LOCKED_CORE_TOKENS).toHaveLength(32);
    expect(ALLOWED_SITE_SPECIFIC_TOKENS).toHaveLength(4);
  });

  it('passes cleanly with 0 errors and 0 warnings when all parity surfaces match', () => {
    const { repoRoot, referenceDir } = createValidParityFixture();
    const result = verifyCompanionParity({
      repoRoot,
      referenceDir,
      requireReference: true,
    });
    expect(result.errors).toEqual([]);
    expect(result.warnings).toEqual([]);
  });

  it('fails with [Group 7] error on engines.node or shared dependency range mismatch, while allowing repo-specific packages and differing package-lock.json', () => {
    // 1. Differing package-lock.json and repo-specific packages pass cleanly
    const okFixture = createValidParityFixture();
    writeFile(path.join(okFixture.repoRoot, 'site/package-lock.json'), '{"lockfileVersion":3,"packages":{"a":{}}}');
    writeFile(path.join(okFixture.referenceDir, 'site/package-lock.json'), '{"lockfileVersion":3,"packages":{"b":{}}}');
    const okResult = verifyCompanionParity({
      ...okFixture,
      requireReference: true,
    });
    expect(okResult.errors).toEqual([]);
    expect(okResult.warnings).toEqual([]);

    // 2. engines.node, shared dependencies, shared devDependencies, and missing shared package fail
    const badFixture = createValidParityFixture();
    const sitePkgPath = path.join(badFixture.repoRoot, 'site/package.json');
    const sitePkg = JSON.parse(fs.readFileSync(sitePkgPath, 'utf8'));
    sitePkg.engines.node = '>=22.0.0';
    sitePkg.dependencies.astro = '^7.4.0';
    sitePkg.devDependencies.vitest = '^5.0.0';
    delete sitePkg.dependencies.katex;
    writeFile(sitePkgPath, JSON.stringify(sitePkg, null, 2));

    const badResult = verifyCompanionParity({
      ...badFixture,
      requireReference: true,
    });
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('engines.node'))).toBe(true);
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('astro'))).toBe(true);
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('vitest'))).toBe(true);
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('katex'))).toBe(true);
  });

  it('fails with [Group 7] error on single-byte drift or missing file among the 9 shared files', () => {
    const { repoRoot, referenceDir } = createValidParityFixture();

    const driftedFile = SHARED_BYTE_IDENTICAL_FILES[0];
    fs.appendFileSync(path.join(referenceDir, 'site', driftedFile), ' ');

    const missingFile = SHARED_BYTE_IDENTICAL_FILES[4];
    fs.rmSync(path.join(repoRoot, 'site', missingFile));

    const result = verifyCompanionParity({
      repoRoot,
      referenceDir,
      requireReference: true,
    });

    expect(result.errors.some((e) => e.startsWith('[Group 7]') && e.includes(driftedFile))).toBe(true);
    expect(result.errors.some((e) => e.startsWith('[Group 7]') && e.includes(missingFile))).toBe(true);
  });

  it('verifies core tokens.css parity while ignoring CSS comments/whitespace and allowing site-specific tokens, and rejects drifted/missing/unknown :root tokens', () => {
    // 1. CSS comment/whitespace differences + allowed site-specific tokens pass
    const okFixture = createValidParityFixture();
    writeFile(
      path.join(okFixture.referenceDir, 'site/src/styles/tokens.css'),
      `/* Leading comment */\n:root {\n  /* inline comment */\n${CORE_TOKENS_BODY.replace('--accent-gold: #d8b154;', '--accent-gold:   #d8b154; /* ENIG gold */')}\n  --led-dark: #c5cad4;\n  --led-dark-bg: #1e2128;\n  --page-max-inline: 1200px;\n}\n`,
    );
    const okResult = verifyCompanionParity({
      ...okFixture,
      requireReference: true,
    });
    expect(okResult.errors).toEqual([]);
    expect(okResult.warnings).toEqual([]);

    // 2. Modified locked token, missing locked token, and unexpected unknown token fail
    const badFixture = createValidParityFixture();
    const siteTokensPath = path.join(badFixture.repoRoot, 'site/src/styles/tokens.css');
    const siteTokens = fs
      .readFileSync(siteTokensPath, 'utf8')
      .replace('--accent-gold: #d8b154;', '--accent-gold: #e0b858;')
      .replace('  --bg-void: #0d0e11;\n', '')
      .replace('}', '  --unexpected-token: #123456;\n}');
    writeFile(siteTokensPath, siteTokens);

    const refTokensPath = path.join(badFixture.referenceDir, 'site/src/styles/tokens.css');
    writeFile(
      refTokensPath,
      fs.readFileSync(refTokensPath, 'utf8').replace('}', '  --ref-unknown: 4px;\n}'),
    );

    const badResult = verifyCompanionParity({
      ...badFixture,
      requireReference: true,
    });
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('--accent-gold'))).toBe(true);
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('--bg-void'))).toBe(true);
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('--unexpected-token'))).toBe(true);
    expect(badResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('--ref-unknown'))).toBe(true);
  });

  it('fails with [Group 7] error on CI workflow node-version mismatch or missing/wrong ASTRO_TELEMETRY_DISABLED', () => {
    const mismatchFixture = createValidParityFixture();
    writeFile(
      path.join(mismatchFixture.repoRoot, '.github/workflows/docs.yml'),
      `jobs:\n  build:\n    env:\n      ASTRO_TELEMETRY_DISABLED: '0'\n    steps:\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '22'\n`,
    );

    const mismatchResult = verifyCompanionParity({
      ...mismatchFixture,
      requireReference: true,
    });
    expect(mismatchResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('node-version'))).toBe(true);
    expect(
      mismatchResult.errors.some((e) => e.startsWith('[Group 7]') && e.includes('ASTRO_TELEMETRY_DISABLED')),
    ).toBe(true);

    const missingTelemetryFixture = createValidParityFixture();
    writeFile(
      path.join(missingTelemetryFixture.referenceDir, '.github/workflows/deploy-pages.yml'),
      `jobs:\n  build:\n    steps:\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '24'\n`,
    );

    const missingTelemetryResult = verifyCompanionParity({
      ...missingTelemetryFixture,
      requireReference: true,
    });
    expect(
      missingTelemetryResult.errors.some(
        (e) => e.startsWith('[Group 7]') && e.includes('ASTRO_TELEMETRY_DISABLED'),
      ),
    ).toBe(true);
  });

  it('warns when reference/ or reference/site/ is absent/empty locally and fails when requireReference is true or GITHUB_ACTIONS=true', () => {
    const { repoRoot, referenceDir } = createTempRepo();

    // 1. Absent reference/
    const absentLocal = verifyCompanionParity({
      repoRoot,
      referenceDir,
      requireReference: false,
    });
    expect(absentLocal.errors).toEqual([]);
    expect(absentLocal.warnings).toHaveLength(1);
    expect(absentLocal.warnings[0]).toMatch(/^\[Group 7\]/);

    const absentRequired = verifyCompanionParity({
      repoRoot,
      referenceDir,
      requireReference: true,
    });
    expect(absentRequired.warnings).toEqual([]);
    expect(absentRequired.errors).toHaveLength(1);
    expect(absentRequired.errors[0]).toMatch(/^\[Group 7\]/);

    // 2. Empty reference/site/
    fs.mkdirSync(path.join(referenceDir, 'site'), { recursive: true });
    const emptySiteLocal = verifyCompanionParity({
      repoRoot,
      referenceDir,
      requireReference: false,
    });
    expect(emptySiteLocal.errors).toEqual([]);
    expect(emptySiteLocal.warnings).toHaveLength(1);
    expect(emptySiteLocal.warnings[0]).toMatch(/^\[Group 7\]/);

    // 3. Omitted requireReference falls back to GITHUB_ACTIONS=true
    const prevActions = process.env.GITHUB_ACTIONS;
    try {
      process.env.GITHUB_ACTIONS = 'true';
      const ciFallback = verifyCompanionParity({ repoRoot, referenceDir });
      expect(ciFallback.warnings).toEqual([]);
      expect(ciFallback.errors).toHaveLength(1);
      expect(ciFallback.errors[0]).toMatch(/^\[Group 7\]/);

      delete process.env.GITHUB_ACTIONS;
      const localFallback = verifyCompanionParity({ repoRoot, referenceDir });
      expect(localFallback.errors).toEqual([]);
      expect(localFallback.warnings).toHaveLength(1);
      expect(localFallback.warnings[0]).toMatch(/^\[Group 7\]/);
    } finally {
      if (prevActions === undefined) {
        delete process.env.GITHUB_ACTIONS;
      } else {
        process.env.GITHUB_ACTIONS = prevActions;
      }
    }
  });
});
