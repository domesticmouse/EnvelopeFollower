# JLCPCB Manufacturing & Ordering Notes — Envelope Follower (6 HP Eurorack)

Complete fabrication, PCBA, and front-panel ordering guide for the **Envelope Follower (`ENVELOPE FOLLOWER Rev 1.0`)** 6 HP Eurorack module, covering both the main circuit board ([EnvelopeFollower.kicad_pcb](./EnvelopeFollower.kicad_pcb)) and the mated 3U aluminum/FR4 shield front panel ([panel/EnvelopeFollower_Panel.kicad_pcb](./panel/EnvelopeFollower_Panel.kicad_pcb)).

---

## 1. Deliverable Inventory & Upload Mapping

| Deliverable | Board | Purpose | JLCPCB Upload Target |
|---|---|---|---|
| [production/EnvelopeFollower_Main.zip](./production/EnvelopeFollower_Main.zip) | `EnvelopeFollower.kicad_pcb` | 14 fab files (9 Gerbers, 2 Excellon `.drl`, 2 drill maps, 1 `.gbrjob`; excludes `*_cpl.csv`) | **PCB Quote → Add Gerber File** (Main Board) |
| [jlcpcb_bom.csv](./jlcpcb_bom.csv) | `EnvelopeFollower.kicad_pcb` | 20 unique BOM lines / 49 `B.Cu` SMT placements (`Comment,Designator,Footprint,LCSC Part #`) | **PCB Assembly → Add BOM File** (Main Board) |
| [production/main/EnvelopeFollower_cpl.csv](./production/main/EnvelopeFollower_cpl.csv) | `EnvelopeFollower.kicad_pcb` | 49 Bottom SMD placements (`Designator,Val,Package,Mid X,Mid Y,Rotation,Layer`, `Layer=Bottom`) | **PCB Assembly → Add CPL File** (Main Board) |
| [production/EnvelopeFollower_Panel.zip](./production/EnvelopeFollower_Panel.zip) | `panel/EnvelopeFollower_Panel.kicad_pcb` | 14 fab files (9 Gerbers, 2 Excellon `.drl`, 2 drill maps, 1 `.gbrjob`) | **PCB Quote → Add Gerber File** (Separate bare-PCB order for Front Panel) |

---

## 2. Main Circuit PCB (`EnvelopeFollower.kicad_pcb`) — PCB Fab & Economic PCBA

### 2.1 PCB Fabrication Settings (`EnvelopeFollower_Main.zip`)

- **Dimensions:** `30.00 mm × 108.00 mm` (`30.10 mm × 108.10 mm` `.gbrjob` outline including `0.10 mm` `Edge.Cuts` stroke)
- **Layers:** `2` (`F.Cu`, `B.Cu`)
- **Material & Thickness:** `FR-4`, **`1.6 mm`**
- **Copper Weight:** **`1 oz`** outer copper (`0.035 mm`)
- **Minimum Track / Spacing:** `0.25 mm` / `0.25 mm` (meets JLCPCB standard 2-layer `0.127 mm` minimum with generous margin)
- **Drills:** `153` PTH holes (`100 × 0.30 mm` via drills, `53` THT component drills `0.80–1.43 mm`), `0` NPTH holes
- **Via Covering / Tenting:** Vias are tented on both sides (`tenting front yes`, `tenting back yes`)
- **Solder Mask & Silkscreen:** **Black** solder mask with **White** silkscreen (`B.Fab` fab notes match; Green/Matte Black also compatible with white silkscreen)
- **Surface Finish:** **Lead-Free HASL** (`HASL-LF`) or **ENIG** (`IPC-6012 Class 2`)
- **JLCPCB QR Code / Order Number Replacement (`5 × 5 mm` `B.SilkS` square):**
  - `EnvelopeFollower.kicad_pcb` reserves a **`5.00 mm × 5.00 mm` solid filled square** on `B.SilkS` at `(24.25, 102.45)` to `(29.25, 107.45)` mm in KiCad PCB coordinates (`(24.25, -107.45)` to `(29.25, -102.45)` mm in Gerber coordinates; center `(26.75, 104.95)` mm) in the unobstructed bottom-right corner next to `J4`.
  - On JLCPCB's PCB quote form under **Mark on PCB / Order Number** (or **Specify a location**), instruct JLCPCB to **replace the `5 × 5 mm` `B.SilkS` square with a JLCPCB 2D QR code** so the production tracking barcode lands cleanly inside that keepout rather than overlapping `B.SilkS` passive values or `J4` pinout markings.

