# Stage 3: Translating the Improved Circuit to SKiDL (`envelope_follower.py`)

Defining the circuit in **SKiDL** turns the netlist into testable, version-controlled Python code that enforces `ERC()` assertions and outputs both a KiCad netlist and a JLCPCB-ready BOM in one execution—while keeping optional `DNP` test points and manual THT panel hardware cleanly separated from the SMT PCBA BOM.

## AI Agent Prompt

> *"Using the `skidl`, `bom`, `datasheets`, `jlcpcb`, and `lcsc` skills together with `EnvelopeFollowerImproved.md` and `EnvelopeFollowerBOM.md`, implement the improved Eurorack Envelope Follower in `envelope_follower.py` using dual `TL074H` (`SOIC-14`, all 8 op-amp channels active). Populate verified `LCSC`, `MPN`, and `JLCPCB_Class` fields, add `TP1`–`TP8` (`Ronghe RH-5001`, `C5199801`) marked `dnp=True` / `Manual THT`, verify `ERC()` passes with 0 errors and 0 warnings, and export `envelope_follower.net`, `envelope_follower_bom.xml`, `jlcpcb_bom.csv`, and `EnvelopeFollower.kicad_sch`."*

## Step 3.1: Set Up the Python Environment & Query Parts

Create an isolated `.venv` with `uv` (Python 3.14 avoids compiling `h5py` from source) and install `skidl` and `kinet2pcb`:

```bash
uv venv --clear --python 3.14 .venv
uv pip install skidl kinet2pcb
```

Verify live JLCPCB stock and Basic vs. Extended pricing for the active ICs, clamps, precision passives, and test points using `jlcpcb_search.py` (or the `lcsc` / `jlcpcb` skills):

```bash
.venv/bin/python .agents/skills/skidl/scripts/jlcpcb_search.py \
    --in-stock-only "TL074HIDR" "BAT54SLT1G" "B5819W" "1N4148W" "47pF 0603" "220nF 0805" "10R 1206" "1k 1206"
```

You can also inspect exact KiCad 10 symbol pins before coding (`show("Amplifier_Operational", "TL074")`, `show("Diode", "BAT54S")`, `show("Connector_Audio", "AudioJack2_SwitchT")`, `show("Connector", "TestPoint")`).

## Step 3.2: Anatomy of `envelope_follower.py`

In `envelope_follower.py`, five SKiDL patterns make the improved 54-part (+8 `DNP` test points), 36-net circuit modular and fabrication-ready:

1. **Pre-Import Environment Setup**:
    Before importing `skidl`, set `XDG_DATA_HOME`, `MPLCONFIGDIR`, `KICAD10_SYMBOL_DIR`, `KICAD_SYMBOL_DIR`, and `KICAD10_FOOTPRINT_DIR` so SKiDL resolves KiCad 10's `.kicad_sym` libraries cleanly on macOS.

