# Envelope Follower (Improved Eurorack Revision) — Silkscreen & Fabrication Markup Instructions

Companion PCB silkscreen and fabrication-layer specification for [EnvelopeFollowerImproved.md](./EnvelopeFollowerImproved.md) and [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md), tailored for a **6 HP (`30.00 mm × 108.00 mm`) 2-layer Eurorack PCB** assembled via **single-sided `B.Cu` JLCPCB Economic PCBA** plus manual through-hole assembly.

> **Core Strategy:** Reserve `F.Cu` strictly for front-panel THT controls (`J1`–`J3`, `RV1`–`RV4`, `D4`) while placing all `49` SMT parts, rear THT parts (`J4`, `C1`, `C2`), and optional `DNP` test points (`TP1`–`TP8`) on **`B.Cu`**. Keep **`fp.Value()` hidden on `.Fab` layers** (`0` `values_visible_on_silk` warnings) and emit human-readable labels via **`PCB_TEXT(fp)` (`fp_text user`)** on `.SilkS`: **concise value-only tokens on `B.SilkS` for all resistors (`R1`–`R29`) and capacitors (`C1`–`C10`)** (with their reference designators kept on `B.Fab`), **`<REF> + <VAL>` pairs for all active, polarized, and interface parts**, and **dual-sided (`F.SilkS` + `B.SilkS`) markings** for all THT controls, `J4`, and `TP1`–`TP8`.

---

## 1. Layer Partition & Global Silkscreen Rules

### 1.1 Component Layer Allocation (`68` Footprints + Fiducials)

| Group | Refs | Count | Primary Side | `F.SilkS` Markup | `B.SilkS` Markup | `.Fab` Layer |
|---|---|---:|---|---|---|---|
| **SMT Op-Amps & Diodes** | `U1`–`U2`, `D1`–`D3`, `D5`–`D11` | `12` | `B.Cu` | None | `<REF>` + `<VAL>` + Pin-1 / `K` polarity | `fp.Value()` hidden (`B.Fab`) |
| **SMT Passives (`0603` / `2512`)** | `R1`–`R29`, `C5`–`C10` | `35` | `B.Cu` | None | **Concise value only** (`10k`, `100nF`, etc.) | `fp.Reference()` & `fp.Value()` hidden (`B.Fab`) |
| **SMT Bulk Electrolytics** | `C3`, `C4` (`47 µF 35 V`) | `2` | `B.Cu` | None | **Concise value (`47uF`) + `+`/`-` polarity** | `fp.Reference()` & `fp.Value()` hidden (`B.Fab`) |
| **Rear THT Film Caps** | `C1`, `C2` (`1 µF 63 V`) | `2` | `B.Cu` | Optional secondary `1uF` | **Concise value (`1uF`)** | `fp.Reference()` & `fp.Value()` hidden (`B.Fab`) |
| **Rear THT Power Header** | `J4` (`2×5` IDC) | `1` | `B.Cu` | Secondary `J4 PWR` + rail pins | Primary `J4 PWR` + key + **`-12V RED` / `GND` / `+12V`** | `fp.Value()` hidden (`B.Fab`) |
| **Rear THT Test Points (`DNP`)** | `TP1`–`TP8` (`RH-5001`) | `8` (`DNP`) | `B.Cu` | Secondary `TP*` + net name | Primary `TP*` + net name + `Ø 2.8 mm` ring | `fp.Value()` hidden (`B.Fab`) |
| **Front Panel THT Controls** | `J1`–`J3`, `RV1`–`RV4`, `D4` | `8` | `F.Cu` | Primary `<REF>` + function/value + polarity/Pin-1 | Secondary `<REF>` + function/value + polarity/Pin-1 | `fp.Value()` hidden (`F.Fab`) |
| **PCBA Fiducials** | `FID1`–`FID3` (min 3) | `3+` | `B.Cu` | None | **None** (`0` silkscreen text; `±1.25 mm` keepout) | `fp.Reference()` & `fp.Value()` hidden (`B.Fab`) |

### 1.2 Typography, Mirroring & Collision Geometry

