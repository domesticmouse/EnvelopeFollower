# Improved Envelope Follower Circuit Specification

Updated engineering specification incorporating all circuit improvements and Eurorack hardware protections from [`EnvelopeFollowerImprovements.md`](./EnvelopeFollowerImprovements.md) applied to [`EnvelopeFollower.md`](./EnvelopeFollower.md), standardized on **2 × `TL074H` (SOIC-14)** with surface-mount construction for JLCPCB Economic PCBA and through-hole panel/power hardware mounted later.

---

## 1. Overview & Electrical Summary

This module is a **±12 V Eurorack analog envelope follower** built around **8 JFET/FET-input op-amp stages** (`2 × TL074HIDR`, `SOIC-14`). Relative to the original 6-op-amp sketch, this revision adds a buffered `100 kΩ` input stage (`U2D`), an active zero-deadzone precision peak detector (`U2C`), `0.1%`-matched `1.000×` full-wave rectification, linearized output offset summing, an in-loop zero-idle-glow LED current sink, and full Eurorack power/ESD/clash protections.

| Parameter | Original (`EnvelopeFollower.md`) | Improved Specification (`TL074H` / `2 × TL074`) |
|---|---|---|
| **Power Supply** | Direct `±12 V`, `4.7 µF` (`≥16 V`), no protection | Shrouded keyed `2×5` IDC (`J4`); `B5819W` (`40 V / 1 A`) reverse-polarity Schottkys + `10 Ω` RC damping ($f_c = 723\text{ Hz}$) → **`±11.55 V` internal rails**; `22 µF / 50 V` SMD bulk caps + `4 × 100 nF / 50 V` X7R local bypasses |
| **Op-Amps** | `1 × TL074 + 1 × TL072` (6 sections) | **`2 × TL074HIDR` (`SOIC-14`)** — all **8 sections used** (`U1A`–`U1D`, `U2A`–`U2D`), zero unused sections |
| **Input (`IN`)** | $Z_{\text{in}} \approx 9.9\text{ k}\Omega$, actual $f_c \approx 3.42\text{ Hz}$, optional switch | **`U2D` unity buffer**: $Z_{\text{in}} = 101\text{ k}\Omega$, $f_c = 1.58\text{ Hz}$ (`1 µF` film), `1 kΩ` series protection + `BAV99` rail clamp + mandatory `J1.TN → GND` |
| **Preamp (`GAIN`)** | `B100k` pot (`0` to `-10×`), `0 Ω` short at CCW | **`RV1` = `A100k` audio taper**; `1 kΩ` gain floor + `1 MΩ` fail-safe + `47 pF` `C0G` HF compensation ($A_v = -0.10\times\text{ to }-9.17\times$, $f_c \ge 36.9\text{ kHz}$) |
| **Rectifier** | `1%`/`5%` resistors, `+1.1×`, `1N4148` | **`7 × 10 kΩ ±0.1%` (`25 ppm/°C`)** matched network + **`BAT54S`** Schottky pair; exact **`+1.000×`** gain ($V_{\text{RECT\_OUT}} = \|V_{\text{PREAMP\_OUT}}\|$), `≤ 0.80%` half-cycle error |
| **Peak Detector** | Passive `D3` (`~0.65 V` deadband), no surge limit | **`U2C` active zero-deadzone peak detector** (`D3` `1N4148WS` inside op-amp loop, `< 5 mV` deadband) + `R_ATK_MIN = 470 Ω` surge limiter |
| **Attack (`ATK`)** | `50 kΩ` (`0` to `50 ms`) | **`RV2` = `A50k` audio taper**; $\tau_{\text{atk}} \approx 0.47\text{ ms to }50.5\text{ ms}$ |
| **Release (`Release`)** | `1 MΩ` (`11 ms`–`1.01 s`), `R9` causes `-9.1%` droop | **`RV3` = `A1M` audio taper** + `R10 = 10 kΩ`; **`R9` removed** (0% droop); $\tau_{\text{rel}} = 10\text{ ms to }1.01\text{ s}$; `10 kΩ` `R_ENV_PROT` on `U1D+` |
| **Offset (`OFFSET`)** | `100 kΩ` pot (`2.25×`–`2.52×` gain, `12%` shift, clips at `+4.2 V`) | **`RV4` = `B10k` linear pot** between `1 kΩ` end resistors, `R13 = 18 kΩ`, **`R14` removed**; gain `1.476×–1.529×` (`3.5%` var), **`±5.09 V` linear shift** (`CW = +OUT`), linear up to `ENV_NODE ≈ +7.5 V` |
| **Outputs** | Single `1 kΩ` outside loop, no ESD clamp | Split **`470 Ω + 470 Ω` (`0.5 W` `1210`)** clash-rated resistors + midpoint **`BAV99`** rail clamps + in-loop `10 kΩ` feedback (`100 pF` `C0G` HF cap) for `0.00%` `OUT`/`INV_OUT` tracking mismatch; `J2.TN`/`J3.TN = NC` |
| **LED Indicator** | `-2.79 V` bias (`23–32 µA` idle glow, `0.36 mA` peak) | **`U2B` in-loop precision current sink** (`R_LED = 2.2 kΩ` + `1N4148WS` anti-parallel clamp; `R21`–`R23` removed); **`0.00 mA` idle**, `0–4.5 mA` linear drive for any 3 mm LED color |

---

## 2. IC Allocation & Component Inventory

### 2.1 Integrated Circuits (`2 × TL074HIDR`, `SOIC-14`)

