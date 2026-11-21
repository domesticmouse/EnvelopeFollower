# `SkillImprovementAuditReport.md` Format & Deduplication Rules

Write `SkillImprovementAuditReport.md` at the repository root using these five top-level sections so [`scripts/verify_skill_audit.py`](../scripts/verify_skill_audit.py) can validate counts, structure, and file citations deterministically.

---

## 1. Required Report Structure

### Header & Executive Summary
- Include **Date**, **Scope** (Stages 1–7 clean-room replay + per-prompt read-only `/agy-customizations` retrospectives), and **Target Skills Audited** (repo names/commits from `stages/stage-7/skills-lock.json`).
- Under `## Executive Summary`, state exact counts matching Section 2 verbatim:
  ```markdown
  Across **<P> prompt retrospectives** (`<A>` yielding concrete findings, `<B>` returning `No Improvements Needed`), clean-room subagents identified **<TOTAL> deduplicated, evidence-backed skill improvements** (`<H> High`, `<M> Medium`, `<L> Low`) without modifying any file under `.agents/skills/` (`diff -rq -x __pycache__ stages/stage-1/.agents/skills stages/stage-7/.agents/skills` verified zero source changes).
  ```
- Summarize 3–5 **Cross-Cutting Themes** observed across stages.

### `## 1. Per-Prompt Coverage Matrix`
Markdown table covering every executed prompt in chronological order:
`Prompt / Step | Subagent Role (conversationId) | Skills Used / Inspected | Verdict | Key Findings Summary`

### `## 2. Consolidated Skill Improvements (Grouped by Skill & Prioritized)`
Deduplicate overlapping findings across prompts and group under upstream source repositories:
- `### A. domesticmouse/skills/packs/hardware` (`kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `skidl`, `eurorack-panel`)
- `### B. aklofas/kicad-happy` (`bom`, `jlcpcb`, `kicad`, `lcsc`, `datasheets`)
- `### C. New Customization Proposals` (or explain why `None Required` under `/agy-customizations` *No Duplication*)

Format every consolidated finding bullet exactly as:
```markdown
- **<PREFIX>-<N> (`<High|Medium|Low>`) — <Concise Title>**
  - **Target File(s):** clickable relative links into `./stages/stage-7/.agents/skills/...`
  - **`/agy-customizations` Principle:** e.g., Executable Helpers (`scripts/`), Progressive Disclosure (`references/`), Validation Steps (`SKILL.md`), Frontmatter `description`, Cross-Skill Consistency
  - **Observed Evidence (`<Stage(s)>`):** exact commands, error strings, line numbers, or measured artifacts
  - **Proposed Change:** concrete, actionable edit
```

### `## 3. Per-Prompt Raw Findings Summary (Traceability Appendix)`
One bullet per executed prompt mapping back to its `<PREFIX>-<N>` IDs in Section 2 (or `No Improvements Needed`).

### `## 4. Prioritized Upstream Action Plan`
Ranked checklist split by upstream repository (`domesticmouse/skills` and `aklofas/kicad-happy`), ordered `High` → `Medium` → `Low`.

---

## 2. Severity Rubric & Verification Rules

- **`High`:** Silent fabrication/BOM/CPL data defect (e.g., fiducial leakage, missing `DNP` parsing, incompatible CPL schema), broken core script path, or workflow forcing repeated unsandboxed prompts.
- **`Medium`:** Misstated fabrication constraint (e.g., `"Top only"` for Economic PCBA), false-positive/false-negative analyzer or keepout check, Python version incompatibility, or undocumented API difference requiring custom workarounds.
- **`Low`:** Documentation clarity, frontmatter trigger narrowing, regex edge case, or optional gate enhancement.

### Mandatory Ground-Truth Rules
1. **Verify every target file path on disk** under `stages/stage-7/.agents/skills/` before writing links — subagents occasionally misremember sibling reference filenames.
2. **Apply `/agy-customizations` *No Duplication*:** Do not invent new skills for general analog electronics theory or prose technical writing where existing tools/domain knowledge suffice.
3. **Never alter evidence counts:** Recompute `<TOTAL>`, `<H>`, `<M>`, and `<L>` directly from the `- **<PREFIX>-<N> (\`<Severity>\`)**` bullets in Section 2 before finishing.