### 2.2 JLCPCB SMT Assembly Settings (`jlcpcb_bom.csv` + `production/main/EnvelopeFollower_cpl.csv`)

- **Assembly Type:** **Economic PCBA** (single-sided SMD only)
- **Assembly Side:** **Bottom (`B.Cu`) only** (`49` placements, `0` SMT parts on `F.Cu`)
- **BOM Composition (`20` lines / `49` parts — see [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md)):**
  - **Basic Parts (`$0` feeder fee):** `15` unique BOM lines / `39` placements (`1N4148WS`, `1N5819WS`, `0603` resistors/capacitors)
  - **Preferred Extended (`$0` feeder fee):** `1` line / `1` placement (`R14`, `4.7M` `0603`, `C23163`)
  - **Extended Parts (`$3.00` × 4 = `$12.00` setup fee):** `U1`/`U2` (`TL074HIDR`, `C2878713`), `D9`–`D11` (`BAT54S`, `C47546`), `C3`/`C4` (`RVT47UF35V67RV0039`, `C2836440`), `R21`/`R24` (`25121WF1001T4E`, `C54315`)
- **BOM ↔ CPL 1:1 Parity Verification:**
  - `production/main/EnvelopeFollower_cpl.csv` contains **49 Bottom SMD rows** matching the `49` designators in `jlcpcb_bom.csv` 1:1 (`Designator`, `Val == Comment`, `Package == Footprint`, `Layer == Bottom`).
  - `translate_bom_pnp.py pnp --bom jlcpcb_bom.csv` confirmed `rows_in = 49`, `rows_out = 49`, `filtered_orphans = 0`.
  - **Zero leakage:** Front THT controls (`J1`–`J3`, `RV1`–`RV4`, `D4`), rear THT parts (`J4`, `C1`, `C2`), optional `DNP` test points (`TP1`–`TP8`), and fiducials (`FID1`–`FID3`) are excluded.
- **Stock Advisory:** Verify live stock for `TL074HIDR` (`C2878713`, `465` pcs at last check in [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md)) before placing large orders.

### 2.3 JLCPCB Rotation Offset Validation & 3D Placement Preview Checklist

`production/main/EnvelopeFollower_cpl.csv` was exported via `kicad-cli pcb export pos --side back --smd-only --exclude-dnp --format csv --units mm` (without `--bottom-negate-x`, so `Mid X` is positive and matches Gerber coordinates `0..30 mm`, and `Mid Y` is `-108..0 mm`), converted to JLCPCB's `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` header with `Layer=Bottom`, and retains KiCad's exported placement angles (`0°`, `90°`, `180°`).

Per the `jlcpcb` skill (`Rotation Offsets` table) and [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md), **always inspect JLCPCB's interactive 3D / Placement Preview before confirming payment** because JLCPCB's pick-and-place zero-orientation differs from KiCad on several packages and bottom-side components (`B.Cu` parts are mirrored across X in KiCad, corresponding to `(180° - Rot)` when viewed directly from the back):

