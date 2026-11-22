# Complete Build & Verification Checklist

End-to-end master checklist tying all four engineering phases to the verified deliverables in [`EnvelopeFollowerWithSkewLimiter`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter) (`4a02c46`). For detailed bench/ordering steps, follow [`checklists/`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/main/checklists) (`01`, `01b`, `02`–`05`).

---

## Phase 1: SKiDL Netlist & `9`-Section Schematic Parity

- [x] **SKiDL Circuit & Project Library (`envelope_follower.py`):**
  - [x] `fp-lib-table` & `footprints/Eurorack_Custom.pretty/SW_Toggle_SPDT_Dailywell_2MS1.kicad_mod` configured (`5.2 mm` drill, multi-layer `F.Cu`/`B.Cu`/`*.Mask` annular rings).
  - [x] `erc_assert` electrical checks + SKiDL `ERC()` pass (`80` netlist components, `48` active nets, explicit `NC` flags on `SW1.1`, `SW2.1`, `J3.TN`, `J4.TN`).
  - [x] `jlcpcb_bom.csv` exported with **`50` SMDs across `17` rows** and strictly **`3` Extended SKUs** (`C2878713` `TL074HIDR`, `C83935` `BAT54S`, `C95204` `10k 0.1%`).
- [x] **Structured Schematic (`generate_schematic.py` -> `envelope_follower.kicad_sch`):**
  - [x] `9` labeled functional blocks matching A3 landscape sheet layout (Sections `1`–`9`, `U1A`–`U1E`/`U2A`–`U2E`).
  - [x] `kicad-cli sch erc` passes cleanly (`0` errors, `0` warnings) and 4-layer netlist parity matches `build_circuit()` without `dnp_prefixes`.
  - [x] Visual inspection via Pillow crops confirms readable labels and zero overlapping text across all `9` sections.

---

## Phase 2: Main PCB Layout, Routing & Hybrid Silkscreen Polish

- [x] **Board Geometry & Placement (`generate_kicad_pcb.py` -> `envelope_follower.kicad_pcb`):**
  - [x] `30.00 × 108.00 mm` 2-layer FR-4 outline (`GridOrigin` / `AuxOrigin` = `(100.00, 40.00) mm`).
  - [x] **`83` footprints placed:** `11` `F.Cu` panel controls (`RV1`–`RV4` on `15.50 mm` vertical pitch, `SW1`–`SW2`, `LED1`, `J1`–`J4`), `50` `B.Cu` SMDs, `7` `B.Cu` THT parts (`C1`, `C2`, `C7`, `C11`–`C13`, `J_PWR`), `12` DNP Keystone test points (`TP1`–`TP12`), and `3` bare-copper `B.Cu` fiducials (`FID1`–`FID3`).
  - [x] Cross-layer clearance check (`verify_placements()`) passes with zero `B.Cu` bodies obstructing `F.Cu` panel shells or vice versa.
- [x] **Routing, Zones & DRC:**
  - [x] `703` trace segments + `133` vias (`48` nets) avoiding `0` acute traps, plus `F.Cu`/`B.Cu` filled `GND` zones (`HitTestFilledArea` verified).
  - [x] `kicad-cli pcb drc --severity-all --refill-zones` passes with `0` errors, `0` warnings, `0` unconnected items, and `0` schematic parity mismatches.
- [x] **Hybrid Silkscreen Co-Editing (`silk_layout.json` + `/edit-silkscreen`):**
  - [x] Pinned layout synchronized via `--sync-silk` and verified via `--check-silk` (`--show-silk` bottom X-flipped previews + generated PDF inspection).
  - [x] `5.0 × 5.0 mm` JLCPCB QR placeholder placed on `F.SilkS` (`X = 23.8–28.8 mm, Y = 1.0–6.0 mm`); heavy `0.8 mm` `-12V` bar beside `J_PWR`; dual-sided `+` on `LED1` + `2-PIN R/G` / `TAYDA A-1076`; off-board `B.Fab` notes (`Y = 108 + 5.0 mm`).

---

## Phase 3: Mated `6 HP` Matte Black + ENIG Front Panel

- [x] **Blank-Front Cutouts & Spec (`generate_eurorack_panel.py --blank-front`):**
  - [x] `30.00 × 128.50 mm` panel (`AuxOrigin` = `(100.00, 29.75) mm`, symmetrical `10.25 mm` Y overhang) with `panel_svg_spec.md` contract exported.
  - [x] Cutouts verified: `4× 7.20 mm` pot PTH (`RV1`–`RV4`), `2× 5.20 mm` sub-mini toggle PTH (`SW1`–`SW2` for Dailywell `2MS1`), `4× 6.20 mm` jack PTH (`J1`–`J4`), `1× 3.20 mm` `LED1` NPTH, and `2× 5.50 × 3.20 mm` M3 oval NPTH mounting slots (`H1`, `H2`).
  - [x] `5` mirrored `B.SilkS` items placed collision-free by 2D SDF planner (stacked 3-line title/rev, rotated repo URL, `5.0 × 5.0 mm` rear QR blank at `(22.50, 121.00)`).
