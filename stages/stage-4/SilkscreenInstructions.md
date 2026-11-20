# Envelope Follower (Improved Eurorack Revision) — PCB Silkscreen & Fabrication Markup Instructions

Complete silkscreen, polarity, value-marking, dual-sided THT/test-point, and fabrication-drawing specification derived from [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md) and [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md).

---

## 1. Purpose & Design Goals

1. **JLCPCB Visual Assembly & BOM Cross-Verification:** Mark every populated component's **Reference Designator (`<REF>`)** alongside a **concise required value / tolerance / power / taper token (`<VAL>`)** on the component's primary silkscreen layer so placed parts in JLCPCB PCBA placement previews, DFM photos, and bench inspections can be verified directly against [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md) without lookup guesswork (e.g., distinguishing `100k 0.1%` vs. `100k`, `1k 1W` vs. `1k`, `15pF C0G` vs. `100nF`, `B5819W` vs. `1N4148W`, `BAT54S` vs. `BAV99`, and `A100k`/`A50k`/`A1M`/`B10k` pot tapers).
2. **Dual-Sided Test Point & Through-Hole Accessibility:** Mark all **8 optional `DNP` test points (`TP1`–`TP8`, Ronghe `RH-5001`)** on **both `F.SilkS` and `B.SilkS`** with net labels, and add secondary-side labels for `J4` (Eurorack power header), `RV1`–`RV4`, `J1`–`J3`, `LED1`, and `C1`/`C2`/`C9` so bring-up probing and hand-soldering can be performed cleanly from either side of the board.
3. **Zero DRC / Analyzer / Assembly Clutter Violations:** Keep KiCad's default `fp.Value()` field hidden on `.Fab` while rendering concise values as `fp_text user` (`PCB_TEXT(fp)`) pairs with `>= 0.35 mm` spacing, zero pad/mask overlap (`SK-001`), zero text-on-text collisions, and `100%` complete `B.Fab` fabrication notes (`fab_notes_completeness`).

---

## 2. Eurorack Sandwich Layer Convention & KiCad Text Standards

### 2.1 Component Side Assignment (Single-Sided JLCPCB Economic SMT)
- **Back Side (`B.Cu` / `B.SilkS`) — Primary SMD Assembly, Power & Test-Point Access:**
  - All **`53` SMD components** (`U1`, `U2`, `D1`–`D10`, `C3`–`C8`, `C10`–`C17`, `R1`–`R21`, `R24`–`R29`) reside on **`B.Cu`** so JLCPCB Economic PCBA remains single-sided SMT (`$0` dual-side setup surcharge) and the front face stays flush behind the `10.5 mm` Eurorack panel standoff.
  - `J4` (`2×5` IDC header) is mounted on `B.Cu`; `TP1`–`TP8` (`RH-5001`, `DNP`) are optionally soldered from `B.Cu` so they remain probeable when the front panel is bolted on.
- **Front Side (`F.Cu` / `F.SilkS`) — Panel Controls & Box Film Capacitors:**
  - Panel-mounted THT hardware (`RV1`–`RV4`, `J1`–`J3`, `LED1`) mounts on `F.Cu` at `10.5 mm` panel standoff.
  - `C1`, `C2`, `C9` (`WIMA MKS2` `1 µF 63 V`, `10.0 mm` tall) mount THT on `F.Cu` (or `B.Cu` for extra panel clearance), and carry dual-sided silkscreen markings.