| Package / LCSC | Refs (`CPL Rot`) | `jlcpcb` Skill Offset Guidance | Physical Pad / Polarity Check in JLCPCB 3D Preview |
|---|---|---|---|
| `SOIC-14_3.9x8.7mm_P1.27mm` (`C2878713`) | `U1` (`0°`), `U2` (`180°`) | SOIC family (`SOIC-8/16`) typically requires **`+90°` or `+270°`** offset relative to KiCad (+ check Bottom mirror) | Verify Pin 1 dot aligns with Pad 1: `U1` Pad 1 (`V_GAIN`) is at `(10.625, -9.710)` mm (visual bottom-right looking at back); `U2` Pad 1 (`V_INV_BUF`) is at `(22.875, -52.790)` mm (visual top-left looking at back). |
| `SOT-23` (`C47546`) | `D9` (`180°`), `D10` (`90°`), `D11` (`0°`) | `SOT-23` typically requires **`+180°`** offset (+ check Bottom mirror) | Verify all 3 pins sit squarely on pads and match Pin 1 (`-12V_PROT`) / Pin 2 (`+12V_PROT`) vs single-side Pin 3 (`COM`): `D9` Pin 3 at `(5.963, -53.700)`, `D10` Pin 3 at `(15.000, -73.912)`, `D11` Pin 3 at `(6.237, -72.300)`. |
| `D_SOD-323` (`C2128`, `C191023`) | `D1`–`D3`, `D5`–`D8` (`0°`) | Polarized 2-pin diode (not in `jlcpcb` skill table; verify Bottom mirror `(180° - 0°)`) | Confirm diode **cathode band** aligns with **Pad 1 (`K`)** at `X - 1.05 mm` (visual right looking at back, adjacent to the bold `B.SilkS` cathode bar). Note `D7` (`+12V`) and `D8` (`-12V`) both have `K` at Pad 1 (`0°`). Rotate `180°` in preview if reversed. |
| `CP_Elec_6.3x5.4` (`C2836440`) | `C3` (`90°`), `C4` (`0°`) | Polarized electrolytic (verify Bottom mirror + chamfer/stripe orientation) | **Critical polarity check:** Verify the black `-` polarity stripe aligns with **Pad 2 (`-`)** and the chamfered `B.SilkS` `-` outline: `C3` Pad 1 (`+`) at `(25.850, -98.400)` / Pad 2 (`-`) at `(25.850, -92.800)`; `C4` Pad 1 (`+`, `GND`) at `(8.650, -92.200)` / Pad 2 (`-`, `-12V_PROT`) at `(14.250, -92.200)`. Rotate `180°` in preview if reversed. |
| `R_2512_6332Metric` (`C54315`) & `0603` (`R*`, `C5`–`C10`) | `37` parts (`0°`, `90°`, `180°`) | Non-polarized symmetric 2-pin passives (`0°`/`180°` functionally identical) | Confirm rectangular component bodies align longitudinally across each pad pair (`0°` vs `90°`). |

---

## 3. Front Panel (`panel/EnvelopeFollower_Panel.kicad_pcb`) — Bare PCB Order

Order `production/EnvelopeFollower_Panel.zip` as a **separate bare-PCB fabrication order** (do **not** enable PCB Assembly, BOM, or CPL for the panel).

### 3.1 Panel Fabrication Settings (`EnvelopeFollower_Panel.zip`)

- **Dimensions:** `30.00 mm × 128.50 mm` (Doepfer A-100 `6 HP × 3U` front panel; `30.05 mm × 128.55 mm` `.gbrjob` outline including `0.05 mm` `Edge.Cuts` stroke)
- **Layers:** `2` (`F.Cu`, `B.Cu` grounded copper shield planes; `F.Paste` / `B.Paste` empty)
- **Material & Thickness:** `FR-4`, **`1.6 mm`** (per `.gbrjob`; optionally `2.0 mm` FR4 if extra rigidity is preferred, noting pot/jack bushing thread depth)
- **Copper Weight:** **`1 oz`** outer copper (`0.035 mm`)
- **Solder Mask & Silkscreen:** **Matte Black** (or Black) solder mask with **White** silkscreen. Note that front `F.Mask` tents over the `8.6 mm` jack pads for a clean faceplate finish around M6 nuts, while rear `B.Mask` exposes the `8.6 mm` copper grounding rings on `B.Cu` so jack bushings/nuts bond the `GND` shield planes directly to chassis ground.
- **Surface Finish:** **ENIG** (recommended for flat exposed `B.Cu` grounding rings and high-contrast matte-black appearance) or **Lead-Free HASL**
- **Drills & Slotted Cutouts:**
  - `7` PTH holes (`3 × 6.20 mm` for `J1`–`J3` 3.5 mm jacks; `4 × 7.20 mm` for `RV1`–`RV4` 9 mm pots)
  - `1` NPTH circular hole (`3.20 mm` for `D4` 3 mm LED)
  - `2` NPTH oval slots (`3.20 mm × 5.50 mm`, `G85` routed slots in `EnvelopeFollower_Panel-NPTH.drl` for M3 Eurorack rail mounting screws)
