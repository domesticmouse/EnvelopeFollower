# Stage 5: Generating, Routing & Auditing the 6 HP Main PCB (`generate_kicad_pcb.py`)

Because `envelope_follower.net` ([Stage 4](stage-4-skidl.md)) already contains all 62 component footprints, 36 nets, `dnp` flags, and custom BOM/silkscreen fields (`LCSC`, `MPN`, `JLCPCB_Class`, `Silkscreen`), KiCad's `pcbnew` API and `kinet2pcb` can generate [`EnvelopeFollower.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_pcb) directly from the netlist without needing an intermediate `.kicad_sch` schematic.

Rather than importing the netlist manually, placing 62 footprints by hand, and routing traces interactively in `pcbnew`, [`generate_kicad_pcb.py`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/generate_kicad_pcb.py) automates the board outline, control grid, single-sided `B.Cu` SMT placement, `DNP` test points, BOM metadata transfer, dual-sided silkscreen markup, 2-layer copper routing, `GND` copper pours, and DRC/DFM verification.

## AI Agent Prompt

> *"`/eurorack-panel` `/kicad` Please create and run `generate_kicad_pcb.py` to generate a 6 HP main PCB (`EnvelopeFollower.kicad_pcb`) from `envelope_follower.net`, following `@EnvelopeFollowerImproved.md` and `@SilkscreenInstructions.md`. Place the 4 pots, 3 jacks, and LED on `F.Cu` aligned to a 6 HP front-panel grid, and place `J_PWR`, the `DNP` test points (`TP1`–`TP8`), and all 45 SMD parts (with their `@SilkscreenInstructions.md` silkscreen labels) on `B.Cu`."*

### How the Prompt Delegates to Your Skills & Specs

1. **`/eurorack-panel` + `/kicad` + `generate_kicad_pcb.py` from `envelope_follower.net`**:
    Converts the SKiDL netlist (`62` footprints, `36` nets, embedded `LCSC`/`MPN`/`JLCPCB_Class`/`Silkscreen` fields, and `dnp` flags) directly into `EnvelopeFollower.kicad_pcb` using `kinet2pcb` and KiCad 10's bundled `pcbnew` Python API, while pulling the 6 HP × 3U Doepfer mechanical envelope (`29.60 × 107.00 mm` main board centered behind a `30.00 × 128.50 mm` panel) and footprint-to-bushing offset rules from `/eurorack-panel`.
2. **Pots, Jacks & LED on `F.Cu` Aligned to a 6 HP Front-Panel Grid**:
    Keeps the 8 user-facing through-hole controls (`RV1`–`RV4`, `J1`–`J3`, `D4`) on `F.Cu` facing the front panel and applies each footprint's shaft/bushing offset (`RD901F` pots, `WQP-PJ398SM` jacks, `3 mm` LED) so the physical shafts and jack bushings land on exact millimeter grid coordinates that [Stage 6](stage-6-front-panel.md) reads to drill the front panel.
3. **`J_PWR`, `DNP` Test Points (`TP1`–`TP8`) & 45 SMD Parts on `B.Cu`**:
    Flips everything that is not a front-panel control onto the rear of the PCB (`B.Cu`)—orienting `J_PWR` with Pin 1/2 (`-12V / RED STRIPE`) at the bottom per `/eurorack-panel`, flagging `TP1`–`TP8` as `DNP` (`exclude_from_pos_files`, `exclude_from_bom`) so JLCPCB leaves the `1.0 mm` probe holes open, and grouping all 45 SMD components by functional stage for single-sided **Bottom Side** JLCPCB Economic PCBA while keeping `F.Cu` completely clear under the pot and jack bodies.
4. **`@SilkscreenInstructions.md` Labels on `B.Cu` (`B.SilkS`) & Dual-Sided THT/TP Markup**:
    Follows `@SilkscreenInstructions.md` to print both Reference and Value (`R8 20k`, `C10 47pF`, `U1 TL074H`, etc.) on `B.SilkS` outside every SMD courtyard, print `TP1`–`TP8` and all 9 THT control/power labels (`RV1 GAIN A100k` … `J_PWR +/-12V`) on **both** `F.SilkS` and `B.SilkS`, and add external Pin-1/cathode/electrolytic `+` polarity markers plus the `5 × 5 mm` JLCPCB QR placeholder square.

