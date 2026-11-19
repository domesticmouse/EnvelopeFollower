# Envelope Follower — Extracted Circuit Description

> **Source:** `EnvelopeFollower.webp` (hand-drawn schematic titled *Envelope Follower*, dated `2022年1月18日 22:58`)  
> **Supply Rails:** Dual ±12 V Eurorack power (`Vcc+ = +12V`, `Vcc- = -12V`, `GND`)  
> **Op-Amps:** `TL074` or `TL072` (6 op-amp stages total; e.g., `1x TL074` + `1x TL072` or `3x TL072`)

---

## 1. Functional Overview

This module is a dual-rail (±12 V) analog **Envelope Follower** for Eurorack audio/CV signals. It converts an AC-coupled input signal into a smooth unipolar positive envelope voltage, adds a bipolar DC offset control, and provides both normal (`OUT`) and inverted (`INV_OUT`) outputs plus a buffered LED activity indicator driven by the raw (pre-offset) envelope.

### Signal Flow

```text
IN ──► [AC Coupling + GAIN Preamp (U1A)]
           ├──► [Feedforward 10k+10k] ──────────────────┐
           └──► [Precision Half-Wave Rectifier (U1B)] ──┴──► [Full-Wave Summer (U1C)]
                                                                    │
                                                            [D3 Peak Diode]
                                                                    │
                                                    [ATK 50k] ──┬── [1k] ── ENV_RAW
                                                                │             ├──► [Release 10k + 1M] ── GND
                                                                │             ├──► [LED Buffer (U2B)] ──► LED
                                                                ▼             └──► [Offset Buffer/Summer (U1D)]
                                                            [C2 1µF]                     ├──► [1k] ──► OUT
                                                                                         └──► [Inverter (U2A)] ──► [1k] ──► INV_OUT
```

---

## 2. Bill of Materials (BOM)

*Note: Reference designators (`R1`–`R23`, `C1`–`C4`, `D1`–`D4`, `RV1`–`RV4`, `U1`–`U2`, `J1`–`J3`) are assigned here for unambiguous netlisting and assembly; they are not printed on `EnvelopeFollower.webp`.*

### Integrated Circuits
| RefDes | Value / Part | Qty | Notes |
|---|---|---|---|
| `U1` | `TL074` (Quad Op-Amp) | 1 | Units `U1A`–`U1D` (or substitute `2x TL072`; schematic specifies `TL074 or TL072`) |
| `U2` | `TL072` (Dual Op-Amp) | 1 | Units `U2A`–`U2B` (or substitute `1x TL074` leaving 2 spare stages; see Section 6) |

### Diodes & Indicator LED
| RefDes | Value / Part | Qty | Notes |
|---|---|---|---|
| `D1`, `D2`, `D3` | `1N4148` | 3 | Small-signal switching diodes (full-wave rectifier & peak detector) |
| `D4` | `LED` | 1 | Envelope level indicator (color/package not specified in schematic) |

### Capacitors
| RefDes | Value | Qty | Type (per Schematic Symbol) | Notes |
|---|---|---|---|---|
| `C1` | `4.7 µF` | 1 | Non-polarized | Input AC coupling capacitor (audio input is bipolar around 0 V) |
| `C2` | `1 µF` | 1 | Non-polarized | Envelope hold/smoothing capacitor (film or low-leakage MLCC recommended) |
| `C3`, `C4` | `4.7 µF` | 2 | Polarized electrolytic | Power rail bulk decoupling (`+12V` to `GND`, `GND` to `-12V`) |

### Resistors
| Value | Qty | RefDes |
|---|---|---|
| `1k` | 3 | `R9`, `R16`, `R19` |
| `10k` | 16 | `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R10`, `R11`, `R12`, `R13`, `R14`, `R15`, `R17`, `R18`, `R20`, `R22` |
| `22k` | 2 | `R8`, `R21` |
| `33k` | 1 | `R23` |
| `1M` | 1 | `R1` |

*Total resistors: **23***

### Potentiometers
| RefDes | Label | Value | Qty | Configuration |
|---|---|---|---|---|
| `RV1` | `GAIN` | `100k` | 1 | 2-terminal variable resistor (rheostat) |
| `RV2` | `ATK` | `50k` | 1 | 2-terminal variable resistor (rheostat) |
| `RV3` | `Release` | `1M` | 1 | 2-terminal variable resistor (rheostat) |
| `RV4` | `OFFSET` | `100k` | 1 | 3-terminal voltage divider potentiometer |

