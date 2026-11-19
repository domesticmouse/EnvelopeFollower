# Envelope Follower — Improved Circuit Specification (Stage 3)

> **Source Documents:** [`EnvelopeFollower.md`](../stage-2/EnvelopeFollower.md) and [`EnvelopeFollowerImprovements.md`](../stage-2/EnvelopeFollowerImprovements.md)  
> **BOM Companion:** [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md)  
> **Op-Amps:** `2× TL074H` (`TL074HIDR`, `SOIC-14`, 8/8 stages active — 0 unused stages)  
> **Assembly Strategy:** 49 SMD components for JLCPCB Economic SMT assembly; 10 populated THT parts (`J1`–`J3`, `RV1`–`RV4`, `J_PWR`, `D4`, and film `C2`) mounted manually later, plus 8 optional **DNP** THT test points (`TP1`–`TP8`, Ronghe `RH-5001`)  
> **Supply Rails:** Dual `±12 V` Eurorack (`+12Vin`, `GND`, `-12Vin` → Schottky-protected `±12V_PROT`, `~±11.55 V` nominal)

---

## 1. Functional Overview & Architectural Decisions

This Stage 3 design incorporates the analog circuit improvements and Eurorack protections from `EnvelopeFollowerImprovements.md` while honoring all user hardware constraints (`2× TL074H` SOIC-14, `U2C`/`U2D` peak detector and buffer, improved pot values `A100k`/`A50k`/`A1M`/`B10k`, SMD JLCPCB construction, and THT jacks/pots/IDC header/3 mm LED mounted later).

### Resolved Conflicts & Ambiguities