## Step 5.1: How `generate_kicad_pcb.py` Works

1. **Dual-Environment Python Bootstrap & Board Initialization**:
    The agent installs `kinet2pcb` into `.venv` (`uv pip install kinet2pcb`). KiCad's compiled `pcbnew` C++ bindings only load inside KiCad's bundled Python (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`), while `kinet2pcb` and `simp_sexp` live in `.venv`. If `import pcbnew` fails under `.venv`, the script re-executes itself (`os.execv`) using `KICAD_PYTHON` and appends `.venv/lib/python*/site-packages` to `sys.path`. From there, `generate_kicad_pcb.py` parses `envelope_follower.net` (via S-expression parsing / `kinet2pcb`) and initializes the board via `pcbnew.LoadBoard()` on a minimal `.kicad_pcb` shell before calling `pcbnew.FootprintLoad()` and `fp.Flip()`.

2. **6 HP Mechanical Coordinates & Bushing Offsets**:
    The target 6 HP × 3U panel measures `30.00 x 128.50 mm` spanning global KiCad coordinates `X = [100.00, 130.00]`, `Y = [10.00, 138.50]`. Leaving `0.20 mm` horizontal clearance per side and `10.75 mm` vertical clearance top/bottom (clearing Eurorack rails and M3 screw heads) yields a main PCB outline of **`29.60 x 107.00 mm`** (`X = [100.20, 129.80]`, `Y = [20.75, 127.75]`).

    KiCad footprints do **not** put `(0, 0)` at the mechanical shaft or jack center. Inside KiCad's coordinate system ($X$ right, $Y$ down), rotating a local offset $(c_x, c_y)$ counter-clockwise by $\theta$ shifts the bushing relative to the footprint origin by:

    $$
    \Delta X = c_x \cos\theta + c_y \sin\theta, \qquad \Delta Y = -c_x \sin\theta + c_y \cos\theta
    $$

    | Component | Panel Role / Value | KiCad Footprint | Local `fp_circle` | Placement Rot | Offset $(\Delta X, \Delta Y)$ | Footprint Origin $(X, Y)$ | Target Panel Bushing $(X, Y)$ |
    | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
    | `RV1` | `GAIN` (`A100k`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `(7.50, 2.50)` | `90°` | `(+2.50, -7.50)` | `(112.50, 36.50)` | `(115.00, 29.00)` |
    | `RV2` | `ATK` (`A50k`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `(7.50, 2.50)` | `90°` | `(+2.50, -7.50)` | `(112.50, 53.00)` | `(115.00, 45.50)` |
    | `RV3` | `REL` (`A1M`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `(7.50, 2.50)` | `90°` | `(+2.50, -7.50)` | `(112.50, 69.50)` | `(115.00, 62.00)` |
    | `RV4` | `OFFSET` (`B10k`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `(7.50, 2.50)` | `90°` | `(+2.50, -7.50)` | `(112.50, 86.00)` | `(115.00, 78.50)` |
    | `J1` | `IN` (`3.5mm`) | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `(0.00, 6.48)` | `0°` | `(0.00, +6.48)` | `(108.00, 91.52)` | `(108.00, 98.00)` |
    | `D4` | `ENV` (`3mm LED`) | `LED_D3.0mm` | `(1.27, 0.00)` | `0°` | `(+1.27, 0.00)` | `(120.73, 98.00)` | `(122.00, 98.00)` |
    | `J2` | `OUT` (`3.5mm`) | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `(0.00, 6.48)` | `0°` | `(0.00, +6.48)` | `(108.00, 109.52)` | `(108.00, 116.00)` |
    | `J3` | `INV_OUT` (`3.5mm`) | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `(0.00, 6.48)` | `0°` | `(0.00, +6.48)` | `(122.00, 109.52)` | `(122.00, 116.00)` |

3. **Single-Sided `B.Cu` SMT Placement & `DNP` Test Points**:
    Keeping the 8 panel controls (`RV1`–`RV4`, `J1`–`J3`, `D4`) on `F.Cu` and placing all **45 SMD components** (`U1`, `U2`, `D1`–`D3`, `D5`–`D9`, `C1`–`C11`, `R1`–`R19`, `R21`, `R24`–`R27`) on **`B.Cu`** prevents backwards CW/CCW pot lug mirroring and left/right X-axis panel mirroring, avoids mechanical collision with `J_PWR` on `B.Cu`, keeps `F.Cu` clear beneath flush-mounted pot and jack housings across the narrow `29.60 mm` board width, and keeps all 45 SMD parts plus their `B.SilkS` value labels visible from the rear after the front panel is mounted—all at zero extra cost under **JLCPCB Economic PCBA** (single-sided assembly on **Bottom Side**).
    - `J_PWR` sits at `0°` on `B.Cu` with Pins 1–2 (`-12V_IN`) at the **bottom** and Pins 9–10 (`+12V_IN`) at the **top** per Eurorack convention.
    - Local decoupling caps `C5`–`C8` (`100 nF`) sit within `2 mm` of `U1` and `U2` pins 4 and 11; `R26`/`R27` (`10R` `1206`), `D5`/`D6` (`B5819W`), and `C3`/`C4` (`10 µF 50V`) cluster cleanly near `J_PWR`.
    - `TP1`–`TP8` (`TestPoint_Keystone_5000-5004_Miniature`, `1.0 mm` drill) are placed on `B.Cu` near their respective circuit nodes with KiCad's `dnp` / `exclude_from_pos_files` / `exclude_from_bom` attributes enabled so JLCPCB leaves the holes open for optional hand soldering.

4. **Automated Silkscreen Markup (`SilkscreenInstructions.md`)**:
    By default, KiCad places component `Value` fields on `F.Fab`/`B.Fab` (which are **excluded** from fabrication silkscreen Gerbers). `generate_kicad_pcb.py` enforces four silkscreen rules directly in the `.kicad_pcb`:
    - **Reference + Value on `B.SilkS` for Every SMD Part**: Unhides and places both `Reference` and concise `Value` (`U1 TL074H`, `R8 20k`, `C10 47pF`, `D8 BAT54S`, `R16 1k`, `R26 10R`, etc.) outside each component's courtyard and pads so unmarked `0603`/`0805` MLCCs and diodes are immediately verifiable in JLCPCB's 3D/DFM preview.
    - **Dual-Sided `F.SilkS` & `B.SilkS` Test Point Labels**: Prints `TP1 GND`, `TP2 +12V`, `TP3 -12V`, `TP4 PRE`, `TP5 HALF`, `TP6 RECT`, `TP7 ENV`, and `TP8 OFS` on **both** sides so probing works both during bare-board bring-up (`F.SilkS`) and from behind a mounted front panel (`B.SilkS`).
    - **Dual-Sided `F.SilkS` & `B.SilkS` THT Control & Power Labels**: Prints `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k`, `J1 IN`, `J2 OUT`, `J3 INV_OUT`, `D4 LED` (`+` anode / `-` cathode), and `J_PWR +/-12V` (`-12V / RED STRIPE`, `GND`, `+12V`) on **both** layers so identical-footprint pots and polarized leads cannot be reversed during solder-side assembly.
    - **External Polarity Marks & JLCPCB DFM Sizing**: Positions Pin-1 dots/notches (`U1`, `U2`), diode cathode bars (`|` on `D1`–`D3`, `D5`–`D7`), and electrolytic `+` symbols (`C3` on `+12V`; **`C4` `+` on `GND`**) outside the component bodies; enforces `0.9–1.2 mm` text height, `0.15 mm` stroke thickness, $\ge 0.20\text{ mm}$ pad clearance, `0°`/`90°` rotations only, a board metadata block (`EURORACK ENVELOPE FOLLOWER`, `Rev 1.0 / 2026-11`), and a `5 × 5 mm` solid square on `B.SilkS` for JLCPCB's order QR code.

5. **2-Layer Copper Routing, Sensitive Analog Nodes & Stitched `GND` Pours**:
    Rather than leaving an unrouted ratsnest, `generate_kicad_pcb.py` enforces power/analog layout rules and completes 2-layer copper routing plus `GND` zone pours automatically:
    - **Power Rail Routing (`B.Cu`)**: Routes `+12V_IN` and `-12V_IN` from `J_PWR` through Schottky diodes `D5`/`D6` (`B5819W`) and series `10 Ω` `1/4 W` (`1206`) resistors `R26`/`R27` into bulk `10 µF` electrolytics `C3`/`C4` (`C4` `+` pad on `GND`, `-` pad on `-12V`), then distributes widened `+12V` and `-12V` power tracks (`0.30–0.60 mm` width; `0.25 mm` for signal nets) through local `100 nF` bypass caps `C5`–`C8` before reaching `U1`/`U2` Pins 4 and 11, and branches to `BAT54S` rail clamps `D8`/`D9`, bias resistors `R11`/`R12`, and test points `TP2` (`+12V`) / `TP3` (`-12V`) with `TP1` anchored on `GND`.
    - **Sensitive Summing Junctions & High-Impedance `ENV_CAP`**: Keeps inverting summing nodes (`PREAMP_INV` at `U1A` Pin 2, `RECT1_INV` at `U1B` Pin 6, `RECT2_INV` at `U1C` Pin 9, `PK_FB_INV` at `U2C` Pin 9, `AMP_INV` at `U1D` Pin 13, `INV_STAGE_IN` at `U2A` Pin 2, and `LED_K` at `U2B` Pin 6) compact; isolates the high-impedance `ENV_CAP` node (`RV2`, `C2` `220 nF`, `R10` `47k`, `U2D` Pin 12 `+`) from power traces while wiring `TP7` (`ENV`) strictly to buffered `ENV_SIG` (`U2D` Pin 14); places `C9` (`100 nF`) directly at `RV4` wiper (`OFFSET_WIPER`) and keeps `D8`/`R16` and `D9`/`R19` close to output jacks `J2` and `J3`.
    - **2-Layer A\* Grid Routing (`GridRouter`) & Stitched `GND` Copper Pours (`F.Cu` + `B.Cu`)**: Pre-places immediate `B.Cu` SMD `GND` stitching vias and perimeter vias (`0.60–0.80 mm` pad / `0.30–0.40 mm` drill), routes all 35 non-`GND` nets with outward `SOIC-14` escape stubs (blocking vias inside SMD pads for `0` `VP-001` warnings, using free THT barrel layer transitions for `0` `holes_co_located`, and preserving T-junction vertices when merging collinear segments for `0` `track_dangling`), and fills full-board `F.Cu` and `B.Cu` `GND` zones (`0.30 mm` inset from `Edge.Cuts`, thermal relief spokes) via `pcbnew.ZONE_FILLER(board).Fill(zones)` with `ISLAND_REMOVAL_MODE_ALWAYS` and `board.BuildConnectivity()` called both before and after filling.

6. **Automated DRC & `kicad` Skill PCB Audit**:
    After generating `EnvelopeFollower.kicad_pcb`, verify physical, electrical, and DFM compliance using KiCad 10's CLI Design Rules Checker and the `kicad` skill's PCB analyzer:

    ```bash
    /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
        --refill-zones --exit-code-violations --format json \
        --output /tmp/main_drc.json EnvelopeFollower.kicad_pcb

    python3 .agents/skills/kicad/scripts/analyze_pcb.py EnvelopeFollower.kicad_pcb --full --analysis-dir analysis/
    ```

    Confirm `0` DRC errors, `0` clearance violations, `0` unrouted nets (`routing_complete: True`), `0` `silk_overlap` / `silk_over_copper` violations, decoupling proximity, `DNP` test-point flags, and `100%` fabrication notes completeness.

Run the script to generate [`EnvelopeFollower.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_pcb):