### Jacks & Power Ports
| RefDes | Label | Qty | Notes |
|---|---|---|---|
| `J1` | `IN` | 1 | 3.5 mm mono audio/CV input jack (Tip = signal, Sleeve = `GND`) |
| `J2` | `OUT` | 1 | 3.5 mm mono envelope output jack (Tip = signal, Sleeve = `GND`) |
| `J3` | `INV_OUT` | 1 | 3.5 mm mono inverted envelope output jack (Tip = signal, Sleeve = `GND`) |
| `J_PWR` | `+12Vin`, `GND`, `-12Vin` | 1 | Power input connections (shown as three port flags in schematic) |

---

## 3. Stage-by-Stage Circuit Description

### 3.1 Power Supply & Bulk Decoupling
- Three power input ports are labeled **`+12Vin`**, **`GND`**, and **`-12Vin`**.
- **`C3` (`4.7 µF`, polarized):** `+` terminal to `+12V`, `-` terminal to `GND`.
- **`C4` (`4.7 µF`, polarized):** `+` terminal to `GND`, `-` terminal to `-12V`.
- **Global Op-Amp Rails:** Per the schematic note, all op-amp stages use `Vcc+ = +12V` and `Vcc- = -12V` (explicitly drawn on `U2B`, implied for `U1A`–`U1D` and `U2A`).

### 3.2 Input AC Coupling & Variable-Gain Preamp (`U1A`)
- Input jack `J1` (`IN`) feeds `C1` (`4.7 µF`, non-polarized) in series to node `IN_AC`.
- `R1` (`1M`) pulls `IN_AC` to `GND`.
- `R2` (`10k`) feeds `IN_AC` into the inverting input (`-`) of `U1A`; `U1A` non-inverting input (`+`) connects to `GND`.
- `RV1` (`100k`, labeled `GAIN`) is wired as a rheostat in `U1A` feedback: one end terminal connects to `U1A` `-` input, and the wiper is tied to the other end terminal at `U1A` output (`PREAMP_OUT`).
- **Behavior:** Inverting amplifier with gain $A_v = -R_{\text{RV1}} / 10\,\text{k}\Omega$ (adjustable from `0` to `-10x`), and high-pass corner $f_c \approx 3.4\,\text{Hz}$ (set by `C1 = 4.7 µF` into `R1 || R2 ≈ 9.9 kΩ`).

### 3.3 Precision Full-Wave Rectifier (`U1B`, `U1C`, `D1`, `D2`)
- **Half-Wave Stage (`U1B`):**
  - `R3` (`10k`) connects `PREAMP_OUT` to `U1B` `-` input; `U1B` `+` input connects to `GND`.
  - `D1` (`1N4148`): **Anode** to `U1B` output (`U1B_OUT`), **Cathode** to `U1B` `-` input.
  - `D2` (`1N4148`): **Cathode** to `U1B` output (`U1B_OUT`), **Anode** to node `HALF_WAVE`.
  - `R6` (`10k`) connects between `U1B` `-` input and `HALF_WAVE`.
- **Summing Stage (`U1C`):**
  - `R7` (`10k`) connects `HALF_WAVE` to `U1C` `-` input.
  - Feedforward path: `R4` (`10k`) and `R5` (`10k`) in series (`20k` total) connect `PREAMP_OUT` directly to `U1C` `-` input.
  - `U1C` `+` input connects to `GND`.
  - `R8` (`22k`) provides feedback from `U1C` output (`RECT_OUT`) to `U1C` `-` input.
- **Behavior:**
  - For $V_{\text{PREAMP\_OUT}} > 0$: `D1` is off, `D2` conducts, $V_{\text{HALF\_WAVE}} = -V_{\text{PREAMP\_OUT}}$, and summing current $(V/20\text{k} - V/10\text{k}) = -V/20\text{k}$ yields $V_{\text{RECT\_OUT}} = +\frac{22\text{k}}{20\text{k}} V_{\text{PREAMP\_OUT}} = +1.1\,V_{\text{PREAMP\_OUT}}$.
  - For $V_{\text{PREAMP\_OUT}} < 0$: `D1` conducts (clamping `U1B_OUT` at $\approx +0.6\text{V}$), `D2` is off ($V_{\text{HALF\_WAVE}} = 0\text{V}$), and current $V/20\text{k}$ yields $V_{\text{RECT\_OUT}} = +1.1\,|V_{\text{PREAMP\_OUT}}|$.
  - Result at `RECT_OUT` is a positive unipolar full-wave rectified signal.