| Topic | Source Tension / User Constraint | Stage 3 Resolution & Rationale |
|---|---|---|
| **Op-Amp Assignment (`U2C` & `U2D`)** | `EnvelopeFollowerImprovements.md` §4 assigned `U1D` as Peak Detector, `U2A` as `ENV_RAW` buffer, and `U2C`/`U2D` as the offset summer/inverter. User required **`U2C` and `U2D` for the active zero-deadzone peak detector and buffer**. | Preserve the original stage roles of `U1A`–`U1C` (Preamp, HWR, FWR Summer), `U2B` (LED driver), `U2A` (`INV_OUT` stage), and `U1D` (`OUT` stage), and assign **`U2C` = Active Zero-Deadzone Peak Detector** (`D3` in feedback) and **`U2D` = `ENV_RAW` Unity Buffer** (`ENV_RAW_BUF`). `U2A` acts as the exact-`1.00x` Inverting Offset Summer (`INV_OUT`) and `U1D` acts as the `-1.00x` Unity Output Inverter (`OUT`), delivering full Option B performance (`0–10 V` headroom, `0.00%` gain modulation, CW-positive `OFFSET`, 0 unused gates). |
| **`TL074H` (`SOIC-14`) Characteristics** | User specified **`TL074H` (SOIC)**. | Selected **`TL074HIDR`** (LCSC `C2878713`, Extended). Per TI's `TL074H` datasheet: $V_{CM}$ spans $(V_{CC}- + 1.5\text{ V})$ all the way up to **$V_{CC}+$** (`0 V` positive headroom — critical for `U2C`/`U2D`/`U2B` operating from `0 V` to `+10.5 V`), output swings within `~115 mV` of `VCC+` / `~105 mV` of `VCC-`, differential input is limited only by supply-rail clamps (safe for `U2C` peak detection), `V_os = 1 mV` typ, `I_b = 1 pA` typ, `SR = 20 V/µs`, `GBW = 5.25 MHz`, `I_sc = 26 mA`, phase-reversal-free, and EMI/RF filtered. |
| **Preamp (`U1A`) with `RV1 = A100k`** | `Improvements.md` §2.1 suggested `R2 = 100k` + `RV1 = A1M` (`100 kΩ` input Z), while §3.3 also documented the `10k / 100k` scaling. User adopted **`RV1 = A100k`**. | Keep **`R2 = 10 kΩ` (`1%`)** and insert **`R26 (R_gain_min) = 1 kΩ` (`1%`)** in series with `RV1 = A100k` (`-0.10x` to `-10.10x` gain, eliminating `0 Ω` dead-mute and wiper-stop dropouts). Add **`C9 = 47 pF`** (`NP0`, `f_c = 33.5 kHz` at max gain) across `R26 + RV1`, add anti-parallel **`1N4148W` clamps (`D5`, `D6`)** on `U1A.IN-` to `GND`, relocate **`R1 = 1 MΩ`** to `IN_JACK → GND`, and tie **`J1.TN → GND`**. *(Trade-off: input Z is `10 kΩ`; raising input Z to `100 kΩ` would require `RV1 = A1M`.)* |
| **Input AC Coupling `C1`** | With `R2 = 10 kΩ`, `1 µF` gives `f_c = 15.9 Hz` (`-2.1 dB` at `20 Hz`). | Retain `≥4.7 µF` (`f_c ≤ 3.39 Hz` into `10 kΩ`). Specify **`10 µF 50 V X7R 1206`** (`C5449000`) so even under worst-case `12 V` DC offset on `J1`, capacitance stays `≥ 4.7 µF` (`f_c ≤ 3.4 Hz`), while keeping `C1` compact and JLCPCB SMT compatible. |
| **Attack/Release (`RV2 = A50k`, `RV3 = A1M`, `C2`, `R10`)** | Original `R9 = 1 kΩ` added `~9%` sag and `R10 = 10 kΩ` caused `84%` divider collapse; `Improvements.md` §1.2 illustrated `A20k/A2M/470nF`. User adopted **`RV2 = A50k`** and **`RV3 = A1M`**. | Delete `R9` (`ENV_CAP` = `ENV_RAW`). Add **`R28 (R_atk_min) = 470 Ω`** in series with `RV2 = A50k` (bounds peak `C2` charge current to `~22.3 mA < 26 mA` `TL074H` limit). Raise **`R10` to `47 kΩ` (`1%`)** and retain **`C2 = 1 µF` film**: yields **`0.47–50.5 ms` attack**, **`47 ms–1.05 s` release**, and cuts worst-case opposite-extreme divider loss from `84%` to `51.8%` (`≤ 18%` loss for `ATK ≤ 10 ms`). |
| **`C2` Assembly Choice (`1 µF` Film)** | Live JLCPCB search for `1uF film` and `470nF film` returned **zero SMD film parts** (all stocked film caps are THT `Plugin`, led by `WIMA MKS2` `C92673`). `X7R` MLCCs lose `50–80%` capacitance under `10 V` DC bias and suffer microphonics/leakage. | Specify **`C2 = WIMA MKS2C041001F00JSSD` (`1 µF 63 V ±5%`, `P = 5.00 mm`, `7.2 × 5.0 × 10.0 mm`, LCSC `C92673`)** as a **Manual THT** component mounted later alongside the jacks/pots/LED/IDC header. Placing `C2` on `B.Cu` avoids the `10.5 mm` front-panel standoff constraint (`10.0 mm` body height). Keeps JLCPCB assembly 100% Economic SMD. |
| **`OFFSET` (`RV4 = B10k`) Scaling** | `Improvements.md` §1.3 noted `R11 = R12 = 1 kΩ` (`±4.8 V` offset) or `470 Ω` (`±5.0 V` offset). | Use **`R11 = R12 = 470 Ω` (`1%`)** (consolidates with `R28`) + **`R13 = 20 kΩ` (`1%`)**, giving **`±5.15 V`** clean linear offset on `±11.55 V` protected rails (`<3.3%` loading bow, `0.00%` gain shift). Wire `R11` (`+12V_PROT`) to `RV4` CW (`Pin 3`) so CW rotation moves `OUT` positively. |
| **Rectifier Symmetry (`U1B`, `U1C`)** | Original `R8 = 22 kΩ` gave `1.1x` gain and `U1B` saturated near `+10 V`. | Adopt **`-0.5x` HWR** (`R3 = 20k`, `R6 = 10k`, `R7 = 10k`, `R4 + R5 = 20k + 20k`, `R8A + R8B = 20k + 20k` `1%`) + **`C10 = 15 pF`** (`NP0`). Gives exact `1.00x` unity rectification, keeps `U1B.OUT` within `-6.2 V`, and reuses `10k`/`20k` BOM lines. |
| **LED Driver (`U2B`, `D4`)** | Original `-2.79 V` cathode bias bled `~30–40 µA` at `0 V` idle. | Delete `R20`–`R23`. Wire `U2B` as a **closed-loop current sink** fed from `ENV_RAW_BUF`: `D4` in feedback, **`R29 = 2.2 kΩ`** (`0–4.5 mA` for standard 3 mm LED; `4.7 kΩ` for ultrabright), **`D7 = 1N4148W`** anti-parallel clamp, **`C13 = 100 pF`** (`NP0`) compensation, and **`R30 = 1 MΩ`** pull-up to `+12V_PROT` (`+25 mV` threshold → guaranteed `0.00 mA` at silence). |
| **Eurorack Power & Output Protections** | Original schematic lacked header, reverse polarity protection, decoupling, and fault-rated output resistors. | Add **`J_PWR` (`2×5` shrouded IDC, THT)**, series **`B5819W` (`SOD-123`)** Schottkys (`D10`, `D11`), **`R24`/`R25 = 10 Ω` (`1206` `0.25 W`)** RC surge resistors, **`C3`/`C4 = 22 µF 35 V`** SMD electrolytics (`5 × 5.4 mm`), **`4× 100 nF 50 V X7R` (`0603`)** IC decoupling (`C5`–`C8`), **`BAV99` (`SOT-23`)** rail clamps (`D8`, `D9`), and **`1 kΩ ±1% 1 W` (`2512` SMD)** output resistors (`R16`, `R19`, `C54315`). |
| **Bench Test Points (`TP1`–`TP8`, `RH-5001`)** | All active stages and protected rails use SMD pads with no easy probe hooks; probing virtual-ground `IN-` pins or `ENV_RAW` (`C2`) directly degrades stability/timing. | Add **`8` optional THT test points (`TP1`–`TP8`, Ronghe `RH-5001`, marked DNP)** on `GND`, `±12V_PROT`, `PREAMP_OUT`, `HALF_WAVE`, `RECT_OUT`, `PEAK_DET`, and `ENV_RAW_BUF`. Mount on `B.Cu` (rear) if populated so nothing interferes with the `10.5 mm` front-panel standoff. Intentionally omit `IN-` summing nodes and raw `ENV_RAW` (`C2`). |

