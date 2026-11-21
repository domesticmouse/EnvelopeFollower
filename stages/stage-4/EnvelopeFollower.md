# Envelope Follower — Circuit Description & Build Specification

Extracted from [EnvelopeFollower.webp](./EnvelopeFollower.webp) (dated `2022-01-18 22:58`).

> **Note on Reference Designators & Net Names:** The source schematic is hand-drawn without printed reference designators (`R1`, `C1`, `U1`, etc.) or internal net names. Consistent designators and net names are assigned throughout this document so every connection can be built unambiguously on a breadboard, perfboard, or schematic/PCB tool (e.g., KiCad / SKiDL). All component values, polarities, and circuit notes match the source schematic verbatim; practical build recommendations not drawn on the schematic (such as `100 nF` IC decoupling capacitors and component voltage/power ratings) are explicitly marked as **Build Notes**.

---

## 1. Overview & Electrical Summary

This circuit is a dual-rail (`±12 V`) Eurorack-style analog **Envelope Follower** that converts an AC audio or modulation input signal (`IN`) into a smooth positive control voltage (`OUT`) and an inverted control voltage (`INV_OUT`), with adjustable input gain (`GAIN`), attack time (`ATK`), release time (`Release`), DC output offset (`OFFSET`), and an envelope activity `LED`.

### Key Specifications (Derived from Schematic Values)

| Parameter | Value / Behavior | Notes |
|---|---|---|
| **Supply Rails** | `+12 V`, `GND`, `-12 V` | Labeled `+12V in`, `GND`, `-12V in` (`Vcc+ = +12V`, `Vcc- = -12V`) |
| **Op-Amps** | `6` op-amp units (`TL074` or `TL072`) | Recommended: `1 × TL074` (quad) + `1 × TL072` (dual), or `3 × TL072` |
| **Input Coupling & Impedance** | AC-coupled (`4.7 µF`), `~9.9 kΩ` AC input impedance | High-pass cutoff `f_c ≈ 3.4 Hz` (`1M \|\| 10k` into `U1A` virtual ground) |
| **Input Gain (`GAIN`, `100k`)** | Inverting gain `0` to `-10×` (`-∞` to `+20 dB` magnitude) | `|A_v| = R_GAIN / 10 kΩ` (`0 Ω` to `100 kΩ`) |
| **Rectifier** | Positive-going precision full-wave rectifier | `V_rect = +1.1 × |V_gain|` (`22k / 20k`), followed by `1N4148` peak diode (`~0.6 V` forward drop) |
| **Attack Time Constant (`ATK`, `50k`)** | `~0 ms` to `50 ms` (`τ_atk ≈ R_ATK × 1 µF`) | Instantaneous slewing at `0 Ω` up to `50 ms` at `50 kΩ` |
| **Release Time Constant (`Release`, `1M`)** | `11 ms` to `~1.01 s` (`τ_rel = (11 kΩ + R_REL) × 1 µF`) | Discharge path is `1 kΩ + 10 kΩ + R_REL` to `GND` |
| **Output Gain & Offset (`OFFSET`, `100k`)** | `V_OUT ≈ 2.25 × V_env` (at center) to `2.52 × V_env ∓ 5.22 V` | **Inverting offset polarity:** wiper toward `+12V` shifts `OUT` negative; wiper toward `-12V` shifts `OUT` positive |
| **Outputs** | `OUT` and `INV_OUT` (`-V_OUT`), `1 kΩ` series output impedance | Clamped near TL07x rail limits (`≈ ±10.5 V` to `±11 V` on `±12 V`) |
| **LED Indicator** | Buffered envelope follower with `-2.79 V` cathode bias | `LED` driven via `U2B` follower + `22k`; cathode biased via `10k` to `GND` / `33k` to `-12V` |

---

## 2. Signal Flow Diagram

```text
  IN (Jack)
     │
  [4.7 µF]──[1M to GND]──[10k]──▶( U1A: Inverting Gain, 0..-10x via GAIN 100k )
                                        │
                    ┌───────────────────┴──────────────────────┐
                    ▼                                          ▼
         [10k]──( U1B: Half-Wave Rectifier )          [10k]──[10k] (= 20k)
                 w/ D1, D2 (1N4148) & 10k fb                   │
                    │                                          │
                    └───────────────[10k]──────────────────────┴──▶( U1C: Inverting Summer, 22k fb )
                                                                          │
                                                                   [D3: 1N4148 (A→K)]
                                                                          │
                                                                    [ATK: 50k pot]
                                                                          │
                                                    ┌─────────────────────┤
                                                [1 µF to GND]            [1k]
                                                                          │  (ENV_RAW / "LED" net)
                              ┌───────────────────────────────────────────┼──────────────────────┐
                              ▼                                           ▼                      ▼
                     [10k + Release 1M]                     ( U1D: Output Amp + OFFSET )     [10k]
                              │                                  │              │                │
                             GND                               [1k]           [10k]        ( U2B: Follower )
                                                                 │              │                │
                                                            OUT (Jack)   ( U2A: Inv -1x )      [22k]
                                                                                │                │
                                                                              [1k]         [LED (D4: A→K)]
                                                                                │                │
                                                                         INV_OUT (Jack)  [10k to GND / 33k to -12V]
```

