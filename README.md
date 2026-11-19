# Envelope Follower

An end-to-end hardware design tutorial (MkDocs Material site and prompt traces) for turning Hagiwo's analog envelope follower sketch into a 6 HP Eurorack KiCad 10 PCB and 3U front panel using AI hardware skills and SKiDL.

The original schematic is based on Hagiwo's [$4 Envelope Follower module - DIY Eurorack Modular Synthesizer](https://note.com/solder_state/n/n110e9ba066b3?hl=en).

![Hagiwo's Envelope Follower Schematic](EnvelopeFollower.webp)

---

## ⚡ Improved Circuit Overview

The tutorial adapts Hagiwo's original circuit for modern **Texas Instruments TL074H** (`TL074HIDR`, `SOIC-14`) quad op-amps, introducing enhancements for zero-deadzone envelope tracking, stability, low-noise performance, and Eurorack hardware protection:

1. **Dual `TL074HIDR` Configuration (All 8 Channels Active)**:
   - **U1 (`TL074H`)**: `U1A` Input Gain Stage, `U1B` Precision Half-Wave Rectifier, `U1C` $1.0\times$ Summing Rectifier (`R8` = $20\text{ k}\Omega$ 1%), `U1D` Output Gain ($\approx 2.98\times$) & Linear DC Offset Stage.
   - **U2 (`TL074H`)**: `U2A` Unity-Gain Inverting Output, `U2B` Active Voltage-to-Current LED Driver, `U2C` Active Zero-Deadzone Peak Driver (with catch diode `D7` & loop compensation `C11` = $47\text{ pF}$ C0G), `U2D` Zero-Load JFET `ENV_CAP` Buffer.

2. **Gain-Floor Limiting & HF Roll-Off**:
   - `R25` ($1\text{ k}\Omega$) in series with `RV1` (`A100k`) sets a $-0.1\times$ minimum gain floor so hot Eurorack audio can be padded down without muting or shorting `C10` ($47\text{ pF}$ C0G, $f_c \approx 33.5\text{ kHz}$ at max gain).

3. **Power Entry, Reverse-Polarity & RC Bus Filtering**:
   - Series `B5819W` Schottky diodes (`D5`, `D6`) and $10\,\Omega$ `1/4 W` (`1206`) series resistors (`R26`, `R27`) feed $10\,\mu\text{F}$ $50\text{ V}$ SMD electrolytics (`C3`, `C4`), plus four $100\text{ nF}$ `0603` X7R local IC bypass capacitors (`C5`–`C8`) placed directly at the $V_{CC+}$ (Pin 4) and $V_{CC-}$ (Pin 11) pins of `U1` and `U2`.

4. **Low-Impedance Linear `OFFSET` & Output Protection**:
   - Scaling `RV4` to `B10k` (`R11 = R12 = 1k`) driving `R13 = R14 = R15 = 100k` holds envelope gain steady at $2.97\times\text{--}2.99\times$ across a full $\pm 9.8\text{ V}$ linear offset range, while `C9` ($100\text{ nF}$) bypasses rail ripple on `OFFSET_WIPER` to `GND`.
   - **Short-Circuit & Rail Clamping**: $1\text{ k}\Omega$ `1/4 W` (`1206`) output resistors (`R16`, `R19`) plus `BAT54SLT1G` (`SOT-23`) dual series Schottky rail clamps (`D8`, `D9`) on `AMP_OUT` and `INV_AMP_OUT`.

---

## 🔄 Signal Flow & Functional Blocks

The circuit covers 54 populated components plus 8 optional `DNP` test points (62 footprints total) across 36 nets (matching [`docs/reference/netlist-and-bom.md`](docs/reference/netlist-and-bom.md)):

1. **Power Entry, Protection & Decoupling (`J_PWR`, `D5`–`D6`, `R26`–`R27`, `C3`–`C8`)**:
   Eurorack $\pm 12\text{ V}$ 10-pin power entry through `B5819W` Schottky reverse-polarity diodes (`D5`, `D6`), $10\,\Omega$ `1/4 W` series resistors (`R26`, `R27`), $10\,\mu\text{F}$ $50\text{ V}$ bulk electrolytics (`C3`, `C4`), and local $100\text{ nF}$ ceramic IC bypass capacitors (`C5`–`C8`).
2. **Input Coupling & Gain Stage (`U1A`)**:
   AC-coupled input (`J1`, `C1` $1\,\mu\text{F}$, `R1` $1\text{ M}\Omega$ pulldown) driving an inverting op-amp stage (`R2` $10\text{ k}\Omega$, `RV1` $100\text{ k}\Omega$, `R25` $1\text{ k}\Omega$, `C10` $47\text{ pF}$).
3. **Precision Full-Wave Rectifier (`U1B`, `U1C`)**:
   `U1B` with `1N4148W` diodes (`D1`, `D2`) and $10\text{ k}\Omega$ resistors (`R3`, `R4`) forms an active half-wave rectifier, which `U1C` sums (`R5` $10\text{ k}\Omega$) against the direct signal (`R6` + `R7`, $20\text{ k}\Omega$ total) with a $20\text{ k}\Omega$ feedback resistor (`R8`).
4. **Active Peak Detector, Envelope Timing & Buffer (`U2C`, `U2D`)**:
   `U2C` with catch diode `D7` (`1N4148W`) and loop compensation `C11` ($47\text{ pF}$) drives `D3` (`1N4148W`) to charge the $220\text{ nF}$ smoothing capacitor `C2` through `R9` ($1\text{ k}\Omega$) and `RV2` ($50\text{ k}\Omega$ attack control) and discharge through `R10` ($47\text{ k}\Omega$) and `RV3` ($1\text{ M}\Omega$ release control), buffered by `U2D` (`R24` $100\text{ k}\Omega$ feedback).
5. **Output Amplifier & Linear DC Offset Stage (`U1D`)**:
   Follows `ENV_SIG` on Pin 12 ($+$) while summing an adjustable $\pm 12\text{ V}$ DC bias (`R11`, `R12`, `RV4`, `C9`, `R13`, `R14`, `R15`) at Pin 13 ($-$) and driving `J2` (`OUT`) through `D8` (`BAT54S`) and `R16` ($1\text{ k}\Omega$ `1/4 W`).
6. **Inverted Output & Active V-to-I LED Driver (`U2A`, `U2B`)**:
   - `U2A`: Unity-gain inverting stage (`R17` = `R18` = $10\text{ k}\Omega$) driving `J3` (`INV_OUT`) through `D9` (`BAT54S`) and `R19` ($1\text{ k}\Omega$ `1/4 W`).
   - `U2B`: Active voltage-to-current LED buffer driving `D4` (`LED`) against `R21` ($1.5\text{ k}\Omega$ to `GND`).

---

## 🎛️ Controls, I/O & Test Points Summary

| Reference | Component / Value | Taper / Type | Function |
| :--- | :--- | :--- | :--- |
| **`RV1`** (`GAIN`) | $100\text{ k}\Omega$ Potentiometer | Audio / Log (`A100k`) | Input Preamp Gain ($-0.1\times$ to $-10.1\times$) |
| **`RV2`** (`ATK`) | $50\text{ k}\Omega$ Potentiometer | Audio / Log (`A50k`) | Attack Time Control ($\tau_{\text{atk}} \approx 0.22\text{--}11.2\text{ ms}$) |
| **`RV3`** (`Release`) | $1\text{ M}\Omega$ Potentiometer | Audio / Log (`A1M`) | Release Time Control ($\tau_{\text{rel}} \approx 10.3\text{--}230\text{ ms}$) |
| **`RV4`** (`OFFSET`) | $10\text{ k}\Omega$ Potentiometer | Linear (`B10k`) | Output DC Offset Adjust ($\approx -9.8\text{ V}$ to $+9.8\text{ V}$, flat $\approx 2.98\times$ gain) |
| **`J1`** (`IN`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT | AC-Coupled Audio / CV Input ($Z_{\text{in}} \approx 10\text{ k}\Omega$, $f_c \approx 15.9\text{ Hz}$) |
| **`J2`** (`OUT`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT | Non-Inverted Envelope CV Output (`BAT54S` + `1k` `1/4 W` protected) |
| **`J3`** (`INV_OUT`) | 3.5mm Mono Jack (`WQP-PJ398SM`) | Switched THT | Inverted Envelope CV Output ($-V_{\text{AMP\_OUT}}$, `BAT54S` + `1k` `1/4 W` protected) |
| **`D4`** (`LED`) | 3mm THT LED | Any Color | Active Voltage-to-Current Envelope Indicator ($I_{\text{LED}} = V_{\text{ENV\_SIG}} / 1.5\text{ k}\Omega$) |
| **`J_PWR`** | 2×5 Shrouded IDC Header | 10-Pin Eurorack | $\pm 12\text{ V}$ & `GND` Power Input (`B5819W` + `10 Ω` RC protected) |
| **`TP1`–`TP8`** (`DNP`) | `Ronghe RH-5001` (`C5199801`) | Optional THT Loops (`1.0 mm` drill) | Bench Probing (`GND`, `+12V`, `-12V`, `PRE`, `HALF`, `RECT`, `ENV`, `OFS`) |

---

## 📄 Documentation, Tutorial & GitHub Pages Site

This repository publishes a multi-page **MkDocs Material** documentation site via [`.github/workflows/docs.yml`](.github/workflows/docs.yml) at **[https://domesticmouse.github.io/EnvelopeFollower/](https://domesticmouse.github.io/EnvelopeFollower/)**.

To preview the documentation site locally:

```bash
mkdocs serve
```

Documentation sources and session traces:

* [**`mkdocs.yml`**](mkdocs.yml) & [**`docs/`**](docs/) – Multi-page MkDocs Material tutorial (Stages 1–7) and technical reference source (deployed to GitHub Pages on push to `main`).
* [**`docs/reference/netlist-and-bom.md`**](docs/reference/netlist-and-bom.md) – Full Bill of Materials, ready-to-upload JLCPCB CSV listing, 36-net connection table, and 8-step KiCad capture guide.
* [**`docs/reference/build-checklist.md`**](docs/reference/build-checklist.md) – Interactive PCB layout, silkscreen verification, front-panel, and JLCPCB ordering checklist.
* [**`prompts/README.md`**](prompts/README.md) – Per-conversation prompt and build logs from the hardware design sessions.

---

## 📁 Repository Structure

```text
EnvelopeFollower/
├── LICENSE                                # Apache License 2.0
├── README.md                              # Project overview & documentation
├── EnvelopeFollower.webp                  # Original Hagiwo hand-drawn reference schematic
├── .github/workflows/
│   └── docs.yml                           # GitHub Pages deployment workflow (MkDocs Material)
├── mkdocs.yml                             # MkDocs Material site configuration
├── docs/
│   ├── index.md                           # Documentation landing page & pipeline overview
│   ├── tutorial/                          # Multi-page stage-by-stage tutorial (Stages 1–7)
│   ├── reference/                         # Netlist/BOM guide and PCB fabrication checklist
│   ├── javascripts/mathjax.js             # MathJax v3 initialization for circuit equations
│   └── images/                            # Original sketch, schematic SVG, and 3D PCB/panel renders
├── prompts/                               # Per-conversation prompt traces and build logs
├── skills-lock.json                       # Agent skill lockfile
└── .agents/skills/agy-brain-explorer/     # Brain trajectory explorer skill
```

---

## 📜 License & Disclaimer

Licensed under the [Apache License 2.0](LICENSE).

This is not an officially supported Google product.
