# EnvelopeFollower Tutorial Test-Drive Audit Report

**Date:** 2026-11-21  
**Scope:** Clean-room end-to-end replay of Stages 1–7 ([`docs/tutorial/`](./docs/tutorial/)) inside isolated `stages/stage-1/` … `stages/stage-7/` directories.

The clean-room tutorial test drive completed end to end across **Stages 1–7** with zero repository contamination outside `stages/`, zero `NO_LIB` netlist entries, zero Stage 4 ERC errors/warnings, zero Stage 5/6 DRC violations, and verified Stage 7 JLCPCB manufacturing archives.

---

## 1. Stage-by-Stage Gate Summary

| Stage | Status | Key Gate Metrics & Outcomes |
| :--- | :--- | :--- |
| **Stage 1** ([`stage-1-agent-skills.md`](./docs/tutorial/stage-1-agent-skills.md)) | **PASS (with notes)** | Installed `9/9` copied skills into [`stages/stage-1/.agents/skills/`](./stages/stage-1/.agents/skills/) + [`skills-lock.json`](./stages/stage-1/skills-lock.json) (`0` symlinks, `10/10` helper scripts/docs, `check-stage1` & `check-clean-root` exit `0`). First `npx` attempt hit an initial 60s approval timeout before user-approved retry succeeded without extra `-y`/`--agent` flags. |
| **Stage 2** ([`stage-2-circuit-upgrades.md`](./docs/tutorial/stage-2-circuit-upgrades.md)) | **PASS** | Downloaded valid WebP [`EnvelopeFollower.webp`](./stages/stage-2/EnvelopeFollower.webp) (`1551×1019`); extracted `6` op-amp stages, `23` resistors, `4` caps, `4` pots, `3× 1N4148`, `1× LED`, `3` jacks into [`EnvelopeFollower.md`](./stages/stage-2/EnvelopeFollower.md); added analog critiques + all `5` Eurorack protections in [`EnvelopeFollowerImprovements.md`](./stages/stage-2/EnvelopeFollowerImprovements.md). Verified `C4` (`+` → `GND`, `-` → `-12V`) and `D1`–`D3` orientations. |
| **Stage 3** ([`stage-3-bom-and-dfm.md`](./docs/tutorial/stage-3-bom-and-dfm.md)) | **PASS (with notes)** | Created [`EnvelopeFollowerImproved.md`](./stages/stage-3/EnvelopeFollowerImproved.md), [`EnvelopeFollowerBOM.md`](./stages/stage-3/EnvelopeFollowerBOM.md), [`EnvelopeFollowerExplanation.md`](./stages/stage-3/EnvelopeFollowerExplanation.md), and [`SilkscreenInstructions.md`](./stages/stage-3/SilkscreenInstructions.md). `19` SMT lines (`49` parts) + `3` LCSC THT lines + `TP1`–`TP8` (`Ronghe RH-5001` `C5199801`, `DNP`) verified live with **0 `PENDING_VERIFY`**. Stage 3 defaulted SMT placement to `F.Cu`, later reconciled to `B.Cu` in Stage 5. |
| **Stage 4** ([`stage-4-skidl.md`](./docs/tutorial/stage-4-skidl.md)) | **PASS** | `check-stage4` exit `0`: `ERC()` clean (`0` errors/warnings, `9` `erc_assert()` checks passed); [`envelope_follower.net`](./stages/stage-4/envelope_follower.net) has `71` comps (`49` SMT + `11` THT + `8` `DNP` TPs + `3` fiducials), `42` nets, `0` `NO_LIB`, `68` `Silkscreen` fields; [`jlcpcb_bom.csv`](./stages/stage-4/jlcpcb_bom.csv) has `19` lines (`49` SMD parts); `ruff` clean; `check-clean-root` exit `0` (`os.chdir` before `from skidl`). |
| **Stage 5** ([`stage-5-schematic-and-pcb.md`](./docs/tutorial/stage-5-schematic-and-pcb.md)) | **PASS (with notes)** | Required Step 5.1b side correction (`F.Cu` SMT → `B.Cu` SMT + `FID1`–`FID3` `exclude_from_pos_files`/`dnp` + via-free QR) and Step 5.2 audit/fix (`J4` `RED STRIPE / -12V` bar, `SOT-23` Pin-1 clearances, `RV2` Pin `1`, `B.Fab` bounds + `TP` `DNP`, QR margin). Final checks on [`EnvelopeFollower.kicad_pcb`](./stages/stage-5/EnvelopeFollower.kicad_pcb): DRC **`0` violations / `0` unconnected**; `silk_annotator.py --inspect` **`RESULT: PASS`** (`68/68` labeled, `0` overlaps/keepout/tether/split hits); `analyze_pcb.py --full` **`0` errors**, `42/42` nets routed, `100%` `B.Fab` notes; `ruff` clean. |
| **Stage 6** ([`stage-6-front-panel.md`](./docs/tutorial/stage-6-front-panel.md)) | **PASS** | Generated [`EnvelopeFollower_Panel.kicad_pcb`](./stages/stage-6/panel/EnvelopeFollower_Panel.kicad_pcb) (`30.0 × 128.5 mm`) and [`EnvelopeFollower_Panel.zip`](./stages/stage-6/production/EnvelopeFollower_Panel.zip). KiCad DRC: `0` non-library violations (`10` expected `lib_footprint_issues` warnings only), `0` unconnected; `analyze_pcb.py`: `0` errors, `0` warnings; `analyze_gerbers.py`: `0` findings (`9/9` layers, `aligned: True`); 3D renders confirmed `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `ENV`, `OUT`, unboxed `INV OUT`, `5 × 5 mm` `B.SilkS` QR square, and zero `JLCJLCJLC`. |
| **Stage 7** ([`stage-7-manufacturing.md`](./docs/tutorial/stage-7-manufacturing.md)) | **PASS** | `check-stage7` exit `0`; `analyze_gerbers.py` on [`production/main/`](./stages/stage-7/production/main/): **`0` errors**, `9/9` Gerber layers, `aligned: True`, **`0` `F.Paste` flashes**, **`126` `B.Paste` flashes**; [`EnvelopeFollower_cpl.csv`](./stages/stage-7/production/main/EnvelopeFollower_cpl.csv) has `49` `Bottom` SMD rows matching `jlcpcb_bom.csv` `49/49` (`0` orphan/missing); both ZIPs exclude CPL (`14` files each); `check-clean-root` clean (`0` `.git` inside `stages/`). |

---

## 2. Generated Artifacts Inventory

### Stage Snapshots
- [`stages/stage-1/`](./stages/stage-1/) — `9` hardware skills + [`skills-lock.json`](./stages/stage-1/skills-lock.json)
- [`stages/stage-2/`](./stages/stage-2/) — [`EnvelopeFollower.webp`](./stages/stage-2/EnvelopeFollower.webp), [`EnvelopeFollower.md`](./stages/stage-2/EnvelopeFollower.md), [`EnvelopeFollowerImprovements.md`](./stages/stage-2/EnvelopeFollowerImprovements.md)
- [`stages/stage-3/`](./stages/stage-3/) — [`EnvelopeFollowerImproved.md`](./stages/stage-3/EnvelopeFollowerImproved.md), [`EnvelopeFollowerBOM.md`](./stages/stage-3/EnvelopeFollowerBOM.md), [`EnvelopeFollowerExplanation.md`](./stages/stage-3/EnvelopeFollowerExplanation.md), [`SilkscreenInstructions.md`](./stages/stage-3/SilkscreenInstructions.md)
- [`stages/stage-4/`](./stages/stage-4/) — [`envelope_follower.py`](./stages/stage-4/envelope_follower.py), [`envelope_follower_sklib.py`](./stages/stage-4/envelope_follower_sklib.py), [`envelope_follower.erc`](./stages/stage-4/envelope_follower.erc), [`envelope_follower.net`](./stages/stage-4/envelope_follower.net), [`envelope_follower_bom.xml`](./stages/stage-4/envelope_follower_bom.xml), [`jlcpcb_bom.csv`](./stages/stage-4/jlcpcb_bom.csv)
- [`stages/stage-5/`](./stages/stage-5/) — [`generate_kicad_pcb.py`](./stages/stage-5/generate_kicad_pcb.py), [`EnvelopeFollower.kicad_pcb`](./stages/stage-5/EnvelopeFollower.kicad_pcb)
- [`stages/stage-6/`](./stages/stage-6/) — [`panel/EnvelopeFollower_Panel.kicad_pcb`](./stages/stage-6/panel/EnvelopeFollower_Panel.kicad_pcb), [`production/panel/`](./stages/stage-6/production/panel/), [`production/EnvelopeFollower_Panel.zip`](./stages/stage-6/production/EnvelopeFollower_Panel.zip)
- [`stages/stage-7/`](./stages/stage-7/) — Final complete manufacturing workspace

### Final Stage 7 Manufacturing Deliverables
- **Main PCB:** [`stages/stage-7/EnvelopeFollower.kicad_pcb`](./stages/stage-7/EnvelopeFollower.kicad_pcb)
- **Front Panel PCB:** [`stages/stage-7/panel/EnvelopeFollower_Panel.kicad_pcb`](./stages/stage-7/panel/EnvelopeFollower_Panel.kicad_pcb)
- **Main Gerber ZIP:** [`stages/stage-7/production/EnvelopeFollower_Main.zip`](./stages/stage-7/production/EnvelopeFollower_Main.zip)
- **Panel Gerber ZIP:** [`stages/stage-7/production/EnvelopeFollower_Panel.zip`](./stages/stage-7/production/EnvelopeFollower_Panel.zip)
- **JLCPCB SMT BOM:** [`stages/stage-7/jlcpcb_bom.csv`](./stages/stage-7/jlcpcb_bom.csv)
- **JLCPCB Bottom CPL:** [`stages/stage-7/production/main/EnvelopeFollower_cpl.csv`](./stages/stage-7/production/main/EnvelopeFollower_cpl.csv)
- **Ordering Guide:** [`stages/stage-7/OrderingNotes.md`](./stages/stage-7/OrderingNotes.md)

---

## 3. Clean-Room Architectural Divergences

- **Part & Net Counts (`71` footprints / `42` nets vs. reference `62` footprints / `36` nets):**
  - **Populated:** `49` SMT (`14` Basic lines / `33` parts + `5` Extended lines / `16` parts) + `11` manual/consigned THT (`C1`/`C2`, `J4`, `D4`, `J1`–`J3`, `RV1`–`RV4`), plus `8` `DNP` `TP1`–`TP8` (`RH-5001` `C5199801`) and `3` `B.Cu` optical fiducials (`FID1`–`FID3`, also marked `DNP` / `exclude_from_pos_files` / `exclude_from_bom`).
- **Op-Amp Allocation (`U2C`/`U2D`):**
  - Clean-room build used `U2C` as the active zero-deadzone peak detector (`D3` `1N4148WS` inside `U2C` loop, no `D7` catch diode, `R_ATK_MIN = 470 Ω` `0603` Basic) and **`U2D` as a `101 kΩ` unity input buffer** (with `J1.TN → GND`, `R_IN_PROT = 1 kΩ`, `R_IN_BUF = 1 kΩ`, `D_IN` `BAV99`) rather than an `ENV_NODE` buffer.
  - Because `ENV_NODE` lacks a dedicated buffer, `TP1`–`TP8` deliberately excluded `ENV_NODE`, mapping `TP4`–`TP8` to `IN_BUF`, `PREAMP_OUT`, `RECT_OUT`, `OUT_CLAMP`, and `INV_OUT_CLAMP`.
- **Component Variants & Protections:**
  - **Rectifier:** `BAT54S` (`D1_D2`, `C47546`) instead of discrete `1N4148W` (`D1`/`D2`), plus `7 × 10 kΩ ±0.1%` (`C95204`, `R4+R5 = 20 kΩ` and `R8A+R8B = 20 kΩ`).
  - **Output Clamps & Clash Resistors:** `BAV99` (`D_IN`, `D_OUT`, `D_INV_OUT`, `C2500` Basic) indexed by physical pin numbers `[1, 2, 3]`, paired with split `470 Ω + 470 Ω` `0.5 W` `1210` clash resistors (`R16A/B`, `R19A/B`, `C333193`) with in-loop feedback (`R15`/`R18`) and `100 pF` `C0G` compensation (`C_OUT1`/`C_OUT2`, `C14858`).
  - **Capacitors & Diodes:** `C1` & `C2` (`1 µF 100 V` TDK `P=5mm` THT PET film `C125397`, mounted on `B.Cu`) instead of `0603`/`0805` MLCCs; `C3` & `C4` upgraded to `22 µF 50 V` (`C2836438`); `D3` & `D_LED_CLAMP` use `1N4148WS` (`SOD-323`, `C2128`); `R_LED = 2.2 kΩ` (`C4190`); `R_GAIN_FAIL = 1 MΩ` (`C22935`); `OFFSET` uses `RV4 = B10k` with `R11`/`R12 = 1 kΩ`, `R13 = 18 kΩ`, no `C9` wiper cap.
- **Mechanical Layout & Hardware:**
  - Main PCB outline is `30.00 × 108.00 mm` with a `2 × 4` two-column `F.Cu` grid (`Alps RK09K` pot footprints, power header `J4`) instead of `29.60 × 107.00 mm` single-column `Alpha RD901F` + `J_PWR`.
- **BOM Cost ([`EnvelopeFollowerBOM.md`](./stages/stage-7/EnvelopeFollowerBOM.md)):**
  - SMT parts: `$1.0494`/board (`$5.25` per 5 boards) + `$15.00` (`5 × $3.00` Extended feeder fees) vs. reference `~$0.85`/board + `$9.00` (`3 × $3.00`); populated LCSC THT (`C1`/`C2`, `J4`, `D4`): `$0.8259`/board (`$4.13` per 5 boards).

---

## 4. Tutorial Gaps & Prompt Findings

1. **Stage 3 Prompts Omit Bottom-Side (`B.Cu`) Single-Sided PCBA Requirement ([`stage-3-bom-and-dfm.md` L13](./docs/tutorial/stage-3-bom-and-dfm.md#L13), [L76](./docs/tutorial/stage-3-bom-and-dfm.md#L76)):**
   - Because neither Stage 3.1 nor Stage 3.3c mentions placing SMT parts on `B.Cu`, the clean-room agent assigned all `49` SMDs to `F.Cu` in `EnvelopeFollowerImproved.md` and `SilkscreenInstructions.md`, causing Stage 5 Step 5.1 to place SMDs on `F.Cu` despite the Stage 5 prompt asking for `B.Cu` (which would break Stage 7 `--side back --smd-only`).
2. **Stage 5 Prompts Hardcode Designators, Counts & Section Numbers ([`stage-5-schematic-and-pcb.md` L9](./docs/tutorial/stage-5-schematic-and-pcb.md#L9), [L112](./docs/tutorial/stage-5-schematic-and-pcb.md#L112)):**
   - Hardcoded `"45 SMD parts"`, `"J_PWR"`, `"D1–D3/D5–D7"`, and `"SilkscreenInstructions.md Sections 3, 4, and 7 / Section 5"` conflict with clean-room architectures (`49` SMDs, `J4`, `D_PWR_*`/`BAT54S`/`BAV99`, 6-section `SilkscreenInstructions.md`).
3. **Stage 5 & Stage 7 Tooling Pitfalls (`FID*` POS Export, `is_passive_ref`, `GR-004`):**
   - **Fiducials in CPL:** Adding `FID1`–`FID3` with `exclude_from_bom` alone (without `exclude_from_pos_files` / `dnp`) leaks fiducials into `kicad-cli pcb export pos --smd-only --exclude-dnp`.
   - **Suffixed passive regex ([`silk_annotator.py` L46–48](./stages/stage-7/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py#L46-L48)):** `is_passive_ref()` (`^[RC]\d+$`) only matched `19/41` passives (`R1`–`R20`, `C1`–`C4`), under-reporting value-only counts on suffixed refs (`R_PWR_P`, `R16A`, `C_DEC1`, `C_HF`).
   - **Stage 6 DRC exit code `5`:** Raw `kicad-cli pcb drc` flags `10` expected `lib_footprint_issues` warnings on embedded `Eurorack_Panel` footprints (`generate_eurorack_panel.py --drc` filters these cleanly).
   - **Stage 7 `analyze_gerbers.py` `GR-004` warning:** Reports `"B paste layer: 126 flashes vs 394 copper (32%)"` because `B.Cu` copper flashes include `212` vias + `53` THT pads + `3` fiducials (`0` errors; `126/126` SMD pads pasted).
   - **Stage 5 `.venv` missing `ruff`:** Stage 4 installed `skidl` into `.venv` and Stage 5 used system `ruff` (`/opt/homebrew/bin/ruff`) rather than `.venv/bin/ruff`.

---

## 5. Recommended Next Actions

1. **Update Stage 3 prompts ([`stage-3-bom-and-dfm.md` L13](./docs/tutorial/stage-3-bom-and-dfm.md#L13)):** Explicitly specify **Bottom-Side (`B.Cu`) single-sided JLCPCB PCBA** (with `F.Cu` reserved for panel-facing controls) in Step 3.1/3.3c so Stages 3–7 agree without mid-Stage-5 rework.
2. **Generalize Stage 5 prompts ([`stage-5-schematic-and-pcb.md` L9](./docs/tutorial/stage-5-schematic-and-pcb.md#L9), [L112](./docs/tutorial/stage-5-schematic-and-pcb.md#L112)):** Replace hardcoded `"45 SMD parts"`, `"J_PWR"`, `"D1–D3/D5–D7"`, and section numbers with netlist-driven phrasing (e.g., *"the Eurorack power header, `DNP` test points, and all SMD parts"* and *"all polarized component categories in `@SilkscreenInstructions.md`"*).
3. **Optional upstream skill enhancements:** Expand `is_passive_ref()` in `silk_annotator.py` for suffixed passives (`^[RC](?:[0-9]+|[A-Z0-9_]+)$` excluding `RV*`), and remind users/SKiDL templates to set `exclude_from_pos_files` (or `dnp=True`) on optical fiducials `FID*`.
4. **Repository state:** Review `git status --short` for `stages/` and this `AuditReport.md` before deciding what to commit or discard.
