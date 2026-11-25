# Research: File-by-File Divergence Audit — Build Tutorial (`site/`) vs. Companion Site (`reference/site/` @ `8ad81d0`)

- **Ticket:** [`domesticmouse/EnvelopeFollower#50`](https://github.com/domesticmouse/EnvelopeFollower/issues/50) (`wayfinder:research`, Parent Map: [`#48`](https://github.com/domesticmouse/EnvelopeFollower/issues/48))
- **Primary Sources Audited:**
  - **Build Tutorial (`site/` + `.github/workflows/docs.yml`):** Checked out on branch `feat/astro-core-tutorial-site` (`44619c2a8b8f1e230e3f7288aa824c77c9b5381b`)
  - **Companion Site (`reference/site/` + `reference/.github/workflows/deploy-pages.yml`):** Submodule `reference/` pinned at `8ad81d0f4277e8ec6dcf434270522493fc1e3ae5` (`8ad81d0`, `domesticmouse/EnvelopeFollowerWithSkewLimiter`)
  - **Repository Pin & `8ad81d0` Footprint:** Audited on both `feat/astro-core-tutorial-site` (`44619c2`) and `main` (`0a6d9b7`), excluding `.git/`, `node_modules/`, `dist/`, `.astro/`, and `reference/`

---

## Executive Summary & Classification Tally

Although the **Build Tutorial** (`site/`, 13 MDX routes) and the **Companion Site** (`reference/site/`, 25 single-source Markdown + **Curated Page** routes) share the same Astro Core + Pagefind + KaTeX + Mermaid + native `<dialog>` architecture and dark-studio aesthetic, inspecting every shared and parallel file reveals **43 concrete file-level deltas** across styles, typography, client runtime, Astro components, build/test configuration, CI workflows, and built-site verification contracts:

| Classification | Count | Summary |
| :--- | :---: | :--- |
| **(a) Build Tutorial improvement to backport to Companion Site** | **19** | Tokenized `--led-amber` / `--led-amber-bg` / `--scrollbar-*`, `latin-400-italic` + `ibm-plex-mono/latin-700` font imports, `showModalSafe()` reuse in `initDialogChrome`, Mermaid non-retry & `<p role="status">` error note, Pagefind combobox ARIA + `/` shortcut + entity decoding + `data-pagefind-ignore` chrome defense-in-depth, remark null-safety without `unified` import, `stripRegistrationFrame()` + motif extraction in `panel-svg`, CLI flags & expanded Group 1–6 contract gates, PR-scoped CI concurrency + `submodules: true` |
| **(b) Companion Site convention/test to adopt in Build Tutorial** | **8** | Restore `supportsClosedBy` short-circuit inside `wireBackdropLightDismiss()`, adopt `--page-max-inline` token instead of 4× hardcoded `1380px`, override LED & `--border-grid` tokens in `@media print`, restore `<meta name="color-scheme" content="dark">` and `main script` absence assertions in `site-contract.ts`, restore dedicated `dialog-chrome.test.ts` edge-case assertions (`returnValue` reset, `command` event sync, `supportsClosedBy: true` non-attachment), and refresh **Companion Site** `/origin/` archival card from `4a02c46` MkDocs framing to live **Build Tutorial** framing |
| **(c) Intentional site-specific divergence** | **16** | `--led-dark` / `--led-dark-bg` vs. `--accent-gold-link`, `1380px` 3-column workbench vs. `1200px` curated container, `routes.ts` 13-route curriculum vs. 25-route hardware/patch/checklist map, `SiteHeader.astro` / `SiteFooter.astro` cross-site link topology & telemetry bar, `repo-files.ts` root sentinel & byte-size helpers, `panel-svg.ts` `reference/` path & `data-normal-arrow`, `astro.config.mjs` & `package.json` (`@astrojs/mdx` vs. `rehype-single-source` + **Static Passthrough**), and route-specific contract/test suites |

Three files are **byte-identical** between both repositories:
- `src/components/MermaidHydrator.astro` (5 lines)
- `tsconfig.json` (16 lines)
- `vitest.config.ts` (13 lines)

---

## 1. Styles & Typography (`tokens.css`, `fonts.css`, and CSS Usage Audit)

### 1.1 `src/styles/tokens.css` (36 lines in Companion Site vs. 45 lines in Build Tutorial)

| Token / Property | Companion Site (`reference/site/src/styles/tokens.css`) | Build Tutorial (`site/src/styles/tokens.css`) | Verified Usage Across Both Sites | Classification |
| :--- | :--- | :--- | :--- | :--- |
| `--led-amber`, `--led-amber-bg` | **Missing** from `tokens.css`; hardcoded `#fbbf24` / `#291e09` in `global.css:515-519` (`.led-pill[data-led='amber']`) | Defined (`#fbbf24`, `#291e09`, lines `30-31`) | Used 5× (`--led-amber`) and 2× (`--led-amber-bg`) in `workbench.css:594-595,1538,1596-1597` (`.search-badge-optional`, `.mermaid-error-note`, `.callout-warning`); Companion Site has `0` token uses | **(a)** Backport `--led-amber` / `--led-amber-bg` to `reference/site/src/styles/tokens.css` and replace raw hex in `global.css:516-518` |
| `--scrollbar-thumb`, `--scrollbar-track` | **Missing**; `tokens.css:27` hardcodes `scrollbar-color: #7b8294 #141518;` | Defined (`#7b8294`, `#141518`, lines `33-34`) and referenced on line `44` | Used 2× each in `site/src/styles/tokens.css`; `0` in `reference/site/` | **(a)** Backport scrollbar custom properties to `reference/site/src/styles/tokens.css` |
| `--font-slab` fallback | `'Barlow Condensed', 'DIN Condensed', system-ui, sans-serif` (line `29`) | Adds `'Arial Narrow'` fallback (line `36`) | Used 3× in each site (`tokens.css` + CSS) | **(a)** Backport `'Arial Narrow'` condensed fallback to Companion Site |
| `color-scheme: light !important` in `@media print` | `global.css:865-894` omits `color-scheme: light !important` (resets colors & `--led-*` / `--border-grid`) | `workbench.css:2207` sets `color-scheme: light !important` | Ensures browser form controls/scrollbars render light on paper in dark-only sites | **(a)** Backport `color-scheme: light !important` to `reference/site/src/styles/global.css` |
| `--page-max-inline` | Defined as `1200px` (line `34`) | **Removed** from `tokens.css` | Used 4× in Companion Site (`tokens.css:34`, `global.css:135,578`, `index.astro:189`); **Build Tutorial** hardcodes `max-inline-size: 1380px;` 4× in `workbench.css:142,172,623,1945` | **(b)** Adopt `--page-max-inline: 1380px;` in `site/src/styles/tokens.css` instead of duplicating `1380px` 4× in `workbench.css` *(value `1380px` vs. `1200px` itself is **(c)** intentional layout width divergence)* |
| Print overrides for `--led-*` & `--border-grid` | `global.css:887-893` resets `--border-grid`, `--led-green*`, `--led-red*`, `--led-dark*` to `#000000`/`#ffffff`/`#888888` | `workbench.css:2210-2226` omits `--border-grid`, `--led-green*`, `--led-red*`, `--led-amber*` | **Tutorial Appendix** callouts, status badges, and tables can print light-green/amber on white | **(b)** Adopt explicit `@media print` overrides for `--led-green*`, `--led-red*`, `--led-amber*`, and `--border-grid` in `workbench.css` |
| `--accent-gold-link` | **Absent** (links use `--accent-gold`) | Defined (`#d8b154`, line `17`), overridden to `#000000` in `@media print` (`workbench.css:2220`) | Used 21× in `site/src/styles/` (`20×` in `workbench.css`, `1×` in `tokens.css`); `0×` in `reference/site/` | **(c)** Intentional semantic split in `workbench.css` (both `#d8b154` on screen, `#000000` in print; Companion Site already overrides `--accent-gold: #000000` in print) |
| `--led-dark`, `--led-dark-bg` | Defined (`#c5cad4`, `#1e2128`, lines `24-25`) | **Removed** | Used 5× / 3× in Companion Site (`global.css:510-511,565-566,892-893` for `0 V` LED state pills & `.cta-secondary:hover`); `0×` in Build Tutorial | **(c)** Intentional hardware-domain token: Build Tutorial has no `0 V` LED simulator pill |

### 1.2 `src/styles/fonts.css` (16 lines in Companion Site vs. 18 lines in Build Tutorial)

| Font Import | Companion Site | Build Tutorial | Verified Usage Across Both Sites | Classification |
| :--- | :--- | :--- | :--- | :--- |
| `@fontsource/ibm-plex-sans/latin-400-italic.css` | **Missing** | Imported (`line 10`) | **Build Tutorial** MDX prose renders numerous `*italic*` spans across 10 MDX files; **Companion Site** also uses `<em>` in `pages/index.astro:174`, `pages/origin.astro:306`, and Markdown specs (`EnvelopeFollower.md`, etc.) | **(a)** Backport `latin-400-italic.css` to `reference/site/src/styles/fonts.css` to eliminate browser-synthesized oblique faux-italics |
| `@fontsource/ibm-plex-mono/latin-700.css` | **Missing** (stops at `latin-600.css`) | Imported (`line 18`) | **Build Tutorial** `workbench.css` pairs `--font-mono` + `font-weight: 700` across **11 selectors** (`.c-brand-qualifier`, `.nav-drawer-group-title`, `.search-dialog-title`, `.search-result-badge`, `.c-rack-module summary`, `.c-toc-heading`, `.c-bay-kicker`, `.c-patch-title`, `.callout-kicker`, `.figure-zoom-badge`, `.figure-lightbox-title`). **Companion Site** *also* pairs `--font-mono` + `font-weight: 700` in `global.css:738` (`.search-dialog-title`) and `global.css:837-839` (`.search-result-badge`), plus `800` in `build.css:650-651` & `curated.css:60-61` | **(a)** Backport `latin-700.css` to `reference/site/src/styles/fonts.css` so Companion Site stops faux-bolding monospace headers/badges |

---

## 2. Client Runtime, Plugins, & Accessibility Modules

### 2.1 `src/lib/dialog-chrome.ts` (145 lines in Companion Site vs. 144 lines in Build Tutorial)

- **`showModalSafe(dialog)` reuse in `initDialogChrome` (`site/src/lib/dialog-chrome.ts:135-137` vs. `reference/site/src/lib/dialog-chrome.ts:136-138`):** Build Tutorial delegates fallback opening to `showModalSafe(dialog)`, whereas Companion Site still duplicates `typeof dialog.showModal === 'function'` inline.
  - **Classification:** **(a)** Backport `showModalSafe(dialog)` call inside `initDialogChrome` to Companion Site.
- **`supportsClosedBy` check removed inside `wireBackdropLightDismiss()` (`site/src/lib/dialog-chrome.ts:48-55` vs. `reference/site/src/lib/dialog-chrome.ts:48-56`):** Companion Site checks `const supportsClosedBy = typeof HTMLDialogElement !== 'undefined' && 'closedBy' in HTMLDialogElement.prototype; if (supportsClosedBy || dialog.getAttribute('closedby') !== 'any') return;` inside `wireBackdropLightDismiss()`. Build Tutorial removed that check from `wireBackdropLightDismiss()`, keeping it only inside `initDialogChrome()` (line `117`). Consequently, direct callers (`search-modal.ts:311` and `figure-lightbox.ts:30`) attach redundant `pointerdown`/`pointerup` listeners even in browsers with native `closedby="any"` support (whereas in `happy-dom`, `'closedBy' in HTMLDialogElement.prototype` is already `false`, so tests would still pass with the guard restored).
  - **Classification:** **(b)** Adopt Companion Site's `supportsClosedBy` short-circuit inside `wireBackdropLightDismiss()` in Build Tutorial.

### 2.2 `src/lib/mermaid-client.ts` (101 lines in Companion Site vs. 112 lines in Build Tutorial)

- **Identical `MERMAID_THEME_CONFIG` (`lines 14-43`)**: Both share identical `darkMode: true`, `#090a0d` background, `#d8b154` ENIG Gold borders/lines, `#1b1d22` nodes, `securityLevel: 'strict'`, and `flowchart.curve: 'basis'`.
- **Error-state non-retry + accessible `<p role="status">` fallback (`site/src/lib/mermaid-client.ts:64-68, 101-107`):** Build Tutorial excludes `[data-mermaid-error="true"]` from re-querying on repeated `hydrateMermaidDiagrams()` calls and inserts `<p class="mermaid-error-note" role="status">Diagram preview unavailable; showing Mermaid source.</p>` idempotently above the `<pre class="mermaid">` fallback. Companion Site marks `data-mermaid-error="true"` only (`line 96`) without a status notice or selector exclusion.
  - **Classification:** **(a)** Backport both `:not([data-mermaid-error="true"])` and the `role="status"` notice to Companion Site.
- **Note on `aria-label` (`line 94` in both):** Both set `aria-label="Circuit signal flow diagram"`, even though Build Tutorial also uses Mermaid for agent/Wayfinder workflow diagrams (e.g., `index.mdx`, `stages/08`, `stages/09`). Worth parameterizing or generalizing per diagram in Build Tutorial if touched later (`(c)` / minor content alignment).

### 2.3 `src/lib/search-modal.ts` & `src/components/SearchModal.astro`

| Delta | Companion Site (`reference/site/`) | Build Tutorial (`site/`) | Classification |
| :--- | :--- | :--- | :--- |
| **Combobox ARIA attributes** | `<input>` lacks combobox roles (`SearchModal.astro:21-30`); `resultsEl` lacks `id`; `updateSelection` does not set `aria-activedescendant` or `aria-expanded` | `SearchModal.astro:26-29,43` adds `role="combobox"`, `aria-autocomplete="list"`, `aria-expanded="false"`, `aria-controls="site-search-results"`, and `id="site-search-results"`; `search-modal.ts:188-205,249` assigns `site-search-result-${idx}` and syncs `aria-activedescendant` + `aria-expanded` | **(a)** Backport full ARIA combobox pattern to Companion Site |
| **HTML entity decoding in `appendSafeExcerpt()`** | `search-modal.ts:81-104` strips non-`<mark>` tags but passes raw Pagefind entities (`&lt;`, `&gt;`, `&quot;`, `&#39;`, `&amp;`) literally into `textContent` | `search-modal.ts:99-106,127-135` decodes `&lt;`, `&gt;`, `&quot;`, `&#x27;`/`&#39;`, `&amp;` before creating text/mark nodes (`&lt;PromptBlock&gt;` renders `<PromptBlock>`) | **(a)** Backport `decodeBasicEntities()` to Companion Site (prevents literal `&lt;` / `&amp;` in Pagefind excerpts) |
| **`/` global shortcut & `isEditableTarget()`** | Only `Cmd+K` / `Ctrl+K` (`search-modal.ts:289-298`) | Adds `/` shortcut guarded by `event.defaultPrevented`, modifier checks, and `isEditableTarget()` for `input`/`textarea`/`select`/`[contenteditable]` (`search-modal.ts:68-97,334-354`) | **(a)** Backport `/` shortcut + `isEditableTarget()` to Companion Site |
| **`data-pagefind-ignore` on `<dialog>`** | Omitted from `SearchModal.astro:1-8` (excluded only indirectly by `<main data-pagefind-body>`) | Explicit `data-pagefind-ignore` on `SearchModal.astro:6` | **(a)** Backport explicit `data-pagefind-ignore` defense-in-depth to Companion Site |
| **Section taxonomy & status copy** | Hardcoded 7-key `classifyRouteSection` (`patches`, `build`, `hardware`, `specs`, `origin`, `downloads`, `overview`), `"Search Documentation"`, `"25 ENV / SKEW pages"`, hardware query examples | `classifyRouteSection` delegates to `getSectionByUrl` + `SEARCH_SECTION_LABELS` (`routes.ts`) for the 5 **Build Tutorial** sections; `"Search Build Tutorial"`, `"13 ENV / SKEW Build Tutorial pages"`, `EMPTY_QUERY_MESSAGE` / `DEV_FALLBACK_MESSAGE` constants | **(c)** Intentional site-specific taxonomy and copy |

### 2.4 `src/components/MermaidHydrator.astro`

- **Identical (5 lines)** in both sites: lazy client script importing `hydrateMermaidDiagrams` from `../lib/mermaid-client.ts`.

### 2.5 `src/lib/panel-svg.ts` & `src/lib/panel-svg-shared.ts`

| Delta | Companion Site | Build Tutorial | Classification |
| :--- | :--- | :--- | :--- |
| **`stripRegistrationFrame()` before layer extraction** | `extractGroupById(maskText, '_03_Registration_Frame', ..., false)` returns `registrationFrameSvg` separately (`panel-svg-shared.ts:45-49,153-163`), relying on `_03_Registration_Frame` being a sibling group rather than nested | `stripRegistrationFrame()` (`panel-svg-shared.ts:98-102`) strips both `_03_Registration_Frame` groups and `id="registration_frame"` elements regardless of nesting (`panel-svg-shared.ts:143-155`) | **(a)** Backport `stripRegistrationFrame()` safety pass on `goldLayerSvg` / `silkLayerSvg` in Companion Site (while preserving `registrationFrameSvg` extraction) |
| **Actionable submodule missing/empty error** | Checks `fs.existsSync` only (`panel-svg.ts:17-22`) | `readPanelSvgFile()` (`panel-svg.ts:13-29`) also rejects empty files and includes `git submodule update --init --recursive` remediation | **(c)** Intentional submodule-specific error message (helpful for Build Tutorial; Companion Site reads local `panel_art/`) |
| **Discrete motif extraction (`extractFaceplateMotifs`) & static `renderAssembledFaceplateSvg()`** | **Not present**; instead exports `polarPoint()`, `describeSweepArc()`, `registrationFrameSvg`, and `data-normal-arrow="true"` tagging (`panel-svg-shared.ts:45-87,134-139`) for `<env-skew-panel>` & `<panel-layer-inspector>` | Exports `FaceplateMotifs` + `parseFaceplateMotifsFromStrings()` (8 header/rail/wing/LED motifs using `currentColor`) + `renderAssembledFaceplateSvg()` for Overview hero bay; drops `polarPoint()`, `describeSweepArc()`, `registrationFrameSvg`, and `data-normal-arrow` | **(c)** Intentional site-specific divergence: Companion Site animates interactive dials & inspector layers; Build Tutorial renders static Overview faceplate + hardware UI motifs |
| **SVG source root path** | Reads `panel_art/front_*.svg` (`panel-svg.ts:14-15`) | Reads `reference/panel_art/front_*.svg` (`panel-svg.ts:34-43`) | **(c)** Intentional repository layout difference |

### 2.6 `src/plugins/remark-double-dollar-math.ts` (46 lines in Companion Site vs. 50 lines in Build Tutorial)

- Build Tutorial removes the `import type { Plugin } from 'unified'` devDependency coupling (`package.json` dropped `unified`), exports a named function `remarkPromoteDoubleDollarMath()` returning `(tree: Root, file?: MathSourceFile) => void`, and safely guards `file?.value` with optional chaining (`site/src/plugins/remark-double-dollar-math.ts:18-29`).
  - **Classification:** **(a)** Backport optional `file?.value` guard and `MathSourceFile` typing to Companion Site (Companion Site still uses `unified` in `astro.config.mjs`, so keeping or dropping `Plugin` type is optional, while `file?.value` prevents crashes if a caller omits `file`).

### 2.7 `src/lib/repo-files.ts` (53 lines in Companion Site vs. 25 lines in Build Tutorial)

- **Root sentinel check (`resolveRepoRoot()`):** Companion Site checks `DesignSpec.md` + `bom/ibom.html` (`lines 12-13`); Build Tutorial checks `GLOSSARY.md` + `docs/adr/0001-astro-core-mdx-tutorial-site.md` (`lines 12-13`).
- **`formatByteSize()` & `getRepoFileSizeLabel()`:** Present in Companion Site (`lines 28-53`) for `/downloads/` **Static Passthrough** cards; absent in Build Tutorial (no passthrough downloads page).
  - **Classification:** **(c)** Intentional site-specific divergence.

### 2.8 `src/lib/routes.ts` (112 lines in Companion Site vs. 280 lines in Build Tutorial)

- **Origin & base:** Both lock `SITE_ORIGIN = 'https://domesticmouse.github.io'`; Companion Site uses `SITE_BASE = '/EnvelopeFollowerWithSkewLimiter'` vs. Build Tutorial `SITE_BASE = '/EnvelopeFollower'`.
- **Route & nav registries:** Companion Site defines `PRIMARY_NAV_ITEMS` (5 audience-ordered links) + `CANONICAL_ROUTES` (25 routes) + `isNavSectionActive()`. Build Tutorial defines `TUTORIAL_SECTIONS` (5 curriculum sections), `SECTION_LABELS`, `SEARCH_SECTION_LABELS`, `TUTORIAL_ROUTES` (13 ordered routes `0..12`), `PRIMARY_JUMP_NAV` (4 desktop jump pills), `getRouteByPath()`, `getRouteGroups()`, `isJumpNavActive()`, `getPrevNextRoutes()`, `formatPrevNextKicker()`, `getProgressMeterLabel()`, and `getSectionByUrl()`.
- **External URL constants:** Build Tutorial centralizes `TUTORIAL_REPO_URL`, `HARDWARE_REPO_URL`, `COMPANION_SITE_URL`, and `HAGIWO_NOTE_URL` in `routes.ts:10-22` (whereas Companion Site only exports `GITHUB_REPO_URL` in `routes.ts:11-12` and hardcodes `EnvelopeFollower` + HAGIWO URLs in `SiteFooter.astro:23,31` and `origin.astro`).
  - **Classification:** Route map/nav helpers are **(c)** intentional site-specific divergence; centralizing external URL constants (`HAGIWO_NOTE_URL`, `TUTORIAL_REPO_URL`, `TUTORIAL_SITE_URL`) in `reference/site/src/lib/routes.ts` is a clean **(a)** backport to Companion Site.

---

## 3. Cross-Site Chrome, Links & `data-pagefind-ignore` Coverage

### 3.1 `src/components/SiteHeader.astro` & `src/components/SiteFooter.astro`

| Aspect | Companion Site (`reference/site/src/components/`) | Build Tutorial (`site/src/components/`) | Classification |
| :--- | :--- | :--- | :--- |
| **Header structure & cross-site links** | Single-row `.site-header` (`SiteHeader.astro:16-84`) with `ENV / SKEW` slab logo, `6 HP · REV 1.0`, 5 `PRIMARY_NAV_ITEMS`, `Search ⌘K`, and `GitHub` icon link (`GITHUB_REPO_URL` → `EnvelopeFollowerWithSkewLimiter`). Mobile drawer links to `Overview`, 5 primary items, `Reference Specs`, and `GitHub Repository`. **No header link to Build Tutorial repo or live site.** | Dual-band workbench header: `.c-telemetry` utility strip (`SiteHeader.astro:23-31`) showing `DM // R1.0 · BUILD TUTORIAL WORKBENCH` with **`Companion Site ↗`** (`COMPANION_SITE_URL`) and **`GitHub ↗`** (`TUTORIAL_REPO_URL`), above `.c-header` (`lines 33-91`) with faceplate `heroEnvelopeSvg`, `ENV / SKEW` + `BUILD TUTORIAL` qualifier, 4 `PRIMARY_JUMP_NAV` pills (with `ledOctagonSvg` active indicator), `Rack` mobile drawer button, and `SEARCH ⌘K`. Mobile drawer groups all 13 routes across 5 sections + `Companion Site ↗` and `GitHub Repository ↗`. | **(c)** Intentional workbench IA & telemetry header; however, see `/origin/` staleness below |
| **Footer links & attribution** | `SiteFooter.astro:5-51`: 7 internal links + `GitHub ↗` (`EnvelopeFollowerWithSkewLimiter`); footer meta credits `HAGIWO/ハギヲ (No. 43: $4 Envelope Follower)` and `domesticmouse/EnvelopeFollower` (repo URL only, line `31`), plus `Apache License 2.0` (`GITHUB_REPO_URL/blob/main/LICENSE`). | `SiteFooter.astro:12-46`: 5 section jump links + **`Companion Site ↗`** (`COMPANION_SITE_URL`) + **`Tutorial Repo ↗`** (`TUTORIAL_REPO_URL`) + **`Hardware Repo ↗`** (`HARDWARE_REPO_URL`); footer meta credits `HAGIWO/ハギヲ` (`HAGIWO_NOTE_URL`) and `domesticmouse/EnvelopeFollowerWithSkewLimiter` (`HARDWARE_REPO_URL`), plus `Apache License 2.0` (`TUTORIAL_REPO_URL/blob/main/LICENSE`). | **(c)** Intentional cross-repo symmetry (each site credits the other repo in footer meta, and Build Tutorial surfaces all 3 destination links in `footer-nav`) |
| **Companion Site link to live Build Tutorial Pages site** | `SiteHeader` and `SiteFooter` do **not** link to `https://domesticmouse.github.io/EnvelopeFollower/`. Only `src/pages/origin.astro:192-218` links to both `github.com/domesticmouse/EnvelopeFollower` and `domesticmouse.github.io/EnvelopeFollower/`, but labels them `"Archival Extraction Repo · 2026-11-18"` (`submodule 4a02c46, 16 documented build prompts`) and `"Live Extraction Docs · GitHub Pages"` (written prior to Build Tutorial's Astro Core migration and `8ad81d0` update). | Prominent `Companion Site ↗` link in `.c-telemetry` (`SiteHeader.astro:27`), mobile drawer (`line 136`), and `SiteFooter.astro:20`, plus inline links throughout Stages 2–9 and Appendix. | **(b) / Upstream Sync Note:** Updating Companion Site's `origin.astro:192-218` card copy (and optionally adding a `Build Tutorial ↗` footer/drawer link) keeps Companion Site aligned once Build Tutorial lands on `main` |

### 3.2 `data-pagefind-ignore` Coverage

- **Companion Site (`reference/site/`):**
  - Root layout (`SiteLayout.astro:54`) places `data-pagefind-body` on `<main id="main-content" class="site-main">`. `SiteHeader.astro`, `SiteFooter.astro`, and `SearchModal.astro` sit outside `<main>`, so Pagefind excludes them implicitly—**none** of those three shared chrome components carry `data-pagefind-ignore`.
  - Inside `<main>`, `data-pagefind-ignore` is applied explicitly to:
    - `DocLayout.astro`: `.doc-rail` (`71`), `.breadcrumbs` (`102`), `.companion-banner` (`122`), `.toc-outline` (`147`), `.doc-prev-next` (`171`)
    - `patches/[slug].astro`: `.doc-rail` (`99`), `.breadcrumbs` (`162`), `.mobile-panel-dock` (`171`), `.doc-prev-next` (`235`), `.patch-dock-aside` (`254`)
    - `build/[slug].astro`: `.checklist-toolbar` (`86`), `.bringup-jump-strip` (`115`)
    - `hardware.astro`: `.mermaid-card` (`127`)
    - `IbomLaunchCard.astro` (`17`), `JlcpcbUploadStrip.astro` (`66`), and `rehype-single-source.ts` (`.mermaid-card` at line `253`, plus `panel_svg_spec.md` §8 `<details>`).
- **Build Tutorial (`site/`):**
  - Tightens indexing scope by moving `data-pagefind-body` off `<main>` onto `h1[data-pagefind-body]` and `article.tutorial-prose[data-pagefind-body]` (`TutorialLayout.astro:220,242`).
  - Applies `data-pagefind-ignore` as defense-in-depth on **all** non-prose regions both outside and inside `<main>`:
    - `SiteHeader.astro`: `.c-telemetry` (`23`), `header.c-header` (`33`), `dialog#mobile-nav-drawer` (`98`)
    - `SiteFooter.astro`: `footer.site-footer` (`12`)
    - `SearchModal.astro`: `dialog#site-search-dialog` (`6`)
    - `FigureLightbox.astro`: `dialog#figure-lightbox` (`6`)
    - `TutorialLayout.astro`: `aside.left-rail` (`147`), `details.toc-mobile` (`186`), `nav.breadcrumbs` (`207`), `.c-bay-specs` (`224`), `.c-bay-faceplate` (`234`), `nav.prev-next-nav` (`248`), `aside.right-toc` (`268`)
    - `PromptBlock.astro`: `.c-patch-spine` (`28`) — excludes repeated `PROMPT` / `T1` / `T2` spine badges from search excerpts
    - `rehype-mermaid.ts`: `.mermaid-card` (`37`)
  - Enforced by `site-contract.ts:461-478` across all 13 built routes.
  - **Classification:** **(a)** Backport explicit `data-pagefind-ignore` on `SiteHeader.astro`, `SiteFooter.astro`, and `SearchModal.astro` (plus `site-contract.ts` assertions) to Companion Site for defense-in-depth.

---

## 4. Verification, Tests, Config, & CI

### 4.1 Verification CLI & Built-Site Contract (`scripts/check-site.ts` & `src/lib/site-contract.ts`)

- **`scripts/check-site.ts` (`29` lines vs. `68` lines):**
  - Build Tutorial adds `parseCliArgs()` supporting `--root`, `--dist`, `--reference-dir`, and `--require-reference` (defaulting `requireReference` to `process.env.GITHUB_ACTIONS === 'true'`), prints `result.warnings`, and reports `verifiedFigures` and `verifiedPrompts` alongside routes, images, and links.
  - **Classification:** **(a)** Backport `--root`/`--dist` CLI flag parsing and `warnings` reporting to Companion Site's `scripts/check-site.ts` (`--require-reference` itself is **(c)** submodule-specific).

- **`src/lib/site-contract.ts` (`644` lines vs. `1,324` lines):**
  - **Build Tutorial improvements to backport to Companion Site `(a)`:**
    1. **Self-hosted font & CDN asset scan** (`checkTypographyAndCssBundles`, `lines 490-531`): verifies all 4 `.woff2` font families exist in `dist/`, rejects `https?://` in built `.css`, and rejects external CDN domains (`fonts.googleapis.com`, `fonts.gstatic.com`, `unpkg.com`, `cdn.jsdelivr.net`) across `.html`, `.css`, and `.js`.
    2. **Canonical `<link rel="canonical">` carve-out** (`lines 545-550`): allows `rel="canonical"` pointing to `${SITE_ORIGIN}${SITE_BASE}/` while still rejecting external `<link href>` / `<script src>`.
    3. **Priority image anti-pattern guard** (`lines 756-761`): forbids pairing `fetchpriority="high"` with `loading="lazy"`.
    4. **Pagefind boundary & dialog attribute assertions** (`checkPagefindBoundariesAndDialogs`, `lines 450-488`): verifies single `<h1>`, `[data-pagefind-body]`, all `data-pagefind-ignore` chrome selectors, `[data-search-trigger]`, and `dialog[closedby="any"]` across every route.
    5. **Static Mermaid AST/Markdown guardrails & `localStorage` ban** (`lines 820-926`): enforces no hardcoded hex `style`/`classDef`, no mixed `direction LR` subgraph cross-edges, Mermaid script isolation on non-diagram routes, KaTeX stylesheet isolation on math-only routes, and zero `localStorage` usage where not intended.
    6. **Terminology / Glossary & root-doc link linting** (`checkRootDocLinks`, `AVOIDED_GLOSSARY_PATTERNS`, `lines 184-219, 987-1197`): generalizes `verifyReadmeLinks()` to scan both `README.md` and `PotentialImprovements.md`, enforces `GLOSSARY.md` `_Avoid_` term absence across MDX + root docs, and validates `8ad81d0` / `main` GitHub links against local checkouts.
  - **Companion Site checks to adopt in Build Tutorial `(b)`:**
    1. **`<meta name="color-scheme" content="dark">` check** (`reference/site/src/lib/site-contract.ts:383-386`): dropped in Build Tutorial's `site-contract.ts` even though `TutorialLayout.astro:121` emits it.
    2. **`main script` absence check** (`reference/site/src/lib/site-contract.ts:392-394`): asserts no inline/page `<script>` lands inside `<main>`, dropped in Build Tutorial's `site-contract.ts`.
  - **Intentional contract divergences `(c)`:**
    - Companion Site checks **97 Static Passthroughs**, byte-identical `bom/ibom.html`, `isExcludedRepoPath()` leak scan, `patch-states.ts` sidecar parity, 211 enabled/unchecked checkboxes, 81 checklist lightboxes, `<env-skew-panel>` / `<zoom-pan-viewer>` / `<panel-layer-inspector>` custom elements, and `panel_svg_spec.md` §8 `<details data-pagefind-ignore>`.
    - Build Tutorial checks 14 bundled `src/assets/images/` assets (with `500 KiB` / `250 KiB` byte ceilings), 17 `<Figure>` instances (`is-framed` vs. unframed rules), 13 `<PromptBlock>` + 3 `<PromptGroup>` specs, 0 prototype leftovers, 8 Mermaid blocks across 7 routes, and static `disabled` Appendix checkboxes (`20`/`66` + `9`/`9`).

### 4.2 Build & Tooling Configs (`tsconfig.json`, `vitest.config.ts`, `package.json`, `astro.config.mjs`)

- **`tsconfig.json` (`16` lines) & `vitest.config.ts` (`13` lines):** **Byte-identical** in both repositories (`astro/tsconfigs/strict`, `allowImportingTsExtensions: true`, `environment: 'happy-dom'`).
- **`package.json` & `astro.config.mjs`:**
  - **Build Tutorial** adds `@astrojs/mdx` (`^8.1.6`), drops unused direct deps (`rehype-raw`, `rehype-stringify`, `remark-gfm`, `remark-parse`, `remark-rehype`, `unified`), configures `shikiConfig.langAlias: { gitignore: 'plaintext' }`, and replaces `rehypeRaw` + `rehypeSingleSource` + `staticPassthroughIntegration()` + Vite `fs.allow: ['..']` with `rehypeMermaidBlocks`, `rehypePromptChips`, and `rehypeCodeConsole`.
  - **Classification:** **(c)** Intentional architectural divergence (MDX components vs. single-source root `.md` ingestion + **Static Passthrough**).

### 4.3 GitHub Actions CI (`.github/workflows/docs.yml` vs. `reference/.github/workflows/deploy-pages.yml`)

| Workflow Setting | Companion Site (`deploy-pages.yml`) | Build Tutorial (`docs.yml`) | Classification |
| :--- | :--- | :--- | :--- |
| **`concurrency`** | `group: pages`, `cancel-in-progress: false` (lines `21-22`) — **PR runs queue behind or serialize on the single `pages` group** | `group: ${{ github.event_name == 'pull_request' && format('docs-pr-{0}', github.ref) || 'pages' }}`, `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` (lines `22-23`) | **(a)** Backport PR-scoped concurrency + `cancel-in-progress` to Companion Site so PRs run in parallel without blocking `main` Pages deploys |
| **`actions/checkout@v4`** | No `submodules` option (lines `31-32`) | `with: { submodules: true }` (lines `34-35`) | **(c)** Intentional: Build Tutorial depends on `reference/` submodule (`panel_art/` + `8ad81d0` link verification) |
| **`paths-ignore`** | Excludes `.agents/**`, `docs/agents/**`, `docs/research/**`, `skills-lock.json` on `push` (lines `6-10`) | Adds `- 'docs/adr/**'` (line `9`) | **(c)** Intentional repo doc layout alignment (both run `pull_request` unconditionally without `paths-ignore`) |
| **Workflow & step labels** | `Build & Deploy Documentation Site`; `(25 routes, passthroughs, Pagefind, README links)` | `Build & Deploy Build Tutorial Site`; `(13 routes, Pagefind, assets, glossary, links)` | **(c)** Intentional site-specific naming |

### 4.4 Test Suite Coverage (`site/tests/` vs. `reference/site/tests/`)

- **Totals:** Build Tutorial has **15 suites / 2,715 lines**; Companion Site has **17 suites / 3,156 lines**.
- **Shared/parallel test suites:**
  1. **`dialog-chrome.test.ts` (Companion Site: 210 lines, 8 tests) vs. `chrome.test.ts` (Build Tutorial: 133 lines, 2 `initDialogChrome` tests + `parseInlineBackticks` + `initTocScrollSpy`):**
     - Build Tutorial merged `initDialogChrome` tests into `chrome.test.ts` and **dropped 4 edge-case tests** present in `reference/site/tests/dialog-chrome.test.ts`:
       - `supportsClosedBy: true` must **not** attach redundant backdrop pointer listeners (`lines 126-139`)
       - `close` event clears `dialog.returnValue` (`lines 141-154`)
       - Native invoker `command` event syncs `aria-expanded="true"` via `queueMicrotask` (`lines 193-209`)
       - Standalone `pointerdown`/`pointerup` light-dismiss outside bounds vs. inside bounds (`lines 78-93, 111-124`)
     - **Classification:** **(b)** Restore these 4 missing `initDialogChrome` assertions (plus `showModalSafe()` error fallback) in Build Tutorial (`chrome.test.ts` or dedicated `dialog-chrome.test.ts`).
  2. **`mermaid-client.test.ts` (79 lines vs. 116 lines):** Build Tutorial adds strict `themeVariables` assertions and tests the accessible `.mermaid-error-note[role="status"]` fallback (`lines 87-115`). → **(a)** Backport to Companion Site.
  3. **`search-modal.test.ts` (183 lines vs. 330 lines):** Build Tutorial adds tests for `/` shortcut, `isEditableTarget()` across `input`/`textarea`/`select`/`[contenteditable]`, `Ctrl+K`, backdrop pointer dismiss, 120 ms `vi.useFakeTimers()` debounce, `ArrowUp` wrap-around, and `&lt;PromptBlock&gt;` entity decoding. → **(a)** Backport to Companion Site.
  4. **`panel-svg.test.ts` (80 lines vs. 124 lines):** Build Tutorial tests `extractFaceplateMotifs()`, `renderAssembledFaceplateSvg()`, nested `_03_Registration_Frame` stripping, and submodule error message (`(a)`/`(c)`). Companion Site tests `tickToDeg()`, `PANEL_CONTROL_COORDS` values, and `data-normal-arrow="true"` (`(c)`).
  5. **`routes.test.ts` (92 lines vs. 234 lines)** & **`site-contract.test.ts` (378 lines vs. 698 lines):** Parallel suite tests covering each site's canonical route registry and contract verifier assertions (`(c)`).
  6. **Site-exclusive test suites `(c)`:**
     - **Build Tutorial only (9 suites):** `code-console.test.ts`, `content-features.test.ts`, `copy-controller.test.ts`, `figure-lightbox.test.ts`, `hast-utils.test.ts`, `markdown-plugins.test.ts`, `prompt-chips.test.ts`, `stages-2-5.test.ts`, `stages-6-7.test.ts`.
     - **Companion Site only (11 suites):** `checklist-controller.test.ts`, `content-manifest.test.ts`, `env-skew-panel.test.ts`, `panel-layer-inspector.test.ts`, `patch-states.test.ts`, `patch-workbench-controller.test.ts`, `patches-hub-controller.test.ts`, `rehype-single-source.test.ts`, `static-passthrough.test.ts`, `toggletip.test.ts`, `zoom-pan-viewer.test.ts`.

---

## 5. Submodule Pin & `8ad81d0` Footprint Across `domesticmouse/EnvelopeFollower`

### 5.1 Submodule Pin Verification

- Gitlink entry (`git ls-tree main reference` and `git -C reference rev-parse HEAD`):
  `160000 commit 8ad81d0f4277e8ec6dcf434270522493fc1e3ae5	reference`
- Identical on both `main` (`0a6d9b7`) and `feat/astro-core-tutorial-site` (`44619c2`).

### 5.2 Exact `8ad81d0` Occurrence Count & Categorization

Excluding `.git/`, `node_modules/`, `dist/`, `.astro/`, and `reference/`:

- **On `feat/astro-core-tutorial-site` (`44619c2`, current Build Tutorial target):** **`116` matching lines / `163` exact `8ad81d0` substring occurrences across `17` files**.
- *(Baseline context on `main` @ `0a6d9b7`, pre-Astro Core migration: **`109` matching lines / `156` exact `8ad81d0` occurrences across `16` files** — legacy `docs/` + `scripts/verify_site.py`.)*

#### Category Breakdown (`feat/astro-core-tutorial-site` @ `44619c2`)

| Category | Exact `8ad81d0` Occurrences | Description |
| :--- | :---: | :--- |
| **Pinned `blob/8ad81d0/...` GitHub file URLs** | **106** | Direct source citations to hardware scripts, BOMs, specs, **Build Checklists**, **Patch Guides**, `GLOSSARY.md`, `ADR 0001`, and **Companion Site** `site/` modules |
| **Pinned `tree/8ad81d0` / `tree/8ad81d0/...` GitHub repo & directory URLs** | **18** | Links to repo root (`tree/8ad81d0`) and directories (`manufacturing/`, `checklists/`, `patches/`, `site/`) |
| **Prose, frontmatter badge, table header, & research audit mentions** | **31** | Textual `@ 8ad81d0` / `` `8ad81d0` `` citations in `README.md`, `index.mdx`, `stages/*`, `appendix/*`, and `docs/research/reference-github-trail.md` |
| **Verifier implementation (`site/src/lib/site-contract.ts`)** | **3** | `PINNED_8AD81D0_RE` regex (`line 296`), uninitialized submodule warning (`line 1139`), and `verifyGithubTarget(..., '8ad81d0', ...)` (`line 1149`) |
| **Verifier test suite (`site/tests/site-contract.test.ts`)** | **5** | Synthetic test fixtures & assertions covering valid and broken `8ad81d0` targets (`lines 236, 339, 621, 624, 629`) |
| **Total (`17` files)** | **163** | (`116` matching lines) |

#### Per-File Inventory (`feat/astro-core-tutorial-site` @ `44619c2`)

| File Path | Matching Lines | Exact `8ad81d0` Count | Role |
| :--- | :---: | :---: | :--- |
| `site/src/content/tutorial/appendix/engineering-sign-off-checklist.mdx` | 23 | 35 | **Engineering Sign-Off Checklist** pinned deliverables & CI/PR citations |
| `site/src/content/tutorial/stages/07-fabrication-checklists-and-patches.mdx` | 22 | 34 | **Build Checklist** (`01`–`05`), `81` generator scripts, `tayda-1000489380`, and **Patch Guide** links |
| `site/src/content/tutorial/stages/09-companion-site-delivery.mdx` | 16 | 24 | **Companion Site** module table (`8ad81d0` pin column), PR `#32`, and `deploy-pages.yml` citations |
| `README.md` | 9 | 14 | Submodule pin header, hardware/site summary, repository tree, and `ADR 0001` links |
| `site/src/content/tutorial/stages/08-wayfinder-site-planning.mdx` | 9 | 9 | `skills-lock.json`, `docs/agents/*`, research reports, `GLOSSARY.md`, and `ADR 0001` links |
| `site/src/content/tutorial/appendix/netlist-and-bom.mdx` | 5 | 11 | `envelope_follower_bom.xml`, `jlcpcb_bom.csv`, `silk_layout.json`, `tayda-1000489380` links |
| `site/src/content/tutorial/index.mdx` | 5 | 8 | Hero metadata badge (`Trail @ 8ad81d0`) and **Decision Trail** / **Repository Front Door** links |
| `site/tests/site-contract.test.ts` | 5 | 5 | Contract Group 6 `8ad81d0` link-resolution tests |
| `PotentialImprovements.md` | 4 | 5 | `EnvelopeFollower.md`, `EnvelopeFollowerImprovements.md`, `DesignSpec.md` pinned references |
| `docs/research/reference-github-trail.md` | 4 | 4 | Upstream PR `#32` (`8ad81d0`) audit trail records |
| `site/src/content/tutorial/stages/06-front-panel-and-artwork.mdx` | 3 | 3 | `panel_svg_spec.md`, `generate_panel_art.py`, `import_svgs_to_kicad.py` links |
| `site/src/lib/site-contract.ts` | 3 | 3 | `PINNED_8AD81D0_RE` & submodule path verification |
| `site/src/content/tutorial/stages/02-sketch-extraction-and-critique.mdx` | 2 | 2 | `EnvelopeFollower.md` & `EnvelopeFollowerImprovements.md` links |
| `site/src/content/tutorial/stages/04-skidl-and-schematic.mdx` | 2 | 2 | `envelope_follower.py` & `generate_schematic.py` links |
| `site/src/content/tutorial/stages/05-main-pcb-and-silkscreen.mdx` | 2 | 2 | `generate_kicad_pcb.py` & `silk_layout.json` links |
| `site/src/content/tutorial/stages/01-hardware-agent-skills.mdx` | 1 | 1 | **Repository Front Door** `README.md` link |
| `site/src/content/tutorial/stages/03-design-spec-and-dft.mdx` | 1 | 1 | `DesignSpec.md` link |
| **Total (`17` files)** | **116** | **163** | — |
