# MkDocs Material Dark-Studio Theming Hooks and Click-to-Copy Prompt Patterns

**Issue:** [#5 — Research MkDocs Material dark-studio theming hooks and click-to-copy prompt patterns](https://github.com/domesticmouse/EnvelopeFollower/issues/5)  
**Parent Map:** [#4](https://github.com/domesticmouse/EnvelopeFollower/issues/4)  
**Verified Toolchain (`uvx --with mkdocs-material`):** `mkdocs 1.6.1`, `mkdocs-material 9.8.2`, `pymdown-extensions 13.1.2`

---

## Executive Summary

1. **Exact `ENV / SKEW` palette adoption requires `primary: custom`, `accent: custom`, and `@media screen` scoping — with one critical link-color trap:** In `mkdocs-material 9.8.2`, setting `palette.primary: custom` and `palette.accent: custom` avoids Material's built-in palette overrides so custom `--md-*` CSS custom properties take effect cleanly ([Material Colors](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/)). However, `--md-primary-fg-color` drives `.md-header` and `.md-tabs` backgrounds while `--md-typeset-a-color` defaults to `var(--md-primary-fg-color)` (`main.57a0d79d.min.css`). To match `ENV / SKEW`'s `#1b1d22` studio header (`reference/site/src/styles/global.css:126-132`) without turning the header bright yellow or turning prose links `#1b1d22`, set `--md-primary-fg-color: #1b1d22` / `--md-primary-bg-color: #f4f5f7` AND explicitly override `--md-typeset-a-color: #d8b154` (ENIG Gold, `8.99:1` AAA on `#141518`). Wrap dark-surface overrides in `@media screen { [data-md-color-scheme="slate"] { ... } }`—matching `palette.fb2fffe2.min.css`—so `@media print` still prints cleanly on white paper.
2. **Dark-only `slate` mapping is cleanest; dark-first toggle requires omitting `media:` on the first entry:** Current `mkdocs.yml:13-27` puts `media: "(prefers-color-scheme: light)"` first, so Light-OS visitors land on light indigo/amber. Using a mapping (`palette: { scheme: slate, primary: custom, accent: custom }`) locks dark studio across all templates (`partials/header.html:37-44`) without injecting a palette switcher. If a light toggle is desired while defaulting dark, list `scheme: slate` first *without* a `media:` filter (`components/palette/index.ts:810-814`).
3. **Full `ENV / SKEW` typography (`4` families) needs `theme.font: false` + explicit CSS:** `templates/base.html:64-75` shows `theme.font` only supports two Google Fonts v1 families (`--md-text-font` and `--md-code-font`) at fixed weights (`300/400/700`), and **no `--md-header-font` variable exists** in Material `9.8.2`. Set `theme.font: false`, load `IBM Plex Sans`, `IBM Plex Mono`, `Space Grotesk`, and `Barlow Condensed` via `extra_css` (self-hosted WOFF2 or CSS2), bind `--md-text-font` and `--md-code-font`, and target headings/header title explicitly for `Space Grotesk` and `Barlow Condensed`.
4. **Mermaid dark synchronization already pierces Shadow DOM reactively:** `components/content/mermaid/index.ts:681-712` initializes `mermaid@11` once and injects each SVG into a **closed shadow root**, styled via `--md-mermaid-*` variables declared on `:root > *` (`main.57a0d79d.min.css`). Overriding `--md-mermaid-*` under `[data-md-color-scheme="slate"]` in `extra_css` synchronizes node fills, ENIG Gold borders (`#d8b154`), and edge labels (`#090a0d` / `#141518`) directly into the closed shadow tree without custom Mermaid JS.
5. **MathJax 3 in `mkdocs.yml` is already dark-safe; currency `$` escaping must stay guarded:** `pymdownx.arithmatex: generic: true` + `mathjax@3` + `docs/javascripts/mathjax.js` inherits `currentColor` (`--md-typeset-color`). Keep `mjx-container[display="true"]` / `div.arithmatex` styled on `#090a0d` card wells and keep backticks around literal `$` prices (`$0`, `$3`, `$9`).
6. **Two viable click-to-copy prompt patterns (with key `pymdownx.superfences` & CSS findings):**
   - **Native `content.code.copy` fenced block (` ```text {.prompt title="AI Agent Prompt"} `):** Zero custom JS and works natively with `mkdocs build --strict`, but requires **two strict workarounds**: (a) `{.prompt title="..."}` *must* use brace syntax with explicit `text` language because `superfences.py:44-60,734` makes `options` and `{attrs}` mutually exclusive and pops the first brace class as language; and (b) Material only sets `white-space: pre-wrap` inside `@media print`, so screen CSS must override `.prompt pre > code { white-space: pre-wrap; overflow-wrap: anywhere; }` and boost `.md-code__button` visibility from its default `12%` idle opacity (`--md-default-fg-color--lightest`).
   - **Custom `!!! prompt` admonition + lightweight `document$.subscribe` copy hook (Recommended for rich inline `@[file]` / `/skill` chips):** Preserves inline `<code>` chips for `@[README.md]` and `/skidl` while `el.innerText` copies clean plain text without backticks or outer quote marks, and hooks directly into Material's already-active global `ClipboardJS("[data-clipboard-target], [data-clipboard-text]")` integration (`integrations/clipboard/index.ts:1016-1023`) for instant toast alerts and focus restoration.

---

## 1. Current Baseline & Prompt Inventory in `EnvelopeFollower`

### 1.1 Existing `mkdocs.yml` & Math Setup

In `/Users/brett/Documents/GitHub/EnvelopeFollower/mkdocs.yml`:

- **Exclusions (`mkdocs.yml:7-9`):** `exclude_docs` currently excludes `agents/` and `adr/` (note: `research/` is *not* excluded; per Wayfinder workflow, `docs/research/mkdocs-theming-and-prompts.md` remains on this unmerged `research/` branch).
- **Theme & Palette (`mkdocs.yml:11-36`):** Uses `name: material` with a 2-entry `palette` list (`media: "(prefers-color-scheme: light)"` with `scheme: default`, `primary: indigo`, `accent: amber`, followed by `media: "(prefers-color-scheme: dark)"` with `scheme: slate`). Enabled features include `navigation.tabs`, `navigation.sections`, `navigation.top`, `navigation.footer`, `toc.follow`, `content.code.copy`, `search.suggest`, and `search.highlight` (`navigation.instant` is currently omitted).
- **Markdown Extensions (`mkdocs.yml:38-60`):** Enables `admonition`, `attr_list`, `md_in_html`, `tables`, `toc` (`permalink: true`), `pymdownx.details`, `pymdownx.arithmatex` (`generic: true`), `pymdownx.highlight` (`anchor_linenums: true`), `pymdownx.inlinehilite`, `pymdownx.snippets`, `pymdownx.tabbed` (`alternate_style: true`), `pymdownx.tasklist` (`custom_checkbox: true`), and `pymdownx.superfences` with a `mermaid` custom fence (`pymdownx.superfences.fence_code_format`).
- **Extra Assets (`mkdocs.yml:62-64`):** No `extra_css` yet; `extra_javascript` loads `javascripts/mathjax.js` (`docs/javascripts/mathjax.js:1-19`) and `https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js`.
- **Strict Build Check:** Running `uvx --with mkdocs-material mkdocs build --strict` against `/Users/brett/Documents/GitHub/EnvelopeFollower/mkdocs.yml` (to `/tmp/mkdocs-probe`) builds cleanly in `0.31s` with `0` warnings/errors.

### 1.2 Inventory of Prompt Shapes Across `docs/tutorial/`

Inspecting all tutorial pages (`docs/tutorial/stage-1-agent-skills.md` through `stage-7-manufacturing.md` and `optional-dc-coupled-mode.md`) reveals **four distinct prompt shapes** plus **non-prompt blockquotes** that must *not* be styled as copyable prompts:

| Prompt Shape | Locations (File & Lines) | Formatting Features Inside Prompt | Copy Granularity Needed |
| :--- | :--- | :--- | :--- |
| **1. Single-turn blockquote prompt** | `stage-1-agent-skills.md:60`, `stage-2-circuit-upgrades.md:22,65`, `stage-3-bom-and-dfm.md:11`, `stage-4-skidl.md:11`, `stage-5-schematic-and-pcb.md:11` | Wrapped in `> *"..."*`; contains inline code filenames (`` `EnvelopeFollower.webp` ``), **`@[file]` tokens** (`` `@[README.md]` ``, `` `@[DesignSpec.md]` ``, `` `@[envelope_follower.net]` ``), **`/skill` invocations** (`` `/skidl` ``, `` `/kicad-pcbnew-layout` ``, `` `/kicad-silkscreen-markup` ``, `` `/eurorack-panel` ``, `` `/kicad` ``), and parenthetical prose (`` (`envelope_follower.kicad_pcb`) ``). | 1 prompt = 1 copy action, without outer `*"` / `"*` quotes and without backticks around `@[file]` or `/skill` (verified in raw session logs `prompts/02-...md:22` and `prompts/06-...md:22`: the user typed `@[README.md]` and `/skidl` unbackticked). |
| **2. Multi-turn blockquote sequence** | `stage-3-bom-and-dfm.md:94-96` (2 turns), `stage-4-skidl.md:130-132` (2 turns), `stage-5-schematic-and-pcb.md:57-59` (2 turns) | Single `>` blockquote containing two separate turns separated by a `>` blank line (`Turn 1` then `Turn 2`). | **Independent copy per turn** (a user pastes Turn 1, waits for the agent response, then pastes Turn 2). |
| **3. Inline / tip-admonition prompt snippets** | `stage-1-agent-skills.md:62` (bold phrase), `stage-3-bom-and-dfm.md:13` (italicized finish prompt), `stage-3-bom-and-dfm.md:121` (inside `!!! tip`), `stage-5-schematic-and-pcb.md:113` (list example *"Saved, please tidy/align"*) | Embedded inside prose, lists, or tips as short follow-up phrases. | Keep inline or optionally promote `stage-3:13` / `stage-3:121` if desired; do not force heavy card chrome inline in bullet text. |
| **4. Non-prompt blockquotes (exclusion check)** | `stage-6-front-panel.md:47`, `docs/agents/domain.md:53` | `stage-6-front-panel.md:47` is an italicized editorial note (`> *(The \`switch_submini\` matcher automatically detects...)*`), **not** an AI prompt. | Must remain a standard prose blockquote; never auto-style all `blockquote` elements as prompt cards. |

---

## 2. MkDocs Material `--md-*` Token System & `ENV / SKEW` Mapping

### 2.1 Primary Source Mechanics (`palette.fb2fffe2.min.css` & `main.57a0d79d.min.css`)

From inspecting Material `9.8.2`'s compiled stylesheets (`material/templates/assets/stylesheets/`):

- **Slate base (`palette.fb2fffe2.min.css`):** All default dark tokens live inside `@media screen { [data-md-color-scheme=slate] { color-scheme: dark; ... } }`. Scoping our dark-studio overrides inside `@media screen { [data-md-color-scheme="slate"] { ... } }` is essential so Material's `@media print` rules do not print dark backgrounds on paper.
- **Custom primary/accent behavior (`palette.fb2fffe2.min.css`, [Material Colors](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/)):** Material ships rules for named colors (`indigo`, `amber`, `black`, etc.) and emits **no rules** for `[data-md-color-primary=custom]` or `[data-md-color-accent=custom]`. When `custom` is set in `mkdocs.yml`, Material falls back to `:root` defaults (`#4051b5` / `#526cfe`) unless overridden in `extra_css`.
- **The Header / Link Contrast Trap (`main.57a0d79d.min.css`):**
  - `.md-header`, `.md-tabs`, `.md-nav--primary .md-nav__title[for=__drawer]`, and `.md-typeset .md-button--primary` use `background-color: var(--md-primary-fg-color)` and `color: var(--md-primary-bg-color)`.
  - `.md-nav__source` uses `background-color: var(--md-primary-fg-color--dark)` and `color: var(--md-primary-bg-color)`.
  - `.md-typeset a`, `.md-typeset a code`, `.md-meta__link`, and `.md-nav__item .md-nav__link--active` use `color: var(--md-typeset-a-color)`, which defaults in `slate` to `var(--md-primary-fg-color)`.
  - Therefore, setting `--md-primary-fg-color: #d8b154` would turn the entire top header and tab bar bright gold; conversely, setting `--md-primary-fg-color: #1b1d22` (matching `global.css:130` `.site-header`) **without** overriding `--md-typeset-a-color` would render dark `#1b1d22` links on `#141518` canvas!
- **Admonition colors are hardcoded hex, not `--md-*` variables (`main.57a0d79d.min.css`, [Material Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)):** `.md-typeset .admonition` sets `color: var(--md-admonition-fg-color)` and `background-color: var(--md-admonition-bg-color)`, while each variant (`note`, `info`, `tip`, `warning`, `danger`, etc.) hardcodes its border, title tint, and icon mask `background-color` (e.g., `#448aff`, `#00bfa5`, `#ff9100`, `#ff1744`). Darkening `--md-admonition-bg-color` to `--bg-surface` (`#1b1d22`) and adding a custom `.admonition.prompt` / `.admonition.tip` rule aligns them cleanly with `ENV / SKEW`.
- **Scrollbar styling (`main.57a0d79d.min.css`):** Pre/code blocks, search scrollwrap, sidebar scrollwrap, and tooltips use `scrollbar-color: var(--md-default-fg-color--lighter) #0000; scrollbar-width: thin` (and `--md-accent-fg-color` on `:hover`, plus `::-webkit-scrollbar-thumb`). Note `tokens.css:27` explicitly warns: *never transition/animate `scrollbar-color`*.
- **Focus rings (`main.57a0d79d.min.css` + `bundle.ts`):** Material imports `focus-visible` polyfill (`bundle.ts:25`) and applies `outline-color: var(--md-accent-fg-color)` across `.focus-visible` selectors (`.md-typeset a.focus-visible`, `.md-code__button.focus-visible`, `.md-nav__link.focus-visible`, `.md-tabs__link`, `.md-header__button`, `.md-typeset summary.focus-visible`). Adding `:focus-visible { outline: 2px solid #e2be66; outline-offset: 2px; }` matches `tokens.css:35` & `global.css:74-77`.

### 2.2 Exact `tokens.css` → MkDocs Material `--md-*` Token Mapping

All contrast ratios below are calculated directly against the hex values in `reference/site/src/styles/tokens.css:4-36`:

| `tokens.css` / `global.css` / `docs.css` Token | Hex / Value | Material `--md-*` Custom Property (inside `@media screen { [data-md-color-scheme="slate"] }`) | Contrast / Notes |
| :--- | :--- | :--- | :--- |
| `--bg-canvas` (`tokens.css:5`) | `#141518` | `--md-default-bg-color: #141518` | Primary page canvas (Matte Black FR4). Derived variants: `--md-default-bg-color--light: rgba(20, 21, 24, 0.72)`, `--md-default-bg-color--lighter: rgba(20, 21, 24, 0.45)`, `--md-default-bg-color--lightest: rgba(20, 21, 24, 0.16)` (also used by Material `.tabbed-control` gradient fade). |
| `--ink-primary` (`tokens.css:10`) | `#e8eaef` | `--md-default-fg-color: #e8eaef`<br>`--md-typeset-color: #e8eaef` | **`15.17:1` AAA** on `#141518`; `14.01:1` AAA on `#1b1d22`. |
| `--ink-muted` (`tokens.css:12`) | `#a6acb8` | `--md-default-fg-color--light: #a6acb8` | **`8.01:1` AAA** on `#141518` (muted captions, breadcrumbs, TOC labels, comments). |
| `--border-ui` (`tokens.css:17`) / `--border-subtle` (`tokens.css:18`) | `#6e7485` / `#2b2f3b` | `--md-default-fg-color--lighter: rgba(166, 172, 184, 0.48)`<br>`--md-default-fg-color--lightest: #2b2f3b` | `#6e7485` (`3.91:1 >= 3:1` UI border contrast on `#141518`) for interactive borders; `#2b2f3b` for subtle dividers, `hr`, and table/code borders (`--md-typeset-table-color: #2b2f3b`, `--md-typeset-table-color--light: rgba(255, 255, 255, 0.025)`). |
| `--bg-surface` (`tokens.css:6`) & `global.css:130` | `#1b1d22` | `--md-primary-fg-color: #1b1d22`<br>`--md-primary-fg-color--light: #1d2028`<br>`--md-primary-fg-color--dark: #0d0e11`<br>`--md-admonition-bg-color: #1b1d22`<br>`--md-admonition-fg-color: #e8eaef` | Studio header/tabs (`#1b1d22`) and repo source pill (`--bg-void` `#0d0e11`), with `border-bottom: 2px solid #d8b154` added on `.md-header` (or `.md-tabs`) to echo `global.css:131`. |
| `--ink-silk` (`tokens.css:11`) | `#f4f5f7` | `--md-primary-bg-color: #f4f5f7`<br>`--md-primary-bg-color--light: #a6acb8` | **`15.46:1` AAA** on `#1b1d22` (header title, search icon, tab labels); explicit CSS `color: #f4f5f7` for `.md-typeset h1, h2, h4`. |
| `--accent-gold` (`tokens.css:13`) & `--accent-gold-bright` (`tokens.css:14`) & `--accent-gold-ink` (`tokens.css:15`) | `#d8b154` / `#e2be66` / `#141518` | `--md-typeset-a-color: #d8b154`<br>`--md-accent-fg-color: #e2be66`<br>`--md-accent-fg-color--transparent: rgba(216, 177, 84, 0.14)`<br>`--md-accent-bg-color: #141518`<br>`--md-accent-bg-color--light: rgba(20, 21, 24, 0.72)` | Links `#d8b154` (**`8.99:1` AAA** on `#141518`); hover/focus `#e2be66` (**`10.25:1` AAA** on `#141518`); knocked-out ink `#141518` on hovered `.md-button` / `.md-top` (`8.99:1` AAA on `#d8b154`). |
| `--bg-code` (`tokens.css:8`) & `--bg-code-elevated` (`tokens.css:9`) | `#090a0d` / `#101216` | `--md-code-bg-color: #090a0d`<br>`--md-code-bg-color--light: #101216`<br>`--md-code-bg-color--lighter: rgba(16, 18, 22, 0.75)`<br>`--md-code-fg-color: #e8eaef` | **`16.45:1` AAA** on `#090a0d` code wells (`docs.css:394`). Override inline `:not(pre) > code` to `--bg-code-elevated` (`#101216`) + `1px solid #2b2f3b` border + `#f4f5f7` text to match `docs.css:382-389`. |
| Code syntax & highlights (`main.57a0d79d.min.css`) | Studio dark-high-contrast | `--md-code-hl-color: #d8b154`<br>`--md-code-hl-color--light: #262013`<br>`--md-code-hl-comment-color: #a6acb8`<br>`--md-code-hl-keyword-color: #e2be66`<br>`--md-code-hl-string-color: #4ade80`<br>`--md-code-hl-number-color: #fbbf24`<br>`--md-code-hl-special-color: #f87171` | Reuses `--accent-gold-tint` (`#262013`), `--led-green` (`#4ade80`), amber (`#fbbf24`), and `--led-red` (`#f87171`) from `tokens.css:16,20-23` & `global.css:517`. |
| `<kbd>` (`tokens.css:17`, `global.css:53-62`) | `#090a0d` / `#6e7485` | `--md-typeset-kbd-color: #090a0d`<br>`--md-typeset-kbd-accent-color: #1b1d22`<br>`--md-typeset-kbd-border-color: #6e7485` | Matches `global.css:53-62` keycap contrast. |
| Footer (`tokens.css:6,12,13`, `global.css:569-575`) | `#1b1d22` / `#0d0e11` | `--md-footer-bg-color: #1b1d22`<br>`--md-footer-bg-color--dark: #0d0e11`<br>`--md-footer-fg-color: #f4f5f7`<br>`--md-footer-fg-color--light: #a6acb8`<br>`--md-footer-fg-color--lighter: #6e7485` | Elevated `#1b1d22` footer prev/next band over `#0d0e11` obsidian meta strip (`global.css:569-611`). |
| Tables (`docs.css:415-483`) | `#1b1d22` / `#1d2028` | `--md-typeset-table-color: #2b2f3b`<br>`--md-typeset-table-color--light: rgba(255, 255, 255, 0.025)` | Material's `.md-typeset table:not([class])` uses `--md-default-bg-color` by default (`main.57a0d79d.min.css`); add CSS rules for `table:not([class]) thead th` (`background: #1d2028`, `color: #f4f5f7`, `border-bottom: 2px solid #d8b154`) and `tbody` (`background: #1b1d22`) to match `docs.css:452-483`. |
| Shadows & Selection | Sharp studio elevation | `--md-shadow-z1: 0 0 0 1px #2b2f3b`<br>`--md-shadow-z2: 0 0.25rem 0.75rem rgba(0,0,0,0.45), 0 0 0 1px #6e7485` | Plus `::selection { background: #d8b154; color: #141518; }` (`global.css:69-72`). |

---

## 3. `theme.palette`, Fonts, and Asset Hooks in `mkdocs.yml`

### 3.1 `theme.palette`: Dark-Only `slate` vs. Dark-Default with Light Toggle

Inspecting `templates/base.html:86-97`, `templates/partials/header.html:37-44`, and `javascripts/components/palette/index.ts:807-887`:

- **Option 1 — Locked Dark-Only `slate` (Recommended for `ENV / SKEW` parity):**
  ```yaml
  theme:
    name: material
    palette:
      scheme: slate
      primary: custom
      accent: custom
  ```
  Because `config.theme.palette` is a YAML **mapping** (not a list), `header.html:37-44` omits `partials/palette.html` and `partials/javascripts/palette.html`, `base.html:94` stamps `data-md-color-scheme="slate" data-md-color-primary="custom" data-md-color-accent="custom"` directly on `<body>`, and `palette.fb2fffe2.min.css` sets `color-scheme: dark` in CSS. Zero flash of wrong theme, zero toggle maintenance on custom `--md-*` variables, and exact parity with `tokens.css:1` (`locked dark-only screen subset`).
- **Option 2 — Dark-Default (`slate`) with Optional Light Toggle (`default`):**
  If a light toggle is kept, **remove `media:`** on the first entry (or use `(prefers-color-scheme: light)` only on the light option *after* an explicit default, noting `watchPalette` runs `inputs.findIndex(input => matchMedia(input.getAttribute("data-md-color-media")!).matches)` on first visit when `localStorage.__palette` is unset). With `media:` omitted (`None`), `matchMedia("")` matches index `0`, so putting `scheme: slate` first boots every visitor into dark studio while keeping a header toggle for `scheme: default`. All custom dark overrides **must** stay scoped inside `@media screen { [data-md-color-scheme="slate"] { ... } }` so toggling to `default` reverts cleanly to light mode (remembering Mermaid and custom prompt cards must also remain legible in `default` if a light toggle is exposed).

### 3.2 Font Loading (`theme.font: false` vs. `theme.font`)

`templates/base.html:64-75` reveals Material's built-in font block:
```jinja
{% if config.theme.font != false %}
  {% set text = config.theme.font.text | d("Roboto", true) %}
  {% set code = config.theme.font.code | d("Roboto Mono", true) %}
  ...
  <style>:root{--md-text-font:"{{ text }}";--md-code-font:"{{ code }}"}</style>
{% endif %}
```
This creates three constraints for `ENV / SKEW` (`tokens.css:29-32`, `fonts.css:1-16`):
1. `theme.font` only loads **two** Google Fonts v1 families (`text` at `300,300i,400,400i,700,700i` and `code` at `400,400i,700,700i`), missing weights `500`/`600`/`800` used by `Space Grotesk`, `IBM Plex Sans`/`Mono`, and `Barlow Condensed`.
2. Material `9.8.2` defines `--md-text-font` and `--md-code-font` only (`--md-header-font` does **not** exist in `main.57a0d79d.min.css`).
3. `reference/site/src/styles/fonts.css:1` self-hosts Latin WOFF2 subsets (`zero third-party font requests`).

**Recommended Setup (`mkdocs.yml` + `extra_css`):**
- Set `theme.font: false` ([Material Fonts](https://squidfunk.github.io/mkdocs-material/setup/changing-the-fonts/)).
- Load `Barlow Condensed` (700, 800), `Space Grotesk` (500, 600, 700), `IBM Plex Sans` (400, 500, 600, 700), and `IBM Plex Mono` (400, 500, 600) either as self-hosted `.woff2` files under `docs/assets/fonts/` with `@font-face` in `docs/stylesheets/fonts.css` (best for offline/privacy parity with `reference/site`) or via a Google Fonts CSS2 `@import` in `docs/stylesheets/fonts.css`.
- Bind Material's tokens plus explicit heading/brand rules in `docs/stylesheets/extra.css`:
  ```css
  :root {
    --md-text-font: "IBM Plex Sans";
    --md-code-font: "IBM Plex Mono";
    --font-display: "Space Grotesk", var(--md-text-font-family);
    --font-slab: "Barlow Condensed", "DIN Condensed", var(--md-text-font-family);
  }
  .md-typeset h1, .md-typeset h2, .md-typeset h3, .md-typeset h4,
  .md-tabs__link, .md-header__title {
    font-family: var(--font-display);
  }
  ```

---

## 4. Mermaid Dark-Theme Synchronization

### 4.1 How Material `9.8.2` Renders and Themes Mermaid

Inspecting `components/content/mermaid/index.ts:658-713` and `components/content/mermaid/index.css` shows:

1. `mkdocs.yml:56-60` already uses `pymdownx.superfences` with `fence_code_format`, outputting `<pre class="mermaid"><code>...</code></pre>` (verified in built HTML for `optional-dc-coupled-mode/index.html`).
2. `mountMermaid` (`content/mermaid/index.ts:660,679-712`) dynamically loads `https://unpkg.com/mermaid@11/dist/mermaid.min.js`, calls `mermaid.initialize({ startOnLoad: false, themeCSS, ... })` **once** (`shareReplay(1)`), renders `<svg>` via `mermaid.render(id, text)`, and attaches it inside a **closed Shadow DOM** (`host.attachShadow({ mode: "closed" })`).
3. Because CSS custom properties pierce closed shadow roots, Material's `themeCSS` (`mermaid/index.css`) drives all diagram colors via `--md-mermaid-*` variables declared on `:root > *` (`main.57a0d79d.min.css`):
   - `--md-mermaid-font-family: var(--md-text-font-family), sans-serif`
   - `--md-mermaid-edge-color: var(--md-code-fg-color)`
   - `--md-mermaid-node-bg-color: var(--md-accent-fg-color--transparent)`
   - `--md-mermaid-node-fg-color: var(--md-accent-fg-color)`
   - `--md-mermaid-label-bg-color: var(--md-default-bg-color)`
   - `--md-mermaid-label-fg-color: var(--md-code-fg-color)`

### 4.2 Studio Mapping & Pitfalls (Light/Dark Toggle & Shadow DOM)

- **Match `reference/site/src/lib/mermaid-client.ts:14-43` via CSS custom properties:** Override `--md-mermaid-*` inside `@media screen { [data-md-color-scheme="slate"] { ... } }` (not `:root`, because `:root > *` in `main.57a0d79d.min.css` redeclares `--md-mermaid-*` directly on `<body>`, shadowing inherited `:root` values!):
  - `--md-mermaid-node-bg-color: #1b1d22` (or `#262013` `--accent-gold-tint`)
  - `--md-mermaid-node-fg-color: #d8b154` (ENIG Gold node border, matching `mermaid-client.ts:25`)
  - `--md-mermaid-edge-color: #d8b154` (ENIG Gold connectors/arrowheads, matching `mermaid-client.ts:30`)
  - `--md-mermaid-label-bg-color: #141518` (canvas-matched edge label pill, matching `mermaid-client.ts:32`)
  - `--md-mermaid-label-fg-color: #f4f5f7` (Silkscreen White node/label ink, matching `mermaid-client.ts:24`)
  - Style the outer `div.mermaid` host card on `--bg-code` (`#090a0d`) with `1px solid #6e7485` and `overflow-x: auto` (`docs.css:600-615`).
- **Pitfalls to avoid:**
  - **External selectors cannot penetrate closed Shadow DOM:** Do *not* write `.mermaid svg rect { ... }` in `extra_css` — `attachShadow({ mode: "closed" })` blocks external element selectors (`mermaid/index.ts:707`). Only CSS custom properties (`--md-mermaid-*`, `--md-default-*`, `--md-text-font-family`) and properties inherited by `div.mermaid` penetrate.
  - **Light/Dark toggle caveat:** Since `mermaid.initialize` runs once with `themeCSS`, custom `--md-mermaid-*` values scoped under `[data-md-color-scheme="slate"]` *will* live-update if a user toggles light/dark, whereas hardcoding dark hexes on `:root > *` without `[data-md-color-scheme="slate"]` would leave dark nodes/light text on a white light-mode page.
  - **Subgraph/cluster contrast:** `mermaid/index.css` sets `.cluster rect { fill: var(--md-default-fg-color--lightest); stroke: var(--md-default-fg-color--lighter) }`. Setting `--md-default-fg-color--lightest: #2b2f3b` keeps subgraphs cleanly framed rather than washed out.

---

## 5. MathJax / KaTeX Compatibility Under Dark Surfaces

Inspecting `mkdocs.yml:46-47,62-64`, `docs/javascripts/mathjax.js:1-19`, `main.57a0d79d.min.css`, and the built HTML (`stage-2-circuit-upgrades/index.html`, `optional-dc-coupled-mode/index.html`):

- **Current MathJax 3 setup works natively in dark mode:** `pymdownx.arithmatex: generic: true` wraps `$...$` in `<span class="arithmatex">\(...\)</span>` (`26` spans in `stage-2`) and `\[...\]` in `<div class="arithmatex">\[...\]</div>` (`2` blocks in `optional-dc-coupled-mode`). MathJax 3 CommonHTML (`tex-mml-chtml.js`) inherits `color: currentColor` (`--md-typeset-color`, `#e8eaef` in `slate`), so formulas remain high-contrast without inverting or per-color JS hooks ([Material Math](https://squidfunk.github.io/mkdocs-material/reference/math/)).
- **`document$.subscribe` lifecycle:** `docs/javascripts/mathjax.js:14-19` already subscribes to `window.document$`, which `browser/document/index.ts:39-45` emits on initial `DOMContentLoaded` and on every instant navigation if `navigation.instant` is later enabled.
- **Studio equation well styling:** `main.57a0d79d.min.css` gives `.md-typeset div.arithmatex` `overflow: auto` and horizontal padding on mobile. Adding a subtle dark card rule on `.md-typeset div.arithmatex` (`background: #090a0d; border: 1px solid #2b2f3b; padding: 0.85rem 1rem; color: #f4f5f7;`) matches `docs.css:563-571` (`.katex-display`) while keeping `.arithmatex mjx-assistive-mml { height: 0 }` intact.
- **KaTeX alternative (`mkdocs.yml` swap option):** Switching to KaTeX is only needed if build/paint speed on math-heavy pages becomes a concern; it uses the same `pymdownx.arithmatex: generic: true` output and inherits `.md-typeset` dark ink identically, though `docs/tutorial/` already uses `\[...\]` and `$...$` cleanly with MathJax 3 (`stage-2` and `optional-dc-coupled-mode`) and already guards literal currency `$` prices in backticks (`index.md:3` `\$4`, `stage-3:86,103` `` `$9` `` / `` `$0` ``, `stage-7:81,97`, `netlist-and-bom.md:14`). Keeping MathJax 3 avoids an unnecessary CDN swap while staying dark-ready.

---

## 6. Click-to-Copy AI Agent Prompt Patterns (Comparison & Trade-Offs)

### 6.1 Key Technical Constraints Discovered in Primary Sources

1. **Non-prompt blockquotes exist (`stage-6-front-panel.md:47`, `docs/agents/domain.md:53`):** Plain CSS styling of `.md-typeset blockquote` cannot distinguish AI prompts from editorial callouts. Prompts need an explicit semantic marker (fenced class/title or `!!! prompt` admonition).
2. **Material `content.code.copy` JS & DOM (`components/content/code/_/index.ts:541-559`, `integrations/clipboard/index.ts:992-1035`):**
   - `mountCodeBlock` attaches `<nav class="md-code__nav"><button class="md-code__button" title="Copy to clipboard" data-clipboard-target="#__code_N > code" data-md-type="copy"></button></nav>` inside `<pre>`.
   - `setupClipboardJS` registers a **single delegated** `ClipboardJS("[data-clipboard-target], [data-clipboard-text]")` listener at boot (`bundle.ts:154`), calling `extract(target)` which sets `data-md-copying`, reads `[data-copy]` or `el.innerText.trimEnd()`, triggers Material's `"Copied to clipboard"` toast (`alert$`), and returns focus (`trigger.focus()`).
   - **Important CSS gotcha:** By default, `.md-code__button` has `color: var(--md-default-fg-color--lightest)` (only `12%` opacity in `slate`!) until hovered (`main.57a0d79d.min.css`). For prompt cards, `.prompt .md-code__button` must be always visible (e.g., ENIG Gold `#d8b154` border/pill or full-contrast icon + `"Copy"` label).
3. **`white-space: pre-wrap` & `innerText` wrapping behavior:**
   - In Material `9.8.2`, `.md-typeset code, .md-typeset pre { white-space: pre-wrap }` is scoped inside `@media print` **only** (`main.57a0d79d.min.css`). On screen, `.md-typeset pre > code` has `overflow: auto; word-break: normal` over `<pre>`'s default `white-space: pre`, causing horizontal scrollbars on long prompt lines.
   - Setting `white-space: pre-wrap; overflow-wrap: anywhere;` on prompt code blocks eliminates horizontal scrollbars on long `@[file]` / `/skill` strings while **not** corrupting clipboard output: per the WHATWG HTML Standard for `HTMLElement.innerText`, CSS soft line wraps are visual only and do **not** insert `\n` characters into `innerText` ([HTML Standard / MDN `innerText`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/innerText)).
   - With `anchor_linenums: true` enabled (`mkdocs.yml:49`), Pygments emits empty `<a id="__codelineno-0-1" ...></a>` elements inside `<code>`; Material's `.highlight code[data-md-copying] { display: initial }` ensures `innerText` produces zero extra line breaks.
4. **`pymdownx.superfences` header parsing trap (`pymdownx/superfences.py:44-60,713-734`):**
   - Verified empirically with `pymdownx 13.1.2`: `RE_NESTED_FENCE_START` treats `{attrs}` and `key="value"` options as **mutually exclusive alternatives**.
   - ` ```text title="AI Agent Prompt" {.prompt .copy} ` **fails completely** and degrades into an inline `<p><code>...</code></p>` paragraph!
   - ` ```{.prompt .copy title="AI Agent Prompt"} ` **drops `.prompt`**, because `handle_attrs` pops `self.classes.pop(0)` as the highlight language (`superfences.py:734`), leaving `<div class="copy highlight">`.
   - **Only** ` ```text {.prompt title="AI Agent Prompt"} ` (explicit `text` language *before* `{...}`) outputs `<div class="prompt highlight"><span class="filename">AI Agent Prompt</span><pre>...</pre></div>`.

### 6.2 Pattern Matrix

| Dimension | Pattern A: Native Fenced Prompt (` ```text {.prompt title="AI Agent Prompt"} `) | Pattern B: Custom `!!! prompt` Admonition + `extra_javascript` (Recommended) | Pattern C: Hybrid (`!!! prompt` wrapper around fenced turns, or custom `superfences` formatter) |
| :--- | :--- | :--- | :--- |
| **Markdown Authoring** | ```` ```text {.prompt title="AI Agent Prompt"} ```` (multi-turn split into 2 fenced blocks: `Turn 1`, `Turn 2`). | `!!! prompt "AI Agent Prompt"` with indented body (or `!!! prompt "Turn 1"` / `"Turn 2"`, or nested `> ` / `[data-prompt-turn]` sub-cards). | `!!! prompt "AI Agent Prompt"` containing nested ```` ```text {.prompt-turn} ```` fences, OR a custom Python `superfences` formatter module. |
| **Inline `@[file]` & `/skill` Styling** | Monospace plain text only; writing backticks (`` `/skidl` ``) inside a `text` fence causes literal backticks to display and copy. | **Full Markdown inline `<code>` pills** (`` `/skidl` ``, `` `@[DesignSpec.md]` ``) plus bold/italic emphasis render cleanly in studio code-chip styling. | Same as A inside nested fenced turns (no inline chips), or full custom HTML if writing a Python `superfences` formatter. |
| **Copied Clipboard Text** | Exact raw text inside fence (no quotes, no backticks if omitted in source). | `el.innerText` on prompt body strips HTML `<code>` tags cleanly → copies exact `/skidl Please turn @[DesignSpec.md] into a circuit.` (if outer `*"` / `"*` quotes are dropped from source). | Identical to A (if nested fences) or B (if custom formatter populates `data-clipboard-text`). |
| **Word Wrap / Zero Scrollbar** | Requires CSS override: `.prompt.highlight pre > code { white-space: pre-wrap; overflow-wrap: anywhere; padding-inline-end: 4rem; }`. | Natural prose `<p>` wrapping out of the box (`overflow-wrap: anywhere` on inline `<code>` handles long `@[EnvelopeFollowerImprovements.md]`). | Same CSS override needed for nested `<pre><code>`. |
| **Copy Button Prominence & UX** | Reuses `content.code.copy` (`.md-code__nav` / `.md-code__button` inside `<pre>`). Needs CSS to stay opaque, gold-bordered, and clear of `span.filename` (`padding-top` or absolute alignment). | Button injected directly into `.admonition-title` bar (`flex` header: `[icon] AI Agent Prompt` on left, crisp `[Copy]` pill button on right) using Material's built-in `data-clipboard-target` (`ClipboardJS` + toast!). | Nested fence puts copy button inside each inner `<pre>`, creating double borders/headers around single-sentence prompts. |
| **Accessibility & Keyboard** | `<button class="md-code__button" title="Copy to clipboard">` receives focus (`focus-visible`) and triggers Material `alert$` toast. Icon-only unless `::before`/`::after` text or `aria-label` is styled. | Native `<button type="button" class="prompt-copy-btn" data-clipboard-target="#...">` with visible `"Copy"` label + `aria-label="Copy prompt"`, `:focus-visible` `2px solid #e2be66`, `min-block-size: 32px`, and Material `alert$` live toast + transient `"Copied"` state. | Same as A; double nested landmarks can add noise for screen readers. |
| **Multi-Turn Prompts (`stage-3`, `4`, `5`)** | Two separate fenced blocks (`Turn 1`, `Turn 2`) give independent copy buttons. | Two stacked `!!! prompt "Turn 1"` / `!!! prompt "Turn 2"` cards (or one `!!! prompt` card with two turn sub-blocks each getting its own Copy button). | One `!!! prompt` outer card visually groups Turn 1 and Turn 2 while each inner fence gets its own Copy button. |
| **JS / Python Complexity & `--strict`** | **Zero custom JS**, zero Python plugins; 100% `mkdocs build --strict` safe. | **~25 lines** of `extra_javascript` inside `document$.subscribe(...)` (zero external deps, reuses Material's `ClipboardJS` + `navigator.clipboard` optional enhancement); 100% `mkdocs build --strict` safe. | Custom Python formatter breaks portability unless a local package is on `PYTHONPATH`; nested fences add visual bulk without fixing inline chip rendering. |

### 6.3 Recommended Prompt Architecture for the Prototype Ticket

Adopt **Pattern B (`!!! prompt` admonition + `document$.subscribe` + Material's native `data-clipboard-target`)**, with **Pattern A (` ```text {.prompt title="AI Agent Prompt"} `)** documented as the zero-JS fallback:

- **Why Pattern B wins for this tutorial:** Every tutorial prompt relies heavily on `@[DesignSpec.md]`, `@[README.md]`, `@[EnvelopeFollowerImprovements.md]`, and `/skill` tokens (`/skidl`, `/kicad-pcbnew-layout`, `/edit-silkscreen`). Pattern B preserves crisp ENIG-tinted inline `<code>` pills visually (`stage-1` through `stage-5`), removes decorative `*"..."*` blockquote quotes so copied text pastes directly into Antigravity/Claude/Cursor without manual quote-trimming, wraps naturally at any viewport width without horizontal scrollbars or copy-button text collisions, and places a high-contrast ENIG Gold `"Copy"` button directly in the `.admonition-title` header bar.
- **Zero-dependency clipboard integration (`docs/javascripts/prompt-copy.js`):**
  1. Subscribe to `document$.subscribe(() => { ... })` so it works both on initial load and if `navigation.instant` is later enabled (`bundle.ts:127,322`).
  2. For each `.md-typeset .admonition.prompt`, wrap all child nodes after `.admonition-title` into a `<div class="prompt-body" id="prompt-body-<n>">` container (idempotent guard `if (el.dataset.promptBound) return`).
  3. Append `<button type="button" class="md-button prompt-copy-btn" data-clipboard-target="#prompt-body-<n>" aria-label="Copy prompt to clipboard">Copy</button>` inside `.admonition-title` (turning `.admonition-title` into a flex row).
  4. Because `setupClipboardJS` (`integrations/clipboard/index.ts:1016-1023`) delegates globally on `[data-clipboard-target]`, clicking or pressing Enter/Space on `.prompt-copy-btn` automatically copies `promptBody.innerText.trimEnd()` (no backticks, no soft-wrap `\n`), fires Material's `"Copied to clipboard"` toast (`alert$`), and keeps focus on the button; a lightweight click listener can briefly flip the button label/attribute (`data-copied="true"`) for `1500ms`.
  5. For the three 2-turn sequences (`stage-3:94-96`, `stage-4:130-132`, `stage-5:57-59`), split into `!!! prompt "AI Agent Prompt — Turn 1"` and `!!! prompt "AI Agent Prompt — Turn 2"` (or group inside one `!!! prompt` with `**Turn 1**` / `> ` sub-blocks if single-box grouping is preferred). Leave non-prompt editorial blockquotes (`stage-6-front-panel.md:47`) as standard `>` blockquotes.
- **Custom admonition CSS (`docs/stylesheets/extra.css`, [Material Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)):**
  - Define `--md-admonition-icon--prompt` SVG data URI on `:root` (e.g., terminal/sparkle icon).
  - Style `.md-typeset .admonition.prompt` with `#1b1d22` body (`--bg-surface`), `1px solid #d8b154` border + `3px solid #d8b154` left rail (`global.css` / `docs.css:207,370`), `#262013` (`--accent-gold-tint`) title header bar, `#d8b154` icon mask, and `#f4f5f7` title text.
  - Keep `.prompt-copy-btn` styled with `#d8b154` border / `#141518` background (hovering to solid `#d8b154` with `#141518` knocked-out text, matching `.cta-primary` / `.md-button` contrast `8.99:1`).

---

## 7. Concrete Guidance for the Upcoming Prototype Ticket

1. **Files to touch in the prototype PR:**
   - `mkdocs.yml`: Set dark-only `palette: { scheme: slate, primary: custom, accent: custom }`, `font: false`, add `extra_css` (`stylesheets/fonts.css`, `stylesheets/extra.css`), and add `javascripts/prompt-copy.js` to `extra_javascript`.
   - `docs/stylesheets/fonts.css` (+ optional `docs/assets/fonts/*.woff2` for offline parity) and `docs/stylesheets/extra.css`: Implement the Section 2.2 token table inside `@media screen { [data-md-color-scheme="slate"] { ... } }`, plus custom table headers, inline code pills, dark MathJax wells, Mermaid host card, and `.admonition.prompt` styling.
   - `docs/javascripts/prompt-copy.js`: Idempotent `document$.subscribe(...)` initializer wiring `.admonition.prompt` headers to Material's native `[data-clipboard-target]`.
   - `docs/tutorial/stage-1-agent-skills.md` through `stage-5-schematic-and-pcb.md`: Convert prompt blockquotes (`10` prompt blocks total, splitting the `3` multi-turn blocks into Turn 1 / Turn 2) to `!!! prompt "..."` without outer `*"..."*` quotes, while keeping `stage-6-front-panel.md:47` as a normal blockquote.
2. **Verification gates for the prototype:**
   - `uvx --with mkdocs-material mkdocs build --strict` exits `0` with zero warnings.
   - Visually inspect rendered pages in dark studio (`#141518` / `#1b1d22` / `#090a0d` / `#d8b154`), verify `optional-dc-coupled-mode` and `stage-2` MathJax equations, verify `index` / `stage-3` / `stage-6` / `stage-7` Mermaid diagrams (including edge labels in `stage-3`), test click & keyboard Copy on single-turn and multi-turn prompts (confirming no backticks, no outer quotes, and no soft-wrap newlines in clipboard), and test print preview (`@media print`) to ensure white-paper legibility.
   - **Note on `mkdocs.yml` `exclude_docs`:** On `main`, `mkdocs.yml:7-9` excludes `agents/` and `adr/` (not `research/`). Keep `docs/research/mkdocs-theming-and-prompts.md` on this unmerged `research/` branch per Wayfinder policy rather than merging into `main`.

---

## 8. Primary Sources Cited

- **MkDocs Material Official Documentation:**
  - Changing the colors (`primary: custom`, `accent: custom`, `slate`, `:root > *`, `[data-md-color-scheme]`): `https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/`
  - Changing the fonts (`theme.font: false`, `@font-face`, `--md-text-font`, `--md-code-font`): `https://squidfunk.github.io/mkdocs-material/setup/changing-the-fonts/`
  - Customization (`extra_css`, `extra_javascript`, `document$`): `https://squidfunk.github.io/mkdocs-material/customization/`
  - Code blocks (`content.code.copy`, `title="..."`, `.copy` `attr_list`): `https://squidfunk.github.io/mkdocs-material/reference/code-blocks/`
  - Diagrams (`pymdownx.superfences`, Mermaid theme synchronization): `https://squidfunk.github.io/mkdocs-material/reference/diagrams/`
  - Math (`pymdownx.arithmatex`, MathJax 3, KaTeX): `https://squidfunk.github.io/mkdocs-material/reference/math/`
  - Admonitions (custom admonition CSS, `mask-image`, `background-color` icon coloring): `https://squidfunk.github.io/mkdocs-material/reference/admonitions/`
- **PyMdown Extensions Official Documentation:**
  - SuperFences (`custom_fences`, `fence_code_format`, `attr_list` vs options): `https://facelessuser.github.io/pymdown-extensions/extensions/superfences/`
  - Highlight (`title`, `auto_title`, `anchor_linenums`, `extend_pygments_lang`): `https://facelessuser.github.io/pymdown-extensions/extensions/highlight/`
  - Arithmatex (`generic: true`, `tex_inline_wrap`, `tex_block_wrap`): `https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/`
- **Installed Package Sources (`mkdocs 1.6.1`, `mkdocs-material 9.8.2`, `pymdown-extensions 13.1.2`):**
  - `material/templates/base.html:64-97` (fonts block & palette body attributes)
  - `material/templates/partials/header.html:37-44` & `partials/palette.html:4-16` & `partials/javascripts/palette.html:4` (mapping vs list palette behavior)
  - `material/templates/assets/stylesheets/palette.fb2fffe2.min.css` (`@media screen { [data-md-color-scheme=slate] }`, named primary/accent rules)
  - `material/templates/assets/stylesheets/main.57a0d79d.min.css` (all `--md-*` definitions/consumers, `:root > *` `--md-mermaid-*`, `@media print` `white-space: pre-wrap`, `.md-code__button`, `.arithmatex`)
  - `material/templates/assets/javascripts/bundle.a5f9d56c.min.js.map` (`bundle.ts:25,127-169,322-332`, `browser/document/index.ts:39-45`, `components/content/code/_/index.ts:540-560`, `components/content/mermaid/index.ts:658-713` & `index.css`, `components/palette/index.ts:807-934`, `integrations/clipboard/index.ts:992-1035`, `templates/clipboard/index.tsx:43-68`)
  - `pymdownx/superfences.py:44-60,137-193,713-750` (`RE_NESTED_FENCE_START`, `fence_code_format`, `handle_attrs`) and `pymdownx/highlight.py:47-141,236-498` (`DEFAULT_CONFIG`, `BlockHtmlFormatter`, `Highlight.highlight`)
- **Repository Files Inspected:**
  - `mkdocs.yml:1-79`, `docs/javascripts/mathjax.js:1-19`
  - `reference/site/src/styles/tokens.css:1-36`, `global.css:1-933`, `docs.css:1-925`, `fonts.css:1-16`, `reference/site/src/lib/mermaid-client.ts:1-101`, `reference/site/src/layouts/SiteLayout.astro:1-67`, `reference/site/src/components/MermaidHydrator.astro:1-5`
  - `docs/index.md:1-87`, `docs/tutorial/stage-1-agent-skills.md:1-107`, `stage-2-circuit-upgrades.md:1-98`, `stage-3-bom-and-dfm.md:1-121`, `stage-4-skidl.md:1-175`, `stage-5-schematic-and-pcb.md:1-123`, `stage-6-front-panel.md:1-164`, `stage-7-manufacturing.md:1-206`, `optional-dc-coupled-mode.md:1-80`, `docs/reference/netlist-and-bom.md:1-120`, `docs/reference/build-checklist.md:1-65`, `docs/agents/domain.md:53`, `prompts/02-7f75c0c1-please-review-envelopefollower-webp-i-d-like.md:1-30`, `prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md:1-30`
- **Web Standards:**
  - MDN / WHATWG `HTMLElement.innerText` (`white-space: pre-wrap` soft-wrap preservation behavior): `https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/innerText`