Both quad op-amps use **Texas Instruments `TL074HIDR`** (`SOIC-14`, `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm`): `±2.25 V to ±20 V` supply, `20 V/µs` slew rate, `5.25 MHz` GBWP, `1 pA` input bias current, `1 mV` offset, `26 mA` output drive, `940 µA/ch` quiescent current, short-circuit protection, and internal EMI/RF suppression.

| IC / Section | Pins (`+`, `-`, `Out`) | Circuit Role | Key Improvement |
|---|---|---|---|
| **`U1A`** | `3`, `2`, `1` | Inverting Gain Preamp (`GAIN` `RV1 = A100k`) | `1 kΩ` gain floor + `1 MΩ` wiper fail-safe + `47 pF` `C0G` HF roll-off |
| **`U1B`** | `5`, `6`, `7` | Precision Half-Wave Rectifier | `BAT54S` (`D1_D2`) low-drop Schottky pair + `0.1%` resistors |
| **`U1C`** | `10`, `9`, `8` | Precision Rectifier Summing Amp | `7 × 10 kΩ ±0.1%` matched network (`R8A+R8B = 20 kΩ` → exact `1.000×` gain) |
| **`U1D`** | `12`, `13`, `14` | Output Non-Inverting Buffer + `OFFSET` Summer (`OUT`) | `R14` removed; `RV4 = B10k`, `R13 = 18 kΩ`; `10 kΩ` `R_ENV_PROT`; `§3.5` in-loop feedback |
| **`U2A`** | `3`, `2`, `1` | Unity-Gain Inverting Buffer (`INV_OUT`) | `§3.5` in-loop feedback (`R18` from `INV_OUT_CLAMP` + `100 pF` `C0G`) |
| **`U2B`** | `5`, `6`, `7` | Precision LED Current Sink (`D4`) | `D4` inside feedback loop (`R_LED = 2.2 kΩ` + `1N4148WS` reverse clamp) |
| **`U2C`** | `10`, `9`, `8` | **Active Zero-Deadzone Peak Detector** | `D3` (`1N4148WS`) inside feedback loop (`< 5 mV` deadband) + `470 Ω` surge limit |
| **`U2D`** | `12`, `13`, `14` | **`100 kΩ` Unity-Gain Input Buffer** | Isolates `R1 = 100 kΩ` from `U1A` virtual ground (`Z_in = 101 kΩ`, `f_c = 1.58 Hz`) |
| **Power** | `V+ = 4`, `V- = 11` | `±11.55 V` Schottky-protected rails (`U1` and `U2`) | `4 × 100 nF` `50 V` X7R local decoupling `< 3–5 mm` from supply pins |

---

### 2.2 Fixed Resistors (30 Total — All SMT)

| Value & Spec | Package | Qty | Reference Designators | Circuit Locations |
|---|---|---|---|---|
| **10 Ω ±1% 250 mW** | `1206` | **2** | `R_PWR_P`, `R_PWR_N` | `+12V` and `-12V` rail RC damping/surge resistors after `D_PWR_P/N` |
| **470 Ω ±1% 100 mW** | `0603` | **1** | `R_ATK_MIN` | Attack minimum current/ringing limiter (`ATK_IN` to `RV2.1`) |
| **470 Ω ±1% 500 mW (0.5 W)** | `1210` | **4** | `R16A`, `R16B`, `R19A`, `R19B` | Split clash-rated output isolation resistors on `OUT` and `INV_OUT` |
| **1 kΩ ±1% 100 mW** | `0603` | **5** | `R_IN_PROT`, `R_IN_BUF`, `R_GAIN_MIN`, `R11`, `R12` | `J1` tip protection; `U2D+` ESD input resistor; `U1A` gain floor; `RV4` end resistors |
| **2.2 kΩ ±1% 100 mW** | `0603` | **1** | `R_LED` | Precision LED cathode current-setting resistor (`LED_K` to `GND`) |
| **10 kΩ ±1% 100 mW** | `0603` | **7** | `R2`, `R10`, `R_ENV_PROT`, `R15`, `R17`, `R18`, `R20` | `U1A` input; `Release` min; `U1D+` protection; `U1D` fb; `U2A` in/fb; `U2B+` input |
| **10 kΩ ±0.1% 25 ppm/°C** | `0603` | **7** | `R3`, `R4`, `R5`, `R6`, `R7`, `R8A`, `R8B` | Precision rectifier: `R3`/`R6`/`R7` (`10 kΩ`), `R4+R5` (`20 kΩ` FF), `R8A+R8B` (`20 kΩ` fb) |
| **18 kΩ ±1% 100 mW** | `0603` | **1** | `R13` | `OFFSET` summing resistor (`OFF_WIPER` to `U1D_INV`) |
| **100 kΩ ±1% 100 mW** | `0603` | **1** | `R1` | Input AC-coupling `GND` bias (`Z_in = 101 kΩ`) |
| **1 MΩ ±1% 100 mW** | `0603` | **1** | `R_GAIN_FAIL` | `U1A` PCB open-wiper fail-safe across `RV1` |

*(Deleted from original design: `R9` (`1 kΩ`), `R14` (`10 kΩ`), `R21` (`22 kΩ`), `R22` (`10 kΩ`), `R23` (`33 kΩ`); `R8` (`22 kΩ`) replaced by `R8A + R8B = 20 kΩ ±0.1%`.)*

---

### 2.3 Potentiometers (4 Total — THT, Mounted Later)