### 2.2 Typography, Clearances & `B.SilkS` Mirroring Rules
| Parameter | Requirement | Notes / Rationale |
|---|---|---|
| **Text Height** | **`>= 0.80 mm`** (`0.80 mm` for `0603`/dense areas; `1.00–1.20 mm` for headers, jacks, title) | Meets JLCPCB minimum legible silkscreen height (`0.80 mm`) |
| **Stroke Thickness** | **`>= 0.15 mm`** (`0.25–0.30 mm` for cathode bars & `-12V` power stripe) | Prevents broken silkscreen ink on black/matte solder mask |
| **Rotations Allowed** | **`0°` or `90°` only** | Consistent left-reading / bottom-reading orientation across all 73 parts |
| **`<REF>` ↔ `<VAL>` Gap** | **`>= 0.35 mm`** between true KiCad `GetBoundingBox()` extents | Use actual stroke bounding boxes (`+0.06 mm` pad), not fixed char-width estimates (wide glyphs `R, V, T, W` otherwise collide) |
| **Silk-to-Pad / Mask Clearance** | **`>= 0.25 mm`** outside all copper pads and `F.Mask` / `B.Mask` openings | Guarantees zero `SK-001` (`silk_over_copper`) warnings and keeps solder paste clean |
| **Silk-to-Outline Clearance** | **`>= 0.20 mm`** outside footprint silk borders & neighbor text (`>= 0.20 mm` text-to-text) | Prevents `<REF>`/`<VAL>` from crossing `SOIC-14`, `CP_Elec`, pot, or jack outlines |
| **Board Edge Clearance** | **`>= 0.45 mm`** inside `Edge.Cuts` | Safely clears JLCPCB `0.30–0.50 mm` routing/V-cut edge margin |
| **`B.SilkS` Mirroring** | **`SetMirrored(True)`** on all `B.SilkS` text; place `<REF>` to visual left (`-X` in board coords) and `<VAL>` to visual right (`+X`) for `0°` horizontal pairs | Ensures `<REF> <VAL>` always reads naturally **left-to-right** when viewing the back (`B.Cu`) of the PCB |

### 2.3 KiCad Field Visibility Architecture (`fp.Reference()` vs. `fp.Value()` vs. `fp_text user`)
- **`fp.Reference()`:** Visible (`SetVisible(True)`) on the component's primary silkscreen layer (`B.SilkS` for `B.Cu` SMDs & `J4`; `F.SilkS` for `F.Cu` panel parts) for **`73 / 73` (`100%`)** footprints.
- **`fp.Value()`:** Hidden (`SetVisible(False)`) on the corresponding fabrication layer (`B.Fab` or `F.Fab`) so automated PCB checks (`analyze_pcb.py`) do not flag raw verbose KiCad values (`TL074HIDR`, `Potentiometer_Alps_RK09K_Single_Vertical`) as silkscreen clutter.
- **Concise Value Label (`fp_text user` / `PCB_TEXT(fp)`):** Add a visible `fp_text user` item on `.SilkS` paired beside `fp.Reference()` displaying the exact concise JLCPCB verification token from **Section 4** below.
- **Secondary-Side THT / TP Labels (`PCB_TEXT(board)`):** For `TP1`–`TP8` and key THT parts (`J4`, `RV1`–`RV4`, `J1`–`J3`, `LED1`, `C1`/`C2`/`C9`), place mirrored/non-mirrored board-level silkscreen labels on the opposite side as well.

---

## 3. Mandatory Polarity, Pin-1 & Orientation Graphics (External to Component Bodies)

All polarity and Pin-1 graphics **must sit outside component body outlines and solder-mask openings** so they remain clearly visible after reflow and wave/hand soldering in JLCPCB inspection photos.

