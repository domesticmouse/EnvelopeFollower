# JLCPCB Production & Ordering Notes — 6 HP Eurorack Envelope Follower

Complete fabrication, assembly (PCBA), and post-PCBA manual assembly instructions for ordering both boards of the **6 HP Eurorack Envelope Follower (`REV 1.0`)** at JLCPCB:

1. **Main Circuit Board (PCB + Single-Sided Economic PCBA):** [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb)
2. **6 HP Eurorack Front Panel (Bare PCB Only, No PCBA):** [`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb)

---

## 1. Upload Files & Archive Contents

Place these as **two separate PCB items** in your JLCPCB cart (only the main circuit board uses PCB Assembly):

| Cart Item | Source KiCad PCB | Gerber ZIP (Upload in PCB Quote) | BOM CSV (PCBA Upload) | CPL CSV (PCBA Upload) | Assembly Mode |
|---|---|---|---|---|---|
| **1. Main Circuit Board** | [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) | [`production/EnvelopeFollower_Main.zip`](./production/EnvelopeFollower_Main.zip) | [`jlcpcb_bom.csv`](./jlcpcb_bom.csv) | [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv) | **Economic PCBA — Bottom Side Only** |
| **2. 6 HP Front Panel** | [`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb) | [`production/EnvelopeFollower_Panel.zip`](./production/EnvelopeFollower_Panel.zip) | *None* | *None* | **Bare PCB Only (No PCBA / No Stencil)** |

> **Archive Hygiene Verified:** Neither [`production/EnvelopeFollower_Main.zip`](./production/EnvelopeFollower_Main.zip) nor [`production/EnvelopeFollower_Panel.zip`](./production/EnvelopeFollower_Panel.zip) contains any `_cpl.csv` or `.csv` file. Each ZIP contains exactly **14 manufacturing files** (`F_Cu.gtl`, `B_Cu.gbl`, `F_Paste.gtp`, `B_Paste.gbp`, `F_Silkscreen.gto`, `B_Silkscreen.gbo`, `F_Mask.gts`, `B_Mask.gbs`, `Edge_Cuts.gm1`, `PTH.drl`, `NPTH.drl`, `PTH-drl_map.gbr`, `NPTH-drl_map.gbr`, `-job.gbrjob`). Upload [`jlcpcb_bom.csv`](./jlcpcb_bom.csv) and [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv) separately on JLCPCB's PCBA upload step.

---

## 2. Order 1 — Main Circuit PCB & Economic PCBA ([`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb))

### 2.1 PCB Fabrication Settings (JLCPCB)

| JLCPCB Parameter | Selected Option | Design Basis & Verified Details |
|---|---|---|
| **Base Material** | `FR-4` (`TG130–140`) | Per `B.Fab` fab notes & `.gbrjob` (`FR4` dielectric `1.51 mm`) |
| **Layers** | `2` (`F.Cu`, `B.Cu`) | `2`-layer PCB with full `GND` copper pours on both layers |
| **Dimensions** | `30.0 × 108.0 mm` | `Edge.Cuts`: `X = 0.00–30.00 mm`, `Y = 10.25–118.25 mm` (`30.1 × 108.1 mm` in `.gbrjob` incl. `0.1 mm` edge stroke; exceeds `100 × 100 mm` promo cap so standard 2L pricing applies) |
| **PCB Qty** | `5` (minimum for PCBA) | Minimum assembly order quantity |
| **PCB Thickness** | `1.6 mm` | Matches `.kicad_pcb` `(thickness 1.6)` & `B.Fab` fab notes |
| **Outer Copper Weight** | `1 oz` (`0.035 mm`) | Matches `.gbrjob` & `B.Fab` fab notes (`1oz CU`) |
| **Min Trace / Spacing** | `0.25 mm / 0.20 mm` | Design rules: `0.25 mm` signal, `0.30 mm` power, `0.20 mm` clearance (`0.4571 mm` measured min spacing — standard tier) |
| **Min Via / Hole** | `0.30 mm` drill / `0.60 mm` pad | `119` vias (`0.30 mm`); `53` component PTH holes (`0.75–1.43 mm`, incl. `8 × 1.10 × 1.80 mm` plated oval slots for `RV1`–`RV4` tabs); `0` NPTH holes |
| **Solder Mask Color** | **Black** | Per `B.Fab` fab notes (`SOLDER MASK: BLACK`) |
| **Silkscreen Color** | **White** | Per `B.Fab` fab notes (`SILK: WHITE`) |
| **Surface Finish** | **ENIG** or **Lead-Free HASL** | Per `B.Fab` notes (`FINISH: ENIG / HASL-LF`). **HASL-LF** is lowest cost and suitable for `1.27 mm` SOIC-14 / `0603`; **ENIG** gives optimal pad flatness |
| **Via Covering** | **Tented** | `.kicad_pcb` sets `(tenting (front yes) (back yes))` |
| **Confirm Production File** | `No` (or `Yes` if manual review desired) | Clean `0`-violation DRC & verified Gerbers |
| **Remove Order Number** | **Specify a Location** *(Recommended)* | **Replace the `5.0 × 5.0 mm` `B.SilkS` solid square with a JLCPCB QR code** (see Section 4 below) |
| **Castellated Holes / Impedance / Gold Fingers** | `No` | None used |

