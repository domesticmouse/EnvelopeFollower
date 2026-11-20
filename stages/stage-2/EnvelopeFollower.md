# Envelope Follower Circuit Description

Extracted from [`EnvelopeFollower.webp`](./EnvelopeFollower.webp) (sketch dated `2022年1月18日 22:58`).

---

## 1. Overview & Electrical Summary

This circuit is a **±12 V Eurorack-style analog envelope follower** built around **6 JFET-input op-amp stages** (`TL074` / `TL072`). It AC-couples an audio or CV input signal, applies adjustable inverting gain, performs precision full-wave rectification, extracts a positive-going amplitude envelope with independent Attack and Release controls, adds an adjustable DC offset, drives both non-inverted (`OUT`) and inverted (`INV_OUT`) outputs, and drives a buffered envelope `LED` indicator.

| Parameter | Specification / Behavior |
|---|---|
| **Power Supply** | Dual rail: `+12V`, `GND`, `-12V` (`Vcc+ = +12V`, `Vcc- = -12V`) |
| **Op-Amps** | `TL074` (quad) or `TL072` (dual); **6 op-amp stages** total |
| **Input (`IN`)** | AC-coupled ($f_c \approx 0.034\text{ Hz}$), $Z_{\text{in}} \approx 9.9\text{ k}\Omega$ |
| **Preamp Gain (`GAIN`)** | Inverting, $A_v = 0\text{ to }-10\times$ ($\text{up to } +20\text{ dB}$) via `100 kΩ` rheostat (`RV1`) |
| **Rectifier** | 2-op-amp precision full-wave rectifier, output $V_{\text{RECT}} = +1.1 \cdot |V_{\text{PREAMP}}|$ |
| **Attack Time (`ATK`)** | $\tau_{\text{atk}} \approx R_{\text{ATK}} \cdot 1\,\mu\text{F} \approx 0\text{ to }50\text{ ms}$ (`50 kΩ` rheostat `RV2`) |
| **Release Time (`Release`)** | $\tau_{\text{rel}} = (1\text{ k}\Omega + 10\text{ k}\Omega + R_{\text{REL}}) \cdot 1\,\mu\text{F} \approx 11\text{ ms to }1.01\text{ s}$ (`1 MΩ` rheostat `RV3`) |
| **DC Offset (`OFFSET`)** | `100 kΩ` pot (`RV4`) spanned between $\pm 10\text{ V}$ via `10 kΩ` end resistors, summed into `U1D` inverting input ($\approx \pm 5.2\text{ V}$ output shift) |
| **Outputs** | `OUT` and `INV_OUT` ($1\text{ k}\Omega$ series output resistors, $V_{\text{INV\_OUT}} = -V_{\text{OUT}}$) |
| **Indicator** | Buffered `LED` driven via `22 kΩ`, cathode biased to $\approx -2.79\text{ V}$ via `10 kΩ` / `33 kΩ` divider |

---

## 2. Bill of Materials (Exact Schematic Component Counts)

> Reference designators (`R1`–`R23`, `RV1`–`RV4`, `C1`–`C4`, `D1`–`D4`, `U1`–`U2`, `J1`–`J4`) are assigned here so every part maps unambiguously to the netlist below.

### 2.1 Integrated Circuits (6 Op-Amp Sections Total)

The schematic notes: *"All op-amp: TL074 or TL072 / Vcc+ is +12V. / Vcc- is -12V."*

| Package Option | ICs Required | Sections Used | Notes |
|---|---|---|---|
| **Option A (Canonical in Netlist)** | `1 × TL074` (`U1`) + `1 × TL072` (`U2`) | 4 + 2 = 6 | Exact fit; zero unused op-amps |
| **Option B** | `3 × TL072` | 2 + 2 + 2 = 6 | Exact fit; zero unused op-amps |
| **Option C** | `2 × TL074` | 4 + 4 = 8 (6 used) | Terminate the 2 unused op-amps cleanly (e.g., tie `+` to `GND`, `-` to `OUT`) |

### 2.2 Fixed Resistors (23 Total)