2. **Reusable Templates, `part.fields` Metadata & `DNP` Test Points**:
    All passives, diodes, panel controls, and test loops derive from `dest=TEMPLATE` parts (`make_templates()`). Catalog metadata is written into `part.fields["LCSC"]`, `part.fields["MPN"]`, and `part.fields["JLCPCB_Class"]` (rather than plain Python attributes, which SKiDL's netlist/XML exporters ignore):

    ```python
    # Verified JLCPCB Basic 1% thick-film resistors (0603 & 1206)
    JLCPCB_RESISTORS_0603 = {
        "1k": ("C21190", "0603WAF1001T5E", "Basic"),
        "1.5k": ("C22843", "0603WAF1501T5E", "Basic"),
        "10k": ("C25804", "0603WAF1002T5E", "Basic"),
        "20k": ("C4184", "0603WAF2002T5E", "Basic"),
        "47k": ("C25819", "0603WAF4702T5E", "Basic"),
        "100k": ("C25803", "0603WAF1003T5E", "Basic"),
        "1M": ("C22935", "0603WAF1004T5E", "Basic"),
    }

    JLCPCB_RESISTORS_1206 = {
        "10R 1/4W": ("C17903", "1206W4F100JT5E", "Basic"),
        "1k 1/4W": ("C4410", "1206W4F1001T5E", "Basic"),
    }
    ```

    - **Panel THT Controls** (`RV1`–`RV4`, `J1`–`J3`, `D4`, `J_PWR`) are tagged `JLCPCB_Class = "Manual THT"` so `generate_jlcpcb_bom()` excludes them from the SMT pick-and-place CSV.
    - **Optional Test Points (`TP1`–`TP8`)** instantiate `Part("Connector", "TestPoint", footprint="TestPoint:TestPoint_Keystone_5000-5004_Miniature")` with `LCSC = "C5199801"`, `MPN = "RH-5001"`, `JLCPCB_Class = "Manual THT"`, and `part.dnp = True` so both the JLCPCB BOM and the `.pos` centroid file leave those `1.0 mm` holes unpopulated.

3. **Power `Interface` & `NetClass` Rules**:
    Power rails (`+12V_IN`, `+12V_PROT`, `+12V`, `-12V_IN`, `-12V_PROT`, `-12V`, `GND`) are bundled into a SKiDL `Interface`, assigned `NetClass("Power", priority=1, trace_width=0.6, clearance=0.25)`, and marked `drive = POWER` on the power-entry rails so ERC verifies every supply connection.

4. **Seven `@subcircuit` Functional Blocks (All 8 `TL074H` Channels Active)**:
    Each stage uses SKiDL's series network operator (`&`) and pin attachment operator (`+=`), connecting unused normalled jack switches (`j1["TN"]`, `j2["TN"]`, `j3["TN"]`) to `builtins.NC`. Notice how `U2C` and `U2D` now form the Stage 4 active peak detector and JFET buffer:

    ```python
    # Stage 3: Precision Full-Wave Rectifier (U1B + U1C, 1.0x symmetry with R8 = 20k)
    preamp_out & r6 & ff_mid & r7 & rect2_inv
    half_rect & r5 & rect2_inv
    rect2_inv += u1[9]
    gnd += u1[10]
    full_rect += u1[8]
    rect2_inv & r8 & full_rect

    # Stage 4: Active Zero-Deadzone Peak Detector (U2C) & Buffer (U2D)
    full_rect += u2[10]
    pk_fb_inv += u2[9]
    pk_drv_out += u2[8]
    pk_drv_out & d3["A", "K"] & atk_in & r9 & atk_mid & rv2[1, 2] & env_cap
    rv2[2] += rv2[3]
    pk_fb_inv & d7["A", "K"] & pk_drv_out  # Anti-saturation catch diode
    pk_fb_inv & c11 & pk_drv_out           # 47 pF C0G loop compensation
    env_cap & c2 & gnd                     # 220 nF hold cap
    env_cap & r10 & rel_mid & rv3[1, 2] & gnd
    rv3[3] += gnd
    env_cap += u2[12]                      # U2D JFET buffer (+)
    env_sig += u2[13, 14]                  # U2D (-) tied to output
    env_sig & r24 & pk_fb_inv              # 100k isolated feedback to U2C
    ```

    Similarly, Stage 5 (`U1D`) and Stage 6 (`U2A`) wire each `BAT54S` dual Schottky rail clamp (`D8` on `AMP_OUT`, `D9` on `INV_AMP_OUT`) with pin `1` (`A`) to `-12V`, pin `2` (`K`) to `+12V`, and pin `3` (`COM`) to the op-amp output ahead of `1/4 W` `1206` resistors `R16`/`R19`, while Stage 7 (`U2B`) places `D4` (`3 mm` LED) between pin `7` (`LED_A`) and pin `6` (`LED_K`) with `R21` (`1.5k`) to `GND`.

5. **Programmatic `erc_assert()` & Exports**:
    Custom assertions verify package pin counts (`len(u1.get_pins()) == 14`, `len(u2.get_pins()) == 14`) and power connections before calling `ERC()`, `generate_netlist()`, `generate_xml()`, `generate_jlcpcb_bom()` (skipping `Manual THT` and `dnp=True`), and `generate_schematic()`.

## Step 3.3: Run SKiDL & Inspect Outputs

```bash
.venv/bin/python envelope_follower.py
ruff check --fix envelope_follower.py envelope_follower_sklib.py
ruff format envelope_follower.py envelope_follower_sklib.py
```

Key generated files:

- [`envelope_follower.erc`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower.erc): `ERC INFO: No errors or warnings found while running ERC.`
- [`envelope_follower.net`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower.net): KiCad netlist containing all **54 populated physical components + 8 `DNP` test points (62 footprints total)** and **36 nets**.
- [`envelope_follower_bom.xml`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower_bom.xml): Full XML BOM with embedded `LCSC`, `MPN`, `JLCPCB_Class`, `DNP`, and `Notes` fields.
- [`jlcpcb_bom.csv`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/jlcpcb_bom.csv): Grouped 4-column JLCPCB SMT BOM (`Comment,Designator,Footprint,LCSC Part #`) with **18 SMT line items** (**45 SMD components total**: `15` JLCPCB Basic lines + `3` Extended lines; the `9` required THT parts and `8` `DNP` test points are excluded automatically).

??? info "Preview of generated `jlcpcb_bom.csv` (18 SMT line items, 45 SMD components)"

    ```csv
    Comment,Designator,Footprint,LCSC Part #
    TL074HIDR,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
    1N4148W,"D1, D2, D3, D7",D_SOD-123,C81598
    B5819W,"D5, D6",D_SOD-123,C8598
    BAT54SLT1G,"D8, D9",SOT-23,C19726
    1uF 50V,C1,C_0603_1608Metric,C15849
    220nF 50V,C2,C_0805_2012Metric,C5378
    10uF 50V,"C3, C4",CP_Elec_6.3x5.4,C72488
    100nF 50V,"C5, C6, C7, C8, C9",C_0603_1608Metric,C14663
    47pF 50V,"C10, C11",C_0603_1608Metric,C1671
    1M,R1,R_0603_1608Metric,C22935
    10k,"R2, R3, R4, R5, R6, R7, R17, R18",R_0603_1608Metric,C25804
    20k,R8,R_0603_1608Metric,C4184
    1k,"R9, R11, R12, R25",R_0603_1608Metric,C21190
    47k,R10,R_0603_1608Metric,C25819
    100k,"R13, R14, R15, R24",R_0603_1608Metric,C25803
    1k 1/4W,"R16, R19",R_1206_3216Metric,C4410
    1.5k,R21,R_0603_1608Metric,C22843
    10R 1/4W,"R26, R27",R_1206_3216Metric,C17903
    ```