### 2.2 PCB Assembly (PCBA) Settings & BOM/CPL Upload

- **Enable PCB Assembly:** `Yes`
- **PCBA Type:** **Economic** (all `44` SMDs are `0603`, `2512`, `SOIC-14`, `SOD-123`, `SOT-23`, and `6.3×5.4 mm` SMD electrolytic — within Economic constraints)
- **Assembly Side:** **Bottom Side (`B.Cu`)** (`100%` of assembled SMDs live on `B.Cu`; `F.Cu` has zero SMDs and `EnvelopeFollower-F_Paste.gtp` is intentionally empty)
- **Tooling Holes:** Added by JLCPCB (or order-specific rail); `3 × B.Cu` optical fiducials are already placed on the PCB (`FID1` at `(2.20, 12.20)`, `FID2` at `(27.80, 12.20)`, `FID3` at `(27.80, 115.60)` with `1.0 mm` Cu / `2.0 mm` mask opening, excluded from BOM/CPL).
- **BOM File:** [`jlcpcb_bom.csv`](./jlcpcb_bom.csv) (`17` unique LCSC lines, `44` components total):
  - **14 Basic lines (`$0` feeder fee):** `R1`–`R13`, `R15`, `R17`, `R18`, `R20`, `R21`, `R24`, `R25`, `R27` (`0603` resistors), `C5`–`C11` (`0603` capacitors), `D1`–`D3`, `D10` (`1N4148W`), `D5`–`D6` (`B5819W`), `D7`–`D9` (`BAV99`).
  - **3 Extended lines (`3 × $3.00 = $9.00` setup fee):** `U1`, `U2` (`TL074HIDR`, `C2878713`), `R16`, `R19`, `R26` (`1k 1W 2512`, `C54315`), `C3`, `C4` (`22uF 50V CP_Elec_6.3x5.4`, `C2836438`).
- **CPL File:** [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv)
  - Generated via `kicad-cli pcb export pos --side back --smd-only --exclude-dnp --format csv --units mm` and converted to the exact 7-column JLCPCB header `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` with `Layer=Bottom`.
  - Uses KiCad's standard Gerber-aligned mm coordinate frame (`Mid X` in `[0, 30]`, `Mid Y` in `[-118.25, -10.25]`) without `--bottom-negate-x`.
  - **44/44 1:1 Designator Parity Confirmed:** Contains **only** the `44` populated `B.Cu` SMDs matching [`jlcpcb_bom.csv`](./jlcpcb_bom.csv). Zero `TP*` (`TP1`–`TP8`), zero `FID*` (`FID1`–`FID3`), zero `RV*` (`RV1`–`RV4`), zero `J*` (`J1`–`J4`), zero `D4`, zero `C1`, zero `C2`.

### 2.3 CRITICAL: JLCPCB Online Placement & Polarity/Rotation Verification

