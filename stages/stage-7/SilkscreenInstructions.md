# Envelope Follower (Improved) — Silkscreen & Fabrication Markup Instructions

Silkscreen, polarity, and fabrication markup specification for the **6 HP Eurorack Envelope Follower** defined in [EnvelopeFollowerImproved.md](./EnvelopeFollowerImproved.md) and [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md), following the automated collision-free conventions of [kicad-silkscreen-markup](./.agents/skills/kicad-silkscreen-markup/SKILL.md) ([silk_annotator.py](./.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py)), [kicad-pcbnew-layout](./.agents/skills/kicad-pcbnew-layout/SKILL.md), and [jlcpcb](./.agents/skills/jlcpcb/SKILL.md).

---

## 1. Board Architecture & Side Partitioning

| Side / Layer | Role | Component Groups | Primary Inspection Purpose |
|---|---|---|---|
| **Front (`F.Cu` / `F.SilkS`)** | Panel-facing THT controls only (`8` parts) | `J1`–`J3`, `RV1`–`RV4`, `D4` | Panel alignment, control identification, LED/pot polarity, and front-side secondary labels for `J4` and `TP1`–`TP8` |
| **Rear (`B.Cu` / `B.SilkS`)** | JLCPCB single-sided Economic SMT PCBA (`44` parts) + rear THT (`3` parts) + `DNP` THT (`8` parts) + fiducials (`FID*`) | `U1`–`U2`, `R1`–`R13`/`R15`–`R21`/`R24`–`R27`, `C1`–`C11`, `D1`–`D3`/`D5`–`D10`, `J4`, `TP1`–`TP8`, `FID*` | Post-PCBA JLCPCB placement/value audit against `jlcpcb_bom.csv`, diode/`C4`/`J4` polarity check, and rear bench probing |
| **Fabrication (`B.Fab` / `F.Fab`)** | Assembly & PCB fab documentation | Hidden `fp.Reference()` (`R*`, `C*`) & `fp.Value()` (all parts), `B.Fab` board fab notes | Clean assembly drawings & `fab_notes_completeness` compliance without crowding `B.SilkS` |

*Total component footprints covered: `55` populated parts (`44` SMT + `3` rear THT + `8` front THT) + `8` `DNP` rear test points (`TP1`–`TP8`) + `B.Cu` optical fiducials (`FID*`). Removed legacy designators (`R14`, `R22`, `R23`) do not appear.*

---

## 2. Core Silkscreen Rules & KiCad Layer Policy

1. **Never Leave Raw `fp.Value()` Visible on Silkscreen:**
   - Move **every** footprint's `fp.Value()` field to its mounting-side `.Fab` layer (`B.Fab` or `F.Fab`) and call `fp.Value().SetVisible(False)`.
   - All value or function text printed on `B.SilkS` or `F.SilkS` **must** be emitted as `pcbnew.PCB_TEXT(fp)` (`fp_text user`) items (or `pcbnew.PCB_TEXT(board)` for board-level callouts) so `silk_annotator.py --inspect` reports `0` raw values on silk and `analyze_pcb.py` emits `0` `values_visible_on_silk` warnings.