### 3.4 Peak Detector & Attack/Release Filter (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)
- `D3` (`1N4148`): **Anode** to `U1C` output (`RECT_OUT`), **Cathode** to `PEAK_DET`.
- `RV2` (`50k`, labeled `ATK`) is wired as a rheostat between `PEAK_DET` (one end lug) and `ENV_CAP` (wiper tied to the other end lug).
- `C2` (`1 µF`, non-polarized) connects from `ENV_CAP` to `GND`.
- `R9` (`1k`) connects `ENV_CAP` to node `ENV_RAW`.
- Release path from `ENV_RAW` to `GND`: `R10` (`10k`) in series with `RV3` (`1M`, labeled `Release`), where `RV3` has one end lug to `R10` and its wiper tied to the other end lug at `GND`.
- **Behavior:**
  - Attack time constant: $\tau_{\text{atk}} \approx R_{\text{RV2}} \cdot 1\,\mu\text{F} \approx 0\text{ to }50\,\text{ms}$.
  - Release time constant: $\tau_{\text{rel}} = (1\,\text{k}\Omega + 10\,\text{k}\Omega + R_{\text{RV3}}) \cdot 1\,\mu\text{F} \approx 11\,\text{ms}\text{ to }1.011\,\text{s}$.

### 3.5 Envelope Buffer & Bipolar DC Offset Stage (`U1D`, `RV4`)
- `U1D` `+` input connects directly to `ENV_RAW`.
- **Offset Divider:**
  - `R11` (`10k`) from `+12V` to top lug of `RV4` (`100k`, labeled `OFFSET`).
  - `R12` (`10k`) from bottom lug of `RV4` to `-12V`.
  - `RV4` wiper (`OFF_WIPER`) spans approximately `-10V` to `+10V` unloaded.
- **Offset Summing & Gain Network on `U1D` `-` input:**
  - `R13` (`10k`) connects `OFF_WIPER` to `U1D` `-` input.
  - `R14` (`10k`) connects `U1D` `-` input to `GND`.
  - `R15` (`10k`) connects `U1D` output (`ENV_OUT`) back to `U1D` `-` input.
- **Behavior:**
  - At `ENV_RAW = 0 V`, `U1D` acts as an inverting stage for the loaded `OFFSET` divider, shifting `ENV_OUT` across roughly `-5.2 V` to `+5.2 V` (inverted relative to `OFF_WIPER`).
  - Non-inverting gain for `ENV_RAW` is $1 + \frac{R_{15}}{R_{14} \parallel (R_{13} + R_{\text{wiper,th}})}$, ranging from $\approx 2.25\times$ (pot centered) to $\approx 2.52\times$ (pot extremes).

### 3.6 Outputs (`J2` `OUT`, `U2A`, `J3` `INV_OUT`)
- **Normal Output (`OUT`):** `ENV_OUT` passes through `R16` (`1k`) to Tip of `J2` (`OUT`); Sleeve connects to `GND`.
- **Inverted Output (`INV_OUT`):**
  - `R17` (`10k`) connects `ENV_OUT` to `U2A` `-` input; `U2A` `+` input connects to `GND`.
  - `R18` (`10k`) connects `U2A` output (`INV_DRV`) back to `U2A` `-` input (unity-gain inverter, $A_v = -1$).
  - `INV_DRV` passes through `R19` (`1k`) to Tip of `J3` (`INV_OUT`); Sleeve connects to `GND`.

### 3.7 LED Indicator Driver (`U2B`, `D4`)
- Net flag `LED` taps `ENV_RAW` (before the `OFFSET` stage).
- `R20` (`10k`) connects `LED` (`ENV_RAW`) to `U2B` `+` input.
- `U2B` `-` input connects directly to `U2B` output (`U2B_OUT`), forming a unity-gain voltage follower.
- `R21` (`22k`) connects `U2B_OUT` to **Anode** of `D4` (`LED`).
- **Cathode** of `D4` (`LED_BIAS`) connects to a resistor divider formed by `R22` (`10k` to `GND`) and `R23` (`33k` to `-12V`).
- **Behavior:** The cathode divider pre-biases the LED cathode at $-12\,\text{V} \cdot \frac{10\text{k}}{10\text{k}+33\text{k}} \approx -2.79\,\text{V}$ (Thevenin resistance $\approx 7.67\,\text{k}\Omega$), offsetting the LED forward-voltage drop so small positive envelopes above `0 V` can illuminate the LED (with low sub-mA current due to `R21 = 22k`).

