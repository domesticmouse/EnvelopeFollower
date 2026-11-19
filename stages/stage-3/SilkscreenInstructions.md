# Envelope Follower — PCB Silkscreen & Fabrication Markup Guide (Stage 3)

> **Circuit Spec:** [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md)  
> **BOM Companion:** [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md) (`49` JLCPCB SMD + `10` Manual THT + `8` Optional DNP Test Points = `67` PCB Footprints)  
> **Workflow Alignment:** Compatible with [`kicad-silkscreen-markup`](../stage-1/.agents/skills/kicad-silkscreen-markup/SKILL.md), [`jlcpcb`](../stage-1/.agents/skills/jlcpcb/SKILL.md), and KiCad PCB analyzer checks (`analyze_pcb.py` / `silk_annotator.py`)

---

## 1. Goals: Easy JLCPCB Inspection Without Assembly Clutter

When reviewing **JLCPCB Economic PCBA** placement reports, 3D DFM renders, and finished boards, two mistakes are easiest to catch visually when clearly printed on the PCB silkscreen:
1. **Wrong component value or dielectric/wattage** (e.g., `10 kΩ` vs. `20 kΩ`, `1 kΩ 0603` vs. `1 kΩ 1 W 2512`, `100 nF X7R` vs. `47 pF NP0`).
2. **180° / 90° rotation or polarity errors** (common on `SOIC-14`, `SOD-123`, `SOT-23`, and SMD electrolytics during CPL export).

This guide standardizes how to show **both Reference Designators and concise Values** on `F.SilkS` / `B.SilkS`, mark **test points and THT parts on both sides**, and add **external polarity markers** while keeping **zero DRC/DFM errors**.

---

## 2. Core KiCad Silkscreen Rules (`Reference` + User-Text `Value`)

### 2.1 Why Values Use `fp_text user` Instead of `fp.Value()`
- **Keep `fp.Value()` hidden on `F.Fab` / `B.Fab`:** KiCad's PCB analyzer (`analyze_pcb.py`) flags visible footprint `Value` fields on `.SilkS` under `values_visible_on_silk` as assembly clutter, and default BOM values (e.g., `WQP-PJ398SM`, `TL074HIDR`, `10uF 50V X7R`) often overflow dense `0603` / `SOD-123` neighborhoods.
- **Keep `fp.Reference()` visible on the primary `.SilkS` layer:** Achieves `100%` `refs_visible_on_silk` (`>= 90%` required).
- **Add concise value/function tokens via `fp_text user` (`pcbnew.PCB_TEXT(fp)`):** Place a short, unambiguous token directly paired with `<REF>` on the same silkscreen layer (e.g., `R2` + `10k`, `R16` + `1k 1W`, `C1` + `10u 50V`, `C10` + `15p NP0`, `U1` + `TL074H`). This displays every required value right on the board for JLCPCB report comparison without triggering `values_visible_on_silk` warnings.

### 2.2 Typography, Clearances & Layer Conventions
| Parameter | Requirement | Rationale |
|---|---|---|
| **Text Height** | **`>= 0.80 mm`** | Minimum crisp legibility on JLCPCB silkscreen (`0.80 mm` standard; `1.0–1.2 mm` for board title / `J_PWR` / `TP` nets if space allows). |
| **Stroke Width** | **`>= 0.15 mm`** | JLCPCB minimum reliable silkscreen line width (`SILK_THICKNESS = 0.15 mm`). |
| **Text Rotations** | **`0°` or `90°` only** | Keeps `<REF> <VAL>` pairs consistently readable without upside-down text during inspection. |
| **Pad / Mask Clearance (`SK-001`)** | **`>= 0.25 mm`** outside pads & `.Mask` boxes | Prevents `silk_over_copper` DRC errors and JLCPCB ink clipping over exposed pads. |
| **Footprint Graphic Clearance** | **`>= 0.20 mm`** outside `.SilkS` outlines | Prevents text crossing IC borders, pot housings, jack circles, or diode outlines. |
| **`<REF>` to `<VAL>` Gap** | **`>= 0.35 mm`** between bounding boxes | Ensures `<REF>` and `<VAL>` stay visually distinct (measured via KiCad `PCB_TEXT.GetBoundingBox()` + `0.06 mm` padding, since uppercase glyphs like `R`, `V`, `T`, `W` exceed simple width heuristics). |
| **Neighbor Label Gap** | **`>= 0.20 mm`** between any two labels | Prevents `silk_overlap` collisions between adjacent `0603` / `SOD-123` parts. |
| **Board Edge Clearance** | **`>= 0.45 mm`** (`0.50 mm` rec.) from `Edge.Cuts` | Prevents silkscreen clipping during V-cut / routing. |

