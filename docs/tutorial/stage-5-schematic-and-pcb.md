# Stage 5: Generating the KiCad Schematic, 6 HP Main PCB & Silkscreen Markup

## Part A: Auto-Generated KiCad Schematic (`EnvelopeFollower.kicad_sch`)

Calling `generate_schematic(...)` at the bottom of `envelope_follower.py` converts the SKiDL netlist into [`EnvelopeFollower.kicad_sch`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_sch) using SKiDL's `schematizer` router:

```python
import schematizer.engine.gen_schematic as _gs

# Disable two-pin snapping in schematizer so series protection diodes (D5, D6)
# and series RC resistors (R26, R27) do not overlap J_PWR pins.
_gs._snap_two_pin_parts = lambda node: None
```

Disabling `_snap_two_pin_parts` prevents compact series diodes (`D5`, `D6`) and series `10 Ω` resistors (`R26`, `R27`) from visually snapping onto adjacent header pins in the schematic canvas.

![Generated KiCad Schematic](../images/EnvelopeFollower.svg)

*(Exported directly via `kicad-cli sch export svg --output docs/images/ EnvelopeFollower.kicad_sch`.)*

---

## Part B: Generating the 6 HP Main PCB (`generate_kicad_pcb.py`)

Rather than importing the netlist manually and placing 62 footprints by hand in `pcbnew`, [`generate_kicad_pcb.py`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/generate_kicad_pcb.py) automates the board outline, control grid, single-sided `B.Cu` SMT placement, `DNP` test points, BOM metadata transfer, and dual-sided silkscreen markup.

### AI Agent Prompt

> *"Update `generate_kicad_pcb.py` using KiCad's `pcbnew` Python API and `kinet2pcb` to generate `EnvelopeFollower.kicad_pcb` from `envelope_follower.net` (62 footprints, 36 nets). Size the board for 6 HP (`29.60 x 107.00 mm`) centered behind a `30.00 x 128.50 mm` Doepfer 3U panel. Place the 4 pots (`RV1`–`RV4`), `D4` (LED), and 3 jacks (`J1`–`J3`) on `F.Cu` aligned to the panel grid using exact bushing offsets. Flip `J_PWR` (Pin 1 / `-12V RED STRIPE` at the bottom), `TP1`–`TP8` (`Ronghe RH-5001`, marked `DNP` / `exclude_from_pos_files`), and all 45 SMD parts onto `B.Cu` grouped by subcircuit. Apply the silkscreen rules from `SilkscreenInstructions.md`: show both Reference and Value on `B.SilkS` for every SMD part outside its courtyard, print `TP1`–`TP8` and all 9 THT parts (`RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k`, `J1 IN`, `J2 OUT`, `J3 INV_OUT`, `D4 LED +/-`, `J_PWR +/-12V`) on both `F.SilkS` and `B.SilkS`, and add external Pin-1/cathode/electrolytic `+` polarity marks."*

### How `generate_kicad_pcb.py` Works

1. **Dual-Environment Python Bootstrap**:
    KiCad's compiled `pcbnew` C++ bindings only load inside KiCad's bundled Python (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`), while `kinet2pcb` and `simp_sexp` live in `.venv`. If `import pcbnew` fails under `.venv`, the script re-executes itself (`os.execv`) using `KICAD_PYTHON` and appends `.venv/lib/python*/site-packages` to `sys.path`.

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
    Because `RV1`–`RV4` and `J1`–`J3` mount flush against `F.Cu` across the narrow `29.60 mm` board width, placing all **45 SMD components** (`U1`, `U2`, `D1`–`D3`, `D5`–`D9`, `C1`–`C11`, `R1`–`R19`, `R21`, `R24`–`R27`) on **`B.Cu`** keeps `F.Cu` mechanically clear for panel controls while qualifying for **JLCPCB Economic PCBA** (single-sided assembly on **Bottom Side**).
    - `J_PWR` sits at `0°` on `B.Cu` with Pins 1–2 (`-12V_IN`) at the **bottom** and Pins 9–10 (`+12V_IN`) at the **top** per Eurorack convention.
    - Local decoupling caps `C5`–`C8` (`100 nF`) sit within `2 mm` of `U1` and `U2` pins 4 and 11; `R26`/`R27` (`10R` `1206`), `D5`/`D6` (`B5819W`), and `C3`/`C4` (`10 µF 50V`) cluster cleanly near `J_PWR`.
    - `TP1`–`TP8` (`TestPoint_Keystone_5000-5004_Miniature`, `1.0 mm` drill) are placed on `B.Cu` near their respective circuit nodes with KiCad's `dnp` / `exclude_from_pos_files` / `exclude_from_bom` attributes enabled so JLCPCB leaves the holes open for optional hand soldering.

4. **Automated Silkscreen Markup (`SilkscreenInstructions.md`)**:
    By default, KiCad places component `Value` fields on `F.Fab`/`B.Fab` (which are **excluded** from fabrication silkscreen Gerbers). `generate_kicad_pcb.py` enforces four silkscreen rules directly in the `.kicad_pcb`:
    - **Reference + Value on `B.SilkS` for Every SMD Part**: Unhides and places both `Reference` and concise `Value` (`U1 TL074H`, `R8 20k`, `C10 47pF`, `D8 BAT54S`, `R16 1k`, `R26 10R`, etc.) outside each component's courtyard and pads so unmarked `0603`/`0805` MLCCs and diodes are immediately verifiable in JLCPCB's 3D/DFM preview.
    - **Dual-Sided `F.SilkS` & `B.SilkS` Test Point Labels**: Prints `TP1 GND`, `TP2 +12V`, `TP3 -12V`, `TP4 PRE`, `TP5 HALF`, `TP6 RECT`, `TP7 ENV`, and `TP8 OFS` on **both** sides so probing works both during bare-board bring-up (`F.SilkS`) and from behind a mounted front panel (`B.SilkS`).
    - **Dual-Sided `F.SilkS` & `B.SilkS` THT Control & Power Labels**: Prints `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k`, `J1 IN`, `J2 OUT`, `J3 INV_OUT`, `D4 LED` (`+` anode / `-` cathode), and `J_PWR +/-12V` (`-12V / RED STRIPE`, `GND`, `+12V`) on **both** layers so identical-footprint pots and polarized leads cannot be reversed during solder-side assembly.
    - **External Polarity Marks & JLCPCB DFM Sizing**: Positions Pin-1 dots/notches (`U1`, `U2`), diode cathode bars (`|` on `D1`–`D3`, `D5`–`D7`), and electrolytic `+` symbols (`C3` on `+12V`; **`C4` `+` on `GND`**) outside the component bodies; enforces `0.9–1.2 mm` text height, `0.15 mm` stroke thickness, $\ge 0.20\text{ mm}$ pad clearance, `0°`/`90°` rotations only, a board metadata block (`EURORACK ENVELOPE FOLLOWER`, `Rev 1.0 / 2026-11`), and a `5 × 5 mm` solid square on `B.SilkS` for JLCPCB's order QR code.

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