```bash
.venv/bin/python generate_kicad_pcb.py
```

Output:

```text
Generated EnvelopeFollower.kicad_pcb: 62 footprints (54 populated + 8 DNP), 36 nets, outline 29.60 x 107.00 mm.
```

| Main PCB Front (`F.Cu` — THT Panel Controls) | Main PCB Rear (`B.Cu` — SMT, `J_PWR` & `TP1`–`TP8`) |
| :---: | :---: |
| ![Main PCB Front (F.Cu Controls)](../images/pcb_front.png) | ![Main PCB Back (B.Cu SMT & Power Header)](../images/pcb_back.png) |

---

## Step 5.2: Semantic Silkscreen & Polarity Audit (Verification & Fix Prompts)

Geometric verification tools (`kicad-cli pcb drc` and `analyze_pcb.py`) confirm **physical and electrical rules** (`0` copper shorts, `0` unrouted nets, `0` `silk_overlap` / `silk_over_copper` violations, and `62/62` visible reference designators), but they do **not** verify **semantic label parity**—whether the human-readable function/value text printed next to each footprint actually matches `@SilkscreenInstructions.md` and the `Silkscreen` fields inside `envelope_follower.net`, or whether every polarized package category in `@SilkscreenInstructions.md` Section 5 received its external orientation mark.