### 2.3 Accounting for `B.SilkS` Mirroring (Left-to-Right Reading)
- All SMD components (`49` pcs) and rear THT components (`J_PWR`, `C2`, optional `TP1`–`TP8`) sit on **`B.Cu`**, so their primary labels live on **`B.SilkS`** with **`SetMirrored(True)`**.
- In KiCad board coordinates (`+X` right), viewing the back of the board flips horizontal direction so `+X` appears to the **visual left**.
- Therefore, when placing a horizontal (`0°`) `<REF> <VAL>` pair centered at `(tx, ty)`:
  - On **`F.SilkS`** (`sign = +1`): `<REF>` goes at `tx - (vw + gap)/2`, `<VAL>` goes at `tx + (rw + gap)/2`.
  - On **`B.SilkS`** (`sign = -1`): `<REF>` goes at `tx + (vw + gap)/2`, `<VAL>` goes at `tx - (rw + gap)/2`.
  - Result: **`<REF> <VAL>` always reads naturally left-to-right on both sides of the PCB** (handled automatically by `place_ref_val_pair()` in [`silk_annotator.py`](../stage-1/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py)).

---

## 3. Dual-Sided Labeling: Test Points (`TP1`–`TP8`) & THT Parts

Because THT holes pass through both copper layers, labeling them on **both `F.SilkS` and `B.SilkS`** lets you probe, solder, and verify the board from either side (before or after panel mounting):

1. **Test Points (`TP1`–`TP8`, Ronghe `RH-5001`, DNP):**
   - Mark **both `<REF>` (`TP1`–`TP8`) and signal/rail name on `B.SilkS` AND `F.SilkS`**.
   - Keep `fp.Reference()` visible on the primary side (`B.SilkS`) and place matching secondary `PCB_TEXT` labels on `F.SilkS` (`SetMirrored(False)`).
   - Add a compact board-level note **`TP1-8: DNP (OPT)`** near the test point group or in the board legend so JLCPCB DFM engineers and assemblers know `TP1`–`TP8` are intentionally unpopulated.
   - Keep `TP1`–`TP8` markings outside the `2.0 mm` pad (`>= 0.25 mm` mask clearance) so needle probes or soldered `RH-5001` loops never obscure the text.

2. **Rear-Mounted Populated THT (`J_PWR`, `C2` on `B.Cu`):**
   - **`J_PWR` (`2×5` IDC Header):** Primary `J_PWR` + rail legend on `B.SilkS`, mirrored duplicate on `F.SilkS`. Draw a solid **`-12V RED` stripe bar** along Pins `1–2`, Pin `1` dot/triangle, and explicit `-12V` / `GND` / `+12V` callouts on **both sides** so backwards ribbon cables or soldering mistakes are caught from either side.
   - **`C2` (`1 µF 63 V` WIMA MKS2 Film):** `C2` + `1u FILM` on `B.SilkS`, plus `C2 1u` on `F.SilkS` (`F.SilkS` label stays outside front-panel pot/jack footprints).