---

## 2. Signal Flow & Topology

```text
POWER:
  J_PWR (2x5 IDC, THT)
    ├── +12Vin ──► [D10 B5819W] ──► [R24 10Ω 1206] ──┬──► +12V_PROT ──► [C3 22µF 35V] ──► GND
    │                                                 └──► U1.4 (+ C5 100nF), U2.4 (+ C7 100nF)
    └── -12Vin ◄── [D11 B5819W] ◄── [R25 10Ω 1206] ◄──┬── -12V_PROT ──► [C4 22µF 35V] ──► GND
                                                      └──► U1.11 (+ C6 100nF), U2.11 (+ C8 100nF)

SIGNAL:
  J1 IN (THT, TN→GND) ─┬─ [R1 1M → GND]
                       └─ [C1 10µF 50V 1206] ─ [R2 10k 1%] ─► [U1A Preamp: (R26 1k + RV1 A100k) || C9 47pF, D5/D6 1N4148W on IN-]
                                                                    │ (PREAMP_OUT, Av = -0.10x to -10.10x)
                                ┌── [R4+R5 40k (20k+20k 1%)] ───────┼── [R3 20k 1%] ──► [U1B -0.5x HWR: D1, D2, R6 10k 1%]
                                │                                                               │
                                └──────────────────────────► [U1C Summer: R7 10k 1%, (R8A+R8B 40k 1%) || C10 15pF] ◄──┘
                                                                    │ (RECT_OUT = +1.00 * |PREAMP_OUT|)
                                                                    ▼
                                                       [U2C Active Zero-Deadzone Peak Detector]
                                                        (D3 1N4148W inside FB loop)
                                                                    │ (PEAK_DET)
                                                       [R28 470Ω] + [RV2 A50k]
                                                                    │ (ENV_RAW)
                                                           ┌────────┴─────────┐
                                                 [C2 1µF 63V Film]     [R10 47k + RV3 A1M] ──► GND
                                                 (WIMA MKS2, THT)
                                                           │
                                                   [U2D Unity Buffer]
                                                           │ (ENV_RAW_BUF)
                                             ┌─────────────┴─────────────┐
                                             ▼                           ▼
                               [U2B LED Current Sink]      [U2A Inv Summer (-1.00x || C11 47pF)] ◄── [RV4 B10k + R11/R12 470Ω → R13 20k]
                                (D4 3mm LED in FB,                │ (INV_DRV = -1.00*ENV_RAW_BUF - 0.50*V_OFF)
                                 D7 1N4148W clamp,                ├──► [D9 BAV99 ±12V] ─► [R19 1k 1W 2512] ─► J3 INV_OUT (THT, TN open)
                                 C13 100pF, R29 2.2k,             ▼
                                 R30 1M → +12V_PROT)       [U1D Unity Inverter (-1.00x || C12 47pF)]
                                                                  │ (ENV_OUT = +1.00*ENV_RAW_BUF + 0.50*V_OFF)
                                                                  └──► [D8 BAV99 ±12V] ─► [R16 1k 1W 2512] ─► J2 OUT (THT, TN open)

TEST POINTS (Optional THT, Ronghe RH-5001, DNP, B.Cu):
  TP1: GND          TP2: +12V_PROT    TP3: -12V_PROT    TP4: PREAMP_OUT
  TP5: HALF_WAVE    TP6: RECT_OUT     TP7: PEAK_DET     TP8: ENV_RAW_BUF
```