- [x] **Dark Techno / Brutalist Artwork (`vectorcraft-cli` -> `panel_art/`):**
  - [x] Batch generation (`--emit-commands`, `vectorcraft-cli run --commands`, `--postprocess-verify`) passes `40 px/mm` (`1016 PPI`) clearance audit (`>= 0.60 mm` ink-to-mask separation, `0` `<text>`/stroked nodes, `0 px` inside nut/edge/rail/bezel keepouts).
  - [x] `preview_clean.png` and `preview_keepouts.png` visually signed off.
- [x] **KiCad 10 Panel Import (`panel_art/import_svgs_to_kicad.py` -> `envelope_follower_panel.kicad_pcb`):**
  - [x] Compound glyphs (`O`, `A`, `R`, `D`, `0`, output knock-out pills) fractured via `SHAPE_POLY_SET.BooleanXor()` + `Fracture()` into `104` `F.SilkS` polygons and `33` `F.Mask` gold openings.
  - [x] `(stackup ...)` injected (`Black` mask, `White` silk, `ENIG`), `F.Cu`/`B.Cu` `~95%` `GND` zones refilled, `kicad-cli pcb drc` passes with `0` non-library violations (`13` expected `lib_footprint_issues` filtered), and `images/panel_front.png` + `panel_back.png` verified.

---

## Phase 4: Dual-Board Manufacturing, Interactive BOM & Bench Bring-Up

- [x] **Fabrication Packages (`manufacturing/`):**
  - [x] Main board (`envelope_follower_gerbers.zip`, separated `PTH`/`NPTH` drills, `manufacturing/jlcpcb_cpl.csv` `50/50` bottom SMD parity).
  - [x] Front panel (`envelope_follower_panel_gerbers.zip`, `--excellon-oval-format route` for `H1`/`H2` slots).
  - [x] `analyze_gerbers.py` clean (`125/125` `B.Paste` flashes matching `50` SMDs; `0` panel findings).
- [x] **THT Interactive BOM (`bom/ibom.html`):**
  - [x] Exported via `InteractiveHtmlBom v2.11.1+` filtered (`Board variant field = JLCPCB_Class`, `Variants whitelist = Manual THT`) to **`14` rows / `18` THT parts**.
- [ ] **JLCPCB Cart & Viewer Sign-Off ([`01-main-board-ordering.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/01-main-board-ordering.md), [`01b-front-panel-ordering.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/01b-front-panel-ordering.md), [`02-pcba-part-alignment.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/02-pcba-part-alignment.md)):**
  - [ ] Upload `envelope_follower_gerbers.zip`, `jlcpcb_bom.csv` (`3` Extended SKUs confirmed), and `jlcpcb_cpl.csv` (`LeadFree HASL` or `ENIG-RoHS`, `SAC305`, `F.SilkS` QR location, Bottom Side Economic PCBA).
  - [ ] Inspect every SMD part in JLCPCB's 2D/3D Bottom viewer against dual `back=(X, Y)` / `board=(X, Y)` coordinates (`U1`, `U2`, `D1`–`D5` orientations confirmed).
  - [ ] Add `envelope_follower_panel_gerbers.zip` to the **same JLCPCB cart** (`Matte Black`, `White` silk, **`ENIG-RoHS`**, bare PCB, QR restricted to `B.SilkS`).
- [ ] **Tayda Parts, Hand Assembly & Bench Bring-Up ([`03-tayda-ordering.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/03-tayda-ordering.md), [`04-hand-assembly.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/04-hand-assembly.md), [`05-board-bringup.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/05-board-bringup.md)):**
  - [ ] Order all `18` manual THT components (`<= 14.0 mm` knobs for `15.50 mm` pot pitch; check `A-1855`/`A-1672`/`A-8401` shaft style).
  - [ ] Solder `B.Cu` parts first (`J_PWR` notch right, **`C1`/`C2` opposite polarities**, `C7`, `C11`–`C13`), trim `F.Cu` leads flush, `5 V + 1 kΩ` bench-test `LED1` (`A-1076`), snap pot anti-rotation tabs, dry-fit Matte Black + ENIG panel with nylon M3 washers, solder `11` panel controls, and scrub high-Z nodes (`U2A.3`, `C11`–`C13`, `SW2`) with IPA.
  - [ ] Cold resistance checks -> `±12 V` current-limited (`40–50 mA`) power-up (`SW1` DOWN = `RAW/OFF`, `SW2` DOWN = `FAST`) -> verify all `12` test points (`TP1`–`TP12`) and musical `SLEW IN` / kick-ducking patches.