| Component Group | Designators | Package / Footprint | Required External Silkscreen Graphic | Critical Orientation / Verification Note |
|---|---|---|---|---|
| **Op-Amps** | `U1`, `U2` | `SOIC-14` (`3.9×8.7mm`) | Solid filled **Pin-1 dot** (`r = 0.25–0.35 mm`) + `"1"` or U-notch outside Pad 1 | Watch JLCPCB `SOIC-14` rotation convention; Pin 1 (`U1A OUT` / `U2A OUT`) must align unambiguously to the dot |
| **Signal & Power Diodes** | `D1`–`D5`, `D9`, `D10` | `D_SOD-123` | Bold **`0.25 mm` external cathode bar (`\|`) + `"K"`** outside **Pad 1 (`K`)** | **Check `D4` vs. `D5` carefully:** `D4.K` faces `+12V`; `D5.K` faces `-12V_IN` (`J4` Pins 1–2)! Also `D9.K` → `DET_OP_OUT`, `D10.K` → `LED_ANODE` |
| **Dual ESD Clamp Arrays** | `D6` (`BAV99`), `D7`/`D8` (`BAT54S`) | `SOT-23` | Solid **Pin-1 dot (`A1`)** outside Pad 1 (`-12V`) + asymmetric 3-pad outline | `SOT-23` commonly needs `+180°` CPL rotation correction at JLCPCB; Pin 1 (`A1`, `-12V`), Pin 2 (`K2`, `+12V`), Pin 3 (`K1/A2`, signal) |
| **SMD Electrolytics** | `C3`, `C4`, `C11`, `C13` | `CP_Elec_6.3x5.4` | Bold **`+`** symbol + chamfered base outline outside **Pin 1 (`+`)** pad | **Negative-rail trap (`C4`, `C13`):** `C4.1 (+)` connects to **`GND`** (`C4.2 -` → `-12V`); `C13.1 (+)` connects to **`GND`** (`C13.2 -` → `OFFSET_BOT`). Verify `+` faces `GND`! |
| **3 mm Indicator LED** | `LED1` | `LED_D3.0mm` | **`+`** outside **Pin 2 (`A`)** and **`-`** + flat edge outside **Pin 1 (`K`)** on **both `F.SilkS` & `B.SilkS`** | Polarity must remain readable from `B.Cu` when bending/soldering leads to the `10.5 mm` front panel |
| **9 mm Vertical Pots** | `RV1`–`RV4` | `Potentiometer_Alps_RK09K_Single_Vertical` | **`"1"`** (`CCW`) marker at Pad 1 on **both `F.SilkS` & `B.SilkS`** | Shaft-side convention: `1 = CCW`, `2 = Wiper`, `3 = CW` (`RV1` CW=+Gain, `RV2` CW=Slower Atk, `RV3` CW=Slower Rel, `RV4` CW=+OUT) |
| **3.5 mm Mono Jacks** | `J1`–`J3` | `WQP-PJ398SM` | Jack function (`IN`, `OUT`, `INV_OUT`) + **`T` / `S` / `TN`** pin tags on `F.SilkS` & `B.SilkS` | Keeps `J1.TN → GND` distinct from `J2.TN`/`J3.TN → NC` |
| **Eurorack Power Header** | `J4` | `IDC-Header_2x05_P2.54mm_Vertical` | Keyed shroud notch + **`0.30 mm` solid `RED -12V` bar** at Pins `1–2`, **`GND`** (`3–8`), **`+12V`** (`9–10`) on **both `B.SilkS` & `F.SilkS`** | Prevents reversed ribbon insertion even with unshrouded cables; dual-sided labels aid front-side probing and `B.Cu` soldering |

---

## 4. Complete Component-by-Component Silkscreen Table (All 73 Footprints)

### 4.1 JLCPCB SMT Components (`53` Parts on `B.Cu` / `B.SilkS`)

Every `B.SilkS` pair below uses **`<REF>` + `<VAL>`** (`SetMirrored(True)`, `>= 0.80 mm` height, `>= 0.15 mm` stroke, `>= 0.35 mm` gap). Critical precision/wattage/dielectric suffixes (`0.1%`, `1W`, `C0G`, `50V`) are included so JLCPCB visual review can distinguish visually identical `0603` packages at a glance.