| Value | Qty | Reference Designators | Circuit Locations |
|---|---|---|---|
| **1 kΩ** | **3** | `R9`, `R16`, `R19` | `R9`: Attack/Release series isolation (`1 µF` node to `ENV_NODE`); `R16`: `OUT` series resistor; `R19`: `INV_OUT` series resistor |
| **10 kΩ** | **16** | `R2`–`R7`, `R10`–`R15`, `R17`–`R18`, `R20`, `R22` | `R2`: `U1A` input; `R3`: `U1B` input; `R4`+`R5`: two in series (`20 kΩ`) feedforward; `R6`: `U1B` feedback; `R7`: `U1C` rectifier summing input; `R10`: `Release` minimum series; `R11`/`R12`: `OFFSET` rail resistors; `R13`: `OFFSET` summing input; `R14`: `U1D` `-` to `GND`; `R15`: `U1D` feedback; `R17`: `U2A` input; `R18`: `U2A` feedback; `R20`: `U2B` LED buffer input; `R22`: LED cathode bias to `GND` |
| **22 kΩ** | **2** | `R8`, `R21` | `R8`: `U1C` summing amplifier feedback; `R21`: `U2B` LED current-limiting resistor |
| **33 kΩ** | **1** | `R23` | `R23`: LED cathode bias divider to `-12V` |
| **1 MΩ** | **1** | `R1` | `R1`: Input AC-coupling DC pull-down to `GND` |

### 2.3 Potentiometers (4 Total)

| Ref | Schematic Label | Value | Wiring Style | Function |
|---|---|---|---|---|
| `RV1` | `GAIN` | **100 kΩ** | 2-terminal rheostat (Pin 1 to `U1A_INV`; Pins 2+3 tied to `PREAMP_OUT`) | Input preamp gain ($0\text{ to }-10\times$) |
| `RV2` | `ATK` | **50 kΩ** | 2-terminal rheostat (Pin 1 to `D3` cathode; Pins 2+3 tied to `ENV_CAP`) | Attack slew/charge time |
| `RV3` | `Release` | **1 MΩ** | 2-terminal rheostat (Pin 1 to `R10`; Pins 2+3 tied to `GND`) | Release decay time |
| `RV4` | `OFFSET` | **100 kΩ** | 3-terminal voltage divider (`R11` to Pin 1, `R12` to Pin 3, Wiper Pin 2 to `R13`) | Output DC offset shift |

### 2.4 Capacitors (4 Total)

| Ref | Value | Schematic Symbol | Qty | Circuit Location |
|---|---|---|---|---|
| `C1` | **4.7 µF** | **Non-polarized** | 1 | Input AC-coupling cap (`IN` Tip to `IN_AC`) |
| `C2` | **1 µF** | **Non-polarized** | 1 | Envelope attack/release storage cap (`ENV_CAP` to `GND`) |
| `C3` | **4.7 µF** | **Polarized electrolytic (`+` marked)** | 1 | `+12V` power rail decoupling (`+12V` to `GND`) |
| `C4` | **4.7 µF** | **Polarized electrolytic (`+` marked)** | 1 | `-12V` power rail decoupling (`GND` to `-12V`) |

### 2.5 Diodes & LED (4 Total)

| Ref | Part | Qty | Function |
|---|---|---|---|
| `D1`, `D2`, `D3` | **1N4148** | **3** | Precision rectifier feedback/output diodes (`D1`, `D2`) and peak-hold charging diode (`D3`) |
| `D4` | **LED** | **1** | Envelope level visual indicator |

### 2.6 Jacks & Power Entry

| Ref | Schematic Label | Type | Connections |
|---|---|---|---|
| `J1` | `IN` | 3.5 mm mono TS jack | Tip -> `C1`; Sleeve -> `GND` *(if switched jack, Tip-Normal can tie to `GND`)* |
| `J2` | `OUT` | 3.5 mm mono TS jack | Tip -> `R16` (`1 kΩ`); Sleeve -> `GND` *(leave any switch pin NC)* |
| `J3` | `INV_OUT` | 3.5 mm mono TS jack | Tip -> `R19` (`1 kΩ`); Sleeve -> `GND` *(leave any switch pin NC)* |
| `J4` | `+12V in`, `GND`, `-12V in` | Power input terminals | Direct feed to `+12V`, `GND`, `-12V` rails (e.g., 10-pin Eurorack IDC header) |

---

## 3. Component Orientation Reference (Critical for Assembly)

### 3.1 Diode & LED Orientations

