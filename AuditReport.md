# EnvelopeFollower Tutorial Test-Drive Audit Report

**Date:** 2026-11-22  
**Scope:** Clean-room end-to-end replay of Stages 1–7 ([`docs/tutorial/`](./docs/tutorial/)) inside isolated `stages/stage-1/` … `stages/stage-7/` directories, paired with per-prompt read-only `/agy-customizations` skill-improvement audits (summarized in [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md)).

The clean-room tutorial test drive completed end to end across **Stages 1–7** with zero repository contamination outside `stages/`, zero `NO_LIB` netlist entries, zero Stage 4 ERC errors/warnings, zero Stage 5/6 DRC violations (even under `--severity-all` on the main PCB), `14/14` Gerber layer & archive verification across both boards, `44/44` 1:1 BOM-to-CPL parity, and zero mutations across all `228` installed skill files (`diff -rq -x __pycache__` clean).

---

## 1. Stage-by-Stage Gate Summary

| Stage | Status | Key Gate Metrics & Outcomes |
| :--- | :--- | :--- |
| **Stage 1** ([`stage-1-agent-skills.md`](./docs/tutorial/stage-1-agent-skills.md)) | **PASS** | Installed `9/9` copied skills (`domesticmouse/skills` `20567628` + `aklofas/kicad-happy` `6b9767e1`) into [`stages/stage-1/.agents/skills/`](./stages/stage-1/.agents/skills/) + [`skills-lock.json`](./stages/stage-1/skills-lock.json) (`0` symlinks, `10/10` helper scripts/docs, `check-stage1` & `check-clean-root` exit `0`). Command 2 paused cleanly on a 60s `BypassSandbox: true` approval timeout and succeeded on resume. |
| **Stage 2** ([`stage-2-circuit-upgrades.md`](./docs/tutorial/stage-2-circuit-upgrades.md)) | **PASS** | Downloaded valid WebP [`EnvelopeFollower.webp`](./stages/stage-2/EnvelopeFollower.webp) (`1551×1019`); extracted `6` op-amp stages, `23` resistors, `4` caps, `4` pots, `3× 1N4148`, `1× LED`, `3` jacks, and `J4` into [`EnvelopeFollower.md`](./stages/stage-2/EnvelopeFollower.md); added analog critiques (`RV2`/`RV3` reversed pot wiring, `GAIN` taper, `R9`/`R10` math, `OFFSET` loading, peak-detector surge/deadzone, `TN` hazard) + all `5` Eurorack protections in [`EnvelopeFollowerImprovements.md`](./stages/stage-2/EnvelopeFollowerImprovements.md). Verified `C4` (`+` → `GND`, `-` → `-12V`) and `D1`–`D3` orientations. |
| **Stage 3** ([`stage-3-bom-and-dfm.md`](./docs/tutorial/stage-3-bom-and-dfm.md)) | **PASS (with notes)** | Created [`EnvelopeFollowerImproved.md`](./stages/stage-3/EnvelopeFollowerImproved.md), [`EnvelopeFollowerBOM.md`](./stages/stage-3/EnvelopeFollowerBOM.md), [`EnvelopeFollowerExplanation.md`](./stages/stage-3/EnvelopeFollowerExplanation.md), and [`SilkscreenInstructions.md`](./stages/stage-3/SilkscreenInstructions.md). `17` SMT lines (`44` `B.Cu` parts) + `3` rear `B.Cu` THT parts (`J4`, `C1`, `C2`) + `1` `F.Cu` LED (`D4` `C85161`) + `7` consigned `F.Cu` controls + `8` `DNP` `TP1`–`TP8` (`Ronghe RH-5001` `C5199801`) verified live with **`0` `PENDING_VERIFY`**. Step 3.1 Batch 2 (`BypassSandbox: true`) timed out twice on user approval and completed cleanly using live-verified Batch 1 (`jlc_batch1.json`) + consigned panel hardware; Step 3.3b paused cleanly for `C5199801` lookup approval. |
| **Stage 4** ([`stage-4-skidl.md`](./docs/tutorial/stage-4-skidl.md)) | **PASS** | `check-stage4` exit `0`: `ERC()` clean (`0` errors/warnings); [`envelope_follower.net`](./stages/stage-4/envelope_follower.net) has `63` netlist comps (`44` SMT + `11` THT + `8` `DNP` TPs), `37` named nets (`158` pad connections), `0` `NO_LIB`, `8` `dnp`, `56` `LCSC` fields, `63` `Silkscreen` fields; [`jlcpcb_bom.csv`](./stages/stage-4/jlcpcb_bom.csv) has `17` lines (`44` SMD parts); `ruff check --no-cache` & `ruff format --check` clean; `check-clean-root` exit `0` (`os.chdir` before `from skidl`). |
| **Stage 5** ([`stage-5-schematic-and-pcb.md`](./docs/tutorial/stage-5-schematic-and-pcb.md)) | **PASS (with notes)** | Step 5.1 generated [`EnvelopeFollower.kicad_pcb`](./stages/stage-5/EnvelopeFollower.kicad_pcb) (`66` footprints = `63` netlist + `3` `FID1`–`FID3` on `B.Cu`, `30.00 × 108.00 mm`) passing DRC & `silk_annotator.py --inspect` (`RESULT: PASS`) on first pass; Step 5.2a read-only audit caught `C3`/`D4` `90°` `"-"` (`|`), `RV4` `90°` `"1"`, `C4` `+` displaced `0.30 mm` from `TP3` (`-12V`), missing `D4` `B.SilkS` cathode bar & `J4` `F.SilkS` Pin-1 dot, and omitted `DRILL TOL` fab line; Step 5.2b fixed every item. Final verification: DRC (`--refill-zones --severity-all`) **`0` violations / `0` unconnected**; `silk_annotator.py --inspect` **`RESULT: PASS`** (`63/63` labeled, `0` overlaps/keepout/tether/split/QR hits); `analyze_pcb.py --full` **`0` errors**, `37/37` nets routed (`602` tracks, `119` vias, `2` zones), `fab_notes_completeness = 100%`; `cpl_check.csv` = `44` `bottom` SMDs (`0` `TP`/`FID`); `ruff` clean (`py39`); 3D renders verified. |
| **Stage 6** ([`stage-6-front-panel.md`](./docs/tutorial/stage-6-front-panel.md)) | **PASS** | Generated [`EnvelopeFollower_Panel.kicad_pcb`](./stages/stage-6/panel/EnvelopeFollower_Panel.kicad_pcb) (`30.0 × 128.5 mm`) and [`EnvelopeFollower_Panel.zip`](./stages/stage-6/production/EnvelopeFollower_Panel.zip). KiCad DRC: `0` real violations (`10` expected `lib_footprint_issues` warnings only), `0` unconnected; `analyze_pcb.py`: `0` errors, `0` warnings; `analyze_gerbers.py`: `0` findings (`9/9` layers, `aligned: True`); 3D renders confirmed `ENV FOLLOW`, `6HP ANALOG`, `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, unboxed `ENV`, `OUT`, `INV OUT`, `5 × 5 mm` `B.SilkS` QR square, and zero `JLCJLCJLC` (no Step 6.2 needed). |
| **Stage 7** ([`stage-7-manufacturing.md`](./docs/tutorial/stage-7-manufacturing.md)) | **PASS** | `check-stage7` exit `0`; `analyze_gerbers.py` on [`production/main/`](./stages/stage-7/production/main/): **`0` errors**, `9/9` Gerber layers, `aligned: True`, **`0` `F.Paste` flashes**, **`115` `B.Paste` flashes** (`115/115` SMD pads covered; `1` benign `GR-004` warning vs `290` `B.Cu` flashes); [`EnvelopeFollower_cpl.csv`](./stages/stage-7/production/main/EnvelopeFollower_cpl.csv) has `44` `Bottom` SMD rows matching `jlcpcb_bom.csv` `44/44` (`0` orphan/missing); both ZIPs (`14` files each) exclude `_cpl.csv`; `check-clean-root` exit `0` (`0` `.git` inside `stages/`). |

---

## 2. Generated Artifacts Inventory

### Stage Snapshots
- [`stages/stage-1/`](./stages/stage-1/) — `9` hardware skills + [`skills-lock.json`](./stages/stage-1/skills-lock.json)
- [`stages/stage-2/`](./stages/stage-2/) — [`EnvelopeFollower.webp`](./stages/stage-2/EnvelopeFollower.webp), [`EnvelopeFollower.md`](./stages/stage-2/EnvelopeFollower.md), [`EnvelopeFollowerImprovements.md`](./stages/stage-2/EnvelopeFollowerImprovements.md)
- [`stages/stage-3/`](./stages/stage-3/) — [`EnvelopeFollowerImproved.md`](./stages/stage-3/EnvelopeFollowerImproved.md), [`EnvelopeFollowerBOM.md`](./stages/stage-3/EnvelopeFollowerBOM.md), [`EnvelopeFollowerExplanation.md`](./stages/stage-3/EnvelopeFollowerExplanation.md), [`SilkscreenInstructions.md`](./stages/stage-3/SilkscreenInstructions.md)
- [`stages/stage-4/`](./stages/stage-4/) — [`envelope_follower.py`](./stages/stage-4/envelope_follower.py), [`envelope_follower_sklib.py`](./stages/stage-4/envelope_follower_sklib.py), [`envelope_follower.erc`](./stages/stage-4/envelope_follower.erc), [`envelope_follower.net`](./stages/stage-4/envelope_follower.net), [`envelope_follower_bom.xml`](./stages/stage-4/envelope_follower_bom.xml), [`jlcpcb_bom.csv`](./stages/stage-4/jlcpcb_bom.csv)
- [`stages/stage-5/`](./stages/stage-5/) — [`generate_kicad_pcb.py`](./stages/stage-5/generate_kicad_pcb.py), [`EnvelopeFollower.kicad_pcb`](./stages/stage-5/EnvelopeFollower.kicad_pcb), [`analysis/`](./stages/stage-5/analysis/)
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
- **Skill Improvement Audit:** [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md)

---

## 3. Clean-Room Architectural Divergences

- **Part & Net Counts (`66` PCB footprints / `37` nets vs. tutorial reference `71` footprints / `42` nets):**
  - **Populated (`55`):** `44` `B.Cu` SMT (`14` Basic lines + `3` Extended lines) + `3` `B.Cu` manual THT (`J4`, `C1`, `C2`) + `8` `F.Cu` panel THT (`J1`–`J3`, `RV1`–`RV4`, `D4`).
  - **Unpopulated / Fiducials (`11`):** `8` `DNP` `TP1`–`TP8` (`Ronghe RH-5001` `C5199801`) + `3` `B.Cu` optical fiducials (`FID1`–`FID3`, marked `dnp` / `exclude_from_pos_files` / `exclude_from_bom`).
- **Circuit Topology Variants (`2 × TL074HIDR` `C2878713`):**
  - **Input Stage (`U2C`):** Places `R26` (`1 kΩ 1 W` `2512` `C54315`) ahead of `C1` (`1 µF 63 V` PET film `C328852`, `P=5mm`) + `R1` (`100 kΩ`) + `R27` (`10 kΩ`) + `D9` (`BAV99` `C2500`), followed by `U2C` unity buffer feeding `U1A` (`R2 = 10 kΩ`, `R24 = 4.7 kΩ` gain floor, `RV1 = A100k`, `C9 = 22 pF` `C0G`).
  - **Precision Rectifier (`U1B`, `U1C`):** Uses `1N4148W` (`SOD-123` `C81598`) for `D1`/`D2` and `1%` `0603` Basic resistors (`10 kΩ` `C25804` + `R8 = 20 kΩ` `C4184`) instead of `0.1%` thin-film `C95204` and `BAT54S`.
  - **Peak Detector & LED (`U2D`, `U2B`):** `U2D` wraps `D3` (`1N4148W`) in an active zero-deadzone loop into `R25 = 330 Ω`, `RV2 = A50k`, `C2 = 1 µF` film, `R10 = 10 kΩ`, and `RV3 = A1M`, tapping `TP7` directly on `ENV_CAP` with a `10×` (`10 MΩ`) probe note; `U2B` drives `D4` (`3 mm` Yellow-Green `C85161`) via `R21 = 3.3 kΩ` and anti-parallel `D10` (`1N4148W`).
  - **Output & Power (`U1D`, `U2A`, `J4`):** Uses single `1 kΩ 1 W` `2512` (`C54315`) clash resistors `R16`/`R19` behind `D7`/`D8` (`BAV99`), `R11`/`R12 = 1 kΩ`, `RV4 = B10k`, `R13 = 22 kΩ`, `R15 = 10 kΩ`, `C10`/`C11 = 47 pF` `C0G`, and `B5819W SL` (`C8598`) series Schottkys into `22 µF 50 V` (`C2836438`) bulk caps without `10 Ω` series bus resistors.
- **Mechanical Layout (`30.00 × 108.00 mm`):** `2 × 4` front-panel grid using `Alpha RD901F-40-00D` vertical pots (`X = 8.00 / 22.00 mm`, `Y = 25.00, 45.00, 65.00, 85.00 mm` in global panel-aligned coordinates), with `TP1`–`TP8` mapped to `GND`, `+12V`, `-12V`, `IN_BUF`, `V_AMP`, `V_FWR`, `ENV_CAP`, and `V_OUT_PRE`.
- **BOM Cost ([`EnvelopeFollowerBOM.md`](./stages/stage-7/EnvelopeFollowerBOM.md)):**
  - `B.Cu` SMT (`17` lines, `44` parts): **`$0.9078`/board** + `$9.00` (`3 × $3.00` Extended feeder fees); `B.Cu` manual THT (`C1`, `C2`, `J4`): `$0.6555`/board; `F.Cu` `D4` LED: `$0.0364`/board (**`$1.5997`/board** LCSC parts subtotal).

---

## 4. Tutorial Gaps & Prompt Findings

1. **Upstream Hardware-Pack Fixes Confirmed:** Comparing commit `20567628` against the prior `a1d39cf9` baseline showed `kicad-pcbnew-layout` and `kicad-silkscreen-markup` resolved `SetExcludedFromPosFiles(True)`, `get_footprint_field()`, `board_edge_bounds()`, QR keepout checks, and `--severity-all` DRC — Stage 5.1 passed DRC and `--inspect` cleanly on its first generation.
2. **Skill-Level Gaps Surfaced via `/agy-customizations`:** Full per-prompt findings (`6 High`, `13 Medium`, `6 Low` across `25` deduplicated items) are cataloged in [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md), highlighted by:
   - `kicad-silkscreen-markup`: `place_board_label()` rotating `"-"`/`"1"` `90°` into `"|"`, `C4` `"+"` drifting near `TP3` (`-12V`) undetected by `--inspect`, and `add_standard_fab_notes()` overflowing `30 mm` boards.
   - `kicad-pcbnew-layout`: `board.Remove()`/`fp.Remove()` SWIG `SIGSEGV` (`exit 139`) and `os.execv` failing under `python3 -c`.
   - `bom` / `jlcpcb` / `lcsc`: `translate_bom_pnp.py pnp` dropping `Val`/`Package` and emitting `Layer=B`, `search_lcsc.py "RH-5001"` returning a `0402` fuse (`C206947`), `provider_lcsc.py` dropping `encapStandard`, and `jlcpcb/SKILL.md` stating `"Top only"` for Economic PCBA without linking `jlcpcb_search.py`.
   - `kicad`: `signal_detectors.py` missing KiCad `"+"` pins during unused op-amp checks, `reader.py` unconditionally failing `polarity_markers` when `len(polarized) > 3`, `analyze_gerbers.py` `GR-004` (`115/290`) and `copper.py` `CP-002` false positives, and `850`-line `SKILL.md` size.
3. **Minor Clean-Room Notes:** Stage 3 Step 3.1 relied on Batch 1 (`jlc_batch1.json`) + consigned panel hardware after Batch 2 timed out twice awaiting approval (`0` `PENDING_VERIFY`), and Stage 4 avoided an external PDF download timeout while keeping all `63` footprints verified against KiCad 10 `.kicad_mod` files.

---

## 5. Recommended Next Actions

1. Review the prioritized upstream PR checklist in [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md) for [`domesticmouse/skills`](https://github.com/domesticmouse/skills/tree/main/packs/hardware) (`20567628`) and [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (`6b9767e1`).
2. Before submitting Gerbers at JLCPCB, follow [`stages/stage-7/OrderingNotes.md`](./stages/stage-7/OrderingNotes.md) to verify `SOIC-14`, `SOT-23`, `SOD-123`, and `CP_Elec_6.3x5.4` part rotations/polarities in JLCPCB's 3D Placement Preview and enable **Mark on PCB → Specify a location** for the `5.0 × 5.0 mm` `B.SilkS` QR code square on both boards.
