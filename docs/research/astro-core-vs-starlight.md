# Research: Astro Core vs. Astro Starlight and Markdown Pipeline Compatibility for the ENV / SKEW Build Tutorial

- **Ticket:** [#28 — Research Astro Core vs. Astro Starlight and Markdown pipeline compatibility for Build Tutorial](https://github.com/domesticmouse/EnvelopeFollower/issues/28)
- **Date:** 2026-11-25
- **Scope:** Evaluate **Astro Core** (isolated `site/` architecture, cf. `reference/docs/adr/0001-astro-core-single-source-site.md` and `reference/site/`) versus **Astro Starlight** (`@astrojs/starlight`) against primary official documentation and an exact corpus audit of the `13` published **Build Tutorial** Markdown files (`docs/index.md`, `docs/tutorial/` `10` files, `docs/reference/` `2` files), `mkdocs.yml`, `docs/javascripts/prompt-copy.js`, and `scripts/verify_site.py`.

---

## Executive Summary & Verdict

**Choose Astro Core (`site/` + Content Layer `glob()` + `@astrojs/markdown-remark` `unified()` + `rehype` plugin + Pagefind + Vanilla TS/Web Components) — do not use Astro Starlight.**

1. **Starlight's content & layout opinions collide with every core requirement of this repository:**
   - Starlight's `docsLoader()` is hardcoded to `src/content/docs/`, and `docsSchema()` requires YAML `title` frontmatter on every page — whereas **`0 / 13` published Build Tutorial files** contain YAML frontmatter (and all `13` live under `docs/` for direct GitHub readability and existing `mkdocs.yml` / `scripts/verify_site.py` parity).
   - Starlight's built-in admonitions use `:::note` (`remark-directive` container syntax) rather than our **`30` `!!!` admonitions** (including **`13` `!!! prompt` Prompt Blocks**) and **`1` `??? info` collapsible detail** (`stage-4-skidl.md`), so Starlight gives zero out-of-the-box compatibility for our existing callout syntax.
   - Incorporating `ENV / SKEW` faceplate SVG motifs (`FaceplateIllustration.astro`, `panel_art/`), chamfered hardware chrome, PCB routing accents, and our multi-turn `.prompt-group` timeline rails is far cleaner in Astro Core (`SiteLayout.astro` / `DocLayout.astro`) — reusing proven tokens and components from `reference/site/` — than overriding Starlight's opinionated 3-column shell and `--sl-*` CSS variable system.
2. **Exact Markdown corpus incompatibilities discovered (`4` specific MkDocs/PyMdown extensions):**
   Unlike the companion repo's `20` CommonMark/GFM files (`EnvelopeFollowerWithSkewLimiter`), the Build Tutorial's `13` `docs/` files were authored for `mkdocs-material` (`mkdocs.yml:38-60`) and use four Python-Markdown / PyMdown constructs that **neither Astro Core nor Starlight parses natively**:
   - **`30` `!!!` admonitions across `12` files** (including **`13` `!!! prompt` Prompt Blocks** across `6` files and `17` `warning`/`tip`/`note`/`info` admonitions).
   - **`1` `??? info` collapsible block** (`docs/tutorial/stage-4-skidl.md:102`).
   - **`11` `attr_list` annotations across `4` files** (`{ width="230" }`, `{ width="240" }`, `{ .framed-shot }`, `{ width="520" .framed-shot }`) — rendered as literal `{ ... }` text in CommonMark unless handled by a plugin or normalized.
   - **`1` LaTeX bracket display math block `\[ ... \]`** (`docs/tutorial/optional-dc-coupled-mode.md:20-22`) — `pymdownx.arithmatex` supports `\[...\]`, whereas `remark-math` only parses `$...$` and `$$...$$`.
   - *(Note on raw HTML & task lists)*: Our audit found **`0` multi-line raw HTML layout blocks** (`<div>`, `<table>`, `<details>`) in prose across all `13` published `docs/` files (the only raw tag outside code/Mermaid in prose is `<env-skew-panel>` inside image alt text at `stage-9-companion-site-delivery.md:94`; `6` of `7` Mermaid files use `<br/>` inside fenced `mermaid` labels). GFM task lists appear in **`2` files** (`build-checklist.md` and `netlist-and-bom.md`) totaling **`75` checkboxes** (`29` top-level + `46` nested; `58` `[x]` + `17` `[ ]`).
3. **Migration implication:** Astro Core with `@astrojs/markdown-remark`'s `unified()` processor lets us **either** ingest `docs/` completely untouched via one small `remark` pre-transform plugin (converting `!!!`/`???`, `\[...\]`, and trailing `{ ... }` image attributes in AST without editing `docs/*.md`), **or** cleanly migrate those four constructs in `docs/` if retiring `mkdocs.yml` — while inheriting `reference/site/`'s proven `base: '/EnvelopeFollower'`, `rehype-katex`, lazy `mermaid`, `Pagefind`, and `ENV / SKEW` visual design system.

---

## 1. Versions, Runtime Requirements & GitHub Pages `base` Support

| Capability | Astro Core (`astro`) | Astro Starlight (`@astrojs/starlight`) | Primary Source / Repo Evidence |
| :--- | :--- | :--- | :--- |
| **Current stable version** | **`v7.4.13`** (`@astrojs/markdown-remark` `^7.3.10`) | **`v0.43.1`** (integrates on Astro) | `reference/site/package.json:19,24`; npm registry |
| **Node.js requirement** | **Node.js `>= 22.12.0`** (dropped Node 18 & 20 in Astro v6; even LTS 22+ / 24+ supported) | **Node.js `>= 22.12.0`** (inherits Astro core runtime) | [Astro v6 Upgrade Guide](https://docs.astro.build/en/guides/upgrade-to/v6/); `reference/site/package.json:7` (`>=24.0.0`); `reference/.github/workflows/deploy-pages.yml:34-37` (`node-version: '24'`) |
| **Astro v7 Markdown engine** | Default switched to Rust **Sätteri** (`@astrojs/markdown-satteri`); **`unified()`** from `@astrojs/markdown-remark` remains first-class opt-in (`markdown.processor`) | Uses Astro's Markdown config (`markdown.processor: unified(...)` for `remark`/`rehype` plugins) + Starlight's own Expressive Code / aside / anchor plugins | [Astro Markdown Content](https://docs.astro.build/en/guides/markdown-content/); `reference/site/astro.config.mjs:3,30-38` |
| **Astro v7 `.astro` compiler** | Strict Rust compiler (rejects unclosed HTML tags; JSX whitespace rules) | Same Astro compiler | [Astro v7 Upgrade Guide](https://docs.astro.build/en/guides/upgrade-to/v7/) |
| **GitHub Pages `base: '/EnvelopeFollower/'`** | `site: 'https://domesticmouse.github.io'`, `base: '/EnvelopeFollower'`, `trailingSlash: 'always'`, `build: { format: 'directory' }`. Internal links/assets prefixed via `withBase()` / `rehype` plugin. | Same `site` / `base` / `trailingSlash` config; Starlight prefixes built-in nav & `_pagefind/` via `import.meta.env.BASE_URL`, though external/custom relative links and `trailingSlash` mismatches can cause Pagefind 404s unless aligned. | [Deploy Astro to GitHub Pages](https://docs.astro.build/en/guides/deploy/github/); [Starlight Config Reference](https://starlight.astro.build/reference/configuration/); `reference/site/astro.config.mjs:15-21`; `reference/site/src/lib/routes.ts:1-77` |

**Important Astro v7 `markdown.processor` note:** In Astro 7, top-level `markdown.remarkPlugins` and `markdown.rehypePlugins` shortcuts were removed in favor of `processor: unified({ gfm: true, remarkPlugins: [...], rehypePlugins: [...] })` from `@astrojs/markdown-remark`, verified directly in `reference/site/astro.config.mjs:3,30-38`.

---

## 2. Exact Corpus Audit of the `13` Published Build Tutorial Markdown Files

Audited all `13` published Markdown files under `docs/` (matching `scripts/verify_site.py:16-30,536-547`, excluding `docs/agents/`, `docs/adr/`, and `docs/research/`):

### 2.1 Per-File Construct Inventory

| File | FM | `!!! prompt` | Other `!!!` | `???` | `mermaid` | Math (`$...$` / `\[...\]`) | `attr_list` | Task Lists (`[x]` / `[ ]`) | Raw HTML / Notes | Int. Links / `![](img)` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| `docs/index.md` | `0` | `0` | `2` (`tip`, `info`) | `0` | `1` (`L25`) | `16` / `0` | `3` (`width="230"`) | `0` | `<br/>` in Mermaid | `12` / `3` |
| `docs/tutorial/stage-1-agent-skills.md` | `0` | `1` | `1` (`info`) | `0` | `0` | `0` / `0` | `0` | `0` | — | `12` / `0` |
| `docs/tutorial/stage-2-circuit-upgrades.md` | `0` | `2` | `1` (`tip`) | `0` | `0` | `26` / `0` | `0` | `0` | — | `3` / `1` |
| `docs/tutorial/stage-3-bom-and-dfm.md` | `0` | `3` *(1 + 2-turn)* | `1` (`tip`) | `0` | `1` (`L46`) | `13` / `0` | `0` | `0` | — | `0` / `0` |
| `docs/tutorial/stage-4-skidl.md` | `0` | `3` *(1 + 2-turn)* | `2` (`warning`) | `1` (`info` `L102`) | `0` | `0` / `0` | `0` | `0` | — | `2` / `1` |
| `docs/tutorial/stage-5-schematic-and-pcb.md` | `0` | `3` *(1 + 2-turn)* | `1` (`warning`) | `0` | `0` | `0` / `0` | `2` (`width="240"`) | `0` | — | `1` / `2` |
| `docs/tutorial/stage-6-front-panel.md` | `0` | `0` | `1` (`warning`) | `0` | `1` (`L5`) | `0` / `0` | `0` | `0` | `1` editorial `>` blockquote (`L47`); `<br/>` in Mermaid | `2` / `4` |
| `docs/tutorial/stage-7-manufacturing.md` | `0` | `0` | `2` (`warning`, `note`) | `0` | `1` (`L7`) | `0` / `0` | `3` (`.framed-shot`, `width="520" .framed-shot`) | `0` | `<br/>` in Mermaid | `4` / `3` |
| `docs/tutorial/stage-8-wayfinder-site-planning.md` | `0` | `1` | `3` (`tip`, `2× note`) | `0` | `1` (`L7`) | `0` / `0` | `0` | `0` | `<br/>` in Mermaid | `3` / `0` |
| `docs/tutorial/stage-9-companion-site-delivery.md` | `0` | `0` | `1` (`warning`) | `0` | `2` (`L7`, `L45`) | `0` / `0` | `3` (`.framed-shot`) | `0` | `<env-skew-panel>` in `L94` alt text; `<br/>` in Mermaid | `2` / `3` |
| `docs/tutorial/optional-dc-coupled-mode.md` | `0` | `0` | `1` (`info`) | `0` | `1` (`L26`) | `1` / `1` (`L20-22`) | `0` | `0` | `<br/>` in Mermaid | `5` / `0` |
| `docs/reference/netlist-and-bom.md` | `0` | `0` | `1` (`note`) | `0` | `0` | `0` / `0` | `0` | `0` / `9` *(9 top-level)* | — | `2` / `0` |
| `docs/reference/build-checklist.md` | `0` | `0` | `0` | `0` | `0` | `0` / `0` | `0` | `58` / `8` *(20 top, 46 nested)* | — | `0` / `0` |
| **Total (`13` files)** | **`0 / 13`** | **`13`** *(6 files)* | **`17`** *(10 files)* | **`1`** *(1 file)* | **`8`** *(7 files)* | **`56` `$...$` + `1` `\[...\]`** *(4 files)* | **`11`** *(4 files)* | **`75` total** *(`29` top-level, 2 files)* | **`0` prose HTML blocks** | **`48` / `17`** |

*(Summary note on `!!!` admonitions: `12` of the `13` published files contain at least one `!!!` block — every file except `docs/reference/build-checklist.md` — for `30` total admonitions: `13` `prompt`, `6` `warning`, `4` `tip`, `4` `note`, `3` `info`. Prompt Blocks contain inline `<code>` pills for `@[file]` and `/skill` tokens, and `stage-3`, `stage-4`, and `stage-5` each include two directly adjacent `Turn 1` / `Turn 2` `!!! prompt` blocks verified by `scripts/verify_site.py:95-128,550-601`.)*

---

## 3. Markdown Feature Compatibility: Astro Core vs. Astro Starlight

| Feature in `docs/` | Astro Core (`@astrojs/markdown-remark` `unified()`) | Astro Starlight (`@astrojs/starlight`) | Migration / Plugin Requirement |
| :--- | :--- | :--- | :--- |
| **`!!!` Admonitions (`30`) & `!!! prompt` (`13`)** | Not built into CommonMark (`!!!` + 4-space indent parses as `<p>` + `<pre><code>`). Needs a custom `remark` plugin (or source syntax change) emitting semantic `<aside class="admonition ...">` + `.prompt-group` wrappers for adjacent turns. | Built-in `asides` only support **`:::note` / `:::tip` / `:::caution` / `:::danger`** (`remark-directive`), **not** Python-Markdown `!!!` and **not** a custom `prompt` type with copy + multi-turn timeline rail. | Either write a ~60-line `remark-pymdown-admonitions` plugin (keeps `docs/` 100% MkDocs-compatible & GitHub-readable) or migrate `30` blocks if retiring MkDocs. Note `docs/javascripts/prompt-copy.js` (`CommandEvent` + clipboard + `role="status"` + `.prompt-group`) ports directly to Astro Core without Material's `document$`. |
| **`???` Collapsible Details (`1` in `stage-4:102`)** | Not built into CommonMark (`??? info` + 4-space indent renders as `<pre><code>`). Handled by the same `remark` plugin emitting native `<details class="spec-disclosure"><summary>...</summary>...</details>` (already styled in `reference/site/src/styles/docs.css:38-98`). | Not built into Starlight (`docs/` must either convert `???` via custom `remark` plugin or switch to raw `<details>`). | Emit native `<details>` via `remark` plugin or replace line 102 with raw HTML `<details>` (valid in GitHub Markdown, Astro Core, and Starlight). |
| **`mermaid` Fences (`8` in `7` files)** | Set `syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] }`, convert in `rehype` to `<figure class="mermaid-card"><pre class="mermaid">`, and lazy-import `mermaid@12` strictly when `.mermaid` blocks exist (`reference/site/src/lib/mermaid-client.ts`). | Expressive Code intercepts code fences unless excluded or handled via `astro-mermaid` (`mermaid` Astro integration) or a custom `rehype` + client script. | **Lazy client-side** (`mermaid` dynamic `import()`, ~0 CI overhead) is strongly preferred over `rehype-mermaid` build-time SVGs (which require Playwright + `~300 MB` Chromium in dev & CI per `ADR 0001`). |
| **Math (`56` `$...$` + `1` `\[...\]`)** | `remark-math` + `rehype-katex` + `katex/dist/katex.min.css` renders all `56` `$...$` expressions at build time (zero client MathJax runtime). Accepts digits right after `$` (`$100\text{ k}\Omega$`, `$1f$`). **Trap:** `\[ ... \]` in `optional-dc-coupled-mode.md:20-22` is **not** parsed by `remark-math`! | Same (`remark-math` + `rehype-katex` configured on top-level `markdown` in `astro.config.mjs` + `customCss: ['katex/dist/katex.min.css']`). Same `\[...\]` gap. | Normalize `\[...\]` (and `\(...\)`) to `$$...$$` in a tiny `remark` pre-pass (or switch lines 20–22 in `optional-dc-coupled-mode.md` to `$$...$$`, which GitHub.com and MkDocs `arithmatex` also render!). |
| **`attr_list` (`11` in `4` files)** | Not supported by `remark-parse` (`{ .framed-shot }` and `{ width="230" }` render as literal prose text!). | Same (`remark-parse` renders `{ .framed-shot }` as literal text). | Either add a small `remark` / `rehype` plugin parsing trailing `{ .class width="N" }` after `<img>` (or convert those `11` images to `<img ...>` / figure helpers — noting `rehype-single-source.ts` already rewrites raw `<img>` `src` and injects PNG `width`/`height`). |
| **GFM Task Lists (`75` items in `2` files)** | Native via `gfm: true` (`remark-gfm`). Emits `<li class="task-list-item"><input type="checkbox" disabled ...>`. | Native via `gfm: true` (`remark-gfm`). | Works out of the box in both (read-only reference checklists, or interactive `localStorage` if desired later via `rehype`). |
| **Raw HTML & Alt-Text Tags** | `rehype-raw` handles raw HTML safely (`reference/site/astro.config.mjs:34`). `stage-9:94` `<env-skew-panel>` in alt text is HTML-escaped safely in `.md` (would fail only in `.mdx`). | Safe in `.md` via `rehype-raw`; breaks only if migrating files to `.mdx`. | Keep files as `.md` (never `.mdx`), matching `ADR 0001`. |
| **Internal `.md` Links (`48`) & Images (`17`)** | `rehype` plugin (`rehype-single-source.ts` pattern) rewrites relative `.md` links (`stage-4-skidl.md#...`, `../reference/netlist-and-bom.md`) to `/EnvelopeFollower/tutorial/.../#...` and resolves `images/` + `../images/` to `/EnvelopeFollower/images/...` with `width`/`height` + `loading="lazy"`. | Built-in link resolution only works cleanly inside `src/content/docs/` with frontmatter/slug conventions; external `glob({ base: '../docs' })` still needs custom `rehype` rewriting for `docs/images/` and `.md#anchor` targets. | `rehype` link + image resolver is required under `format: 'directory'` (`.../index.html`) for both options if `docs/` stays outside `src/`. |

---

## 4. Content Source Constraints & Theme / Chrome Flexibility

### 4.1 Frontmatter-Free `docs/` & GitHub Readability

- **Astro Core:** Proven in `reference/site/src/content.config.ts:1-44`. Using `glob({ base: '..', pattern: [...] })` with `schema: z.object({}).strict()` ingests `docs/` verbatim with **zero YAML frontmatter**, preserving 100% clean GitHub rendering and keeping `scripts/verify_site.py` (or a TypeScript `npm run check` port) intact. Page titles are extracted cleanly from each file's `# Heading` (`extractDocumentTitle()`), and navigation order is defined centrally in a typed TypeScript manifest (mirroring `mkdocs.yml:71-89` without touching `docs/*.md`).
- **Astro Starlight:** Starlight's `docsLoader()` is locked to `src/content/docs/` ([Starlight Manual Setup](https://starlight.astro.build/guides/manual-setup/)), and `docsSchema()` requires a YAML `title` field on every document ([Starlight Frontmatter Reference](https://starlight.astro.build/reference/frontmatter/)). Pointing an Astro `glob()` loader at `../docs` with Starlight requires bypassing `docsLoader()`, implementing custom `generateId` + synthetic `title` injection, and forfeiting Starlight's default sidebar autogeneration and GitHub `editUrl` mapping (`docs/tutorial/...` vs `src/content/docs/...`).

### 4.2 Custom Theme, `ENV / SKEW` Faceplate SVG Motifs & PCB Routing Hints

- **Astro Core:** Full HTML/CSS/SVG ownership in `SiteLayout.astro`, `DocLayout.astro`, `SiteHeader.astro`, and custom components (`FaceplateIllustration.astro` renders `panel_art/front_soldermask.svg` + `front_silkscreen.svg` directly).
  - Reuses `reference/site/src/styles/tokens.css` (`#0d0e11` / `#141518` matte FR4, `#d8b154` / `#e2be66` ENIG Gold, `#f4f5f7` silkscreen white) and self-hosted WOFF2 fonts already present in `docs/assets/fonts/` (`Space Grotesk`, `IBM Plex Sans`, `IBM Plex Mono`, plus `OFL.txt`).
  - Lets header chrome, section rails, chamfered callouts, and subtle PCB copper/via routing dividers integrate natively without fighting framework CSS specificity.
  - Note: Unlike `reference/site` (which is dark-only on screen + white `@media print`), `mkdocs.yml:15-27` currently offers a `slate`/`default` light/dark toggle (`docs/stylesheets/extra.css:138-187`). In Astro Core, keeping that toggle is ~25 lines of inline `<head>` FOUC-free script + `[data-theme="light"]` token overrides + dual Shiki themes (`themes: { dark: 'github-dark', light: 'github-light' }`).
- **Astro Starlight:** Provides turnkey docs chrome (`Header`, `Sidebar`, `TwoColumnContent`, `TableOfContents`, `ThemeSelect`), customizable via `--sl-*` CSS tokens (`customCss`) and `components` overrides (`PageFrame`, `Header`, `Hero`, `Sidebar`, `Footer` per [Starlight Overrides](https://starlight.astro.build/reference/overrides/)). However, Starlight generates its own color ramps (`--sl-color-accent-*`, `--sl-color-gray-*`) and Expressive Code frame styles; layering `ENV / SKEW` faceplate SVG motifs, chamfered borders, PCB trace/pad accents, and Variant B `.prompt-group` timeline cards requires overriding multiple Starlight internal components and CSS layers.

---

## 5. Search (`Pagefind`), Shiki + Code Copy, Theme Toggle & Mermaid

| Capability | Astro Core | Astro Starlight | Assessment for Build Tutorial |
| :--- | :--- | :--- | :--- |
| **Search (`Pagefind`)** | Pluggable: `"build": "astro build --force && npx pagefind --site dist"` (`reference/site/package.json:11`) + native `<dialog closedby="any">` `⌘K` modal (`SearchModal.astro` + `search-modal.ts`, `348` lines) scoped via `data-pagefind-body` / `data-pagefind-ignore`. | Built-in `@pagefind/default-ui` out of the box (indexed automatically on `astro build`); supports `data-pagefind-body` / `data-pagefind-ignore`; occasional `base` + `trailingSlash` URL issues require overriding `Search.astro`. | **Tie / slight edge to Starlight for zero setup**, though Astro Core can copy `SearchModal.astro` + `search-modal.ts` directly from `reference/site/`. |
| **Shiki + Code Copy** | Built-in Shiki (`shikiConfig` supports dual light/dark themes + `@shikijs/transformers`), **no built-in copy button** (add a ~30-line vanilla copy script or `astro-expressive-code`). Unifying regular code copy with `!!! prompt` copy gives one consistent ENIG Gold UX. | Built-in **`astro-expressive-code`** with copy button, dark/light theme sync (`useStarlightDarkModeSwitch: true`), and frames — **does not** cover `!!! prompt` prose blocks. | **Starlight wins out-of-the-box for code fences**, while Astro Core keeps one unified copy system across both code fences and `!!! prompt` blocks. |
| **Light/Dark Toggle** | Opt-in: ~25-line `<head>` theme script + `[data-theme="light"]` CSS tokens (or dark-only matching `reference/site`). | Built-in `ThemeSelect` (`dark`/`light`/`auto`, `data-theme`) synced with Expressive Code. | **Starlight wins out-of-the-box**; small effort in Astro Core if light toggle is retained. |
| **Mermaid Diagrams** | `excludeLangs: ['mermaid']` + `rehype` wrapper + lazy client-side `mermaid@12` (`mermaid-client.ts`, zero Chromium in CI). Supports reactive dark/light variables. | Same (`astro-mermaid` or custom `rehype` + lazy client script) or Playwright `rehype-mermaid`. | **Equal** — both should use lazy client-side Mermaid (`~0` CI overhead vs `~300 MB` Chromium for `8` diagrams). |

---

## 6. Concrete Recommendation for the Build Tutorial

1. **Adopt Astro Core in an isolated `site/` workspace** (matching `reference/site/` and `ADR 0001`), keeping Node.js `24` LTS (`>=22.12.0` minimum) and GitHub Actions OIDC deployment (`base: '/EnvelopeFollower'`, `trailingSlash: 'always'`).
2. **Handle the `4` PyMdown/MkDocs syntax extensions cleanly at the Astro Core `unified()` seam** (either via a dedicated `remark-build-tutorial.ts` pre-transform so `docs/*.md` stays 100% untouched, or by normalizing `\[...\]` → `$$...$$` and `??? info` → `<details>` while keeping `!!!` / `!!! prompt` and `attr_list` parsed in AST):
   - Convert `!!! <type> "<title>"` + 4-space indented body (including adjacent `!!! prompt` Turn 1/Turn 2 groups) into semantic `.admonition` / `.admonition.prompt` / `.prompt-group` HTML structures reusing `docs/javascripts/prompt-copy.js` (`CommandEvent` + `role="status"`).
   - Convert `??? info "<title>"` (`stage-4-skidl.md:102`) into native `<details class="spec-disclosure"><summary>...</summary>...</details>`.
   - Convert `\[ ... \]` (`optional-dc-coupled-mode.md:20-22`) into `$$ ... $$` before `remark-math` + `rehype-katex`.
   - Parse trailing `{ .framed-shot }` / `{ width="..." }` (`11` occurrences across `4` files) onto `<img>` properties in `remark`/`rehype` alongside base-prefixed path & dimension resolution.
3. **Reuse `reference/site/` primitives directly:** `SiteLayout`/`DocLayout`, `ENV / SKEW` FR4+ENIG tokens, `FaceplateIllustration.astro` / SVG panel motifs, lazy `mermaid-client.ts`, scoped `Pagefind` `⌘K` modal, and zero-Chromium `npm run check` contract verification (`scripts/verify_site.py` invariants ported or paired with `site-contract.ts`).

---

## 7. Primary Sources Cited

- **Astro Official Documentation:**
  - Astro v6 Upgrade Guide (Node.js `>=22.12.0` requirement): <https://docs.astro.build/en/guides/upgrade-to/v6/>
  - Astro v7 Upgrade Guide (Rust compiler & `unified` processor shift): <https://docs.astro.build/en/guides/upgrade-to/v7/>
  - Content Collections & `glob()` loader: <https://docs.astro.build/en/guides/content-collections/>
  - Markdown & `@astrojs/markdown-remark` `unified()` / Shiki `excludeLangs` / transformers: <https://docs.astro.build/en/guides/markdown-content/> · <https://docs.astro.build/en/reference/configuration-reference/>
  - Deploy Astro to GitHub Pages (`site`, `base`, `withastro/action`): <https://docs.astro.build/en/guides/deploy/github/>
- **Astro Starlight Official Documentation:**
  - Manual Setup (`docsLoader()` locked to `src/content/docs/`): <https://starlight.astro.build/guides/manual-setup/>
  - Frontmatter Reference (required `title` in `docsSchema()`): <https://starlight.astro.build/reference/frontmatter/>
  - Asides (`:::note`), Overrides Reference, Configuration, & Custom CSS: <https://starlight.astro.build/guides/authoring-content/> · <https://starlight.astro.build/reference/overrides/> · <https://starlight.astro.build/reference/configuration/> · <https://starlight.astro.build/guides/css-and-tailwind/>
- **Repository & Reference Implementation Files Inspected:**
  - `mkdocs.yml`, `scripts/verify_site.py`, `docs/javascripts/prompt-copy.js`, `docs/stylesheets/extra.css`, and all `13` published files in `docs/` (`docs/index.md`, `docs/tutorial/*.md`, `docs/reference/*.md`).
  - `/Users/brett/Documents/GitHub/EnvelopeFollower/reference/docs/adr/0001-astro-core-single-source-site.md`
  - `/Users/brett/Documents/GitHub/EnvelopeFollower/reference/docs/research/static-site-generators.md`
  - `/Users/brett/Documents/GitHub/EnvelopeFollower/reference/site/package.json`, `astro.config.mjs`, `src/content.config.ts`, `src/plugins/rehype-single-source.ts`, `src/plugins/remark-double-dollar-math.ts`, `src/lib/routes.ts`, `src/lib/content-manifest.ts`, `src/lib/mermaid-client.ts`, `src/lib/search-modal.ts`, `src/layouts/DocLayout.astro`, `src/components/FaceplateIllustration.astro`, and `.github/workflows/deploy-pages.yml`.