---

## 3. Stage-by-Stage Electrical Specifications & `TL074H` Pinout

### Op-Amp Pin Map (`U1`, `U2` = `TL074HIDR`, `SOIC-14`)

| Unit | IC / Pins (`IN+`, `IN-`, `OUT`) | Stage Function | Common-Mode Range Used | Output Swing / Margin |
|---|---|---|---|---|
| `U1A` | `TL074H` (`3`, `2`, `1`) | Inverting Preamp (`GAIN` `A100k`, `-0.10x` to `-10.10x`) | `0 V` | `±11.4 V` max (`±10 V` nominal) |
| `U1B` | `TL074H` (`5`, `6`, `7`) | `-0.5x` Half-Wave Rectifier | `0 V` | `-6.2 V` to `+0.65 V` |
| `U1C` | `TL074H` (`10`, `9`, `8`) | `1.00x` Full-Wave Summing Amp | `0 V` | `0 V` to `+11.4 V` |
| `U1D` | `TL074H` (`12`, `13`, `14`) | `OUT` Unity Output Inverter (`-1.00x` of `INV_DRV`) | `0 V` | `±11.4 V` (`0–10 V` + `±5.15 V` offset) |
| `U2A` | `TL074H` (`3`, `2`, `1`) | `INV_OUT` Inverting Offset Summer (`-1.00x` + `-0.50x`) | `0 V` | `±11.4 V` (`0 to -10 V` + `∓5.15 V` offset) |
| `U2B` | `TL074H` (`5`, `6`, `7`) | Closed-Loop LED Current Sink (`D4` in FB) | `0 V` to `+10.5 V` | `~+1.6 V` to `+11.4 V` |
| `U2C` | `TL074H` (`10`, `9`, `8`) | Active Zero-Deadzone Peak Detector (`D3` in FB) | `0 V` to `+10.5 V` | `-11.4 V` (idle/hold) to `+11.2 V` (peak) |
| `U2D` | `TL074H` (`12`, `13`, `14`) | `ENV_RAW` Unity-Gain Buffer (`ENV_RAW_BUF`) | `0 V` to `+10.5 V` | `0 V` to `+10.5 V` |