2. **Density-Adaptive Passive Policy (`R*`, `C*` on `B.SilkS`) vs. Active/Interface Parts:**
   - **Fixed Resistors & Capacitors (`R1`–`R13`, `R15`–`R21`, `R24`–`R27`, `C1`–`C11`):**
     - On `B.SilkS`, print **only the concise primary value token** (`fp_text user`, e.g., `10k`, `100nF`, `22uF`, `1uF`) immediately adjacent to each passive body so a visual/AOI check can compare every populated SMT value directly against the JLCPCB BOM without saturating the narrow `6 HP` (`~30 mm` wide) rear silkscreen.
     - Move both `fp.Reference()` (`R*`, `C*`) and `fp.Value()` to **`B.Fab`** with `SetVisible(False)` (`place_val_only()` / `place_ref_val_pair(..., val_only="auto")`).
     - *Exception for `RV1`–`RV4`:* Potentiometers (`RV*`) are UI controls, **not** fixed passives (`is_passive_ref()` excludes `RV*`), and receive `<REF> + <VAL>` labels on both sides.
   - **Active, Polarized & Interface Parts (`U*`, `D*`, `LED*`, `RV*`, `J*`, `TP*`):**
     - Keep `fp.Reference()` visible on the part's primary silkscreen layer (`B.SilkS` for `U*`, `D1`–`D3`/`D5`–`D10`, `J4`, `TP1`–`TP8`; `F.SilkS` for `J1`–`J3`, `RV1`–`RV4`, `D4`).
     - Place a paired `fp_text user` `<VAL/FUNC>` token beside or stacked with `<REF>` (`gap >= 0.35 mm`, pair separation `<= 1.2 mm`).
   - **Fiducials (`FID*`):**
     - Keep **both** `fp.Reference()` and `fp.Value()` hidden on `B.Fab`; emit **zero** silkscreen text or graphics inside the `±1.25 mm` fiducial solder-mask keepout (`2.0 mm` mask opening around `1.0 mm` pad).

3. **Dual-Sided Labeling for THT Controls, Power Header & Test Points (`F.SilkS` + `B.SilkS`):**
   - **Front Panel Controls (`J1`–`J3`, `RV1`–`RV4`, `D4`):** Primary `<REF> + <FUNC>` on `F.SilkS`, plus a combined secondary `fp_text user` label (e.g., `J1 IN`, `RV1 GAIN A100k`, `D4 ENV`) on **`B.SilkS`** so pots, jacks, and LED can be identified from the back during hand-soldering and bench debugging.
   - **Rear Power Header (`J4`) & Rear Test Points (`TP1`–`TP8`):** Primary `<REF> + <VAL/NET>` pair on `B.SilkS`, plus a combined secondary `fp_text user` label (e.g., `J4 PWR`, `TP1 GND` … `TP8 V_OUT_PRE`) on **`F.SilkS`** (where clear of panel hardware bodies) so bare plated `1.0 mm` test-point holes and power pins can be identified from either side.
   - *Important `silk_annotator.py` constraint:* Keep only **one** `fp.Reference()` per footprint on its primary side; put the secondary-side label in `fp_text user` (`PCB_TEXT(fp)`) on the **opposite** silkscreen layer (`1 - ref_side`) so `inspect_board_silk()` never treats the opposite-side text as a split pair.

4. **Typography, Mirroring, Tethering & Clearances (`JLCPCB` DFM + `SilkGrid`):**
   - **Text geometry:** Height `>= 0.80 mm` (`SILK_HEIGHT`), stroke thickness `>= 0.15 mm` (`SILK_THICKNESS`, JLCPCB minimum), rotations strictly **`0°` or `90°`** (never angled or upside-down). Measure exact KiCad stroke bounding boxes (`PCB_TEXT.GetBoundingBox() + 0.06 mm` padding) rather than fixed character-width estimates.
   - **`B.SilkS` mirroring:** Set `SetMirrored(True)` on every `B.SilkS` text item. Place `<REF>` at `-X` (`-1.0 * offset`) and `<VAL>` at `+X` (`+1.0 * offset`) in board coordinates so `<REF> <VAL>` always reads left-to-right when viewing the rear of the board (`place_ref_val_pair()` handles this automatically).
   - **Pad, body & edge keepouts:**
     - `>= 0.45 mm` inward from `Edge.Cuts` center (`SILK_EDGE_CLEARANCE`).
     - Exposed pad bbox + solder-mask expansion + `0.25 mm` margin (`0` `SK-001` `silk_over_copper` violations).
     - Existing footprint `.SilkS` graphics + `0.20 mm` margin; label-to-label gap `>= 0.20 mm`.
     - Mounting-side `.Fab` body interiors + `0.05 mm` margin (`block_smd_fab=True`, `block_tht_fab=True`) so no label prints underneath a soldered `SOIC-14`, `SOD-123`, `SOT-23`, `2512`, electrolytic can, film box, or shrouded header.
   - **Strict local tethering (never use board-wide fallback scans):**
     - SMD labels: `<= 3.5 mm` edge distance (`MAX_SMD_TETHER_MM`).
     - THT labels: `<= 6.0 mm` edge distance (`MAX_THT_TETHER_MM`).
     - `<REF>` / `<VAL>` pair separation: `<= 1.2 mm` (`MAX_PAIR_SPLIT_MM`).
     - *Layout rule:* Reserve `>= 1.5–2.0 mm` silkscreen label corridors between dense `0603` rows and IC/THT keepouts during placement rather than pushing labels across the board.