---

## 3. Bill of Materials (BOM)

### 3.1 Integrated Circuits (6 Op-Amp Units Total)

The schematic specifies: **"All op-amp: TL074 or TL072, Vcc+ is +12V, Vcc- is -12V."**

Because the circuit uses exactly **6 op-amp units**, the cleanest zero-waste package options are:
- **Option A (used in Pin Map below):** `1 × TL074` (quad, 14-pin DIP/SOIC) + `1 × TL072` (dual, 8-pin DIP/SOIC) — `0` spare units.
- **Option B (all duals):** `3 × TL072` — `0` spare units.
- **Option C (all quads):** `2 × TL074` — `2` unused units (must be terminated as unity-gain followers with `+` tied to `GND` and `-` tied to output; never leave unused inputs floating).

| Ref | Qty | Value | Description | Package Notes |
|---|---|---|---|---|
| `U1` | 1 | `TL074` | Quad JFET-input op-amp (`U1A`–`U1D`) | DIP-14 (breadboard/THT) or SOIC-14 (SMD) |
| `U2` | 1 | `TL072` | Dual JFET-input op-amp (`U2A`–`U2B`) | DIP-8 (breadboard/THT) or SOIC-8 (SMD) |

### 3.2 Diodes & Indicator LED

| Ref | Qty | Value | Schematic Orientation | Role |
|---|---|---|---|---|
| `D1` | 1 | `1N4148` | Cathode (`K`) to `U1B` `-` input; Anode (`A`) to `U1B` output | Rectifier clamping feedback diode |
| `D2` | 1 | `1N4148` | Cathode (`K`) to `U1B` output; Anode (`A`) to `R4`/`R7` junction | Rectifier series output diode |
| `D3` | 1 | `1N4148` | Anode (`A`) to `U1C` output; Cathode (`K`) to `RV2` (`ATK`) | Peak-charging isolation diode |
| `D4` | 1 | `LED` | Anode (`A`) to `R21` (`22k`); Cathode (`K`) to `R22`/`R23` node | Envelope indicator LED (3 mm or 5 mm; see Section 6.5) |

### 3.3 Resistors (23 Total)

*Build Note:* `1/4 W` metal-film (`1%`) through-hole or `0603`/`0805` (`1%`) SMD resistors are suitable across the entire circuit (power dissipation per resistor is `< 10 mW` everywhere). Using `1%` tolerance is especially helpful in the precision rectifier (`R3`–`R8`) and inverter (`R17`, `R18`) for clean half-wave symmetry and accurate `-1×` inversion.

#### Summary by Value

| Value | Qty | Reference Designators |
|---|---|---|
| `1 kΩ` | 3 | `R9`, `R16`, `R19` |
| `10 kΩ` | 16 | `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R10`, `R11`, `R12`, `R13`, `R14`, `R15`, `R17`, `R18`, `R20`, `R22` |
| `22 kΩ` | 2 | `R8`, `R21` |
| `33 kΩ` | 1 | `R23` |
| `1 MΩ` | 1 | `R1` |

#### Detailed Resistor List