- **Power Supply Pins:** `U1.4`, `U2.4` = `+12V_PROT` (`+11.55 V` typ); `U1.11`, `U2.11` = `-12V_PROT` (`-11.60 V` typ).
- **Protected Rail Drop & Power Budget:** `2× TL074H` quiescent = `~7.5 mA` (`940 µA/ch`); `RV4` divider = `~2.1 mA`; `LED` at `+10 V` = `~4.5 mA` (`~14 mA` max normal draw on `+12V`, `~10 mA` on `-12V`). `B5819W` (`~0.30 V`) + `10 Ω` `R24`/`R25` (`~0.10–0.15 V`) leaves **`+11.55 V / -11.60 V`**. `R24`/`R25` + `C3`/`C4` (`22 µF`) provides a `723 Hz` RC supply ripple filter.
- **Output Fault Thermal Margin:** Under a direct opposite-rail short (`+11.4 V` output patched into `-12 V` PSU = `23.4 V`), `R16`/`R19` (`1 kΩ`, `2512`, `1.0 W`) dissipates `0.55 W` (`55%` of rated `1.0 W`).
- **LED Current Sink Transfer:** `R29 = 2.2 kΩ`, `R30 = 1 MΩ` → `I_LED = 0.00 mA` for `ENV_RAW_BUF ≤ +25 mV`, rising linearly at `0.455 mA/V` to **`4.53 mA` at `+10 V`** independent of LED forward voltage.

### Bench Test Points (`TP1`–`TP8`, Ronghe `RH-5001`, Optional THT / DNP)

| RefDes | Net | Connected Circuit Node | Nominal / Bench Verification Signal (`1 kHz ±5 V` Sine, `GAIN = 1.0x`, `OFFSET = 0 V`) | Probing & Layout Notes |
|---|---|---|---|---|
| `TP1` | `GND` | Reference ground plane | `0.00 V` | Ground clip anchor for DMM/scope during rear `B.Cu` testing. |
| `TP2` | `+12V_PROT` | Post-Schottky / RC positive rail | `+11.55 V` typ | Verify protected positive supply before signal testing (SMD-only net). |
| `TP3` | `-12V_PROT` | Post-Schottky / RC negative rail | `-11.60 V` typ | Verify protected negative supply before signal testing (SMD-only net). |
| `TP4` | `PREAMP_OUT` | `U1A.OUT` (`1`) | `±5.0 V` (`-0.10x` to `-10.10x` range, `±11.4 V` max) | Calibrate `GAIN` (`RV1`) and check AC-coupled preamp headroom before rectification. |
| `TP5` | `HALF_WAVE` | `D2.A` / `R6.2` / `R7.1` | `0 V` and `-2.5 V` half-waves (`-0.5x` of positive `PREAMP_OUT`) | SMD-only net; isolates `U1B` / `D1` / `D2` half-wave rectifier faults. |
| `TP6` | `RECT_OUT` | `U1C.OUT` (`8`) | `0 V` to `+5.0 V` full-wave pulses (`+1.00 × |PREAMP_OUT|`) | SMD-only net; verifies `100%` half-cycle symmetry prior to peak detector. |
| `TP7` | `PEAK_DET` | `D3.K` / `U2C.IN-` (`9`) / `R28.1` | Tracks `RECT_OUT` peaks down to mV (zero diode deadzone) | SMD-only net; keep pad stub short and probe with `10×` scope probe or `≥ 10 MΩ` DMM. |
| `TP8` | `ENV_RAW_BUF` | `U2D.OUT` (`14`) | `< +25 mV` idle (unpatched); `~+5.0 V` DC envelope (`0.47–50.5 ms` atk, `47 ms–1.05 s` rel) | SMD-only buffered envelope; zero loading on `C2` (`1 µF`) / `RV3` (`1 MΩ`) during `1 s` release checks. |

