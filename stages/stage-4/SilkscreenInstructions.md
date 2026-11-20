# Silkscreen & Fabrication Markup Instructions

Silkscreen, assembly-layer (`.Fab`), polarity, and JLCPCB DFM/QR markup specification for [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md) and [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md), designed for a narrow **6 HP (`30.00 × 108.00 mm`) 2-layer Eurorack PCB** assembled via **JLCPCB Economic single-sided SMT (`F.Cu`)** plus post-PCBA manual through-hole mounting.

> **Tooling Alignment:** Rules below align directly with [`.agents/skills/kicad-silkscreen-markup/SKILL.md`](./.agents/skills/kicad-silkscreen-markup/SKILL.md) (`silk_annotator.py`), [`.agents/skills/jlcpcb/SKILL.md`](./.agents/skills/jlcpcb/SKILL.md), and [`.agents/skills/kicad/scripts/analyze_pcb.py`](./.agents/skills/kicad/scripts/analyze_pcb.py).

---

## 1. Board Architecture & Side Assignment

| Layer / Side | Components Placed | Silkscreen Density & Strategy |
|---|---|---|
| **`F.Cu` / `F.SilkS` (Front / JLCPCB SMT Top)** | **49 SMT parts** (`U1`, `U2`, 30 SMT resistors, 9 SMT capacitors, 8 SMT diodes) + **8 panel THT parts** (`J1`–`J3`, `RV1`–`RV4`, `D4`) + **3 SMT fiducials** | **High density (`57` functional footprints / `32.4 cm²` ≈ `1.76 / cm²`, `≥ 35` parts/side).** Mandatory dense-side rule: concise **value-only** silkscreen labels on fixed `R*`/`C*` passives; `<REF> + <VAL/FUNC>` pairs on `U*`, `D*`, `J*`, `RV*`. |
| **`B.Cu` / `B.SilkS` (Rear / Solder Side)** | **3 rear THT parts** (`J4` `2×5` IDC header, `C1` & `C2` `1 µF` box film) + **8 DNP THT test points** (`TP1`–`TP8`) + solder-side pins of `J1`–`J3`, `RV1`–`RV4`, `D4` | **Dual-sided serviceability.** Rear THTs (`J4`, `C1`, `C2`), panel THTs (`J1`–`J3`, `RV1`–`RV4`, `D4`), and all test points (`TP1`–`TP8`) receive legible mirrored `B.SilkS` labels for rear bench probing and hand soldering. |
| **`F.Fab` / `B.Fab` (Assembly & Fab Layers)** | All **68** component references + `B.Fab` board fabrication notes | Keeps every passive reference designator (`R1`–`R20`, `R_PWR_*`, `R16A/B`, `C_DEC*`, `C3`–`C4`, etc.) intact for Assembly PDF exports (`0.1%` vs. `1%` verification) without crowding `.SilkS`. |

---

## 2. Global Silkscreen Geometry, Keepout & Tether Rules

1. **Typography Minimums (JLCPCB & `silk_annotator.py`)**:
   - Text height: **`≥ 0.80 mm`** (`SILK_HEIGHT = 0.80 mm`; up to `1.00–1.20 mm` for `J4` rail headers or board title if space allows).
   - Stroke thickness: **`≥ 0.15 mm`** (`SILK_THICKNESS = 0.15 mm`; `0.20–0.25 mm` for diode cathode bars and `J4` Pin-1/stripe bars).
   - Rotations: **`0°` and `90°` only** (never inverted `180°`, `270°`, or arbitrary angles).
   - Exact bounding-box measurement: Always measure true KiCad stroke text via `pcbnew.PCB_TEXT.GetBoundingBox()` (`+0.06 mm` safety padding in `SilkGrid.measure_text()`), never character-width heuristics.

2. **Mirroring on `B.SilkS`**:
   - All `B.SilkS` text uses `SetMirrored(True)`. Because `+X` in board coordinates appears to the visual left from the back of the board, `place_ref_val_pair()` automatically applies `sign = -1.0` on `B.SilkS` (`+1.0` on `F.SilkS`) so `<REF> <VAL>` pairs always read left-to-right on both sides.