| Ref | Value | Circuit Stage | Connections (Net 1 ↔ Net 2) |
|---|---|---|---|
| `R1` | `1 MΩ` | Input Stage | `IN_AC` ↔ `GND` |
| `R2` | `10 kΩ` | Input Gain (`U1A`) | `IN_AC` ↔ `IN_SUM` (`U1A` `-`) |
| `R3` | `10 kΩ` | Rectifier (`U1B`) | `V_GAIN` (`U1A` out) ↔ `RECT_INV` (`U1B` `-`) |
| `R4` | `10 kΩ` | Rectifier (`U1B`) | `RECT_INV` (`U1B` `-`) ↔ `RECT_MID` (`D2.A` / `R7`) |
| `R5` | `10 kΩ` | Rectifier (`U1C` `20k` branch) | `V_GAIN` (`U1A` out) ↔ `RECT_FF_MID` |
| `R6` | `10 kΩ` | Rectifier (`U1C` `20k` branch) | `RECT_FF_MID` ↔ `SUM_INV` (`U1C` `-`) |
| `R7` | `10 kΩ` | Rectifier (`U1C` summing) | `RECT_MID` (`D2.A` / `R4`) ↔ `SUM_INV` (`U1C` `-`) |
| `R8` | `22 kΩ` | Rectifier (`U1C` feedback) | `SUM_INV` (`U1C` `-`) ↔ `V_RECT` (`U1C` out) |
| `R9` | `1 kΩ` | Envelope Detector | `ENV_CAP` (`RV2` / `C2`) ↔ `ENV_RAW` |
| `R10` | `10 kΩ` | Release Path | `ENV_RAW` ↔ `REL_MID` (`RV3` top) |
| `R11` | `10 kΩ` | Offset Divider | `+12V` ↔ `OFF_TOP` (`RV4` top) |
| `R12` | `10 kΩ` | Offset Divider | `-12V` ↔ `OFF_BOT` (`RV4` bottom) |
| `R13` | `10 kΩ` | Output Stage (`U1D`) | `OFF_WIPER` (`RV4` wiper) ↔ `OUT_INV_NODE` (`U1D` `-`) |
| `R14` | `10 kΩ` | Output Stage (`U1D`) | `OUT_INV_NODE` (`U1D` `-`) ↔ `GND` |
| `R15` | `10 kΩ` | Output Stage (`U1D`) | `OUT_INV_NODE` (`U1D` `-`) ↔ `V_OUT_BUF` (`U1D` out) |
| `R16` | `1 kΩ` | Output (`OUT`) | `V_OUT_BUF` (`U1D` out) ↔ `OUT_TIP` (`J2` Tip) |
| `R17` | `10 kΩ` | Inverted Output (`U2A`) | `V_OUT_BUF` (`U1D` out) ↔ `INV_SUM` (`U2A` `-`) |
| `R18` | `10 kΩ` | Inverted Output (`U2A`) | `INV_SUM` (`U2A` `-`) ↔ `V_INV_BUF` (`U2A` out) |
| `R19` | `1 kΩ` | Inverted Output (`INV_OUT`) | `V_INV_BUF` (`U2A` out) ↔ `INV_OUT_TIP` (`J3` Tip) |
| `R20` | `10 kΩ` | LED Buffer (`U2B`) | `ENV_RAW` (`LED` net) ↔ `LED_BUF_IN` (`U2B` `+`) |
| `R21` | `22 kΩ` | LED Driver | `V_LED_DRV` (`U2B` out) ↔ `LED_A` (`D4` Anode) |
| `R22` | `10 kΩ` | LED Cathode Bias | `LED_BIAS` (`D4` Cathode) ↔ `GND` |
| `R23` | `33 kΩ` | LED Cathode Bias | `LED_BIAS` (`D4` Cathode) ↔ `-12V` |

### 3.4 Capacitors (4 Drawn on Schematic + Recommended Decoupling)

| Ref | Qty | Value | Type / Polarity on Schematic | Connections | Build Spec Recommendation |
|---|---|---|---|---|---|
| `C1` | 1 | `4.7 µF` | Non-polarized symbol | `IN_TIP` ↔ `IN_AC` | Film or bipolar/non-polarized electrolytic (`≥ 25 V`; audio AC coupling) |
| `C2` | 1 | `1 µF` | Non-polarized symbol | `ENV_CAP` ↔ `GND` | Film (polyester/polypropylene) or C0G/X7R ceramic (`≥ 25 V`; envelope timing cap) |
| `C3` | 1 | `4.7 µF` | Polarized electrolytic (`+` / hatched) | `+` to `+12V`, `-` to `GND` | Aluminum electrolytic (`≥ 25 V`, e.g., `25 V` or `35 V`) |
| `C4` | 1 | `4.7 µF` | Polarized electrolytic (`+` / hatched) | `+` to `GND`, `-` to `-12V` | Aluminum electrolytic (`≥ 25 V`, e.g., `25 V` or `35 V`) |
| *`C5`–`C8`* | *4 (Build Note)* | *`100 nF`* | *Not drawn in source schematic* | *`+12V`/`-12V` to `GND` at `U1` & `U2`* | *Recommended ceramic X7R (`≥ 25 V`) local IC supply decoupling* |

### 3.5 Potentiometers (4 Total, Linear Taper `B`)

| Ref | Label | Value | Wiring Configuration | Schematic Terminal Mapping |
|---|---|---|---|---|
| `RV1` | `GAIN` | `100 kΩ` | 2-terminal variable resistor (rheostat) | Terminal 1 (`CCW`) → `IN_SUM`; Terminal 2 (`Wiper`) + Terminal 3 (`CW`) tied → `V_GAIN` |
| `RV2` | `ATK` | `50 kΩ` | 2-terminal variable resistor (rheostat) | Terminal 1 (`CCW`) → `RECT_DIODE_OUT`; Terminal 2 (`Wiper`) + Terminal 3 (`CW`) tied → `ENV_CAP` |
| `RV3` | `Release` | `1 MΩ` | 2-terminal variable resistor (rheostat) | Terminal 1 (`CCW`) → `REL_MID` (`R10`); Terminal 2 (`Wiper`) + Terminal 3 (`CW`) tied → `GND` |
| `RV4` | `OFFSET` | `100 kΩ` | 3-terminal potentiometer | Top (`1`) → `OFF_TOP` (`R11` to `+12V`); Bottom (`3`) → `OFF_BOT` (`R12` to `-12V`); Wiper (`2`) → `OFF_WIPER` (`R13`) *(see Section 6.4 for CW polarity)* |

### 3.6 Jacks & Power Connector