- **Mounting & Exclusions:** Leave `TP1`–`TP8` unpopulated for needle probing via plated holes, or optionally solder Ronghe `RH-5001` loops on **`B.Cu` (rear)** to preserve the `10.5 mm` front-panel standoff. Label both `RefDes` and net name on `B.SilkS`. Do **not** add test points on op-amp inverting summing junctions (`PREAMP_INV`, `RECT_INV`, `SUM_INV`, `SUM_OFF_INV`, `OUT_INV`) or directly on `ENV_RAW` (`C2.1`).

---

## 4. Complete Netlist (Net-by-Net Pin Connections)

Pin notation:
- Op-amps (`U1`, `U2`, `TL074HIDR` SOIC-14): pins `1`–`14`.
- Potentiometers (`RV1`–`RV4`): `L1` (CCW / Pin 1), `W` (Wiper / Pin 2), `L2` (CW / Pin 3).
- 3.5 mm Switched Jacks (`J1`–`J3`): `T` (Tip), `TN` (Tip Normalled Switch), `S` (Sleeve).
- Diodes (`D1`–`D7`, `D10`–`D11`): `A` (Anode), `K` (Cathode).
- Dual Series Diode `BAV99` (`D8`, `D9`): `1` (`A1`), `2` (`K2`), `3` (`K1/A2` common midpoint).
- Polarized Electrolytics (`C3`, `C4`): `+`, `-`. Non-polarized passives (`R*`, `C1`, `C2`, `C5`–`C13`): `1`, `2`.
- Optional Test Points (`TP1`–`TP8`, Ronghe `RH-5001`, DNP): `1`.