---

## 3. Component-by-Component Silkscreen Markup Matrix

### 3.1 Active ICs (`B.Cu` SMT — `2` Parts)

| Ref | MPN / Package | `B.SilkS` Markup | `F.SilkS` | `B.Fab` | Mandatory Polarity / Pin-1 Graphics (`B.SilkS`) |
|---|---|---|---|---|---|
| `U1` | `TL074HIDR` (`SOIC-14`) | `U1` + `TL074H` (`<REF> <VAL>`) | — | Hidden `Value` + outline | Filled **`0.25 mm` radius Pin-1 dot** (`place_silk_dot`) immediately outside `Pin 1` (`U1A_Out`) + Pin-1 notch/chamfer clear of pads |
| `U2` | `TL074HIDR` (`SOIC-14`) | `U2` + `TL074H` (`<REF> <VAL>`) | — | Hidden `Value` + outline | Filled **`0.25 mm` radius Pin-1 dot** immediately outside `Pin 1` (`U2A_Out`) + Pin-1 notch/chamfer clear of pads |

### 3.2 Fixed Resistors (`B.Cu` — `24` SMT Parts, Concise Value-Only on `B.SilkS`)

Keep `fp.Reference()` and `fp.Value()` on **`B.Fab` (`SetVisible(False)`)** and print a single `fp_text user` value token on **`B.SilkS`** (`<= 3.5 mm` tether).

| Ref(s) | Qty | Package | BOM Value | `B.SilkS` Value Token | `F.SilkS` | `B.Fab` | Notes |
|---|---:|---|---|---|---|---|---|
| `R1` | 1 | `0603` | `100 kΩ` 1% | `100k` | — | `R1` (hidden) | Input AC pull-down |
| `R2`–`R7`, `R9`, `R10`, `R15`, `R17`, `R18`, `R20`, `R27` | 13 | `0603` | `10 kΩ` 1% | `10k` | — | `R2`–`R27` (hidden) | Standard `10k` network |
| `R8` | 1 | `0603` | `20 kΩ` 1% | `20k` | — | `R8` (hidden) | Exact `1.00×` rectifier feedback (`U1C`) |
| `R11`, `R12` | 2 | `0603` | `1 kΩ` 1% | `1k` | — | `R11`, `R12` (hidden) | `OFFSET` divider endpoints |
| `R13` | 1 | `0603` | `22 kΩ` 1% | `22k` | — | `R13` (hidden) | `OFFSET` summing (`1.400×–1.436×`) |
| `R16`, `R19`, `R26` | 3 | `2512` | `1 kΩ` **`1 W`** 1% | `1k_1W` *(or `1k/1W`)* | — | `R16`, `R19`, `R26` (hidden) | **Single non-spaced token** so `compact_passive_value()` does not strip `1W`—distinguishes `1 W` fault resistors from `0603` `1k` (`R11`, `R12`) |
| `R21` | 1 | `0603` | `3.3 kΩ` 1% | `3.3k` | — | `R21` (hidden) | Active `LED` current sense |
| `R24` | 1 | `0603` | `4.7 kΩ` 1% | `4.7k` | — | `R24` (hidden) | `GAIN` `0.47×` floor |
| `R25` | 1 | `0603` | `330 Ω` 1% | `330R` | — | `R25` (hidden) | Attack surge limiter (`0.33 ms`) |