3. **Front-Mounted THT Controls (`J1`–`J3`, `RV1`–`RV4`, `D4` on `F.Cu`):**
   - Primary `<REF> <VAL>` on **`F.SilkS`** (`J1 IN`, `J2 OUT`, `J3 INV`, `RV1 A100k`, `RV2 A50k`, `RV3 A1M`, `RV4 B10k`, `D4 LED`) plus secondary `PCB_TEXT` labels on **`B.SilkS`** so every pot lug (`1` = CCW), jack pin (`T`/`TN`/`S`), and LED polarity (`+`/`-`) can be identified from the rear while hand-soldering or bench-probing.

---

## 4. Mandatory External Polarity & Pin-1 Markers

Footprint internal graphics often sit directly under the plastic body once JLCPCB solders the part. Always add **external** silkscreen indicators (`>= 0.25 mm` outside all pads/mask openings) so you can verify orientation in JLCPCB 3D/optical inspection photos:

| Part Group | Package | External Silkscreen Graphic (`B.SilkS` / Both) | Exact Pin / Pad Mapping |
|---|---|---|---|
| **`U1`, `U2`** (`TL074HIDR`) | `SOIC-14` | Filled circle dot (`radius = 0.25 mm`, `Ø 0.50 mm`) outside **Pin 1** | `Pin 1` = `U1A.OUT` (`PREAMP_OUT`) / `U2A.OUT` (`INV_DRV`) |
| **`D1`–`D3`, `D5`–`D7`** (`1N4148W`) & **`D10`, `D11`** (`B5819W`) | `SOD-123` | Bold **`0.25 mm` wide cathode bar** outside **Pad 1 (`K`)** *(add small `K` if space permits)* | KiCad `Device:D` / `D_SOD-123`: **Pad 1 = `K` (Cathode)**, **Pad 2 = `A` (Anode)** |
| **`D8`, `D9`** (`BAV99`) | `SOT-23` | Filled Pin-1 dot (`radius = 0.25 mm`) outside **Pin 1** | `Pin 1` = `A1` (`-12V_PROT`), `Pin 2` = `K2` (`+12V_PROT`), `Pin 3` = output midpoint (`ENV_OUT` / `INV_DRV`) |
| **`C3`, `C4`** (`22 µF 35 V`) | `CP_Elec_5x5.4` | Clear **`+`** symbol (`>= 0.80 mm`) outside **Pad 1 (`+`)** | **`C3.+`** → `+12V_PROT`; **`C4.+`** → `GND` *(note: `C4` faces opposite `C3` because `-12V_PROT < GND`!)* |
| **`D4`** (`3 mm` THT LED) | `LED_D3.0mm` | External **`+`** outside **Pad 2 (`A`)** and **`-` / bar** outside **Pad 1 (`K`, square pad)** on **both sides** | `Pad 1` = `K` (`LED_K`), `Pad 2` = `A` (`LED_A`) |
| **`RV1`–`RV4`** (`9 mm` pots) | `RK09K` Vertical | External **`1`** beside **Pin 1 (`L1` / CCW)** on **both sides** | Confirms CW/CCW direction for `GAIN`, `ATK`, `Release`, and `OFFSET` (`RV4.L1` = `-12V_PROT`) |
| **`J_PWR`** (`2×5` IDC) | `2×5` Shrouded | Solid **`-12V RED`** stripe bar at Pins `1–2` + Pin `1` dot + key notch outline on **both sides** | Pins `1–2` = `-12Vin`, Pins `3–8` = `GND`, Pins `9–10` = `+12Vin` |

---

## 5. Board-Level Markings, JLCPCB QR Placeholder & `B.Fab` Notes

1. **Board Title & Revision (Silkscreen):**
   - Place module identifier (e.g., `ENVELOPE FOLLOWER`) and revision (e.g., `REV A` / `V1.0`, matching the KiCad title block `rev` field) on `B.SilkS` (and `F.SilkS` if clear of panel components) so `analyze_pcb.py` (`has_board_name`, `has_revision`) passes with zero documentation warnings.
2. **JLCPCB QR Code Placeholder (`5.0 × 5.0 mm`):**
   - Draw a **`5.0 × 5.0 mm` solid filled silkscreen square** on **`B.SilkS`** (and optionally `F.SilkS`) in an unobstructed area (`>= 0.45 mm` from board edges, `>= 0.25 mm` from any pad/mask) so JLCPCB places its tracking QR there instead of over component labels.
