# EnvelopeFollower Tutorial Test-Drive Audit Report

**Date:** 2026-11-21  
**Scope:** Clean-room end-to-end replay of Stages 1–7 ([`docs/tutorial/`](./docs/tutorial/)) inside isolated `stages/stage-1/` … `stages/stage-7/` directories, paired with per-prompt `/agy-customizations` skill-improvement audits (summarized in [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md)).

The clean-room tutorial test drive completed end to end across **Stages 1–7** with zero repository contamination outside `stages/`, zero `NO_LIB` netlist entries, zero Stage 4 ERC errors/warnings, zero Stage 5/6 DRC violations (even under `--severity-all` on the main PCB), verified Stage 7 JLCPCB manufacturing archives, and zero mutations to installed `.agents/skills/` (`diff -rq -x __pycache__` clean).

---

## 1. Stage-by-Stage Gate Summary

| Stage | Status | Key Gate Metrics & Outcomes |
| :--- | :--- | :--- |
| **Stage 1** ([`stage-1-agent-skills.md`](./docs/tutorial/stage-1-agent-skills.md)) | **PASS** | Installed `9/9` copied skills into [`stages/stage-1/.agents/skills/`](./stages/stage-1/.agents/skills/) + [`skills-lock.json`](./stages/stage-1/skills-lock.json) (`0` symlinks, `10/10` helper scripts/docs, `check-stage1` & `check-clean-root` exit `0`). Both `npx skills add` calls ran cleanly without extra `-y`/`--agent` flags (`BypassSandbox: true` required for npm network access). |
| **Stage 2** ([`stage-2-circuit-upgrades.md`](./docs/tutorial/stage-2-circuit-upgrades.md)) | **PASS** | Downloaded valid WebP [`EnvelopeFollower.webp`](./stages/stage-2/EnvelopeFollower.webp) (`1551×1019`); extracted `6` op-amp stages, `23` resistors, `4` caps, `4` pots, `3× 1N4148`, `1× LED`, `3` jacks into [`EnvelopeFollower.md`](./stages/stage-2/EnvelopeFollower.md); added analog critiques (`Path A`/`Path B`) + all `5` Eurorack protections in [`EnvelopeFollowerImprovements.md`](./stages/stage-2/EnvelopeFollowerImprovements.md). Verified `C4` (`+` → `GND`, `-` → `-12V`) and `D1`–`D3` orientations. |
| **Stage 3** ([`stage-3-bom-and-dfm.md`](./docs/tutorial/stage-3-bom-and-dfm.md)) | **PASS (with notes)** | Created [`EnvelopeFollowerImproved.md`](./stages/stage-3/EnvelopeFollowerImproved.md), [`EnvelopeFollowerBOM.md`](./stages/stage-3/EnvelopeFollowerBOM.md), [`EnvelopeFollowerExplanation.md`](./stages/stage-3/EnvelopeFollowerExplanation.md), and [`SilkscreenInstructions.md`](./stages/stage-3/SilkscreenInstructions.md). `20` SMT lines (`49` `B.Cu` parts) + `3` rear `B.Cu` THT parts (`J4`, `C1`, `C2`) + `8` `DNP` `TP1`–`TP8` (`Ronghe RH-5001` `C5199801`) + `D4` (`C85161`) verified live with **`0` `PENDING_VERIFY`**. Steps 3.1 and 3.3b paused cleanly for user `BypassSandbox: true` approvals on JLCPCB/LCSC lookups before completing. |
| **Stage 4** ([`stage-4-skidl.md`](./docs/tutorial/stage-4-skidl.md)) | **PASS** | `check-stage4` exit `0`: `ERC()` clean (`0` errors/warnings); [`envelope_follower.net`](./stages/stage-4/envelope_follower.net) has `68` netlist comps (`49` SMT + `11` THT + `8` `DNP` TPs), `39` named nets (+`NC`, `170` total pins), `0` `NO_LIB`, `8` `dnp`, `61` `LCSC` fields, `68` `Silkscreen` fields; [`jlcpcb_bom.csv`](./stages/stage-4/jlcpcb_bom.csv) has `20` lines (`49` SMD parts); `ruff check` & `ruff format --check` clean; `check-clean-root` exit `0` (`os.chdir` before `from skidl`). |
| **Stage 5** ([`stage-5-schematic-and-pcb.md`](./docs/tutorial/stage-5-schematic-and-pcb.md)) | **PASS (with notes)** | Step 5.1 added `FID1`–`FID3` / `TP1`–`TP8` `exclude_from_pos_files` + `dnp` and `QR_BOX` via keepout after initial check; Step 5.2 Audit + Fix removed hardcoded label overrides in favor of netlist `Silkscreen` fields (`TP2 -12V_PROT`, `J4 -12V RED`), fixed `U1`/`U2`/`J4`/`C3`/`C4`/`RV1`–`RV4` `.Fab`/mask/edge clearances, and seeded THT `.Fab` + `B.Mask` margins. Final [`EnvelopeFollower.kicad_pcb`](./stages/stage-5/EnvelopeFollower.kicad_pcb): DRC (`--refill-zones --severity-all`) **`0` violations / `0` unconnected**; `silk_annotator.py --inspect` **`RESULT: PASS`** (`68/68` labeled, `0` overlaps/keepout/tether/split hits); `analyze_pcb.py --full` **`0` errors**, `39/39` nets routed (`498` tracks, `100` vias, `2` zones); `pcb export pos` = `49` SMDs (`0` `FID`/`TP`); `ruff` clean; 3D renders verified. |
| **Stage 6** ([`stage-6-front-panel.md`](./docs/tutorial/stage-6-front-panel.md)) | **PASS** | Generated [`EnvelopeFollower_Panel.kicad_pcb`](./stages/stage-6/panel/EnvelopeFollower_Panel.kicad_pcb) (`30.0 × 128.5 mm`) and [`EnvelopeFollower_Panel.zip`](./stages/stage-6/production/EnvelopeFollower_Panel.zip). KiCad DRC: `0` non-library violations (`10` expected `lib_footprint_issues` warnings only), `0` unconnected; `analyze_pcb.py`: `0` errors, `0` warnings; `analyze_gerbers.py`: `0` findings (`9/9` layers, `aligned: True`); 3D renders confirmed `ENV FOLLOW`, `6HP ANALOG`, `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, unboxed `ENV`, `OUT`, `INV OUT`, `5 × 5 mm` `B.SilkS` QR square, and zero `JLCJLCJLC` (no Step 6.2 QR fix needed). |
| **Stage 7** ([`stage-7-manufacturing.md`](./docs/tutorial/stage-7-manufacturing.md)) | **PASS** | `check-stage7` exit `0`; `analyze_gerbers.py` on [`production/main/`](./stages/stage-7/production/main/): **`0` errors**, `9/9` Gerber layers, `aligned: True`, **`0` `F.Paste` flashes**, **`125` `B.Paste` flashes** (`125/125` SMD pads covered; `1` benign `GR-004` warning vs `281` `B.Cu` flashes); [`EnvelopeFollower_cpl.csv`](./stages/stage-7/production/main/EnvelopeFollower_cpl.csv) has `49` `Bottom` SMD rows matching `jlcpcb_bom.csv` `49/49` (`0` orphan/missing); both ZIPs exclude CPL (`14` files each); `check-clean-root` exit `0` (`0` `.git` inside `stages/`). |

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

- **Part & Net Counts (`71` footprints / `39` named nets vs. reference `62` footprints / `36` nets):**
  - **Populated (`60`):** `49` `B.Cu` SMT (`15` Basic lines / `39` parts + `1` Preferred Extended line `R14` + `4` Extended lines / `9` parts) + `3` `B.Cu` manual THT (`J4`, `C1`, `C2`) + `8` `F.Cu` panel THT (`J1`–`J3`, `RV1`–`RV4`, `D4`).
  - **Unpopulated / Fiducials (`11`):** `8` `DNP` `TP1`–`TP8` (`Ronghe RH-5001` `C5199801`) + `3` `B.Cu` optical fiducials (`FID1`–`FID3`, marked `dnp` / `exclude_from_pos_files` / `exclude_from_bom`).
- **Op-Amp & Signal Topology (`2 × TL074HIDR` `C2878713`):**
  - **`U1A` High-Z Non-Inverting Attenuator (`Z_in ≈ 113 kΩ`):** Input clamp `R1 = 10 kΩ` + `D9` (`BAT54S`) placed *ahead* of `C1` (`1 µF 63 V` THT film `C328852`, `f_c = 1.41 Hz`), driving `RV1 = A100k` log attenuator + `R2 = 4.7 kΩ` gain floor + `R3 = 1 MΩ` open-wiper pull-down into fixed `+11×` `U1A` (`R4 = 10 kΩ`, `R5 = 100 kΩ || C9 = 22 pF C0G C1653`) for `+0.45×` to `+10.04×`.
  - **`U1B`, `U1C` `1.00×` Precision Rectifier:** Uses `10 kΩ` (`R6`, `R7`, `R9`) and `20 kΩ` (`R8`, `R10`, `C4184`) with `D1`/`D2` (`1N4148WS`, `SOD-323` `C2128`).
  - **`U2C`, `U2D` Active Zero-Deadzone Peak Detector & Buffer:** `U2C` drives `D3` (`1N4148WS`) inside feedback with `D5` anti-saturation clamp, `R11 = 200 kΩ` (`C25811`) / `C10 = 100 pF` `C0G` (`C14858`), `R12 = 150 Ω` (`C22808`), `RV2 = A50k`, `C2` (`1 µF 63 V` film `C328852`), `R13 = 10 kΩ`, `RV3 = A1M || R14 = 4.7 MΩ` (`C23163`), and `U2D` unity buffer.
  - **`U1D`, `U2A`, `U2B` Output, Inverter & Constant-Current LED:** `U1D` (`0.975×` diff amp, `R15`/`R16`/`R19`/`R20 = 100 kΩ`, `RV4 = B10k`, `R17`/`R18 = 6.8 kΩ` `C23212`), `U2A` (`-1.00×`), `D10`/`D11` (`BAT54S`, `C47546`) behind `R21`/`R24` (`1 kΩ 1 W 2512` `C54315`), and `U2B` (`0.5 mA/V` constant-current LED driver with `D6` `1N4148WS` reverse clamp + `R27 = 1 kΩ`).
  - **Power Entry (`J4`):** Shrouded `2×5` `J4` (`C53207560`) + `D7`/`D8` (`1N5819WS`, `C191023` Basic) + `R28`/`R29` (`10 Ω`, `C22859`) + `C3`/`C4` (`47 µF 35 V`, `C2836440`) + `C5`–`C8` (`100 nF 50 V` X7R `C14663`).
- **Mechanical Layout (`30.00 × 108.00 mm`):** `2 × 4` two-column `F.Cu` panel control layout (`Alps RD901F`, `X = 7.25 / 22.75 mm`, `Y = 16.50, 37.00, 64.00, 82.00 mm`) instead of the reference single-column `29.60 × 107.00 mm` board, and `TP1`–`TP8` mapped to `+12V_PROT`, `-12V_PROT`, `GND`, `V_GAIN`, `V_RECT`, `V_ENV_BUF`, `V_OUT_BUF`, and `V_INV_BUF`.
- **BOM Cost ([`EnvelopeFollowerBOM.md`](./stages/stage-7/EnvelopeFollowerBOM.md)):**
  - `B.Cu` SMT (`20` lines, `49` parts): **`$0.8755`/board** + `$12.00` (`4 × $3.00` Extended feeder fees); `B.Cu` manual THT (`J4`, `C1`, `C2`): `$0.6555`/board; `F.Cu` `D4` LED: `$0.0360`/board.

---

## 4. Tutorial & Skill Findings

1. **Updated Stage 3 & Stage 5 Prompts Held Cleanly:** The recent edits to `stage-3-bom-and-dfm.md` (`B.Cu` single-sided PCBA guidance) and `stage-5-schematic-and-pcb.md` (netlist-driven silkscreen/audit phrasing) worked as intended—Stage 3 placed all SMDs, `J4`, `C1`/`C2`, and `TP1`–`TP8` on `B.Cu` upfront with zero side-flip rework in Stage 5, and Step 5.2 audited clean-room designators (`J4`, `D7`–`D11`, `C3`/`C4` `47uF`, `TP1`–`TP8`) cleanly.
2. **Skill-Level Gaps Surfaced via `/agy-customizations`:** Full per-prompt skill improvement findings (`4 High`, `10 Medium`, `8 Low` across `22` deduplicated items) are cataloged in [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md), including:
   - `pcbnew_layout_template.py` missing `SetExcludedFromPosFiles(True)` (`FID1`–`FID3` leaked into initial Step 5.1 CPL until caught) and missing SKiDL 3.0.0 valueless `(property (name "dnp"))`.
   - `bom/scripts/translate_bom_pnp.py pnp` dropping `Val`/`Package` and emitting `Layer=B` instead of JLCPCB's 7-column `Layer=Bottom` schema.
   - `silk_annotator.py` omitting THT `.Fab` body keepouts, mask margins, `Edge.Cuts` stroke inset, and `PCB_SHAPE` silk/QR-via checks (all caught in Stage 5 Step 5.2a/b).
   - `analyze_gerbers.py` `GR-004` (`125 vs 281 = 44%`) and `reader.py` `polarity_markers` false warnings, `sexp.py` Python 3.9 crash, `jlcpcb/SKILL.md` `"Top only"` misstatement, and `eurorack-panel/SKILL.md` `/tmp/` PNG `read_file` timeout.

---

## 5. Recommended Next Actions

1. Review the prioritized upstream PR checklist in [`SkillImprovementAuditReport.md`](./SkillImprovementAuditReport.md) for [`domesticmouse/skills`](https://github.com/domesticmouse/skills/tree/main/packs/hardware) and [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy).
2. Before ordering PCBs at JLCPCB, follow [`stages/stage-7/OrderingNotes.md`](./stages/stage-7/OrderingNotes.md) to verify `SOIC-14`, `SOT-23`, `SOD-323`, and `CP_Elec_6.3x5.4` part rotations/polarities in JLCPCB's interactive 3D Placement Preview and enable **Mark on PCB → Specify a location** for the `5 × 5 mm` `B.SilkS` QR code square on both boards.