### 3.3 Fixed Capacitors (`B.Cu` — `9` SMT + `2` Rear THT Parts, Concise Value-Only on `B.SilkS`)

Keep `fp.Reference()` and `fp.Value()` on **`B.Fab` (`SetVisible(False)`)** and print a single `fp_text user` value token on **`B.SilkS`**.

| Ref(s) | Qty | Package / Side | BOM Value | `B.SilkS` Value Token | `F.SilkS` | `B.Fab` | Mandatory Polarity & Notes |
|---|---:|---|---|---|---|---|---|
| `C1`, `C2` | 2 | `P=5.0 mm` Film (`B.Cu` THT) | `1 µF` `63 V` | `1uF` | — | `C1`, `C2` (hidden) | Non-polarized polyester film box (`<= 6.0 mm` THT tether); keep `F.Cu` pad clearances clear of `F.SilkS` labels |
| `C3` | 1 | `6.3×5.4 mm` SMD Elec (`B.Cu`) | `22 µF` `50 V` | `22uF` | — | `C3` (hidden) | **`+12V` rail polarity:** Bold **`+`** outside `Pin 1` (`+12V`) and chamfered/bar `-` on `Pin 2` (`GND`) on `B.SilkS` visible outside the `6.3 mm` can |
| `C4` | 1 | `6.3×5.4 mm` SMD Elec (`B.Cu`) | `22 µF` `50 V` | `22uF` | — | `C4` (hidden) | **CRITICAL `-12V` rail polarity:** Bold **`+`** outside `Pin 1` (**`GND`**) and `-` outside `Pin 2` (**`-12V`**) on `B.SilkS` (reversed relative to `GND` because `0 V > -11.65 V`) |
| `C5`–`C8` | 4 | `0603` X7R (`B.Cu`) | `100 nF` `50 V` | `100nF` | — | `C5`–`C8` (hidden) | Local op-amp bypass (`U1.4`, `U1.11`, `U2.4`, `U2.11`) |
| `C9` | 1 | `0603` C0G (`B.Cu`) | `22 pF` `50 V` | `22pF` | — | `C9` (hidden) | `U1A` ultrasonic compensation (`69.1 kHz`) |
| `C10`, `C11` | 2 | `0603` C0G (`B.Cu`) | `47 pF` `50 V` | `47pF` | — | `C10`, `C11` (hidden) | `U1D` & `U2A` stabilization |

### 3.4 SMT Diodes (`B.Cu` — `9` Parts, `<REF> + <VAL>` on `B.SilkS`)

| Ref(s) | Qty | Package | `B.SilkS` Label (`<REF> <VAL>`) | `F.SilkS` | Mandatory Polarity / Pin-1 Graphics (`B.SilkS`) |
|---|---|---|---|---|---|
| `D1`, `D2`, `D3`, `D10` | 4 | `SOD-123` | `D1 1N4148W`, `D2 1N4148W`, `D3 1N4148W`, `D10 1N4148W` | — | Bold **`0.25 mm` external cathode bar (`place_silk_seg`)** outside `Pin 1 (K)` that remains visible outside the `SOD-123` package outline after reflow |
| `D5`, `D6` | 2 | `SOD-123` | `D5 B5819W`, `D6 B5819W` | — | Bold **`0.25 mm` external cathode bar** outside `Pin 1 (K)` (`D5.K -> +12V`; `D6.K -> -12V_IN`—note opposite orientation!) |
| `D7`, `D8`, `D9` | 3 | `SOT-23` | `D7 BAV99`, `D8 BAV99`, `D9 BAV99` | — | Filled **`0.25 mm` Pin-1 dot** outside `Pin 1` (`A1`, `-12V`); verify physical pad `1=-12V`, `2=+12V`, `3=COM` |

