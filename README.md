# Envelope Follower

An end-to-end hardware design tutorial (MkDocs Material site and clean-room stage snapshots) for turning Hagiwo's analog envelope follower sketch into a 6 HP Eurorack KiCad 10 PCB and 3U front panel using AI hardware skills and SKiDL.

![Eurorack Envelope Follower 6 HP PCBA 3D Render](docs/images/pcb_back_landscape.png)

The original schematic is based on Hagiwo's [$4 Envelope Follower module - DIY Eurorack Modular Synthesizer](https://note.com/solder_state/n/n110e9ba066b3?hl=en):

![Hagiwo's Envelope Follower Schematic](EnvelopeFollower.webp)

---

## ⚡ Improved Circuit Overview

The tutorial adapts Hagiwo's original circuit for modern **Texas Instruments TL074H** (`TL074HIDR`, `SOIC-14`) quad op-amps, introducing enhancements for buffered high-Z input, zero-deadzone envelope tracking, precision rectification, linear offset summing, and Eurorack hardware protection:

1. **Dual `TL074HIDR` Configuration (All 8 Channels Active)**:
   - **U1 (`TL074H`)**: `U1A` Protected Inverting Preamp (`-0.10×` to `-9.17×`), `U1B` Precision Half-Wave Rectifier (`BAT54S`), `U1C` `0.1%`-Matched $1.000\times$ Summing Rectifier (`R8A+R8B = 20 kΩ`), `U1D` Output Buffer & Linearized `OFFSET` Summer (`1.476×–1.529×`, `±5.09 V`).
   - **U2 (`TL074H`)**: `U2A` Unity-Gain Inverting Output (`INV_OUT`), `U2B` Active In-Loop Precision LED Current Sink (`R_LED = 2.2 kΩ` + `D_LED_CLAMP`), `U2C` Active Zero-Deadzone Peak Detector (`D3` `1N4148WS`, `< 5 mV` threshold), `U2D` `101 kΩ` Unity-Gain Input Buffer.

2. **Input Buffering, Gain-Floor Limiting & HF Roll-Off**:
   - `J1.TN → GND` eliminates unpatched hum while `U2D` isolates `C1` ($1\,\mu\text{F}$ PET film) and `R1` ($100\text{ k}\Omega$) for $Z_{\text{in}} = 101\text{ k}\Omega$ and $f_c = 1.58\text{ Hz}$ (clamped by `D_IN` `BAV99`).
   - `R_GAIN_MIN` ($1\text{ k}\Omega$) in series with `RV1` (`A100k`) sets a $-0.10\times$ gain floor, `R_GAIN_FAIL` ($1\text{ M}\Omega$) guards against open-wiper faults, and `C_HF` ($47\text{ pF}$ C0G) sets $f_c \ge 36.9\text{ kHz}$.

3. **Power Entry, Reverse-Polarity & RC Bus Filtering**:
   - Shrouded keyed `2×5` Eurorack header `J4` (`B.Cu`) feeds series `B5819W` Schottky diodes (`D_PWR_P`, `D_PWR_N`) and $10\,\Omega$ `250 mW` (`1206`) series resistors (`R_PWR_P`, `R_PWR_N`) into $22\,\mu\text{F}$ $50\text{ V}$ SMD electrolytics (`C3`, `C4`, $f_c = 723\text{ Hz}$, internal `≈ ±11.55 V`), plus four $100\text{ nF}$ `50 V` `0603` X7R local IC bypass capacitors (`C_DEC1`–`C_DEC4`) at Pins 4 and 11 of `U1` and `U2`.

4. **Linearized `OFFSET`, Zero-Droop Film Hold & Clash-Rated Outputs**:
   - Deleting `R9` removes the `9.1%` release droop on `C2` ($1\,\mu\text{F}$ PET film, immune to MLCC microphonics and DC-bias collapse), while `R_ATK_MIN` ($470\,\Omega$) limits attack surge current.
   - Deleting `R14` and scaling `RV4` to `B10k` (`R11 = R12 = 1k`, `R13 = 18k`) holds envelope gain steady at $1.476\times\text{--}1.529\times$ across a linear $\pm 5.09\text{ V}$ offset range (`CW = +OUT`).
   - Split $470\,\Omega + 470\,\Omega$ `0.5 W` (`1210`) clash resistors (`R16A/B`, `R19A/B`), midpoint `BAV99` rail clamps (`D_OUT`, `D_INV_OUT`), and in-loop `10 kΩ` DC feedback (`R15`, `R18` + `100 pF` C0G `C_OUT1`, `C_OUT2`) deliver `0.00%` `OUT`/`INV_OUT` tracking mismatch.

---

## 🔄 Signal Flow & Functional Blocks

The circuit covers **60 populated physical components (`49` `B.Cu` SMD across `19` BOM lines + `11` manual/consigned THT)** plus **8 optional `DNP` test points** and **3 `DNP` optical fiducials** (**71 footprints total across 42 active nets**, matching [`docs/reference/netlist-and-bom.md`](docs/reference/netlist-and-bom.md)):

1. **Stage 0 — Power Entry, Protection & Decoupling (`J4`, `D_PWR_P/N`, `R_PWR_P/N`, `C3`–`C4`, `C_DEC1`–`C_DEC4`)**:
   Eurorack $\pm 12\text{ V}$ `2×5` IDC entry through `B5819W` Schottky reverse-polarity diodes, $10\,\Omega$ `1206` resistors, $22\,\mu\text{F}$ $50\text{ V}$ bulk electrolytics, and local $100\text{ nF}$ ceramic IC decoupling.
2. **Stage 1A & 1B — Input Buffer (`U2D`) & Protected Preamp (`U1A`)**:
   `J1.TN → GND`, `R_IN_PROT` ($1\text{ k}\Omega$), `C1` ($1\,\mu\text{F}$ PET film), `R1` ($100\text{ k}\Omega$), `D_IN` (`BAV99`), `R_IN_BUF` ($1\text{ k}\Omega$), and `U2D` buffer driving `U1A` (`R2` $10\text{ k}\Omega$, `R_GAIN_MIN` $1\text{ k}\Omega$ + `RV1` $100\text{ k}\Omega$ $\parallel$ `R_GAIN_FAIL` $1\text{ M}\Omega$ $\parallel$ `C_HF` $47\text{ pF}$).
3. **Stages 2 & 3 — `0.1%`-Matched Precision Full-Wave Rectifier (`U1B`, `U1C`, `D1_D2`)**:
   `U1B` with `BAT54S` dual Schottky (`D1_D2`) and `U1C` summing `7 × 10 kΩ ±0.1%` thin-film resistors (`R3`, `R4+R5`, `R6`, `R7`, `R8A+R8B`) for exact $+1.000\,|V_{\text{PREAMP\_OUT}}|$ (`≤ 0.80%` error).
4. **Stage 4 — Active Zero-Deadzone Peak Detector (`U2C`)**:
   `U2C` wrapping `D3` (`1N4148WS`) inside feedback to charge $1\,\mu\text{F}$ PET film `C2` through `R_ATK_MIN` ($470\,\Omega$) and `RV2` (`A50k` attack) and discharge through `R10` ($10\text{ k}\Omega$) and `RV3` (`A1M` release).
5. **Stage 5 — Linearized `OFFSET` & Protected Outputs (`U1D`, `U2A`, `RV4`)**:
   `U1D` (`R_ENV_PROT` $10\text{ k}\Omega$, `RV4` `B10k` / `R11`–`R13`) and `U2A` unity inverter (`R17` = `R18` = $10\text{ k}\Omega$) driving `J2` (`OUT`) and `J3` (`INV_OUT`) through split $470\,\Omega + 470\,\Omega$ `0.5 W` (`1210`) resistors, `BAV99` clamps, and in-loop feedback.
6. **Stage 6 — Active In-Loop LED Sink (`U2B`)**:
   `U2B` driving `D4` (`3 mm` Red LED) and anti-parallel `D_LED_CLAMP` (`1N4148WS`) against `R_LED` ($2.2\text{ k}\Omega$ to `GND`).

---

## 🎛️ Controls, I/O & Test Points Summary

| Reference | Component / Value | Taper / Type | Function |
| :--- | :--- | :--- | :--- |
| **`RV1`** (`GAIN`) | $100\text{ k}\Omega$ Potentiometer | Audio / Log (`A100k`) | Input Preamp Gain ($-0.10\times$ to $-9.17\times$, `-20 dB` to `+19.25 dB`) |
| **`RV2`** (`ATK`) | $50\text{ k}\Omega$ Potentiometer | Audio / Log (`A50k`) | Attack Time Control ($\tau_{\text{atk}} \approx 0.47\text{--}50.5\text{ ms}$) |
| **`RV3`** (`REL`) | $1\text{ M}\Omega$ Potentiometer | Audio / Log (`A1M`) | Release Time Control ($\tau_{\text{rel}} \approx 10\text{ ms--}1.01\text{ s}$) |
| **`RV4`** (`OFFSET`) | $10\text{ k}\Omega$ Potentiometer | Linear (`B10k`) | Output DC Offset Adjust (`±5.09 V` linear span, `CW = +OUT`) |
| **`J1`** (`IN`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN → GND`) | AC-Coupled Audio / CV Input ($Z_{\text{in}} = 101\text{ k}\Omega$, $f_c = 1.58\text{ Hz}$) |
| **`J2`** (`OUT`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN = NC`) | Non-Inverted Envelope CV Output (`BAV99` + `470R + 470R 0.5W` protected) |
| **`J3`** (`INV_OUT`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN = NC`) | Inverted Envelope CV Output ($-V_{\text{OUT}}$, `0.00%` tracking mismatch) |
| **`D4`** (`LED`) | 3mm Red THT LED (`C99771`) | Radial THT (In-Loop) | Precision V-to-I Envelope Indicator ($I_{\text{LED}} = V_{\text{ENV}} / 2.2\text{ k}\Omega$, `0.00 mA` idle) |
| **`J4`** (`PWR`) | 2×5 Shrouded IDC Header (`C53207560`) | 10-Pin Eurorack (`B.Cu`) | $\pm 12\text{ V}$ & `GND` Power Input (`B5819W` + `10 Ω / 22 µF` RC protected) |
| **`TP1`–`TP8`** (`DNP`) | `Ronghe RH-5001` (`C5199801`) | Optional THT Loops (`1.0 mm` drill) | Rear `B.Cu` Probing (`GND`, `+12V`, `-12V`, `IN_BUF`, `PREAMP`, `RECT`, `OUT`, `INV_OUT`) |

---

## 📄 Documentation, Tutorial & GitHub Pages Site

This repository publishes a multi-page **MkDocs Material** documentation site via [`.github/workflows/docs.yml`](.github/workflows/docs.yml) at **[https://domesticmouse.github.io/EnvelopeFollower/](https://domesticmouse.github.io/EnvelopeFollower/)**.

To preview the documentation site locally:

```bash
mkdocs serve
```

Documentation sources, clean-room stage artifacts, and session traces:

* [**`mkdocs.yml`**](mkdocs.yml) & [**`docs/`**](docs/) – Multi-page MkDocs Material tutorial (Stages 1–7) and technical reference source (deployed to GitHub Pages on push to `main`).
* [**`docs/reference/netlist-and-bom.md`**](docs/reference/netlist-and-bom.md) – Full Bill of Materials, ready-to-upload 19-line JLCPCB CSV listing, 42-net connection table, and manual KiCad capture guide.
* [**`docs/reference/build-checklist.md`**](docs/reference/build-checklist.md) – Interactive PCB layout, silkscreen verification, front-panel, and JLCPCB ordering checklist.
* [**`stages/`**](stages/) & [**`AuditReport.md`**](AuditReport.md) – Clean-room end-to-end replay artifacts (`stages/stage-1/` through `stages/stage-7/`) including SKiDL code, KiCad PCBs, Gerbers/drills, CPL, and audit report.
* [**`prompts/README.md`**](prompts/README.md) – Per-conversation prompt and build logs from the hardware design sessions.

---

## 📁 Repository Structure

```text
EnvelopeFollower/
├── LICENSE                                # Apache License 2.0
├── README.md                              # Project overview & documentation
├── AuditReport.md                         # Clean-room Stages 1–7 test-drive audit report
├── EnvelopeFollower.webp                  # Original Hagiwo hand-drawn reference schematic
├── .github/workflows/
│   └── docs.yml                           # GitHub Pages deployment workflow (MkDocs Material)
├── mkdocs.yml                             # MkDocs Material site configuration
├── docs/
│   ├── index.md                           # Documentation landing page & pipeline overview
│   ├── tutorial/                          # Multi-page stage-by-stage tutorial (Stages 1–7)
│   ├── reference/                         # Netlist/BOM guide and PCB fabrication checklist
│   ├── javascripts/mathjax.js             # MathJax v3 initialization for circuit equations
│   └── images/                            # Sketch, 3D portrait PCB/panel renders & landscape PCBA hero
├── stages/                                # Clean-room tutorial stage snapshots (stage-1 .. stage-7)
├── prompts/                               # Per-conversation prompt traces and build logs
├── skills-lock.json                       # Agent skill lockfile
└── .agents/skills/                        # Workspace skills (agy-brain-explorer, tutorial-test-drive)
```

---

## 📜 License & Disclaimer

Licensed under the [Apache License 2.0](LICENSE).

This is not an officially supported Google product.
