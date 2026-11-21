# Stage 4: Translating the Improved Circuit to SKiDL (`envelope_follower.py`)

Defining the circuit in **SKiDL** turns the netlist into testable, version-controlled Python code that enforces `ERC()` assertions and outputs both a KiCad netlist and a JLCPCB-ready BOM in one execution—while keeping optional `DNP` test points, optical fiducials, and manual THT hardware cleanly separated from the SMT PCBA BOM.

## AI Agent Prompt

Because [Stage 3](stage-3-bom-and-dfm.md) already froze every net, component reference, LCSC code, `DNP` attribute, and silkscreen schedule inside `EnvelopeFollowerImproved.md`, `EnvelopeFollowerBOM.md`, and `SilkscreenInstructions.md`, you only need a single prompt to drive the `/skidl` skill:

> *"`/skidl` Please turn `@EnvelopeFollowerImproved.md`, `@EnvelopeFollowerBOM.md`, and `@SilkscreenInstructions.md` into a SKiDL circuit in `envelope_follower.py`, run ERC (`envelope_follower.erc`), and export `envelope_follower.net`, `envelope_follower_bom.xml`, and `jlcpcb_bom.csv`."*

!!! note "One Prompt Runs the Entire Stage"
    **You do not need to run the commands below manually.** Sending this single prompt causes the AI agent (guided by `.agents/skills/skidl/SKILL.md`) to execute Steps 4.1–4.3 automatically behind the scenes:

    - Creating the isolated Python 3.14 `.venv` and installing `skidl`.
    - Inspecting KiCad 10 symbol pins and footprint pad polarities (and optionally querying `jlcpcb_search.py` if any LCSC codes need live verification).
    - Writing `envelope_follower.py` with all `71` footprints (`60` populated physical parts = `49` SMD + `11` THT, plus `8` `DNP` `TP1`–`TP8` test points and `3` `DNP` optical fiducials `FID1`–`FID3`) across `42` active nets.
    - Running `.venv/bin/python envelope_follower.py`, verifying `ERC()` passes with `0` errors and `0` warnings, exporting `envelope_follower.net`, `envelope_follower_bom.xml`, and `jlcpcb_bom.csv`, and formatting the code with `ruff`.

    Steps 4.1–4.3 below show what the agent executes under the hood—and give you the exact commands to re-run manually if you ever edit `envelope_follower.py` by hand.

## Step 4.1: Environment Setup & Symbol Verification (Run by the Agent)

In response to the `/skidl` prompt, **the agent creates** an isolated `.venv` with `uv` (using Python 3.14 so prebuilt `h5py` wheels install without compiling from source) and installs `skidl`:

```bash
uv venv --clear --python 3.14 .venv
uv pip install skidl
```

Before writing `envelope_follower.py`, **the agent inspects** the local KiCad 10 `.kicad_sym` and `.kicad_mod` definitions—for example via `show("Amplifier_Operational", "TL074")`, `show("Diode", "BAT54S")`, `show("Diode", "BAV99")`, `show("Connector_Audio", "AudioJack2_SwitchT")`, and `show("Connector", "TestPoint")`—to confirm exact pin numbers and pad polarities.

Because `EnvelopeFollowerBOM.md` ([Stage 3](stage-3-bom-and-dfm.md)) already locked down the LCSC part numbers, the agent reads them directly from the BOM. If any part needs a live stock or Basic vs. Extended pricing re-check, the agent (or you) can run `jlcpcb_search.py`:

```bash
.venv/bin/python .agents/skills/skidl/scripts/jlcpcb_search.py \
    --in-stock-only "TL074HIDR" "BAT54S" "BAV99" "B5819W" "1N4148WS" "RT0603BRD0710KL" "RTT124700FTP" "22uF 50V"
```

## Step 4.2: Anatomy of the Generated `envelope_follower.py`

**The agent generates `envelope_follower.py`** using four SKiDL patterns from the `skidl` skill that make the improved 60-populated (+8 `DNP` test points + 3 fiducials), 42-net circuit modular and fabrication-ready:

1. **Working-Directory Lock & Pre-Import Environment Setup**:
   Call `os.chdir(Path(__file__).resolve().parent)` *before* importing `skidl` so SKiDL writes `skidl_REPL.*` logs locally instead of polluting parent folders, and set `XDG_DATA_HOME`, `MPLCONFIGDIR`, `KICAD*_SYMBOL_DIR`, and `KICAD10_FOOTPRINT_DIR` so SKiDL resolves KiCad 10's `.kicad_sym` libraries cleanly on macOS.

2. **Templates, `_apply_fields()` Metadata, `DNP` Test Points & Optical Fiducials**:
   Instantiate reusable `dest=TEMPLATE` parts for `0603`/`1206`/`1210` resistors, `0603` capacitors, `Alps RK09K` pots, `WQP-PJ398SM` jacks, `TestPoint_THTPad_D2.0mm_Drill1.0mm` test points, and `Mechanical:Fiducial` (`Fiducial:Fiducial_1mm_Mask2mm`), setting `fid_t.lib.filename = "Mechanical"` when present. Write catalog and silkscreen metadata directly into `part.fields` via `_apply_fields()` (rather than plain Python attributes, which SKiDL's netlist and XML exporters ignore):

    ```python
    def _apply_fields(
        part,
        *,
        lcsc: str = "",
        mpn: str = "",
        manufacturer: str = "",
        jlc_class: str = "",
        silkscreen: str = "",
        notes: str = "",
    ) -> None:
        """Populate BOM, catalog, silkscreen, and assembly metadata into part.fields."""
        metadata = {
            "LCSC": lcsc,
            "MPN": mpn,
            "Manufacturer": manufacturer,
            "JLCPCB_Class": jlc_class,
            "Silkscreen": silkscreen,
            "Notes": notes,
        }
        for key, val in metadata.items():
            if val:
                part.fields[key] = val


    def make_r_10k_01(ref: str):
        return make_r(
            r0603_t,
            ref,
            "10k 0.1%",
            lcsc="C95204",
            mpn="RT0603BRD0710KL",
            manufacturer="YAGEO",
            jlc_class="Extended",
            silkscreen="10k",
            notes="0.1% 25ppm matched rectifier network at U1B/U1C",
        )
    ```

    - **Populated THT Hardware** (`RV1`–`RV4`, `J1`–`J3`, `D4`, `J4`, `C1`, `C2`) is tagged `JLCPCB_Class = "Manual THT"` or `"Consigned THT"` so `generate_jlcpcb_bom()` excludes them from the SMT pick-and-place CSV while `part.fields["Silkscreen"]` preserves labels like `"RV1 GAIN A100k"` and `"J4 PWR"`.
    - **Optional Test Points (`TP1`–`TP8`) & SMT Fiducials (`FID1`–`FID3`)**: Both instantiate with `tp.dnp = True` and `tp.exclude_from_bom = True` (`TP1`–`TP8` carry `LCSC="C5199801"`, `MPN="RH-5001"`, `Silkscreen=tp_silk`) so neither `jlcpcb_bom.csv` nor the assembly build tries to populate them (`exclude_from_pos_files` is likewise enforced during [Stage 5](stage-5-schematic-and-pcb.md) PCB generation).

3. **Stage-by-Stage Net Wiring in `build_circuit()` (All 8 `TL074H` Channels Active)**:
   Power nets (`+12V_IN`, `-12V_IN`, `+12V_PROT`, `-12V_PROT`, `+12V`, `-12V`, `GND`) carry `drive = POWER` and `NetClass("Power", priority=1, trace_width=0.5, clearance=0.2)`. Unused output jack normalled switches (`j2["TN"]`, `j3["TN"]`) connect to `builtins.NC`, while `j1["TN"]` wires to `gnd`. Notice how `U2D` forms the `101 kΩ` input buffer (`Stage 1A`), `U2C` forms the active peak detector (`Stage 4`), and `D_IN`/`D_OUT`/`D_INV_OUT` (`BAV99`) wire by physical pin number `[1, 2, 3]`:

    ```python
    # Stages 2 & 3 — 0.1%-Matched Unity-Gain Precision Rectifier (U1B, U1C, D1_D2)
    gnd += u1[5], u1[10]
    u1b_inv += r3[2], u1[6], r6[1], d1_d2[2]
    u1b_out += u1[7], d1_d2[3]
    rect_hw += d1_d2[1], r6[2], r7[1]
    ff_mid += r4[2], r5[1]
    u1c_inv += r5[2], r7[2], u1[9], r8a[1]
    rect_fb_mid += r8a[2], r8b[1]
    rect_out += u1[8], r8b[2], u2[10]

    # Stage 4 — Active Zero-Deadzone Peak Detector & Attack/Release (U2C)
    u2c_out += u2[8], d3[2]  # A
    atk_in += d3[1], u2[9], r_atk_min[1]  # K
    atk_pot_1 += r_atk_min[2], rv2[1]
    env_node += rv2[2], rv2[3], c2[1], r10[1], r_env_prot[1], r20[1]
    rel_pot_top += r10[2], rv3[1]
    gnd += c2[2], rv3[2], rv3[3]

    # Stage 5 — Linearized OFFSET, In-Loop Feedback & Protected Outputs (U1D, U2A)
    u1d_in += r_env_prot[2], u1[12]
    off_top += r11[2], rv4[1]
    off_bot += r12[2], rv4[3]
    off_wiper += rv4[2], r13[1]
    u1d_inv += r13[2], r15[1], c_out1[1], u1[13]
    u1d_out += u1[14], c_out1[2], r16a[1]
    out_clamp += r16a[2], r15[2], d_out[3], r16b[1], r17[1]
    out_tip += r16b[2], j2["T"]
    gnd += j2["S"], u2[3], j3["S"]
    j2["TN"] += builtins.NC

    u2a_inv += r17[2], r18[1], c_out2[1], u2[2]
    u2a_out += u2[1], c_out2[2], r19a[1]
    inv_out_clamp += r19a[2], r18[2], d_inv_out[3], r19b[1]
    inv_out_tip += r19b[2], j3["T"]
    j3["TN"] += builtins.NC
    ```

4. **Programmatic `erc_assert()` & BOM Filtering**:
   Ten exact part-count and net pin-count assertions catch missing or stray connections before `ERC()`, `generate_netlist()`, `generate_xml()`, and `generate_jlcpcb_bom()` run:

    ```python
    erc_assert(
        "len(builtins.default_circuit.parts) == 71",
        "Expected 71 total footprints (68 BOM/DNP + 3 fiducials)",
    )
    erc_assert(
        "len(builtins.default_circuit.get_nets()) == 42",
        "Expected 42 active signal/power nets",
    )
    erc_assert("len(v12p) == 11", "Expected 11 nodes on +12V rail")
    erc_assert("len(v12n) == 11", "Expected 11 nodes on -12V rail")
    erc_assert("len(gnd) == 26", "Expected 26 nodes on GND net")
    erc_assert("len(preamp_out) == 8", "Expected 8 nodes on PREAMP_OUT")
    erc_assert("len(rect_out) == 4", "Expected 4 nodes on RECT_OUT")
    erc_assert("len(env_node) == 6", "Expected 6 nodes on ENV_NODE")
    erc_assert("len(out_clamp) == 6", "Expected 6 nodes on OUT_CLAMP")
    erc_assert("len(inv_out_clamp) == 5", "Expected 5 nodes on INV_OUT_CLAMP")
    ```

!!! warning "KiCad 10 Polarized & Dual-Diode Pin Conventions"
    Always inspect `.kicad_sym` and `.kicad_mod` definitions before wiring polarized parts by pin number:

    - **`Device:C_Polarized` (`CP_Elec_6.3x5.4`)**: Pin `1` is `+` and Pin `2` is `-`. On the `-12V` rail, **`c4[1]` connects to `GND`** (`0 V`) and **`c4[2]` connects to `-12V`** (`-11.55 V`).
    - **`Device:D_Schottky`, `Diode:1N4148WS`, and `Device:LED`**: Pin `1` is **`K` (cathode)** and Pin `2` is **`A` (anode)**—the opposite of intuitive "1 = anode" assumptions. Verify `d_pwr_n[1]` (`K`) goes to `-12V_IN`, `d_pwr_n[2]` (`A`) goes to `-12V_PROT`, and `d_led_clamp` sits anti-parallel (`[1]` to `U2B_OUT`, `[2]` to `LED_K`) across `D4`.
    - **`Diode:BAV99` (`SOT-23`)**: Physical `SOT-23` pins are `1 = A1` (`-12V`), `2 = K2` (`+12V`), and `3 = COM` (`IN_AC` / `OUT_CLAMP` / `INV_OUT_CLAMP`). Always index `BAV99` by physical pin integers `[1, 2, 3]` because KiCad's legacy hidden pin names read `K`/`A`/`K`.

## Step 4.3: Automated Execution, Linting & Outputs (Run by the Agent)

After writing `envelope_follower.py`, **the agent automatically runs the script** inside `.venv` to execute `ERC()` and generate the netlist and BOM files, then lints and formats the Python files with `ruff` (you can re-run these same commands manually any time you tweak `envelope_follower.py`):

```bash
.venv/bin/python envelope_follower.py
ruff check --fix envelope_follower.py envelope_follower_sklib.py
ruff format envelope_follower.py envelope_follower_sklib.py
```

Console summary:

```text
Summary: 71 total footprints, 42 active nets, jlcpcb_bom.csv -> 19 lines (49 SMT parts)
```

Key generated files:

- `envelope_follower.erc`: `ERC INFO: No errors or warnings found while running ERC.`
- `envelope_follower.net`: KiCad netlist containing all **60 populated physical components + 8 `DNP` test points + 3 `DNP` fiducials (`71` footprints total)** and **42 active nets** (zero `NO_LIB` entries).
- `envelope_follower_bom.xml`: Full XML BOM with embedded `LCSC`, `MPN`, `JLCPCB_Class`, `Silkscreen`, `DNP`, and `Notes` fields.
- `jlcpcb_bom.csv`: Grouped 4-column JLCPCB SMT BOM (`Comment,Designator,Footprint,LCSC Part #`) with **19 SMT line items** (**49 SMD components total**: `14` JLCPCB Basic lines / `33` parts + `5` Extended lines / `16` parts; the `11` populated THT parts, `8` `DNP` test points, and `3` `DNP` fiducials are excluded automatically).

??? info "Preview of generated `jlcpcb_bom.csv` (19 SMT line items, 49 SMD components)"

    ```csv
    Comment,Designator,Footprint,LCSC Part #
    TL074H,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
    B5819W,"D_PWR_P, D_PWR_N",D_SOD-123,C8598
    BAT54S,D1_D2,SOT-23,C47546
    1N4148WS,"D3, D_LED_CLAMP",D_SOD-323,C2128
    BAV99,"D_IN, D_OUT, D_INV_OUT",SOT-23,C2500
    10R,"R_PWR_P, R_PWR_N",R_1206_3216Metric,C17903
    470R,R_ATK_MIN,R_0603_1608Metric,C23179
    470R 0.5W,"R16A, R16B, R19A, R19B",R_1210_3225Metric,C333193
    1k,"R_IN_PROT, R_IN_BUF, R_GAIN_MIN, R11, R12",R_0603_1608Metric,C21190
    2.2k,R_LED,R_0603_1608Metric,C4190
    10k,"R2, R10, R_ENV_PROT, R15, R17, R18, R20",R_0603_1608Metric,C25804
    10k 0.1%,"R3, R4, R5, R6, R7, R8A, R8B",R_0603_1608Metric,C95204
    18k,R13,R_0603_1608Metric,C25810
    100k,R1,R_0603_1608Metric,C25803
    1M,R_GAIN_FAIL,R_0603_1608Metric,C22935
    100nF,"C_DEC1, C_DEC2, C_DEC3, C_DEC4",C_0603_1608Metric,C14663
    47pF C0G,C_HF,C_0603_1608Metric,C1671
    100pF C0G,"C_OUT1, C_OUT2",C_0603_1608Metric,C14858
    22uF 50V,"C3, C4",CP_Elec_6.3x5.4,C2836438
    ```