| Ref | Panel Label | Taper & Value | Wiring Style | Function & Range |
|---|---|---|---|---|
| **`RV1`** | `GAIN` | **`A100k`** (`100 kΩ` audio/log) | 2-terminal rheostat (`1` to `GAIN_POT_1`; `2+3` to `PREAMP_OUT`) | Input preamp gain: **`-0.10×` (`-20 dB`) to `-9.17×` (`+19.25 dB`)** |
| **`RV2`** | `ATK` | **`A50k`** (`50 kΩ` audio/log) | 2-terminal rheostat (`1` to `ATK_POT_1`; `2+3` to `ENV_NODE`) | Attack slew/charge time: **`0.47 ms` to `50.5 ms`** |
| **`RV3`** | `Release` | **`A1M`** (`1 MΩ` audio/log) | 2-terminal rheostat (`1` to `REL_POT_TOP`; `2+3` to `GND`) | Release decay time: **`10 ms` to `1.01 s`** |
| **`RV4`** | `OFFSET` | **`B10k`** (`10 kΩ` linear) | 3-terminal divider (`1` to `OFF_TOP`, `2` wiper to `R13`, `3` to `OFF_BOT`) | Bipolar DC offset: **`±5.09 V`** (`CW` = more positive `OUT`) |

---

### 2.4 Capacitors (11 Total — 9 SMT + 2 THT Box Film)

| Ref | Value & Rating | Dielectric / Polarity | Package & Mount | Qty | Circuit Location |
|---|---|---|---|---|---|
| **`C1`, `C2`** | **`1 µF` `100 V` `±5%`** | Metallized Polyester (PET) Film, **Non-polarized** | `P=5mm` Box Film (**THT**, mounted later) | **2** | `C1`: Input AC-coupling (`f_c = 1.58 Hz`); `C2`: Envelope hold cap (`ENV_NODE` to `GND`, zero microphonics/droop) |
| **`C3`, `C4`** | **`22 µF` `50 V` `±20%`** | Aluminum Electrolytic, **Polarized** | `SMD,D6.3xL5.4mm` (**SMT**) | **2** | `C3`: `+12V` bulk decoupling; `C4`: `-12V` bulk decoupling (`+` to `GND`) |
| **`C_DEC1`–`C_DEC4`** | **`100 nF` `50 V` `±10%`** | `X7R` MLCC | `0603` (**SMT**) | **4** | Local `V+`/`V-` decoupling `< 3–5 mm` from `U1` and `U2` |
| **`C_HF`** | **`47 pF` `50 V` `±5%`** | `C0G / NP0` MLCC (Class I) | `0603` (**SMT**) | **1** | `U1A` ultrasonic/RF feedback roll-off (`U1A_INV` to `PREAMP_OUT`) |
| **`C_OUT1`, `C_OUT2`** | **`100 pF` `50 V` `±5%`** | `C0G / NP0` MLCC (Class I) | `0603` (**SMT**) | **2** | `U1D` & `U2A` local HF feedback caps (`§3.5` in-loop output compensation) |

*(Note: Class-2 MLCCs (`X7R`/`X5R`) are excluded from `C1`/`C2` per `§3.3` due to piezoelectric microphonics and DC-bias capacitance collapse; JLCPCB carries `0` stock of `1 µF` SMD film (`ECWU1105KCV`), so `C1` and `C2` are specified as compact `P=5mm` THT film capacitors mounted alongside the other THT hardware.)*

---

### 2.5 Diodes & LED (9 Physical Packages: 8 SMT + 1 THT LED)

| Ref | Part | Package & Mount | Qty | Function |
|---|---|---|---|---|
| **`D_PWR_P`, `D_PWR_N`** | `B5819W` (`40 V / 1 A` Schottky) | `SOD-123` (**SMT**) | **2** | Eurorack `+12V` and `-12V` reverse-polarity power protection |
| **`D1_D2`** | `BAT54S` (Dual Series Schottky) | `SOT-23` (**SMT**) | **1** | Combines rectifier diodes `D1` (`U1B_OUT → U1B_INV`) and `D2` (`RECT_HW → U1B_OUT`) |
| **`D3`, `D_LED_CLAMP`** | `1N4148WS` (`100 V` low-leakage) | `SOD-323` (**SMT**) | **2** | `D3`: Active peak-detector diode (`< 25 nA` leakage); `D_LED_CLAMP`: Anti-parallel clamp across `D4` |
| **`D_IN`, `D_OUT`, `D_INV_OUT`** | `BAV99` (Dual Series Switching) | `SOT-23` (**SMT**) | **3** | ESD and overvoltage rail clamps (`±12 V`) on `IN_AC`, `OUT_CLAMP`, `INV_OUT_CLAMP` |
| **`D4`** | `3 mm` Indicator LED (Red / Any) | `3 mm` Round (**THT**, later) | **1** | Envelope level indicator inside `U2B` feedback loop |

---

### 2.6 Jacks & Power Entry (4 Total — THT, Mounted Later)

| Ref | Label | Type & Footprint | Connections |
|---|---|---|---|
| **`J1`** | `IN` | 3.5 mm mono switched jack (`WQP-PJ398SM`) | `Tip` → `R_IN_PROT`; `Sleeve` → `GND`; **`Tip-Normal (TN)` → `GND`** (mandatory) |
| **`J2`** | `OUT` | 3.5 mm mono switched jack (`WQP-PJ398SM`) | `Tip` → `R16B`; `Sleeve` → `GND`; **`Tip-Normal (TN)` → `NC`** |
| **`J3`** | `INV_OUT` | 3.5 mm mono switched jack (`WQP-PJ398SM`) | `Tip` → `R19B`; `Sleeve` → `GND`; **`Tip-Normal (TN)` → `NC`** |
| **`J4`** | `PWR` | `2×5` (`10-pin`) `2.54 mm` shrouded keyed Eurorack IDC | Pins `1–2` = `-12V_IN` (`RED STRIPE`), Pins `3–8` = `GND`, Pins `9–10` = `+12V_IN` |

