# Stage 4: Translating the Improved Circuit to SKiDL (`envelope_follower.py`)

Defining the circuit in **SKiDL** turns the netlist into testable, version-controlled Python code that enforces `ERC()` assertions and outputs both a KiCad netlist and a JLCPCB-ready BOM in one execution—while keeping optional `DNP` test points and manual THT panel hardware cleanly separated from the SMT PCBA BOM.

## AI Agent Prompt

Because [Stage 3](stage-3-bom-and-dfm.md) already froze every net, component reference, LCSC code, and `DNP` attribute inside `EnvelopeFollowerImproved.md` and `EnvelopeFollowerBOM.md`, you only need a single prompt to drive the `/skidl` skill:

> *"`/skidl` Please turn `@EnvelopeFollowerImproved.md` and `@EnvelopeFollowerBOM.md` into a SKiDL circuit."*

!!! note "One Prompt Runs the Entire Stage"
    **You do not need to run the commands below manually.** Sending this single prompt causes the AI agent (guided by `.agents/skills/skidl/SKILL.md`) to execute Steps 4.1–4.3 automatically behind the scenes:

    - Creating the isolated Python 3.14 `.venv` and installing `skidl`.
    - Inspecting KiCad 10 symbol pins and footprint pad polarities (and optionally querying `jlcpcb_search.py` if any LCSC codes need live verification).
    - Writing `envelope_follower.py` with all `62` components (`2× TL074H`, `45` SMD parts, `9` manual THT parts, and `8` `DNP` `TP1`–`TP8` test points) across `36` nets.
    - Running `.venv/bin/python envelope_follower.py`, verifying `ERC()` passes with `0` errors and `0` warnings, exporting `envelope_follower.net`, `envelope_follower_bom.xml`, and `jlcpcb_bom.csv`, and formatting the code with `ruff`.

    Steps 4.1–4.3 below show what the agent executes under the hood—and give you the exact commands to re-run manually if you ever edit `envelope_follower.py` by hand.

## Step 4.1: Environment Setup & Symbol Verification (Run by the Agent)

In response to the `/skidl` prompt, **the agent creates** an isolated `.venv` with `uv` (using Python 3.14 so prebuilt `h5py` wheels install without compiling from source) and installs `skidl`:

```bash
uv venv --clear --python 3.14 .venv
uv pip install skidl
```

Before writing `envelope_follower.py`, **the agent inspects** the local KiCad 10 `.kicad_sym` and `.kicad_mod` definitions—for example via `show("Amplifier_Operational", "TL074")`, `show("Diode", "BAT54S")`, `show("Connector_Audio", "AudioJack2_SwitchT")`, and `show("Connector", "TestPoint")`—to confirm exact pin numbers and pad polarities.

Because `EnvelopeFollowerBOM.md` ([Stage 3](stage-3-bom-and-dfm.md)) already locked down the LCSC part numbers, the agent reads them directly from the BOM. If any part needs a live stock or Basic vs. Extended pricing re-check, the agent (or you) can run `jlcpcb_search.py`:

```bash
.venv/bin/python .agents/skills/skidl/scripts/jlcpcb_search.py \
    --in-stock-only "TL074HIDR" "BAT54SLT1G" "B5819W" "1N4148W" "47pF 0603" "220nF 0805" "10R 1206" "1k 1206"
```

## Step 4.2: Anatomy of the Generated `envelope_follower.py`

**The agent generates `envelope_follower.py`** using four SKiDL patterns from the `skidl` skill that make the improved 54-part (+8 `DNP` test points), 36-net circuit modular and fabrication-ready:

1. **Pre-Import Environment Setup**:
    Before importing `skidl`, set `XDG_DATA_HOME`, `MPLCONFIGDIR`, `KICAD10_SYMBOL_DIR`, `KICAD_SYMBOL_DIR`, and `KICAD10_FOOTPRINT_DIR` so SKiDL resolves KiCad 10's `.kicad_sym` libraries cleanly on macOS.

