# JLCPCB Fabrication & Assembly Ordering Notes

Ordering, upload, QR-code placement, and CPL rotation-verification guide for both PCBs in the **6 HP ±12 V Eurorack Envelope Follower** (`REV 1.0`):

1. **Main Circuit Board**: [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) — 2-layer PCB + **JLCPCB Economic Single-Sided Bottom (`B.Cu`) SMT PCBA**
2. **Mated 3U Front Panel**: [`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb) — 2-layer bare PCB only (no BOM/CPL upload)

---

## 1. Ready-to-Upload Fabrication & Assembly Files

| Artifact | Path | Upload Step | Contents / Notes |
|---|---|---|---|
| **Main PCB Gerbers** | [`production/EnvelopeFollower_Main.zip`](./production/EnvelopeFollower_Main.zip) | Main PCB Quote (`Gerber Upload`) | `14` files from [`production/main/`](./production/main/): `9` Gerber layers (`F.Cu`, `B.Cu`, `F.Paste`, `B.Paste`, `F.SilkS`, `B.SilkS`, `F.Mask`, `B.Mask`, `Edge.Cuts`), `2` Excellon drill files (`PTH.drl`, `NPTH.drl`), `2` GerberX2 drill maps, and `EnvelopeFollower-job.gbrjob`. **Excludes `_cpl.csv`.** |
| **Main PCBA BOM** | [`jlcpcb_bom.csv`](./jlcpcb_bom.csv) | Main PCB Assembly (`Add BOM`) | `19` unique SMT lines (`49` total components: `14` Basic lines / `33` pcs + `5` Extended lines / `16` pcs). Format: `Comment,Designator,Footprint,LCSC Part #`. Excludes THT parts and DNP `TP1`–`TP8` / `FID1`–`FID3`. |
| **Main PCBA CPL** | [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv) | Main PCB Assembly (`Add CPL`) | `49` SMT rows matching `jlcpcb_bom.csv` 1:1. Format: `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` with **`Layer=Bottom`**, coordinates in `mm`, and rotations normalized to `[0°, 360°)`. |
| **Front Panel Gerbers** | [`production/EnvelopeFollower_Panel.zip`](./production/EnvelopeFollower_Panel.zip) | Separate Bare PCB Quote (`Gerber Upload`) | `14` files from [`production/panel/`](./production/panel/): `9` Gerber layers, `2` Excellon drill files (`PTH.drl`, `NPTH.drl`), `2` GerberX2 drill maps, and `EnvelopeFollower_Panel-job.gbrjob`. |

> **Important Side Assignment Note:** Unlike early planning drafts that assumed top-side SMT placement, the routed [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) places **all `49` SMT components and all `3` optical fiducials (`FID1`–`FID3`) strictly on the Bottom side (`B.Cu`)** so the front face (`F.Cu`) sits cleanly behind the `3U` front panel (`~10.5 mm` standoff) with only front-panel THT controls (`J1`–`J3`, `RV1`–`RV4`, `D4`). Always select **Assembly Side = Bottom Side** in JLCPCB's PCBA configurator.

---

## 2. JLCPCB Order Settings

### 2.1 Main PCB (`EnvelopeFollower.kicad_pcb`)

| Parameter | Setting | Source / Basis |
|---|---|---|
| **Gerber Archive** | [`production/EnvelopeFollower_Main.zip`](./production/EnvelopeFollower_Main.zip) | `30.00 × 108.00 mm` `Edge.Cuts` (`.gbrjob` `30.10 × 108.10 mm`) |
| **Layers / Material** | `2` Layers, `FR-4` | `F.Cu` / `B.Cu` |
| **PCB Thickness** | `1.6 mm` | `.kicad_pcb` general thickness + `B.Fab` notes |
| **Copper Weight** | `1 oz` (`35 µm`) | `.gbrjob` stackup + `B.Fab` notes |
| **PCB Color (Solder Mask)** | **Black** | Matches `B.Fab` fabrication notes (`SOLDER MASK: BLACK`) |
| **Silkscreen** | **White** | Matches `B.Fab` fabrication notes (`SILK: WHITE`) |
| **Surface Finish** | **LeadFree HASL** (budget) or **ENIG** (recommended for flat fine-pitch `SOIC-14` / probe pads) | Both permitted by `B.Fab` notes (`FINISH: ENIG / HASL-LF`) |
| **Confirm Production File** | **Yes** (recommended for first run) | Ensures JLCPCB engineers verify bottom-side CPL polarity before reflow |
| **PCB Assembly** | **Enable — Economic PCBA** | Single-sided SMT (`Layer=Bottom`), `5` boards minimum recommended |
| **Assembly Side** | **Bottom Side** (`B.Cu`) | `49` SMDs + `3` fiducials (`FID1`–`FID3`) on `B.Cu`; `F.Paste` intentionally has `0` pads |
| **Tooling Holes** | Added by JLCPCB (or panel edges if panelized by JLCPCB) | `3` optical fiducials (`1.0 mm` copper / `2.0 mm` mask) are already on `B.Cu` |
| **BOM / CPL Upload** | [`jlcpcb_bom.csv`](./jlcpcb_bom.csv) + [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv) | `49/49` designator parity; `0` orphan rows |
| **JLCPCB QR Code Placement** | **Specify Location — replace `5 × 5 mm` `B.SilkS` square** | See §3 below |

### 2.2 Front Panel (`panel/EnvelopeFollower_Panel.kicad_pcb`)

| Parameter | Setting | Source / Basis |
|---|---|---|
| **Gerber Archive** | [`production/EnvelopeFollower_Panel.zip`](./production/EnvelopeFollower_Panel.zip) | `30.00 × 128.50 mm` `Edge.Cuts` (`.gbrjob` `30.05 × 128.55 mm`), `6 HP` `3U` |
| **Layers / Material** | `2` Layers, `FR-4` | Grounded `F.Cu` & `B.Cu` shield planes |
| **PCB Thickness** | `1.6 mm` *(or `2.0 mm` aluminum/FR-4 if desired; designed for `1.6 mm` FR-4)* | `.kicad_pcb` general thickness |
| **Copper Weight** | `1 oz` (`35 µm`) | `.gbrjob` stackup |
| **PCB Color (Solder Mask)** | **Black** *(matte black recommended for front panel)* | `F.Mask` tents all `7` jack/pot grounding rings for a clean exterior face |
| **Silkscreen** | **White** | `F.SilkS` front legends + `B.SilkS` rear label & QR square |
| **Surface Finish** | **ENIG** (recommended) or **LeadFree HASL** | `B.Cu` exposes `8.6 mm` / `9.6 mm` `GND` rings under jack/pot nuts |
| **PCB Assembly** | **Off (Bare PCB only)** | `0` SMD parts, `F.Paste`/`B.Paste` empty |
| **Slot / Drill Verification** | Confirm `5.5 × 3.2 mm` M3 oval NPTH slots (`H1`, `H2`, `G85` in `NPTH.drl`) | `7` PTH cutouts (`6.2 mm` / `7.2 mm`) + `3` NPTH (`3.2 mm` LED + `2` M3 slots) |
| **JLCPCB QR Code Placement** | **Specify Location — replace `5 × 5 mm` `B.SilkS` square** | See §3 below |

---

## 3. JLCPCB QR Code Replacement (`5 × 5 mm` `B.SilkS` Square)

Both PCBs contain an explicit, unobstructed **`5.0 × 5.0 mm` solid filled `B.SilkS` square** reserved for JLCPCB's order-tracking QR code. During JLCPCB checkout, under **"Mark on PCB / Order Number / QR Code"**, choose **"Specify Location"** (or leave an order note instructing JLCPCB engineering to **replace the `5 × 5 mm` solid white `B.SilkS` square on the bottom silkscreen with the JLCPCB QR code**) so the QR stamp never overwrites component references or panel hardware markings:

| Board | Layer | Square Bounds (`Edge.Cuts` ref.) | Center (`mm`) | Clearance & Keepout Notes |
|---|---|---|---|---|
| **Main PCB** (`EnvelopeFollower.kicad_pcb`) | `B.SilkS` | `(12.50, 7.80)` to `(17.50, 12.80)` | `(15.00, 10.30)` from top-left `(0, 0)` | Above `ENVELOPE FOLLOWER` title block on `B.SilkS`; via-free, pad-free, and `≥ 0.30 mm` clear of neighboring silkscreen |
| **Front Panel** (`EnvelopeFollower_Panel.kicad_pcb`) | `B.SilkS` | Global `(12.50, 50.25)` to `(17.50, 55.25)` *(panel-local `(12.50, 60.50)` to `(17.50, 65.50)`)* | Global `(15.00, 52.75)` / Panel-local `(15.00, 63.00)` | Centered in open `B.SilkS` space between the `REL`/`OFFSET` pots and `IN`/`ENV` row; clear of all `B.Mask` grounding rings |

*(Note: Do **not** confuse the main PCB's `9.00 × 0.85 mm` solid `B.SilkS` rectangle at `(10.50, 104.00)–(19.50, 104.85)` with the QR square — that bar marks `RED STRIPE / -12V` for `J4` Pins `1–2`.)*

---

## 4. BOM-to-CPL Parity & Rotation Offset Verification

### 4.1 Designator & Metadata Parity (`jlcpcb_bom.csv` vs. `production/main/EnvelopeFollower_cpl.csv`)

- **BOM lines (`jlcpcb_bom.csv`):** `19` lines, **`49` designators** (`14` Basic lines / `33` parts; `5` Extended lines / `16` parts).
- **CPL rows (`production/main/EnvelopeFollower_cpl.csv`):** **`49` rows** (`Layer=Bottom`, exported via `kicad-cli pcb export pos --format csv --units mm --side back --smd-only --exclude-dnp`).
- **Designator parity:** **`49 / 49` exact 1:1 match** (`0` missing from CPL, `0` orphan designators in CPL, `0` `Val`/`Comment` or `Package`/`Footprint` mismatches).
- **Correctly excluded (`22` of `71` total PCB footprints):**
  - `3` bottom-side optical fiducials (`FID1`–`FID3`, marked `DNP` / `exclude_from_bom` / `exclude_from_pos_files`)
  - `8` bottom-side DNP test points (`TP1`–`TP8`, THT & marked `DNP` / `exclude_from_bom` / `exclude_from_pos_files`)
  - `3` bottom-side manual THT parts (`J4`, `C1`, `C2`)
  - `8` top-side manual THT panel parts (`J1`–`J3`, `RV1`–`RV4`, `D4`)

### 4.2 CPL Rotation Offsets & JLCPCB 3D Placement Preview Checklist

`production/main/EnvelopeFollower_cpl.csv` retains KiCad's exported `Layer=Bottom` rotations normalized to `[0°, 360°)` (`-90° → 270°`) without guessing reel-specific offsets. **Because JLCPCB's component reel zero-orientations differ from KiCad library footprints—and because `Layer=Bottom` components may also require a `(180° − Rot)` or `180°` bottom-view check depending on JLCPCB's parser—inspect every asymmetrical/polarized part in JLCPCB's 3D/CPL Placement Viewer before paying and adjust rotations in the viewer if needed:**

| Ref(s) | LCSC # | Package | KiCad CPL `Rotation` | Physical Pin-1 / Polarity Marker on `B.Cu` / `B.SilkS` | JLCPCB Offset Check (`jlcpcb/SKILL.md` & `SilkscreenInstructions.md`) |
|---|---|---|---:|---|---|
| **`U1`** | `C2878713` (`TL074H`) | `SOIC-14_3.9x8.7mm_P1.27mm` | `90°` | Pin `1` (`PREAMP_OUT`) at `(9.31, 32.68)` — **bottom-left** in rear `B.SilkS` view, marked by solid `r=0.25 mm` dot | **Likely `+90°` or `+270°`** (check Pin-1 bevel/dot matches `B.SilkS` dot) |
| **`U2`** | `C2878713` (`TL074H`) | `SOIC-14_3.9x8.7mm_P1.27mm` | `0°` | Pin `1` (`U2A_OUT`) at `(19.08, 63.86)` — **bottom-right** in rear `B.SilkS` view, marked by solid `r=0.25 mm` dot | **Likely `+90°` or `+270°`** (check Pin-1 bevel/dot matches `B.SilkS` dot) |
| **`D1_D2`** | `C47546` (`BAT54S`) | `SOT-23` | `0°` | Pin `1` (`A1`, `RECT_HW`) at `(16.06, 34.35)`; Pin `3` (`COM`) at `(17.94, 33.40)` — single pin facing left in rear view, Pin-1 dot marked | **Likely `+180°`** (verify 1-pin `COM` vs 2-pin side and Pin-1 dot) |
| **`D_IN`** | `C2500` (`BAV99`) | `SOT-23` | `90°` | Pin `1` (`A1`, `-12V`) at `(12.55, 65.84)`; Pin `3` (`COM`) at `(11.60, 63.96)` — single pin facing top in rear view, Pin-1 dot marked | **Likely `+180°`** (verify `COM` toward top & Pin-1 dot) |
| **`D_OUT`** | `C2500` (`BAV99`) | `SOT-23` | `90°` | Pin `1` (`A1`, `-12V`) at `(23.15, 71.79)`; Pin `3` (`COM`) at `(22.20, 69.91)` — single pin facing top in rear view, Pin-1 dot marked | **Likely `+180°`** (verify `COM` toward top & Pin-1 dot) |
| **`D_INV_OUT`** | `C2500` (`BAV99`) | `SOT-23` | `0°` | Pin `1` (`A1`, `-12V`) at `(9.86, 80.25)`; Pin `3` (`COM`) at `(11.74, 79.30)` — single pin facing left in rear view, Pin-1 dot marked | **Likely `+180°`** (verify `COM` toward left & Pin-1 dot) |
| **`D_PWR_P`** | `C8598` (`B5819W`) | `D_SOD-123` | `270°` | Pad `1` (`K`, `+12V_PROT`) at `(27.60, 88.35)` — **cathode bar at TOP** (`-Y`) | Verify diode cathode band matches `0.25 mm` `B.SilkS` cathode bar at **top** |
| **`D_PWR_N`** | `C8598` (`B5819W`) | `D_SOD-123` | `90°` | Pad `1` (`K`, `-12V_IN`) at `(2.40, 91.25)` — **cathode bar at BOTTOM** (`+Y`, opposite `D_PWR_P`) | Verify diode cathode band matches `0.25 mm` `B.SilkS` cathode bar at **bottom** |
| **`D3`** | `C2128` (`1N4148WS`) | `D_SOD-323` | `0°` | Pad `1` (`K`, `ATK_IN`) at `(22.95, 2.10)` — **cathode bar at RIGHT** in rear view (`-X`) | Verify diode cathode band matches `0.25 mm` `B.SilkS` cathode bar at **right** |
| **`D_LED_CLAMP`** | `C2128` (`1N4148WS`) | `D_SOD-323` | `90°` | Pad `1` (`K`, `U2B_OUT`) at `(14.60, 72.30)` — **cathode bar at BOTTOM** (`+Y`) | Verify diode cathode band matches `0.25 mm` `B.SilkS` cathode bar at **bottom** |
| **`C3`** | `C2836438` (`22uF 50V`) | `CP_Elec_6.3x5.4` | `270°` | Pad `1` (`+`, `+12V`) at `(25.60, 95.70)` — **`+` chamfer at TOP**, black `-` half-moon (`GND`) at bottom | Verify `+` chamfer faces **top** (`B.SilkS` `+` mark) and black band faces bottom |
| **`C4`** | `C2836438` (`22uF 50V`) | `CP_Elec_6.3x5.4` | `270°` | Pad `1` (`+`, `GND`) at `(4.40, 97.00)` — **`+` chamfer at TOP**, black `-` half-moon (`-12V`) at bottom | Verify `+` chamfer faces **top** (`B.SilkS` `+` mark) and black band faces bottom |
| **37 Passives** (`R*`, `C_DEC*`, `C_HF`, `C_OUT*`) | Basic / `C95204` / `C333193` | `0603` / `1206` / `1210` | `0°`, `90°`, `180°`, `270°` | Non-polarized chip resistors & MLCCs | Verify in 2D/3D preview that bodies span their pads (not rotated `90°` across pads) |

*(Tip: `C4` is on the `-12 V` rail, so its **`+`** terminal connects to **`GND`** and its **`-`** terminal connects to **`-12V`**. Both `C3` and `C4` intentionally face with `+` toward the top of the board.)*

---

## 5. Automated Gerber & DRC Verification Summary

| Check | Target | Result | Details |
|---|---|---|---|
| **Gerber Analyzer (`analyze_gerbers.py`)** | [`production/main/`](./production/main/) | **0 errors, 1 warning (`GR-004` heuristic)** | `11` Gerber files + `2` Excellon drill files, `complete: true`, `aligned: true`, `Edge.Cuts` closed (`30.0 × 108.0 mm`), `265` PTH holes (`212` × `0.3 mm` vias + `53` THT component holes across `7` tool sizes), `0` NPTH holes. `GR-004` ("B paste layer: 126 flashes vs 394 copper (32%)") is an expected false positive: `B.Cu` has `126` `SMDPad` + `212` `ViaPad` + `53` `ComponentPad` + `3` `FiducialPad` = `394` flashes, while `B.Paste` properly pastes **all `126/126` (`100%`) SMD pads only** (`F.Paste` has `0` flashes). |
| **Gerber Analyzer (`analyze_gerbers.py`)** | [`production/panel/`](./production/panel/) | **0 errors, 0 warnings** | `11` Gerber files + `2` Excellon drill files, `complete: true`, `aligned: true`, `Edge.Cuts` closed (`30.0 × 128.5 mm`), `10` total holes (`3` × `6.2 mm` jack PTH + `4` × `7.2 mm` pot PTH + `1` × `3.2 mm` LED NPTH + `2` × `5.5 × 3.2 mm` M3 NPTH slots). |
| **KiCad DRC (`kicad-cli pcb drc`)** | [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) | **0 violations, 0 unconnected** | Verified with `--refill-zones`. |
| **Silkscreen Audit (`silk_annotator.py`)** | [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) | **`RESULT: PASS`** | `68/68` non-fiducial footprints labeled, `0` overlaps, `0` keepout/pad hits, `0` tether drift, `0` split pairs. |

---

## 6. Post-PCBA Manual Assembly Sequence (Upon Delivery)

1. **Rear-Side (`B.Cu`) THT Parts:** Solder `C1`, `C2` (`1 µF 100 V` `P=5mm` box film, non-polarized, LCSC `C125397`) and `J4` (`2×5` shrouded keyed header, LCSC `C53207560`, key aligned per shroud/Pin-1 triangle next to the `RED STRIPE / -12V` bar) on `B.Cu`. Leave `TP1`–`TP8` unpopulated (bare probe pads) unless installing optional `RH-5001` (`C5199801`) test pins.
2. **Front-Panel (`F.Cu`) Mechanical Alignment & Soldering:** Insert `J1`–`J3` (`WQP-PJ398SM`), `RV1` (`A100k`), `RV2` (`A50k`), `RV3` (`A1M`), `RV4` (`B10k`), and `D4` (`3 mm` red LED, long lead = `+` / short flat = `-` toward `B.SilkS`/`F.SilkS` markers) onto `F.Cu` **without soldering**, seat [`EnvelopeFollower_Panel`](./panel/EnvelopeFollower_Panel.kicad_pcb) over the shafts/bushings/LED, tighten the jack/pot nuts gently so every part sits flush and square to the panel, and **then** solder `J1`–`J3`, `RV1`–`RV4`, and `D4` on `B.Cu`.