### 3.5 Panel-Facing THT Controls (`F.Cu` — `8` Parts, Dual-Sided `F.SilkS` + `B.SilkS`)

Keep `fp.Reference()` on `F.SilkS` alongside its concise function token (`fp_text user`), and place a combined `fp_text user` label on `B.SilkS` (`<= 6.0 mm` THT tether).

| Ref | Part / Value | `F.SilkS` (Primary: `<REF> + <FUNC>`) | `B.SilkS` (Secondary Combined Label) | Polarity / Pin-1 Markers (Both `F.SilkS` & `B.SilkS`) |
|---|---|---|---|---|
| `J1` | `WQP-PJ398SM` (`IN`) | `J1` + `IN` | `J1 IN` | `S` / `TN` / `T` pad hint if room permits; keep silk outside `F.Cu` jack keepout & pad mask |
| `J2` | `WQP-PJ398SM` (`OUT`) | `J2` + `OUT` | `J2 OUT` | Same as `J1`; note `TN = NC` on assembly/fab |
| `J3` | `WQP-PJ398SM` (`INV_OUT`) | `J3` + `INV_OUT` *(or `INV`)* | `J3 INV_OUT` | Same as `J1`; note `TN = NC` on assembly/fab |
| `RV1` | `A100k` 9 mm Vertical Pot | `RV1` + `GAIN` | `RV1 GAIN A100k` | **`1`** marker next to `Pin 1` (`CCW`, `GAIN_MID`) on both sides |
| `RV2` | `A50k` 9 mm Vertical Pot | `RV2` + `ATK` | `RV2 ATK A50k` | **`1`** marker next to `Pin 1` (`CCW`, `ATK_POT_IN`) on both sides |
| `RV3` | `A1M` 9 mm Vertical Pot | `RV3` + `REL` *(or `Release`)* | `RV3 REL A1M` | **`1`** marker next to `Pin 1` (`CCW`, `REL_MID`) on both sides |
| `RV4` | `B10k` 9 mm Vertical Pot | `RV4` + `OFFSET` | `RV4 OFFSET B10k` | **`1`** marker next to `Pin 1` (`CCW`, `+12V` end) on both sides |
| `D4` | `3 mm` Yellow-Green LED | `D4` + `ENV` | `D4 ENV` | Flat-side cathode chamfer + **`-` (`K`)** at `Pin 1` (square pad, `LED_K`) and **`+` (`A`)** at `Pin 2` (`LED_A`) on **both** `F.SilkS` and `B.SilkS` |

### 3.6 Rear Power Header (`J4`, `B.Cu` — `1` Part, Dual-Sided `B.SilkS` + `F.SilkS`)

| Ref | Part | `B.SilkS` (Primary) | `F.SilkS` (Secondary) | Mandatory Shroud & Rail Polarity Callouts |
|---|---|---|---|---|
| `J4` | `2×5` `2.54 mm` Shrouded IDC (`IDC2.54-2*5PZ`) | `J4` + `PWR` (`<REF> <VAL>`) | `J4 PWR` | • **`-12V RED` solid silkscreen bar** (`add_silk_rect` / `0.25 mm` stripe) alongside Pins `1–2` on **`B.SilkS`** and Pin-`1` / `-12V` callout on **`F.SilkS`**<br>• Board-level rail labels **`-12V`**, **`GND`**, **`+12V`** (`PCB_TEXT(board)`) beside pin groups `1–2`, `3–8`, `9–10` on `B.SilkS`<br>• Explicit key-notch box outline matching `IDC2.54-2*5PZ` shroud orientation |