2. **Deterministic `make_part()` Helpers, `part.fields` Metadata & `DNP` Test Points**:
    Instead of relying on `dest=TEMPLATE` auto-numbering—which would shift resistor references because the Stage 7 LED fix intentionally removed `R20`, `R22`, and `R23`—instantiate every component deterministically with explicit `ref=ref` and `tag=ref.lower()` via `make_part()` and `make_resistors()`. Write catalog and silkscreen metadata directly into `part.fields["LCSC"]`, `part.fields["MPN"]`, `part.fields["JLCPCB_Class"]`, and `part.fields["Silkscreen"]` (rather than plain Python attributes, which SKiDL's netlist and XML exporters ignore):

    ```python
    def make_part(
        lib: str,
        symbol: str,
        ref: str,
        value: str,
        footprint: str,
        fields: dict[str, str] | None = None,
        *,
        dnp: bool = False,
    ) -> Part:
        """Instantiate a SKiDL Part with deterministic tag, footprint, and BOM fields."""
        part = Part(
            lib,
            symbol,
            ref=ref,
            value=value,
            footprint=footprint,
            tag=ref.lower(),
        )
        if fields:
            for key, field_val in fields.items():
                part.fields[key] = field_val
        if dnp:
            part.dnp = True
        return part


    def make_resistors(
        specs: list[tuple[str, str, str, str, str, str]],
    ) -> dict[str, Part]:
        """Instantiate fixed SMD resistors from (ref, value, fp, lcsc, mpn, silk) rows."""
        resistors: dict[str, Part] = {}
        for ref, value, footprint, lcsc, mpn, silkscreen in specs:
            resistors[ref] = make_part(
                "Device",
                "R",
                ref=ref,
                value=value,
                footprint=footprint,
                fields={
                    "LCSC": lcsc,
                    "MPN": mpn,
                    "Manufacturer": "UNI-ROYAL",
                    "JLCPCB_Class": "Basic",
                    "Silkscreen": silkscreen,
                },
            )
        return resistors
    ```

    - **Panel THT Controls** (`RV1`–`RV4`, `J1`–`J3`, `D4`, `J_PWR`) are tagged `JLCPCB_Class = "Manual THT"` so `generate_jlcpcb_bom()` excludes them from the SMT pick-and-place CSV, while `part.fields["Silkscreen"]` preserves labels such as `"RV1 GAIN A100k"` and `"J_PWR +/-12V"` for PCB layout.
    - **Optional Test Points (`TP1`–`TP8`)** instantiate `Part("Connector", "TestPoint", ref=ref, value=val, footprint="TestPoint:TestPoint_Keystone_5000-5004_Miniature", tag=ref.lower())` with `LCSC = "C5199801"`, `MPN = "RH-5001"`, `JLCPCB_Class = "Manual THT (DNP)"`, `Silkscreen = f"{ref} {val}"`, and `part.dnp = True` so both the JLCPCB BOM and the `.pos` centroid file leave those `1.0 mm` holes unpopulated.

3. **Stage-by-Stage Net Wiring in `build_envelope_follower()` (All 8 `TL074H` Channels Active)**:
    Protected power rails (`v_p12`, `v_n12`, `gnd`) are marked `drive = POWER`, and all 36 named nets wire pins directly via SKiDL's pin attachment operator (`+=`), connecting unused normalled jack switches (`j1["TN"]`, `j2["TN"]`, `j3["TN"]`) to `builtins.NC`. Notice how `U2C` and `U2D` now form the Stage 4 active peak detector and JFET buffer:

    ```python
    # Stage 3: Precision Full-Wave Rectifier (U1B & U1C)
    rect1_inv += r["R3"][2], u1[6], d1["K"], r["R4"][1]
    rect1_out += u1[7], d1["A"], d2["K"]
    half_rect += d2["A"], r["R4"][2], r["R5"][1], tp5[1]
    ff_mid += r["R6"][2], r["R7"][1]
    rect2_inv += r["R7"][2], r["R5"][2], u1[9], r["R8"][1]
    full_rect += u1[8], r["R8"][2], u2[10], tp6[1]

    # Stage 4: Active Zero-Deadzone Peak Envelope Detector & Buffer (U2C & U2D)
    pk_fb_inv += u2[9], r["R24"][2], d7["A"], c11[1]
    pk_drv_out += u2[8], d3["A"], d7["K"], c11[2]
    atk_in += d3["K"], r["R9"][1]
    atk_mid += r["R9"][2], rv2[1]
    env_cap += rv2[2, 3], c2[1], r["R10"][1], u2[12]
    rel_mid += r["R10"][2], rv3[1]
    env_sig += u2[14], u2[13], r["R24"][1], u1[12], u2[5], tp7[1]
    ```

    Similarly, Stage 5 (`U1D`) and Stage 6 (`U2A`) wire each `BAT54S` dual Schottky rail clamp (`D8` on `AMP_OUT`, `D9` on `INV_AMP_OUT`) with pin `1` (`A`) to `-12V`, pin `2` (`K`) to `+12V`, and pin `3` (`COM`) to the op-amp output ahead of `1/4 W` `1206` resistors `R16`/`R19`, while Stage 7 (`U2B`) places `D4` (`3 mm` LED) between pin `7` (`LED_A`) and pin `6` (`LED_K`) with `R21` (`1.5k`) to `GND`.

4. **Programmatic `erc_assert()` & Exports**:
    Custom net-level pin-count and part-count assertions catch missing or stray connections before `ERC()`, `generate_netlist()`, `generate_xml()`, and `generate_jlcpcb_bom()` (skipping `Manual THT` and `dnp=True`) run:

    ```python
    erc_assert("len(v_p12) == 10", "+12V rail expected 10 connected pins")
    erc_assert("len(v_n12) == 10", "-12V rail expected 10 connected pins")
    erc_assert("len(gnd) == 27", "GND rail expected 27 connected pins")
    erc_assert("len(out_tip) == 2", "OUT_TIP net should connect R16 and J2 tip")
    erc_assert("len(inv_out_tip) == 2", "INV_OUT_TIP net should connect R19 and J3 tip")
    erc_assert(
        "len(builtins.default_circuit.parts) == 62",
        "Expected 62 total components (45 SMD + 9 THT + 8 DNP TPs)",
    )
    ```

    Verifying exact net counts (such as `len(gnd) == 27`) immediately catches off-by-one wiring or ground-pin omissions before a netlist ever reaches PCB layout.

!!! warning "KiCad 10 Polarized Pin Numbers vs. Pin Names"
    Always inspect `.kicad_sym` and `.kicad_mod` definitions before wiring polarized parts by pin number:

    - **`Device:C_Polarized` (`CP_Elec_6.3x5.4`)**: Pin `1` is `+` and Pin `2` is `-`. On the `-12V` rail, **`c4[1]` connects to `GND`** (`0 V`) and **`c4[2]` connects to `-12V`** (`-11.78 V`).
    - **`Diode:1N4148W`, `Device:D_Schottky`, and `Device:LED`**: Pin `1` is **`K` (cathode)** and Pin `2` is **`A` (anode)**—the opposite of intuitive "1 = anode" assumptions. Always wire diodes and LEDs by pin name (`d["A"]`, `d["K"]`) rather than raw pin integers.

## Step 4.3: Automated Execution, Linting & Outputs (Run by the Agent)

After writing `envelope_follower.py`, **the agent automatically runs the script** inside `.venv` to execute `ERC()` and generate the netlist and BOM files, then lints and formats the Python files with `ruff` (you can re-run these same commands manually any time you tweak `envelope_follower.py`):

```bash
.venv/bin/python envelope_follower.py
ruff check --fix envelope_follower.py envelope_follower_sklib.py
ruff format envelope_follower.py envelope_follower_sklib.py
```

Key generated files:

- `envelope_follower.erc`: `ERC INFO: No errors or warnings found while running ERC.`
- `envelope_follower.net`: KiCad netlist containing all **54 populated physical components + 8 `DNP` test points (62 footprints total)** and **36 nets**.
- `envelope_follower_bom.xml`: Full XML BOM with embedded `LCSC`, `MPN`, `JLCPCB_Class`, `DNP`, and `Notes` fields.
- `jlcpcb_bom.csv`: Grouped 4-column JLCPCB SMT BOM (`Comment,Designator,Footprint,LCSC Part #`) with **18 SMT line items** (**45 SMD components total**: `15` JLCPCB Basic lines + `3` Extended lines; the `9` required THT parts and `8` `DNP` test points are excluded automatically).

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
