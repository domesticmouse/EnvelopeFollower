# Envelope Follower

An end-to-end hardware design tutorial (MkDocs Material site and clean-room stage snapshots) for turning Hagiwo's analog envelope follower sketch into a 6 HP Eurorack KiCad 10 PCB and 3U front panel using AI hardware skills and SKiDL.

![Eurorack Envelope Follower 6 HP PCBA 3D Render](docs/images/pcb_back_landscape.png)

The original schematic is based on Hagiwo's [$4 Envelope Follower module - DIY Eurorack Modular Synthesizer](https://note.com/solder_state/n/n110e9ba066b3?hl=en):

![Hagiwo's Envelope Follower Schematic](EnvelopeFollower.webp)

---

## ⚡ Improved Circuit Overview

The tutorial adapts Hagiwo's original circuit for modern **Texas Instruments TL074H** (`TL074HIDR`, `SOIC-14`) quad op-amps, introducing enhancements for high-Z protected input, zero-deadzone envelope tracking, exact unity-gain precision rectification, linear offset summing, and Eurorack hardware protection:

1. **Dual `TL074HIDR` Configuration (All 8 Channels Active)**:
   - **U1 (`TL074H`)**: `U1A` High-Z Non-Inverting Gain Stage (`+0.45×` to `+10.04×`, fixed `+11.0×` behind `A100k` attenuator), `U1B` Precision Half-Wave Rectifier (`D1`, `D2` `1N4148WS`), `U1C` Exact `1.00×` Summing Rectifier (`R8 = R10 = 20 kΩ`), `U1D` Near-Unity (`0.975×`) Difference Amplifier & Linear `OFFSET` Stage (`±4.69 V`, `CW = +OUT`).
   - **U2 (`TL074H`)**: `U2A` Unity-Gain Inverting Output (`INV_OUT`, `-1.00×`), `U2B` Precision Constant-Current LED Sink (`0.50 mA/V`, `R27 = 1 kΩ` + `D6` reverse clamp), `U2C` Active Zero-Deadzone Peak Detector (`D3` `1N4148WS` inside loop + `D5` anti-saturation clamp + `R11`/`C10` compensation), `U2D` Dedicated Unity-Gain `C2` (`ENV_CAP`) Buffer (`V_ENV_BUF`).

2. **High-Z Protected Input, Gain Floor & HF Roll-Off**:
   - `J1.TN → GND` eliminates unpatched hum, while `R1` ($10\text{ k}\Omega$) + `D9` (`BAT54S`) rail clamps sit **ahead of `C1`** ($1\,\mu\text{F}$ $63\text{ V}$ `P=5mm` box film, `B.Cu` THT) so Schottky leakage never crosses into `U1A`'s DC gain path.
   - `RV1` (`A100k`) log attenuator, `R2` ($4.7\text{ k}\Omega$) gain-floor resistor, and `R3` ($1\text{ M}\Omega$) open-wiper pull-down provide $Z_{\text{in}} \approx 113\text{ k}\Omega$ and $f_c = 1.41\text{ Hz}$ into `U1A` (`R4` = $10\text{ k}\Omega$, `R5` = $100\text{ k}\Omega$ $\parallel$ `C9` = $22\text{ pF}$ C0G, $f_{-3\text{dB}} = 72\text{ kHz}$).

3. **Power Entry, Reverse-Polarity & RC Bus Filtering**:
   - Shrouded keyed `2×5` Eurorack header `J4` (`B.Cu`) feeds series `1N5819WS` (`SOD-323`) Schottky diodes (`D7`, `D8`) and $10\,\Omega$ `0603` series resistors (`R28`, `R29`) into $47\,\mu\text{F}$ $35\text{ V}$ SMD electrolytics (`C3`, `C4`, $f_c = 339\text{ Hz}$, internal `≈ ±11.6 V`), plus four $100\text{ nF}$ `50 V` `0603` X7R local IC bypass capacitors (`C5`–`C8`) at Pins 4 and 11 of `U1` and `U2`.

4. **Zero-Droop Film Hold, Linear `OFFSET` & Fault-Rated Outputs**:
   - Removing `R9` and buffering `C2` ($1\,\mu\text{F}$ $63\text{ V}$ box film, immune to MLCC microphonics and DC-bias collapse) with `U2D` eliminates release-tap droop and `~0.6 V` diode deadzone; `R12` ($150\,\Omega$) limits attack surge (`RV2` `A50k`) and `R14` ($4.7\text{ M}\Omega$) parallels `RV3` (`A1M`) for open-wiper safety.
   - Converting `U1D` to a near-unity (`0.975×`, `R15`/`R16`/`R19`/`R20` = $100\text{ k}\Omega$) difference amplifier with `RV4` (`B10k`) and `R17`/`R18` ($6.8\text{ k}\Omega$) tracks `0–10 V` unclipped with `±0.25%` gain flatness across a linear `±4.69 V` offset span (`CW = +OUT`).
   - `1 kΩ` `1 W` `2512` output build-out resistors (`R21`, `R24`) backed by `BAT54S` ESD/rail clamps (`D10`, `D11`) survive continuous worst-case $\pm 12\text{ V}$ output clashes (`0.51 W` = `51%` rating).

---

## 🔄 Signal Flow & Functional Blocks

The latest clean-room Stage 7 build covers **60 populated physical components (`49` `B.Cu` SMD across `20` BOM lines + `11` manual/consigned THT: `3` rear `B.Cu` + `8` front `F.Cu`)** plus **8 optional `DNP` test points** and **3 `DNP` optical fiducials** (**71 footprints total / 68 netlist components across 39 named nets**, matching [`stages/stage-7/EnvelopeFollowerImproved.md`](stages/stage-7/EnvelopeFollowerImproved.md) and [`stages/stage-7/EnvelopeFollowerBOM.md`](stages/stage-7/EnvelopeFollowerBOM.md)):

1. **Stage 0 — Power Entry, Protection & Decoupling (`J4`, `D7`–`D8`, `R28`–`R29`, `C3`–`C8`)**:
   Eurorack $\pm 12\text{ V}$ `2×5` IDC entry through `1N5819WS` Schottky reverse-polarity diodes, $10\,\Omega$ series resistors, $47\,\mu\text{F}$ $35\text{ V}$ bulk electrolytics, and local $100\text{ nF}$ ceramic IC decoupling (`±11.6 V` protected rails).
2. **Stage 1 — High-Z Protected AC Input & Gain (`J1`, `R1`–`R5`, `D9`, `C1`, `C9`, `RV1`, `U1A`)**:
   `J1.TN → GND`, `R1` ($10\text{ k}\Omega$) + `D9` (`BAT54S`) pre-cap clamp, `C1` ($1\,\mu\text{F}$ film), `RV1` (`A100k`) + `R2` ($4.7\text{ k}\Omega$) + `R3` ($1\text{ M}\Omega$) driving fixed `+11.0×` `U1A` (`R4` $10\text{ k}\Omega$, `R5` $100\text{ k}\Omega$ $\parallel$ `C9` $22\text{ pF}$ C0G).
3. **Stage 2 — Exact `1.00×` Precision Full-Wave Rectifier (`U1B`, `U1C`, `R6`–`R10`, `D1`–`D2`)**:
   `U1B` half-wave stage (`R6` = `R7` = $10\text{ k}\Omega$, `D1`/`D2` `1N4148WS`) feeding `U1C` summer (`R8` = `R10` = $20\text{ k}\Omega$, `R9` = $10\text{ k}\Omega$) for exact $+1.00\,|V_{\text{GAIN}}|$.
4. **Stage 3 — Active Zero-Deadzone Peak Detector & `C2` Buffer (`U2C`, `U2D`, `D3`, `D5`, `R11`–`R14`, `C2`, `C10`, `RV2`, `RV3`)**:
   `U2C` wrapping `D3` (`1N4148WS`) inside feedback (with `D5` anti-saturation clamp and `R11` $200\text{ k}\Omega$ / `C10` $100\text{ pF}$ C0G compensation) to charge $1\,\mu\text{F}$ film `C2` via `R12` ($150\,\Omega$) + `RV2` (`A50k` attack), discharge via `R13` ($10\text{ k}\Omega$) + `RV3` (`A1M` $\parallel$ `R14` $4.7\text{ M}\Omega$ release), and buffer `ENV_CAP` with unity-gain `U2D`.
5. **Stage 4 — Linear `OFFSET`, Output Buffer & Protected Dual Outputs (`U1D`, `U2A`, `RV4`, `R15`–`R24`, `D10`–`D11`, `J2`, `J3`)**:
   `U1D` (`0.975×` diff amp, `R15`/`R16`/`R19`/`R20` $100\text{ k}\Omega$, `RV4` `B10k` + `R17`/`R18` $6.8\text{ k}\Omega$) and `U2A` unity inverter (`R22` = `R23` = $10\text{ k}\Omega$) driving `J2` (`OUT`) and `J3` (`INV_OUT`) via `BAT54S` clamps (`D10`, `D11`) and `1 kΩ` `1 W` `2512` resistors (`R21`, `R24`).
6. **Stage 5 — Precision Constant-Current LED Driver (`U2B`, `R25`–`R27`, `D4`, `D6`)**:
   `R25`/`R26` ($10\text{ k}\Omega$ / $10\text{ k}\Omega$ `0.5×` divider) into `U2B` driving `D4` (`3 mm` THT LED) and reverse-protection clamp `D6` (`1N4148WS`) against `R27` ($1\text{ k}\Omega$ sense resistor to `GND`) for $0.50\text{ mA/V}$ $V_f$-independent brightness.

---

## 🎛️ Controls, I/O & Test Points Summary

| Reference | Component / Value | Taper / Type | Function |
| :--- | :--- | :--- | :--- |
| **`RV1`** (`GAIN`) | $100\text{ k}\Omega$ Potentiometer | Audio / Log (`A100k`) | Input Attenuator / Gain ($+0.45\times$ to $+10.04\times$, `-6.9 dB` to `+20.0 dB`) |
| **`RV2`** (`ATK`) | $50\text{ k}\Omega$ Potentiometer | Audio / Log (`A50k`) | Attack Time Control ($\tau_{\text{atk}} \approx 0.15\text{--}50.15\text{ ms}$) |
| **`RV3`** (`REL`) | $1\text{ M}\Omega$ Potentiometer | Audio / Log (`A1M`) | Release Time Control ($\tau_{\text{rel}} \approx 10\text{--}835\text{ ms}$, `4.7 MΩ` fail-safe) |
| **`RV4`** (`OFFSET`) | $10\text{ k}\Omega$ Potentiometer | Linear (`B10k`) | Output DC Offset Adjust (`±4.69 V` linear span, `CW = +OUT`) |
| **`J1`** (`IN`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN → GND`) | AC-Coupled Audio / CV Input ($Z_{\text{in}} \approx 113\text{ k}\Omega$, $f_c = 1.41\text{ Hz}$, `BAT54S` clamped) |
| **`J2`** (`OUT`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN = NC`) | Non-Inverted Envelope CV Output (`0.975×`, `BAT54S` + `1 kΩ 1 W` protected) |
| **`J3`** (`INV_OUT`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN = NC`) | Inverted Envelope CV Output ($-1.00\,V_{\text{OUT}}$, `BAT54S` + `1 kΩ 1 W` protected) |
| **`D4`** (`LED`) | 3mm Green THT LED (`C85161`) | Radial THT (In-Loop) | Constant-Current Envelope Indicator ($0.50\text{ mA/V}$, `0.00 mA` idle, $V_f$-independent) |
| **`J4`** (`PWR`) | 2×5 Shrouded IDC Header (`C53207560`) | 10-Pin Eurorack (`B.Cu`) | $\pm 12\text{ V}$ & `GND` Power Input (`1N5819WS` + `10 Ω / 47 µF` RC protected → `±11.6 V`) |
| **`TP1`–`TP8`** (`DNP`) | `Ronghe RH-5001` (`C5199801`) | Optional THT Loops (`1.0 mm` drill) | Rear `B.Cu` Probing (`+12V_PROT`, `-12V_PROT`, `GND`, `V_GAIN`, `V_RECT`, `V_ENV_BUF`, `V_OUT_BUF`, `V_INV_BUF`) |

---

## 📄 Documentation, Tutorial & GitHub Pages Site

This repository publishes a multi-page **MkDocs Material** documentation site via [`.github/workflows/docs.yml`](.github/workflows/docs.yml) at **[https://domesticmouse.github.io/EnvelopeFollower/](https://domesticmouse.github.io/EnvelopeFollower/)**.

To preview the documentation site locally:

```bash
mkdocs serve
```

Documentation sources, clean-room stage artifacts, and audit reports:

* [**`mkdocs.yml`**](mkdocs.yml) & [**`docs/`**](docs/) – Multi-page MkDocs Material tutorial (Stages 1–7 plus optional DC-coupled CV mode) and technical reference source (deployed to GitHub Pages on push to `main`).
* [**`docs/reference/netlist-and-bom.md`**](docs/reference/netlist-and-bom.md) – Tutorial reference Bill of Materials, ready-to-upload JLCPCB CSV listing, netlist connection table, and manual KiCad capture guide.
* [**`docs/reference/build-checklist.md`**](docs/reference/build-checklist.md) – Interactive PCB layout, silkscreen verification, front-panel, and JLCPCB ordering checklist.
* [**`stages/`**](stages/) & [**`AuditReport.md`**](AuditReport.md) – Clean-room end-to-end replay artifacts (`stages/stage-1/` through `stages/stage-7/`) including SKiDL code, KiCad PCBs, Gerbers/drills, bottom-side CPL, [`stages/stage-7/OrderingNotes.md`](stages/stage-7/OrderingNotes.md), and test-drive audit report.
* [**`SkillImprovementAuditReport.md`**](SkillImprovementAuditReport.md) – Per-prompt `/agy-customizations` hardware skill improvement audit (`22` deduplicated findings across `15` tutorial prompts).
* [**`PotentialImprovements.md`**](PotentialImprovements.md) – Engineering note on adding an `AC / DC` input coupling switch (`SW1`) for CV rectification and AR slew limiting.

---

## 📁 Repository Structure

```text
EnvelopeFollower/
├── LICENSE                                # Apache License 2.0
├── README.md                              # Project overview & documentation
├── AuditReport.md                         # Clean-room Stages 1–7 test-drive audit report
├── SkillImprovementAuditReport.md         # Per-prompt hardware skills improvement audit
├── PotentialImprovements.md               # Optional DC-coupled CV / LFO slew design note
├── EnvelopeFollower.webp                  # Original Hagiwo hand-drawn reference schematic
├── .github/workflows/
│   └── docs.yml                           # GitHub Pages deployment workflow (MkDocs Material)
├── mkdocs.yml                             # MkDocs Material site configuration
├── docs/
│   ├── index.md                           # Documentation landing page & pipeline overview
│   ├── tutorial/                          # Multi-page stage-by-stage tutorial (Stages 1–7 + optional mode)
│   ├── reference/                         # Netlist/BOM guide and PCB fabrication checklist
│   ├── javascripts/mathjax.js             # MathJax v3 initialization for circuit equations
│   └── images/                            # Sketch, 3D portrait PCB/panel renders & landscape PCBA hero
├── stages/                                # Clean-room tutorial stage snapshots (stage-1 .. stage-7)
├── skills-lock.json                       # Agent skill lockfile
└── .agents/skills/                        # Workspace skills (agy-brain-explorer, tutorial-test-drive)
```

---

## 📜 License & Disclaimer

Licensed under the [Apache License 2.0](LICENSE).

This is not an officially supported Google product.