| Refs | Qty | Primary Layer | Visible `<REF>` | Silkscreen `<VAL>` Token (`fp_text user`) | BOM Target (`EnvelopeFollowerBOM.md`) | Polarity / JLCPCB Visual Check Notes |
|---|---:|---|---|---|---|---|
| `U1`, `U2` | 2 | `B.SilkS` | `U1`, `U2` | `TL074H` | `TL074HIDR` (`C2878713`) | External Pin-1 dot outside Pad 1 |
| `D1`, `D2`, `D3`, `D9`, `D10` | 5 | `B.SilkS` | `D1`, `D2`, `D3`, `D9`, `D10` | `1N4148W` | `1N4148W` (`C81598`) | External `K` bar at Pad 1 (`D1.K→RECT_SUM`, `D2.K→RECT_OUT_N`, `D3.K→R9`, `D9.K→DET_OP_OUT`, `D10.K→LED_ANODE`) |
| `D4`, `D5` | 2 | `B.SilkS` | `D4`, `D5` | `B5819W` | `B5819W SL` (`C8598`) | External `K` bar at Pad 1 (**opposing directions:** `D4.K→+12V`, `D5.K→-12V_IN`) |
| `D6` | 1 | `B.SilkS` | `D6` | `BAV99` | `BAV99,215` (`C2500`) | External Pin-1 dot (`A1 → -12V`); distinct from `D7`/`D8` |
| `D7`, `D8` | 2 | `B.SilkS` | `D7`, `D8` | `BAT54S` | `BAT54S,215` (`C47546`) | External Pin-1 dot (`A1 → -12V`); verify `SOT-23` `+180°` CPL rotation |
| `C3`, `C4`, `C11`, `C13` | 4 | `B.SilkS` | `C3`, `C4`, `C11`, `C13` | `22uF 50V` | `RVT1H220M0605` (`C970664`) | External `+` at Pin 1 (`C3.1→+12V`, **`C4.1→GND`**, `C11.1→OFFSET_TOP`, **`C13.1→GND`**) |
| `C5`–`C8`, `C12`, `C14`, `C15` | 7 | `B.SilkS` | `C5`–`C8`, `C12`, `C14`, `C15` | `100nF` | `CC0603KRX7R9BB104` (`C14663`) | Non-polarized `0603` X7R (`50 V`); place `C5`–`C8` `< 3–5 mm` from `U1`/`U2` pins 4 & 11 |
| `C10`, `C17` | 2 | `B.SilkS` | `C10`, `C17` | `15pF C0G` | `CL10C150JB8NNNC` (`C1644`) | Class I C0G feedback comp across `R29` (`C10`) and `R8` (`C17`) |
| `C16` | 1 | `B.SilkS` | `C16` | `47pF C0G` | `CL10C470JB8NNNC` (`C1671`) | Class I C0G lead comp on `U2C` (`DET_OP_OUT` ↔ `DET_FB`) |
| `R1`, `R26` | 2 | `B.SilkS` | `R1`, `R26` | `1M` | `0603WAF1004T5E` (`C22935`) | `0603` 1% thick film (bleed/reference) |
| `R2`, `R13`–`R15`, `R17`, `R18`, `R20`, `R27` | 8 | `B.SilkS` | `R2`, `R13`–`R15`, `R17`, `R18`, `R20`, `R27` | `10k` | `0603WAF1002T5E` (`C25804`) | `0603` 1% thick film |
| **`R3`, `R4`, `R5`, `R6`, `R7`** | 5 | `B.SilkS` | `R3`, `R4`, `R5`, `R6`, `R7` | **`100k 0.1%`** | `RT0603BRD07100KL` (`C122538`) | **Precision FWR thin-film — must stay visibly distinct from `R29` (`100k` 1%)!** |
| **`R8`** | 1 | `B.SilkS` | `R8` | **`200k 0.1%`** | `RT0603BRE07200KL` (`C136955`) | **Precision FWR feedback thin-film (`1.000×` gain)** |
| `R9` | 1 | `B.SilkS` | `R9` | `470R` | `0603WAF4700T5E` (`C23179`) | Pre-`C2` attack surge limiter |
| `R10` | 1 | `B.SilkS` | `R10` | `22k` | `0603WAF2202T5E` (`C31850`) | Minimum release discharge resistor |
| `R11`, `R12`, `R28` | 3 | `B.SilkS` | `R11`, `R12`, `R28` | `1k` | `0603WAF1001T5E` (`C21190`) | `0603` 1% thick film (`OFFSET` RC & `U1A+` clamp limit) |
| **`R16`, `R19`, `R25`** | 3 | `B.SilkS` | `R16`, `R19`, `R25` | **`1k 1W`** | `25121WF1001T4E` (`C54315`) | **`2512` 1 W fault-rated I/O resistor — distinct from `0603` `1k`!** |
| `R21` | 1 | `B.SilkS` | `R21` | `1.5k` | `0603WAF1501T5E` (`C22843`) | `LED1` V-to-I `R_set` |
| `R24` | 1 | `B.SilkS` | `R24` | `4.7k` | `0603WAF4701T5E` (`C23162`) | `GAIN` floor resistor |
| `R29` | 1 | `B.SilkS` | `R29` | `100k` | `0603WAF1003T5E` (`C25803`) | `U1A` `11.0×` feedback (`1%` thick film, vs. `R3`–`R7` `0.1%`) |