1. **Minimum Legible Font (JLCPCB & `silk_annotator.py` Compliant):**
   - Text height: **`0.80 mm`** nominal (`1.00 mm` for board title / `J4` rail headers where space permits).
   - Stroke thickness: **`0.15 mm`** minimum (never thinner than `0.15 mm`).
   - Allowed rotations: **`0°` and `90°` only** (consistent horizontal or upward-reading vertical orientation).
   - **Exact Bounding-Box Measurement:** Always compute true KiCad stroke glyph dimensions via `pcbnew.PCB_TEXT.GetBoundingBox()` (`+0.06 mm` safety padding) rather than fixed character-width heuristics, which underestimate wide capitals (`R`, `V`, `W`, `T`).
2. **`B.SilkS` Mirroring & Reading Order:**
   - Every text object on `B.SilkS` must have `SetMirrored(True)`.
   - When placing `<REF> <VAL>` pairs horizontally on `B.SilkS`, mirror the X offset (`sign = -1.0` on `B.SilkS` vs. `+1.0` on `F.SilkS`) so `<REF>` sits visually to the left of `<VAL>` when looking directly at the back of the board.
3. **Clearances & Body Keepouts (Zero `silk_over_copper` / `silk_overlap`):**
   - Exposed pad & solder-mask clearance (`F.Mask` / `B.Mask`): **`≥ 0.25 mm`**.
   - Footprint `.SilkS` graphic outline clearance: **`≥ 0.20 mm`**.
   - Inter-label text-to-text gap: **`≥ 0.20 mm`** (within a `<REF>` + `<VAL>` pair: **`gap ≥ 0.35 mm`**).
   - Board edge (`Edge.Cuts`) clearance: **`≥ 0.45 mm`**.
   - **SMD `.Fab` Body Keepout:** Treat every SMD part's `.Fab` body outline (`+0.05 mm` margin) as a strict silkscreen keepout so labels **never sit underneath `U1`/`U2`, `D1`–`D11`, `R*`, or `C*` packages** and remain readable after JLCPCB reflow for post-assembly value inspection.
4. **Strict Local Tether & Corridor Discipline:**
   - SMD labels must stay within **`≤ 3.5 mm`** edge-to-edge of their own footprint; THT labels within **`≤ 6.0 mm`**; `<REF>` + `<VAL>` pairs within **`≤ 1.2 mm`** of each other.
   - **Never use board-wide label drift fallbacks** onto empty board corners: maintain **`1.5–2.0 mm` clear solder-mask label corridors** between `0603` passive rows and away from `F.Cu` jack/pot pin bands and IC pads during PCB placement so every component's value sits unambiguously next to its own pads.
5. **Never Set `fp.Value().SetVisible(True)` on `.SilkS`:**
   - Keep `fp.Value()` hidden on `F.Fab` / `B.Fab` across all `68` footprints so `analyze_pcb.py` (`values_visible_on_silk`) and `silk_annotator.py --inspect` (`Raw Values on Silk`) report **`0`** violations. Place all printed value/function tokens as `pcbnew.PCB_TEXT(fp)` (`fp_text user`) items on `.SilkS`.

---

## 2. `B.SilkS` Markup for JLCPCB SMT Inspection (`49` Parts)

To make comparing the physical populated PCB against JLCPCB's placement/BOM reports effortless on a narrow `30 mm` (`6 HP`) board:

### 2.1 Active ICs & Diodes (`<REF>` + `<VAL>` + Polarity on `B.SilkS`)

| Refs | Visible `B.SilkS` Text | Polarity & Orientation Graphics (`B.SilkS`) | Notes |
|---|---|---|---|
| `U1`, `U2` | **`U1` `TL074H`**, **`U2` `TL074H`** | Filled **`Ø 0.5 mm` Pin-1 dot** outside Pin `1` + Pin-1 end chamfer/notch | Keep text outside `SOIC-14` `B.Fab` body (`3.9 × 8.7 mm`) |
| `D1`–`D3`, `D5`, `D6` | **`D1` `1N4148WS`** … **`D6` `1N4148WS`** | Bold **`0.25 mm` cathode (`K`) bar** outside **Pad `1` (`K`)** | External bar remains visible after reflow; verify cathode direction vs. schematic |
| `D7`, `D8` | **`D7` `1N5819WS`**, **`D8` `1N5819WS`** | Bold **`0.25 mm` cathode (`K`) bar** outside **Pad `1` (`K`)** | **Opposite rail polarities:** `D7.K` → `+12V_FILT_IN`, `D8.K` → `-12V_IN` |
| `D9`, `D10`, `D11` | **`D9` `BAT54S`**, **`D10` `BAT54S`**, **`D11` `BAT54S`** | **`Ø 0.4 mm` Pin-1 dot** outside **Pin `1` (`A` / `-12V_PROT`)** | `SOT-23` 3-pin diode array (`Pin 2 = K` `+12V_PROT`, `Pin 3 = COM`) |