3. **Keepouts & Clearances (Zero DRC Errors)**:
   - **No `silk_over_copper`**: Block all copper pads and solder-mask openings (`F.Mask` / `B.Mask` + **`0.25 mm`** clearance), plus fiducial mask openings (`±1.25 mm` around each `2.0 mm` opening).
   - **No `silk_overlap`**: Maintain **`≥ 0.20 mm`** clearance between adjacent placed text labels and **`≥ 0.20 mm`** outside non-text `.SilkS` graphics (pot bodies, jack outlines, IC silk borders).
   - **SMD `.Fab` Body Keepout (`block_smd_fab=True`)**: Block every SMD footprint's `F.Fab`/`B.Fab` body interior (`+0.05 mm` margin) so labels never land under `SOIC-14` (`U1`/`U2`), `SOD-123`/`SOD-323`/`SOT-23` diodes, or `CP_Elec_6.3x5.4` cans (`C3`/`C4`) after reflow.
   - **Board-Edge Margin**: Keep all silkscreen ink **`≥ 0.45 mm`** inside `Edge.Cuts` (`SILK_EDGE_CLEARANCE = 0.45 mm`; keep copper `≥ 0.30 mm` min / `0.50 mm` recommended).

4. **Strict Local Tethering (No Board-Wide Fallback Scans)**:
   - **SMD edge distance**: **`≤ 3.5 mm`** (`MAX_SMD_TETHER_MM`) from own footprint bounding box.
   - **THT edge distance**: **`≤ 6.0 mm`** (`MAX_THT_TETHER_MM`) from own footprint bounding box.
   - **`<REF>`/`<VAL>` pair split**: Gap **`≥ 0.35 mm`** and **`≤ 1.20 mm`** (`MAX_PAIR_SPLIT_MM`) between `<REF>` and `<VAL>` on the same side.
   - Never widen search radii across the board; if a label cannot fit within `3.5 mm` (`6.0 mm` THT), expand passive row spacing (`≥ 1.5–2.0 mm` label corridors) in layout instead.

5. **KiCad Field Visibility Discipline**:
   - **Every component (`68/68`)**: Set `fp.Value().SetVisible(False)` on its `.Fab` layer (`0` `values_visible_on_silk` warnings); all visible silkscreen value tokens are placed cleanly as collision-checked `fp_text user` (`pcbnew.PCB_TEXT(fp)`) items.
   - **Fixed Resistors & Capacitors (`41/41`: `R*`, `C*`, excluding `RV*`)**: Set `fp.Reference().SetVisible(False)` on `.Fab` so only the concise value token prints on `.SilkS`, while `.Fab` assembly drawings retain the exact reference designator.
     - *Implementation Caution (`silk_annotator.py`):* `is_passive_ref()` uses regex `^[RC]\d+$`, which matches `R1`–`R20` and `C1`–`C4` but **not** suffixed/named passives (`R_PWR_P/N`, `R16A/B`, `R19A/B`, `R8A/B`, `R_IN_PROT`, `R_IN_BUF`, `R_GAIN_MIN`, `R_GAIN_FAIL`, `R_ATK_MIN`, `R_ENV_PROT`, `R_LED`, `C_DEC1`–`C_DEC4`, `C_HF`, `C_OUT1`, `C_OUT2`). In the layout/markup script, explicitly call `place_val_only()` (or pass `val_only=True` whenever `ref.startswith(("R", "C")) and not ref.startswith("RV")`) so **all 30 resistors and all 11 capacitors** follow the value-only rule uniformly.
   - **Fiducials (`FID*`)**: Hide both `fp.Reference()` and `fp.Value()` on `.Fab`; zero silkscreen text.

---

## 3. Component Label Schedule (All 68 Footprints)

### 3.1 Fixed Resistors & Capacitors (`41` Parts — Concise Value-Only on `.SilkS`, Ref on `.Fab`)

Secondary tolerance (`0.1%`), wattage (`0.5W`), dielectric (`C0G`, `X7R`), and voltage (`50V`, `100V`) suffixes are stripped on `.SilkS` so labels fit in tight `1.5–2.0 mm` corridors and remain directly comparable against the `Comment` column in JLCPCB's PCBA BOM/CPL preview.