*(Note: `R22` and `R23` do not exist in this revision per IMP-06.)*

### 4.2 Populated Through-Hole Hardware (`12` Parts on `F.Cu` / `B.Cu`, Dual-Sided Labels)

| Refs | Qty | Primary Silk | Primary Label (`<REF>` + `<VAL>`) | Secondary Silk Label (`PCB_TEXT(board)`) | BOM Target | Mechanical / Polarity Notes |
|---|---|---|---|---|---|---|
| `C1`, `C2`, `C9` | 3 | `F.SilkS` *(or `B.SilkS`)* | `C1 1uF FILM`, `C2 1uF FILM`, `C9 1uF FILM` | Mirror `C1 1uF`, `C2 1uF`, `C9 1uF` on opposite side | `WIMA MKS2` (`C92673`) | `7.2×5.0 mm` box outline; confirms film dielectric (never MLCC) on `C1`/`C2`/`C9` |
| `RV1` | 1 | `F.SilkS` | `RV1 A100k` *(+ `GAIN`)* | `B.SilkS`: `RV1 GAIN A100k` | `A100k` 9 mm pot | Mark Pin `1` (`CCW`) on both sides |
| `RV2` | 1 | `F.SilkS` | `RV2 A50k` *(+ `ATK`)* | `B.SilkS`: `RV2 ATK A50k` | `A50k` 9 mm pot | Mark Pin `1` (`CCW`) on both sides |
| `RV3` | 1 | `F.SilkS` | `RV3 A1M` *(+ `REL`)* | `B.SilkS`: `RV3 REL A1M` | `A1M` 9 mm pot | Mark Pin `1` (`CCW`) on both sides |
| `RV4` | 1 | `F.SilkS` | `RV4 B10k` *(+ `OFFSET`)* | `B.SilkS`: `RV4 OFFSET B10k` | `B10k` 9 mm pot (`C2839839`) | Mark Pin `1` (`CCW`) on both sides |
| `LED1` | 1 | `F.SilkS` | `LED1 ENV` | `B.SilkS`: `LED1 ENV` + `+` / `-` | `3mm Yellow` (`C85160`) | External `+` (`A`, Pin 2) & `-` (`K`, Pin 1) on **both sides** |
| `J1` | 1 | `F.SilkS` | `J1 IN` | `B.SilkS`: `J1 IN` + `T`/`TN`/`S` | `WQP-PJ398SM` | `J1.TN → GND` |
| `J2` | 1 | `F.SilkS` | `J2 OUT` | `B.SilkS`: `J2 OUT` + `T`/`S` | `WQP-PJ398SM` | `J2.TN → NC` |
| `J3` | 1 | `F.SilkS` | `J3 INV_OUT` | `B.SilkS`: `J3 INV_OUT` + `T`/`S` | `WQP-PJ398SM` | `J3.TN → NC` |
| `J4` | 1 | `B.SilkS` | `J4 ±12V PWR` | `F.SilkS`: `J4` + **`-12V RED`**, `GND`, **`+12V`** | `IDC2.54-2*5PZ` (`C53207560`) | Bold `0.30 mm` stripe bar next to Pins `1–2` (`-12V_IN`) on **both sides** |