### 2.2 Resistors & Capacitors (`R1`–`R29`, `C3`–`C10` — Concise Value-Only on `B.SilkS`)

For all fixed resistors (`R1`–`R29`) and capacitors (`C3`–`C10`), hide `fp.Reference()` and `fp.Value()` on **`B.Fab`** and print **only the concise primary value token** (`compact_passive_value`) on **`B.SilkS`** adjacent to the footprint:

| `B.SilkS` Value Label | Footprint / Package | Qty | Designators (Kept on `B.Fab`) | Additional `B.SilkS` Markings |
|---|---|---:|---|---|
| **`10k`** | `0603` | `10` | `R1`, `R4`, `R6`, `R7`, `R9`, `R13`, `R22`, `R23`, `R25`, `R26` | None |
| **`100k`** | `0603` | `5` | `R5`, `R15`, `R16`, `R19`, `R20` | None |
| **`20k`** | `0603` | `2` | `R8`, `R10` | None |
| **`6.8k`** | `0603` | `2` | `R17`, `R18` | None |
| **`10R`** | `0603` | `2` | `R28`, `R29` | None |
| **`1k`** *(or `1k 1W` if space permits)* | `2512` | `2` | `R21`, `R24` | `2512` outline already distinguishes `1 W` output resistors from `0603` `R27` |
| **`1k`** | `0603` | `1` | `R27` | None |
| **`4.7k`** | `0603` | `1` | `R2` | None |
| **`150R`** | `0603` | `1` | `R12` | None |
| **`200k`** | `0603` | `1` | `R11` | None |
| **`1M`** | `0603` | `1` | `R3` | None |
| **`4.7M`** | `0603` | `1` | `R14` | None |
| **`47uF`** | `CP_Elec_6.3x5.4` | `2` | `C3`, `C4` | **Mandatory `+` and `-` symbols + chamfer/cathode stripe outside body:** `C3` (`+` = `+12V_PROT`, `-` = `GND`); **`C4` (`+` = `GND`, `-` = `-12V_PROT`)** |
| **`100nF`** | `0603` | `4` | `C5`, `C6`, `C7`, `C8` | Place adjacent to `U1` (`C5`, `C6`) and `U2` (`C7`, `C8`) supply pins `4`/`11` |
| **`22pF`** | `0603` | `1` | `C9` | None |
| **`100pF`** | `0603` | `1` | `C10` | None |

---

## 3. Dual-Sided (`F.SilkS` + `B.SilkS`) Markings for THT Parts, Power Header & Test Points

Every through-hole component must be readable from **both sides** so front-panel assembly (`F.Cu`), rear THT soldering (`B.Cu`), solder-side probing (`B.Cu`), and continuity checks from either side never require flipping a schematic open.

### 3.1 Rear `B.Cu` THT Components (`J4`, `C1`, `C2`, and `DNP` `TP1`–`TP8`)