| Group | Refs (Kept on `.Fab`) | Qty | Mount Layer | BOM Comment / Value | Silkscreen Text (`.SilkS`) | JLCPCB Comparison & Disambiguation Notes |
|---|---|---:|---|---|---|---|
| **Rail Damping** | `R_PWR_P`, `R_PWR_N` | 2 | `F.Cu` (SMT `1206`) | `10R` | **`10R`** (`F.SilkS`) | Unique `1206` value (`C17903`) |
| **Attack Floor** | `R_ATK_MIN` | 1 | `F.Cu` (SMT `0603`) | `470R` | **`470R`** (`F.SilkS`) | `0603` (`C23179`); smaller pads than `1210` clash resistors |
| **Output Clash** | `R16A`, `R16B`, `R19A`, `R19B` | 4 | `F.Cu` (SMT `1210`) | `470R 0.5W` | **`470R`** (`F.SilkS`) | `1210` `0.5 W` (`C333193`); footprint visually separates from `R_ATK_MIN` |
| **1 kΩ Group** | `R_IN_PROT`, `R_IN_BUF`, `R_GAIN_MIN`, `R11`, `R12` | 5 | `F.Cu` (SMT `0603`) | `1k` | **`1k`** (`F.SilkS`) | All `0603` `1%` (`C21190`) |
| **LED Sink** | `R_LED` | 1 | `F.Cu` (SMT `0603`) | `2.2k` | **`2.2k`** (`F.SilkS`) | Unique value (`C4190`) |
| **10 kΩ `1%` Group** | `R2`, `R10`, `R_ENV_PROT`, `R15`, `R17`, `R18`, `R20` | 7 | `F.Cu` (SMT `0603`) | `10k` | **`10k`** (`F.SilkS`) | Standard `1%` (`C25804`); cross-check `F.Fab` refs vs. `U1B`/`U1C` cluster |
| **10 kΩ `0.1%` Rect.** | `R3`, `R4`, `R5`, `R6`, `R7`, `R8A`, `R8B` | 7 | `F.Cu` (SMT `0603`) | `10k 0.1%` | **`10k`** (`F.SilkS`) | Thin-film `0.1%` (`C95204`) clustered at `U1B`/`U1C`; verify `C95204` vs. `C25804` on `F.Fab` + JLCPCB BOM/CPL review |
| **Offset Sum** | `R13` | 1 | `F.Cu` (SMT `0603`) | `18k` | **`18k`** (`F.SilkS`) | Unique value (`C25810`) |
| **Input Bias** | `R1` | 1 | `F.Cu` (SMT `0603`) | `100k` | **`100k`** (`F.SilkS`) | Unique value (`C25803`) |
| **Gain Fail-Safe** | `R_GAIN_FAIL` | 1 | `F.Cu` (SMT `0603`) | `1M` | **`1M`** (`F.SilkS`) | Unique value (`C22935`) |
| **IC Bypass Caps** | `C_DEC1`, `C_DEC2`, `C_DEC3`, `C_DEC4` | 4 | `F.Cu` (SMT `0603`) | `100nF` | **`100nF`** (`F.SilkS`) | Placed `< 3–5 mm` from `U1`/`U2` supply pins (`C14663`) |
| **Preamp HF Cap** | `C_HF` | 1 | `F.Cu` (SMT `0603`) | `47pF C0G` | **`47pF`** (`F.SilkS`) | Unique value (`C1671`) |
| **Output HF Caps** | `C_OUT1`, `C_OUT2` | 2 | `F.Cu` (SMT `0603`) | `100pF C0G` | **`100pF`** (`F.SilkS`) | Unique `0603` picofarad value (`C14858`) |
| **Bulk Rail Caps** | `C3`, `C4` | 2 | `F.Cu` (SMT `6.3×5.4`) | `22uF 50V` | **`22uF`** (`F.SilkS`) | Unique SMD electrolytic (`C2836438`); **mandatory `+` polarity mark** (§4) |
| **Film Audio/Hold** | `C1`, `C2` | 2 | `B.Cu` (THT `P=5mm`) | `1uF 100V` | **`1uF`** (`B.SilkS` + `F.SilkS`) | Non-polarized box film (`C125397`); value echoed on both sides (`C1`/`C2` on `.Fab`) |