| Ref | Part | Anode (`+`) Connection | Cathode (`-`, band / flat) Connection | Schematic Orientation |
|---|---|---|---|---|
| `D1` | `1N4148` | `U1B` output (`U1B_OUT`) | `U1B` inverting input (`U1B_INV`, `-` pin) | Points **left** (clamp loop around `U1B`) |
| `D2` | `1N4148` | Rectifier summing node (`RECT_HW`, junction of `R6` & `R7`) | `U1B` output (`U1B_OUT`) | Points **left** (into `U1B` output) |
| `D3` | `1N4148` | `U1C` output (`RECT_OUT`, junction with `R8`) | `ATK` pot Pin 1 (`ATK_IN`) | Points **left** (from `U1C` out toward `ATK`) |
| `D4` | `LED` | `R21` (`22 kΩ`, from `U2B` output) | `LED_K` (junction of `R22` `10 kΩ` to `GND` & `R23` `33 kΩ` to `-12V`) | Points **right** |

### 3.2 Capacitor Polarity & Type Notes

| Ref | Value | Schematic Polarity | Positive (`+`) Terminal | Negative (`-`) Terminal | Build Note |
|---|---|---|---|---|---|
| `C1` | `4.7 µF` | **Non-polarized** (no `+` mark) | N/A | N/A | Use non-polarized film or bipolar electrolytic; `IN` carries bipolar AC audio/CV |
| `C2` | `1 µF` | **Non-polarized** (no `+` mark) | N/A | N/A | Use low-leakage film (or MLCC); node `ENV_CAP` stays $\ge 0\text{ V}$ (if polarized substituted, `+` -> `ENV_CAP`, `-` -> `GND`) |
| `C3` | `4.7 µF` | **Polarized** (`+` marked at top) | **`+12V`** | **`GND`** | Electrolytic rated $\ge 25\text{ V}$ (minimum $16\text{ V}$) |
| `C4` | `4.7 µF` | **Polarized** (`+` marked at top) | **`GND`** | **`-12V`** | Electrolytic rated $\ge 25\text{ V}$; **`GND` is positive relative to `-12V`** |

---

## 4. Stage-by-Stage Circuit Description

```
IN ──► [C1 4.7µF + R1 1M] ──► [U1A Inverting Preamp (GAIN 100k)] ──► PREAMP_OUT
                                                                         │
              ┌─────── [R4 10k] ── [R5 10k] (20k feedforward) ───────────┤
              │                                                          ▼
              │        [U1B Precision Half-Wave Rectifier (D1, D2)] ──► [R7 10k]
              │                                                          │
              └─────────────────────────► [U1C Summing Amp (R8 22k)] ◄───┘
                                                 │
                                                 ▼
                                          [D3 1N4148]
                                                 │
                                                 ▼
     [ATK 50k] ──► ENV_CAP ([C2 1µF] to GND) ──► [R9 1k] ──► ENV_NODE
                                                                ├──► [R10 10k + RV3 1M Release] ──► GND
                                                                ├──► [R20 10k] ──► [U2B Buffer] ──► [R21 22k] ──► [LED D4] ──► (-2.79V bias)
                                                                └──► [U1D Buffer + OFFSET (RV4 100k)] ──► [R16 1k] ──► OUT
                                                                             │
                                                                             └──► [U2A Inverter (R17/R18 10k)] ──► [R19 1k] ──► INV_OUT
```

### Stage 0 — Power Supply Entry & Bulk Decoupling
- `+12V in`, `GND`, and `-12V in` (`J4`) feed the module power rails `+12V`, `GND`, and `-12V`.
- `C3` (`4.7 µF`, `+` on `+12V`, `-` on `GND`) decouples the positive rail; `C4` (`4.7 µF`, `+` on `GND`, `-` on `-12V`) decouples the negative rail.
- All op-amps (`U1` and `U2`) receive `+12V` on `V+` and `-12V` on `V-` (drawn explicitly on the bottom-left buffer `U2B` and noted globally for all `TL074`/`TL072` sections).

### Stage 1 — Input AC Coupling & Inverting Gain Preamplifier (`U1A`)
- Signal enters `J1` (`IN` Tip) through `C1` (`4.7 µF`) into `IN_AC`, biased to `GND` via `R1` (`1 MΩ`), forming a $\sim 0.034\text{ Hz}$ high-pass input filter.
- `U1A` is configured as an inverting amplifier: `+` input (`pin 3`) to `GND`; `-` input (`pin 2`) driven from `IN_AC` via `R2` (`10 kΩ`); feedback via `RV1` (`100 kΩ` `GAIN` pot wired as a rheostat).
- Closed-loop gain is $A_v = -\frac{R_{\text{GAIN}}}{10\text{ k}\Omega}$, variable from $0\times$ to $-10\times$.

