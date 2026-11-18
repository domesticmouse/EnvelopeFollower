# Envelope Follower

A Eurorack analog envelope follower module designed for KiCad, defined in SKiDL with a generated KiCad netlist, JLCPCB PCBA BOM, complete netlist specification, and build checklist.

The original schematic is based on Hagiwo's [$4 Envelope Follower module - DIY Eurorack Modular Synthesizer](https://note.com/solder_state/n/n110e9ba066b3).

![Hagiwo's Envelope Follower Schematic](EnvelopeFollower.webp)

---

## ⚡ Improved Circuit Overview

This repository adapts Hagiwo's original circuit for modern **Texas Instruments TL074H** quad op-amps, introducing enhancements for stability, low-noise performance, and hardware protection:

1. **Dual TL074H Quad Op-Amp Configuration (6 Active Channels)**:
   - **U1 (TL074H)**: $U1A$ Input Gain Stage, $U1B$ Half-Wave Precision Rectifier, $U1C$ Summing Precision Rectifier, $U1D$ Output Amplifier & Offset Stage.
   - **U2 (TL074H)**: $U2A$ Inverting Output Buffer, $U2B$ LED Driver Buffer.
   - **Unused Op-Amp Termination ($U2C$, $U2D$)**: Unused channels are configured as unity-gain followers with non-inverting inputs ($+$) grounded to prevent floating inputs, parasitic oscillation, and excessive power draw.

2. **Gain Control Minimum Series Resistor**:
   - Added $R_{\text{GAIN\_MIN}} = 1\text{ k}\Omega$ in series with the $100\text{ k}\Omega$ gain potentiometer (`RV_GAIN`). This prevents setting closed-loop feedback resistance to $0\,\Omega$ at minimum pot travel, avoiding pot wiper contact noise and op-amp loading.

3. **High-Frequency Supply Decoupling**:
   - Four $100\text{ nF}$ ceramic bypass capacitors ($C_5$–$C_8$) placed directly at the $V_{CC+}$ (Pin 4) and $V_{CC-}$ (Pin 11) pins of each TL074H IC to suppress high-frequency noise and oscillation.

4. **Power & Output Protection**:
   - **Reverse Polarity Protection**: Schottky diodes ($D_4, D_5$ / 1N5817) on $+12\text{V}$ and $-12\text{V}$ supply lines.
   - **Short Circuit Protection**: $1\text{ k}\Omega$ output resistors ($R_{16}, R_{19}$) on `J_OUT` and `J_INV_OUT` jacks to protect against patch cable shorts.

5. **Precision Rectification**:
   - Recommended 1% metal film resistors ($10\text{ k}\Omega, 22\text{ k}\Omega$) in the full-wave rectifier stage for balanced positive and negative peak response.

---

## 🔄 Signal Flow & Functional Blocks

The circuit is partitioned into six functional blocks (matching [`ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md`](ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md)):

1. **Power Entry, Protection & Decoupling (`J_PWR`, `D4`–`D5`, `C3`–`C8`)**:
   Eurorack $\pm 12\text{V}$ 10-pin power entry through 1N5817 Schottky reverse-polarity diodes (`D4`, `D5`), $4.7\,\mu\text{F}$ bulk electrolytics (`C3`, `C4`), and local $100\text{ nF}$ ceramic IC bypass capacitors (`C5`–`C8`).
2. **Input Coupling & Gain Stage (`U1A`)**:
   AC-coupled input (`J_IN`, `C1` $4.7\,\mu\text{F}$, `R1` $1\text{ M}\Omega$ pulldown) driving an inverting op-amp stage (`R2` $10\text{ k}\Omega$, `RV_GAIN` $100\text{ k}\Omega$, `R_GAIN_MIN` $1\text{ k}\Omega$).
3. **Precision Full-Wave Rectifier (`U1B`, `U1C`)**:
   `U1B` with 1N4148 diodes (`D1`, `D2`) and $10\text{ k}\Omega$ resistors (`R3`, `R4`) forms an active half-wave rectifier, which `U1C` sums (`R7` $10\text{ k}\Omega$) against the direct signal (`R5` + `R6`, $20\text{ k}\Omega$ total) with a $22\text{ k}\Omega$ feedback resistor (`R8`).
4. **Peak Detector & Envelope Timing**:
   1N4148 diode `D3` charges the $1\,\mu\text{F}$ smoothing capacitor `C2` through `RV_ATK` ($50\text{ k}\Omega$ attack control) and discharges through `R9` ($1\text{ k}\Omega$), `R10` ($10\text{ k}\Omega$), and `RV_REL` ($1\text{ M}\Omega$ release control).
5. **Output Amplifier & DC Offset Stage (`U1D`)**:
   Follows the envelope voltage on Pin 12 ($+$) while summing an adjustable $\pm 12\text{V}$ DC bias (`R11`, `R12`, `RV_OFFSET`, `R13`, `R14`, `R15`) at Pin 13 ($-$) and driving `J_OUT` through `R16` ($1\text{ k}\Omega$).
6. **Inverted Output, LED Driver & Termination (`U2A`–`U2D`)**:
   - `U2A`: Unity-gain inverting stage (`R17` = `R18` = $10\text{ k}\Omega$) driving `J_INV_OUT` through `R19` ($1\text{ k}\Omega$).
   - `U2B`: Unity-gain LED buffer (`R20` $10\text{ k}\Omega$ input isolation, `R21` $22\text{ k}\Omega$ current limit) driving `LED1` against a cathode bias divider (`R22` $10\text{ k}\Omega$ to `GND`, `R23` $33\text{ k}\Omega$ to $-12\text{V}$).
   - `U2C`, `U2D`: Terminated as unity-gain followers with non-inverting inputs tied to `GND`.

---

## 🎛️ Controls & I/O Summary

| Reference | Component / Value | Taper / Type | Function |
| :--- | :--- | :--- | :--- |
| **`RV_GAIN`** | $100\text{ k}\Omega$ Potentiometer | Linear / Log | Input Gain Control |
| **`RV_ATK`** | $50\text{ k}\Omega$ Potentiometer | Linear | Attack Time Control |
| **`RV_REL`** | $1\text{ M}\Omega$ Potentiometer | Audio / Log | Release Time Control |
| **`RV_OFFSET`** | $100\text{ k}\Omega$ Potentiometer | Linear | Output DC Offset Adjust |
| **`J_IN`** | 3.5mm Mono Jack | Switched | Audio / CV Input |
| **`J_OUT`** | 3.5mm Mono Jack | Switched | Non-Inverted Envelope CV Output |
| **`J_INV_OUT`** | 3.5mm Mono Jack | Switched | Inverted Envelope CV Output |
| **`LED1`** | 3mm / 5mm LED | Red / Blue / Green | Envelope Signal Level Indicator |
| **`J_PWR`** | 2x5 Shrouded Header | 10-Pin Eurorack | $\pm 12\text{V}$ & `GND` Power Input |

---

## 📄 Documentation, Tutorial & Netlist

For the complete end-to-end build tutorial and technical reference, see:

* [**`TUTORIAL.md`**](TUTORIAL.md) – **Step-by-Step Build Tutorial**: From Hagiwo's circuit sketch and installing hardware agent skills (`skidl`, `kicad`, `eurorack-panel`) through SKiDL capture, KiCad schematic/6 HP PCB generation, interactive routing, and 3U front panel construction.
* [**`ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md`**](ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md) – Full Bill of Materials, 35-Net Connection List, and 8-Step KiCad Build Checklist.
* [**`TODO.md`**](TODO.md) – KiCad PCB routing, panel, and JLCPCB fabrication progress checklist.

---

## 🐍 SKiDL Circuit & Generated Artifacts

The circuit is implemented in Python with [SKiDL](https://devbisme.github.io/skidl/) in [**`envelope_follower.py`**](envelope_follower.py) using dual **Texas Instruments TL074H** (`TL074HIDR`, `SOIC-14`) quad op-amps across 6 `@subcircuit` blocks, 48 physical components, and 35 nets:

* [**`envelope_follower.py`**](envelope_follower.py) – Complete SKiDL circuit definition (`ERC()` passes with 0 errors and 0 warnings).
* [**`EnvelopeFollower.kicad_sch`**](EnvelopeFollower.kicad_sch) – Generated KiCad schematic (`generate_schematic()`).
* [**`generate_kicad_pcb.py`**](generate_kicad_pcb.py) & [**`EnvelopeFollower.kicad_pcb`**](EnvelopeFollower.kicad_pcb) – Automated 6 HP (`29.60 × 107.00 mm`) main PCB layout with pre-placed `F.Cu` panel controls and `B.Cu` SMT parts/power entry.
* [**`panel/EnvelopeFollower_Panel.kicad_pcb`**](panel/EnvelopeFollower_Panel.kicad_pcb) – Mated 6 HP × 3U (`30.00 × 128.50 mm`) Eurorack front panel PCB (`0` DRC violations) with Gerber export in [`production/panel/`](production/panel/) and [`production/EnvelopeFollower_Panel.zip`](production/EnvelopeFollower_Panel.zip).
* [**`envelope_follower.net`**](envelope_follower.net) – Generated KiCad netlist ready to import in `pcbnew` (`File -> Import -> Netlist...`).
* [**`envelope_follower_bom.xml`**](envelope_follower_bom.xml) – KiCad XML BOM with embedded `LCSC`, `MPN`, and `JLCPCB_Class` fields.
* [**`jlcpcb_bom.csv`**](jlcpcb_bom.csv) – Grouped 4-column JLCPCB SMT PCBA BOM (`Comment,Designator,Footprint,LCSC Part #`, 12 SMT line items; panel-mounted THT controls and jacks are marked `Manual THT`).
* [**`envelope_follower_sklib.py`**](envelope_follower_sklib.py) & [**`envelope_follower.erc`**](envelope_follower.erc) – Generated backup SKiDL symbol library and Electrical Rules Check report.

To regenerate the netlist, BOMs, schematic, and initial 6 HP PCB locally using `uv`:

```bash
uv venv --clear --python 3.14 .venv
uv pip install skidl kinet2pcb
.venv/bin/python envelope_follower.py
.venv/bin/python generate_kicad_pcb.py
```

---

## 📁 Repository Structure

```text
EnvelopeFollower/
├── LICENSE                                # Apache License 2.0
├── README.md                              # Project overview & documentation
├── TUTORIAL.md                            # End-to-end tutorial (sketch -> SKiDL -> KiCad -> 3U panel)
├── TODO.md                                # KiCad PCB routing & fabrication checklist
├── ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md  # Complete BOM, netlist, and KiCad capture checklist
├── EnvelopeFollower.webp                  # Original Hagiwo hand-drawn reference schematic
├── envelope_follower.py                   # SKiDL circuit definition (dual TL074H, 6 subcircuits)
├── envelope_follower_sklib.py             # Backup SKiDL symbol library
├── envelope_follower.net                  # Generated KiCad netlist
├── envelope_follower_bom.xml              # KiCad XML BOM with LCSC/MPN metadata
├── jlcpcb_bom.csv                         # Grouped JLCPCB SMT PCBA BOM
├── envelope_follower.erc                  # SKiDL ERC report
├── envelope_follower.log                  # SKiDL generation log
├── EnvelopeFollower.kicad_sch             # Generated KiCad 10 schematic
├── generate_kicad_pcb.py                  # Automated 6 HP KiCad PCB placement script
├── EnvelopeFollower.kicad_pcb             # 6 HP main circuit PCB (pre-placed, ready to route)
├── panel/
│   └── EnvelopeFollower_Panel.kicad_pcb   # Mated 6 HP x 3U Eurorack front panel PCB
├── production/
│   ├── EnvelopeFollower_Panel.zip         # Packaged front panel Gerbers & Excellon drills
│   └── panel/                             # Individual front panel Gerber & drill files
├── docs/
│   └── images/                            # Schematic SVG and 3D PCB/panel renders for TUTORIAL.md
├── skills-lock.json                       # Agent skill lockfile
└── .agents/skills/                        # Installed hardware skills (kicad, skidl, eurorack-panel)
```

---

## 📜 License & Disclaimer

Licensed under the [Apache License 2.0](LICENSE).

This is not an officially supported Google product.