### 3.2 Active ICs & Diodes (`11` Parts — `<REF> + <VAL>` Pairs)

Keep `fp.Reference()` visible on the component's mounting silkscreen layer (`F.SilkS`) and place the concise BOM part value adjacent/stacked (`gap = 0.35 mm`, `≤ 1.2 mm` pair split, `≤ 3.5 mm` SMD / `≤ 6.0 mm` THT tether).

| Refs | Qty | Mount Layer | Silkscreen `<REF>` | Silkscreen `<VAL>` | Notes |
|---|---:|---|---|---|---|
| `U1`, `U2` | 2 | `F.Cu` (SMT `SOIC-14`) | `U1`, `U2` (`F.SilkS`) | **`TL074H`** (`F.SilkS`) | Matches JLCPCB `Comment` (`TL074H`, `C2878713`); add Pin-1 dot (§4) |
| `D_PWR_P`, `D_PWR_N` | 2 | `F.Cu` (SMT `SOD-123`) | `D_PWR_P`, `D_PWR_N` (`F.SilkS`) | **`B5819W`** (`F.SilkS`) | Add external `0.25 mm` cathode bar (§4); note `D_PWR_N` faces opposite `D_PWR_P` |
| `D1_D2` | 1 | `F.Cu` (SMT `SOT-23`) | `D1_D2` (`F.SilkS`) | **`BAT54S`** (`F.SilkS`) | Add Pin-1 (`A1`) dot (§4) to prevent confusion with `BAV99` (`SOT-23`) |
| `D3`, `D_LED_CLAMP` | 2 | `F.Cu` (SMT `SOD-323`) | `D3`, `D_LED_CLAMP` (`F.SilkS`) | **`1N4148WS`** (`F.SilkS`) | Stack `<REF>`/`<VAL>` if needed to stay `≤ 3.5 mm` tether; add external cathode bar (§4) |
| `D_IN`, `D_OUT`, `D_INV_OUT` | 3 | `F.Cu` (SMT `SOT-23`) | `D_IN`, `D_OUT`, `D_INV_OUT` (`F.SilkS`) | **`BAV99`** (`F.SilkS`) | Add Pin-1 (`A1`) dot (§4) |
| `D4` | 1 | `F.Cu` (THT `3mm LED`) | `D4` (`F.SilkS` + `B.SilkS`) | **`LED`** (`F.SilkS` + `B.SilkS`) | Dual-sided label + `+` / `-` polarity marks (§4) |

### 3.3 Panel Hardware, Power Header & Test Points (`16` THT Parts — Dual-Sided `F.SilkS` + `B.SilkS`)

Every through-hole user interface, power entry, and test point footprint receives **dual-sided silkscreen labels** (`F.SilkS` and mirrored `B.SilkS`) so assembly, pot taper verification, power cabling, and bench probing are unambiguous from either side of the board.

- **Primary side**: Keep `fp.Reference()` + `fp.GraphicalItems()` user label on the side where the body sits (`F.SilkS` for `J1`–`J3`, `RV1`–`RV4`, `D4`; `B.SilkS` for `J4` and `TP1`–`TP8`), obeying `≤ 1.2 mm` pair split and `≤ 6.0 mm` tether.
- **Opposite side**: Place mirrored/non-mirrored `PCB_TEXT(board)` or `PCB_TEXT(fp)` secondary text (`<REF> <LABEL>`, e.g., `J1 IN`, `RV1 A100k`, `TP4 IN_BUF`) within `≤ 6.0 mm` of the footprint and clear of all pads/mask/traces-under-copper rules. *(Note: keeping the secondary-side label as a combined single string or `PCB_TEXT(board)` ensures `inspect_board_silk()` checks collisions/keepouts/tether cleanly without triggering false same-side split-pair alerts.)*

