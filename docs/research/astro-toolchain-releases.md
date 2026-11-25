# Research: Latest Astro and Shared Toolchain Releases Across Build Tutorial and Companion Site

- **Ticket:** [`domesticmouse/EnvelopeFollower#49`](https://github.com/domesticmouse/EnvelopeFollower/issues/49) (`wayfinder:research`, Parent Map: [`#48`](https://github.com/domesticmouse/EnvelopeFollower/issues/48))
- **Audit Date:** `2026-11-25`
- **Inspected Targets:**
  - **Build Tutorial** (`domesticmouse/EnvelopeFollower`, branch `feat/astro-core-tutorial-site`): `site/package.json`, `site/package-lock.json`, `site/astro.config.mjs`, `site/tsconfig.json`, `site/vitest.config.ts`, `site/scripts/check-site.ts`, `site/src/`, `.github/workflows/docs.yml` (note: `site/` does not yet exist on `main`)
  - **Companion Site** (`domesticmouse/EnvelopeFollowerWithSkewLimiter` submodule pinned at `8ad81d0` in `main`, inspected read-only at `reference/site/`): `package.json`, `package-lock.json`, `astro.config.mjs`, `tsconfig.json`, `vitest.config.ts`, `scripts/check-site.ts`, `src/`, `.github/workflows/deploy-pages.yml`
- **Primary Sources Verified:** npm registry metadata (`npm view` on `2026-11-25`), official Astro v6/v7 upgrade guides, Microsoft TypeScript 6.0/7.0 announcements & documentation, Node.js TypeScript type-stripping documentation, Mermaid v12 release notes, Pagefind v1.5/v1.6 release notes, Vitest v5 migration guide, Happy DOM v21 release notes, and KaTeX v0.19 release notes.

---

## Executive Summary

1. **Both repositories are already synchronized at the latest stable Astro 7 stack (`26` of `28` audited packages are at exact current `latest`):** Both the **Build Tutorial** (`feat/astro-core-tutorial-site:site/package.json`) and **Companion Site** (`reference/site/package.json`) already pin `astro@^7.4.13` (`7.4.13`), `@astrojs/markdown-remark@^7.3.10` (`7.3.10`), `@astrojs/check@^0.9.12` (`0.9.12`), `katex@^0.19.1` (`0.19.1`), `mermaid@^12.3.0` (`12.3.0`), `pagefind@^1.6.0` (`1.6.0`), `vitest@^5.1.1` (`5.1.1`), `happy-dom@^21.0.4` (`21.0.4`), `@fontsource/*@^5.3.0` (`5.3.0`), and the entire `unified` / `remark` / `rehype` stack at their latest stable versions (verified `2026-11-25`). The only direct dependency present exclusively in the **Build Tutorial** is `@astrojs/mdx@^8.1.6` (also already `latest`).
2. **Only two packages have newer major versions on npm — and both should be deferred:**
   - **`typescript` (`^5.9.3` pinned vs. `7.0.2` latest / `6.0.3` bridge):** Defer `7.0.2` (and `6.0.3`). `@astrojs/check@0.9.12` strictly declares `peerDependencies: { "typescript": "^5.0.0 || ^6.0.0" }` and breaks under TypeScript 7.0's native Go compiler (`tsgo`) without `@typescript/typescript6` aliasing or Astro language-tools updates. TypeScript 6.0 also changes `types` to default to `[]` and `rootDir` to `.`. Keeping `^5.9.3` preserves clean `astro check && tsc --noEmit` parity across both sites.
   - **`@types/node` (`^24.0.0` / `24.19.2` pinned vs. `26.6.10` latest):** Defer `26.x`. Both sites declare `engines.node: ">=24.0.0"` and execute CI (`docs.yml` and `deploy-pages.yml`) on **Node.js 24 LTS**. Upgrading `@types/node` to `^26.0.0` would let Node-26-only APIs pass `tsc --noEmit` while failing at runtime in Node 24 CI. Only a routine lockfile patch to `24.19.3` is safe if refreshing lockfiles.
3. **All Astro v6/v7, Mermaid v12, Vitest v5, Happy DOM v21, KaTeX v0.19, and Node 24 constraints are already satisfied by both architectures:**
   - Both sites explicitly retain `@astrojs/markdown-remark` with `markdown.processor: unified(...)` so Astro v7's default Rust Markdown pipeline (`@astrojs/markdown-satteri@0.4.10`) does not bypass their custom remark/rehype AST plugins.
   - Both sites already use `glob()` from `astro/loaders` in `src/content.config.ts`, `syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] }`, `strict: false` in `rehypeKatex`, explicit `theme: 'base'` in `mermaid-client.ts`, explicit `happy-dom` devDependencies, and strictly erasable TypeScript syntax (`allowImportingTsExtensions: true`, `noEmit: true`) for native `node scripts/check-site.ts` execution on Node 24 LTS.

---

## 1. Repository Baseline Comparison (`site/` vs. `reference/site/`)

Inspecting `feat/astro-core-tutorial-site:site/` and `reference/site/` shows an intentionally aligned toolchain and config structure:

| Aspect | Build Tutorial (`feat/astro-core-tutorial-site:site/`) | Companion Site (`reference/site/`, commit `8ad81d0`) |
| :--- | :--- | :--- |
| **Package Name** | `env-skew-build-tutorial` | `env-skew-site` |
| **Node Engine / CI Runtime** | `"node": ">=24.0.0"` (`docs.yml`: `node-version: '24'`) | `"node": ">=24.0.0"` (`deploy-pages.yml`: `node-version: '24'`) |
| **Astro Integrations** | `integrations: [mdx()]` (`@astrojs/mdx@^8.1.6`) | None (`staticPassthroughIntegration()` local hook) |
| **Content Sourcing** | `glob({ pattern: '**/*.mdx', base: './src/content/tutorial' })` | `glob({ base: '..', pattern: [...] })` across 20 root `.md` files |
| **Markdown Pipeline** | `unified({ gfm: true, ... })` via `@astrojs/markdown-remark` | `unified({ gfm: true, ... })` via `@astrojs/markdown-remark` |
| **Routing & Output** | `trailingSlash: 'always'`, `build: { format: 'directory' }` | `trailingSlash: 'always'`, `build: { format: 'directory' }` |
| **Shiki Config** | `type: 'shiki'`, `excludeLangs: ['mermaid']`, `langAlias` | `type: 'shiki'`, `excludeLangs: ['mermaid']` |
| **Image Handling** | `astro:assets` (`<Image>` and `getImage()` in `Figure.astro`) | Native HTML/static passthrough images (`astro:assets` unused) |
| **TypeScript Config** | `extends: astro/tsconfigs/strict`, `allowImportingTsExtensions: true`, `noEmit: true` | Identical (`extends: astro/tsconfigs/strict`, `allowImportingTsExtensions: true`, `noEmit: true`) |
| **Test & Check Scripts** | `vitest run` (`happy-dom`), `astro check && tsc --noEmit`, `node scripts/check-site.ts` | Identical (`vitest run`, `astro check && tsc --noEmit`, `node scripts/check-site.ts`) |
| **Unified/Remark/Rehype Deps** | Transitive via `@astrojs/markdown-remark` in `package-lock.json` | Explicit `devDependencies` (imported directly by `tests/rehype-single-source.test.ts` and `tests/checklist-controller.test.ts`) |

---

## 2. Full Package Audit & Comparison Table

All registry versions, timestamps (`time.modified` / version publish dates), `engines`, and `peerDependencies` below were queried via `npm view` on `2026-11-25`. None of the 28 packages carry a `deprecated` flag on `latest`.

| Package | Current Pinned (`site/` & `reference/site/`) | Latest Stable | Delta Type | Breaking Changes / Compatibility Notes | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`astro`** | Both: `^7.4.13` (lock `7.4.13`) | `7.4.13` (`2026-11-18`) | Up to date | Requires `node >=22.23.4`; peer `@astrojs/markdown-remark: ^7.3.0`; bundles `vite@^8.3.8`, `rolldown@~1.3.2`, `shiki@^4.6.0`, `@astrojs/compiler-rs@^0.5.3`, `@astrojs/markdown-satteri@^0.4.10`, `zod@^4.6.7`. | Keep `^7.4.13` in lockstep. |
| **`@astrojs/mdx`** | `site/`: `^8.1.6` (lock `8.1.6`)<br>`reference/site/`: — | `8.1.6` (`2026-11-13`) | Up to date | Build Tutorial only. Requires `node >=22.23.4`; peers `astro: ^7.2.10`, `@astrojs/markdown-remark: ^7.3.0`, `@astrojs/markdown-satteri: ^0.4.0`. | Keep `^8.1.6` in `site/`. |
| **`@astrojs/markdown-remark`** | Both: `^7.3.10` (lock `7.3.10`) | `7.3.10` (`2026-11-18`) | Up to date | No longer auto-installed in Astro 7 (which defaults to Sätteri); required explicitly by both sites' `processor: unified(...)` config. | Keep `^7.3.10` in lockstep. |
| **`@astrojs/check`** | Both: `^0.9.12` (lock `0.9.12`) | `0.9.12` (`2026-10-21`) | Up to date | Peer `typescript: "^5.0.0 || ^6.0.0"`. Depends on `@astrojs/language-server@^2.17.3`. Incompatible with TypeScript 7.0 (`tsgo`) without TS6 aliasing. | Keep `^0.9.12` in lockstep. |
| **`katex`** | Both: `^0.19.1` (lock `0.19.1`) | `0.19.1` (`2026-10-23`) | Up to date | `0.19.0` added `symbolNotInFont` strict reporting and stricter strict-callback return checks (`false`/`"ignore"`). Both sites pass `{ strict: false }` to `rehypeKatex`. | Keep `^0.19.1` in lockstep. |
| **`rehype-katex`** | Both: `^7.0.1` (lock `7.0.1`) | `7.0.1` (`2024-08-19`) | Up to date | Latest stable `7.0.1`; compatible with `unified@11` and `katex@0.19.1`. | Keep `^7.0.1` in lockstep. |
| **`remark-math`** | Both: `^6.0.0` (lock `6.0.0`) | `6.0.0` (`2023-09-19`) | Up to date | Latest stable `6.0.0`; works with `remarkPromoteDoubleDollarMath` plugin in both sites. | Keep `^6.0.0` in lockstep. |
| **`mermaid`** | Both: `^12.3.0` (lock `12.3.0`) | `12.3.0` (`2026-11-03`) | Up to date | Requires `node >=22.12.0`; browser ES2024; bundles ELK layout engine & `redux-color`/`neo` defaults (overridden by `theme: 'base'` in `mermaid-client.ts`). `13.0.0-alpha.3` exists on `v13-alpha`. | Keep `^12.3.0` in lockstep; do not adopt `v13` alpha. |
| **`pagefind`** | Both: `^1.6.0` (lock `1.6.0`) | `1.6.0` (`2026-11-01`) | Up to date | `1.5.0`/`1.6.0` added Web Worker search, metadata indexing by default, diacritics/CJK, and Linux/Node API fixes. Both sites invoke CLI `npx pagefind --site dist` and lazy-import `pagefind.js`. | Keep `^1.6.0` in lockstep. |
| **`vitest`** | Both: `^5.1.1` (lock `5.1.1`) | `5.1.1` (`2026-11-18`) | Up to date | Requires `node: ^22.12.0 || ^24.0.0 || >=26.0.0`, `vite: ^6.4.0 || ^7.0.0 || ^8.0.0`; v5 defaults `clearMocks: true` and requires explicit `happy-dom` devDep. | Keep `^5.1.1` in lockstep. |
| **`happy-dom`** | Both: `^21.0.4` (lock `21.0.4`) | `21.0.4` (`2026-10-20`) | Up to date | Requires `node >=20.0.0`. `21.0.0` disabled external CSS & iframe loading by default (SSRF fix); `21.0.3` stopped forwarding `Authorization` on redirects; `21.0.4` isolated `data:` iframes. Safe for both test suites & `site-contract.ts`. | Keep `^21.0.4` in lockstep. |
| **`typescript`** | Both: `^5.9.3` (lock `5.9.3`) | `7.0.2` (`2026-07-08` release; `6.0.3` bridge exists) | **Major (+2)** | TS `6.0` changes `types` default to `[]` and `rootDir` to `.`. TS `7.0` (`tsgo`) makes TS6 deprecations hard errors and breaks `@astrojs/check@0.9.12` (`typescript: ^5.0.0 || ^6.0.0`). | **Defer `6.x` & `7.x`.** Keep `^5.9.3` until `@astrojs/check` supports `^7.0.0`. |
| **`@fontsource/barlow-condensed`** | Both: `^5.3.0` (lock `5.3.0`) | `5.3.0` (`2026-07-19`) | Up to date | Self-hosted WOFF2 CSS package; offline-safe. | Keep `^5.3.0` in lockstep. |
| **`@fontsource/ibm-plex-mono`** | Both: `^5.3.0` (lock `5.3.0`) | `5.3.0` (`2026-07-19`) | Up to date | Self-hosted WOFF2 CSS package; offline-safe. | Keep `^5.3.0` in lockstep. |
| **`@fontsource/ibm-plex-sans`** | Both: `^5.3.0` (lock `5.3.0`) | `5.3.0` (`2026-07-19`) | Up to date | Self-hosted WOFF2 CSS package; offline-safe. | Keep `^5.3.0` in lockstep. |
| **`@fontsource/space-grotesk`** | Both: `^5.3.0` (lock `5.3.0`) | `5.3.0` (`2026-07-19`) | Up to date | Self-hosted WOFF2 CSS package; offline-safe. | Keep `^5.3.0` in lockstep. |
| **`github-slugger`** | Both: `^2.0.0` (lock `2.0.0`) | `2.0.0` (`2023-09-15`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^2.0.0`). | Keep `^2.0.0` in lockstep. |
| **`invokers-polyfill`** | Both: `^1.0.5` (lock `1.0.5`) | `1.0.5` (`2026-11-22`) | Up to date | Polyfills Invoker Commands (`commandfor`/`command`) for older browsers. | Keep `^1.0.5` in lockstep. |
| **`unist-util-visit`** | Both: `^5.2.0` (lock `5.2.0`) | `5.2.0` (`2026-10-24`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^5.2.0`). | Keep `^5.2.0` in lockstep. |
| **`@types/hast`** | Both: `^3.0.5` (lock `3.0.5`) | `3.0.5` (`2026-10-04`) | Up to date | Compatible with `unified@11` / `rehype-raw@7`. | Keep `^3.0.5` in lockstep. |
| **`@types/mdast`** | Both: `^4.0.4` (lock `4.0.4`) | `4.0.4` (`2026-10-04`) | Up to date | Compatible with `remark-parse@11` / `remark-math@6`. | Keep `^4.0.4` in lockstep. |
| **`@types/node`** | Both: `^24.0.0` (lock `24.19.2`) | `26.6.10` (`2026-11-25`)<br>(`24.x` latest: `24.19.3`) | **Major (+2)** | `26.x` exposes Node 26 stdlib APIs unavailable in Node 24 LTS CI (`docs.yml`, `deploy-pages.yml`). | **Defer `26.x`.** Keep `^24.0.0` (optional patch bump `24.19.2` → `24.19.3`). |
| **`unified`** | `site/`: transitive `11.0.5`<br>`reference/site/`: `^11.0.5` (`11.0.5`) | `11.0.5` (`2024-06-19`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^11.0.5`). | Keep `11.0.5` (`^11.0.5` if direct). |
| **`remark-parse`** | `site/`: transitive `11.0.0`<br>`reference/site/`: `^11.0.0` (`11.0.0`) | `11.0.0` (`2023-11-20`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^11.0.0`). | Keep `11.0.0` (`^11.0.0` if direct). |
| **`remark-gfm`** | `site/`: transitive `4.0.1`<br>`reference/site/`: `^4.0.1` (`4.0.1`) | `4.0.1` (`2025-02-10`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^4.0.1`). | Keep `4.0.1` (`^4.0.1` if direct). |
| **`remark-rehype`** | `site/`: transitive `11.1.2`<br>`reference/site/`: `^11.1.2` (`11.1.2`) | `11.1.2` (`2025-04-02`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^11.1.2`). | Keep `11.1.2` (`^11.1.2` if direct). |
| **`rehype-raw`** | `site/`: transitive `7.0.0`<br>`reference/site/`: `^7.0.0` (`7.0.0`) | `7.0.0` (`2023-11-20`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^7.0.0`). | Keep `7.0.0` (`^7.0.0` if direct). |
| **`rehype-stringify`** | `site/`: transitive `10.0.1`<br>`reference/site/`: `^10.0.1` (`10.0.1`) | `10.0.1` (`2024-09-27`) | Up to date | Matches `@astrojs/markdown-remark` dependency (`^10.0.1`). | Keep `10.0.1` (`^10.0.1` if direct). |

---

## 3. Deep-Dive: Astro v6/v7 & Node.js 24 LTS Compatibility

### 3.1 Node.js 24 LTS Compatibility Across Toolchain & CI

Both `site/package.json` (on `feat/astro-core-tutorial-site`) and `reference/site/package.json` declare `"engines": { "node": ">=24.0.0" }`, and both GitHub Actions workflows (`.github/workflows/docs.yml` and `.github/workflows/deploy-pages.yml`) provision `actions/setup-node@v4` with `node-version: '24'`.

- **Registry `engines` check:** Every package declaring an `engines.node` constraint is satisfied by Node 24 LTS:
  - `astro@7.4.13` & `@astrojs/mdx@8.1.6`: `>=22.23.4`
  - `mermaid@12.3.0`: `>=22.12.0`
  - `vitest@5.1.1`: `^22.12.0 || ^24.0.0 || >=26.0.0`
  - `happy-dom@21.0.4`: `>=20.0.0`
  - `typescript@5.9.3`: `>=14.17` (`typescript@7.0.2`: `>=16.20.0`)
- **Native TypeScript Execution (`node scripts/check-site.ts`):**
  - Node.js 24 executes `.ts` entrypoints natively via **type stripping** without `tsx` or `ts-node`, but ignores `tsconfig.json`, requires explicit `.ts` file extensions in relative imports, and rejects non-erasable TypeScript constructs (`enum`, runtime `namespace`, constructor parameter properties, legacy `import =` aliases) ([Node.js TypeScript docs](https://nodejs.org/api/typescript.html)).
  - **Codebase audit:** Searching `site/src/`, `site/scripts/`, `reference/site/src/`, and `reference/site/scripts/` confirmed **zero** occurrences of `enum`, `namespace`, or constructor parameter properties. Both `tsconfig.json` files set `"allowImportingTsExtensions": true` and `"noEmit": true`, ensuring `tsc --noEmit` checks the exact `.ts` relative imports executed by `node scripts/check-site.ts`.

### 3.2 Astro v6/v7 Surface-Area Audit

Both sites already run on `astro@7.4.13` (released `2026-11-18`). Reviewing the [Astro v6](https://docs.astro.build/en/guides/upgrade-to/v6/) and [Astro v7](https://docs.astro.build/en/guides/upgrade-to/v7/) upgrade guides against both configurations confirms the following status for each surface:

1. **`@astrojs/markdown-remark` & `unified()` Processor:**
   - **Breaking change in Astro v7:** Astro v7 introduced the Rust-powered **Sätteri** pipeline (`@astrojs/markdown-satteri@0.4.10`) as the default Markdown/MDX engine and removed `@astrojs/markdown-remark` from default core dependencies. Projects with custom `remark`/`rehype` plugins must install `@astrojs/markdown-remark` explicitly and wire `markdown.processor: unified(...)` in `astro.config.mjs`.
   - **Impact:** Already handled in both sites (`@astrojs/markdown-remark@^7.3.10` + `unified(...)` in both `astro.config.mjs` files). Note that **Build Tutorial** `site/` also installs `@astrojs/mdx@^8.1.6`, whose peer dependency requires `@astrojs/markdown-remark: "^7.3.0"` alongside `astro: "^7.2.10"`.
2. **`astro:assets` `<Image>` and `getImage()`:**
   - **Breaking change in Astro v6:** Default image service crops by default when dimensions require it, never upscales images past source resolution, and throws if `getImage()` is called client-side.
   - **Impact:** **Build Tutorial** `site/src/components/Figure.astro` invokes `await getImage({ src })` in server frontmatter (build-time) and `<Image>` without upscaling; **Companion Site** does not import `astro:assets`. No compatibility issues.
3. **`glob()` Content Loader:**
   - **Breaking change in Astro v6:** Legacy `Astro.glob()` was removed; Content Layer `glob()` from `astro/loaders` is standard.
   - **Impact:** Both sites already use `defineCollection` + `glob()` from `astro/loaders` in `src/content.config.ts`.
4. **`trailingSlash: 'always'` & `build.format: 'directory'`:**
   - **Breaking change in Astro v6:** Endpoints with file extensions can no longer be requested with a trailing slash regardless of `trailingSlash`.
   - **Impact:** Both sites serve static directory HTML routes (`/index.html`) and copy raw binary/HTML assets via **Static Passthrough** integration/files rather than Astro file-extension endpoints; unaffected.
5. **Shiki `excludeLangs: ['mermaid']`:**
   - **Breaking change in Astro v6:** Upgraded Shiki to `4.x` (`shiki@4.6.0` in both lockfiles).
   - **Impact:** Both `astro.config.mjs` files use high-level `syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] }` with `theme: 'github-dark'`, avoiding low-level Shiki transformer internals.
6. **Rust `.astro` Compiler & Vite 8 / Rolldown:**
   - **Breaking change in Astro v7:** Replaced Go compiler with Rust compiler (`@astrojs/compiler-rs@0.5.3`), disallowing auto-repair of unclosed HTML tags and adopting strict JSX inline whitespace; upgraded Vite to `8.x` (`vite@8.3.8`, `rolldown@~1.3.2`).
   - **Impact:** Already absorbed in both codebases; maintain strict well-formed HTML in `.astro` templates and MDX files.
7. **`astro check` (`@astrojs/check@0.9.12`):**
   - **Critical constraint:** `@astrojs/check@0.9.12` (with `@astrojs/language-server@2.17.3`) only accepts `"typescript": "^5.0.0 || ^6.0.0"` in `peerDependencies`. This is the single active blocker preventing a `typescript@7.0.2` upgrade.

---

## 4. Deep-Dive: Mermaid, Pagefind, Vitest, Happy DOM, KaTeX, and TypeScript

- **Mermaid (`^12.3.0`):** Mermaid v12 bumped minimum Node to `>=22.12.0`, targeted ES2024 browsers, and changed default layout/theme to bundled ELK (`@mermaid-js/layout-elk`) and `redux-color`/`neo`. Both sites already pin `12.3.0` and explicitly configure `theme: 'base'`, `themeVariables`, and `flowchart: { useMaxWidth: false, htmlLabels: true, curve: 'basis' }` in `src/lib/mermaid-client.ts`, keeping diagrams isolated from default-theme drift. Mermaid `13.0.0-alpha.3` is prerelease-only and should not be adopted.
- **Pagefind (`^1.6.0`):** Pagefind `1.5.0`/`1.6.0` brought Web Worker search execution, default metadata indexing, diacritics/CJK segmentation, and Linux/Node API bug fixes. Both sites invoke `npx pagefind --site dist` in `npm run build` and dynamically import `${SITE_BASE}/pagefind/pagefind.js` (`init()` + `search()`) in `src/lib/search-modal.ts`, which remains API-compatible.
- **Vitest (`^5.1.1`) & Happy DOM (`^21.0.4`):** Vitest v5 requires Node `>=22.12.0`, Vite `>=6.4.0`, explicit `happy-dom` devDependencies, and sets `clearMocks: true` by default. Happy DOM v21 disabled external `<link rel="stylesheet">` (`enableCSSFileLoading`) and `<iframe>` (`enableIframePageLoading`) network loading by default (v21.0.0), stopped forwarding `Authorization` headers across redirects (v21.0.3), and isolated opaque `data:` iframes (v21.0.4). Both sites already run `vitest@5.1.1` + `happy-dom@21.0.4`, and neither `tests/*.test.ts` nor `src/lib/site-contract.ts` (`new Window(...)` HTML DOM parsing) relies on external CSS/iframe fetching.
- **KaTeX (`^0.19.1`):** KaTeX `0.19.0` tightened strict-mode reporting (`symbolNotInFont`) and strict-callback return values, while `0.19.1` fixed `%` handling in raw arguments. Both `astro.config.mjs` files pass `[rehypeKatex, { strict: false }]`, preventing strict-mode build failures on technical/Unicode math symbols.
- **TypeScript (`^5.9.3` vs. `6.0.3` / `7.0.2`):**
  - **TypeScript 6.0** (released March 2026) was the final JS-based bridge release and changed compiler defaults (`types: []` instead of auto-discovering all `@types/*`, `rootDir: .`, deprecating `es5`, `baseUrl`, and `moduleResolution: node`).
  - **TypeScript 7.0** (released July 2026, Go-native `tsgo`) turned TypeScript 6.0 deprecations into hard errors, introduced `--stableTypeOrdering`, and dropped the legacy JS programmatic compiler API expected by Volar / `@astrojs/check@0.9.12` (until Astro language tools ship native TS 7.1+ content-mapper integration).

---

## 5. Lockstep Target Ranges & Deferral Recommendations

### Recommended Lockstep Ranges (Both `site/` and `reference/site/`)

Maintain identical semver ranges across both repositories for all shared packages:

```json
{
  "engines": {
    "node": ">=24.0.0"
  },
  "dependencies": {
    "@astrojs/markdown-remark": "^7.3.10",
    "@fontsource/barlow-condensed": "^5.3.0",
    "@fontsource/ibm-plex-mono": "^5.3.0",
    "@fontsource/ibm-plex-sans": "^5.3.0",
    "@fontsource/space-grotesk": "^5.3.0",
    "astro": "^7.4.13",
    "github-slugger": "^2.0.0",
    "invokers-polyfill": "^1.0.5",
    "katex": "^0.19.1",
    "mermaid": "^12.3.0",
    "rehype-katex": "^7.0.1",
    "remark-math": "^6.0.0",
    "unist-util-visit": "^5.2.0"
  },
  "devDependencies": {
    "@astrojs/check": "^0.9.12",
    "@types/hast": "^3.0.5",
    "@types/mdast": "^4.0.4",
    "@types/node": "^24.0.0",
    "happy-dom": "^21.0.4",
    "pagefind": "^1.6.0",
    "typescript": "^5.9.3",
    "vitest": "^5.1.1"
  }
}
```

- **Build Tutorial (`site/`) addition:** Retain `"@astrojs/mdx": "^8.1.6"` in `dependencies`.
- **Companion Site (`reference/site/`) addition:** Retain `"unified": "^11.0.5"`, `"remark-parse": "^11.0.0"`, `"remark-gfm": "^4.0.1"`, `"remark-rehype": "^11.1.2"`, `"rehype-raw": "^7.0.0"`, and `"rehype-stringify": "^10.0.1"` in `devDependencies` (imported directly by `reference/site/tests/rehype-single-source.test.ts` and `tests/checklist-controller.test.ts`).

### Explicit Deferrals

| Package | Latest Available | Action | Rationale |
| :--- | :--- | :--- | :--- |
| **`typescript`** | `7.0.2` (`6.0.3` bridge) | **Defer** (stay on `^5.9.3`) | `@astrojs/check@0.9.12` restricts `peerDependencies` to `^5.0.0 || ^6.0.0` and breaks with TypeScript 7 (`tsgo`) without `@typescript/typescript6` workarounds; TS 6.0 adds churn (`types: []`) with no Astro build benefit. Re-evaluate only after `@astrojs/check` ships native TS 7.x support. |
| **`@types/node`** | `26.6.10` | **Defer `26.x`** (stay on `^24.0.0`, patch `24.19.3` optional) | CI (`docs.yml` & `deploy-pages.yml`) and `engines.node` target **Node.js 24 LTS**. Keeping `@types/node` on `^24.0.0` prevents accidental compile-time acceptance of Node 26 APIs. |
| **`mermaid` v13** | `13.0.0-alpha.3` | **Defer** (stay on `^12.3.0`) | Pre-release `alpha` channel only. |