| Ref | Label | Type | Connections |
|---|---|---|---|
| `J1` | `IN` | 3.5 mm mono jack (2-pin shown) | Tip → `IN_TIP` (`C1`), Sleeve → `GND` *(if using a 3-pin switched jack like PJ398SM, leave switch pin `TN` open or ground it)* |
| `J2` | `OUT` | 3.5 mm mono jack (2-pin shown) | Tip ← `OUT_TIP` (`R16`), Sleeve → `GND` |
| `J3` | `INV_OUT` | 3.5 mm mono jack (2-pin shown) | Tip ← `INV_OUT_TIP` (`R19`), Sleeve → `GND` |
| `J4` | `PWR` | 3-rail power port (`+12V in`, `GND`, `-12V in`) | `+12V`, `GND`, `-12V` (e.g., standard 10-pin 2×5 Eurorack IDC header) |

---

## 4. Stage-by-Stage Circuit Description

### 4.1 Power Input & Bulk Filtering (`J4`, `C3`, `C4`)
- Three power input flags (`+12V in`, `GND`, `-12V in`) feed the global `+12V`, `GND`, and `-12V` rails.
- Two polarized `4.7 µF` electrolytic bulk capacitors decouple the rails to ground:
  - `C3`: `+` terminal to `+12V`, `-` terminal to `GND`.
  - `C4`: `+` terminal to `GND`, `-` terminal to `-12V` *(note polarity: `GND` is more positive than `-12V`)*.
- **Op-Amp Supply Connections:** Per the schematic note, all 6 op-amps are `TL074` or `TL072` devices powered by `Vcc+ = +12V` and `Vcc- = -12V`. Power pins are explicitly drawn on `U2B` (the LED buffer) and implied for `U1A`–`U1D` and `U2A`.

### 4.2 Stage 1 — AC Input Coupling & Gain (`J1`, `C1`, `R1`, `R2`, `RV1`, `U1A`)
- **Topology:** AC-coupled inverting amplifier.
- **Connections:**
  - `J1` Tip feeds `C1` (`4.7 µF`), blocking any DC offset on the incoming signal. `J1` Sleeve connects to `GND`.
  - After `C1`, `R1` (`1 MΩ`) references the node to `GND`, and `R2` (`10 kΩ`) feeds the inverting input (`-`) of `U1A`.
  - `U1A` non-inverting input (`+`) connects directly to `GND`.
  - `RV1` (`100 kΩ`, `GAIN`) is wired as a feedback rheostat from `U1A` `-` input to `U1A` output (with wiper tied to the output-side terminal).
- **Transfer Function:**
  $$V_{\text{gain}} = -\frac{R_{\text{GAIN}}}{10\,\text{k}\Omega} \cdot V_{\text{in,AC}}, \qquad \left|\frac{V_{\text{gain}}}{V_{\text{in,AC}}}\right| \in [0,\; 10]\;(0\text{ to }+20\text{ dB})$$
- **Input Impedance & Cutoff:** Because `U1A` `-` sits at virtual ground, `Z_in ≈ R1 || R2 = 1 MΩ || 10 kΩ ≈ 9.90 kΩ`, giving a high-pass `-3 dB` cutoff of `f_c = 1 / (2π · 9.90 kΩ · 4.7 µF) ≈ 3.42 Hz`.

### 4.3 Stage 2 — Precision Full-Wave Rectifier (`R3`–`R8`, `D1`, `D2`, `U1B`, `U1C`)
- **Topology:** Classic two-op-amp inverting precision full-wave rectifier producing a **positive-going** rectified waveform.
- **Half-Wave Stage (`U1B`):**
  - `R3` (`10 kΩ`) connects `V_GAIN` to `U1B` `-` input (`RECT_INV`), with `U1B` `+` grounded.
  - `D1` (`1N4148`) connects from `U1B` output (`Anode`) to `U1B` `-` input (`Cathode`).
  - `D2` (`1N4148`) connects from `RECT_MID` (`Anode`) to `U1B` output (`Cathode`).
  - `R4` (`10 kΩ`) provides feedback from `RECT_MID` back to `U1B` `-` input.
- **Summing Stage (`U1C`):**
  - Two series `10 kΩ` resistors (`R5` + `R6` = `20 kΩ`) feed `V_GAIN` directly to `U1C` `-` input (`SUM_INV`).
  - `R7` (`10 kΩ`) feeds `RECT_MID` into `U1C` `-` input (`SUM_INV`).
  - `U1C` `+` input is grounded; `R8` (`22 kΩ`) provides feedback from `U1C` output to `U1C` `-` input.
- **Circuit Operation:**
  - When `V_GAIN > 0`: `U1B` output swings negative, reverse-biasing `D1` and forward-biasing `D2`. Thus `V(RECT_MID) = -(10k/10k)·V_GAIN = -V_GAIN`. `U1C` sums `V_GAIN / 20k + (-V_GAIN) / 10k = -V_GAIN / 20k`, yielding `V_RECT = -22k · (-V_GAIN / 20k) = +1.1 · V_GAIN`.
  - When `V_GAIN < 0`: `U1B` output swings positive (`~+0.6 V`), forward-biasing `D1` and reverse-biasing `D2`. `R4` and `R7` tie `RECT_MID` between two `0 V` virtual grounds, so `V(RECT_MID) = 0 V`. `U1C` sums `V_GAIN / 20k + 0`, yielding `V_RECT = -22k · (V_GAIN / 20k) = -1.1 · V_GAIN = +1.1 · |V_GAIN|`.
  - Overall rectifier output: $V_{\text{RECT}} = +1.1\,\left|V_{\text{GAIN}}\right| \ge 0$.