In JLCPCB's web preview (**Component Placement** step), verify every polarized and multi-pin component below against its `B.SilkS` Pin-1 dot, external `0.25 mm` cathode bar, or `+`/`-` marking (see [`analysis/bottom.png`](./analysis/bottom.png)). Because JLCPCB's tape-and-reel `0°` convention differs from KiCad on several package families (for example, `SOT-23` typically `+180°`, `SOIC` typically `+90°` or `+270°`, `SOD-123` / diodes typically `+180°`), adjust the `Rotation` column in [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv) (or rotate directly in JLCPCB's interactive placement viewer) if any part preview disagrees with the board markings below:

| Ref(s) | Part / LCSC # | Package | CPL `Rotation` (KiCad) | Physical Pin-1 / Polarity Verification on Board (`B.Cu` / `B.SilkS`) |
|---|---|---|---|---|
| `U1` | `TL074HIDR` (`C2878713`) | `SOIC-14` | `0.000000` | `Pin 1` (`V_AMP`) at `(-2.47, +3.81)` mm relative to center (`X=12.53, Y=20.41`); **bottom-right** in rear view (`bottom.png`), marked by `B.SilkS` Pin-1 dot |
| `U2` | `TL074HIDR` (`C2878713`) | `SOIC-14` | `180.000000` | `Pin 1` (`V_INV_PRE`) at `(+2.48, -3.81)` mm relative to center (`X=16.18, Y=70.79`); **top-left** in rear view (`bottom.png`), marked by `B.SilkS` Pin-1 dot |
| `C3` | `22uF 50V` (`C2836438`) | `CP_Elec_6.3x5.4` | `0.000000` | **Positive (`Pin 1`, `+12V`)** at `(-2.80, 0.00)` mm (`X=21.60`); **Negative (`Pin 2`, `GND`)** at `(+2.80, 0.00)` mm (`X=27.20`). Marked `+` / `-` on `B.SilkS` |
| `C4` | `22uF 50V` (`C2836438`) | `CP_Elec_6.3x5.4` | `0.000000` | **CRITICAL `-12V` POLARITY:** **Positive (`Pin 1`, `GND`)** at `(-2.80, 0.00)` mm (`X=2.80`); **Negative (`Pin 2`, `-12V`)** at `(+2.80, 0.00)` mm (`X=8.40`). Marked `+` below `Pin 1` and `-` right of `Pin 2` on `B.SilkS` |
| `D1` | `1N4148W` (`C81598`) | `SOD-123` | `0.000000` | **Cathode (`Pin 1`, `U1B_IN_M`)** at `(-1.65, 0.00)` mm (`X=6.35`), marked by external `B.SilkS` cathode bar |
| `D2` | `1N4148W` (`C81598`) | `SOD-123` | `180.000000` | **Cathode (`Pin 1`, `U1B_OUT`)** at `(+1.65, 0.00)` mm (`X=5.65`), marked by external `B.SilkS` cathode bar |
| `D3` | `1N4148W` (`C81598`) | `SOD-123` | `180.000000` | **Cathode (`Pin 1`, `ATK_IN`)** at `(+1.65, 0.00)` mm (`X=18.25`), marked by external `B.SilkS` cathode bar |
| `D5` | `B5819W` (`C8598`) | `SOD-123` | `0.000000` | **Cathode (`Pin 1`, `+12V`)** at `(-1.65, 0.00)` mm (`X=19.15`); `Pin 2 (A)` = `+12V_IN` |
| `D6` | `B5819W` (`C8598`) | `SOD-123` | `180.000000` | **Opposite to `D5`:** **Cathode (`Pin 1`, `-12V_IN`)** at `(+1.65, 0.00)` mm (`X=11.65`); `Pin 2 (A)` = `-12V` |
| `D10` | `1N4148W` (`C81598`) | `SOD-123` | `-90.000000` | **Cathode (`Pin 1`, `LED_A`)** at `(0.00, -1.65)` mm (`Y=63.35`, top pad), marked by horizontal `B.SilkS` cathode bar |
| `D7`–`D9` | `BAV99` (`C2500`) | `SOT-23` | `0.000000` | `Pin 1` (`-12V`) at `(-0.94, +0.95)` mm, `Pin 2` (`+12V`) at `(-0.94, -0.95)` mm, `Pin 3` (`signal`) at `(+0.94, 0.00)` mm; `B.SilkS` Pin-1 dot beside `Pin 1` |

---

## 3. Order 2 — 6 HP Eurorack Front Panel ([`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb))

### 3.1 PCB Fabrication Settings (JLCPCB — Bare PCB Only)

| JLCPCB Parameter | Selected Option | Design Basis & Verified Details |
|---|---|---|
| **Upload Archive** | [`production/EnvelopeFollower_Panel.zip`](./production/EnvelopeFollower_Panel.zip) | `14` files; **do NOT upload BOM/CPL** and **do NOT enable PCBA or Stencil** |
| **Base Material** | `FR-4` (`TG130–140`) | `2`-layer FR4 with grounded `F.Cu` & `B.Cu` EMI/chassis shield pours |
| **Layers** | `2` (`F.Cu`, `B.Cu`) | Mated to `F.Cu` of main board via `10.5 mm` hardware standoff |
| **Dimensions** | `30.0 × 128.5 mm` | `6 HP × 3U` Doepfer A-100 (`30.05 × 128.55 mm` in `.gbrjob`; exceeds `100 × 100 mm` promo cap) |
| **PCB Qty** | `5` (minimum bare PCB qty) | Match main PCB quantity |
| **PCB Thickness** | `1.6 mm` *(or `2.0 mm` FR4)* | `.gbrjob` specifies `1.6 mm`; `2.0 mm` FR4 is also valid if extra panel stiffness is desired |
| **Outer Copper Weight** | `1 oz` (`0.035 mm`) | Matches `.gbrjob` |
| **Solder Mask Color** | **Black** *(Matte Black recommended for front panel)* | Crisp Eurorack faceplate contrast; matches main PCB aesthetic |
| **Silkscreen Color** | **White** | Top (`F.SilkS`) panel labels + bottom (`B.SilkS`) `ENV FOLLOW 6HP` & QR box |
| **Surface Finish** | **ENIG** *(recommended)* or **Lead-Free HASL** | `F.Mask` tents over front jack/pot copper rings; `B.Mask` exposes `8.6 mm` (`J1`–`J3`) & `9.6 mm` (`RV1`–`RV4`) `GND` pads on the rear for chassis bonding |
| **Drills (`10` holes total)** | `7` PTH + `3` NPTH | PTH: `3 × 6.2 mm` (`J1`–`J3`), `4 × 7.2 mm` (`RV1`–`RV4`); NPTH: `1 × 3.2 mm` circular (`D4` LED @ `(22.0, 65.0)`), `2 × 3.2 × 5.5 mm` oval M3 slots (`H1` @ `(7.5, 3.0)`, `H2` @ `(7.5, 125.5)`) |
| **Remove Order Number** | **Specify a Location** *(Mandatory for clean panel face)* | **Replace the `5.0 × 5.0 mm` `B.SilkS` square on the rear with a JLCPCB QR code** so zero order text appears on the front (`F.SilkS`) face |

---

## 4. Replacing the `5 × 5 mm` `B.SilkS` Squares with a JLCPCB QR Code

Both [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) and [`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb) include pre-reserved, copper/via-free **`5.0 × 5.0 mm` filled silkscreen squares** on **`B.SilkS`** (`*-B_Silkscreen.gbo`) specifically for JLCPCB's order-tracking QR code replacement:

| Board | Layer | Square Bounds (KiCad mm) | Center (KiCad / Gerber mm) | Board Location | JLCPCB Ordering Instruction / PCB Remark |
|---|---|---|---|---|---|
| **Main PCB** ([`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb)) | `B.SilkS` | `(12.50, 98.80)` to `(17.50, 103.80)` | `(15.00, +101.30)` / `(15.00, -101.30)` | Bottom-center power corridor between `C3`/`C4`, above `J4` (`0` vias, `0` tracks inside `±0.5 mm`) | Under **Remove Order Number**, select **"Specify a location"** (and/or add **PCB Remark**): *"Replace the 5x5mm filled silkscreen square on Bottom Silkscreen (B.SilkS / .gbo) at X=15.0mm, Y=-101.3mm with JLCPCB order QR code. Do NOT alter the vertical polarity stripe beside J4 or add order text elsewhere."* |
| **Front Panel** ([`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb)) | `B.SilkS` | `(12.50, 106.50)` to `(17.50, 111.50)` | `(15.00, +109.00)` / `(15.00, -109.00)` | Rear bottom center below `ENV FOLLOW 6HP` (`Y=102.5`) and above `H2` (`Y=125.5`) | Under **Remove Order Number**, select **"Specify a location"** (and/or add **PCB Remark**): *"Replace the 5x5mm filled silkscreen square on Bottom Silkscreen (B.SilkS / .gbo) at X=15.0mm, Y=-109.0mm with JLCPCB order QR code. Keep Front Silkscreen (F.SilkS / .gto) 100% free of JLCPCB order numbers."* |

*(Note: [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) also contains a matching `5.0 × 5.0 mm` copper/via-free `F.SilkS` square at `(12.50, 98.80)–(17.50, 103.80)`; request the QR code on `B.SilkS` for single-sided bottom PCBA tracking. On the main PCB, do not confuse the `5 × 5 mm` QR square with the `0.8 × 5.6 mm` `J4` `-12V RED` polarity stripe bar at `(3.22, 108.20)–(4.02, 113.80)`.)*

---

## 5. Pre-Order Verification Summary

All fabrication exports and checks were executed and verified locally in this workspace:

| Check | Target | Result | Report / Details |
|---|---|---|---|
| **Main Gerber & Drill Analysis** | [`production/main/`](./production/main/) | **PASS** (`0` errors, `1` benign warning) | [`analysis/main_gerbers.json`](./analysis/main_gerbers.json): `9/9` expected layers (`complete: true`, `aligned: true`), `172` PTH holes (`119` `0.30 mm` vias + `53` component holes), `0` NPTH holes. Benign `GR-004` (`warning`, heuristic) compares `115` `B.Paste` flashes to `290` total `B.Cu` flashes (`40%`), where `290 = 115 SMDPad + 53 THT ComponentPad + 119 ViaPad + 3 FiducialPad` — i.e., `115/115` (**100%**) SMD paste coverage |
| **Panel Gerber & Drill Analysis** | [`production/panel/`](./production/panel/) | **PASS** (`0` findings) | [`analysis/panel_gerbers.json`](./analysis/panel_gerbers.json): `9/9` expected layers (`complete: true`, `aligned: true`), `0` errors / `0` warnings / `0` info, `10` holes (`7` PTH + `3` NPTH) |
| **Main PCB DRC & Silkscreen** | [`EnvelopeFollower.kicad_pcb`](./EnvelopeFollower.kicad_pcb) | **PASS** | [`analysis/drc.json`](./analysis/drc.json): `0` violations, `0` unconnected items; `silk_annotator.py --inspect`: `RESULT: PASS` (`63/63` labeled, `0` overlaps, `0` keepout hits, `0` QR via/track hits) |
| **Panel PCB DRC** | [`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb) | **PASS** | [`panel/panel_drc.json`](./panel/panel_drc.json): `0` unconnected items, `0` geometry/clearance violations (`10` expected `lib_footprint_issues` warnings for inline `Eurorack_Panel` library references) |
| **BOM / CPL 1:1 Parity** | [`jlcpcb_bom.csv`](./jlcpcb_bom.csv) vs [`production/main/EnvelopeFollower_cpl.csv`](./production/main/EnvelopeFollower_cpl.csv) | **PASS (`44/44`)** | Exact 7-column JLCPCB header `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer`, `Layer=Bottom` for all `44` rows, zero `TP*`/`FID*`/`RV*`/`J*`/`D4`/`C1`/`C2`, excluded from both ZIP archives |

---

## 6. Post-PCBA Manual Assembly & Bring-Up Checklist

After receiving the `B.Cu`-assembled main PCBs and bare `6 HP` panels from JLCPCB (for complete part numbers and bring-up steps, see [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md) and [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md)):

1. **Inspect PCBA Board:** Visually verify `D5` vs `D6` opposite cathode orientation, `C4` reversed electrolytic orientation (`+` toward `GND`, `-` toward `-12V`), `C3` orientation, and `U1`/`U2`/`D7`–`D9` Pin-1 dots before adding THT parts.
2. **Solder Rear (`B.Cu`) THT Components:**
   - `C1`, `C2`: `1 µF 63 V` `P=5.0 mm` metallized polyester film capacitors (`C328852`).
   - `J4`: `2×5` `2.54 mm` keyed Eurorack box header (`C53207560`), aligning key notch per `B.SilkS` outline and `-12V RED` stripe at Pins `1–2`.
   - *(Optional)* `TP1`–`TP8`: `RH-5001` test loops (`C5199801`) mounted on **`B.Cu` only** (keep `F.Cu` flush so panel clearance is preserved), or leave as bare `1.0 mm` plated probe pads.
3. **Fit & Solder Front (`F.Cu`) Panel Controls:**
   - Dry-fit `J1`–`J3` (`WQP-PJ398SM` jacks), `RV1`–`RV4` (`A100k`, `A50k`, `A1M`, `B10k` 9 mm vertical pots), and `D4` (`3 mm` LED `C85161` — square Pad `1` = Cathode `-` / flat side) into `F.Cu` **without soldering**.
   - Place the [`panel/EnvelopeFollower_Panel.kicad_pcb`](./panel/EnvelopeFollower_Panel.kicad_pcb) faceplate over the shafts/bushings/LED lens (`~10.5 mm` standoff), lightly tighten the jack/pot nuts to register all parts coaxially, verify `D4` sits cleanly inside its `3.2 mm` NPTH hole, then solder `J1`–`J3`, `RV1`–`RV4`, and `D4` from `B.Cu`.
4. **Power-Up Verification:** Clip ground to `TP1` (`GND`) on a current-limited `±12 V` bench supply (`~15–25 mA`), verify `+11.65 V ± 0.1 V` at `TP2` and `-11.65 V ± 0.1 V` at `TP3`, confirm `D4` is dark at idle, and step through `TP4`–`TP8` per [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md).
