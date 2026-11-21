# Hardware Skills Improvement Audit Report (`/agy-customizations`)

**Date:** `2026-11-22`  
**Scope:** End-to-end clean-room replay of the **EnvelopeFollower** hardware tutorial ([`docs/tutorial/`](./docs/tutorial/)) across **Stages 1–7**, executing a read-only `/agy-customizations` skill-improvement retrospective immediately after each of the **15 tutorial prompts** completed in its subagent.  
**Target Skills Audited (Zero Modifications Made):**
- [`domesticmouse/skills/packs/hardware`](https://github.com/domesticmouse/skills/tree/main/packs/hardware) (commit `20567628`): `skidl`, `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel`
- [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (commit `6b9767e1`): `kicad`, `bom`, `datasheets`, `jlcpcb`, `lcsc`

---

## Executive Summary

Across **15 prompt retrospectives** (`12` yielding concrete findings, `3` returning `No Improvements Needed`), clean-room subagents identified **25 deduplicated, evidence-backed skill improvements** (`6 High`, `13 Medium`, `6 Low`) without modifying any file under `.agents/skills/` (`diff -rq -x __pycache__ stages/stage-1/.agents/skills stages/stage-7/.agents/skills` verified zero source changes across `228` files).

### Cross-Cutting Themes
1. **Upstream Fixes Verified vs. Remaining Silkscreen & KiCad 10 SWIG Edge Cases:** `domesticmouse/skills` (`20567628`) already resolved several prior gaps (`get_footprint_field()`, `board_edge_bounds()`, `SetExcludedFromPosFiles(True)`, QR keepout checks in `silk_annotator.py --inspect`, and `--severity-all` DRC), enabling Stage 5.1 to pass DRC and `--inspect` on the first run. Remaining friction centered on `place_board_label()` rotating asymmetric `"-"`/`"1"` markers `90°` into `"|"`, `C4` external `+` drifting next to `TP3` (`-12V`), `add_standard_fab_notes()` overflowing `30 mm` `6 HP` boards, `board.Remove()`/`fp.Remove()` triggering `SIGSEGV` (`exit 139`), and `os.execv` breaking under `python3 -c`.
2. **Sourcing & Manufacturing Schema Mismatches Across `aklofas/kicad-happy`:** `search_lcsc.py "RH-5001"` returned an unrelated `0402` fuse (`C206947`) with exit `0`, `provider_lcsc.py` dropped `encapStandard`, batch `jlcpcb_search.py` remained hidden inside `skidl` without links from `jlcpcb`/`lcsc`, `jlcpcb/SKILL.md` still claimed Economic PCBA is `"Top only"` while omitting `kicad-cli`/ZIP/QR steps, and `bom/scripts/translate_bom_pnp.py pnp` dropped `Val`/`Package` and emitted `Layer=B` instead of JLCPCB's 7-column `Layer=Bottom` schema.
3. **Static Analyzer Blind Spots & False Positives:** `kicad/scripts/signal_detectors.py` (`line 3271`) missed KiCad 10's `"+"` op-amp pin names (`TL074`/`TL072`) during unused-channel checking; `reader.py` unconditionally failed `polarity_markers` whenever `len(polarized) > 3`; `copper.py` flagged `17` false `CP-002` notices at THT drill centers on stitched `GND` pours; and `analyze_gerbers.py` `GR-004` flagged `115/290 = 40%` paste coverage instead of comparing against `115` `SMDPad` flashes (`100%`).
4. **Progressive Disclosure & Workspace-Isolated Path Discipline:** `kicad/SKILL.md` (`850` lines / `78.9 KB`) exceeded single-read truncation while omitting pre-KiCad schematic/raster extraction branches and op-amp/potentiometer review patterns, and multiple skill docs/scripts (`kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel`, `skidl`) still wrote temporary verification artifacts to `/tmp/` outside clean-room workspace boundaries.

---

## 1. Per-Prompt Coverage Matrix

| Prompt / Step | Subagent Role (`conversationId`) | Skills Used / Inspected | Verdict | Key Findings Summary |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** (`npx skills add`) | `Stage 1 Skills Installer` (`6ca09dba`) | None executed (inspected all 9 headers) | `No Improvements Needed` | Clean non-interactive install (`9/9` skills, `0` symlinks) |
| **Stage 2 — Step 2.1** (Sketch extraction) | `Stage 2.1 Sketch Extractor` (`c0f76094`) | `kicad` (`pdf-schematic-extraction.md`) | `Improvements Suggested` | Raster schematic extraction + `sips` crop + KCL check; `kicad/SKILL.md` size (`2 Med`) |
| **Stage 2 — Step 2.2** (Analog audit) | `Stage 2.2 Analog Auditor` (`b6aac465`) | `kicad` (all refs), inspected `eurorack-panel` + 7 headers | `Improvements Suggested` | `kicad/SKILL.md` pre-KiCad branch & bloat; op-amp/pot/MLCC patterns (`2 Med`) |
| **Stage 2 — Step 2.3** (Eurorack hardening) | `Stage 2.3 Eurorack Hardening` (`61154eec`) | `kicad`, `skidl`, `eurorack-panel` + 6 headers | `Improvements Suggested` | `signal_detectors.py` misses `"+"` unused pin; `BAV99` pin quirk; `kicad/SKILL.md` size (`1 High, 1 Med, 1 Low`) |
| **Stage 3 — Step 3.1** (JLCPCB BOM) | `Stage 3.1 JLCPCB BOM Researcher` (`8c51d2a6`) | `jlcpcb`, `lcsc`, `bom`, `skidl`, `eurorack-panel`, `datasheets`, `kicad-pcbnew-layout` | `Improvements Suggested` | `jlcpcb_search.py` discovery; `jlcpcb` `"Top only"`; `bom` pre-schematic; `jlcpcb_search.py` empty JSON/`/tmp/`; `RD901F` (`1 High, 2 Med, 2 Low`) |
| **Stage 3 — Step 3.2** (Audio walkthrough) | `Stage 3.2 Circuit Walkthrough Author` (`68819892`) | Inspected all 9 headers (`kicad`, `eurorack-panel`) | `No Improvements Needed` | Educational Markdown synthesis; progressive disclosure cleanly skipped CAD tools |
| **Stage 3 — Step 3.3a** (TP ideas) | `Stage 3.3 Test Points and Silkscreen` (`aa88b772`) | `kicad`, `bom`, `eurorack-panel`, `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `lcsc`, `jlcpcb`, `skidl` | `Improvements Suggested` | `kicad/SKILL.md` truncation; missing `TestPoint:*` `1.0 mm` footprint table (`1 Med, 1 Low`) |
| **Stage 3 — Step 3.3b** (`RH-5001` `DNP` TPs) | `Stage 3.3 Test Points and Silkscreen` (`aa88b772`) | `lcsc`, `skidl`, `bom`, `jlcpcb`, `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel` | `Improvements Suggested` | `search_lcsc.py` false `C206947` fuse hit on `"RH-5001"`; `provider_lcsc.py` drops `encapStandard`; `lcsc` sandbox note (`1 High, 1 Med, 1 Low`) |
| **Stage 3 — Step 3.3c** (`SilkscreenInstructions.md`) | `Stage 3.3 Test Points and Silkscreen` (`aa88b772`) | `kicad-silkscreen-markup`, `kicad`, `kicad-pcbnew-layout`, `jlcpcb`, `eurorack-panel` | `No Improvements Needed` | Updated `silk_annotator.py` & `SKILL.md` (`20567628`) matched `reader.py` fab/silk rules cleanly |
| **Stage 4** (SKiDL & ERC) | `Stage 4 SKiDL Builder` (`0f49ca7d`) | `skidl`, `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel` | `Improvements Suggested` | `BAV99` duplicate-name indexing; `BypassSandbox: true` overstatement & `fp-lib-table`; post-export `.kicad_mod` pad check; `Silkscreen`/`Side` contract; `ruff --no-cache` (`1 High, 3 Med, 1 Low`) |
| **Stage 5 — Step 5.1** (Main PCB build) | `Stage 5.1 PCB Layout Engineer` (`554de6d0`) | `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel`, `kicad` | `Improvements Suggested` | `/tmp/` output paths; `os.execv` `-c` & `str` path bugs; `AC_IN` THT bridge priority; `--analysis-dir` stdout & `CP-002` false positives; `+/-` dual-side offsets (`4 Med, 1 Low`) |
| **Stage 5 — Step 5.2a** (Silkscreen audit) | `Stage 5.2 Silkscreen Auditor` (`612ddbbe`) | `kicad-silkscreen-markup`, `kicad-pcbnew-layout`, `kicad` | `Improvements Suggested` | `place_board_label()` `90°` `"-"`/`"1"` rotation; polarity tether/wrong-net (`C4` `+` near `TP3`) & visual checklist; `add_standard_fab_notes()` width overflow (`2 High, 1 Med`) |
| **Stage 5 — Step 5.2b** (Silkscreen fixes) | `Stage 5.2 Silkscreen Auditor` (`612ddbbe`) | `kicad-silkscreen-markup`, `kicad-pcbnew-layout`, `kicad`, `eurorack-panel` | `Improvements Suggested` | `board.Remove()`/`fp.Remove()` SWIG `SIGSEGV` (`exit 139`); multi-pass corridor ordering & `SilkGrid.explain_block()` (`2 Med`) |
| **Stage 6** (3U Front Panel) | `Stage 6 Front Panel Builder` (`f37a9b8d`) | `eurorack-panel`, `kicad` | `Improvements Suggested` | `/tmp/` verification & DRC paths; `RD901F` `(+7.5, +2.5)` vs `RK09K` `(-7.0)` offset; `capability_mode.json` sidecar dir (`1 Med, 2 Low`) |
| **Stage 7** (Manufacturing & CPL) | `Stage 7 Manufacturing Exporter` (`bc2b9009`) | `kicad`, `jlcpcb`, `bom`, `eurorack-panel`, `kicad-silkscreen-markup`, `kicad-pcbnew-layout` | `Improvements Suggested` | `translate_bom_pnp.py` drops `Val`/`Package` & emits `Layer=B`; `jlcpcb` `"Top only"`/CLI/ZIP/QR gaps; `analyze_gerbers.py` `GR-004` false positive; `/tmp/` paths (`1 High, 2 Med, 1 Low`) |

---

## 2. Consolidated Skill Improvements (Grouped by Skill & Prioritized)

### A. `domesticmouse/skills/packs/hardware`

#### 1. `kicad-pcbnew-layout`

- **KPL-1 (`Medium`) — Undocumented `board.Remove()`/`fp.Remove()` SWIG `SIGSEGV` (`exit 139`) and `os.execv` `-c` / `str` Path Bugs**
  - **Target File(s):** [`kicad10_pcbnew_api.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/references/kicad10_pcbnew_api.md#L16-L26), [`pcbnew_layout_template.py`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/scripts/pcbnew_layout_template.py#L18-L95), [`silk_annotator.py`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L18-L23)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Progressive Disclosure (`references/`)
  - **Observed Evidence (`Stages 5.1, 5.2b`):** Calling `board.Remove(dr)` / `fp.Remove(gi)` on `PCB_TEXT`/`PCB_SHAPE` drawings in KiCad 10 SWIG Python crashed with `exit code 139` (`SIGSEGV` + `swig/python detected a memory leak`); running `python3 -c '... import pcbnew_layout_template ...'` exited `2` (`Argument expected for the -c option`) because `sys.argv == ['-c']` breaks `os.execv`; and `parse_netlist("envelope_follower.net")` raised `AttributeError: 'str' object has no attribute 'read_text'` at line 95.
  - **Proposed Change:** Document `board.Delete()`/`fp.Delete()` (vs. crashing `Remove()`) and the `python3 -c` caveat in `kicad10_pcbnew_api.md`; fail fast in `pcbnew_layout_template.py` and `silk_annotator.py` when `sys.argv[0] == "-c"`; and coerce `net_path = pathlib.Path(net_path)` inside `parse_netlist()`.

- **KPL-2 (`Medium`) — `/tmp/` Verification Output Paths and Unclear `--output` vs. `--analysis-dir` Semantics**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/SKILL.md#L56-L70)
  - **`/agy-customizations` Principle:** Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stages 5.1, 5.2b`):** While line 70 instructs rendering into workspace-local paths (`analysis/`), lines 56, 65, and 68 still write `--output /tmp/drc.json`, `/tmp/pcb_analysis.json`, and `/tmp/cpl_check.csv`, and Step 5.1/5.2b surfaced confusion because `--analysis-dir analysis/` suppresses stdout and writes timestamped `analysis/YYYY-MM-DD_HHMM/pcb.json` without updating a flat `analysis/pcb_analysis.json`.
  - **Proposed Change:** Replace `/tmp/*` targets with `analysis/drc.json`, `analysis/pcb_analysis.json`, and `analysis/cpl_check.csv`, and note explicitly when to use flat `--output` vs. timestamped `--analysis-dir`.

- **KPL-3 (`Low`) — Trapped THT Bridge-Net Priority (`tier = -1`) and BFS Pocket Diagnostics**
  - **Target File(s):** [`routing_and_dfm_patterns.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/references/routing_and_dfm_patterns.md#L27-L35)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`)
  - **Observed Evidence (`Stage 5.1`):** Net `AC_IN` (`R1.1`, `R27.1`, `C1.2`) failed routing (`targets=2 sample=[(0, 81, 191), (1, 81, 191)]`) because a 2-layer BFS probe showed THT pad `C1.2` got sealed inside a `3,072`-cell copper island by earlier perimeter buses; adding `"AC_IN"` to `tier = -1` resolved routing (`unconnected=0`).
  - **Proposed Change:** Add a note under `routing_and_dfm_patterns.md` §2 rule 7 noting mid-board THT bridge nets next to dense SMD intersections may need `tier = -1`, plus a brief 2-layer BFS pocket check from failed `targets`.

#### 2. `kicad-silkscreen-markup`

- **KSM-1 (`High`) — Asymmetric Polarity Glyphs (`"-"`, `"1"`) Rotated `90°`, Polarity Tether/Wrong-Net Blind Spots, and Missing Visual Checklist**
  - **Target File(s):** [`silk_annotator.py`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L584), [`silk_annotator.py` (`inspect_board_silk`)](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L1460), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/SKILL.md#L51-L71)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stage 5.2a`):** `place_board_label()` defaults to `rotations=(0.0, 90.0)` while KiCad measures `"-"` as `1.28 × 1.46 mm`, causing `C3` `"-"`, `D4` `B.SilkS` `"-"`, and `RV4` `B.SilkS` `"1"` to fall back to `rot=90.0°` (rendering `"-"` as vertical `"|"`). Simultaneously, `C4` external `"+"` drifted `4.76 mm` away from `C4.1` to `(1.80, 97.75)` — `0.30 mm` from `TP3`'s (`-12V`) keepout — and `D4` lacked a `B.SilkS` cathode bar, yet `silk_annotator.py --inspect` returned `RESULT: PASS`.
  - **Proposed Change:** Default upright polarity marks (`"-"`, `"1"`) to `rotations=(0.0,)` (or add `place_polarity_label()`); extend `inspect_board_silk()` to flag `90°` `"-"` tokens and `+`/`-` markers closer to an unrelated `TP*`/header pad than their target polarized pad; and add an upright-glyph / wrong-net proximity checklist for `top.png`/`bottom.png` in `SKILL.md`.

- **KSM-2 (`Medium`) — `add_standard_fab_notes()` Width (`32–38 mm`) Overflows `6 HP` (`30 mm`) Eurorack Boards**
  - **Target File(s):** [`silk_annotator.py`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L1255), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/SKILL.md#L55-L57)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & `SKILL.md` Consistency
  - **Observed Evidence (`Stage 5.2a`):** `add_standard_fab_notes()` hardcodes lines measuring `32.05 mm` and `37.53 mm` via `SilkGrid.measure_text(..., 0.80, 0.15)`, overflowing the `30.00 mm` `6 HP` board width and forcing `generate_kicad_pcb.py` to emit custom 6-line fab notes that initially omitted `DRILL TOL: +/-0.08mm | NO EDGE CUT`.
  - **Proposed Change:** Add an optional `max_width: float | None = None` wrapping parameter (auto-reading `board_edge_bounds(board)`) to `add_standard_fab_notes()` so narrow boards wrap pipe-separated clauses without dropping lines or overflowing `Edge.Cuts`.

- **KSM-3 (`Medium`) — Multi-Pass Polarity Ordering, Opaque `None` Failures (`explain_block()`), and Multi-Side `+/-` Offsets**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/SKILL.md#L51), [`silk_annotator.py`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L584)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Workflow Ordering (`SKILL.md`)
  - **Observed Evidence (`Stages 5.1, 5.2b`):** Placing `D4` `B.SilkS` `+`/`-` before passive/opposite-side passes broke `opp_label D4 ('D4 ENV') side=1` (`task-106`), placing `C3` `"-"` before `J3` broke `opp_label J3 ('J3 INV_OUT') side=1` (`task-86`), and single-target `-Y` placement missed the open `+Y` slot under `D4.2`. Because `place_*` helpers return `None` with no obstacle diagnostics, each collision required ad-hoc probing scripts.
  - **Proposed Change:** Document the dense dual-sided placement order in `SKILL.md` §6 (primary polarities -> SMD + opposite-side THT labels -> corridor-sharing secondary polarity marks probing both `-Y`/`+Y`), add `SilkGrid.explain_block(side, box)` diagnostics, and add a rotation-agnostic `place_pad_polarity_mark()` helper in `silk_annotator.py`.

- **KSM-4 (`Low`) — Replace `/tmp/` Verification Paths in `kicad-silkscreen-markup/SKILL.md`**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/SKILL.md#L65-L68)
  - **`/agy-customizations` Principle:** Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stages 5.1, 7`):** Lines 65 and 68 instruct `--output /tmp/drc.json` and `--output /tmp/pcb_analysis.json`, violating workspace isolation in clean-room runs.
  - **Proposed Change:** Update both commands to `mkdir -p analysis` with `analysis/drc.json` and `analysis/pcb_analysis.json`.

#### 3. `skidl`

- **SKD-1 (`High`) — Duplicate-Name Pin Indexing Hazard (`Diode:BAV99` `1="K", 2="A", 3="K"`)**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/skidl/SKILL.md#L103-L108), [`advanced_patterns.md`](./stages/stage-7/.agents/skills/skidl/references/advanced_patterns.md)
  - **`/agy-customizations` Principle:** `SKILL.md` Pitfall Callout & Progressive Disclosure (`references/`)
  - **Observed Evidence (`Stages 2.3, 4`):** KiCad 10's `Diode:BAV99` symbol labels both Pin `1` and Pin `3` `"K"` and Pin `2` `"A"`, whereas physical `SOT-23` `BAV99,215` is `1=A1 (-12V)`, `2=K2 (+12V)`, `3=COM`. Indexing `d["K"]` via Section 4's default name-indexing pattern selects pins `1` and `3` together and shorts `-12V` to signal `COM`.
  - **Proposed Change:** Warn in `skidl/SKILL.md` §4 (`Pin Indexing`) and `advanced_patterns.md` to verify pin-name uniqueness via `show()` and always address dual/series diodes (`BAV99`, `BAT54S`) by numeric pad index (`part.p[1]`, `part.p[2]`, `part.p[3]`).

- **SKD-2 (`Medium`) — Overstated `BypassSandbox: true` Rule, Missing `fp-lib-table` Context & Post-Export `.kicad_mod` Pad Validation**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/skidl/SKILL.md#L42), [`SKILL.md` (Validation & Ruff)](./stages/stage-7/.agents/skills/skidl/SKILL.md#L183-L195)
  - **`/agy-customizations` Principle:** Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stage 4`):** `SKILL.md` line 42 tells macOS users *"Always execute the SKiDL script outside the sandbox (`BypassSandbox: true`)"*, yet `.venv/bin/python envelope_follower.py` ran cleanly inside the sandbox (`0` `NO_LIB`). Meanwhile, SKiDL emitted `5× WARNING: fp-lib-table file was not found` even with `KICAD10_FOOTPRINT_DIR` set—meaning SKiDL never validates footprint names or pin-to-pad numbers against `.kicad_mod` files—and Section 7 omits `--no-cache` / `--check` verification after regenerating `*_sklib.py`.
  - **Proposed Change:** Instruct running sandboxed first (`BypassSandbox: true` only on `Can't open file` / `NO_LIB`), clarify `fp-lib-table` warnings, add a netlist-vs-`.kicad_mod` pad check + `pcbnew_layout_template.py --netlist` to Section 6, and append `ruff check --no-cache` / `ruff format --check` to Section 7.

- **SKD-3 (`Medium`) — Missing `Silkscreen` / `Side` Cross-Skill Contract, Consigned THT Handling, and `TestPoint:*` Footprint Reference**
  - **Target File(s):** [`jlcpcb_bom.md`](./stages/stage-7/.agents/skills/skidl/references/jlcpcb_bom.md#L19-L90)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`) & Cross-Skill Contract
  - **Observed Evidence (`Stages 3.3a, 4`):** `jlcpcb_bom.md` omits `part.fields["Silkscreen"]` (including single-token passive values like `"1k_1W"` so `compact_passive_value()` keeps `1W`), `Side`, consigned THT tagging (`JLCPCB_Class="Manual THT"` with no `"PENDING"` placeholder), and standard `1.0 mm`-drill `TestPoint:*` footprint names (causing `TestPoint.pretty/*.kicad_mod` read timeouts in Stage 3.3a).
  - **Proposed Change:** Document `Silkscreen`/`Side` fields, consigned THT metadata rules, and a `TestPoint` table row (`TestPoint_THTPad_D2.0mm_Drill1.0mm` / `TestPoint_Keystone_5000-5004_Miniature` vs. `0.7 mm` `D1.5mm`) in `jlcpcb_bom.md`.

- **SKD-4 (`Low`) — `jlcpcb_search.py` Empty `-o` Output, DNS Retry Delay, and `/tmp/` Doc Paths**
  - **Target File(s):** [`jlcpcb_search.py`](./stages/stage-7/.agents/skills/skidl/scripts/jlcpcb_search.py#L188-L226), [`SKILL.md`](./stages/stage-7/.agents/skills/skidl/SKILL.md#L180), [`jlcpcb_bom.md`](./stages/stage-7/.agents/skills/skidl/references/jlcpcb_bom.md#L41)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Workspace Isolation
  - **Observed Evidence (`Stage 3.1`):** When sandboxed (`BypassSandbox: false`), `jlcpcb_search.py` slept `0.25 s` across all `33` DNS-failed queries (~`8.25 s`) and wrote `[]`-filled `jlc_batch1.json`/`jlc_batch2.json` before exiting `1`; docs also example `-o /tmp/...`.
  - **Proposed Change:** Skip writing `-o` when `failed == len(args.keywords)`, fail fast on repeated `URLError` DNS errors, and replace `/tmp/...` examples with workspace-local `.cache/` paths.

#### 4. `eurorack-panel`

- **ERP-1 (`Medium`) — Hardcoded `/tmp/` Output Paths in `eurorack-panel/SKILL.md` and `generate_eurorack_panel.py::run_drc_check()`**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/eurorack-panel/SKILL.md#L66-L70), [`generate_eurorack_panel.py`](./stages/stage-7/.agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py#L997)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stages 5.1, 6, 7`):** `eurorack-panel/SKILL.md` line 70 warns against `/tmp/` yet lines 66–67 pass `--output /tmp/panel_pcb.json` and `/tmp/panel_gerbers.json`, and `generate_eurorack_panel.py` line 997 hardcodes `drc_json = pathlib.Path("/tmp") / f"{pcb_path.stem}_drc.json"`.
  - **Proposed Change:** Update `SKILL.md` lines 66–67 to `analysis/panel_pcb.json` and `analysis/panel_gerbers.json`, and use a `tempfile.TemporaryDirectory()` (or optional `--drc-output`) inside `run_drc_check()`.

- **ERP-2 (`Low`) — `Alpha RD901F` Potentiometer Shaft Offset (`(+7.50, +2.50)` / `(+2.50, -7.50)`) Omitted & Aliased to `RK09K` `(-7.00)`**
  - **Target File(s):** [`eurorack_mechanical_spec.md`](./stages/stage-7/.agents/skills/eurorack-panel/references/eurorack_mechanical_spec.md#L40), [`generate_eurorack_panel.py`](./stages/stage-7/.agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py#L72-L77)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`) & Script Fallback Accuracy (`scripts/`)
  - **Observed Evidence (`Stages 3.1, 6`):** KiCad 10's `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` places `fp_circle` at `(7.5, 2.5)` (`(+2.50, -7.50)` at `90°`), whereas `eurorack_mechanical_spec.md` line 40 only lists `Alps RK09K` (`(+2.50, -7.00)`) and `PANEL_COMPONENT_SPECS` lines 72–77 alias `RD901F` onto `RK09K`'s `(2.5, -7.0)` fallback (`0.50 mm` Y error if `fp_circle` were missing).
  - **Proposed Change:** Add a dedicated `Alpha RD901F-40-00D` row in `eurorack_mechanical_spec.md` and give `RD901F` its own `PANEL_COMPONENT_SPECS` entry with `(7.5, 2.5)`.

---

### B. `aklofas/kicad-happy`

#### 1. `bom`

- **BOM-1 (`High`) — `translate_bom_pnp.py` Drops `Val`/`Package` and Emits `Layer=B` Instead of JLCPCB's 7-Column `Layer=Bottom` Schema**
  - **Target File(s):** [`translate_bom_pnp.py`](./stages/stage-7/.agents/skills/bom/scripts/translate_bom_pnp.py#L270-L294), [`translate_bom_pnp.py` (`translate_pnp`)](./stages/stage-7/.agents/skills/bom/scripts/translate_bom_pnp.py#L680-L697), [`ordering-and-fabrication.md`](./stages/stage-7/.agents/skills/bom/references/ordering-and-fabrication.md#L106-L120)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Reference Consistency (`references/`)
  - **Observed Evidence (`Stage 7`):** While `ordering-and-fabrication.md` lines 110–116 specify `Layer` as `Top` or `Bottom` and link to `translate_bom_pnp.py pnp`, `_normalize_layer()` maps `bottom` -> `'B'` (lines 289–292) and `translate_pnp()` strips `Val`/`Package` to output a 5-column header `["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]` (line 697), forcing a custom Python script to generate JLCPCB's `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` (`Layer=Bottom`) CSV.
  - **Proposed Change:** Support preserving `Val`/`Package` and emitting `Top`/`Bottom` in `translate_bom_pnp.py pnp` (matching `ordering-and-fabrication.md`), add `--strict-bom` 1:1 parity checking, and document `kicad-cli pcb export pos --side <front|back> --smd-only --exclude-dnp --units mm` (warning against `--bottom-negate-x`).

- **BOM-2 (`Medium`) — Missing Pre-Schematic / Spec-Stage BOM Shortcut in `bom/SKILL.md`**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/bom/SKILL.md#L2-L8)
  - **`/agy-customizations` Principle:** Workflow Routing (`SKILL.md`)
  - **Observed Evidence (`Stage 3.1`):** `bom/SKILL.md` triggers unconditionally on *"generate JLCPCB BOM"* and component sourcing, yet all Steps 1–11 assume an existing `.kicad_sch` (`bom_manager.py`, `edit_properties.py`), leaving pre-schematic Markdown BOM planning (`EnvelopeFollowerBOM.md`) unsupported.
  - **Proposed Change:** Add a concise **"Pre-Schematic / Spec-Stage BOM"** branch routing to `jlcpcb_search.py` / `search_lcsc.py` and the 3-bucket SMT / Manual THT / Consigned-DNP layout.

#### 2. `jlcpcb`

- **JLC-1 (`High`) — Live Batch `jlcpcb_search.py` Is Hidden Inside `skidl` Without Cross-Links from `jlcpcb` or `lcsc`**
  - **Target File(s):** [`jlcpcb/SKILL.md`](./stages/stage-7/.agents/skills/jlcpcb/SKILL.md#L34-L55), [`lcsc/SKILL.md`](./stages/stage-7/.agents/skills/lcsc/SKILL.md#L36-L68)
  - **`/agy-customizations` Principle:** Executable Helper Discovery (`SKILL.md`)
  - **Observed Evidence (`Stage 3.1`):** Searching live JLCPCB assembly stock and Basic/Extended status across 33 BOM parts required `.agents/skills/skidl/scripts/jlcpcb_search.py`, yet neither `jlcpcb/SKILL.md` nor `lcsc/SKILL.md` mentions or links to `jlcpcb_search.py`.
  - **Proposed Change:** Cross-link `skidl/scripts/jlcpcb_search.py` (for multi-part live JLCPCB stock/tier batching) vs. `lcsc/scripts/search_lcsc.py` (for single-part parametric/price-break detail) in both `jlcpcb/SKILL.md` and `lcsc/SKILL.md`.

- **JLC-2 (`Medium`) — `jlcpcb/SKILL.md` Misstates Economic PCBA as `"Top only"` and Omits Headless CLI Export, ZIP Hygiene & QR Placement**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/jlcpcb/SKILL.md#L114-L167)
  - **`/agy-customizations` Principle:** `SKILL.md` Technical Accuracy & Validation Steps
  - **Observed Evidence (`Stages 3.1, 7`):** Line 116 says `| Sides | Top only | Top + Bottom |`, contradicting JLCPCB Economic single-sided **Bottom (`B.Cu`)** PCBA used throughout Stages 3–7; lines 158–167 omit headless `kicad-cli` Gerber/drill/pos commands, excluding `_cpl.csv` from Gerber ZIPs, and `"Specify a location"` instructions for `5 × 5 mm` `B.SilkS` QR placeholders.
  - **Proposed Change:** Update line 116 to `Single-sided (Top or Bottom)` and add concise headless export, ZIP-exclusion, and QR-location subsections (cross-linking `bom/references/ordering-and-fabrication.md`).

#### 3. `lcsc`

- **LCS-1 (`High`) — `search_lcsc.py` Returns False Substring Match (`C206947` Fuse) for MPNs Missing from `jlcsearch` (`"RH-5001"`)**
  - **Target File(s):** [`search_lcsc.py`](./stages/stage-7/.agents/skills/lcsc/scripts/search_lcsc.py#L296-L366), [`SKILL.md`](./stages/stage-7/.agents/skills/lcsc/SKILL.md#L36-L68)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Steps
  - **Observed Evidence (`Stage 3.3b`):** Running `search_lcsc.py "RH-5001" --details --json` exited `0` (`count: 1`) and returned **`C206947` (`0435001.KRHF`, Littelfuse `0402` fuse)** instead of Ronghe `RH-5001` (`C5199801`), because lines 299–328 only invoke direct LCSC lookup on `^C\d+$` queries with empty `jlcsearch` results.
  - **Proposed Change:** When a hyphenated/single-token MPN query yields zero exact/prefix `mpn` matches on `jlcsearch`, fall back to JLCPCB keyword search or emit an explicit `"exact_mpn_match": false` / stderr mismatch warning; note this `jlcsearch` caveat in `lcsc/SKILL.md`.

- **LCS-2 (`Medium`) — `provider_lcsc.search_lcsc_direct()` Drops `encapStandard` (`package`) and Conflates LCSC vs. JLCPCB Stock/Class**
  - **Target File(s):** [`provider_lcsc.py`](./stages/stage-7/.agents/skills/lcsc/scripts/provider_lcsc.py#L135-L195), [`search_lcsc.py`](./stages/stage-7/.agents/skills/lcsc/scripts/search_lcsc.py#L118-L161), [`SKILL.md`](./stages/stage-7/.agents/skills/lcsc/SKILL.md#L136)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) Bug Fix
  - **Observed Evidence (`Stage 3.3b`):** Although `lcsc/SKILL.md` line 136 documents `encapStandard` (`package`), `provider_lcsc.py` never reads `encapStandard`, forcing `"package": "-"` on `search_lcsc.py "C5199801" --details --json`, while marking direct `wmsc` hits `"is_basic": false` (`"Extended ($3 feeder fee on JLCPCB)"`) using LCSC warehouse `stockNumber`.
  - **Proposed Change:** Extract `_text(result.get("encapStandard"))` in `search_lcsc_direct()` and emit `"stock_source"` (`"jlcsearch"` vs. `"lcsc_wmsc"`) and `"jlcpcb_type_known"` in JSON output.

- **LCS-3 (`Low`) — Missing Sandbox Network Caveat in `lcsc/SKILL.md`**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/lcsc/SKILL.md#L36-L68)
  - **`/agy-customizations` Principle:** Executable Helper Invocation Guidance (`SKILL.md`)
  - **Observed Evidence (`Stage 3.3b`):** Sandboxed `search_lcsc.py` calls fail with DNS `URLError` without hinting at `BypassSandbox: true`, unlike `skidl` and `eurorack-panel`.
  - **Proposed Change:** Add a brief note under `Component Search` / `Datasheet Download & Sync` noting `BypassSandbox: true` is needed when sandbox network access is blocked.

#### 4. `kicad`

- **KIC-1 (`High`) — Unused Op-Amp Detector (`signal_detectors.py`) Misses Standard KiCad `"+"` Pin Names (`TL074`/`TL072`) and Invalid Dual-`GND` Tie**
  - **Target File(s):** [`signal_detectors.py` (`detect_unused_opamps`)](./stages/stage-7/.agents/skills/kicad/scripts/signal_detectors.py#L3266-L3283), [`signal_detectors.py` (`detect_opamp_circuits`)](./stages/stage-7/.agents/skills/kicad/scripts/signal_detectors.py#L2950-L2954)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Accuracy
  - **Observed Evidence (`Stage 2.3`):** KiCad 10's `TL074`/`TL072` symbols name inputs `"+"` and `"-"`. While line 2951 checks `pn in ("+", "+IN", ...)`, line 3271 checks only `any(k in pname for k in ("+IN", "INP", "IN+", "NON_INV"))`, silently missing floating `TL074`/`TL072` channels and failing to flag invalid open-loop `pos_net == neg_net` ties (without `neg_net == out_net`).
  - **Proposed Change:** Share the normalized pin-name check (`pname == "+"`) at line 3271 and validate inverting (`"-"`) and output pin connectivity (`neg_net == out_net` or biased feedback) on unused sections.

- **KIC-2 (`Medium`) — `kicad/SKILL.md` Size (`850` Lines / `78.9 KB`), Pre-KiCad Review Branch, and Undocumented `--analysis-dir` / `capability_mode.json` Behavior**
  - **Target File(s):** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md#L42-L99), [`SKILL.md` (CLI/Output)](./stages/stage-7/.agents/skills/kicad/SKILL.md#L188-L306)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`docs/skills.md` Best Practice #1) & Tool Usage Clarity
  - **Observed Evidence (`Stages 2.1, 2.2, 2.3, 3.3a, 5.1, 6`):** Reading `kicad/SKILL.md` truncated at `800/850` lines (`46,080/78,983` bytes) because JSON schemas and CLI matrices are inlined alongside `references/output-schema.md`; Design Review Contract lacks a lightweight branch for pre-KiCad Markdown/image specs; `--analysis-dir` suppresses stdout (`analyze_pcb.py` lines 157–167) contrary to line 264; and `--output <dir>/file.json` without `--analysis-dir` drops `capability_mode.json` into `<dir>/`.
  - **Proposed Change:** Trim `kicad/SKILL.md` to ~250–300 lines of routing + links to `references/`, add a Pre-KiCad review branch, and document exact `--analysis-dir` stdout suppression and `capability_mode.json` placement.

- **KIC-3 (`Medium`) — `analyze_gerbers.py` `GR-004` False Positive & `analyze_pcb.py` `CP-002` THT Drill-Center False Positive**
  - **Target File(s):** [`analyze_gerbers.py`](./stages/stage-7/.agents/skills/kicad/scripts/analyze_gerbers.py#L2117-L2150), [`copper.py`](./stages/stage-7/.agents/skills/kicad/scripts/pcb/copper.py#L1098-L1110)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) False-Positive Reduction
  - **Observed Evidence (`Stages 5.1, 7`):** `analyze_gerbers.py` emitted `WARNING GR-004: B paste layer: 115 flashes vs 290 copper (40%)` on `production/main/` even though `115/115` `SMDPad` apertures were pasted (`290` included `53` THT `ComponentPad` + `119` `ViaPad` + `3` `FiducialPad`), and `copper.py` line 1103 emitted `17` `CP-002` warnings (`No opposite-layer copper`) by sampling `zones_at_point(px, py)` at exact THT drill centers on a 2-layer ground-poured board.
  - **Proposed Change:** Compute `GR-004` denominators from `SMDPad + HeatsinkPad` when X2 `by_function_flashes` exists, and skip or offset-sample `thru_hole` pads in `copper.py::analyze_copper_presence()`.

- **KIC-4 (`Medium`) — Missing Op-Amp/Potentiometer/Analog Patterns and Raster Schematic Image Extraction Guidance**
  - **Target File(s):** [`schematic-analysis.md`](./stages/stage-7/.agents/skills/kicad/references/schematic-analysis.md#L563), [`deep-review.md`](./stages/stage-7/.agents/skills/kicad/references/deep-review.md#L47-L52), [`pdf-schematic-extraction.md`](./stages/stage-7/.agents/skills/kicad/references/pdf-schematic-extraction.md#L1-L49), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md#L1-L17)
  - **`/agy-customizations` Principle:** Frontmatter `description` & Progressive Disclosure (`references/`)
  - **Observed Evidence (`Stages 2.1, 2.2, 2.3`):** `kicad/SKILL.md` and `pdf-schematic-extraction.md` assume `.kicad_sch`/vector PDFs (omitting `.webp`/`.png`/`.jpg` sketches, macOS `sips --cropOffset 1 1 -c` ordering when `PIL` is missing, and KCL polarity sanity checks after `D2` was initially misread in `EnvelopeFollower.webp`), while `schematic-analysis.md` and `deep-review.md` lack analog op-amp/potentiometer patterns (rheostat pin direction/taper, pot `R_th` loading, peak-detector surge & diode deadband, `TL07x` phase reversal, X7R MLCC DC-bias derating, and KiCad `BAV99` `1="K", 2="A", 3="K"`).
  - **Proposed Change:** Broaden `kicad/SKILL.md` frontmatter to raster schematic images, add a raster-image/cropping/`sips`/KCL sanity subsection in `pdf-schematic-extraction.md`, and add an Analog Op-Amp/Potentiometer/MLCC + `BAV99` subsection to `schematic-analysis.md` / `deep-review.md`.

- **KIC-5 (`Low`) — `reader.py` `polarity_markers` Unconditionally Fails When `len(polarized) > 3` Regardless of Silkscreen Markings**
  - **Target File(s):** [`reader.py`](./stages/stage-7/.agents/skills/kicad/scripts/pcb/reader.py#L1948-L2010)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) Consistency
  - **Observed Evidence (`Stages 5.1, 5.2b`):** After fixing every polarity item and passing `silk_annotator.py --inspect` (`RESULT: PASS`) and `--severity-all` DRC (`0` violations), `analyze_pcb.py` still failed `silkscreen_completeness.checks.polarity_markers = false` because `reader.py` lines 1950–1957 and 2007–2009 unconditionally append `polarity_reminder` whenever `len(polarized) > 3` without inspecting silkscreen `gr_circle`/`gr_line`/`gr_text` markers.
  - **Proposed Change:** Check nearby silkscreen shapes/texts (`<= 2.5 mm`) on polarized components (`D*`, `U*`, polarized `C*`, `LED*`) before failing `polarity_markers`, separating informational reminders from completeness checks.

### C. New Customization Proposals

- **None Required (`/agy-customizations` *No Duplication* Principle):** Per [`docs/skills.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md) and `/agy-customizations`, Step 2.2 (analog engineering critique) and Step 3.2 (educational audio walkthrough) needed zero new domain skills, and all `25` concrete tool/doc gaps belong inside the existing 9 skills above rather than duplicating rules or wrappers.

---

## 3. Per-Prompt Raw Findings Summary (Traceability Appendix)

- **Stage 1 (`6ca09dba`):** `No Improvements Needed` (`9/9` skills copied cleanly with `0` symlinks).
- **Stage 2 — Step 2.1 (`c0f76094`):** Raster image extraction, `sips` flag order, KCL diode check, and `kicad/SKILL.md` bloat → **KIC-4**, **KIC-2**.
- **Stage 2 — Step 2.2 (`b6aac465`):** Pre-KiCad schematic branch, `kicad/SKILL.md` size, and op-amp/pot/MLCC patterns → **KIC-2**, **KIC-4**.
- **Stage 2 — Step 2.3 (`61154eec`):** `signal_detectors.py` `"+"` unused op-amp bug, `BAV99` pin quirk, and `kicad/SKILL.md` size → **KIC-1**, **SKD-1**, **KIC-4**, **KIC-2**.
- **Stage 3 — Step 3.1 (`8c51d2a6`):** `jlcpcb_search.py` discoverability, `jlcpcb` `"Top only"`, `bom` pre-schematic branch, `jlcpcb_search.py` empty JSON/`/tmp/`, and `RD901F` spec → **JLC-1**, **JLC-2**, **BOM-2**, **SKD-4**, **ERP-2**.
- **Stage 3 — Step 3.2 (`68819892`):** `No Improvements Needed`.
- **Stage 3 — Step 3.3a (`aa88b772`):** `kicad/SKILL.md` truncation and `TestPoint:*` footprint table → **KIC-2**, **SKD-3**, **KPL-3**.
- **Stage 3 — Step 3.3b (`aa88b772`):** `search_lcsc.py` false `C206947` match on `"RH-5001"`, `provider_lcsc.py` `encapStandard` omission, and `lcsc` sandbox caveat → **LCS-1**, **LCS-2**, **LCS-3**.
- **Stage 3 — Step 3.3c (`aa88b772`):** `No Improvements Needed`.
- **Stage 4 (`0f49ca7d`):** Overstated `BypassSandbox: true` & `fp-lib-table`, `.kicad_mod` pad check, `BAV99` pin indexing, `Silkscreen`/`Side` contract, and `ruff --no-cache` → **SKD-1**, **SKD-2**, **SKD-3**.
- **Stage 5 — Step 5.1 (`554de6d0`):** `/tmp/` verification outputs, `os.execv` `-c` & `str` path bugs, `AC_IN` THT bridge priority, `--analysis-dir` stdout & `CP-002` false positives, and `D4` `+/-` dual-side offsets → **KPL-2**, **KSM-4**, **ERP-1**, **KPL-1**, **KPL-3**, **KIC-2**, **KIC-3**, **KSM-3**.
- **Stage 5 — Step 5.2a (`612ddbbe`):** `place_board_label()` `90°` `"-"`/`"1"` rotation, polarity tether/wrong-net (`C4` `+` near `TP3`) & visual checklist, and `add_standard_fab_notes()` `30 mm` overflow → **KSM-1**, **KSM-2**.
- **Stage 5 — Step 5.2b (`612ddbbe`):** `board.Remove()`/`fp.Remove()` `SIGSEGV`, multi-pass ordering & `SilkGrid.explain_block()`, `--output` vs. `--analysis-dir`, and `polarity_markers` false warning → **KPL-1**, **KSM-3**, **KPL-2**, **KIC-5**.
- **Stage 6 (`f37a9b8d`):** `/tmp/` verification & DRC paths, `RD901F` vs. `RK09K` fallback offset, and `capability_mode.json` sidecar dir → **ERP-1**, **ERP-2**, **KIC-2**.
- **Stage 7 (`bc2b9009`):** `translate_bom_pnp.py` 7-column `Layer=Bottom` mismatch, `jlcpcb` `"Top only"`/CLI/ZIP/QR gaps, `GR-004` false positive, and `/tmp/` verification paths → **BOM-1**, **JLC-2**, **KIC-3**, **ERP-1**, **KSM-4**.

---

## 4. Prioritized Upstream Action Plan

### `domesticmouse/skills` (`packs/hardware`)
1. **`High` — KSM-1 (`kicad-silkscreen-markup`):** Lock `"-"`, `"1"` polarity tokens to `rotations=(0.0,)`, warn on `90°` `"-"` or displaced `+`/`-` marks near unrelated `TP*` pads in `--inspect`, and add visual polarity checks to `SKILL.md`.
2. **`High` — SKD-1 (`skidl`):** Warn in `SKILL.md` §4 & `advanced_patterns.md` to verify pin-name uniqueness and index multi-diode SOT-23 symbols (`BAV99`) strictly by physical pad number (`part.p[1..3]`).
3. **`Medium` — KPL-1 (`kicad-pcbnew-layout` / `kicad-silkscreen-markup`):** Document `Delete()` vs. crashing `Remove()` (`SIGSEGV`), reject `sys.argv[0] == "-c"` before `os.execv`, and coerce `str` paths in `parse_netlist()`.
4. **`Medium` — KPL-2 (`kicad-pcbnew-layout`):** Switch verification targets from `/tmp/` to `analysis/` and clarify `--output` vs. `--analysis-dir`.
5. **`Medium` — KSM-2 (`kicad-silkscreen-markup`):** Add width-aware wrapping (`max_width` / `board_edge_bounds`) to `add_standard_fab_notes()` for `6 HP` (`30 mm`) boards.
6. **`Medium` — KSM-3 (`kicad-silkscreen-markup`):** Document dense dual-sided polarity placement ordering and add `SilkGrid.explain_block()` + `place_pad_polarity_mark()`.
7. **`Medium` — SKD-2 (`skidl`):** Correct the macOS sandbox rule, explain `fp-lib-table` warnings, add `.kicad_mod` pad validation to Section 6, and add `ruff check --no-cache` / `ruff format --check` to Section 7.
8. **`Medium` — SKD-3 (`skidl`):** Document `Silkscreen`/`Side` fields, `"Manual THT"` consigned metadata, and `1.0 mm` `TestPoint:*` footprints in `jlcpcb_bom.md`.
9. **`Medium` — ERP-1 (`eurorack-panel`):** Replace `/tmp/` verification/DRC paths in `SKILL.md` and `generate_eurorack_panel.py::run_drc_check()` with workspace-local or `TemporaryDirectory` paths.
10. **`Low` — KPL-3, KSM-4, SKD-4, ERP-2:** Document trapped THT bridge-net `tier = -1` + BFS pocket checks, clean remaining `/tmp/` paths in `kicad-silkscreen-markup`/`skidl`, fail fast in `jlcpcb_search.py` without writing empty `-o` files, and split `Alpha RD901F` (`(+7.5, +2.5)`) from `Alps RK09K` in `eurorack-panel`.

### `aklofas/kicad-happy`
1. **`High` — BOM-1 (`bom`):** Fix `translate_bom_pnp.py pnp` to emit JLCPCB's 7-column `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` (`Top`/`Bottom`) schema, enforce `--strict-bom` parity, and document `kicad-cli pcb export pos` in `ordering-and-fabrication.md`.
2. **`High` — JLC-1 (`jlcpcb` / `lcsc`):** Cross-link `skidl/scripts/jlcpcb_search.py` from `jlcpcb/SKILL.md` and `lcsc/SKILL.md` for batched live JLCPCB assembly lookups.
3. **`High` — LCS-1 (`lcsc`):** Fix `search_lcsc.py` fuzzy MPN matching (`"RH-5001"` -> `C206947`) by validating exact/prefix MPN matches or falling back to JLCPCB search + mismatch warnings.
4. **`High` — KIC-1 (`kicad`):** Include `"+"` in `signal_detectors.py` line 3271 and validate unused op-amp inverting/output feedback (`neg_net == out_net`) instead of accepting dual-`GND` open-loop ties.
5. **`Medium` — BOM-2 (`bom`):** Add a pre-schematic / Markdown-spec BOM workflow branch to `bom/SKILL.md`.
6. **`Medium` — JLC-2 (`jlcpcb`):** Change Economic PCBA sides from `"Top only"` to `"Single-sided (Top or Bottom)"` and document headless `kicad-cli` export, ZIP hygiene, and `5 × 5 mm` QR `"Specify a location"` ordering steps.
7. **`Medium` — LCS-2 (`lcsc`):** Extract `encapStandard` inside `provider_lcsc.search_lcsc_direct()` and distinguish `jlcsearch` vs. `lcsc_wmsc` stock/feeder status.
8. **`Medium` — KIC-2 (`kicad`):** Slim `kicad/SKILL.md` (`850` -> `~250–300` lines) into `references/`, add a pre-KiCad review branch, and document `--analysis-dir` stdout suppression and `capability_mode.json` sidecar paths.
9. **`Medium` — KIC-3 (`kicad`):** Scope `analyze_gerbers.py` `GR-004` to `SMDPad + HeatsinkPad` when X2 tags exist and skip/offset `thru_hole` pads for `CP-002` in `copper.py`.
10. **`Medium` — KIC-4 (`kicad`):** Add `.webp`/`.png` raster schematic extraction + macOS `sips`/KCL checks and op-amp/pot/MLCC/`BAV99` analog review patterns to `references/`.
11. **`Low` — LCS-3, KIC-5:** Document `BypassSandbox: true` in `lcsc/SKILL.md` and check nearby silkscreen markers before failing `polarity_markers` in `reader.py`.
