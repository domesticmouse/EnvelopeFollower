# Stage 3: Translating the Schematic to SKiDL (`envelope_follower.py`)

Defining the circuit in **SKiDL** turns the netlist into testable, version-controlled Python code that enforces `ERC()` assertions and outputs both a KiCad netlist and a JLCPCB-ready BOM in one execution.

## AI Agent Prompt

> *"Using the `skidl` skill and `ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md`, implement the Envelope Follower circuit in `envelope_follower.py` using dual `TL074H` (`SOIC-14`) packages across 6 `@subcircuit` blocks. Query live JLCPCB/LCSC parts with `jlcpcb_search.py` to populate `LCSC`, `MPN`, and `JLCPCB_Class` fields, verify `ERC()` passes with 0 errors and 0 warnings, and export `envelope_follower.net`, `envelope_follower_bom.xml`, `jlcpcb_bom.csv`, and `EnvelopeFollower.kicad_sch`."*

## Step 3.1: Set Up the Python Environment & Query Parts

Create an isolated `.venv` with `uv` (Python 3.14 avoids compiling `h5py` from source) and install `skidl` and `kinet2pcb`:

```bash
uv venv --clear --python 3.14 .venv
uv pip install skidl kinet2pcb
```

Query JLCPCB stock and pricing directly from the `skidl` skill's catalog helper:

```bash
.venv/bin/python .agents/skills/skidl/scripts/jlcpcb_search.py \
    --in-stock-only "TL074HIDR" "B5819W" "1N4148W" "10k 0603" "100nF 0603"
```

You can also inspect exact KiCad 10 symbol pins before coding (`show("Amplifier_Operational", "TL074")`, `show("Connector_Audio", "AudioJack2_SwitchT")`).

## Step 3.2: Anatomy of `envelope_follower.py`

In [`envelope_follower.py`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower.py), five SKiDL patterns make the circuit modular and fabrication-ready:

1. **Pre-Import Environment Setup (Lines 15–30)**:
    Before importing `skidl`, set `XDG_DATA_HOME`, `MPLCONFIGDIR`, `KICAD10_SYMBOL_DIR`, `KICAD_SYMBOL_DIR`, and `KICAD10_FOOTPRINT_DIR` so SKiDL resolves KiCad 10's `.kicad_sym` libraries cleanly on macOS.
2. **Reusable Templates & `part.fields` Dictionary (Lines 70–148)**:
    All 2-pin passives and panel hardware derive from `dest=TEMPLATE` parts (`make_templates()`). Catalog metadata is written into `part.fields["LCSC"]`, `part.fields["MPN"]`, and `part.fields["JLCPCB_Class"]` (rather than plain Python attributes, which SKiDL's netlist/XML exporters ignore):

    ```python
    JLCPCB_RESISTORS_0603 = {
        "1k": ("C21190", "0603WAF1001T5E", "Basic"),
        "10k": ("C25804", "0603WAF1002T5E", "Basic"),
        "22k": ("C31850", "0603WAF2202T5E", "Basic"),
        "33k": ("C4216", "0603WAF3302T5E", "Basic"),
        "1M": ("C22935", "0603WAF1004T5E", "Basic"),
    }
    ```

    Panel-mounted controls (`RV_*`, `J_IN`, `J_OUT`, `J_INV_OUT`, `LED1`, `J_PWR`) are tagged `JLCPCB_Class = "Manual THT"` so the SMT BOM generator excludes them automatically.
3. **Power `Interface` & `NetClass` Rules (Lines 476–486)**:
    Power rails are bundled into a SKiDL `Interface`, marked `drive = POWER` so ERC knows they are externally driven, and assigned to a `NetClass("Power", priority=1, trace_width=0.6, clearance=0.25)`.
4. **Six `@subcircuit` Functional Blocks (Lines 151–443)**:
    Each stage uses SKiDL's series network operator (`&`) and pin attachment operator (`+=`), while intentionally unused normalled jack switches (`j_in["TN"]`, `j_out["TN"]`, `j_inv_out["TN"]`) connect to `builtins.NC`:

    ```python
    # Example from precision_rectifier_stage (U1B + U1C)
    out_gain & r5 & sum_top_mid & r6 & sum_in
    half_wave_node & r7 & sum_in
    sum_in += u1[9]
    gnd += u1[10]
    rect_out += u1[8]
    sum_in & r8 & rect_out
    ```

5. **Programmatic `erc_assert()` & Exports (Lines 500–531)**:
    Custom assertions verify package pin counts (`len(u1.get_pins()) == 14`) and power connections before calling `ERC()`, `generate_netlist()`, `generate_xml()`, `generate_jlcpcb_bom()`, and `generate_schematic()`.

## Step 3.3: Run SKiDL & Inspect Outputs

```bash
.venv/bin/python envelope_follower.py
ruff check --fix envelope_follower.py envelope_follower_sklib.py
ruff format envelope_follower.py envelope_follower_sklib.py
```

Key generated files:

- [`envelope_follower.erc`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower.erc): `ERC INFO: No errors or warnings found while running ERC.`
- [`envelope_follower.net`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower.net): KiCad netlist containing all **48 physical components** and **35 nets**.
- [`envelope_follower_bom.xml`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/envelope_follower_bom.xml): Full XML BOM with embedded `LCSC`, `MPN`, `JLCPCB_Class`, and `Notes` fields.
- [`jlcpcb_bom.csv`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/jlcpcb_bom.csv): Grouped 4-column JLCPCB SMT BOM (`Comment,Designator,Footprint,LCSC Part #`) with **12 SMT line items** (39 SMT components total; the 9 THT components are filtered out as `Manual THT`).

??? info "Preview of generated `jlcpcb_bom.csv` (12 SMT line items)"

    ```csv
    Comment,Designator,Footprint,LCSC Part #
    TL074H,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
    B5819W,"D4, D5",D_SOD-123,C8598
    4.7uF,"C3, C4",CP_Elec_4x5.4,C5246584
    100nF,"C5, C6, C7, C8",C_0603_1608Metric,C14663
    4.7uF,C1,C_0805_2012Metric,C354262
    1M,R1,R_0603_1608Metric,C22935
    10k,"R2, R3, R4, R5, R6, R7, R10, R11, R12, R13, R14, R15, R17, R18, R20, R22",R_0603_1608Metric,C25804
    1k,"R_GAIN_MIN, R9, R16, R19",R_0603_1608Metric,C21190
    22k,"R8, R21",R_0603_1608Metric,C31850
    1N4148W,"D1, D2, D3",D_SOD-123,C81598
    1uF,C2,C_0603_1608Metric,C559769
    33k,R23,R_0603_1608Metric,C4216
    ```