| Refs | `B.SilkS` (Primary Mounting Side) | `F.SilkS` (Solder / Probe Side) | Polarity & Mechanical Graphics |
|---|---|---|---|
| **`J4`** (`2×5` IDC Power) | **`J4` `PWR`** + **`-12V RED`** bar beside Pins `1–2`, **`GND`** at Pins `3–8`, **`+12V`** at Pins `9–10`, Pin `1` dot | **`J4` `PWR`** + **`-12V`** bar at Pins `1–2`, **`GND`** at Pins `3–8`, **`+12V`** at Pins `9–10`, Pin `1` square pad indicator | Draw full shrouded header courtyard & key-notch facing board interior on `B.SilkS`; add solid `0.30 mm` stripe bar along the Pins `1–2` (`-12V`) edge on **both** layers |
| **`C1`, `C2`** (`1 µF 63 V` Film) | **`1uF`** (box outline on `B.SilkS`; `C1`, `C2` kept on `B.Fab`) | **`1uF`** (optional mirror label beside `P=5mm` pads if space clears controls) | Box film caps are non-polarized (`7.2 × 5.5 mm`, `P=5.0 mm`) |
| **`TP1`** | **`TP1` `+12V_PROT`** *(or `+12V`)* | **`TP1` `+12V_PROT`** *(or `+12V`)* | `Ø 2.8 mm` ring (`TestPoint_Keystone_5000-5004_Miniature`); place near `J4` |
| **`TP2`** | **`TP2` `-12V_PROT`** *(or `-12V`)* | **`TP2` `-12V_PROT`** *(or `-12V`)* | `Ø 2.8 mm` ring; place near `J4` |
| **`TP3`** | **`TP3` `GND`** | **`TP3` `GND`** | `Ø 2.8 mm` ring; place near `TP1`/`TP2`; use thermal-relief spokes on `GND` pour |
| **`TP4`** | **`TP4` `V_GAIN`** | **`TP4` `V_GAIN`** | Place within `≤ 3 mm` of `U1.1` (`V_GAIN`) |
| **`TP5`** | **`TP5` `V_RECT`** | **`TP5` `V_RECT`** | Place within `≤ 3 mm` of `U1.8` (`V_RECT`) |
| **`TP6`** | **`TP6` `V_ENV_BUF`** *(or `V_ENV`)* | **`TP6` `V_ENV_BUF`** *(or `V_ENV`)* | Place within `≤ 3 mm` of `U2.14` (`V_ENV_BUF`) |
| **`TP7`** | **`TP7` `V_OUT_BUF`** *(or `V_OUT`)* | **`TP7` `V_OUT_BUF`** *(or `V_OUT`)* | Place within `≤ 3 mm` of `U1.14` / `R21.1` |
| **`TP8`** | **`TP8` `V_INV_BUF`** *(or `V_INV`)* | **`TP8` `V_INV_BUF`** *(or `V_INV`)* | Place within `≤ 3 mm` of `U2.1` / `R24.1` |