| Refs | Qty | Body Side | Primary Silkscreen (`<REF> + <LABEL>`) | Secondary-Side Echo | Critical Markup Notes |
|---|---:|---|---|---|---|
| `J1` | 1 | `F.Cu` | `J1` + `IN` (`F.SilkS`) | `J1 IN` (`B.SilkS`) | Thonkiconn `WQP-PJ398SM`; keep clear of M6 nut keepout |
| `J2` | 1 | `F.Cu` | `J2` + `OUT` (`F.SilkS`) | `J2 OUT` (`B.SilkS`) | Thonkiconn `WQP-PJ398SM` |
| `J3` | 1 | `F.Cu` | `J3` + `INV_OUT` (`F.SilkS`) | `J3 INV_OUT` (`B.SilkS`) | Thonkiconn `WQP-PJ398SM` |
| `RV1` | 1 | `F.Cu` | `RV1` + `GAIN A100k` (`F.SilkS`) | `RV1 GAIN A100k` (`B.SilkS`) | Including taper (`A100k`) prevents mixing up `RV1`–`RV4` during hand soldering; mark Pin `1` |
| `RV2` | 1 | `F.Cu` | `RV2` + `ATK A50k` (`F.SilkS`) | `RV2 ATK A50k` (`B.SilkS`) | Include taper (`A50k`) + Pin `1` |
| `RV3` | 1 | `F.Cu` | `RV3` + `REL A1M` (`F.SilkS`) | `RV3 REL A1M` (`B.SilkS`) | Include taper (`A1M`) + Pin `1` |
| `RV4` | 1 | `F.Cu` | `RV4` + `OFF B10k` (`F.SilkS`) | `RV4 OFF B10k` (`B.SilkS`) | Include linear taper (`B10k`) + Pin `1` (`+9.63 V` CCW) |
| `J4` | 1 | `B.Cu` | `J4` + `PWR` (`B.SilkS`) | `J4 PWR` (`F.SilkS`) | Add `RED STRIPE / -12V` bar + `-12V`, `GND`, `+12V` rail labels on `B.SilkS` (§4) |
| `TP1` | 1 *(DNP)* | `B.Cu` | `TP1` + `GND` (`B.SilkS`) | `TP1 GND` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`); mark DNP on `.Fab` |
| `TP2` | 1 *(DNP)* | `B.Cu` | `TP2` + `+12V` (`B.SilkS`) | `TP2 +12V` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |
| `TP3` | 1 *(DNP)* | `B.Cu` | `TP3` + `-12V` (`B.SilkS`) | `TP3 -12V` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |
| `TP4` | 1 *(DNP)* | `B.Cu` | `TP4` + `IN_BUF` (`B.SilkS`) | `TP4 IN_BUF` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |
| `TP5` | 1 *(DNP)* | `B.Cu` | `TP5` + `PREAMP` (`B.SilkS`) | `TP5 PREAMP` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |
| `TP6` | 1 *(DNP)* | `B.Cu` | `TP6` + `RECT` (`B.SilkS`) | `TP6 RECT` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |
| `TP7` | 1 *(DNP)* | `B.Cu` | `TP7` + `OUT` (`B.SilkS`) | `TP7 OUT` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |
| `TP8` | 1 *(DNP)* | `B.Cu` | `TP8` + `INV_OUT` (`B.SilkS`) | `TP8 INV_OUT` (`F.SilkS`) | Dual-sided (`F.SilkS` + `B.SilkS`) |

*(Keep `≥ 2.5–3.0 mm` clear around `TP1`–`TP8` pads for `RH-5001` pin grabber clips and keep labels outside `0.25 mm` of pad mask openings on both layers.)*

---

## 4. Mandatory Polarity, Pin-1 & Orientation Marks

Every polarized or asymmetrical component must have **visible post-assembly markings outside its package body and solder-mask openings**:

1. **Quad Op-Amps (`U1`, `U2` — `SOIC-14`)**:
   - Solid filled silkscreen dot (`r = 0.25 mm`) on `F.SilkS` just outside **Pin 1** (`U1.1` / `U2.1`), outside the `.Fab` body and `0.25 mm` pad mask margin.
2. **2-Pin SMD Diodes (`D_PWR_P`, `D_PWR_N` `SOD-123`; `D3`, `D_LED_CLAMP` `SOD-323`)**:
   - Bold **`0.25 mm` external cathode (`K`) bar** on `F.SilkS` outside **Pad 1 (`K`)**, plus external `U`-bracket or cathode notch clear of pads so diode orientation stays visible after reflow.
   - **Critical checks**:
     - `D_PWR_N` cathode bar faces `J4` (`-12V_IN`), **reversed** relative to `D_PWR_P` (cathode bar faces `+12V_PROT`).
     - `D_LED_CLAMP` cathode bar faces `U2B_OUT` (`D4.A`, anti-parallel across `D4`).
3. **3-Pin `SOT-23` Dual Series Diodes (`D1_D2` `BAT54S`; `D_IN`, `D_OUT`, `D_INV_OUT` `BAV99`)**:
   - Filled Pin-1 dot (`r = 0.20–0.25 mm`) on `F.SilkS` outside **Pad 1 (`A1`)** alongside external `SOT-23` outline ticks so `180°` orientation errors are immediately caught.
4. **SMD Electrolytic Capacitors (`C3`, `C4` — `CP_Elec_6.3x5.4`)**:
   - Bold **`+`** symbol (`≥ 0.80 mm` height) on `F.SilkS` outside the `+` pad plus the chamfered `+` outline.
   - **Critical check on `C4` (`-12V` rail)**: `C4`'s **`+`** pad connects to **`GND`**, and its **`-`** pad (black cathode half-moon on cap top) connects to **`-12V`**.
5. **THT 3 mm Indicator LED (`D4`)**:
   - Mark **`+`** adjacent to **Pad 2 (`A`, long lead)** and **`-`** (or flat cathode bar) adjacent to **Pad 1 (`K`, short lead)** on **both `F.SilkS` and `B.SilkS`**.
6. **Potentiometers (`RV1`–`RV4`)**:
   - Mark **`1`** adjacent to **Pad 1 (CCW lug)** on `F.SilkS` and `B.SilkS` to verify taper/rotation orientation (`RV4.1` = `OFF_TOP`, `+9.63 V`; `RV4.3` = `OFF_BOT`, `-9.63 V`).
7. **Eurorack `2×5` Power Header (`J4` on `B.Cu`)**:
   - Draw a **`0.8–1.0 mm` wide filled stripe bar** along the **Pins `1–2`** edge on `B.SilkS` labeled **`RED STRIPE / -12V`**, plus pin-pair rail labels **`-12V` (`1–2`)**, **`GND` (`3–8`)**, **`+12V` (`9–10`)**, and a shrouded key-notch outline (`key faces pin side per header spec`). Echo **`-12V` / Pin 1** marker on `F.SilkS`.
8. **Film Capacitors (`C1`, `C2`)**:
   - Non-polarized (`1 µF 100 V` PET film); no `+`/`-` marks needed.

---

## 5. JLCPCB DFM, Fiducials, QR Placeholder & `B.Fab` Fabrication Notes

### 5.1 JLCPCB QR Code Placeholders & Optical Fiducials
- **QR Code Placeholders**: Draw and reserve **`5.0 × 5.0 mm` solid filled silkscreen squares** (`add_silk_rect(..., filled=True)`) on **`B.SilkS`** (and **`F.SilkS`** if clear space permits) in open board areas free of pads, vias, labels, and `≥ 0.45 mm` from `Edge.Cuts` so JLCPCB replaces the square with its order tracking QR code cleanly rather than stamping over component markings.
- **SMT Fiducials (`FID1`–`FID3`)**: Place **3** global fiducial markers on **`F.Cu`** (the JLCPCB Economic SMT side) arranged asymmetrically near board corners (`1.0 mm` bare copper pad, `2.0 mm` solder-mask expansion, **`±1.25 mm`** silkscreen keepout, zero `.SilkS` text).

### 5.2 Board Identity & JLCPCB Pick-and-Place Review Rules
- **Board Title Block (`B.SilkS` + open `F.SilkS` corner)**: `ENVELOPE FOLLOWER`, `6HP ±12V EURORACK`, `REV 1.0`.
- **CPL Rotation Verification**: Before confirming the JLCPCB order in their 3D/CPL viewer, verify every asymmetrical SMT part against its silkscreen Pin-1 dot / cathode bar:
  - `SOIC-14` (`U1`, `U2`): JLCPCB frequently differs from KiCad by **`+90°` or `+270°`**.
  - `SOT-23` (`D1_D2`, `D_IN`, `D_OUT`, `D_INV_OUT`): JLCPCB frequently differs by **`+180°`**.
  - `SOD-123` / `SOD-323` (`D_PWR_P/N`, `D3`, `D_LED_CLAMP`) and `CP_Elec_6.3x5.4` (`C3`, `C4`): verify cathode bar / `+` chamfer visually in JLCPCB's placement preview.
- **DNP / Orphan CPL Exclusion**: Export the JLCPCB SMT BOM CSV (`19` lines, `49` parts) excluding THT parts and **DNP** `TP1`–`TP8`, and filter the KiCad CPL via `translate_bom_pnp.py pnp ... --bom jlc_bom.csv` so JLCPCB's web uploader does not reject `TP1`–`TP8`, `J1`–`J4`, `RV1`–`RV4`, `C1`–`C2`, `D4`, or `FID1`–`FID3` as orphan CPL designators.

### 5.3 Mandatory `B.Fab` Fabrication Notes (`100%` `fab_notes_completeness`)
Include the complete 4-line fabrication note block on **`B.Fab`** (`add_standard_fab_notes(board, cx, y_start)`, mirrored `0.80 mm` height / `0.15 mm` stroke) covering all 6 metadata checks in `analyze_pcb.py` (`material`, `board_thickness`, `copper_weight`, `surface_finish`, `ipc_class`, `solder_mask`):

```text
FAB NOTES: 2L FR4 | THICKNESS: 1.6mm | 1oz CU
FINISH: ENIG / HASL-LF | IPC-6012 CLASS 2
SOLDER MASK: BLACK | SILK: WHITE | MIN TR/SP: 0.127mm
DRILL TOL: +/-0.08mm | NO EDGE CUT
```

*(Also export `F.Fab` / `B.Fab` assembly drawings with all `R*`/`C*` references visible on `.Fab` so bench builders and QC reviewers can cross-reference any `.SilkS` value token like `10k` or `470R` against `EnvelopeFollowerBOM.md` and JLCPCB's BOM/CPL report.)*

---

## 6. Automated Verification Checklist

Run all checks after generating or editing the PCB silkscreen:

```bash
# 1. Inspect silkscreen coverage, collisions, keepouts, tether drift, and split pairs (must print RESULT: PASS)
python3 .agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py --inspect EnvelopeFollower.kicad_pcb