### 2.7 Test Points (8 Total — THT, Optional / DNP)

Tier 1 core bench test points (`TP1`–`TP8`) use **Ronghe `RH-5001`** (`2.5 mm` black pin-type through-board test points, LCSC **`C5199801`**) marked **DNP (Do Not Populate)** in the BOM. Bare plated through-hole pads on `B.Cu` allow immediate probe contact on unstuffed boards, with optional hand-soldering of `RH-5001` pins on `B.Cu` for clip-on oscilloscope/DMM grabbers. Every test point sits exclusively on a low-impedance power rail or buffered/closed-loop op-amp output node.

*(KiCad footprint: `TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` or `TestPoint:TestPoint_Keystone_5000-5004_Miniature` — verify exact drill diameter against the `C5199801` datasheet before PCB drill freeze.)*

| Ref | Net Name | Stage | Expected Signal / Range | Bench & Troubleshooting Role |
|---|---|---|---|---|
| **`TP1`** | **`GND`** | Stage 0 | `0.000 V` reference | Dedicated clip-on return for oscilloscope ground leads and DMM black probe |
| **`TP2`** | **`+12V`** | Stage 0 | `≈ +11.55 V` DC (`±1%`) | Verifies `D_PWR_P` orientation, `R_PWR_P`/`C3` RC drop, and `U1.4`/`U2.4` rail health |
| **`TP3`** | **`-12V`** | Stage 0 | `≈ -11.55 V` DC (`±1%`) | Verifies reversed `D_PWR_N` orientation, `R_PWR_N`/`C4` RC drop, and `U1.11`/`U2.11` rail health |
| **`TP4`** | **`IN_BUF`** | Stage 1A | `±V_in` AC (`0 V` DC) | Confirms `J1` tip/normalled ground, `C1` DC blocking (`f_c = 1.58 Hz`), `D_IN` clamp, and `U2D` buffer without loading `IN_AC` |
| **`TP5`** | **`PREAMP_OUT`** | Stage 1B | `(-0.10× to -9.17×)·IN_BUF` | Verifies `RV1` (`GAIN`) range, audio taper, and `U1A` clipping headroom ahead of rectifier |
| **`TP6`** | **`RECT_OUT`** | Stages 2–3 | `+1.000·\|PREAMP_OUT\|` | Verifies `U1B`/`D1_D2`/`U1C` full-wave rectification and `0.1%` half-cycle symmetry |
| **`TP7`** | **`OUT_CLAMP`** | Stage 5 | `1.476×–1.529× ENV ± 5.09 V` | Measures closed-loop `U1D` output (`R16A` in-loop); with `RV4` centered (`0.000 V` idle), doubles as buffered `1.476× ENV_NODE` monitor |
| **`TP8`** | **`INV_OUT_CLAMP`** | Stage 5 | `-1.000 × V(OUT_CLAMP)` | Verifies `U2A` inverter, `D_INV_OUT` clamp, and `0.00%` tracking symmetry vs. `TP7` |