| Net Name | Connected Component Pins |
|---|---|
| **`+12Vin`** | `J_PWR.9`, `J_PWR.10`, `D10.A` |
| **`-12Vin`** | `J_PWR.1`, `J_PWR.2`, `D11.K` |
| **`+12V_DIODE`** | `D10.K`, `R24.1` |
| **`-12V_DIODE`** | `D11.A`, `R25.1` |
| **`+12V_PROT`** | `R24.2`, `C3.+`, `C5.1`, `C7.1`, `U1.4`, `U2.4`, `R11.1`, `R30.1`, `D8.2`, `D9.2`, `TP2.1` |
| **`-12V_PROT`** | `R25.2`, `C4.-`, `C6.1`, `C8.1`, `U1.11`, `U2.11`, `R12.1`, `D8.1`, `D9.1`, `TP3.1` |
| **`GND`** | `J_PWR.3`, `J_PWR.4`, `J_PWR.5`, `J_PWR.6`, `J_PWR.7`, `J_PWR.8`, `C3.-`, `C4.+`, `C5.2`, `C6.2`, `C7.2`, `C8.2`, `J1.S`, `J1.TN`, `R1.2`, `U1.3`, `D5.K`, `D6.A`, `U1.5`, `U1.10`, `C2.2`, `RV3.W`, `RV3.L2`, `R29.2`, `U2.3`, `U1.12`, `J2.S`, `J3.S`, `TP1.1` |
| **`IN_JACK`** | `J1.T`, `R1.1`, `C1.1` |
| **`IN_AC`** | `C1.2`, `R2.1` |
| **`PREAMP_INV`** | `R2.2`, `U1.2`, `R26.1`, `C9.1`, `D5.A`, `D6.K` |
| **`GAIN_MIN`** | `R26.2`, `RV1.L1` |
| **`PREAMP_OUT`** | `U1.1`, `RV1.W`, `RV1.L2`, `C9.2`, `R3.1`, `R4.1`, `TP4.1` |
| **`RECT_INV`** | `R3.2`, `U1.6`, `D1.K`, `R6.1` |
| **`U1B_OUT`** | `U1.7`, `D1.A`, `D2.K` |
| **`HALF_WAVE`** | `D2.A`, `R6.2`, `R7.1`, `TP5.1` |
| **`RECT_FF_MID`** | `R4.2`, `R5.1` |
| **`SUM_INV`** | `R5.2`, `R7.2`, `U1.9`, `R8A.1`, `C10.1` |
| **`RECT_FB_MID`** | `R8A.2`, `R8B.1` |
| **`RECT_OUT`** | `U1.8`, `R8B.2`, `C10.2`, `U2.10`, `TP6.1` |
| **`U2C_OUT`** | `U2.8`, `D3.A` |
| **`PEAK_DET`** | `D3.K`, `U2.9`, `R28.1`, `TP7.1` |
| **`ATK_MIN`** | `R28.2`, `RV2.L1` |
| **`ENV_RAW`** | `RV2.W`, `RV2.L2`, `C2.1`, `R10.1`, `U2.12` |
| **`REL_MID`** | `R10.2`, `RV3.L1` |
| **`ENV_RAW_BUF`** | `U2.14`, `U2.13`, `U2.5`, `R14.1`, `TP8.1` |
| **`LED_A`** | `U2.7`, `D4.A`, `D7.K`, `C13.1` |
| **`LED_K`** | `D4.K`, `U2.6`, `D7.A`, `C13.2`, `R29.1`, `R30.2` |
| **`OFF_TOP`** | `R11.2`, `RV4.L2` |
| **`OFF_BOT`** | `R12.2`, `RV4.L1` |
| **`OFF_WIPER`** | `RV4.W`, `R13.1` |
| **`SUM_OFF_INV`** | `R13.2`, `R14.2`, `U2.2`, `R18.1`, `C11.1` |
| **`INV_DRV`** | `U2.1`, `R18.2`, `C11.2`, `R17.1`, `D9.3`, `R19.1` |
| **`INV_OUT_JACK`** | `R19.2`, `J3.T` |
| **`OUT_INV`** | `R17.2`, `U1.13`, `R15.1`, `C12.1` |
| **`ENV_OUT`** | `U1.14`, `R15.2`, `C12.2`, `D8.3`, `R16.1` |
| **`OUT_JACK`** | `R16.2`, `J2.T` |
| **`NC`** | `J2.TN`, `J3.TN` |

---

## 5. Designator Changes vs. `EnvelopeFollower.md` (Traceability)

- **Deleted:** `R9` (`1 kΩ`, merged `ENV_CAP` into `ENV_RAW`), `R20` (`10 kΩ`, `U2B.IN+` fed directly by `ENV_RAW_BUF`), `R21`–`R23` (replaced by `U2B` current sink).
- **Modified:** `R1` (`1 MΩ` moved to `IN_JACK → GND`), `R3` (`10k → 20k`), `R4` & `R5` (`10k → 20k`), `R8` (`22k` split into `R8A + R8B = 20k + 20k`), `R10` (`10k → 47k`), `R11` & `R12` (`10k → 470 Ω`), `R13` (`10k → 20k`), `R14` (`GND` leg repurposed to `ENV_RAW_BUF → U2A.IN-`), `R16` & `R19` (upgraded to `1 kΩ 1 W 2512`), `C1` (`10 µF 50 V X7R 1206`), `C3` & `C4` (`4.7 µF → 22 µF 35 V` SMD), `U2` (`TL072 → TL074H`), `RV1`–`RV4` (`A100k`, `A50k`, `A1M`, `B10k`), `J_PWR` (`2×5` shrouded IDC).
- **Added:** `R24`, `R25` (`10 Ω 1206`), `R26` (`1 kΩ`), `R28` (`470 Ω`), `R29` (`2.2 kΩ`), `R30` (`1 MΩ`), `C5`–`C8` (`100 nF`), `C9`–`C13` (`NP0` compensation), `D5`–`D7` (`1N4148W`), `D8`–`D9` (`BAV99`), `D10`–`D11` (`B5819W`), `TP1`–`TP8` (optional DNP THT test points, Ronghe `RH-5001`).