- **JLCPCB QR Code Replacement (`5 × 5 mm` `B.SilkS` square):**
  - `panel/EnvelopeFollower_Panel.kicad_pcb` places a **`5.00 mm × 5.00 mm` solid filled square** on `B.SilkS` at `(12.50, 50.25)` to `(17.50, 55.25)` mm in KiCad PCB coordinates (`(12.50, -55.25)` to `(17.50, -50.25)` mm in Gerber coordinates; center `(15.00, 63.00)` mm relative to the panel's top-left origin `(0, -10.25)` mm).
  - On JLCPCB's panel quote form under **Mark on PCB / Order Number**, select **"Specify a location"** (replace silkscreen with JLCPCB 2D QR code) so JLCPCB prints the tracking QR code onto that rear `B.SilkS` square and keeps the front face (`F.SilkS`) completely clean.

---

## 4. Post-PCBA Manual Assembly Sequence

After receiving the `B.Cu`-assembled main PCBs and bare front panels from JLCPCB:

1. **Rear `B.Cu` THT parts:** Hand-solder `J4` (`2×5` shrouded Eurorack power header, key notch inward, Pin 1 `-12V` on the `RED` stripe side) and `C1`, `C2` (`1 µF 63 V` `P=5mm` box film capacitors). Optionally fit `TP1`–`TP8` (`RH-5001`, `C5199801`) from `B.Cu` and trim leads flush on `F.Cu` before mounting the panel.
2. **Front `F.Cu` panel controls:** Insert `J1`–`J3` (`WQP-PJ398SM`), `RV1`–`RV4` (`Alpha RD901F` `A100k`/`A50k`/`A1M`/`B10k`), and `D4` (`3 mm` LED, square pad `Pin 1` = cathode `-`) loosely on `F.Cu`, seat the `EnvelopeFollower_Panel` over the bushings/LED, tighten jack/pot nuts to set mechanical alignment, and solder all `F.Cu` pins from `B.Cu`.

---

## 5. Verification Summary

- **Main PCB DRC (`kicad-cli pcb drc --refill-zones`):** `0` violations, `0` unconnected items.
- **Main PCB Gerbers (`analyze_gerbers.py production/main/`):**
  - Layer completeness: **complete** (`9/9` Gerber layers + `PTH`/`NPTH` Excellon drills matching `.gbrjob`).
  - Layer alignment: **aligned** (`issues: []`, `Edge.Cuts` `30.0 × 108.0 mm`).
  - Paste coverage note: `analyze_gerbers.py` emits heuristic warning `GR-004` (`125` `B.Paste` flashes vs `281` `B.Cu` flashes = `44%`). Inspection of `gerber.json` confirms `pad_summary.smd_apertures = 125` (`2×14 + 3×3 + 44×2 = 125` SMD pads), so **`125 / 125` (`100%`) of SMD pads have solder paste apertures**; the remaining `156` `B.Cu` flashes are `100` tented vias, `53` THT pads, and `3` fiducials.
- **Panel PCB DRC & Gerbers (`kicad-cli pcb drc`, `analyze_gerbers.py production/panel/`):** `0` non-library DRC violations, `0` unconnected items, `0` Gerber findings (`complete: true`, `aligned: true`, `10` total drill hits: `7` PTH + `3` NPTH).
- **ZIP Hygiene:** `production/EnvelopeFollower_Main.zip` (14 files) and `production/EnvelopeFollower_Panel.zip` (14 files) verified clean via `unzip -l` with **zero `*_cpl.csv`** files included.