---

## 4. Complete Netlist (Net-by-Net Pin Connections)

Every physical connection in `EnvelopeFollower.webp` is listed below. Potentiometer lugs are denoted `L1` (one end), `W` (wiper), and `L2` (other end); diode pins are `A` (anode) and `K` (cathode); polarized capacitor pins are `+` and `-`; non-polarized passive pins are `1` and `2`; jack pins are `T` (tip) and `S` (sleeve).

| Net Name | Connected Component Pins |
|---|---|
| **`+12V`** *(also `+12`, `+12Vin`)* | `J_PWR.+12Vin`, `C3.+`, `R11.1`, `U1.V+`, `U2.V+` *(and any additional op-amp IC `V+`)* |
| **`-12V`** *(also `-12Vin`)* | `J_PWR.-12Vin`, `C4.-`, `R12.2`, `R23.2`, `U1.V-`, `U2.V-` *(and any additional op-amp IC `V-`)* |
| **`GND`** | `J_PWR.GND`, `C3.-`, `C4.+`, `J1.S`, `R1.2`, `U1A.IN+`, `U1B.IN+`, `U1C.IN+`, `C2.2`, `RV3.W`, `RV3.L2`, `R14.2`, `J2.S`, `U2A.IN+`, `J3.S`, `R22.2` |
| **`IN_JACK`** | `J1.T`, `C1.1` |
| **`IN_AC`** | `C1.2`, `R1.1`, `R2.1` |
| **`PREAMP_INV`** | `R2.2`, `U1A.IN-`, `RV1.L1` |
| **`PREAMP_OUT`** | `U1A.OUT`, `RV1.W`, `RV1.L2`, `R3.1`, `R4.1` |
| **`RECT_FF_MID`** | `R4.2`, `R5.1` |
| **`RECT_INV`** | `R3.2`, `U1B.IN-`, `D1.K`, `R6.1` |
| **`U1B_OUT`** | `U1B.OUT`, `D1.A`, `D2.K` |
| **`HALF_WAVE`** | `D2.A`, `R6.2`, `R7.1` |
| **`SUM_INV`** | `R5.2`, `R7.2`, `U1C.IN-`, `R8.1` |
| **`RECT_OUT`** | `U1C.OUT`, `R8.2`, `D3.A` |
| **`PEAK_DET`** | `D3.K`, `RV2.L1` |
| **`ENV_CAP`** | `RV2.W`, `RV2.L2`, `C2.1`, `R9.1` |
| **`ENV_RAW`** *(also `LED` net flag)* | `R9.2`, `R10.1`, `U1D.IN+`, `R20.1` |
| **`REL_MID`** | `R10.2`, `RV3.L1` |
| **`OFF_TOP`** | `R11.2`, `RV4.L1` |
| **`OFF_BOT`** | `R12.1`, `RV4.L2` |
| **`OFF_WIPER`** | `RV4.W`, `R13.1` |
| **`BUF_INV`** | `R13.2`, `R14.1`, `R15.1`, `U1D.IN-` |
| **`ENV_OUT`** | `U1D.OUT`, `R15.2`, `R16.1`, `R17.1` |
| **`OUT_JACK`** | `R16.2`, `J2.T` |
| **`INV_SUM`** | `R17.2`, `R18.1`, `U2A.IN-` |
| **`INV_DRV`** | `U2A.OUT`, `R18.2`, `R19.1` |
| **`INV_OUT_JACK`** | `R19.2`, `J3.T` |
| **`LED_IN`** | `R20.2`, `U2B.IN+` |
| **`U2B_OUT`** | `U2B.OUT`, `U2B.IN-`, `R21.1` |
| **`LED_DRV`** | `R21.2`, `D4.A` |
| **`LED_BIAS`** | `D4.K`, `R22.1`, `R23.1` |

---

## 5. Reference IC Pin Mapping (1× `TL074` + 1× `TL072`)

If building with one `TL074` (`U1`) and one `TL072` (`U2`), standard DIP-14 / SOIC-14 and DIP-8 / SOIC-8 pinouts map as follows:

| Unit | Function | `IN+` Pin | `IN-` Pin | `OUT` Pin | `V+` (`+12V`) | `V-` (`-12V`) |
|---|---|---|---|---|---|---|
| `U1A` (`TL074`) | Input Preamp (`GAIN`) | 3 | 2 | 1 | 4 | 11 |
| `U1B` (`TL074`) | Half-Wave Rectifier | 5 | 6 | 7 | 4 | 11 |
| `U1C` (`TL074`) | Full-Wave Summing Amp | 10 | 9 | 8 | 4 | 11 |
| `U1D` (`TL074`) | Envelope Buffer & Offset | 12 | 13 | 14 | 4 | 11 |
| `U2A` (`TL072`) | `INV_OUT` Inverter | 3 | 2 | 1 | 8 | 4 |
| `U2B` (`TL072`) | `LED` Buffer | 5 | 6 | 7 | 8 | 4 |

*(If building with `3x TL072` instead, each `TL072` uses pins 3/2/1 for Unit A, 5/6/7 for Unit B, pin 8 for `+12V`, and pin 4 for `-12V`. If building with `2x TL074`, terminate the 2 unused op-amps as unity-gain followers with `IN+` tied to `GND`.)*

---

## 6. Ambiguities, Unspecified Details & Practical Build Notes

The schematic values and connections in `EnvelopeFollower.webp` are crisp and legible, but the following physical/implementation details are **not specified** in the drawing and require design decisions when building:

1. **Op-Amp IC Count & Supply Pin Notation:**
   - The note specifies `All op-amp: TL074 or TL072`, and `Vcc+ is +12V. Vcc- is -12V.`
   - There are 6 op-amp stages total (`1x TL074 + 1x TL072` or `3x TL072` fills all 6 with zero unused gates; `2x TL074` leaves 2 unused gates that should be safely tied off).
   - Power supply pins (`+12V`, `-12V`) are drawn explicitly only on `U2B`, though the blue note applies them to all op-amps.
   - Local `100 nF` ceramic bypass capacitors at each IC's `V+`/`V-` pins are not shown in the schematic, though adding them (`+12V` to `GND` and `-12V` to `GND` close to each IC) is standard Eurorack PCB practice.

2. **Eurorack Power Header & Protection:**
   - The schematic shows three terminal flags (`+12Vin`, `GND`, `-12Vin`) rather than a standard 10-pin (`2x5`) or 16-pin (`2x8`) Eurorack IDC power header, reverse-polarity protection diodes, or `10 Ω` current-limiting resistors.

3. **3.5 mm Jack Switching Contacts:**
   - `IN`, `OUT`, and `INV_OUT` are drawn as 2-pin Tip/Sleeve symbols (`Sleeve` to `GND`). When using 3-pin Eurorack switched jacks (e.g., Thonkiconn `PJ398SM`), `IN` may optionally wire its tip-normalled switch pin (`TN`) to `GND` so an unpatched input is quiet, whereas `OUT` and `INV_OUT` must leave `TN` unconnected.

4. **Potentiometer Taper & Clockwise Direction:**
   - Tapers (`B` linear vs `A` audio/log) are not specified for `GAIN` (`100k`), `ATK` (`50k`), `Release` (`1M`), or `OFFSET` (`100k`).
   - For the three rheostats (`GAIN`, `ATK`, `Release`), connecting Pin 1 (CCW) to one terminal and Pins 2+3 (Wiper + CW) to the other causes resistance (and thus gain, attack time, or release time) to **increase** when turned clockwise; swapping Pin 1 and Pin 3 reverses this direction.
   - For `OFFSET` (`RV4`), because `U1D` inverts the `OFFSET` wiper voltage, connecting `+12V` side (`R11`) to Pin 3 (CW) and `-12V` side (`R12`) to Pin 1 (CCW) causes `OUT` DC offset to move **negative** as you turn CW (and `INV_OUT` positive); swap `R11`/`R12` between Pin 1 and Pin 3 if you want `OUT` offset to increase positively when turned CW.

5. **LED Brightness & Current (`R21 = 22k`):**
   - `R21` clearly reads `22k` (not `2.2k`). Combined with the `-2.79 V` (`7.67 kΩ` Thevenin) cathode bias (`R22 = 10k`, `R23 = 33k`), LED current at `+10 V` envelope is only `~0.36 mA` (assuming $V_F \approx 2\,\text{V}$). This works well with a high-efficiency/ultrabright LED; for standard low-efficiency LEDs, a lower `R21` value (e.g. `2.2k`–`4.7k`) may be preferred during breadboarding.

6. **Feedforward Sum Resistors (`10k + 10k` vs `22k`):**
   - The feedforward path deliberately uses two `10k` resistors in series (`R4 + R5 = 20k`), while `U1C` feedback uses `R8 = 22k`, giving a rectifier gain of `1.1x` rather than `1.0x` (likely to stay with standard E12 resistor values).