### 3.7 Rear Optional `DNP` Test Points (`TP1`–`TP8`, `B.Cu` — `8` Footprints, Dual-Sided `B.SilkS` + `F.SilkS`)

Every `TP*` footprint uses a `2.0 mm` pad / `1.0 mm` drill (`TestPoint:TestPoint_Keystone_5000-5004_Miniature` or `TestPoint_Loop_D2.50mm_Drill1.0mm` for Ronghe `RH-5001`, marked `DNP` + `Exclude from BOM` + `Exclude from Position Files`), labeled on **both** `B.SilkS` and `F.SilkS` (`<= 6.0 mm` THT tether):

| Ref | Net | `B.SilkS` (Primary `<REF> + <NET>`) | `F.SilkS` (Secondary Combined Label) | Probing / Silkscreen Notes |
|---|---|---|---|---|
| `TP1` | `GND` | `TP1` + `GND` | `TP1 GND` | Reference ground clip (`0 V`) |
| `TP2` | `+12V` | `TP2` + `+12V` | `TP2 +12V` | Protected `+11.65 V` rail (post-`D5`) |
| `TP3` | `-12V` | `TP3` + `-12V` | `TP3 -12V` | Protected `-11.65 V` rail (post-`D6`) |
| `TP4` | `IN_BUF` | `TP4` + `IN_BUF` | `TP4 IN_BUF` | `U2C` input buffer output (`U2.8`) |
| `TP5` | `V_AMP` | `TP5` + `V_AMP` | `TP5 V_AMP` | `U1A` variable gain output (`U1.1`) |
| `TP6` | `V_FWR` | `TP6` + `V_FWR` | `TP6 V_FWR` | `U1C` full-wave rectifier output (`U1.8`) |
| `TP7` | `ENV_CAP` | `TP7` + `ENV_CAP` | `TP7 ENV_CAP` | Envelope storage cap (`C2.1`); probe with `10×` (`10 MΩ`) |
| `TP8` | `V_OUT_PRE` | `TP8` + `V_OUT_PRE` | `TP8 V_OUT_PRE` | `U1D` pre-`R16` output (`U1.14`) |

---

## 4. Board-Level Markings, JLCPCB QR Placeholders & `B.Fab` Notes

1. **Board Title & Revision (`F.SilkS` and `B.SilkS`):**
   - Populate `board.GetTitleBlock()` (`Title`, `Rev`, `Date`) and place `f"{tb.GetTitle()} {tb.GetRevision()}".strip()` (e.g., `ENVELOPE FOLLOWER REV 1.0`) on both `F.SilkS` and `B.SilkS` via `place_board_label(...)` so `analyze_pcb.py` (`silkscreen_completeness`) detects both `board_name` and `revision_marking`.

2. **JLCPCB `5.0 × 5.0 mm` QR Code Placeholders (`B.SilkS` & `F.SilkS`):**
   - Place a solid filled `5.0 × 5.0 mm` square (`place_silk_rect(..., filled=True)`) on **`B.SilkS`** (required for bottom-side JLCPCB PCBA tracking) and on **`F.SilkS`** if panel-behind clearance permits.
   - Block the `5.0 × 5.0 mm` QR zone (`±0.5 mm` margin) from **all vias and same-side copper tracks** during routing and GND via-stitching (`qr_copper_hits = 0`).

3. **`B.Fab` Fabrication Notes (`100%` `fab_notes_completeness`):**
   - Call `add_standard_fab_notes(board, cx, y_start)` on `B.Fab` (`mirrored=True`, `0.80 mm` height, `0.15 mm` stroke) emitting all six keywords checked by `analyze_pcb.py`:
     ```text
     FAB NOTES: 2L FR4 | THICKNESS: 1.6mm | 1oz CU
     FINISH: ENIG / HASL-LF | IPC-6012 CLASS 2
     SOLDER MASK: BLACK | SILK: WHITE | MIN TR/SP: 0.127mm
     DRILL TOL: +/-0.08mm | NO EDGE CUT
     ```