### 4.4 Stage 3 — Attack / Release Envelope Detector (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)
- **Topology:** Unidirectional peak-charging diode followed by separate attack (`RV2`) and release (`R9` + `R10` + `RV3`) RC paths around `C2` (`1 µF`).
- **Connections:**
  - `D3` (`1N4148`) conducts when `V_RECT > V(ENV_CAP) + V_f` (`Anode` at `U1C` output, `Cathode` toward `RV2`). When `V_RECT` drops below the stored voltage, `D3` reverse-biases and prevents `C2` from discharging back into `U1C`.
  - `RV2` (`50 kΩ`, `ATK`) is wired as a rheostat from `D3` cathode to `ENV_CAP` (`C2` positive/top plate to `GND`).
  - `R9` (`1 kΩ`) connects `ENV_CAP` to the output/sensing node `ENV_RAW` (also tagged with the `LED` net flag).
  - From `ENV_RAW`, `R10` (`10 kΩ`) goes in series with `RV3` (`1 MΩ`, `Release`, wired as a rheostat) to `GND`.
- **Time Constants:**
  - **Attack:** $\tau_{\text{atk}} \approx R_{\text{ATK}} \cdot C_2 \in [\approx 0\text{ ms},\; 50\text{ ms}]$ (when $R_{\text{REL}} \gg R_{\text{ATK}}$; see Section 6.3 for interaction when `Release` is near minimum).
  - **Release:** $\tau_{\text{rel}} = (R_9 + R_{10} + R_{\text{REL}}) \cdot C_2 = (11\,\text{k}\Omega + R_{\text{REL}}) \cdot 1\,\mu\text{F} \in [11\text{ ms},\; 1.011\text{ s}]$.

### 4.5 Stage 4 — Output Gain, DC Offset & Inverted Output (`U1D`, `RV4`, `R11`–`R19`, `U2A`, `J2`, `J3`)
- **Non-Inverting Output & Offset Stage (`U1D`):**
  - `ENV_RAW` connects directly to `U1D` `+` input.
  - `RV4` (`100 kΩ`, `OFFSET`) sits between `R11` (`10 kΩ` to `+12V`) and `R12` (`10 kΩ` to `-12V`), producing an unloaded wiper Thevenin voltage $V_{\text{th}} \in [-10\text{ V},\; +10\text{ V}]$ with Thevenin source resistance $R_{\text{pot,th}} \in [9.17\text{ k}\Omega,\; 30\text{ k}\Omega]$ (maximum at midpoint).
  - `R13` (`10 kΩ`) feeds the `OFFSET` wiper into `U1D` `-` input (`OUT_INV_NODE`), which also connects to `GND` via `R14` (`10 kΩ`) and to `U1D` output via `R15` (`10 kΩ`).
  - Defining $R_{\text{off}} = 10\text{ k}\Omega + R_{\text{pot,th}}$ ($40\text{ k}\Omega$ at midpoint; $19.17\text{ k}\Omega$ at extremes):
    $$V_{\text{OUT\_BUF}} = \left(2 + \frac{10\text{ k}\Omega}{R_{\text{off}}}\right) V_{\text{ENV\_RAW}} - \left(\frac{10\text{ k}\Omega}{R_{\text{off}}}\right) V_{\text{th}}$$
    - **Center (`OFFSET` = 50%):** $V_{\text{OUT\_BUF}} = 2.25 \cdot V_{\text{ENV\_RAW}}$ (`0 V` DC offset).
    - **Top extreme (`+12V` side):** $V_{\text{OUT\_BUF}} \approx 2.52 \cdot V_{\text{ENV\_RAW}} - 5.22\text{ V}$.
    - **Bottom extreme (`-12V` side):** $V_{\text{OUT\_BUF}} \approx 2.52 \cdot V_{\text{ENV\_RAW}} + 5.22\text{ V}$.
  - `R16` (`1 kΩ`) feeds `V_OUT_BUF` to `J2` (`OUT`) Tip (`J2` Sleeve → `GND`).
- **Inverted Output Stage (`U2A`):**
  - `R17` (`10 kΩ`) feeds `V_OUT_BUF` into `U2A` `-` input (`U2A` `+` → `GND`), with `R18` (`10 kΩ`) feedback:
    $$V_{\text{INV\_BUF}} = -\frac{10\text{ k}\Omega}{10\text{ k}\Omega}\, V_{\text{OUT\_BUF}} = -V_{\text{OUT\_BUF}}$$
  - `R19` (`1 kΩ`) feeds `V_INV_BUF` to `J3` (`INV_OUT`) Tip (`J3` Sleeve → `GND`).