# 2. Run KiCad DRC (verify 0 silk_overlap and 0 silk_over_copper violations)
kicad-cli pcb drc --refill-zones --format json --output /tmp/drc.json EnvelopeFollower.kicad_pcb

# 3. Run full PCB static/DFM analyzer (verify fab_notes_completeness and 0 silkscreen/assembly findings)
python3 .agents/skills/kicad/scripts/analyze_pcb.py EnvelopeFollower.kicad_pcb --full --output /tmp/pcb_analysis.json

# 4. Visual raytraced render check (top and bottom)
kicad-cli pcb render --side top --width 1200 --height 1600 --output /tmp/env_top.png EnvelopeFollower.kicad_pcb
kicad-cli pcb render --side bottom --width 1200 --height 1600 --output /tmp/env_bottom.png EnvelopeFollower.kicad_pcb
```

**Pass Criteria:**
- `silk_annotator.py --inspect` exits `0` with **`RESULT: PASS`**: `100%` non-fiducial footprints labeled (`68/68` total; `41` value-only passives + `27` `<REF> + <VAL>` parts), `0` raw `fp.Value()` on silk, `0` overlaps, `0` keepout hits, `0` out-of-bounds, `0` tether drift hits, and `0` split-pair hits.
- KiCad DRC reports `0` `silk_overlap` and `0` `silk_over_copper` violations.
- Visual renders confirm clear Pin-1 dots, diode cathode bars, `C3`/`C4` `+` marks, dual-sided `TP1`–`TP8` & `J4` `RED STRIPE / -12V` labels, and unobstructed `5.0 × 5.0 mm` QR square(s).