**Sensitive & Virtual-Ground Nodes Deliberately Omitted:**
- **`IN_AC` & `U2D_IN` (Stage 1A)**: High-impedance `100 kΩ` / `1 µF` AC-coupling node; scope probe capacitance and unshielded test pins inject `50/60 Hz` hum that `U1A` amplifies up to `-9.17×` (probe **`TP4` `IN_BUF`** instead).
- **`U1A_INV`, `U1B_INV`, `U1C_INV`, `U1D_INV`, `U2A_INV`, `LED_K` (`U2B-`)**: Op-amp inverting summing / virtual-ground / feedback pins; adding THT pad + probe capacitance (`~10–20 pF`) degrades phase margin (risking HF peaking/oscillation on `U1A` with `C_HF = 47 pF` or instability inside `U2B`'s nonlinear LED loop).
- **`ENV_NODE`, `ATK_IN`, `REL_POT_TOP`, `U1D_IN`, `U2B_IN` (Stage 4)**: High-impedance peak-hold node (`C2 = 1 µF` discharging into up to `1.01 MΩ`); a `1 MΩ` (`1×`) or `10 MΩ` (`10×`) probe distorts `1 s` release decay, and residual solder flux on an unwashed THT pin creates leakage droop (center `RV4` and monitor buffered `ENV_NODE` at **`TP7` `OUT_CLAMP`**).

---

## 3. Component Orientation, Pinout & Polarity Reference

### 3.1 Diode & LED Pin Mapping (Verified Against KiCad Libraries & Datasheets)

- **2-Pin SMD Diodes (`SOD-123`, `SOD-323`) & THT `LED_D3.0mm`**: KiCad pad/pin convention is **`Pin 1 = K` (Cathode, band / flat / short lead)**, **`Pin 2 = A` (Anode)**.
- **3-Pin `SOT-23` Dual Series Diodes (`BAT54S`, `BAV99`)**: Physical SOT-23 pinout is **`Pin 1 = A1`**, **`Pin 2 = K2`**, **`Pin 3 = COM (K1 / A2)`**. *(Note: KiCad's `Diode:BAV99` symbol places Pin 1 at the left diode's anode and Pin 2 at the right diode's cathode, matching the physical SOT-23 package despite legacy hidden pin-name labels.)*

| Ref | Part | Package | Anode (`A` / `Pin 1`) | Cathode (`K` / `Pin 2`) | Common (`COM` / `Pin 3`) | Critical Note |
|---|---|---|---|---|---|---|
| **`D_PWR_P`** | `B5819W` | `SOD-123` | `+12V_IN` (`J4.9–10`) | `+12V_PROT` | — | Blocks reversed `+12V` cable |
| **`D_PWR_N`** | `B5819W` | `SOD-123` | `-12V_PROT` | `-12V_IN` (`J4.1–2`) | — | **Reversed vs. `+12V`**: Cathode faces `J4` (`-12V_IN`) |
| **`D1_D2`** | `BAT54S` | `SOT-23` | `RECT_HW` (`Pin 1 = A1`, `D2.A`) | `U1B_INV` (`Pin 2 = K2`, `D1.K`) | `U1B_OUT` (`Pin 3 = K1/A2`) | `D2`: `RECT_HW → U1B_OUT`; `D1`: `U1B_OUT → U1B_INV` |
| **`D3`** | `1N4148WS` | `SOD-323` | `U2C_OUT` (`U2.8`) | `ATK_IN` (`U2.9`, `R_ATK_MIN`) | — | Inside `U2C` feedback loop |
| **`D_IN`** | `BAV99` | `SOT-23` | `-12V` (`Pin 1 = A1`) | `+12V` (`Pin 2 = K2`) | `IN_AC` (`Pin 3 = COM`) | Shunts `> +12V` or `< -12V` transients to rails |
| **`D_OUT`** | `BAV99` | `SOT-23` | `-12V` (`Pin 1 = A1`) | `+12V` (`Pin 2 = K2`) | `OUT_CLAMP` (`Pin 3 = COM`) | Midpoint between `R16A` and `R16B` |
| **`D_INV_OUT`** | `BAV99` | `SOT-23` | `-12V` (`Pin 1 = A1`) | `+12V` (`Pin 2 = K2`) | `INV_OUT_CLAMP` (`Pin 3 = COM`) | Midpoint between `R19A` and `R19B` |
| **`D4`** | `3 mm LED` | `THT` | `U2B_OUT` (`U2.7`, long lead) | `LED_K` (`U2.6`, flat/short) | — | Inside `U2B` current-sink loop |
| **`D_LED_CLAMP`** | `1N4148WS` | `SOD-323` | `LED_K` (`U2.6`) | `U2B_OUT` (`U2.7`) | — | **Anti-parallel** across `D4`; prevents LED `-12V` breakdown |

### 3.2 Capacitor Polarity & Placement

| Ref | Value | Polarity | `+` Terminal | `-` Terminal | Assembly Note |
|---|---|---|---|---|---|
| **`C1`, `C2`** | `1 µF` `100 V` | Non-polarized | N/A | N/A | `P=5mm` box film (`~11 mm` tall); mount on `B.Cu` if `F.Cu` panel standoff is `10.5 mm` |
| **`C3`** | `22 µF` `50 V` | **Polarized** | **`+12V`** | **`GND`** | `5.4 mm` tall SMD elec (`4.2×` voltage derating) |
| **`C4`** | `22 µF` `50 V` | **Polarized** | **`GND`** | **`-12V`** | **`GND` is positive relative to `-12V`** |
| **`C_DEC1`, `C_DEC3`** | `100 nF` `50 V` | Non-polarized | `+12V` (`U1.4` / `U2.4`) | `GND` | Place `< 3–5 mm` from IC `V+` pin |
| **`C_DEC2`, `C_DEC4`** | `100 nF` `50 V` | Non-polarized | `-12V` (`U1.11` / `U2.11`) | `GND` | Place `< 3–5 mm` from IC `V-` pin |

---

## 4. Stage-by-Stage Circuit Description

```
J1 (IN) ─► [R_IN_PROT 1k] ─► [C1 1µF] ─► IN_AC ([R1 100k→GND] + [D_IN BAV99±12V]) ─► [R_IN_BUF 1k] ─► [U2D Buffer]
                                                                                                             │
                               ┌─────────────────────────────────────────────────────────────────────────────┘
                               ▼
                         [R2 10k] ─► [U1A Preamp (R_GAIN_MIN 1k + RV1 A100k || R_GAIN_FAIL 1M || C_HF 47pF)] ─► PREAMP_OUT
                                                                                                                     │
                          ┌──────────────── [R4 10k 0.1%] ── [R5 10k 0.1%] (20k FF) ─────────────────────────────────┤
                          │                                                                                          ▼
                          │    [U1B Half-Wave Rectifier (R3/R6 10k 0.1%, D1_D2 BAT54S)] ─► [R7 10k 0.1%] ───► [U1C Summer (R8A+R8B 20k 0.1%)]
                          │                                                                                          │
                          └──────────────────────────────────────────────────────────────────────────────────────────┘
                                                                                                                     │
                                                                                                                     ▼
 [U2C Active Peak Detector (D3 1N4148WS in loop)] ◄────────────────────────────────────────────────────────────── RECT_OUT
            │
            ▼
  [R_ATK_MIN 470Ω + RV2 A50k] ─► ENV_NODE ([C2 1µF→GND] + [R10 10k + RV3 A1M→GND])
                                     ├──► [R20 10k] ─► [U2B LED Sink (D4 || 1N4148WS, R_LED 2.2k→GND)]
                                     └──► [R_ENV_PROT 10k] ─► [U1D Summer (+ OFFSET RV4 B10k / R13 18k)]
                                                                   │
                                                                   ▼
                                           [R16A 470Ω 0.5W] ─► OUT_CLAMP (BAV99±12V, R15 fb) ─► [R16B 470Ω 0.5W] ─► J2 (OUT)
                                                                   │
                                                                   ▼
                                           [R17 10k] ─► [U2A Inverter] ─► [R19A 470Ω 0.5W] ─► INV_OUT_CLAMP (BAV99±12V, R18 fb) ─► [R19B 470Ω 0.5W] ─► J3 (INV_OUT)
```

### Stage 0 — Eurorack Power Entry, Reverse-Polarity Protection & Decoupling
- `J4` receives external `+12V_IN`, `GND`, and `-12V_IN` through a keyed shrouded `2×5` header.
- `D_PWR_P` and `D_PWR_N` (`B5819W`) block reversed power cables and row-shifted headers with zero fault current, followed by `R_PWR_P` and `R_PWR_N` (`10 Ω`, `1206`) and `C3`/`C4` (`22 µF 50 V`) forming a `723 Hz` supply low-pass filter and inrush damper. At `~15 mA` nominal draw, internal rails sit at `≈ ±11.55 V`.
- `C_DEC1`–`C_DEC4` (`100 nF 50 V` X7R `0603`) bypass `U1.4`/`U1.11` and `U2.4`/`U2.11` locally to `GND`.

### Stage 1A — Input Protection, AC Coupling & `100 kΩ` Input Buffer (`U2D`)
- `J1.TN` connects unconditionally to `GND` so unpatched hum is muted.
- `J1.Tip` passes through `R_IN_PROT` (`1 kΩ`) and `C1` (`1 µF` film) into `IN_AC`, biased to `GND` by `R1` (`100 kΩ`), yielding $Z_{\text{in}} = 101\text{ k}\Omega$ and $f_c = 1.58\text{ Hz}$.
- `D_IN` (`BAV99`) clamps `IN_AC` to `[−12.3 V, +12.3 V]`, while `R_IN_BUF` (`1 kΩ`) limits current into `U2D+` (`U2.12`). Unity-gain buffer `U2D` (`U2.14` = `IN_BUF`) drives `R2` (`10 kΩ`) without loading `C1`/`R1`.

### Stage 1B — Protected Inverting Preamp (`U1A`)
- `U1A` (`U1.3` to `GND`) inverts `IN_BUF` through `R2` (`10 kΩ`).
- Feedback uses `R_GAIN_MIN` (`1 kΩ`) + `RV1` (`A100k` rheostat) in parallel with `R_GAIN_FAIL` (`1 MΩ`) and `C_HF` (`47 pF` `C0G`), providing smooth audio-taper control from `-0.10×` (`-20 dB`) to `-9.17×` (`+19.25 dB`), bounded `-100×` gain if a pot wire breaks, and a `36.9 kHz` HF pole at max gain.

### Stages 2 & 3 — `0.1%`-Matched Unity-Gain Precision Rectifier (`U1B`, `U1C`, `D1_D2`)
- `R3`, `R4`, `R5`, `R6`, `R7`, `R8A`, and `R8B` are all `10 kΩ ±0.1%` (`25 ppm/°C`) thin-film resistors, with `R4+R5 = 20.00 kΩ` feedforward and `R8A+R8B = 20.00 kΩ` feedback.
- `D1_D2` (`BAT54S`) improves negative swing margin at `U1B_OUT` by `~0.35 V` while `R8A+R8B = 20 kΩ` locks full-wave output to $V_{\text{RECT\_OUT}} = +1.000\,|V_{\text{PREAMP\_OUT}}|$ with `≤ 0.80%` worst-case half-cycle asymmetry.

### Stage 4 — Active Zero-Deadzone Peak Detector & Attack/Release (`U2C`)
- `U2C` (`+` = `RECT_OUT`, `OUT` → `D3.A`, `D3.K` → `-`) places low-leakage `1N4148WS` (`D3`) inside the feedback loop, removing the `~0.65 V` deadband and thermal drift (`< 5 mV` threshold).
- `ATK_IN` charges `C2` (`1 µF` film) through `R_ATK_MIN` (`470 Ω`, capping peak charge current at `~21 mA`) + `RV2` (`A50k`), giving $\tau_{\text{atk}} \approx 0.47\text{ ms to }50.5\text{ ms}$.
- `R9` is deleted so `ENV_CAP` = `ENV_NODE` directly (eliminating the `9.1%` release droop). Discharge flows through `R10` (`10 kΩ`) + `RV3` (`A1M`), giving $\tau_{\text{rel}} = 10\text{ ms to }1.01\text{ s}$.

### Stage 5 — Linearized `OFFSET`, In-Loop Feedback & Protected Outputs (`U1D`, `U2A`)
- `R_ENV_PROT` (`10 kΩ`) isolates `U1D+` (`U1.12`) from `C2` during rail brownouts.
- `RV4` (`B10k`) between `R11` (`1 kΩ` to `+12V`) and `R12` (`1 kΩ` to `-12V`) produces `±9.63 V` with $R_{\text{th}} \in [0.92\text{ k}\Omega, 3.00\text{ k}\Omega]$. With `R14` removed and `R13 = 18 kΩ`, `OUT_CLAMP` achieves `1.476×–1.529×` envelope gain (`3.5%` variation vs. `12%`) and **`±5.09 V`** near-linear offset (`CW` → `+OUT`).
- `R16A`/`R16B` (`470 Ω + 470 Ω`, `0.5 W` `1210`) and `R19A`/`R19B` (`470 Ω + 470 Ω`, `0.5 W` `1210`) safely handle continuous `±12 V` output-to-output clashes (`0.269 W` per resistor, `1.86×` continuous margin). Midpoint `BAV99` clamps (`D_OUT`, `D_INV_OUT`) shunt ESD/overvoltage spikes into the bypassed rails, while `R15`/`R18` tap the clamp nodes (`§3.5`, compensated locally by `C_OUT1`/`C_OUT2 = 100 pF` `C0G`).

### Stage 6 — In-Loop Precision LED Current Sink (`U2B`)
- `ENV_NODE` drives `U2B+` via `R20` (`10 kΩ`). `D4` (`3 mm` LED) sits inside `U2B`'s loop with `R_LED` (`2.2 kΩ`) to `GND`, producing $I_{\text{LED}} = V_{\text{ENV}} / 2.2\text{ k}\Omega$ (`0.00 mA` idle glow, up to `~4.5 mA` peak) regardless of LED color/$V_f$. `D_LED_CLAMP` (`1N4148WS`) clamps reverse swings at `-0.65 V`.

---

## 5. Complete Pin-Level Netlist

Pin conventions: `U1`/`U2` = `TL074HIDR` (`SOIC-14`); 2-pin passives = `.1`, `.2`; polarized caps = `.+`, `.-`; 2-pin diodes & LED (`1N4148WS`, `B5819W`, `LED`) = `.K` (Pin 1) and `.A` (Pin 2); `SOT-23` dual series diodes (`BAV99`, `BAT54S`) = `.1` (`A1`), `.2` (`K2`), `.3` (`COM = K1/A2`); pots = `.1` (CCW), `.2` (Wiper), `.3` (CW); jacks = `.S` (Sleeve), `.T` (Tip), `.TN` (Tip-Normal); test points (`TP1`–`TP8`) = `.1`.

| Net Name | Connected Pins |
|---|---|
| **`+12V_IN`** | `J4.9`, `J4.10`, `D_PWR_P.A` |
| **`-12V_IN`** | `J4.1`, `J4.2`, `D_PWR_N.K` |
| **`+12V_PROT`** | `D_PWR_P.K`, `R_PWR_P.1` |
| **`-12V_PROT`** | `D_PWR_N.A`, `R_PWR_N.1` |
| **`+12V`** | `R_PWR_P.2`, `C3.+`, `C_DEC1.1`, `C_DEC3.1`, `U1.4` (`V+`), `U2.4` (`V+`), `D_IN.2` (`K2`), `D_OUT.2` (`K2`), `D_INV_OUT.2` (`K2`), `R11.1`, `TP2.1` |
| **`-12V`** | `R_PWR_N.2`, `C4.-`, `C_DEC2.1`, `C_DEC4.1`, `U1.11` (`V-`), `U2.11` (`V-`), `D_IN.1` (`A1`), `D_OUT.1` (`A1`), `D_INV_OUT.1` (`A1`), `R12.1`, `TP3.1` |
| **`GND`** | `J4.3`, `J4.4`, `J4.5`, `J4.6`, `J4.7`, `J4.8`, `C3.-`, `C4.+`, `C_DEC1.2`, `C_DEC2.2`, `C_DEC3.2`, `C_DEC4.2`, `J1.S`, `J1.TN`, `R1.2`, `U1.3` (`U1A+`), `U1.5` (`U1B+`), `U1.10` (`U1C+`), `C2.2`, `RV3.2`, `RV3.3`, `J2.S`, `U2.3` (`U2A+`), `J3.S`, `R_LED.2`, `TP1.1` |
| **`IN_TIP`** | `J1.T`, `R_IN_PROT.1` |
| **`IN_AC_PRE`** | `R_IN_PROT.2`, `C1.1` |
| **`IN_AC`** | `C1.2`, `R1.1`, `D_IN.3` (`COM`), `R_IN_BUF.1` |
| **`U2D_IN`** | `R_IN_BUF.2`, `U2.12` (`U2D+`) |
| **`IN_BUF`** | `U2.14` (`U2D_OUT`), `U2.13` (`U2D-`), `R2.1`, `TP4.1` |
| **`U1A_INV`** | `R2.2`, `U1.2` (`U1A-`), `R_GAIN_MIN.1`, `R_GAIN_FAIL.1`, `C_HF.1` |
| **`GAIN_POT_1`** | `R_GAIN_MIN.2`, `RV1.1` |
| **`PREAMP_OUT`** | `U1.1` (`U1A_OUT`), `RV1.2`, `RV1.3`, `R_GAIN_FAIL.2`, `C_HF.2`, `R3.1`, `R4.1`, `TP5.1` |
| **`U1B_INV`** | `R3.2`, `U1.6` (`U1B-`), `R6.1`, `D1_D2.2` (`K2`, `D1.K`) |
| **`U1B_OUT`** | `U1.7` (`U1B_OUT`), `D1_D2.3` (`COM`, `D1.A`/`D2.K`) |
| **`RECT_HW`** | `D1_D2.1` (`A1`, `D2.A`), `R6.2`, `R7.1` |
| **`FF_MID`** | `R4.2`, `R5.1` |
| **`U1C_INV`** | `R5.2`, `R7.2`, `U1.9` (`U1C-`), `R8A.1` |
| **`RECT_FB_MID`** | `R8A.2`, `R8B.1` |
| **`RECT_OUT`** | `U1.8` (`U1C_OUT`), `R8B.2`, `U2.10` (`U2C+`), `TP6.1` |
| **`U2C_OUT`** | `U2.8` (`U2C_OUT`), `D3.A` |
| **`ATK_IN`** | `D3.K`, `U2.9` (`U2C-`), `R_ATK_MIN.1` |
| **`ATK_POT_1`** | `R_ATK_MIN.2`, `RV2.1` |
| **`ENV_NODE`** | `RV2.2`, `RV2.3`, `C2.1`, `R10.1`, `R_ENV_PROT.1`, `R20.1` |
| **`REL_POT_TOP`** | `R10.2`, `RV3.1` |
| **`U1D_IN`** | `R_ENV_PROT.2`, `U1.12` (`U1D+`) |
| **`OFF_TOP`** | `R11.2`, `RV4.1` |
| **`OFF_BOT`** | `R12.2`, `RV4.3` |
| **`OFF_WIPER`** | `RV4.2`, `R13.1` |
| **`U1D_INV`** | `R13.2`, `R15.1`, `C_OUT1.1`, `U1.13` (`U1D-`) |
| **`U1D_OUT`** | `U1.14` (`U1D_OUT`), `C_OUT1.2`, `R16A.1` |
| **`OUT_CLAMP`** | `R16A.2`, `R15.2`, `D_OUT.3` (`COM`), `R16B.1`, `R17.1`, `TP7.1` |
| **`OUT_TIP`** | `R16B.2`, `J2.T` |
| **`U2A_INV`** | `R17.2`, `R18.1`, `C_OUT2.1`, `U2.2` (`U2A-`) |
| **`U2A_OUT`** | `U2.1` (`U2A_OUT`), `C_OUT2.2`, `R19A.1` |
| **`INV_OUT_CLAMP`** | `R19A.2`, `R18.2`, `D_INV_OUT.3` (`COM`), `R19B.1`, `TP8.1` |
| **`INV_OUT_TIP`** | `R19B.2`, `J3.T` |
| **`U2B_IN`** | `R20.2`, `U2.5` (`U2B+`) |
| **`U2B_OUT`** | `U2.7` (`U2B_OUT`), `D4.A`, `D_LED_CLAMP.K` |
| **`LED_K`** | `D4.K`, `D_LED_CLAMP.A`, `U2.6` (`U2B-`), `R_LED.1` |
| **`NC`** | `J2.TN`, `J3.TN` |

---

## 6. Practical PCB Layout & Assembly Guidelines

1. **JLCPCB Economic Single-Sided SMT Assembly**: Place all 49 SMT components on `F.Cu` (`U1`, `U2`, `0603`/`1206`/`1210` resistors, `0603` ceramic caps, `D6.3×5.4mm` SMD electrolytics, `SOD-123`/`SOD-323`/`SOT-23` diodes) so JLCPCB populates the board in a single Economic SMT pass.
2. **Later Manual THT Mounting & Height Clearances**:
   - Front-panel THT parts (`J1`–`J3`, `RV1`–`RV4`, `D4`) mount on `F.Cu` and align to the `3U` Eurorack front panel (`~10.5 mm` board-to-panel standoff).
   - `J4` (`2×5` shrouded IDC header) mounts on **`B.Cu`** (rear side) with silkscreen `RED STRIPE / -12V` marking Pins `1–2`.
   - `C1` and `C2` (`B32529D1105J000`, `7.2 × 6.0 × 11.0 mm` box film) exceed `10.5 mm` if mounted upright on `F.Cu`; mount `C1` and `C2` on **`B.Cu`** (same hand-soldering pass as `J4`) so `F.Cu` clears the front panel cleanly.
   - `TP1`–`TP8` (`Ronghe RH-5001` through-board test pins, **DNP** in PCBA BOM) are plated through-hole pads accessible from **`B.Cu`**, allowing bare-pad probing or optional rear-side pin installation (`F.Cu` remains flush behind the front panel, and probing works with the module mounted to the faceplate). Label each pad clearly on `B.SilkS` (`TP1 GND`, `TP2 +12V`, `TP3 -12V`, `TP4 IN_BUF`, `TP5 PREAMP`, `TP6 RECT`, `TP7 OUT`, `TP8 INV_OUT`) and keep `≥ 2.5–3.0 mm` clip clearance around adjacent `J4`/`C1`/`C2` bodies.
3. **Critical Layout Rules**:
   - Place `C_DEC1`–`C_DEC4` (`100 nF`) within `< 3–5 mm` of `U1.4`, `U1.11`, `U2.4`, and `U2.11` with direct vias to the ground plane.
   - Keep `C_HF` (`47 pF`) and `R_GAIN_FAIL` (`1 MΩ`) close to `U1.1`/`U1.2` to minimize stray capacitance at the summing node.
   - Keep the `ATK_IN` / `ENV_NODE` traces (`U2.9`, `D3.K`, `C2.1`) compact and guarded away from `PREAMP_OUT`, clock/power traces, and test-point THT pads.
   - Give `R16A/B` and `R19A/B` (`1210`, `0.5 W`) generous copper pad/pour area for thermal relief during continuous output-to-output rail clashes.
4. **Potentiometer Rotation Verification**:
   - `RV1` (`GAIN`, `A100k`): `1` = `GAIN_POT_1`, `2+3` = `PREAMP_OUT` → clockwise increases gain (`-0.10×` → `-9.17×`).
   - `RV2` (`ATK`, `A50k`): `1` = `ATK_POT_1`, `2+3` = `ENV_NODE` → clockwise lengthens attack (`0.47 ms` → `50.5 ms`).
   - `RV3` (`Release`, `A1M`): `1` = `REL_POT_TOP`, `2+3` = `GND` → clockwise lengthens release (`10 ms` → `1.01 s`).
   - `RV4` (`OFFSET`, `B10k`): `1` = `OFF_TOP` (`+9.63 V`), `3` = `OFF_BOT` (`-9.63 V`), `2` = `OFF_WIPER` → clockwise pushes `OFF_WIPER` negative and `U1D` (`OUT`) **positive** (`-5.09 V` → `+5.09 V`).