---

## 5. Automated Implementation & Verification Sequence

### Implementation Workflow (`silk_annotator.py`)
1. Initialize `grid = SilkGrid(board, block_smd_fab=True, block_tht_fab=True)` **after** routing/zone-fill so all mask-expanded pads, footprint silkscreen outlines, SMD/THT `.Fab` interiors, and `±1.25 mm` fiducial zones are seeded as keepouts.
2. Reserve the `5.0 × 5.0 mm` QR placeholder rectangle(s), `B.Fab` fab notes, board title/rev labels, and `J4` `-12V RED` stripe/rail labels.
3. Iterate footprints on `board`:
   - `FID*`: hide `fp.Reference()` and `fp.Value()` on `B.Fab`.
   - `R*` / `C*` (excluding `RV*`): call `place_val_only(..., side=1)` on `B.SilkS` (passing `"1k_1W"` or `"1k/1W"` for `R16`, `R19`, `R26` so the `1 W` rating is preserved).
   - `U*`, `D1`–`D3`/`D5`–`D10`: call `place_ref_val_pair(..., side=1, val_only=False)` on `B.SilkS`, then place Pin-1 dots (`U1`, `U2`, `D7`–`D9`) and external `0.25 mm` cathode bars (`D1`–`D3`, `D5`, `D6`, `D10`) + `C3`/`C4` `+`/`-` polarity markers.
   - `J1`–`J3`, `RV1`–`RV4`, `D4`: call `place_ref_val_pair(..., side=0, val_only=False)` on `F.SilkS`, place `RV*` `"1"` and `D4` `+`/`-` markers on both sides, and call `place_board_label(grid, fp, side=1, text=secondary_label, fp=fp)` on `B.SilkS`.
   - `J4`, `TP1`–`TP8`: call `place_ref_val_pair(..., side=1, val_only=False)` on `B.SilkS`, and call `place_board_label(grid, fp, side=0, text=secondary_label, fp=fp)` on `F.SilkS`.

### Mandatory Post-Generation Checks
Run all four checks after generating the final `.kicad_pcb`:

```bash
# 1. Silkscreen tether-drift, keepout, QR copper/via, and collision check (must return RESULT: PASS)
python3 .agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py --inspect EnvelopeFollower.kicad_pcb

# 2. KiCad DRC with --severity-all and zone refill (confirm 0 silk_overlap / silk_over_copper)
kicad-cli pcb drc --severity-all --refill-zones --format json --output analysis/drc.json EnvelopeFollower.kicad_pcb

# 3. Full KiCad PCB static & DFM audit (confirm 0 SK-001 errors, 100% fab_notes_completeness)
.venv/bin/python .agents/skills/kicad/scripts/analyze_pcb.py EnvelopeFollower.kicad_pcb --full --output analysis/pcb_analysis.json

# 4. Visual 3D render inspection (render to workspace-local analysis/ directory)
mkdir -p analysis
kicad-cli pcb render --side top -o analysis/top.png --width 1200 --height 1600 --background transparent EnvelopeFollower.kicad_pcb
kicad-cli pcb render --side bottom -o analysis/bottom.png --width 1200 --height 1600 --background transparent EnvelopeFollower.kicad_pcb
```

*Expected audit interpretation:* `silk_annotator.py --inspect` (`RESULT: PASS`) and `kicad-cli pcb drc --severity-all` (`0` violations/warnings) are authoritative for `100%` non-fiducial silkscreen coverage and collision safety. In `analyze_pcb.py`, `SK-001` (`silk_over_copper`) must be `0` and `fab_notes_completeness` must be `100%`; `analyze_pcb.py`'s heuristic `silkscreen_completeness.checks.ref_designators_visible` (`< 90%`) and `polarity_reminder` notices are expected side effects of keeping `R*`/`C*` reference designators on `B.Fab`.