### 4.6 Stage 5 — LED Indicator Buffer & Negative Bias (`R20`–`R23`, `U2B`, `D4`)
- **Connections:**
  - The net labeled `LED` connects `ENV_RAW` through `R20` (`10 kΩ`) into `U2B` `+` input (`LED_BUF_IN`).
  - `U2B` is configured as a unity-gain voltage follower (`U2B` `-` connected directly to `U2B` output), preventing the LED current from loading the envelope timing network (`C2` / `Release`).
  - `U2B` output (`V_LED_DRV = V_ENV_RAW`) drives `R21` (`22 kΩ`) → `D4` (`LED`, `Anode` on `R21` side, `Cathode` on divider side).
  - `D4` cathode connects to `LED_BIAS`, set by `R22` (`10 kΩ` to `GND`) and `R23` (`33 kΩ` to `-12V`).
- **Bias Analysis:**
  - Open-circuit cathode bias voltage: $V_{\text{bias}} = -12\text{ V} \times \frac{10\text{ k}\Omega}{10\text{ k}\Omega + 33\text{ k}\Omega} = -2.79\text{ V}$, with Thevenin impedance $R_{\text{th}} = 10\text{ k}\Omega \parallel 33\text{ k}\Omega = 7.67\text{ k}\Omega$.
  - This negative bias shifts the LED turn-on knee down by `~2.79 V`, allowing even small positive envelope voltages above `0 V` to overcome `V_f` and illuminate the LED linearly (especially suited for green/blue/white LEDs with `V_f ≈ 2.8–3.0 V`).
  - LED current: $I_{\text{LED}} \approx \dfrac{V_{\text{ENV\_RAW}} + 2.79\text{ V} - V_f}{22\text{ k}\Omega + 7.67\text{ k}\Omega} = \dfrac{V_{\text{ENV\_RAW}} + 2.79\text{ V} - V_f}{29.67\text{ k}\Omega}$.

---

## 5. Complete Pin-for-Pin Netlist & IC Pin Mapping

### 5.1 Op-Amp IC Pin Assignment (`U1 = TL074`, `U2 = TL072`)

| IC & Unit | Function | `+` Input Pin (Net) | `-` Input Pin (Net) | Output Pin (Net) | Supply Pins |
|---|---|---|---|---|---|
| `U1A` (`TL074`) | Input Gain (`-0..-10×`) | Pin `3` (`GND`) | Pin `2` (`IN_SUM`) | Pin `1` (`V_GAIN`) | Pin `4` (`+12V`), Pin `11` (`-12V`) |
| `U1B` (`TL074`) | Precision Rectifier 1 | Pin `5` (`GND`) | Pin `6` (`RECT_INV`) | Pin `7` (`RECT_OP_OUT`) | Shared on `U1` |
| `U1C` (`TL074`) | Precision Rectifier 2 | Pin `10` (`GND`) | Pin `9` (`SUM_INV`) | Pin `8` (`V_RECT`) | Shared on `U1` |
| `U1D` (`TL074`) | Output Gain & Offset | Pin `12` (`ENV_RAW`) | Pin `13` (`OUT_INV_NODE`) | Pin `14` (`V_OUT_BUF`) | Shared on `U1` |
| `U2A` (`TL072`) | Inverted Output (`-1×`) | Pin `3` (`GND`) | Pin `2` (`INV_SUM`) | Pin `1` (`V_INV_BUF`) | Pin `8` (`+12V`), Pin `4` (`-12V`) |
| `U2B` (`TL072`) | LED Buffer (`+1×`) | Pin `5` (`LED_BUF_IN`) | Pin `6` (`V_LED_DRV`) | Pin `7` (`V_LED_DRV`) | Shared on `U2` |

*(If building with `3 × TL072` instead of `1 × TL074 + 1 × TL072`, note that `TL072` Pin `4` is `Vcc-` and Pin `8` is `Vcc+`, whereas `TL074` Pin `4` is `Vcc+` and Pin `11` is `Vcc-`.)*

### 5.2 Complete Net-by-Net Connectivity Table

Every component terminal in the circuit (`105` total pins) is listed below:

| Net Name | Connected Component Pins |
|---|---|
| **`+12V`** | `J4.+12V`, `C3.+`, `R11.1`, `U1.4` (`Vcc+`), `U2.8` (`Vcc+`) |
| **`-12V`** | `J4.-12V`, `C4.-`, `R12.1`, `R23.1`, `U1.11` (`Vcc-`), `U2.4` (`Vcc-`) |
| **`GND`** | `J4.GND`, `C3.-`, `C4.+`, `J1.Sleeve`, `R1.2`, `U1.3` (`U1A+`), `U1.5` (`U1B+`), `U1.10` (`U1C+`), `C2.2`, `RV3.2` (`Wiper`), `RV3.3` (`CW`), `R14.2`, `U2.3` (`U2A+`), `J2.Sleeve`, `J3.Sleeve`, `R22.2` |
| **`IN_TIP`** | `J1.Tip`, `C1.1` |
| **`IN_AC`** | `C1.2`, `R1.1`, `R2.1` |
| **`IN_SUM`** | `R2.2`, `U1.2` (`U1A-`), `RV1.1` (`GAIN`) |
| **`V_GAIN`** | `U1.1` (`U1A OUT`), `RV1.2` (`Wiper`), `RV1.3`, `R3.1`, `R5.1` |
| **`RECT_INV`** | `R3.2`, `U1.6` (`U1B-`), `R4.1`, `D1.K` |
| **`RECT_OP_OUT`** | `U1.7` (`U1B OUT`), `D1.A`, `D2.K` |
| **`RECT_MID`** | `D2.A`, `R4.2`, `R7.1` |
| **`RECT_FF_MID`** | `R5.2`, `R6.1` |
| **`SUM_INV`** | `R6.2`, `R7.2`, `U1.9` (`U1C-`), `R8.1` |
| **`V_RECT`** | `U1.8` (`U1C OUT`), `R8.2`, `D3.A` |
| **`RECT_DIODE_OUT`** | `D3.K`, `RV2.1` (`ATK`) |
| **`ENV_CAP`** | `RV2.2` (`Wiper`), `RV2.3`, `C2.1`, `R9.1` |
| **`ENV_RAW`** *(schematic label: `LED`)* | `R9.2`, `R10.1`, `U1.12` (`U1D+`), `R20.1` |
| **`REL_MID`** | `R10.2`, `RV3.1` (`Release`) |
| **`OFF_TOP`** | `R11.2`, `RV4.1` (`OFFSET`) |
| **`OFF_BOT`** | `R12.2`, `RV4.3` (`OFFSET`) |
| **`OFF_WIPER`** | `RV4.2` (`Wiper`), `R13.1` |
| **`OUT_INV_NODE`** | `R13.2`, `R14.1`, `R15.1`, `U1.13` (`U1D-`) |
| **`V_OUT_BUF`** | `U1.14` (`U1D OUT`), `R15.2`, `R16.1`, `R17.1` |
| **`OUT_TIP`** | `R16.2`, `J2.Tip` |
| **`INV_SUM`** | `R17.2`, `R18.1`, `U2.2` (`U2A-`) |
| **`V_INV_BUF`** | `U2.1` (`U2A OUT`), `R18.2`, `R19.1` |
| **`INV_OUT_TIP`** | `R19.2`, `J3.Tip` |
| **`LED_BUF_IN`** | `R20.2`, `U2.5` (`U2B+`) |
| **`V_LED_DRV`** | `U2.6` (`U2B-`), `U2.7` (`U2B OUT`), `R21.1` |
| **`LED_A`** | `R21.2`, `D4.A` |
| **`LED_BIAS`** | `D4.K`, `R22.1`, `R23.2` |

---

## 6. Practical Build & Verification Notes

### 6.1 Additions Recommended for Reliable Hardware Builds (Not Drawn in Source)
1. **Local IC Decoupling (`C5`–`C8`):** Add a `100 nF` (`0.1 µF`, ≥ 25 V X7R ceramic) capacitor from `+12V` to `GND` and from `-12V` to `GND` directly at the power pins of **each** op-amp IC (`U1` and `U2`) to prevent oscillation/noise.
2. **Power Reverse-Polarity / Inrush Protection:** If building for Eurorack with a standard 2×5 IDC header (`J4`), consider adding series Schottky diodes (e.g., `1N5819`) or `10 Ω` current-limiting resistors on `+12V in` and `-12V in` upstream of `C3`/`C4` to protect `U1` and `U2` against reversed power cables.
3. **Capacitor Selection (`C1`, `C2`):** Both `C1` (`4.7 µF`) and `C2` (`1 µF`) are drawn as non-polarized capacitors. Avoid standard polarized electrolytic capacitors for `C2` (leakage current degrades long `Release` times) and for `C1` (AC signal swings both positive and negative around `0 V`). Film or ceramic X7R (≥ 25 V) for `1 µF` (`C2`) and film or bipolar electrolytic (`BP`/`NP`) for `4.7 µF` (`C1`) are ideal.

### 6.2 Input Impedance & Signal Levels
- Because `R2` (`10 kΩ`) terminates into `U1A`'s virtual ground, the input impedance is `~9.9 kΩ`. This works cleanly with modular/synth line and Eurorack outputs (`~1 kΩ` source impedance), and `GAIN` up to `10×` accommodates quiet line-level signals (`~0.5–1 Vpp`). High-impedance passive pickups (e.g., electric guitar) will experience treble/level loss unless preceded by a high-Z buffer.
- Because `D3` (`1N4148`) sits outside `U1C`'s feedback loop, signals whose rectified amplitude `1.1 · |V_gain|` stays below `~0.6 V` will not charge `C2`. Turn `GAIN` up so peak signal amplitude after `U1A`/`U1C` comfortably exceeds `~0.6 V` (`1 V` to `10 V` peak).