### 4.3 Optional `DNP` Through-Hole Test Points (`8` Parts: `TP1`–`TP8` — Mandatory Dual-Sided Marking)

All test points use KiCad footprint `TestPoint:TestPoint_Keystone_5000-5004_Miniature` for **Ronghe `RH-5001` (`C5199801`, `DNP`)**. Because the bare plated holes can be needle-probed from the front before panel assembly or optionally hand-soldered and clipped from the back (`B.Cu`) with the panel mounted, **every test point MUST carry its reference and net name on BOTH `B.SilkS` and `F.SilkS`**:

| Ref | Net Name | `B.SilkS` Label (`SetMirrored(True)`) | `F.SilkS` Label (`PCB_TEXT`) | BOM / Silkscreen Value Note |
|---|---|---|---|---|
| **`TP1`** | `GND` | `TP1 GND` | `TP1 GND` | `RH-5001 (DNP)` — scope ground clip anchor |
| **`TP2`** | `+12V` | `TP2 +12V` | `TP2 +12V` | `RH-5001 (DNP)` — protected `+11.65 V` rail (post-`D4`) |
| **`TP3`** | `-12V` | `TP3 -12V` | `TP3 -12V` | `RH-5001 (DNP)` — protected `-11.65 V` rail (post-`D5`) |
| **`TP4`** | `PREAMP_OUT` | `TP4 PREAMP` | `TP4 PREAMP` | `RH-5001 (DNP)` — Stage 1 `U1A` output (`0.494×`–`11.0×`) |
| **`TP5`** | `FWR_OUT` | `TP5 FWR_OUT` | `TP5 FWR_OUT` | `RH-5001 (DNP)` — Stage 3 `U1C` `1.000×` FWR output |
| **`TP6`** | `ENV_NODE` | `TP6 ENV_NODE` | `TP6 ENV_NODE` | `RH-5001 (DNP)` — Stage 4 `U2D` buffered envelope (avoids loading `C2`) |
| **`TP7`** | `ENV_OUT` | `TP7 ENV_OUT` | `TP7 ENV_OUT` | `RH-5001 (DNP)` — Stage 5 `U1D` output (pre-`R16`/`D7`) |
| **`TP8`** | `INV_OUT_RAW` | `TP8 INV_RAW` | `TP8 INV_RAW` | `RH-5001 (DNP)` — Stage 6 `U2A` output (pre-`R19`/`D8`) |

*(Also place a compact legend on `B.SilkS` near the test-point cluster or fab summary: `TP1-TP8: RH-5001 (DNP)` so assembly operators know empty test-point holes are intentional.)*

---

## 5. Board-Level Markings, Fiducials, QR Placeholders & `B.Fab` Notes

1. **Board Identification & Revision (`F.SilkS` & `B.SilkS`):**
   - Place clear board title + revision text (e.g., `ENVELOPE FOLLOWER REV 1.0`, `1.00–1.20 mm` height, `0.15–0.20 mm` thickness) on `B.SilkS` (and optionally `F.SilkS`), plus populate KiCad's title block `rev` field so `analyze_pcb.py` `missing_board_name` and `missing_revision` checks pass.
2. **JLCPCB QR Code / 2D Barcode Placeholders (`5.0 × 5.0 mm`):**
   - Draw a **`5.0 × 5.0 mm` solid filled silkscreen square** on **`B.SilkS`** (and **`F.SilkS`** if clear of controls) in a pad-free area so JLCPCB can swap it with their production tracking barcode without obscuring part markings or crossing exposed pads.