For example, in our Stage 5 trace (`357a293d`), the generator script passed DRC with `0` violations, yet a semantic comparison against `@SilkscreenInstructions.md` revealed two issues:

1. **Hardcoded Override Drift (`SILK_VALUE_OVERRIDES`)**: The script overrode the netlist's `Silkscreen` metadata on `J2`, `J3`, `RV4`, `D4`, and `TP1`/`TP4`–`TP8` with labels from a Gate/Threshold comparator circuit (`J2 ENV`, `J3 GATE`, `RV4 THRESH`, `D4 GATE`, `TP1 GAIN`, `TP4 RECT`, `TP5 ATK`, `TP6 ENV`, `TP7 BUF`, `TP8 GATE`) instead of the actual design labels (`J2 OUT`, `J3 INV_OUT`, `RV4 OFFSET`, `D4 LED`, `TP1 GND`, `TP4 PRE`, `TP5 HALF`, `TP6 RECT`, `TP7 ENV`, `TP8 OFS`).
2. **Missing Electrolytic `+` Polarity Marks (`C3`, `C4`)**: External Pin-1 dots (`U1`, `U2`), `SOD-123` cathode bars (`D1`–`D3`, `D5`–`D7`), `D4` `+`/`-` markers, and `J_PWR` `-12V RED` stripe bars were placed, but external `+` polarity symbols outside the positive pads of SMD bulk electrolytic capacitors `C3` (`+12V` pad) and `C4` (`GND` pad) were omitted.