### Stages 2 & 3 — Precision Full-Wave Rectifier (`U1B`, `U1C`, `D1`, `D2`)
- `PREAMP_OUT` splits into two branches feeding summing amplifier `U1C`:
  1. **Direct feedforward branch**: `R4` (`10 kΩ`) + `R5` (`10 kΩ`) in series (`20 kΩ` total) into `U1C` `-` input (`pin 9`).
  2. **Half-wave rectifier branch (`U1B`)**: `R3` (`10 kΩ`) into `U1B` `-` input (`pin 6`), with `U1B` `+` input (`pin 5`) at `GND`.
     - When `PREAMP_OUT` $> 0$: `U1B` output swings negative, reverse-biasing `D1` (`Anode = U1B_OUT`, `Cathode = U1B_INV`) and forward-biasing `D2` (`Anode = RECT_HW`, `Cathode = U1B_OUT`). Feedback through `R6` (`10 kΩ`) sets `RECT_HW` $= -V_{\text{PREAMP\_OUT}}$. Summed into `U1C` (`+V/20k - V/10k = -V/20k`), `U1C` (`R8 = 22 kΩ`) outputs $+\frac{22}{20} V_{\text{PREAMP\_OUT}} = +1.1\,V_{\text{PREAMP\_OUT}}$.
     - When `PREAMP_OUT` $< 0$: `U1B` output swings positive, forward-biasing `D1` to clamp `U1B` output near $+0.6\text{ V}$ and reverse-biasing `D2`. Zero current flows through `R7` (`10 kΩ`) from `RECT_HW`, so only the `20 kΩ` branch drives `U1C`, yielding $-\frac{22}{20} V_{\text{PREAMP\_OUT}} = +1.1\,|V_{\text{PREAMP\_OUT}}|$.
- Result: `RECT_OUT` (`U1C` output, `pin 8`) is a **strictly positive-going full-wave rectified waveform**: $V_{\text{RECT\_OUT}} = +1.1\,|V_{\text{PREAMP\_OUT}}|$ (before op-amp rail saturation).

### Stage 4 — Attack / Release Envelope Detector (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)
- `D3` (`1N4148`, `Anode` at `U1C` output, `Cathode` at `RV2` `ATK`) passes positive peaks from `RECT_OUT` into `RV2` (`50 kΩ` `ATK` rheostat) to charge `C2` (`1 µF` to `GND`) positively, while blocking reverse discharge back into `U1C` when `RECT_OUT` falls.
- `C2` (`ENV_CAP`) connects through `R9` (`1 kΩ`) to `ENV_NODE`, which is buffered by `U1D` (`+`) and `U2B` (`+`) and discharged to `GND` through `R10` (`10 kΩ`) in series with `RV3` (`1 MΩ` `Release` rheostat).
- `R9` + `R10` establish a minimum discharge resistance of `11 kΩ` ($\tau_{\text{rel,min}} = 11\text{ ms}$) even with `Release` dialed to `0 Ω`, extending up to $1.011\text{ s}$ at `1 MΩ`.

### Stage 5 — Offset Summing, `OUT`, and `INV_OUT` (`U1D`, `U2A`, `RV4`)
- `RV4` (`100 kΩ` `OFFSET` pot) sits between `R11` (`10 kΩ` to `+12V`) and `R12` (`10 kΩ` to `-12V`), spanning $-10\text{ V}$ to $+10\text{ V}$ unloaded.
- The `OFFSET` wiper connects via `R13` (`10 kΩ`) into `U1D` `-` input (`pin 13`), alongside `R14` (`10 kΩ` to `GND`) and `R15` (`10 kΩ` feedback to `U1D_OUT`, `pin 14`), while `ENV_NODE` drives `U1D` `+` input (`pin 12`).
- Because `OFFSET` enters the inverting input (`U1D` `-`) and the `100 kΩ` pot has source impedance $R_{\text{th}} \in [9.17\text{ k}\Omega,\,30\text{ k}\Omega]$ depending on wiper position:
  - Envelope gain at `U1D_OUT` is $2 + \frac{10\text{ k}\Omega}{10\text{ k}\Omega + R_{\text{th}}} \approx 2.25\times\text{ (center) to }2.52\times\text{ (ends)}$.
  - Sweeping `OFFSET` toward $+12\text{ V}$ shifts `OUT` downward (to $\approx -5.2\text{ V}$ at zero envelope); sweeping `OFFSET` toward `-12V` shifts `OUT` upward (to $\approx +5.2\text{ V}$).
