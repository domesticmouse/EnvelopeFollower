---
status: accepted
---

# Astro Core in `site/` with Relocated MDX Content Collections and Managed Image Assets

We will build the **`ENV / SKEW` Build Tutorial** GitHub Pages site using **Astro (Core)** inside an isolated `site/` directory managed by `npm` on Node.js `>=24.0.0`, relocating the `13` published tutorial pages from `docs/` into `site/src/content/` as `.mdx` (`@astrojs/mdx`) files with YAML frontmatter and typed Astro components (`<PromptBlock>`, `<PromptGroup>`, `<Callout>`, native `<details>`, and `$$...$$`) and moving the `14` unique tutorial images (rendered across `17` figures) into `site/src/assets/images/`, while keeping repository-level `docs/agents/`, `docs/adr/`, and `docs/research/` in `docs/`.

## Considered Options

- **Astro Starlight (`@astrojs/starlight`):** Rejected because `docsLoader()` locks content to `src/content/docs/`, its built-in asides only support `:::note` directives (zero compatibility with our `30` MkDocs `!!!` admonitions, `13` **Prompt Blocks**, or `1` `??? info` disclosure), and overriding its 3-column shell and `--sl-*` color-ramp tokens adds friction for incorporating custom `ENV / SKEW` faceplate SVG motifs and PCB routing chrome.
- **Frontmatter-free single-source `docs/` ingestion (`glob({ base: '..' })`, mirroring the Companion Site's `ADR 0001`):** Rejected because unlike `EnvelopeFollowerWithSkewLimiter` — whose `20` CommonMark/GFM files are hardware-repo specs, checklists, and patch guides co-located with KiCad/BOM artifacts — this repository's `13` tutorial pages were already authored with MkDocs-specific extensions (`30` `!!!` blocks, `1` `??? info`, `1` `\[...\]` display math block, and `11` `attr_list` image annotations). Relocating them to `site/src/content/*.mdx` with YAML frontmatter eliminates custom MkDocs `remark` parsers, gives **Prompt Blocks** and multi-turn groups type-checked Astro components, and unlocks Astro's native asset optimization via `site/src/assets/images/`.
- **Root-level Astro project or plain `.md` in `site/src/content/`:** Root-level layout was rejected to keep `package.json` and `node_modules/` out of the repository root and maintain 1:1 `site/` structural parity with `reference/site/`. Plain `.md` inside `site/src/content/` was rejected because it would still require custom `remark` plugins for callouts, **Prompt Blocks**, and image attributes.

## Consequences

- `.gitignore` must replace the legacy MkDocs `/site/` output rule with `/site/dist/`, `/site/.astro/`, and `/site/node_modules/` on cutover, and obsolete MkDocs directories (`docs/index.md`, `docs/tutorial/`, `docs/reference/`, `docs/images/`, `docs/stylesheets/`, `docs/javascripts/`, `docs/assets/fonts/`) will be removed once the Astro build takes over.
- Root `README.md` must update its `3` hero `<img>` paths (`docs/images/...` → `site/src/assets/images/...`) and tutorial source links at cutover.
- Only `2` bare angle-bracket strings in existing prose (`<img src>` in Stage 7 and `<env-skew-panel>` in Stage 9 alt text) need escaping during `.mdx` migration.
- Downstream tickets define the Zod YAML frontmatter schema and URL taxonomy (ticket #31), `<PromptBlock>`/`<PromptGroup>`/`<Callout>`/figure component contracts (ticket #33), and `site/` CI/cutover gates (ticket #34).