### 1. Verification Prompt (Finds Semantic Label & Polarity Discrepancies)

Run this follow-up audit prompt to catch any drift between the generated PCB silkscreen and `@SilkscreenInstructions.md`:

> *"Please audit `generate_kicad_pcb.py` and the generated `EnvelopeFollower.kicad_pcb` against `@SilkscreenInstructions.md` and `@envelope_follower.net`. Check: (1) whether every component's rendered silkscreen value/function label on `F.SilkS` and `B.SilkS` matches the exact schedule in `@SilkscreenInstructions.md` (Sections 3, 4, and 7) and the `Silkscreen` field in `@envelope_follower.net` rather than hardcoded overrides, and (2) whether all polarized component categories in `@SilkscreenInstructions.md` Section 5 (`U1`/`U2` Pin-1 dots, `D1`–`D3`/`D5`–`D7` cathode bars, `D4` `+`/`-`, `J_PWR` `-12V RED` bar, and `C3`/`C4` external electrolytic `+` marks) are present on the silkscreen. Report every discrepancy without editing files yet."*

### 2. Fix Prompt (Resolves Discrepancies & Re-Verifies DRC)

Once the audit lists the mismatches, send this prompt to fix them and re-verify the board (and update `kicad-silkscreen-markup` if you extracted the skill in Step 5.3):