3. **Complete Fabrication Notes (`B.Fab` Layer — Not `.SilkS`):**
   - Place mirrored text (`0.80 mm` height, `0.15 mm` thickness) on **`B.Fab`** containing all 6 items checked by `analyze_pcb.py` (`fab_notes_completeness`):
     ```text
     FAB NOTES: 2L FR4 | THICKNESS: 1.6mm | 1oz CU
     FINISH: ENIG / HASL-LF | IPC-6012 CLASS 2
     SOLDER MASK: BLACK | SILK: WHITE | MIN TR/SP: 0.127mm
     DRILL TOL: +/-0.08mm | NO EDGE CUT
     ```
     *(Update `SOLDER MASK` color if ordering green/blue/white solder mask.)*

---

## 6. Complete Component-by-Component Silkscreen Table (`67` Footprints)

> Keep `<VAL>` tokens concise (`0.80 mm` / `0.15 mm`) so every label stays legible on compact Eurorack layouts while still distinguishing package/rating variants in JLCPCB reports (`1k` vs. `1k 1W`, `10R 0.25W`, `10u 50V`, `NP0` vs. `100n`, pot tapers).

### 6A. JLCPCB SMD Components (`49` Parts — Primary `B.SilkS`)

| RefDes | Qty | BOM Value / MPN | `<REF>` | `<VAL>` (`fp_text user`) | Silk Layer(s) | Required External Marker |
|---|---:|---|---|---|---|---|
| `U1`, `U2` | 2 | `TL074HIDR` (`SOIC-14`) | `U1`, `U2` | `TL074H` | `B.SilkS` | Pin 1 dot (`Ø 0.50 mm`) |
| `D1`, `D2`, `D3`, `D5`, `D6`, `D7` | 6 | `1N4148W` (`SOD-123`) | `D1`–`D3`, `D5`–`D7` | `1N4148W` *(or `4148` if tight)* | `B.SilkS` | `0.25 mm` external `K` bar outside Pad 1 |
| `D10`, `D11` | 2 | `B5819W` (`SOD-123`) | `D10`, `D11` | `B5819W` | `B.SilkS` | `0.25 mm` external `K` bar outside Pad 1 |
| `D8`, `D9` | 2 | `BAV99` (`SOT-23`) | `D8`, `D9` | `BAV99` | `B.SilkS` | Pin 1 dot (`A1 = -12V_PROT`) outside Pin 1 |
| `R11`, `R12`, `R28` | 3 | `470 Ω 1%` (`0603`) | `R11`, `R12`, `R28` | `470R` | `B.SilkS` | — |
| `R26` | 1 | `1 kΩ 1%` (`0603`) | `R26` | `1k` | `B.SilkS` | — |
| `R29` | 1 | `2.2 kΩ 1%` (`0603`) | `R29` | `2.2k` | `B.SilkS` | — |
| `R2`, `R6`, `R7`, `R14`, `R15`, `R17`, `R18` | 7 | `10 kΩ 1%` (`0603`) | `R2`, `R6`, `R7`, `R14`, `R15`, `R17`, `R18` | `10k` | `B.SilkS` | — |
| `R3`, `R4`, `R5`, `R8A`, `R8B`, `R13` | 6 | `20 kΩ 1%` (`0603`) | `R3`, `R4`, `R5`, `R8A`, `R8B`, `R13` | `20k` | `B.SilkS` | — |
| `R10` | 1 | `47 kΩ 1%` (`0603`) | `R10` | `47k` | `B.SilkS` | — |
| `R1`, `R30` | 2 | `1 MΩ 1%` (`0603`) | `R1`, `R30` | `1M` | `B.SilkS` | — |
| `R24`, `R25` | 2 | `10 Ω 1% 0.25 W` (`1206`) | `R24`, `R25` | `10R 0.25W` *(or `10R`)* | `B.SilkS` | Distinguishes `1206` surge Rs from `0603` |
| `R16`, `R19` | 2 | `1 kΩ 1% 1 W` (`2512`) | `R16`, `R19` | `1k 1W` | `B.SilkS` | Distinguishes `1 W` fault Rs from `R26` |
| `C5`, `C6`, `C7`, `C8` | 4 | `100 nF 50 V X7R` (`0603`) | `C5`–`C8` | `100n` | `B.SilkS` | — |
| `C1` | 1 | `10 µF 50 V X7R` (`1206`) | `C1` | `10u 50V` | `B.SilkS` | `50V` confirms DC-bias voltage rating |
| `C3`, `C4` | 2 | `22 µF 35 V` Elec (`5×5.4`) | `C3`, `C4` | `22u 35V` | `B.SilkS` | External `+` outside Pad 1 (`C3.+` = `+12P`, `C4.+` = `GND`) |
| `C10` | 1 | `15 pF 50 V NP0` (`0603`) | `C10` | `15p NP0` | `B.SilkS` | `NP0` distinguishes feedback cap from X7R |
| `C9`, `C11`, `C12` | 3 | `47 pF 50 V NP0` (`0603`) | `C9`, `C11`, `C12` | `47p NP0` | `B.SilkS` | `NP0` distinguishes feedback caps from X7R |
| `C13` | 1 | `100 pF 50 V NP0` (`0603`) | `C13` | `100p NP0` | `B.SilkS` | `NP0` distinguishes feedback cap from X7R |