*(Note on `silk_annotator.py --inspect` for dual-sided THTs: Keep `fp.Reference()` on the component's primary silk layer (`B.SilkS` for `J4`, `TP1`–`TP8`; `F.SilkS` for `J1`–`J3`, `RV1`–`RV4`, `D4`) paired with its primary `PCB_TEXT(fp)` value/function token within `≤ 1.2 mm`, and add secondary-side labels as `PCB_TEXT(board)` or `PCB_TEXT(fp)` within `≤ 6.0 mm` of the footprint pads so `SPLIT PAIR` only evaluates same-side pairs while both sides pass tether and collision checks.)*

### 3.2 Front `F.Cu` Panel Controls (`J1`–`J3`, `RV1`–`RV4`, `D4`)

| Refs | `F.SilkS` (Component Side) | `B.SilkS` (Solder Side) | Polarity & Pinout Markers (Both Sides) |
|---|---|---|---|
| **`J1`** (`WQP-PJ398SM`) | **`J1` `IN`** | **`J1` `IN`** | Mark `T` / `S` / `TN` (or `TN=GND`) near pins if space permits |
| **`J2`** (`WQP-PJ398SM`) | **`J2` `OUT`** | **`J2` `OUT`** | `TN=NC` |
| **`J3`** (`WQP-PJ398SM`) | **`J3` `INV_OUT`** *(or `INV`)* | **`J3` `INV_OUT`** *(or `INV`)* | `TN=NC` |
| **`RV1`** (`Alpha RD901F`) | **`RV1` `A100k`** *(+ `GAIN`)* | **`RV1` `A100k`** *(+ `GAIN`)* | **`1`** marker next to Pin `1` (`CCW` / `IN_POT_BOT`) on both sides to prevent wrong-taper pot swaps |
| **`RV2`** (`Alpha RD901F`) | **`RV2` `A50k`** *(+ `ATK`)* | **`RV2` `A50k`** *(+ `ATK`)* | **`1`** marker next to Pin `1` (`CCW` / `ATK_MID`) on both sides |
| **`RV3`** (`Alpha RD901F`) | **`RV3` `A1M`** *(+ `REL`)* | **`RV3` `A1M`** *(+ `REL`)* | **`1`** marker next to Pin `1` (`CCW` / `REL_MID`) on both sides |
| **`RV4`** (`Alpha RD901F`) | **`RV4` `B10k`** *(+ `OFFSET`)* | **`RV4` `B10k`** *(+ `OFFSET`)* | **`1`** marker next to Pin `1` (`CCW` / `OFF_TOP`, `+12V` leg) on both sides |
| **`D4`** (`3 mm` LED) | **`D4` `ENV`** *(or `LED`)* | **`D4` `ENV`** *(or `LED`)* | **`-` / `K`** at **Pin `1` (square pad)** and **`+` / `A`** at **Pin `2` (round pad)** on **both `F.SilkS` and `B.SilkS`** |

---

## 4. Board Metadata, JLCPCB QR Placeholder & `B.Fab` Fabrication Notes

1. **Board Name & Revision (`F.SilkS` & `B.SilkS` + KiCad Title Block):**
   - Set KiCad `title_block` `title` (`ENVELOPE FOLLOWER`) and `rev` (`Rev 1.0`).
   - Print **`ENVELOPE FOLLOWER`** and **`Rev 1.0`** (`0.80–1.00 mm` height, `0.15 mm` stroke) in clear margins on **`B.SilkS`** (and optionally `F.SilkS`) so every board revision is identifiable after assembly.
   - Add a brief rear assembly note on `B.SilkS` (if room permits) or `B.Fab`: `TP1-8: RH-5001 (DNP)`.
2. **JLCPCB 2D QR Code Keepout (`5.0 mm × 5.0 mm`):**
   - Reserve an unobstructed **`5.0 mm × 5.0 mm` solid filled silkscreen square** on **`B.SilkS`** (and optionally `F.SilkS`) away from pads, vias, `Edge.Cuts`, and labels for JLCPCB's automated assembly QR code.
3. **Complete `B.Fab` Fabrication Drawing Notes (`100%` `fab_notes_completeness`):**
   Include all 6 fabrication parameters checked by `analyze_pcb.py` on **`B.Fab`** (mirrored, `0.80 mm` height, `0.15 mm` stroke, placed cleanly beside the board outline or in a clear fabrication block):
   ```text
   FAB NOTES: 2L FR4 | THICKNESS: 1.6mm | 1oz CU
   FINISH: ENIG / HASL-LF | IPC-6012 CLASS 2
   SOLDER MASK: BLACK | SILK: WHITE | MIN TR/SP: 0.127mm
   DRILL TOL: +/-0.08mm | NO EDGE CUT
   ```
   *(Adjust `SOLDER MASK` color if ordering green/matte black/white PCB solder mask; keep high-contrast white silk on dark mask or dark silk on white mask.)*

---

## 5. Verification Checklist (Stage 5 Gate)

After generating or editing the KiCad `.kicad_pcb` layout, verify silkscreen and fabrication compliance with:

1. **Collision, Tether & Density-Adaptive Markup Inspection:**
   ```bash
   python3 .agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py --inspect <board>.kicad_pcb
   ```
   Confirm **`RESULT: PASS`**: `100%` labeled non-fiducial footprints (`0` unlabeled), `0` raw `fp.Value()` items on silk (`vals_on_silk == 0`), `0` text overlaps, `0` pad/keepout hits, `0` out-of-bounds hits, `0` tether drift hits, and `0` split pair hits.
2. **KiCad DRC Check:**
   ```bash
   kicad-cli pcb drc --refill-zones --format json --output /tmp/drc.json <board>.kicad_pcb
   ```
   Confirm `0` `silk_overlap` and `0` `silk_over_copper` violations.
3. **PCB Static & Documentation Audit:**
   ```bash
   python3 .agents/skills/kicad/scripts/analyze_pcb.py <board>.kicad_pcb --full --output /tmp/pcb_analysis.json
   ```
   Confirm `fab_notes_completeness` is **`100%`** (`pass`), `board_name` / `revision_marking` / `connector_labels` / `polarity_markers` checks pass in `silkscreen_completeness` (noting `ref_designators_visible` is intentionally `false` because `R*`/`C*` passives keep `Reference` on `B.Fab` with concise values on `B.SilkS`), and `values_visible_on_silk` is absent/empty.
4. **Top & Bottom 3D Render Inspection:**
   ```bash
   kicad-cli pcb render --side top -o /tmp/top.png --width 1200 --height 1600 --background transparent <board>.kicad_pcb
   kicad-cli pcb render --side bottom -o /tmp/bottom.png --width 1200 --height 1600 --background transparent <board>.kicad_pcb
   ```
   Visually verify on `/tmp/bottom.png` (`B.SilkS`) that every SMD passive (`R1`–`R29`, `C3`–`C10`) displays its legible concise value outside package bodies, `C3`/`C4`/`D1`–`D11`/`U1`–`U2` polarity markers are clear, `J4` `-12V RED` stripe matches Pins `1–2`, `TP1`–`TP8` labels read clearly on both sides, and the `5 × 5 mm` QR square sits in a clean region.