> *"Please update `generate_kicad_pcb.py` (and `.agents/skills/kicad-silkscreen-markup/` if present) to fix every silkscreen discrepancy found in the audit: derive component value/function labels from `@envelope_follower.net` and `@SilkscreenInstructions.md` (`J1 IN`, `J2 OUT`, `J3 INV_OUT`, `RV1 GAIN`, `RV2 ATK`, `RV3 REL`, `RV4 OFFSET`, `D4 LED`, `J_PWR +/-12V`, `U1`/`U2 TL074H`, and `TP1 GND`, `TP2 +12V`, `TP3 -12V`, `TP4 PRE`, `TP5 HALF`, `TP6 RECT`, `TP7 ENV`, `TP8 OFS`), add external `+` polarity markers on `B.SilkS` outside the positive anode pads of `C3` (Pad 1 / `+12V`) and `C4` (Pad 1 / `GND`), re-run `generate_kicad_pcb.py`, and re-verify with `ruff`, `kicad-cli pcb drc --refill-zones`, and `analyze_pcb.py`."*

---

## Step 5.3 (Optional): Extracting Reusable PCB & Silkscreen Skills (`/agy-customizations`)

Looking at the 7 skills installed in [Stage 1](stage-1-agent-skills.md), there is a natural boundary between `skidl` (which ends at `envelope_follower.net`), `eurorack-panel` (which inspects an existing main `.kicad_pcb` to build the 3U front panel), and `kicad` (which audits an existing `.kicad_pcb`). Turning `envelope_follower.net` into a routed, DFM-clean 2-layer `.kicad_pcb` required solving several non-obvious KiCad 10 `pcbnew` API and silkscreen geometry problems during Stage 5.

You can use the built-in `/agy-customizations` skill right after Stage 5 to distill those hard-won patterns into reusable workspace skills under `.agents/skills/`:

### AI Agent Prompts

> *"`/agy-customizations` are there skills that could be created from this step?"*
>
> *"Please create these skills, and append to the build log in `@README.md`."*

### Resulting Workspace Skills

1. **`kicad-pcbnew-layout` (`.agents/skills/kicad-pcbnew-layout/`)**:
   - **`SKILL.md` & References (`kicad10_pcbnew_api.md`, `routing_and_dfm_patterns.md`)**: Documents self-bootstrapping to KiCad 10's bundled Python (`os.execv`), initializing boards via `pcbnew.LoadBoard()` on a minimal shell (preventing the `fp.Flip()` segfault on raw `pcbnew.BOARD()`), Eurorack `F.Cu` controls + `B.Cu` SMD/power sandwich placement, pre-placing immediate `B.Cu` SMD `GND` stitching vias before signal routing, blocking vias inside SMD pad bounds (`0` `VP-001` via-in-pad warnings), free layer transitions at THT barrels (`0` `holes_co_located`), preserving T-junction vertices during collinear track merging (`0` `track_dangling`), and calling `board.BuildConnectivity()` both **before and after** `ZONE_FILLER.Fill()` with `ISLAND_REMOVAL_MODE_ALWAYS`.
   - **`scripts/pcbnew_layout_template.py`**: Reusable S-expression `.net` parser, board initializer, 2-layer `GridRouter`, `GND` zone filler, and `--netlist` summary CLI.
2. **`kicad-silkscreen-markup` (`.agents/skills/kicad-silkscreen-markup/`)**:
   - **`SKILL.md`**: Documents measuring true KiCad stroke-font bounding boxes via a cached scratch `pcbnew.PCB_TEXT(board).GetBoundingBox()` (avoiding character-width heuristics that clip uppercase glyphs), seeding `SilkGrid` with both solder-mask pad openings (`+0.25 mm`) and non-text footprint graphics (`+0.20 mm`), pairing visible `fp.Reference()` on `.SilkS` with a `PCB_TEXT(fp)` value item (`62/62` `refs_visible_on_silk`, `0` `values_visible_on_silk` warnings), handling `B.SilkS` mirroring (`+X` = visual left), placing external polarity markers and `5 × 5 mm` JLCPCB QR squares, and emitting the 6 required `B.Fab` keywords for `100%` `fab_notes_completeness`.
   - **`scripts/silk_annotator.py`**: Reusable `SilkGrid` collision detector, exact text measurer, `add_standard_fab_notes()` helper, and `--inspect <board.kicad_pcb>` CLI that checks reference visibility and text bounding-box overlaps on any KiCad PCB.