### 6B. Manual THT Components (`10` Populated Parts — Dual-Sided Labeling)

| RefDes | Qty | BOM Part / Spec | Primary Layer | Secondary Layer | `<REF>` + `<VAL>` (`F.SilkS` / `B.SilkS`) | Required External Marker |
|---|---|---|---|---|---|---|
| `C2` | 1 | `1 µF 63 V` WIMA MKS2 Film | `B.SilkS` | `F.SilkS` | `C2` + `1u FILM` (`B`), `C2 1u` (`F`) | Non-polarized film |
| `J_PWR` | 1 | `2×5P` Shrouded Eurorack IDC | `B.SilkS` | `F.SilkS` | `J_PWR` + `-12V RED` / `GND` / `+12V` | Pin 1 dot, `-12V RED` stripe bar (Pins 1–2), notch outline on **both sides** |
| `D4` | 1 | `3 mm` Indicator LED | `F.SilkS` | `B.SilkS` | `D4` + `ENV LED` (`F`/`B`) | External `+` (Pad 2 `A`) and `-` (Pad 1 `K`) on **both sides** |
| `J1` | 1 | `3.5 mm` Jack (`IN`) | `F.SilkS` | `B.SilkS` | `J1` + `IN` | Optional `T`/`TN`/`S` pin hint on `B.SilkS` |
| `J2` | 1 | `3.5 mm` Jack (`OUT`) | `F.SilkS` | `B.SilkS` | `J2` + `OUT` | Optional `T`/`S` pin hint on `B.SilkS` |
| `J3` | 1 | `3.5 mm` Jack (`INV_OUT`) | `F.SilkS` | `B.SilkS` | `J3` + `INV` (`INV_OUT`) | Optional `T`/`S` pin hint on `B.SilkS` |
| `RV1` | 1 | `A100k` 9 mm Pot (`GAIN`) | `F.SilkS` | `B.SilkS` | `RV1` + `A100k GAIN` | `"1"` (Pin 1 CCW) on **both sides** |
| `RV2` | 1 | `A50k` 9 mm Pot (`ATK`) | `F.SilkS` | `B.SilkS` | `RV2` + `A50k ATK` | `"1"` (Pin 1 CCW) on **both sides** |
| `RV3` | 1 | `A1M` 9 mm Pot (`Release`) | `F.SilkS` | `B.SilkS` | `RV3` + `A1M REL` | `"1"` (Pin 1 CCW) on **both sides** |
| `RV4` | 1 | `B10k` 9 mm Pot (`OFFSET`) | `F.SilkS` | `B.SilkS` | `RV4` + `B10k OFF` | `"1"` (Pin 1 CCW = `-12V_PROT`) on **both sides** |