- `U1D_OUT` feeds:
  - `OUT` jack (`J2`) through `R16` (`1 kΩ`).
  - `U2A` inverting unity-gain stage (`R17 = 10 kΩ` input, `R18 = 10 kΩ` feedback, `+` pin 3 to `GND`) -> `R19` (`1 kΩ`) -> `INV_OUT` jack (`J3`), producing $V_{\text{INV\_OUT}} = -V_{\text{OUT}}$.

### Stage 6 — Buffered Envelope LED Driver (`U2B`, `D4`)
- The `LED` net flag connects from `ENV_NODE` through `R20` (`10 kΩ`) into unity-gain voltage follower `U2B` (`+` pin 5; `-` pin 6 tied to output pin 7).
- `U2B` output drives LED `D4` anode through `R21` (`22 kΩ`).
- `D4` cathode connects to a `GND`/`-12V` divider (`R22 = 10 kΩ` to `GND`, `R23 = 33 kΩ` to `-12V`), setting a Thévenin reference of $-12\text{ V} \cdot \frac{10}{10 + 33} \approx -2.79\text{ V}$ ($R_{\text{th}} \approx 7.67\text{ k}\Omega$). This pre-biases the LED cathode below `GND` so the LED turns on smoothly near $0\text{ V}$ envelope levels despite the LED forward voltage drop.

---

## 5. Complete Pin-Level Netlist

Pin numbers below follow **Option A**: `U1 = TL074` (14-pin) and `U2 = TL072` (8-pin). Resistors/non-polarized capacitors use `.1` and `.2`; potentiometers use `.1` (CCW end), `.2` (wiper), `.3` (CW end); diodes use `.A` (anode) and `.K` (cathode); polarized electrolytics use `.+` and `.-`.

| Net Name | Connected Pins |
|---|---|
| **`+12V`** | `J4.+12V_in`, `C3.+`, `R11.1`, `U1.4` (`V+`), `U2.8` (`V+`) |
| **`-12V`** | `J4.-12V_in`, `C4.-`, `R12.2`, `R23.2`, `U1.11` (`V-`), `U2.4` (`V-`) |
| **`GND`** | `J4.GND`, `C3.-`, `C4.+`, `J1.Sleeve`, `R1.2`, `U1.3` (`U1A+`), `U1.5` (`U1B+`), `U1.10` (`U1C+`), `C2.2`, `RV3.2`, `RV3.3`, `R14.2`, `J2.Sleeve`, `U2.3` (`U2A+`), `J3.Sleeve`, `R22.2` |
| **`IN_TIP`** | `J1.Tip`, `C1.1` |
| **`IN_AC`** | `C1.2`, `R1.1`, `R2.1` |
| **`U1A_INV`** | `R2.2`, `U1.2` (`U1A-`), `RV1.1` |
| **`PREAMP_OUT`** | `U1.1` (`U1A_OUT`), `RV1.2`, `RV1.3`, `R3.1`, `R4.1` |
| **`U1B_INV`** | `R3.2`, `U1.6` (`U1B-`), `R6.1`, `D1.K` |
| **`U1B_OUT`** | `U1.7` (`U1B_OUT`), `D1.A`, `D2.K` |
| **`RECT_HW`** | `D2.A`, `R6.2`, `R7.1` |
| **`FF_MID`** | `R4.2`, `R5.1` |
| **`U1C_INV`** | `R5.2`, `R7.2`, `U1.9` (`U1C-`), `R8.1` |
| **`RECT_OUT`** | `U1.8` (`U1C_OUT`), `R8.2`, `D3.A` |
| **`ATK_IN`** | `D3.K`, `RV2.1` |
| **`ENV_CAP`** | `RV2.2`, `RV2.3`, `C2.1`, `R9.1` |
| **`ENV_NODE`** *(labeled `LED`)* | `R9.2`, `R10.1`, `U1.12` (`U1D+`), `R20.1` |
| **`REL_POT_TOP`** | `R10.2`, `RV3.1` |
| **`OFF_TOP`** | `R11.2`, `RV4.1` |
| **`OFF_BOT`** | `R12.1`, `RV4.3` |
| **`OFF_WIPER`** | `RV4.2`, `R13.1` |
| **`U1D_INV`** | `R13.2`, `R14.1`, `R15.1`, `U1.13` (`U1D-`) |
| **`U1D_OUT`** | `U1.14` (`U1D_OUT`), `R15.2`, `R16.1`, `R17.1` |
| **`OUT_TIP`** | `R16.2`, `J2.Tip` |
| **`U2A_INV`** | `R17.2`, `R18.1`, `U2.2` (`U2A-`) |
| **`U2A_OUT`** | `U2.1` (`U2A_OUT`), `R18.2`, `R19.1` |
| **`INV_OUT_TIP`** | `R19.2`, `J3.Tip` |
| **`U2B_IN`** | `R20.2`, `U2.5` (`U2B+`) |
| **`U2B_OUT`** | `U2.7` (`U2B_OUT`), `U2.6` (`U2B-`), `R21.1` |
| **`LED_A`** | `R21.2`, `D4.A` |
| **`LED_K`** | `D4.K`, `R22.1`, `R23.1` |

