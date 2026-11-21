# Hardware Skills Improvement Audit Report (`/agy-customizations`)

**Date:** `2026-11-21`  
**Scope:** End-to-end clean-room replay of the **EnvelopeFollower** hardware tutorial ([`docs/tutorial/`](./docs/tutorial/)) across **Stages 1–7**, executing a read-only `/agy-customizations` skill-improvement retrospective immediately after each of the **15 tutorial prompts** completed in its subagent.  
**Target Skills Audited (Zero Modifications Made):**
- [`domesticmouse/skills/packs/hardware`](https://github.com/domesticmouse/skills/tree/main/packs/hardware) (commit `a1d39cf9`): `skidl`, `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel`
- [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (commit `6b9767e1`): `kicad`, `bom`, `datasheets`, `jlcpcb`, `lcsc`

---

## Executive Summary

Across **15 prompt retrospectives** (`11` yielding concrete findings, `4` returning `No Improvements Needed`), clean-room subagents identified **22 deduplicated, evidence-backed skill improvements** (`4 High`, `10 Medium`, `8 Low`) without modifying any file under `.agents/skills/` (`diff -rq -x __pycache__ stages/stage-1/.agents/skills stages/stage-7/.agents/skills` verified zero source changes).

### Cross-Cutting Themes
1. **KiCad 10 SWIG & Python Version Skew (`3.9.13` vs. `3.10+`):** KiCad 10's bundled Python on macOS is `3.9.13`, crashing `kicad/scripts/kicad_core/sexp.py` (`str | None` without `from __future__ import annotations`), breaking `itertools.pairwise` (`ruff` `RUF007`), and exhibiting undocumented API quirks (`fp.GetFields()` vs. missing `GetFieldByName()`, `GetLocalZoneConnection()`, `GetLocalSolderMaskMargin() -> None`, `PCB_SHAPE.GetFillMode()`, and `"*.Silkscreen"` `GetLayerName()`).
2. **DNP / Fiducial / Bottom-Side PCBA Pipeline Gaps:** `pcbnew_layout_template.py` omits `SetExcludedFromPosFiles(True)` and misses SKiDL 3.0.0's `(property (name "dnp"))`, `bom/scripts/translate_bom_pnp.py pnp` drops `Val`/`Package` and outputs `Layer=B` instead of JLCPCB's `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` (`Layer=Bottom`), and `jlcpcb/SKILL.md` states `Economic | Sides: Top only`.
3. **False-Negative Silkscreen Checks vs. False-Positive Static Analyzers:** `silk_annotator.py` missed THT `.Fab` bodies, `PCB_SHAPE` polarity graphics, solder-mask expansion margins, `Edge.Cuts` stroke inset, and `5 × 5 mm` QR via keepouts; conversely, `analyze_gerbers.py` `GR-004` and `reader.py` `polarity_markers` fired deterministic false positives on valid mixed THT+SMD `B.Cu` boards.
4. **Multi-Tool Network Batching & Sandbox Ergonomics:** Single-query CLIs (`search_lcsc.py`, `jlcpcb_search.py` missing datasheet URLs and misreading `is_basic` on `jlcsearch` fallback) and `/tmp/` PNG render targets (`eurorack-panel/SKILL.md`) caused avoidable `BypassSandbox: true` / out-of-workspace `read_file` permission prompts.

---

## 1. Per-Prompt Coverage Matrix

| Prompt / Step | Subagent Role (`conversationId`) | Skills Used / Inspected | Verdict | Key Findings Summary |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** (`npx skills add`) | `Stage 1 Skills Installer` (`e2fff363`) | None executed (inspected all 9 headers) | `No Improvements Needed` | Clean non-interactive install (`9/9` skills, `0` symlinks) |
| **Stage 2 — Step 2.1** (Sketch extraction) | `Stage 2.1 Sketch Extractor` (`06b70808`) | `kicad` (`pdf-schematic-extraction.md`) | `Improvements Suggested` | Broaden `kicad` PDF extraction docs/triggers to raster hand-drawn sketches (`Low`) |
| **Stage 2 — Step 2.2** (Analog audit) | `Stage 2.2 Analog Auditor` (`5a15dcc9`) | None (`No Duplication`) | `No Improvements Needed` | Standard domain engineering; no skill needed |
| **Stage 2 — Step 2.3** (Eurorack hardening) | `Stage 2.3 Eurorack Hardening` (`191660bf`) | Inspected `kicad`, `eurorack-panel`, `skidl`, `datasheets` | `Improvements Suggested` | Tighten overly broad `kicad/SKILL.md` trigger phrasing & trim 850-line `SKILL.md` (`Low`) |
| **Stage 3 — Step 3.1** (JLCPCB BOM) | `Stage 3.1 JLCPCB BOM Researcher` (`97ae374f`) | `jlcpcb`, `lcsc`, `skidl`, `bom`, `datasheets` | `Improvements Suggested` | `jlcpcb_search.py` `is_basic` bug & batch flags; `jlcpcb` `Top only`; `search_lcsc.py`/`provider_lcsc.py`; `jlcpcb_bom.md` query traps (`3 Med, 1 Low`) |
| **Stage 3 — Step 3.2** (Audio walkthrough) | `Stage 3.2 Circuit Walkthrough Author` (`32419e58`) | None (`No Duplication`) | `No Improvements Needed` | Educational prose walkthrough; progressive disclosure cleanly skipped CAD skills |
| **Stage 3 — Step 3.3a** (TP ideas) | `Stage 3.3 Test Points and Silkscreen` (`d1a78fe8`) | Inspected `kicad-pcbnew-layout`, `eurorack-panel`, `skidl`, `bom`, `kicad` | `No Improvements Needed` | Existing skills cleanly covered `DNP` `B.Cu` TPs and `10–11 mm` panel standoff |
| **Stage 3 — Step 3.3b** (`RH-5001` `DNP` TPs) | `Stage 3.3 Test Points and Silkscreen` (`d1a78fe8`) | `skidl`, `lcsc`, `datasheets`, `bom`, `jlcpcb` | `Improvements Suggested` | `provider_lcsc.py` drops `encapStandard`; 3 separate prompts for lookup+PDF; `package: "-"` drill check; `DNP` flag alignment (`1 High, 2 Med`) |
| **Stage 3 — Step 3.3c** (`SilkscreenInstructions.md`) | `Stage 3.3 Test Points and Silkscreen` (`d1a78fe8`) | `kicad-silkscreen-markup`, `kicad`, `jlcpcb` | `Improvements Suggested` | `is_passive_ref()` skips suffixed passives; `SilkGrid` `.Fab` seeding; `silkscreen_completeness` doc gap; `jlcpcb` vs value-only passives (`1 Med, 3 Low`) |
| **Stage 4** (SKiDL & ERC) | `Stage 4 SKiDL Builder` (`e8a29204`) | `skidl`, `bom`, `jlcpcb`, `kicad-pcbnew-layout` | `Improvements Suggested` | `pcbnew_layout_template.py` misses `(property (name "dnp"))`; `skidl` CWD/`KICAD*_SYMBOL_DIR`/`.erc` vs `.log`/`print(show())`/`gen_xml` & natural sort (`1 High, 1 Med, 2 Low`) |
| **Stage 5 — Step 5.1** (Main PCB build) | `Stage 5.1 PCB Layout Engineer` (`f7009d02`) | `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `eurorack-panel`, `kicad`, `jlcpcb` | `Improvements Suggested` | Missing `SetExcludedFromPosFiles(True)` + `FID*`; QR copper/via keepout; `PCB_SHAPE` blind spot & `--severity-all`; 3 routing pitfalls; Python 3.9 vs `RUF007` (`1 High, 3 Med, 1 Low`) |
| **Stage 5 — Step 5.2a** (Silkscreen audit) | `Stage 5.2 Silkscreen Auditor` (`e93540d9`) | `kicad-silkscreen-markup`, `kicad-pcbnew-layout`, `kicad`, `jlcpcb` | `Improvements Suggested` | `SilkGrid` THT `.Fab`/mask/`Edge.Cuts` stroke/shape gaps; netlist `Silkscreen`-field helper; KiCad 10 SWIG quirks; `SK-001` anchor-only gap (`1 High, 2 Med, 1 Low`) |
| **Stage 5 — Step 5.2b** (Silkscreen fixes) | `Stage 5.2 Silkscreen Auditor` (`e93540d9`) | `kicad-silkscreen-markup`, `kicad-pcbnew-layout`, `kicad`, `jlcpcb` | `Improvements Suggested` | `sexp.py` Python 3.9 crash; rigid `style_idx=1` `place_ref_val_pair`; `"*.Silkscreen"` `GetLayerName()`; `reader.py` `polarity_markers` bug (`3 Med, 1 Low`) |
| **Stage 6** (3U Front Panel) | `Stage 6 Front Panel Builder` (`fb18af32`) | `eurorack-panel`, `kicad`, `jlcpcb`, `kicad-silkscreen-markup` | `Improvements Suggested` | `/tmp/` PNG render causes out-of-workspace `read_file` timeout; silent `lib_footprint_issues` count & `8 jack` checklist drift (`1 Med, 1 Low`) |
| **Stage 7** (Manufacturing & CPL) | `Stage 7 Manufacturing Exporter` (`9910adce`) | `kicad`, `jlcpcb`, `bom`, `eurorack-panel`, `lcsc` | `Improvements Suggested` | `translate_bom_pnp.py` schema mismatch (`Layer=B`, drops `Val`/`Package`); `GR-004` X2 false positive; `jlcpcb` Bottom PCBA/`--bottom-negate-x`/rotations/QR; `fab_release_gate.py` `--schematic` required (`1 High, 2 Med, 1 Low`) |

---

## 2. Consolidated Skill Improvements (Grouped by Skill & Prioritized)

### A. `domesticmouse/skills/packs/hardware`

#### 1. `kicad-pcbnew-layout`

- **KPL-1 (`High`) — Missing `SetExcludedFromPosFiles(True)`, `FID*` Handling, and SKiDL 3.0.0 `(property (name "dnp"))` Parsing**
  - **Target Files:** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/SKILL.md#L29), [`scripts/pcbnew_layout_template.py`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/scripts/pcbnew_layout_template.py#L126-L144), [`references/kicad10_pcbnew_api.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/references/kicad10_pcbnew_api.md#L69-L73)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stages 4, 5.1, 5.2b`):**
    1. SKiDL 3.0.0 emits `(property (name "dnp"))` without a `(value ...)` child, whereas `parse_netlist()` (`pcbnew_layout_template.py` lines 127–138) requires both `pname` and `pval`, silently missing `dnp = True` unless duplicated in `Notes` or `dnp_prefixes`.
    2. `populate_footprints()` (lines 320–322), `SKILL.md`, and `kicad10_pcbnew_api.md` call `SetDNP(True)` and `SetExcludedFromBOM(True)` without `SetExcludedFromPosFiles(True)`, and ignore optical fiducials `FID*`. Without `SetExcludedFromPosFiles(True)` + `SetDNP(True)`, `FID1`–`FID3` leak into `kicad-cli pcb export pos --smd-only --exclude-dnp`.
  - **Proposed Change:** Update `parse_netlist()` to accept valueless `(property (name "dnp"))`; call `fp.SetExcludedFromPosFiles(True)` inside `if comp["dnp"]:` and on `FID*` footprints; add `get_footprint_field(fp, name)`; and add `kicad-cli pcb export pos --side back --smd-only --exclude-dnp` to the `SKILL.md` Mandatory Verification Sequence.

- **KPL-2 (`Medium`) — Routing & DFM Patterns Missing Pre-Via Pruning, Bridged-Pin Stubs, Breakout Scope, and QR Keepouts**
  - **Target File:** [`references/routing_and_dfm_patterns.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/references/routing_and_dfm_patterns.md#L25-L35)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`)
  - **Observed Evidence (`Stage 5.1`):** Following the pre-route decoupling and breakout priority patterns caused `2` `via_dangling` warnings (`C7`/`C8` pre-vias unused after MST), `1` `track_dangling` warning (`U2.13`–`U2.14` bridged directly while emitting unconditional grid stubs), `IN_CLAMP` boxing when `70–90 mm` nets took priority `-1`, and a `GND` via (`26.5, 103.5`) punched directly inside the `5 × 5 mm` `B.SilkS` QR box.
  - **Proposed Change:** Add four concise rules to `references/routing_and_dfm_patterns.md`: prune unreferenced `pre_vias` post-MST, emit pad-to-grid stubs only for consumed MST anchors, restrict priority `-1` to local IC escape nets, and block `QR_BOX` (`±0.5 mm` margin) in trace routing and GND via-stitching grids.

- **KPL-3 (`Medium`) — Undocumented KiCad 10 Bundled Python `3.9.13` & SWIG API Quirks**
  - **Target File:** [`references/kicad10_pcbnew_api.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/references/kicad10_pcbnew_api.md)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`)
  - **Observed Evidence (`Stages 5.1, 5.2a, 5.2b`):** KiCad 10.0.7 bundles Python `3.9.13` (`itertools.pairwise` suggested by `ruff` `RUF007` raises `ImportError`), and SWIG calls hit `AttributeError` on `pad.GetZoneConnection()` (must use `GetLocalZoneConnection()`/`SetLocalZoneConnection()`), `fp.GetFieldByName()` (must iterate `fp.GetFields()`), `dr.IsFilled` (must use `dr.GetFillMode()`), `None` returns from `pad.GetLocalSolderMaskMargin()`, and `item.GetLayerName()` returning `"F.Silkscreen"`/`"B.Silkscreen"` instead of `"F.SilkS"`/`"B.SilkS"`.
  - **Proposed Change:** Document Python `3.9` compatibility (`ruff check --target-version py39` / `# noqa: RUF007`) and add those five SWIG API mappings to `references/kicad10_pcbnew_api.md`.

- **KPL-4 (`Medium`) — DRC `--severity-all`, Netlist `Silkscreen` Parity, `.venv` Analyzer Python, and `EXE001` Parity**
  - **Target File:** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-pcbnew-layout/SKILL.md#L55)
  - **`/agy-customizations` Principle:** Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stages 5.1, 5.2a, 5.2b`):** Running `kicad-cli pcb drc` without `--severity-all` hid `8` silkscreen warnings and `3` dangling copper warnings; ignoring netlist `Silkscreen` fields caused hardcoded drift (`TP2 -12V`, `J4 -12V`); running `analyze_pcb.py` under KiCad Python 3.9 crashed; and `chmod +x` (`EXE001`) was missing unlike `eurorack-panel/SKILL.md`.
  - **Proposed Change:** Pass `--severity-all` to `kicad-cli pcb drc`, remind authors to consume footprint `Silkscreen` fields directly instead of hardcoded dicts, specify `.venv/bin/python` (Python `>= 3.10`) for `analyze_pcb.py`, and mirror `chmod +x` guidance before `ruff check`.

#### 2. `kicad-silkscreen-markup`

- **KSM-1 (`High`) — `SilkGrid` & `--inspect` Miss THT `.Fab` Bodies, Solder-Mask Margins, `Edge.Cuts` Stroke Inset, `PCB_SHAPE` Graphics, and Rigid Pair Offsets**
  - **Target Files:** [`scripts/silk_annotator.py`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/SKILL.md)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Steps
  - **Observed Evidence (`Stages 3.3c, 5.1, 5.2a, 5.2b`):** `silk_annotator.py --inspect` reported `RESULT: PASS` while:
    1. `SilkGrid.__init__` (`line 184`) blocked `.Fab` bodies only when `is_smd_footprint(fp)`, letting `C3` `47uF` land inside `J4`'s shroud and `RV1` `'1'` inside `C1`.
    2. `SilkGrid` (`lines 149–159`) padded copper bboxes by `0.25 mm` without solder-mask margin, allowing 7 texts within `0.244–0.249 mm` of `B.Mask`.
    3. `SilkGrid` & `inspect_board_silk()` (`lines 131–138`, `817`) used `GetBoardEdgesBoundingBox()`, inflating a `30.00 × 108.00 mm` board by the `0.10 mm` `Edge.Cuts` stroke (`-0.05..30.05`).
    4. `inspect_board_silk()` ignored `PCB_SHAPE` items from `add_silk_dot()`/`add_silk_seg()`/`add_silk_rect()`, missing `U2`'s Pin-1 dot on `U2.1` `B.Mask` (`0.000 mm`), `J4`'s bar/dot inside `J4`'s shroud, and vias inside the `5 × 5 mm` QR box.
    5. `place_ref_val_pair()` (`lines 688–693`) forced centered alignment for `style_idx=1` at `90°`, failing in tight corridors where sliding `<REF>` within `<= 1.2 mm` split worked; and no `get_fp_silkscreen_field()` or grid-checked polarity/board-label helpers existed.
  - **Proposed Change:** Block mounting-side THT `.Fab` outlines in `SilkGrid`; expand pad keepouts by mask margin + `0.25 mm`; inset `GetBoardEdgesBoundingBox()` by half edge stroke width; validate `PCB_SHAPE` silk items (and QR copper/via keepouts) in `--inspect`; allow shifted `style_idx=1` offsets in `place_ref_val_pair()`; and provide `get_fp_silkscreen_field()`, `place_silk_dot/seg/rect()`, and `place_board_label()`.

- **KSM-2 (`Low`) — `is_passive_ref()` Drops Suffixed / Underscored Passives**
  - **Target File:** [`scripts/silk_annotator.py`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L46-L48)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`)
  - **Observed Evidence (`Stage 3.3c`):** `re.match(r"^[RC]\d+$", ref)` skips split/suffixed passives (`R16A`, `R_PWR`, `C_DEC1`) during value-only enforcement.
  - **Proposed Change:** Update to `not ref.startswith("RV") and bool(re.match(r"^[RC](?:\d+[A-Za-z0-9_]*|_[A-Za-z0-9_]+)$", ref))`.

- **KSM-3 (`Low`) — Clarify `analyze_pcb.py` `silkscreen_completeness` Warnings & Board Name/Rev**
  - **Target File:** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/SKILL.md#L37)
  - **`/agy-customizations` Principle:** Validation Steps (`SKILL.md`)
  - **Observed Evidence (`Stages 3.3c, 5.2b`):** `SKILL.md` notes `findings[]` emits zero errors for hidden passive refs, but omits that `silkscreen_completeness.checks.ref_designators_visible` (`>= 90%`) and `polarity_markers` (`> 3` polarized parts) still report `"warning"`, and omits mentioning `board_name`/`revision_marking` texts or `.venv/bin/python`.
  - **Proposed Change:** Document the expected `silkscreen_completeness` warning keys vs. `silk_annotator.py --inspect`, include board title + `Rev` guidance, and specify `.venv/bin/python` for `analyze_pcb.py`.

#### 3. `skidl`

- **SKD-1 (`Medium`) — `SKILL.md` CWD Pinning, `KICAD6`–`KICAD9_SYMBOL_DIR`, `.erc` vs. `.log`, `print(show())`, and `generate_xml()` Quirk**
  - **Target File:** [`SKILL.md`](./stages/stage-7/.agents/skills/skidl/SKILL.md#L23-L68)
  - **`/agy-customizations` Principle:** `SKILL.md` Procedures & Validation Steps
  - **Observed Evidence (`Stage 4`):** Importing `skidl==3.0.0` creates `<script>.log`/`.erc` in `os.getcwd()` unless `os.chdir(Path(__file__).resolve().parent)` runs *first*; missing `KICAD6`–`KICAD9_SYMBOL_DIR` emits `4` startup warnings; `.log` emits `6` benign `fp-lib-table`/empty-root-tag warnings even when `.erc` is clean; `show(...)` without `print(...)` prints nothing under `python -c`; and `generate_xml()` produces malformed XML (`part=""...""` + S-expr `<fields>`).
  - **Proposed Change:** Update Section 1 (`os.chdir` + `KICAD{6..10}_SYMBOL_DIR`), Section 2 (`print(show(...))`), and Section 6 (separate `.erc` vs. `.log` expectations and warn against passing `*_bom.xml` to strict XML parsers).

- **SKD-2 (`Medium`) — `jlcpcb_search.py` `is_basic` Fallback Bug, Missing `dataManualUrl`, and Batching Flags**
  - **Target File:** [`scripts/jlcpcb_search.py`](./stages/stage-7/.agents/skills/skidl/scripts/jlcpcb_search.py#L48-L129)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`)
  - **Observed Evidence (`Stages 3.1, 3.3b`):** `query_jlcsearch()` line 96 reads `item.get("basic")` instead of `is_basic`/`is_preferred` (mislabeling Basic parts as `Extended`), omits `dataManualUrl`, lacks `-o/--output`, `--basic`, and `--delay` for large BOMs, and returns `"package": "-"` for THT parts like `RH-5001` (`C5199801`), forcing extra network calls.
  - **Proposed Change:** Fix `is_basic`/`is_preferred` parsing, extract `dataManualUrl`, and add `-o/--output`, `--basic`, and `--delay` CLI options.

- **SKD-3 (`Low`) — `jlcpcb_bom.md` Query Traps, `package: "-"` Drill Verification, `TP*` `DNP` Parity, and Natural Designator Sort**
  - **Target File:** [`references/jlcpcb_bom.md`](./stages/stage-7/.agents/skills/skidl/references/jlcpcb_bom.md)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`) & Validation Steps
  - **Observed Evidence (`Stages 3.1, 3.3b, 4`):** Multi-word `"22pF 50V C0G 0603"`/`"47pF..."`/`"100pF..."` returned `1 nF` (`C18255878`) while `"22pF 0603"` found Samsung Basic `C1653`/`C1671`/`C14858`; `"3mm LED green"` returned `0` hits vs. `"3mm LED"` (`C85161`); `RH-5001` returned `"package": "-"` despite `"2.5mm"` referring to bead OD (`Ø 1.0 mm` drill); and unsorted `", ".join(refs)` scrambled BOM CSV designators.
  - **Proposed Change:** Document minimal query tokens, add a datasheet drill/height/protrusion check for `"package": "-"`, document the 3-bucket Eurorack BOM split + all-3 `DNP` flags (`dnp`, `exclude_from_bom`, `exclude_from_pos_files`), and natural-sort `refs` in `generate_jlcpcb_bom()`.

#### 4. `eurorack-panel`

- **EP-1 (`Medium`) — Rendering 3D Inspection Images to `/tmp/` Causes Out-of-Workspace `read_file` Timeouts**
  - **Target File:** [`SKILL.md`](./stages/stage-7/.agents/skills/eurorack-panel/SKILL.md#L72-L77)
  - **`/agy-customizations` Principle:** `SKILL.md` Workflow & Validation Steps
  - **Observed Evidence (`Stage 6`):** Running `kicad-cli pcb render ... --output /tmp/panel_front.png` as instructed caused `read_file "/private/tmp/panel_front.png"` to time out after 60s awaiting permission; rendering into `panel/EnvelopeFollower_Panel_front.png` succeeded immediately.
  - **Proposed Change:** Change Step 3 paths to workspace-local `panel/<Panel>_front.png` / `_back.png` and warn against `/tmp/` for visual inspection.

- **EP-2 (`Low`) — Silent `lib_footprint_issues` Filtering & Hardcoded `8 jack` Checklist**
  - **Target Files:** [`scripts/generate_eurorack_panel.py`](./stages/stage-7/.agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py#L1012-L1021), [`SKILL.md`](./stages/stage-7/.agents/skills/eurorack-panel/SKILL.md#L69)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Steps
  - **Observed Evidence (`Stage 6`):** `run_drc_check()` hid `10` `lib_footprint_issues` warnings without logging their count; `SKILL.md` assumed `8 jack PTH holes`, whereas mixed panels report `7` PTH + `3` NPTH (`D4` `3.2 mm` LED counted under `mounting_holes` by `analyze_gerbers.py`) and `CP-002` `info` notices in `analyze_pcb.py`.
  - **Proposed Change:** Print the filtered `lib_footprint_issues` count in `run_drc_check()` and generalize the `SKILL.md` Step 3 checklist.

---

### B. `aklofas/kicad-happy`

#### 5. `bom`

- **BOM-1 (`High`) — `translate_bom_pnp.py pnp` Drops `Val`/`Package` & Outputs `Layer=B`, Contradicting `ordering-and-fabrication.md` and JLCPCB CPL**
  - **Target Files:** [`scripts/translate_bom_pnp.py`](./stages/stage-7/.agents/skills/bom/scripts/translate_bom_pnp.py#L270-L293), [`references/ordering-and-fabrication.md`](./stages/stage-7/.agents/skills/bom/references/ordering-and-fabrication.md#L106-L120)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Cross-File Consistency
  - **Observed Evidence (`Stage 7`):** `translate_bom_pnp.py pnp` emits `["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]` with `Layer="T"`/`"B"` (dropping `Val` & `Package` and contradicting `ordering-and-fabrication.md`'s `"Top or Bottom"`). Generating JLCPCB's `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` (`Layer=Bottom`) required a custom converter script, and `--bom` silently ignores BOM parts missing from the PnP CSV.
  - **Proposed Change:** Add `--format jlcpcb` (emitting 7 columns, `Top`/`Bottom`, optional `mm` suffixes) and `--strict-bom-match` (bidirectional designator + `Val`/`Package` parity check), and align `ordering-and-fabrication.md` with exact `kicad-cli pcb export pos` flags.

- **BOM-2 (`Medium`) — Unify `DNP` vs. `exclude_from_bom` / `exclude_from_pos_files` Guidance for Optional THT Parts**
  - **Target File:** [`references/kicad-fields.md`](./stages/stage-7/.agents/skills/bom/references/kicad-fields.md#L20-L45)
  - **`/agy-customizations` Principle:** Progressive Disclosure (`references/`) & Cross-Skill Consistency
  - **Observed Evidence (`Stage 3.3b`):** Skills split `dnp`, `exclude_from_bom`, and `exclude_from_pos_files` inconsistently for `TP1`–`TP8` (`RH-5001`).
  - **Proposed Change:** Specify setting all three KiCad flags on optional `DNP` test points while documenting their LCSC part number in a separate `DNP / Optional` BOM section.

#### 6. `jlcpcb`

- **JLC-1 (`Medium`) — `SKILL.md` States `"Economic | Sides: Top only"`, Omits Bottom CPL Flags/`--bottom-negate-x` Warning, Polarized Packages, ZIP Hygiene & `5 × 5 mm` QR**
  - **Target File:** [`SKILL.md`](./stages/stage-7/.agents/skills/jlcpcb/SKILL.md#L114-L208)
  - **`/agy-customizations` Principle:** `SKILL.md` Procedural Accuracy & Validation Steps
  - **Observed Evidence (`Stages 3.1, 3.3c, 7`):**
    1. Line 116 falsely states `Economic | Sides: Top only` despite single-sided `B.Cu` Economic PCBA being supported.
    2. Missing `kicad-cli pcb export pos` flags (`--side back --smd-only --exclude-dnp --units mm`), warning **against** `--bottom-negate-x`, and rule excluding `*_cpl.csv` from Gerber ZIPs.
    3. Rotation table omits `SOIC-14`, `D_SOD-323`, and `CP_Elec_*` electrolytics, plus `(180° - Rot)` `B.Cu` mirror check.
    4. No cross-reference to value-only `B.SilkS` passive conventions or JLCPCB's modern `5 × 5 mm` `B.SilkS` QR square (`Mark on PCB -> Specify a location`, replacing obsolete `JLCJLCJLCJLC`).
  - **Proposed Change:** Update line 116 to `Single-sided (Top OR Bottom)` and add concise Bottom-side CPL export, rotation/mirror, ZIP exclusion, density-adaptive silkscreen, and `5 × 5 mm` QR square instructions.

#### 7. `kicad`

- **KCD-1 (`Medium`) — `analyze_gerbers.py` `GR-004` False Positive on Mixed THT+SMD / Stitched `B.Cu` Boards**
  - **Target Files:** [`scripts/analyze_gerbers.py`](./stages/stage-7/.agents/skills/kicad/scripts/analyze_gerbers.py#L2117-L2150), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Validation Accuracy
  - **Observed Evidence (`Stage 7`):** Emitted `WARNING GR-004: B paste layer: 125 flashes vs 281 copper (44%)` even though X2 `pad_summary.smd_apertures` on the same run confirmed `125/125` (`100%`) SMD pads received paste (the extra `156` flashes were `100` tented vias, `53` THT pads, and `3` fiducials).
  - **Proposed Change:** Compare `paste_flashes[side]` against `SMDPad` flashes whenever X2 `%TA.AperFunction` attributes are present.

- **KCD-2 (`Medium`) — `kicad_core/sexp.py` Crashes Under KiCad 10's Bundled Python `3.9.13`**
  - **Target Files:** [`scripts/kicad_core/sexp.py`](./stages/stage-7/.agents/skills/kicad/scripts/kicad_core/sexp.py#L226), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & `SKILL.md` Prerequisites
  - **Observed Evidence (`Stage 5.2b`):** Running `analyze_pcb.py` under KiCad's bundled Python raised `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'` because `sexp.py` lacks `from __future__ import annotations`.
  - **Proposed Change:** Add `from __future__ import annotations` across `kicad/scripts/` (or explicitly document Python `>= 3.10` / `.venv/bin/python` in `SKILL.md`).

- **KCD-3 (`Low`) — `reader.py` `silkscreen_completeness.checks["polarity_markers"]` Always Fails When `len(polarized) > 3`**
  - **Target File:** [`scripts/pcb/reader.py`](./stages/stage-7/.agents/skills/kicad/scripts/pcb/reader.py#L1950-L2017)
  - **`/agy-customizations` Principle:** Validation Steps / Script Precision
  - **Observed Evidence (`Stage 5.2b`):** `reader.py` emits an unconditional `info` `polarity_reminder` whenever `len(polarized) > 3`, and evaluates `polarity_markers` as `not any(w["type"] == "polarity_reminder" ...)`, making `polarity_markers: false` unavoidable even when every diode/IC/electrolytic has verified silkscreen marks.
  - **Proposed Change:** Check actual footprint/board polarity silkscreen marks (or decouple `polarity_markers` from the unconditional `info` reminder).

- **KCD-4 (`Low`) — `assembly.py` `SK-001` Checks Only `board_texts` Origins vs. Copper Pads**
  - **Target Files:** [`scripts/pcb/assembly.py`](./stages/stage-7/.agents/skills/kicad/scripts/pcb/assembly.py#L1145-L1207), [`SKILL.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md)
  - **`/agy-customizations` Principle:** Validation Steps
  - **Observed Evidence (`Stage 5.2a`):** `SK-001` reported zero warnings while `U2`'s `B.SilkS` Pin-1 dot (`PCB_SHAPE`) overlapped `U2.1`'s `B.Mask` opening (`0.000 mm` mask clearance, `0.025 mm` copper clearance).
  - **Proposed Change:** Check `fp_text` and `PCB_SHAPE` silk bboxes against mask-expanded pads in `SK-001`, or document `kicad-cli pcb drc --severity-all` as mandatory for real silk-over-copper checks.

- **KCD-5 (`Low`) — `fab_release_gate.py` Requires `--schematic`, Blocking SKiDL / Netlist-First PCBs**
  - **Target File:** [`scripts/fab_release_gate.py`](./stages/stage-7/.agents/skills/kicad/scripts/fab_release_gate.py#L657-L700)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`)
  - **Observed Evidence (`Stage 7`):** Running `fab_release_gate.py --pcb ... --gerbers ...` exited `2` (`--schematic/-s` required) on a SKiDL PCB with no `.kicad_sch`.
  - **Proposed Change:** Make `--schematic/-s` optional (marking schematic-only gates as `skip`).

- **KCD-6 (`Low`) — `kicad/SKILL.md` Overly Broad Triggers, 850-Line Context Bloat, and Raster Schematic Support**
  - **Target Files:** [`SKILL.md`](./stages/stage-7/.agents/skills/kicad/SKILL.md#L1-L99), [`references/pdf-schematic-extraction.md`](./stages/stage-7/.agents/skills/kicad/references/pdf-schematic-extraction.md)
  - **`/agy-customizations` Principle:** Frontmatter `description` & Progressive Disclosure (`docs/skills.md`)
  - **Observed Evidence (`Stages 2.1, 2.3`):** Catch-all phrases (`"review any hardware design"`, `"any electronics/PCB design question"`) caused the 850-line `kicad/SKILL.md` to match prose/image reviews; meanwhile `pdf-schematic-extraction.md` omitted raster/hand-drawn schematic handling (`ffmpeg`/`sips` 2×–4× symbol crops, provisional designators, pin-conservation math check).
  - **Proposed Change:** Scope `description` to KiCad project files/Gerbers/PDF+raster schematics; move inline JSON schema dumps into `references/`; and add a **Raster & Hand-Drawn Schematics** subsection to `references/pdf-schematic-extraction.md`.

#### 8. `lcsc` & `datasheets`

- **LCS-1 (`High`) — `provider_lcsc.py` Drops `encapStandard`/`attributes`, `search_lcsc.py` Lacks Batching/Datasheet Download & Stock Source Disambiguation**
  - **Target Files:** [`lcsc/scripts/provider_lcsc.py`](./stages/stage-7/.agents/skills/lcsc/scripts/provider_lcsc.py#L162-L194), [`lcsc/scripts/search_lcsc.py`](./stages/stage-7/.agents/skills/lcsc/scripts/search_lcsc.py#L184-L212), [`lcsc/SKILL.md`](./stages/stage-7/.agents/skills/lcsc/SKILL.md), [`datasheets/SKILL.md`](./stages/stage-7/.agents/skills/datasheets/SKILL.md)
  - **`/agy-customizations` Principle:** Executable Helpers (`scripts/`) & Workflow Efficiency
  - **Observed Evidence (`Stages 3.1, 3.3b`):**
    1. `search_lcsc_direct()` omits `encapStandard` and `attributes`, leaving `enrich_from_wmsc()` backfill dead (`package: "-"` for `RH-5001` and `C14663`) and hides `lcsc_stock` vs. JLCPCB stock (`C14663` showed `stk=0` in `wmsc` vs. `53.4M` at JLCPCB).
    2. `search_lcsc.py` accepts only 1 query, aborts (`sys.exit(2)`) on a single `jlcsearch` HTTP 500 (`"MKS2 1uF 63V"`), and lacks `--download-datasheet <path>`—forcing `3` separate `BypassSandbox: true` prompts for `RH-5001`.
  - **Proposed Change:** Map `encapStandard` and `attributes` in `search_lcsc_direct()`, preserve both `stock` and `lcsc_stock`, support `nargs="+"` queries + `--output` + per-query error handling + `--download-datasheet` in `search_lcsc.py`, and document JLCPCB vs. LCSC `wmsc` stock and PDF reader fallbacks (`qlmanage`/native reader when `pypdf`/`pdftotext` are absent).

---

### C. New Customization Proposals

- **None Required (`No Duplication`):** All Stage 2–3 analog critique, Eurorack protection, and educational circuit walkthrough prompts were cleanly served by domain knowledge and existing tools; adding standalone skills for general analog theory or prose documentation would violate `agy-customizations` Best Practice #4 (*No Duplication*).

---

## 3. Per-Prompt Raw Findings Summary (Traceability Appendix)

- **Stage 1 (`e2fff363`):** `No Improvements Needed` — Both `npx skills add` calls auto-detected `antigravity` non-interactively (`0` symlinks).
- **Stage 2.1 (`06b70808`):** `KCD-6` (raster/hand-drawn schematic extraction + `ffmpeg` crop/pin-conservation checklist).
- **Stage 2.2 (`5a15dcc9`):** `No Improvements Needed` — Prose analog audit (`EnvelopeFollowerImprovements.md`).
- **Stage 2.3 (`191660bf`):** `KCD-6` (`kicad/SKILL.md` overly broad frontmatter triggers + 850-line size vs. `eurorack-panel`/`skidl`).
- **Stage 3.1 (`97ae374f`):** `SKD-2` (`jlcpcb_search.py` `is_basic` + flags), `JLC-1` (`Top only`), `LCS-1` (batching/`encapStandard`/`wmsc` stock `0` on `C14663`), `SKD-3` (`"22pF 50V C0G 0603"` returning `1 nF`, `"3mm LED green"` 0 hits).
- **Stage 3.2 (`32419e58`):** `No Improvements Needed` — Educational walkthrough (`EnvelopeFollowerExplanation.md`).
- **Stage 3.3a (`d1a78fe8`):** `No Improvements Needed` — Read-only TP architecture analysis (`TP1`–`TP8`).
- **Stage 3.3b (`d1a78fe8`):** `SKD-2` (missing `dataManualUrl`), `LCS-1` (dead `encapStandard` backfill & 3 `BypassSandbox` calls for `RH-5001`), `SKD-3`/`BOM-2` (`package: "-"` drill check & unified `DNP` flags).
- **Stage 3.3c (`d1a78fe8`):** `KSM-1` (`SilkGrid` `.Fab` body seeding), `KSM-2` (`is_passive_ref()`), `KSM-3` (`silkscreen_completeness` doc), `JLC-1` (value-only passives + `5 × 5 mm` QR square).
- **Stage 4 (`e8a29204`):** `KPL-1` (`(property (name "dnp"))` bug in `pcbnew_layout_template.py`), `SKD-1` (`os.chdir`, `KICAD6-9_SYMBOL_DIR`, `.erc`/`.log`, `print(show())`, `gen_xml`), `SKD-3` (natural-sort `generate_jlcpcb_bom()`).
- **Stage 5.1 (`f7009d02`):** `KPL-1` (`SetExcludedFromPosFiles(True)` + `FID*` + `pcb export pos`), `KPL-2`/`KSM-1` (`QR_BOX` via keepout), `KSM-1`/`KPL-4` (`PCB_SHAPE` blind spots + `--severity-all`), `KPL-2` (3 routing pitfalls), `KPL-3`/`KPL-4` (Python 3.9 vs `RUF007`, `GetLocalZoneConnection`, `chmod +x`).
- **Stage 5.2a (`e93540d9`):** `KSM-1` (THT `.Fab`, `B.Mask` margin, `Edge.Cuts` stroke, `PCB_SHAPE` inspections), `KSM-1`/`KPL-4` (`Silkscreen`-field helper/parity), `KPL-3` (`GetFieldByName`, `GetFillMode`, `GetLocalSolderMaskMargin`), `KCD-4` (`SK-001` anchor-only).
- **Stage 5.2b (`e93540d9`):** `KCD-2`/`KPL-4`/`KSM-3` (`sexp.py` Python 3.9 crash), `KSM-1` (rigid `style_idx=1` `place_ref_val_pair`), `KPL-1`/`KPL-3` (`"*.Silkscreen"` `GetLayerName()`), `KCD-3` (`reader.py` `polarity_markers` false negative).
- **Stage 6 (`fb18af32`):** `EP-1` (`/tmp/` PNG render `read_file` timeout), `EP-2` (`run_drc_check()` silent `lib_footprint_issues` count + `8 jack` checklist).
- **Stage 7 (`9910adce`):** `BOM-1` (`translate_bom_pnp.py` schema mismatch & missing `--strict-bom-match`), `KCD-1` (`GR-004` X2 false positive), `JLC-1` (Bottom PCBA/`--bottom-negate-x`/rotations/ZIP/`5 × 5 mm` QR), `KCD-5` (`fab_release_gate.py` `--schematic` required).

---

## 4. Prioritized Upstream Action Plan

### `domesticmouse/skills` (`packs/hardware`)
1. **[`High`]** Patch `kicad-pcbnew-layout/scripts/pcbnew_layout_template.py` (`parse_netlist()` valueless `(property (name "dnp"))`, `SetExcludedFromPosFiles(True)` on `dnp` and `FID*`, `get_footprint_field()`), and add `kicad-cli pcb export pos` verification to `kicad-pcbnew-layout/SKILL.md`.
2. **[`High`]** Harden `kicad-silkscreen-markup/scripts/silk_annotator.py`: block mounting-side THT `.Fab` outlines, add solder-mask pad expansion, inset `Edge.Cuts` stroke width, inspect `PCB_SHAPE` silk graphics + QR copper/via keepouts, allow shifted `style_idx=1` pairs, and add `get_fp_silkscreen_field()` + `is_passive_ref()` regex expansion.
3. **[`Medium`]** Update `skidl/scripts/jlcpcb_search.py` (`is_basic`/`is_preferred`, `dataManualUrl`, `-o`/`--basic`/`--delay`) and `skidl/SKILL.md` (`os.chdir` before import, `KICAD6-9_SYMBOL_DIR`, `.erc` vs `.log`, `print(show())`, `generate_xml()` note).
4. **[`Medium`]** Update `kicad-pcbnew-layout/references/routing_and_dfm_patterns.md` (pre-via pruning, consumed-anchor stubs, local breakout scope, QR via block), `references/kicad10_pcbnew_api.md` (Python `3.9.13` + 5 KiCad 10 SWIG differences), and `kicad-pcbnew-layout/SKILL.md` (`--severity-all`, `.venv/bin/python`, `chmod +x`).
5. **[`Medium`]** Update `eurorack-panel/SKILL.md` Step 3 render paths from `/tmp/` to workspace-local paths (and log filtered `lib_footprint_issues` counts + generalize Step 3 hole checklist).
6. **[`Low`]** Update `skidl/references/jlcpcb_bom.md` (short Class I pF queries, `package: "-"` drill check, unified `DNP` flags, natural sort) and `kicad-silkscreen-markup/SKILL.md` (`silkscreen_completeness` note).

### `aklofas/kicad-happy`
1. **[`High`]** Update `bom/scripts/translate_bom_pnp.py` (`--format jlcpcb` 7-column `Top`/`Bottom` schema + `--strict-bom-match`) and align `bom/references/ordering-and-fabrication.md` + `references/kicad-fields.md`.
2. **[`High`]** Fix `lcsc/scripts/provider_lcsc.py` (`encapStandard`, `attributes`, `lcsc_stock`) and `lcsc/scripts/search_lcsc.py` (`nargs="+"`, per-query HTTP 500 handling, `--download-datasheet`, JLCPCB vs `wmsc` stock warning).
3. **[`Medium`]** Update `jlcpcb/SKILL.md` (`Single-sided (Top OR Bottom)`, Bottom CPL export without `--bottom-negate-x`, `SOIC-14`/`SOD-323`/`CP_Elec_*` + `(180° - Rot)` mirror note, ZIP exclusion of `*_cpl.csv`, `5 × 5 mm` QR square, value-only `B.SilkS` cross-ref).
4. **[`Medium`]** Fix `kicad/scripts/analyze_gerbers.py` `GR-004` to compare paste flashes against X2 `SMDPad` apertures, and add `from __future__ import annotations` to `kicad/scripts/kicad_core/sexp.py`.
5. **[`Low`]** Fix `kicad/scripts/pcb/reader.py` `polarity_markers` check, upgrade `kicad/scripts/pcb/assembly.py` `SK-001`, make `--schematic` optional in `kicad/scripts/fab_release_gate.py`, and refine `kicad/SKILL.md` triggers + `references/pdf-schematic-extraction.md` raster sketch guidance.