### 6C. Optional DNP Test Points (`8` Footprints — Mandatory Dual-Sided Labeling)

| RefDes | Net | BOM Part / Status | Silk Layers | Label (`B.SilkS` & `F.SilkS`) | Compact Alias (if 4–6 HP space is tight) | Notes |
|---|---|---|---|---|---|---|
| `TP1` | `GND` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP1 GND` | `TP1 GND` | Ground clip anchor |
| `TP2` | `+12V_PROT` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP2 +12V_PROT` | `TP2 +12P` | Post-`D10`/`R24` (`+11.55 V`) |
| `TP3` | `-12V_PROT` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP3 -12V_PROT` | `TP3 -12P` | Post-`D11`/`R25` (`-11.60 V`) |
| `TP4` | `PREAMP_OUT` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP4 PREAMP_OUT` | `TP4 PRE` | `U1A.OUT` (`1`) |
| `TP5` | `HALF_WAVE` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP5 HALF_WAVE` | `TP5 HWR` | `D2.A` / `R6.2` / `R7.1` |
| `TP6` | `RECT_OUT` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP6 RECT_OUT` | `TP6 RECT` | `U1C.OUT` (`8`) |
| `TP7` | `PEAK_DET` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP7 PEAK_DET` | `TP7 PEAK` | `D3.K` / `U2C.IN-` (`9`) |
| `TP8` | `ENV_RAW_BUF` | `RH-5001` (`DNP`) | **`B.SilkS` + `F.SilkS`** | `TP8 ENV_RAW_BUF` | `TP8 ENV` | `U2D.OUT` (`14`) |

> Add a board-level note **`TP1-8: DNP`** (or `TP = DNP`) on `B.SilkS` (and `F.SilkS` if visible) so unpopulated test point pads are never mistaken for missing assembly parts during JLCPCB QA.

---

## 7. Pre-Order Verification Checklist (KiCad & JLCPCB)

Run these checks on the finished `.kicad_pcb` before exporting production Gerbers and reviewing JLCPCB's PCBA preview:

1. **Automated Silkscreen Bounding-Box Inspection:**
   ```bash
   python3 /Users/brett/Documents/GitHub/EnvelopeFollower/stages/stage-1/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py \
     --inspect EnvelopeFollower.kicad_pcb
   ```
   Confirm: `Refs on SilkS: 67/67`, `Values on Silk: 0`, `Text overlaps: 0`, `Keepout/pad hits: 0`, `Out-of-bounds: 0`.
2. **KiCad DRC Check:**
   Confirm `0` `silk_overlap` and `0` `silk_over_copper` violations (`kicad-cli pcb drc`).
3. **PCB Static Analyzer Check (`analyze_pcb.py`):**
   Confirm `0` `SK-001` warnings, `refs_visible_on_silk = 100%`, `values_visible_on_silk` empty, `fab_notes_completeness = 100%`, and `documentation_warnings` clean (board name, revision, and polarity markers present).
4. **Visual 3D Render & JLCPCB DFM Cross-Check:**
   Render top and bottom views (`kicad-cli pcb render --side top` / `--side bottom`), then cross-check JLCPCB's interactive PCBA placement preview line-by-line against [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md):
   - Verify every `<REF> <VAL>` text reads left-to-right on `B.SilkS` and matches the assigned JLCPCB LCSC part value (`10k`, `20k`, `1k 1W`, `10R 0.25W`, `10u 50V`, `15p/47p/100p NP0`).
   - Verify **IC Pin 1** (`U1`, `U2`), **diode `K` bars** (`D1`–`D3`, `D5`–`D7`, `D10`–`D11`), **`BAV99` Pin 1** (`D8`, `D9`), and **opposite electrolytic `+` signs** (`C3` vs. `C4`) match the 3D bodies in JLCPCB's preview (fixing any `90°`/`180°` CPL rotation offsets before submitting).
