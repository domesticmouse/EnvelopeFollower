---
name: tutorial-test-drive
description: >-
  Reset stages/stage-* directories and test-drive the EnvelopeFollower hardware
  tutorial (Stages 1-7) end to end using clean-room subagents prompt by prompt.
  Use when asked to test-drive, validate, or replay the full tutorial cleanly
  from Stage 1 through Stage 7 with a consolidated audit report.
---

# Tutorial Test Drive (`Stages 1–7`)

Replay the **EnvelopeFollower** hardware tutorial from a clean `stages/` directory using isolated subagents, rolling continuously from Stage 1 through Stage 7, stopping only on hard blockers, and printing a full audit report at the end.

- Per-stage inputs, prompts, expected outputs, verification commands, and pitfalls: [`references/stage-gates.md`](./references/stage-gates.md)
- Reset and deterministic gate verification helper: [`scripts/check_stage.py`](./scripts/check_stage.py)

---

## 1. Reset & Pre-Flight Guardrails

Run these steps before launching Stage 1:

1. **Wipe existing stage directories:**
   ```bash
   python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py reset --dry-run
   python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py reset
   ```
   This removes only `stages/stage-[0-9]*` directories and verifies `.venv/` is listed in `.gitignore`.
2. **Verify clean repository root:**
   ```bash
   python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py check-clean-root
   ```
3. **Preserve repository boundaries:**
   - Keep all generated stage outputs inside `stages/stage-1/` … `stages/stage-7/` as regular repository files.
   - Never run `git init` inside `stages/`, never modify `.gitignore` to ignore `stages/`, never modify `docs/tutorial/` during the test-drive run, and never commit changes unless explicitly asked.

---

## 2. Dynamic Prompt Reading & Clean-Room Rules

Always read the live tutorial markdown files under `docs/tutorial/` right before dispatching each stage so every AI prompt and verification command reflects the current repository state.

### Subagent Isolation Rules

Before each stage `N` (`1`–`7`), the orchestrator runs `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage <N>` so `stages/stage-1/` starts empty and each subsequent `stages/stage-N/` starts as a **full copy** of `stages/stage-(N-1)/` (carrying forward `.agents/skills/`, `.venv/`, and all cumulative deliverables):

- **Stage 1 (`tutorial-runner`, `EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`):**
  - Works strictly inside `stages/stage-1/`.
  - Must never modify root `.agents/skills/`, root `skills-lock.json`, or initialize nested `.git` repos.
- **Stages 2–7 (`clean-room-stage-N`, `EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`):**
  - **Allowed READS:** Strictly inside its own `stages/stage-N/` directory (which already contains `.agents/skills/` and all prior stage deliverables) plus `/Applications/KiCad/KiCad.app/Contents/SharedSupport/`.
  - **Allowed WRITES:** Strictly inside its assigned `stages/stage-N/` directory.
  - **FORBIDDEN:** Reading, listing, or modifying any other `stages/stage-<k>/` directory (`k != N`), as well as `docs/`, `prompts/`, `README.md`, `mkdocs.yml`, root `.agents/`, root `EnvelopeFollower.webp`, or running `git` commands.

### Subagent Lifecycle

- Launch a **fresh** `invoke_subagent` for each independent prompt/step so there is no hidden memory bleed across steps.
- Reuse an existing subagent via `send_message` **only** for:
  1. Multi-turn conversational sequences inside the same step (Step `3.3a` → `3.3b` → `3.3c`, Step `5.2` Audit → Fix, or Stage 6 QR fix if needed).
  2. One filename-normalization nudge when a verbatim prompt lacked an output filename and the subagent picked a different name.
  3. Resuming a subagent left waiting after a sandbox-escape approval timeout once the user checks in (do **not** kill the subagent or spawn a replacement; see Section 5).
- Always wait reactively after `invoke_subagent` or `send_message`—never poll in a loop.

---

## 3. Continuous Roll-Forward Workflow (`Stages 1 → 7`)

Execute stages in strict order without pausing between stages for manual approval. Read each stage's `docs/tutorial/stage-*.md` file before running it, pass the verbatim prompt(s), and run the stage gate check from [`references/stage-gates.md`](./references/stage-gates.md) before advancing:

1. **Stage 1 (`docs/tutorial/stage-1-agent-skills.md`):** Run `check_stage.py init-stage 1`; install all 9 hardware skills into `stages/stage-1/.agents/skills/` using the two `npx skills add` commands; verify with `check_stage.py check-stage1` and `check_stage.py check-clean-root`.
2. **Stage 2 (`docs/tutorial/stage-2-circuit-upgrades.md`):** Run `check_stage.py init-stage 2` (cloning `stages/stage-1/` into `stages/stage-2/` so `.agents/skills/` is local to Stage 2); download `EnvelopeFollower.webp` into `stages/stage-2/` (`file` must report valid WebP, not HTML); execute Steps `2.1`, `2.2`, and `2.3` sequentially with fresh subagents producing `EnvelopeFollower.md` and `EnvelopeFollowerImprovements.md`.
3. **Stage 3 (`docs/tutorial/stage-3-bom-and-dfm.md`):** Run `check_stage.py init-stage 3` (cloning the full `stages/stage-2/` directory into `stages/stage-3/`); run Step `3.1` (`EnvelopeFollowerImproved.md` + `EnvelopeFollowerBOM.md` with live JLCPCB/LCSC lookups via `stages/stage-3/.agents/skills/`—zero `PENDING_VERIFY` allowed before Stage 4), Step `3.2` (`EnvelopeFollowerExplanation.md`), and Step `3.3a → 3.3b → 3.3c` (`TP1`–`TP8` `DNP` `RH-5001` + `SilkscreenInstructions.md`).
4. **Stage 4 (`docs/tutorial/stage-4-skidl.md`):** Run `check_stage.py init-stage 4` (cloning the full `stages/stage-3/` directory into `stages/stage-4/`); run the `/skidl` prompt using `stages/stage-4/.agents/skills/skidl/` to create `.venv`, `envelope_follower.py`, `envelope_follower.erc`, `envelope_follower.net`, `envelope_follower_bom.xml`, and `jlcpcb_bom.csv`; verify with `check_stage.py check-stage4`, `ruff`, and `check-clean-root`.
5. **Stage 5 (`docs/tutorial/stage-5-schematic-and-pcb.md`):** Run `check_stage.py init-stage 5` (cloning the full `stages/stage-4/` directory into `stages/stage-5/`); run the Step `5.1` main PCB prompt (`generate_kicad_pcb.py` → `EnvelopeFollower.kicad_pcb`) using `stages/stage-5/.agents/skills/`, verify DRC (`--refill-zones`), `stages/stage-5/.agents/skills/kicad/scripts/analyze_pcb.py`, `stages/stage-5/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py --inspect`, and top/bottom 3D renders; run Step `5.2` Audit (and Fix if discrepancies exist).
6. **Stage 6 (`docs/tutorial/stage-6-front-panel.md`):** Run `check_stage.py init-stage 6` (cloning the full `stages/stage-5/` directory into `stages/stage-6/`); run the `/eurorack-panel` prompt using `stages/stage-6/.agents/skills/` (`panel/EnvelopeFollower_Panel.kicad_pcb`, `production/panel/`, `production/EnvelopeFollower_Panel.zip`), verify DRC, `stages/stage-6/.agents/skills/kicad/scripts/analyze_pcb.py`, `stages/stage-6/.agents/skills/kicad/scripts/analyze_gerbers.py`, and 3D renders (apply the QR fix prompt only if `JLCJLCJLC` appears instead of a `5 × 5 mm` `B.SilkS` square).
7. **Stage 7 (`docs/tutorial/stage-7-manufacturing.md`):** Run `check_stage.py init-stage 7` (cloning the full `stages/stage-6/` directory into `stages/stage-7/`); run the `/kicad` `/jlcpcb` export prompt using `stages/stage-7/.agents/skills/`; verify `check_stage.py check-stage7` and `stages/stage-7/.agents/skills/kicad/scripts/analyze_gerbers.py` on `production/main/`.

---

## 4. Stopping Policy: Hard Blockers vs. Soft Friction

### Hard Blockers (Stop Immediately & Report)

Stop the roll-forward immediately and emit the audit report up to the failure point if any of these occur:

- **Repository contamination:** Root `.agents/skills/`, root `skills-lock.json`, or any earlier completed `stages/stage-<k>/` directory is modified, or a nested `.git` repository is created inside `stages/`.
- **Clean-room breach:** Any subagent reads `docs/`, `prompts/`, root `README.md`, or `mkdocs.yml`.
- **Stage 1 integrity failure:** Missing skills (`<9`), broken/external symlinks inside `stages/stage-1/`, or missing scripts/reference docs.
- **Corrupt reference image:** `stages/stage-2/EnvelopeFollower.webp` fails image validation (e.g., HTML wrapper page).
- **Repeated command/network failure (`2×`):** A required network command (`npx`, `curl`, `jlcpcb_search.py`, `search_lcsc.py`, `uv pip install`), KiCad CLI export, or Python script fails twice (excluding sandbox-escape approval timeouts handled via the async wait policy in Section 5), or SMT parts remain `PENDING_VERIFY` entering Stage 4.
- **Electrical / fabrication failure:** Unrecoverable polarity error (`C4`, diodes, `BAV99` pin numbers, `J_PWR`), Stage 4 `ERC()` non-zero errors/warnings or `NO_LIB > 0`, or Stage 5/6 DRC violations / fatal Gerber errors persisting after one fix pass.

### Soft Friction (Log & Continue)

Record in the audit report and continue rolling forward when:

- A subagent picks a different filename and normalizes cleanly after one `send_message` nudge (log as a tutorial prompt gap).
- A clean-room agent makes valid alternative engineering choices (e.g., `BAV99` vs. `BAT54S`, `1 W 2512` vs. `1/4 W 1206`, `WIMA MKS2` THT `C2`) that remain internally consistent through Stages 3–7.

---

## 5. Sandbox & Tooling Watch-Outs

- **Sandbox rule:** Always try commands with `BypassSandbox: false` first; retry only the single command needing network (`npx`, `curl`, `uv pip install`, `jlcpcb_search.py`, `search_lcsc.py`) or external reads with `BypassSandbox: true` and the identical `toolSummary`.
- **Async sandbox-escape approval timeouts:** Expect the user to monitor long test-drive runs asynchronously. If a subagent fails or stalls due to a sandbox-escape (`BypassSandbox: true`) approval timeout, **do not kill the subagent, spawn a replacement, or immediately abort the run**. Leave that subagent alive in a waiting state, post a short comment in the main conversation noting the stage/step, subagent role and `conversationId`, and the command that timed out, and pause for the user to check in and poke/resume the subagent via `send_message`.
- **Batch JLCPCB lookups:** Consolidate pending parts into a single `jlcpcb_search.py` invocation so the user sees at most one permission prompt per lookup step.
- **Class I pF capacitor queries:** Query short tokens (`"15pF"`, `"47pF"`, `"100pF"`) rather than `"15pF NP0 0603"` (which can return `1 nF` false matches on JLCPCB's endpoint).
- **SKiDL working directory:** Ensure `os.chdir(Path(__file__).resolve().parent)` executes **before** `from skidl import ...` so `.erc` and `.log` files never leak to the repository root.

---

## 6. Consolidated End-of-Run Audit Report Format

At completion (or on a hard blocker), report concisely using clickable `file://` links with these five sections:

1. **Stage-by-Stage Gate Summary:** Markdown table (`Stage 1`–`Stage 7`, status `PASS` / `PASS (with notes)` / `BLOCKED`, key counts/DRC/ERC metrics).
2. **Generated Artifacts Inventory:** Links to `stages/stage-1/` … `stages/stage-7/` and final manufacturing outputs (`EnvelopeFollower.kicad_pcb`, `panel/EnvelopeFollower_Panel.kicad_pcb`, `production/EnvelopeFollower_Main.zip`, `production/EnvelopeFollower_Panel.zip`, `jlcpcb_bom.csv`, `OrderingNotes.md`).
3. **Clean-Room Architectural Divergences:** Concrete differences between the clean-room build and the reference design (part counts, net counts, resistor/diode/capacitor variants, BOM cost).
4. **Tutorial Gaps & Prompt Findings:** Any prompt friction, missing filenames, skill script mismatches, or tooling caveats observed, citing exact `docs/tutorial/` file and line references.
5. **Recommended Next Actions:** Exact fixes (if any) or confirmation that the tutorial ran cleanly end to end.