---

## 6. Practical Build & Implementation Notes

1. **Op-Amp Pinout Reference (DIP/SOIC):**
   - `TL074` (14-pin): `V+ = pin 4`, `V- = pin 11`; Units: `A(+=3, -=2, out=1)`, `B(+=5, -=6, out=7)`, `C(+=10, -=9, out=8)`, `D(+=12, -=13, out=14)`.
   - `TL072` (8-pin): `V+ = pin 8`, `V- = pin 4`; Units: `A(+=3, -=2, out=1)`, `B(+=5, -=6, out=7)`.
2. **Local IC Decoupling (Optional Best Practice, Not Shown on Sketch):** In addition to the drawn `4.7 µF` bulk caps `C3`/`C4`, placing `100 nF` ceramic decoupling capacitors close to each IC's `V+` and `V-` pins to `GND` improves high-frequency stability.
3. **Potentiometer Rotation Conventions:**
   - With Pin 1 = CCW, Pin 2 = Wiper, Pin 3 = CW (looking at shaft front):
     - `RV1` (`GAIN`): Pin 1 -> `U1A_INV`, Pins 2+3 -> `PREAMP_OUT` (clockwise increases gain).
     - `RV2` (`ATK`): Pin 1 -> `ATK_IN`, Pins 2+3 -> `ENV_CAP` (clockwise slows attack).
     - `RV3` (`Release`): Pin 1 -> `REL_POT_TOP`, Pins 2+3 -> `GND` (clockwise lengthens release).
     - `RV4` (`OFFSET`): Pin 1 -> `OFF_TOP`, Pin 3 -> `OFF_BOT` makes clockwise push `OUT` more negative (or swap Pin 1/Pin 3 if you want clockwise to push `OUT` more positive).
   - Linear (`B` taper) potentiometers work well for `GAIN` and `OFFSET`; logarithmic/audio (`A` taper) or linear (`B`) can be used for `ATK` and `Release` (`A` taper gives finer resolution at fast attack/release settings).
4. **LED Selection:** Because the LED cathode sits at a $\approx -2.79\text{ V}$ Thévenin bias (`R22`/`R23`), a red/yellow/standard green LED ($V_f \approx 1.8\text{–}2.1\text{ V}$) may glow faintly at $0\text{ V}$ envelope, whereas a blue/white/high-$V_f$ green LED ($V_f \approx 2.8\text{–}3.2\text{ V}$) sits right near cutoff at idle.
5. **Switched Jacks & Power Protection:**
   - Standard Eurorack switched 3.5 mm jacks (e.g., PJ301M-12 / Thonkiconn): optionally ground the Tip-Normal pin on `J1` (`IN`) to prevent floating-input hum when unpatched; leave Tip-Normal pins unconnected (`NC`) on `J2` (`OUT`) and `J3` (`INV_OUT`).
   - The original schematic omits reverse-polarity protection diodes or `10 Ω` / resettable polyfuse series rail protection at `J4`; add those inline before `C3`/`C4` if building for a Eurorack bus board.