### 6.3 Attack / Release Control Interaction
- When `ATK` (`RV2`) is set high (`~50 kΩ`) **and** `Release` (`RV3`) is set near minimum (`0 Ω`), `RV2` (`50 kΩ`) and `R9 + R10` (`11 kΩ`) form a voltage divider during charging (`11k / (50k + 11k) ≈ 0.18`), which limits peak envelope voltage on `C2` unless `Release` is increased or `GAIN` is raised. This is normal behavior for passive diode-resistor AR envelope followers.

### 6.4 Potentiometer Rotation Direction (`GAIN`, `ATK`, `Release`, `OFFSET`)
Looking at the front of a standard rotary potentiometer with pins pointing down (`1 = CCW`, `2 = Wiper`, `3 = CW`):
- **`GAIN` (`RV1`), `ATK` (`RV2`), `Release` (`RV3`):** Wiring Pin `1` (`CCW`) to one circuit node and tying Pins `2 + 3` (`Wiper + CW`) to the other gives `0 Ω` at full CCW and maximum resistance (`100 kΩ` / `50 kΩ` / `1 MΩ`) at full CW (clockwise = more gain, slower attack, slower release). If you prefer clockwise = *faster* attack on `ATK`, tie Pins `1 + 2` together instead.
- **`OFFSET` (`RV4`):** Because the wiper feeds the **inverting** input (`-`) of `U1D`, turning the wiper toward `+12V` shifts `OUT` **negative** (and `INV_OUT` positive), while turning toward `-12V` shifts `OUT` **positive**.
  - To make **clockwise = more positive `OUT`**: wire Pin `1` (`CCW`) to `OFF_TOP` (`R11` → `+12V`) and Pin `3` (`CW`) to `OFF_BOT` (`R12` → `-12V`).
  - To make **clockwise = more negative `OUT` / positive `INV_OUT`**: wire Pin `1` (`CCW`) to `OFF_BOT` (`-12V`) and Pin `3` (`CW`) to `OFF_TOP` (`+12V`).

### 6.5 LED Brightness & Threshold (`D4`, `R21`–`R23`)
- With `R21 = 22 kΩ`, `R22 = 10 kΩ`, and `R23 = 33 kΩ`, the LED forward current is relatively low (`~0.33 mA` at `V_ENV_RAW = +10 V`, `~0.16 mA` at `+5 V` for a `2.9 V` green/blue LED). Use a **high-brightness / high-efficiency LED** so it remains clearly visible at sub-milliamp current.
- At idle (`V_ENV_RAW = 0 V`), the cathode sits at `-2.79 V`:
  - A **green, blue, or white LED** (`V_f ≈ 2.8–3.2 V`) stays completely off at `0 V` and lights promptly as soon as `V_ENV_RAW` rises above `~0.1–0.4 V`.
  - A **red or amber LED** (`V_f ≈ 1.8–2.0 V`) has `~30 µA` trickle current at `0 V` (usually invisible or a very faint glow; if unwanted, adjust `R23` upward slightly, e.g., `47 kΩ`, so `V_bias ≈ -2.1 V`).

### 6.6 Bring-Up & Bench Test Procedure
1. **Unpowered continuity check:** Verify no shorts between `+12V`, `GND`, and `-12V`. Confirm polarity of `C3`, `C4`, `D1`, `D2`, `D3`, and `D4` (`LED`).
2. **Power-up (no input, `U1`/`U2` installed):**
   - Measure `+12 V` and `-12 V` at `U1` pins `4`/`11` and `U2` pins `8`/`4`.
   - With `IN` unplugged (`GND`), verify `U1A` out (`pin 1`), `U1B` out (`pin 7` ≈ `0 V`), `U1C` out (`pin 8` ≈ `0 V`), and `ENV_RAW` (`≈ 0 V`).
   - Adjust `OFFSET` (`RV4`) through its full sweep and verify `OUT` (`J2` Tip) sweeps smoothly between roughly `-5.2 V` and `+5.2 V`, and `INV_OUT` (`J3` Tip) tracks at `-OUT`. Center `OFFSET` so `OUT ≈ 0.0 V`.
3. **Dynamic envelope test:**
   - Set `GAIN` (`RV1`) to ~50%, `ATK` (`RV2`) to ~10% (fast), `Release` (`RV3`) to ~30%.
   - Inject a `1 kHz`, `2 Vpp` sine wave into `IN` (`J1`).
   - Verify `U1A` out (`pin 1`) shows an inverted amplified sine wave (`~10 Vpp` at 50% linear pot), `U1C` out (`pin 8`) shows a positive full-wave rectified waveform (`~5.5 V` peak), `OUT` (`J2`) outputs a steady positive DC envelope (`~+10 V` capped near op-amp headroom if `GAIN` is high), `INV_OUT` (`J3`) outputs the negative mirror (`~-10 V`), and `LED` (`D4`) lights brightly.
   - Gate/burst the sine wave on and off and confirm `ATK` slows the rising edge and `Release` extends the falling tail up to several seconds.