3. **SMT Assembly Fiducials (`FD-001`):**
   - Place **`>= 3` global fiducials** on the SMT side (`B.Cu`, `1.0 mm` bare copper pad, `2.0 mm` solder-mask opening, `>= 5 mm` inside board edges) and seed their mask openings into silkscreen keepouts so no text touches fiducials.
4. **Complete `B.Fab` Fabrication Notes (`100%` `fab_notes_completeness`):**
   - Place mirrored text on **`B.Fab`** (`0.80 mm` height, `0.15 mm` thickness) containing all 6 analyzer-checked metadata items:
     ```text
     FAB NOTES: 2L FR4 | THICKNESS: 1.6mm | 1oz CU
     FINISH: ENIG / HASL-LF | IPC-6012 CLASS 2
     SOLDER MASK: BLACK | SILK: WHITE | MIN TR/SP: 0.127mm
     DRILL TOL: +/-0.08mm | NO EDGE CUT
     ```
     *(Adjust `SOLDER MASK:` / `FINISH:` strings only if ordering a different board color or finish, keeping explicit `FR4`, `THICKNESS`, `1oz CU`, `ENIG`/`HASL`, `IPC-6012 CLASS 2`, and `SOLDER MASK` tokens present.)*

---

## 6. Automated Verification & Sign-Off Checklist

When generating or inspecting the KiCad `.kicad_pcb` (e.g., via [`silk_annotator.py`](./.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py)), verify **all** checks pass before ordering from JLCPCB:

```bash
# 1. Inspect silkscreen visibility, overlaps, pad hits, and board-edge clearance
python3 .agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py --inspect EnvelopeFollower.kicad_pcb

# 2. Run KiCad DRC (confirm 0 silk_overlap and 0 silk_over_copper errors/warnings)
kicad-cli pcb drc --refill-zones --format json --output /tmp/drc.json EnvelopeFollower.kicad_pcb

# 3. Run full PCB static/DFM analysis (confirm 100% refs_visible_on_silk, 0 SK-001, 100% fab_notes_completeness)
python3 .agents/skills/kicad/scripts/analyze_pcb.py EnvelopeFollower.kicad_pcb --full --output /tmp/pcb_analysis.json

# 4. Visually inspect top and bottom 3D renders
kicad-cli pcb render --side top    -o /tmp/top.png    --width 1200 --height 1600 EnvelopeFollower.kicad_pcb
kicad-cli pcb render --side bottom -o /tmp/bottom.png --width 1200 --height 1600 EnvelopeFollower.kicad_pcb
```

- [ ] **`73 / 73` visible `<REF>` fields** (`refs_visible_on_silk = 100%`) and **`0` raw `fp.Value()` clutter warnings** (`values_visible_on_silk = []`), with concise `fp_text user` values paired cleanly beside every component.
- [ ] **All `TP1`–`TP8` labels readable on both `F.SilkS` and `B.SilkS`** (`TP1 GND` … `TP8 INV_RAW`) and `TP1-TP8: RH-5001 (DNP)` legend present.
- [ ] **`100k 0.1%` (`R3`–`R7`), `200k 0.1%` (`R8`), `1k 1W` (`R16`/`R19`/`R25`), `15pF C0G` (`C10`/`C17`), and `47pF C0G` (`C16`)** visually verified against JLCPCB PCBA placement preview.
- [ ] **Polarity verified outside bodies:** `U1`/`U2` Pin-1 dots, `D1`–`D5`/`D9`/`D10` cathode bars (`D4` vs. `D5` opposite orientations), `D6`–`D8` Pin-1 dots, `C3`/`C4`/`C11`/`C13` `+` markers (`C4`/`C13` `+` → `GND`), `LED1` `+`/`-`, `RV1`–`RV4` Pin `1`, and `J4` `-12V RED` bar.
- [ ] **`0` `silk_overlap`, `0` `silk_over_copper` (`SK-001`), `0` out-of-bounds silk items, and `100%` `fab_notes_completeness`.**
