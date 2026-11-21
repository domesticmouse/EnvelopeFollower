# Envelope Follower (Improved Eurorack Revision) — Circuit Description & Build Specification

Improved production-oriented revision of [EnvelopeFollower.md](./EnvelopeFollower.md), incorporating the electrical fixes, usability upgrades, and Eurorack protections analyzed in [EnvelopeFollowerImprovements.md](./EnvelopeFollowerImprovements.md). Companion Bill of Materials and live JLCPCB/LCSC sourcing specification: [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md).

> **Design Highlights:** Uses **2 × `TL074H` (`TL074HIDR`, `SOIC-14`)** quad op-amps (`8` active op-amp units, `0` unused spares) with **`U2C` and `U2D` implementing the active zero-deadzone peak detector and dedicated `C2` buffer**, updated potentiometer tapers/values (**`A100k`**, **`A50k`**, **`A1M`**, **`B10k`**), full Eurorack power/I/O protections, **`8` rear `B.Cu` `DNP` through-hole test points (`TP1`–`TP8`, Ronghe `RH-5001`)**, and a **single-sided `B.Cu` SMT assembly** layout compatible with **JLCPCB Economic PCBA** (`F.Cu` reserved strictly for panel-facing THT controls, `B.Cu` rear THT reserved for `J4`, `C1`/`C2` box film capacitors, and optional `TP1`–`TP8`, all hand-soldered later).

---

## 1. Overview & Improvements Applied

This module converts a Eurorack audio or modulation signal (`IN`) into a smooth positive DC envelope (`OUT`), an inverted mirror (`INV_OUT`), and a linear, color-independent activity indicator (`LED`), powered from a standard Eurorack `±12 V` bus (`J4`).

### Key Specifications & Baseline Comparison

| Parameter | Original ([EnvelopeFollower.md](./EnvelopeFollower.md)) | Improved Revision (`EnvelopeFollowerImproved.md`) |
|---|---|---|
| **Op-Amps (`U1`, `U2`)** | `1 × TL074` + `1 × TL072` (`6` units) | **`2 × TL074H`** (`TL074HIDR`, `SOIC-14`, `8` active units, `0` spares) |
| **Assembly Split** | Generic THT/SMD | **Single-sided `B.Cu` SMT** (JLCPCB Economic PCBA, `49` SMD parts) + **rear `B.Cu` THT** (`J4`, `C1`, `C2`, plus `8` `DNP` test points `TP1`–`TP8`) + **front `F.Cu` THT** controls (`J1`–`J3`, `RV1`–`RV4`, `D4`) |
| **Input Stage (`J1`, `RV1`, `U1A`)** | Inverting `Z_in ≈ 9.9 kΩ`, `4.7 µF` cap, linear `100k` rheostat (`0×` deadzone), `J1.TN` floating | **High-Z non-inverting attenuator** (`Z_in ≈ 113 kΩ`, `f_c = 1.41 Hz`), `J1.TN → GND`, `R1 = 10 kΩ` + `BAT54S` (`D9`) clamp **ahead of `C1` (`1 µF 63 V` film)**, **`RV1 = A100k`** log pot + `4.7 kΩ` gain floor (`+0.45×` to `+10.04×`, `1 MΩ` open-wiper pull-down, `22 pF` HF comp) |
| **Full-Wave Rectifier (`U1B`, `U1C`)** | `+1.1×` gain (`R8 = 22 kΩ`), premature clipping | **Exact `1.00×` gain** (`R8 = R10 = 20 kΩ`, `1%`), symmetric saturation headroom |
| **Peak Detector & Buffer (`U2C`, `U2D`)** | Passive `1N4148` outside feedback (`~0.6 V` deadzone), `U1D +` tapped after `1 kΩ` `R9` (`-9.1%` release droop) | **`U2C` active zero-deadzone peak detector** (`D3` inside loop + `D5` anti-saturation clamp + `R11 = 200 kΩ` / `C10 = 100 pF` loop comp, `> 70°` phase margin) + **`U2D` dedicated unity-gain `C2` buffer** (`0 mV` diode deadzone, `0%` release tap droop) |
| **Attack & Release (`RV2`, `RV3`, `C2`)** | Linear `50k` `ATK` (`0 Ω` short risk), linear `1M` `Release`, X7R allowed for `C2` | **`RV2 = A50k`** log pot + `150 Ω` min series protection (`0.15 ms`–`50.15 ms`); **`RV3 = A1M`** log pot + `4.7 MΩ` open-wiper safety (`10 ms`–`835 ms`); **`C2 = 1 µF 63 V` film** (`P=5mm`) |
| **Output Gain & Offset (`U1D`, `RV4`, `U2A`)** | `2.25×`–`2.52×` gain (clips above `4.6 V`), `100k` `RV4` (`+12%` gain modulation, `72%` S-curve crowding, CW = negative `OUT`) | **Near-unity (`0.975×`) difference amplifier** (`0–10 V` unclipped tracking); **`RV4 = B10k`** linear pot (`R17 = R18 = 6.8 kΩ`) giving **`±4.69 V`** smooth linear offset (`< 1%` error, `±0.25%` gain flatness, **CW = positive `OUT`**) |
| **LED Driver (`U2B`, `D4`)** | Passive `-2.79 V` bias (`0.17–0.34 mA` dim output, `30 µA` idle glow on red/amber) | **Precision constant-current sink** (`0.5 mA/V · V_ENV_BUF`, `0.00 mA` dark idle, `5.00 mA` at `+10 V`, `V_f`-independent for any 3 mm LED color, `D6` reverse clamp) |
| **Eurorack Protections (`J4`, `D7`–`D11`, `R21`, `R24`)** | Unprotected bare power port, no decoupling caps, `1/4 W` `1 kΩ` output resistors | Shrouded keyed `2×5` `J4` + **`1N5819WS` (`D7`, `D8`)** reverse-polarity Schottkys + `10 Ω` RC rail filters (`R28`, `R29`) + **`47 µF 35 V`** bulk caps (`C3`, `C4`) + **`4 × 100 nF`** decoupling (`C5`–`C8`) + **`1 kΩ 1 W 2512`** fault-rated outputs (`R21`, `R24`) + **`BAT54S`** ESD/rail clamps (`D9`–`D11`) |

---

## 2. Signal Flow & Block Architecture Diagram

```text
====================================================================================================
 FRONT THT (F.Cu)             REAR THT (B.Cu)                 REAR SMT PCBA (B.Cu)
====================================================================================================

  J1 (IN Jack)
   ├─ TN ──▶ GND
   └─ Tip ──▶ [R1: 10k]──┬──▶ [C1: 1uF 63V Film]──▶ RV1 (GAIN: A100k, F.Cu)
                         │                            ├─ CW (3) ◀── C1
                      [D9: BAT54S]                    ├─ CCW(1) ──▶ [R2: 4.7k]──▶ GND
                      (±12V_PROT)                     └─ Wip(2) ──┬── [R3: 1M to GND]
                                                                  ▼
                                                         ( U1A: +11x Gain ) [R4=10k, R5=100k||C9=22pF]
                                                                  │ V_GAIN ──▶ [TP4]
                                            ┌─────────────────────┴──────────────────────┐
                                            ▼                                            ▼
                                  [R6: 10k]──( U1B: Half-Wave )                   [R8: 20k]
                                             w/ D1, D2 (1N4148WS) & R7=10k               │
                                            │                                            │
                                            └─────────[R9: 10k]──────────────────────────┴──▶( U1C: 1.00x Summer, R10=20k )
                                                                                                    │ V_RECT ──▶ [TP5]
                                            ┌───────────────────────────────────────────────────────┘
                                            ▼
                                 ( U2C: Active Peak Detector ) ◀──[C10: 100pF]──┐
                                  │     [D5: 1N4148WS clamp]                    │
                                  ▼                                        [R11: 200k]
                            [D3: 1N4148WS]──▶[R12: 150R]──▶ RV2 (ATK: A50k, F.Cu)│
                                                                 │ ENV_CAP       │
                                            ┌────────────────────┼───────────────┤
                                            ▼                    ▼               │
                                     [C2: 1uF 63V Film]   [R13: 10k]             │
                                     (B.Cu Rear THT)             │               │
                                                        RV3 (Release: A1M, F.Cu) │
                                                           || [R14: 4.7M]        │
                                                                 │               │
                                                                GND              │
                                                                                 │
                              ENV_CAP ──▶( U2D: Unity Buffer +1x )───────────────┴── V_ENV_BUF ──▶ [TP6]
                                                │
                 ┌──────────────────────────────┴───────────────────────────────┐
                 ▼                                                              ▼
       [R15: 100k] / [R16: 100k to GND]                              [R25: 10k] / [R26: 10k to GND]
                 │                                                              │
                 ▼                                                              ▼
       ( U1D: 0.975x Difference / OFFSET )                            ( U2B: LED Current Sink )
          ▲  ▲                                                           │              ▲
          │  └──[R20: 100k]── V_OUT_BUF                                  ▼              │
          └─────[R19: 100k]── RV4 (OFFSET: B10k, F.Cu)             [D4: 3mm LED (F.Cu)] │
                              (R17=6.8k +12V, R18=6.8k -12V)        || [D6: 1N4148WS]   │
                 │                                                       │              │
                 ├──────────────────────────┬──▶ [TP7]                   ├──▶───────────┘
                 ▼                          ▼                            ▼
          [D10: BAT54S]               [R22: 10k]                    [R27: 1k]──▶ GND
                 │                          ▼
          [R21: 1k 1W 2512]           ( U2A: Inv -1.00x, R23=10k )
                 │                          │
                 ▼                          ├──▶ [D11: BAT54S]   ──▶ [TP8] (V_INV_BUF)
          J2 (OUT Jack, F.Cu)               ▼
          (TN = NC)                   [R24: 1k 1W 2512]
                                            │
                                            ▼
                                      J3 (INV_OUT Jack, F.Cu)
                                      (TN = NC)

  Power / Reference TPs (B.Cu Rear THT, DNP):  [TP1] = +12V_PROT   [TP2] = -12V_PROT   [TP3] = GND
```

---

## 3. PCB Side Allocation & Manufacturing Strategy

The PCB is partitioned for **single-sided JLCPCB Economic PCBA** on the bottom side (`B.Cu`) followed by simple manual through-hole assembly of the panel interface (`F.Cu`) and rear THT components (`B.Cu`).

| Assembly Layer / Side | Process | Components | Qty | Notes |
|---|---|---|---|---|
| **`B.Cu` (Rear SMD)** | **JLCPCB Economic PCBA** (single-sided reflow) | `U1`, `U2` (`TL074HIDR` SOIC-14), `D1`–`D3`, `D5`–`D11` (`SOD-323` / `SOT-23`), `R1`–`R29` (`0603` / `2512`), `C3`–`C10` (`6.3×5.4 mm` / `0603`) | **`49`** | All SMT components placed strictly on `B.Cu`; **`0` SMT parts on `F.Cu`** so JLCPCB Economic single-sided assembly applies with zero double-sided surcharge. |
| **`B.Cu` (Rear THT — Populated)** | **Manual Hand-Solder** (after PCBA) | `J4` (`2×5` shrouded keyed IDC power header), `C1`, `C2` (`1 µF 63 V` `P=5mm` metallized polyester box film) | **`3`** | Mounted on `B.Cu` facing away from the front panel; `C1`/`C2` height (`~9.5 mm`) clears the rear Eurorack envelope cleanly without colliding with the `~10.5 mm` front-panel standoff. |
| **`B.Cu` (Rear THT — `DNP`)** | **Optional Hand-Solder** (`DNP` in BOM/PCBA) | `TP1`–`TP8` (`Ronghe RH-5001` `2.5 mm` black through-board test points, `TestPoint:TestPoint_Keystone_5000-5004_Miniature`, `Ø 1.0 mm` drill) | **`8 (DNP)`** | Excluded from JLCPCB SMT BOM & CPL (`DNP`). Leave unpopulated as probeable `1.0 mm` plated holes, or insert from `B.Cu` (`4.6 mm` rear height; trim `~3.0 mm` split pins flush on `F.Cu` before panel fitment). |
| **`F.Cu` (Front THT)** | **Manual Hand-Solder** (after panel fitment) | `J1`–`J3` (`WQP-PJ398SM` 3.5 mm mono jacks), `RV1`–`RV4` (`Alpha RD901F` 9 mm vertical pots: `A100k`, `A50k`, `A1M`, `B10k`), `D4` (`3 mm` round LED) | **`8`** | Reserved strictly for panel-facing controls. Loosely insert into `F.Cu`, bolt the `3U` front panel (`128.5 mm` height, `~10.5 mm` standoff) with M6/M7 nuts, seat `D4` into its `3.2 mm` hole, then solder from `B.Cu` for zero mechanical stress. |

### Layout & Eurorack Mechanical Guidelines (For Stage 4/5)
1. **Main PCB Height & Clearance:** Keep rear PCB height `≤ 108.0 mm` centered behind the `128.5 mm` `3U` Eurorack panel (`10.25 mm` top/bottom rail clearance).
2. **THT Courtyard Discipline on `B.Cu`:** Keep all `B.Cu` SMD parts outside the `F.Cu` jack/pot pin bands and mounting-lug holes, clustering SMDs in clear horizontal corridors between control rows.
3. **Decoupling & Grounding:** Place `C5`–`C8` (`100 nF`) `< 5 mm` from `U1`/`U2` pins `4` and `11` with immediate `GND` stitching vias before routing signals.
4. **Rear Test Point Placement & Labeling (`TP1`–`TP8`):**
   - Place `TP4`–`TP8` locally within `≤ 3 mm` of their respective op-amp output nets (`V_GAIN`, `V_RECT`, `V_ENV_BUF`, `V_OUT_BUF`, `V_INV_BUF`) rather than grouping AC and DC signals onto a single header strip (avoiding trace crosstalk). `TP1` (`+12V_PROT`), `TP3` (`GND`), and `TP2` (`-12V_PROT`) may sit near `J4` in an accessible rear corridor.
   - Connect `TP3` (`GND`) to the ground pour using **thermal-relief spokes** (not a solid flood) so optional hand-soldering of `RH-5001` is not heat-sunk by the plane.
   - Label every `TP1`–`TP8` on **`B.SilkS`** (and `F.SilkS` where space permits) with both designator and net name (e.g., `TP1 +12V_PROT`, `TP6 V_ENV_BUF`).
5. **JLCPCB Silkscreen QR Placeholder:** Reserve a `5 mm × 5 mm` clear square on `B.SilkS` for JLCPCB's automated assembly QR code.

---

## 4. Stage-by-Stage Circuit Description & Mathematical Analysis

### 4.1 Power Input, Reverse-Polarity Protection & Filtering (`J4`, `D7`, `D8`, `R28`, `R29`, `C3`–`C8`)
- **Connector (`J4`):** Shrouded, keyed `2×5` (`2.54 mm`) Eurorack IDC header on `B.Cu` following Doepfer A-100 pinout:
  - Pins `1, 2` = `-12V_IN` (red stripe)
  - Pins `3–8` = `GND` (all 6 pins bonded to ground plane)
  - Pins `9, 10` = `+12V_IN`
- **Reverse-Polarity Protection (`D7`, `D8`):** Series `1N5819WS` (`40 V, 1 A`, `SOD-323`) Schottky diodes block reversed bus cables with zero standby fault dissipation:
  - **`D7` (`+12 V` rail):** Anode (`A`) to `+12V_IN`, Cathode (`K`) to `+12V_FILT_IN`.
  - **`D8` (`-12 V` rail):** Cathode (`K`) to `-12V_IN`, Anode (`A`) to `-12V_FILT_IN`.
- **RC Rail Filtering & Bulk Storage (`R28`, `R29`, `C3`, `C4`):**
  - `R28` (`10 Ω`) and `R29` (`10 Ω`) feed downstream `47 µF 35 V` SMD aluminum electrolytic bulk capacitors `C3` (`+` to `+12V_PROT`, `-` to `GND`) and `C4` (`+` to `GND`, `-` to `-12V_PROT`), forming a `339 Hz` RC supply filter that damps hot-plug inrush spikes and switching-PSU ripple.
  - At total typical module current (`~7.5 mA` quiescent for `2 × TL074H` + `0–5 mA` LED = `~12.5 mA`), `D7`/`D8` drop `~0.28 V` and `R28`/`R29` drop `~0.12 V`, yielding **`±11.6 V`** protected internal rails (`+12V_PROT`, `-12V_PROT`).
- **Local IC Supply Decoupling (`C5`–`C8`):** Four `100 nF` (`50 V` X7R `0603`) ceramic capacitors placed `< 5 mm` from `U1` (`Pin 4`, `Pin 11`) and `U2` (`Pin 4`, `Pin 11`) to `GND`.

### 4.2 Stage 1 — High-Z Protected AC Input & Gain Stage (`J1`, `R1`–`R5`, `D9`, `C1`, `C9`, `RV1`, `U1A`)
- **Jack Normalization (`J1`):** Tip feeds `R1`; Sleeve connects to `GND`; normalled switch pin `TN` connects directly to `GND` so unplugged cables never inject hum.
- **ESD/Overvoltage Protection Ahead of `C1` (`R1`, `D9`):**
  - `R1` (`10 kΩ`) feeds `IN_CLAMP`, which is clamped to `+12V_PROT` and `-12V_PROT` by `D9` (`BAT54S`: Pin `1` `A` → `-12V_PROT`, Pin `2` `K` → `+12V_PROT`, Pin `3` `COM` → `IN_CLAMP`).
  - Placing `D9` **ahead of `C1`** ensures that `BAT54S` reverse leakage (`≤ 2 µA`) drains harmlessly through `R1` / `J1` and **cannot cross `C1`** into `U1A`'s `11×` DC-gain input (preventing false zero-deadzone baseline envelopes), while `R1` limits even `±24 V` sustained external faults to `~1.2 mA` (`14.4 mW` in `R1`).
- **AC Coupling & `A100k` Attenuator with Gain Floor (`C1`, `RV1`, `R2`, `R3`):**
  - `C1` (`1 µF 63 V` metallized polyester box film, `B.Cu` THT) blocks incoming DC offsets without piezoelectric microphonics or DC-bias distortion.
  - `RV1` (`A100k` log pot, `F.Cu`) has Pin `3` (`CW`) on `IN_POT_TOP` (`C1`), Pin `1` (`CCW`) returned to `GND` through `R2` (`4.7 kΩ` gain-floor resistor), and Pin `2` (`Wiper`) feeding `U1A +` (`Pin 3`) alongside open-wiper pull-down `R3` (`1 MΩ` to `GND`).
  - **Input Impedance & Cutoff:** $Z_{\text{in}} \approx 10\,\text{k}\Omega + 100\,\text{k}\Omega + 4.7\,\text{k}\Omega \parallel 1\,\text{M}\Omega \approx 113\,\text{k}\Omega$ (`f_c = 1.41 Hz` with `C1 = 1 µF`), matching the `~100 kΩ` Eurorack standard with `< 2%` variation over pot travel.
- **Fixed `+11.0×` Non-Inverting Gain (`U1A`, `R4`, `R5`, `C9`):**
  - `R4` (`10 kΩ` to `GND`) and `R5` (`100 kΩ` feedback, bypassed by `C9 = 22 pF` C0G giving `f_-3dB = 72 kHz` stability rolloff) set fixed gain $A_{v,\text{U1A}} = 1 + 100\,\text{k}\Omega / 10\,\text{k}\Omega = +11.0\times$.
  - **Overall Input Gain Span:**
    - **Minimum (`0%` CCW):** $\dfrac{4.7\,\text{k}\Omega}{114.7\,\text{k}\Omega} \times 0.99 \times 11.0 = \mathbf{+0.45\times}$ (`-6.9 dB` floor — accepts `±10 V` = `20 Vpp` hot Eurorack signals without clipping `U1A`, while avoiding a silent `0×` dead zone).
    - **Mid (`50%`, `A100k` ~15% log taper):** $\mathbf{+1.89\times}$ (`+5.5 dB` — ideal for `±5 V` audio/synth sources around 12 o'clock).
    - **Maximum (`100%` CW):** $\dfrac{104.7\,\text{k}\Omega}{114.7\,\text{k}\Omega} \times 0.99 \times 11.0 = \mathbf{+10.04\times}$ (`+20.0 dB` — matches baseline maximum gain).
  - **Zero Phase Reversal:** `TL074H` is phase-reversal immune and `V(U1A +)` never exceeds `±10.5 V` (`< +11.6 V`), remaining well inside its `[-11.6 V, +9.6 V]` linear input range at normal audio levels.

### 4.3 Stage 2 — Precision `1.00×` Full-Wave Rectifier (`U1B`, `U1C`, `R6`–`R10`, `D1`, `D2`)
- **Topology:** Classic 2-op-amp inverting precision full-wave rectifier scaled for **exact `1.00×` gain** (eliminating the original `+1.1×` premature clipping and consolidating `10k+10k` into a single `20 kΩ` `0603` Basic resistor).
- **Half-Wave Stage (`U1B`):** `R6` (`10 kΩ`) feeds `V_GAIN` to `U1B -` (`Pin 6`, `U1B +` at `GND`); `D1` (`1N4148WS`, `A` at `U1B OUT` Pin `7`, `K` at `U1B -`), `D2` (`1N4148WS`, `A` at `RECT_MID`, `K` at `U1B OUT`), and `R7` (`10 kΩ` from `RECT_MID` to `U1B -`).
- **Summing Stage (`U1C`):** `R8` (`20 kΩ`) feeds `V_GAIN` and `R9` (`10 kΩ`) feeds `RECT_MID` into `U1C -` (`Pin 9`, `U1C +` at `GND`), with `R10` (`20 kΩ`) feedback to `V_RECT` (`Pin 8`):
  $$V_{\text{RECT}} = +1.00\,\left|V_{\text{GAIN}}\right| \ge 0$$

### 4.4 Stage 3 — Active Zero-Deadzone Peak Detector (`U2C`), `C2` Buffer (`U2D`) & Attack/Release Core (`D3`, `D5`, `R11`–`R14`, `C10`, `RV2`, `RV3`, `C2`)
- **Active Zero-Deadzone Peak Detector (`U2C`, `D3`, `D5`, `R11`, `C10`):**
  - `V_RECT` drives `U2C +` (`Pin 10`).
  - `U2C OUT` (`Pin 8`) drives `D3` (`1N4148WS`, `A` at `Pin 8`, `K` at `RECT_DIODE_OUT`) → `R12` (`150 Ω` minimum attack protection) → `RV2` (`A50k`, `ATK` rheostat) → `C2` (`1 µF 63 V` film to `GND`, node `ENV_CAP`).
  - `U2D` (`Pins 12, 13, 14`) acts as a **unity-gain JFET/CMOS buffer** directly sensing `ENV_CAP` (`Pin 12` `+`, `Pin 13` `-` tied to `Pin 14` `OUT`, net `V_ENV_BUF`).
  - `V_ENV_BUF` feeds back to `U2C -` (`Pin 9`, net `PEAK_INV`) through `R11` (`200 kΩ`), closing the peak-detector loop around `D3`, `R12`, `RV2`, and `C2`. Because `D3` sits **inside `U2C`'s feedback loop**, signals down to a few millivolts charge `C2` cleanly with **`0 mV` diode deadzone** and zero temperature drift of `V_f`.
  - **Anti-Saturation Clamp (`D5`):** `1N4148WS` (`A` at `U2C -` Pin `9`, `K` at `U2C OUT` Pin `8`) clamps `U2C OUT` at `V_RECT - 0.55 V` whenever `V_RECT < V(ENV_CAP)` instead of saturating to `-11.6 V`, allowing `~55 ns` recovery (`20 V/µs` slew) on the next peak.
  - **Loop Compensation (`R11 = 200 kΩ`, `C10 = 100 pF` C0G):** Because `(R12 + RV2) · C2` introduces a variable `3.17 Hz`–`1.06 kHz` pole inside `U2C`'s loop, `C10` (`100 pF` directly across `U2C OUT` ↔ `U2C -`) paired with `R11` (`200 kΩ`) provides a high-frequency bypass zero (`τ_c = 20 µs`, `f_z = 7.96 kHz`), yielding **`70.4°` unity-gain crossover phase margin** and **`+19.3 dB` gain margin (`16.1°` phase margin)** at the worst-case RC/compensation notch across all `ATK` settings (`150 Ω` to `50.15 kΩ`) and diode impedances.
- **Attack & Release Dynamics (`RV2 = A50k`, `RV3 = A1M`, `R12`–`R14`, `C2`):**
  - **Attack (`RV2 = A50k`):** `R_atk = 150 Ω` (`0%` CCW) to `50.15 kΩ` (`100%` CW). Audio/log taper (`~15%` at midpoint = `7.5 kΩ`) spreads crisp percussive `0.15–7.7 ms` attacks across the lower half of rotation. Because `U2C` drives `D3` toward `+10.5 V` while `V(C2) < V_RECT`, charging acts as a fast active slew (`I_chg ≈ (10.5 V - V(C2)) / R_atk`) stopping cleanly at `V(C2) = V_RECT`.
  - **Release (`RV3 = A1M`, `R13 = 10 kΩ`, `R14 = 4.7 MΩ`):** `U2D`, `U1D`, and `U2B` tap `C2` exclusively via `U2D` (`~1 pA` input bias), and `R13` (`10 kΩ`) connects directly to `ENV_CAP`, completely eliminating the baseline `9.1%` release-dependent amplitude drop. `R14` (`4.7 MΩ`) parallels `RV3` (`A1M`) so an open wiper never latches the envelope high:
    - `0%` CCW: $\tau_{\text{rel}} = 10\,\text{k}\Omega \times 1\,\mu\text{F} = \mathbf{10.0\text{ ms}}$
    - `50%` (~15% taper, `150 kΩ || 4.7 MΩ`): $\tau_{\text{rel}} = \mathbf{155\text{ ms}}$
    - `100%` CW (`1 MΩ || 4.7 MΩ = 825 kΩ`): $\tau_{\text{rel}} = \mathbf{835\text{ ms}}$ (`~2.5 s` for `95%` decay).

### 4.5 Stage 4 — Unity Difference/Offset Output (`U1D`), Inverted Output (`U2A`) & Jack Protection (`R15`–`R24`, `RV4`, `D10`, `D11`, `J2`, `J3`)
- **Difference / DC Offset Stage (`U1D`, `RV4 = B10k`, `R15`–`R20`):**
  - Positive leg: `R15` (`100 kΩ`) from `V_ENV_BUF` to `U1D +` (`Pin 12`), and `R16` (`100 kΩ`) from `U1D +` to `GND`, giving $V_+ = 0.500\,V_{\text{ENV\_BUF}}$.
  - Offset divider: `RV4` (`B10k`, `10 kΩ` linear) sits between `R17` (`6.8 kΩ` to `+12V_PROT`, Pin `1` `CCW`) and `R18` (`6.8 kΩ` to `-12V_PROT`, Pin `3` `CW`), producing an unloaded wiper swing of $\pm 11.6\,\text{V} \times \frac{5\,\text{k}\Omega}{11.8\,\text{k}\Omega} = \pm 4.92\,\text{V}$ and Thevenin source resistance `R_pot,th = 4.84 kΩ` (extremes) to `5.90 kΩ` (center).
  - Inverting leg: `R19` (`100 kΩ`) from `RV4` wiper (`Pin 2`) to `U1D -` (`Pin 13`), with `R20` (`100 kΩ`) feedback to `V_OUT_BUF` (`Pin 14`).
  - **Transfer Function:**
    $$V_{\text{OUT\_BUF}} = \frac{1}{2}\left(1 + \frac{100\,\text{k}\Omega}{100\,\text{k}\Omega + R_{\text{pot,th}}}\right) V_{\text{ENV\_BUF}} - \left(\frac{100\,\text{k}\Omega}{100\,\text{k}\Omega + R_{\text{pot,th}}}\right) V_{\text{th}}$$
    - **Envelope Gain:** **`0.972×` (center) to `0.977×` (extremes)** — `±0.25%` gain flatness across full offset sweep, passing the entire `0–10 V` envelope completely unclipped!
    - **Offset Sweep:** **`-4.69 V` (CCW) to `+4.69 V` (CW)** with `< 1%` linearity error and **clockwise = more positive `OUT`**.
- **Inverted Output Stage (`U2A`, `R22`, `R23`):**
  - `U2A +` (`Pin 3`) → `GND`, `R22` (`10 kΩ`) from `V_OUT_BUF` to `U2A -` (`Pin 2`), `R23` (`10 kΩ`) feedback to `V_INV_BUF` (`Pin 1`):
    $$V_{\text{INV\_BUF}} = -1.00\,V_{\text{OUT\_BUF}}$$
- **Output Fault & ESD Protections (`D10`, `D11`, `R21`, `R24`, `J2`, `J3`):**
  - `D10` (`BAT54S` at `V_OUT_BUF`) and `D11` (`BAT54S` at `V_INV_BUF`) clamp op-amp outputs to `±12V_PROT` **behind** `R21` and `R24`.
  - `R21` and `R24` use **`1 kΩ` `2512` `1 W` `1%`** resistors (`C54315`), surviving continuous worst-case cross-patching (`-10.5 V` patched into external `+12 V` = `0.51 W` dissipation, `51%` of `1 W` rating) while isolating cable capacitance.
  - `J2.TN` and `J3.TN` are left **`NC`** (unconnected) so unplugged outputs are never shorted to `GND`.

### 4.6 Stage 5 — Precision Constant-Current LED Driver (`U2B`, `R25`–`R27`, `D4`, `D6`)
- **Connections:**
  - `R25` (`10 kΩ`) and `R26` (`10 kΩ`) divide `V_ENV_BUF` by `0.500` into `U2B +` (`Pin 5`, net `LED_REF_IN`).
  - `D4` (`3 mm` THT LED on `F.Cu`) sits in `U2B`'s feedback path (`Anode` at `U2B OUT` `Pin 7`, `Cathode` at `U2B -` `Pin 6`, net `LED_SENSE`), with `R27` (`1 kΩ` `0603` Basic) sensing current to `GND`.
  - `D6` (`1N4148WS`, `A` at `LED_SENSE`, `K` at `V_LED_DRV`) clamps reverse voltage across `D4` to `≤ 0.6 V` if `V_ENV_BUF` has sub-millivolt negative offset.
- **Performance:**
  $$I_{\text{LED}} = \frac{0.500 \cdot V_{\text{ENV\_BUF}}}{1\,\text{k}\Omega} = 0.50\,\text{mA/V} \cdot V_{\text{ENV\_BUF}}$$
  - Exact **`0.00 mA` OFF** at `0 V`, turning on below `~20 mV`, reaching **`2.50 mA` at `+5 V`** and **`5.00 mA` at `+10 V`**, completely independent of LED forward voltage (`1.8 V` red to `3.4 V` green/blue/white) with zero static `-12V` bleed.

---

## 5. Complete Pin-for-Pin Netlist & IC Pin Mapping

### 5.1 Op-Amp IC Pin Assignment (`U1 = TL074HIDR`, `U2 = TL074HIDR`)

| IC & Unit | Function | `+` Pin (Net) | `-` Pin (Net) | `OUT` Pin (Net) | Supply Pins |
|---|---|---|---|---|---|
| **`U1A`** | Input Gain (`+0.45×` to `+10.04×`) | `3` (`IN_WIPER`) | `2` (`IN_GAIN_INV`) | `1` (`V_GAIN`) | `4` (`+12V_PROT`), `11` (`-12V_PROT`) |
| **`U1B`** | Precision Rectifier Half-Wave | `5` (`GND`) | `6` (`RECT_INV`) | `7` (`RECT_OP_OUT`) | Shared on `U1` |
| **`U1C`** | Precision Rectifier `1.00×` Summer | `10` (`GND`) | `9` (`SUM_INV`) | `8` (`V_RECT`) | Shared on `U1` |
| **`U1D`** | Output `0.975×` Diff / `OFFSET` | `12` (`OUT_NONINV`) | `13` (`OUT_INV_NODE`) | `14` (`V_OUT_BUF`) | Shared on `U1` |
| **`U2A`** | Inverted Output (`-1.00×`) | `3` (`GND`) | `2` (`INV_SUM`) | `1` (`V_INV_BUF`) | `4` (`+12V_PROT`), `11` (`-12V_PROT`) |
| **`U2B`** | Constant-Current LED Driver | `5` (`LED_REF_IN`) | `6` (`LED_SENSE`) | `7` (`V_LED_DRV`) | Shared on `U2` |
| **`U2C`** | **Active Zero-Deadzone Peak Detector** | `10` (`V_RECT`) | `9` (`PEAK_INV`) | `8` (`PEAK_OP_OUT`) | Shared on `U2` |
| **`U2D`** | **Dedicated `C2` Unity Buffer (`+1×`)** | `12` (`ENV_CAP`) | `13` (`V_ENV_BUF`) | `14` (`V_ENV_BUF`) | Shared on `U2` |

### 5.2 Designator Cross-Reference (Original → Improved)

| Original Ref ([EnvelopeFollower.md](./EnvelopeFollower.md)) | Improved Ref(s) | Change Summary |
|---|---|---|
| `U1` (`TL074`), `U2` (`TL072`) | `U1`, `U2` (`2 × TL074HIDR`) | Upgraded to `TL074H` SOIC-14; `U2C`/`U2D` added for peak detector & buffer |
| `R1` (`1M`), `R2` (`10k`) | `R1` (`10k`), `R2` (`4.7k`), `R3` (`1M`), `R4` (`10k`), `R5` (`100k`) | Converted to high-Z non-inverting `A100k` attenuator + `+11×` gain |
| `R3`, `R4`, `R5+R6`, `R7`, `R8` | `R6` (`10k`), `R7` (`10k`), `R8` (`20k`), `R9` (`10k`), `R10` (`20k`) | Exact `1.00×` rectifier; `10k+10k` consolidated to single `20k` Basic |
| `R9` (`1k`), `R10` (`10k`) | Removed `R9`; `R12` (`150R`), `R13` (`10k`), `R14` (`4.7M`) | `150 Ω` min attack + direct `C2` tap + `4.7 MΩ` release safety |
| `R11`–`R15` | `R15`, `R16`, `R19`, `R20` (`100k`), `R17`, `R18` (`6.8k`) | `R14` omitted; converted to `0.975×` diff amp with `B10k` pot |
| `R16`, `R17`, `R18`, `R19` | `R21` (`1k 1W`), `R22` (`10k`), `R23` (`10k`), `R24` (`1k 1W`) | Output build-out resistors upgraded to `2512` `1 W` fault rating |
| `R20`–`R23` | `R25` (`10k`), `R26` (`10k`), `R27` (`1k`) | Converted to `0.5 mA/V` constant-current LED sink (`-12V` divider removed) |
| *(New)* | `R11` (`200k`), `R28` (`10R`), `R29` (`10R`) | Peak detector feedback + `±12 V` RC rail damping |
| `D1`–`D4` | `D1`–`D3`, `D4` (`3mm LED`), plus `D5`–`D11` | Added `D5` peak clamp, `D6` LED clamp, `D7`/`D8` `1N5819WS`, `D9`–`D11` `BAT54S` |
| `C1`–`C4` (+ `C5`–`C8` note) | `C1`, `C2` (`1µF 63V` film), `C3`, `C4` (`47µF 35V`), `C5`–`C8` (`100nF`), `C9` (`22pF`), `C10` (`100pF`) | Film caps on `B.Cu` THT, SMD bulk/decoupling/C0G comp caps on `B.Cu` SMT |
| `RV1`–`RV4` (`100k, 50k, 1M, 100k` lin) | `RV1` (`A100k`), `RV2` (`A50k`), `RV3` (`A1M`), `RV4` (`B10k`) | Audio tapers for `GAIN`/`ATK`/`Release`; linear `B10k` for `OFFSET` |

### 5.3 Complete Net-by-Net Connectivity Table (`60` Populated + `8` `DNP` Test Points = `68` Footprints, `170` Total Pins)

Every pin of all `60` populated components (`49` SMT on `B.Cu` + `3` THT on `B.Cu` + `8` THT on `F.Cu`) and all `8` rear `B.Cu` `DNP` test points (`TP1`–`TP8`) is explicitly mapped below:

| Net Name | Connected Component Pins |
|---|---|
| **`+12V_IN`** | `J4.9`, `J4.10`, `D7.A` |
| **`-12V_IN`** | `J4.1`, `J4.2`, `D8.K` |
| **`+12V_FILT_IN`** | `D7.K`, `R28.1` |
| **`-12V_FILT_IN`** | `D8.A`, `R29.1` |
| **`+12V_PROT`** | `R28.2`, `C3.+`, `C5.1`, `C7.1`, `U1.4`, `U2.4`, `R17.1`, `D9.2` (`K`), `D10.2` (`K`), `D11.2` (`K`), **`TP1.1`** |
| **`-12V_PROT`** | `R29.2`, `C4.-`, `C6.1`, `C8.1`, `U1.11`, `U2.11`, `R18.1`, `D9.1` (`A`), `D10.1` (`A`), `D11.1` (`A`), **`TP2.1`** |
| **`GND`** | `J4.3`, `J4.4`, `J4.5`, `J4.6`, `J4.7`, `J4.8`, `C3.-`, `C4.+`, `C5.2`, `C6.2`, `C7.2`, `C8.2`, `J1.S`, `J1.TN`, `R2.2`, `R3.2`, `R4.2`, `U1.5`, `U1.10`, `C2.2`, `R14.2`, `RV3.2`, `RV3.3`, `R16.2`, `U2.3`, `R26.2`, `R27.2`, `J2.S`, `J3.S`, **`TP3.1`** |
| **`IN_TIP`** | `J1.T`, `R1.1` |
| **`IN_CLAMP`** | `R1.2`, `D9.3` (`COM`), `C1.1` |
| **`IN_POT_TOP`** | `C1.2`, `RV1.3` (`CW`) |
| **`IN_POT_BOT`** | `RV1.1` (`CCW`), `R2.1` |
| **`IN_WIPER`** | `RV1.2` (`Wiper`), `R3.1`, `U1.3` (`U1A+`) |
| **`IN_GAIN_INV`** | `R4.1`, `U1.2` (`U1A-`), `R5.1`, `C9.1` |
| **`V_GAIN`** | `U1.1` (`U1A OUT`), `R5.2`, `C9.2`, `R6.1`, `R8.1`, **`TP4.1`** |
| **`RECT_INV`** | `R6.2`, `U1.6` (`U1B-`), `R7.1`, `D1.K` |
| **`RECT_OP_OUT`** | `U1.7` (`U1B OUT`), `D1.A`, `D2.K` |
| **`RECT_MID`** | `D2.A`, `R7.2`, `R9.1` |
| **`SUM_INV`** | `R8.2`, `R9.2`, `U1.9` (`U1C-`), `R10.1` |
| **`V_RECT`** | `U1.8` (`U1C OUT`), `R10.2`, `U2.10` (`U2C+`), **`TP5.1`** |
| **`PEAK_INV`** | `U2.9` (`U2C-`), `R11.2`, `C10.1`, `D5.A` |
| **`PEAK_OP_OUT`** | `U2.8` (`U2C OUT`), `C10.2`, `D5.K`, `D3.A` |
| **`RECT_DIODE_OUT`** | `D3.K`, `R12.1` |
| **`ATK_MID`** | `R12.2`, `RV2.1` (`CCW`) |
| **`ENV_CAP`** | `RV2.2`, `RV2.3` (`Wiper+CW`), `C2.1`, `R13.1`, `U2.12` (`U2D+`) |
| **`REL_MID`** | `R13.2`, `RV3.1` (`CCW`), `R14.1` |
| **`V_ENV_BUF`** | `U2.13` (`U2D-`), `U2.14` (`U2D OUT`), `R11.1`, `R15.1`, `R25.1`, **`TP6.1`** |
| **`OUT_NONINV`** | `R15.2`, `R16.1`, `U1.12` (`U1D+`) |
| **`OFF_TOP`** | `R17.2`, `RV4.1` (`CCW`) |
| **`OFF_BOT`** | `R18.2`, `RV4.3` (`CW`) |
| **`OFF_WIPER`** | `RV4.2` (`Wiper`), `R19.1` |
| **`OUT_INV_NODE`** | `R19.2`, `R20.1`, `U1.13` (`U1D-`) |
| **`V_OUT_BUF`** | `U1.14` (`U1D OUT`), `R20.2`, `D10.3` (`COM`), `R21.1`, `R22.1`, **`TP7.1`** |
| **`OUT_TIP`** | `R21.2`, `J2.T` |
| **`INV_SUM`** | `R22.2`, `R23.1`, `U2.2` (`U2A-`) |
| **`V_INV_BUF`** | `U2.1` (`U2A OUT`), `R23.2`, `D11.3` (`COM`), `R24.1`, **`TP8.1`** |
| **`INV_OUT_TIP`** | `R24.2`, `J3.T` |
| **`LED_REF_IN`** | `R25.2`, `R26.1`, `U2.5` (`U2B+`) |
| **`LED_SENSE`** | `U2.6` (`U2B-`), `D4.K` (`Pin 1`), `D6.A`, `R27.1` |
| **`V_LED_DRV`** | `U2.7` (`U2B OUT`), `D4.A` (`Pin 2`), `D6.K` |
| **`NC` (Unconnected)** | `J2.TN`, `J3.TN` |

### 5.4 Rear `B.Cu` Test Point Allocation (`TP1`–`TP8`, `Ronghe RH-5001`, `DNP`)

All `8` test points use `Connector:TestPoint` (`TestPoint:TestPoint_Keystone_5000-5004_Miniature`: `Ø 2.0 mm` circular pad, `Ø 1.0 mm` plated drill, `Ø 2.8 mm` silk ring, `Ø 3.3 mm` courtyard) on **`B.Cu`** for rear access behind the `3U` front panel, marked **`DNP`** (`Manual THT`, excluded from JLCPCB SMT BOM & CPL) so they can be probed bare or optionally populated with **Ronghe `RH-5001`** (`C5199801`, `2.5 mm` black nylon bead, `4.6 mm` above-board height, `7.6 ± 0.4 mm` overall length, `0.25 mm` split phosphor-bronze spring pins splayed to `1.4 mm` for `1.0 mm` snap-fit retention).

| Ref | Net | Source Pin | Expected Range / Signal | Diagnostic Purpose & Guardrails |
|---|---|---|---|---|
| **`TP1`** | `+12V_PROT` | Post-`D7`/`R28` | `+11.6 V` DC (`±0.2 V`) | Unpowered rail resistance check (`> 10 kΩ`) & powered `+12 V` rail verification |
| **`TP2`** | `-12V_PROT` | Post-`D8`/`R29` | `-11.6 V` DC (`±0.2 V`) | Unpowered rail resistance check (`> 10 kΩ`) & powered `-12 V` rail verification |
| **`TP3`** | `GND` | Ground plane | `0.00 V` reference | Rear-side oscilloscope ground-clip loop near signal TPs (connect via thermal-relief spokes) |
| **`TP4`** | `V_GAIN` | `U1.1` (`U1A OUT`) | `±10.5 V` max (`+0.45×`–`+10.04×`) | Low-Z Stage 1 output; confirms `J1`, `C1`, `RV1` (`GAIN`), idle DC (`±15 mV`), and headroom |
| **`TP5`** | `V_RECT` | `U1.8` (`U1C OUT`) | `0` to `+10.5 V` (`+\|V_GAIN\|`) | Low-Z Stage 2 output; confirms `1.00×` full-wave symmetry (`U1B`/`U1C`) and `75 mV` sensitivity |
| **`TP6`** | `V_ENV_BUF` | `U2.14` (`U2D OUT`) | `0` to `+10.5 V` DC envelope | Low-Z buffered copy of `C2`; measures `ATK` (`0.15–50 ms`) & `Release` (`10–835 ms`) with **zero probe loading on `ENV_CAP`** |
| **`TP7`** | `V_OUT_BUF` | `U1.14` (`U1D OUT`) | `0–10 V` env `± 4.69 V` offset | Pre-`R21` (`1 kΩ 1 W`) op-amp output; checks `R21` continuity (`1 kΩ` to `J2.T`) & isolates `U1D`/`RV4`/`D10` |
| **`TP8`** | `V_INV_BUF` | `U2.1` (`U2A OUT`) | `-V_OUT_BUF` (`-1.00×`) | Pre-`R24` (`1 kΩ 1 W`) op-amp output; checks `R24` continuity (`1 kΩ` to `J3.T`) & isolates `U2A`/`D11` |

*(Intentionally omitted nodes: `ENV_CAP` (`C2.1`) is high-Z (`4.7 MΩ` parallel bleed) so direct `1–10 MΩ` probing loads down `Release`—always probe `TP6` (`V_ENV_BUF`) instead; op-amp inverting inputs `IN_GAIN_INV`, `RECT_INV`, `SUM_INV`, `PEAK_INV`, `OUT_INV_NODE`, and `INV_SUM` are omitted to avoid adding stray pad capacitance to summing/compensation nodes.)*

---

## 6. Assembly, Control Polarity & Bring-Up Verification

### 6.1 Post-PCBA Manual Assembly Sequence
1. **Inspect `B.Cu` SMT assembly:** Confirm orientation of `U1`/`U2` (`SOIC-14` Pin `1`), `C3`/`C4` electrolytics (`+` stripe), `D1`–`D3`/`D5`–`D8` (`SOD-323` cathode band to Pad `1`), and `D9`–`D11` (`SOT-23`).
2. **Solder Rear `B.Cu` THT (`J4`, `C1`, `C2`, and Optional `TP1`–`TP8`):**
   - Install `J4` (`2×5` shrouded IDC header with key notch facing board interior/silkscreen outline) and `C1`, `C2` (`1 µF 63 V` `P=5mm` film caps) on `B.Cu`, soldering cleanly on `F.Cu` pads and trimming leads flush so nothing protrudes toward the front panel.
   - **Optional `TP1`–`TP8` (`Ronghe RH-5001`, `DNP`):** Leave unpopulated for bare plated-hole probing, or snap `RH-5001` loops into `B.Cu` (`4.6 mm` rear height), solder on `F.Cu`, and trim the `~3.0 mm` protruding split pins flush on `F.Cu` before mounting the front panel (alternatively, tack-solder from `B.Cu` later without removing the panel).
3. **Fit & Solder Front `F.Cu` Controls (`J1`–`J3`, `RV1`–`RV4`, `D4`):**
   - Insert `J1`–`J3` (`WQP-PJ398SM`), `RV1`–`RV4` (`A100k`, `A50k`, `A1M`, `B10k`), and `D4` (`3 mm` LED, `Pin 1` square pad = Cathode `K`, `Pin 2` round pad = Anode `A` — **do not trim `D4` leads yet**) onto `F.Cu` without soldering.
   - Slide the `3U` front panel over the shafts/bushings, tighten M6 jack nuts and M7 pot nuts finger-tight, push `D4`'s lens dome flush into its `3.2 mm` panel hole, then solder all `F.Cu` THT pins from `B.Cu` and trim leads.

### 6.2 Bench Bring-Up & Verification Checklist
1. **Unpowered Resistance Check:** Verify `> 10 kΩ` across **`TP1` (`+12V_PROT`)**, **`TP2` (`-12V_PROT`)**, and **`TP3` (`GND`)**, and confirm `J2.T` / `J3.T` read `1 kΩ` to **`TP7` (`V_OUT_BUF`)** / **`TP8` (`V_INV_BUF`)** (never `0 Ω` to `GND`).
2. **Power & Reverse-Polarity Test:** Power via `J4` (`±12 V` current-limited bench supply) with DMM/scope reference on **`TP3` (`GND`)**. Confirm **`TP1` (`+12V_PROT`) ≈ `+11.6 V`** and **`TP2` (`-12V_PROT`) ≈ `-11.6 V`**.
3. **Zero-Input Idle Check (`J1` unplugged, `OFFSET` centered):**
   - Verify **`TP4` (`V_GAIN`)**, **`TP5` (`V_RECT`)**, and **`TP6` (`V_ENV_BUF`)** are all within `±15 mV` of `0.00 V` (and `ENV_CAP` follows `TP6` without direct probe loading).
   - Confirm **`D4` (`LED`) is completely dark (`0.00 mA`)**.
   - Sweep `RV4` (`OFFSET`): confirm **`TP7` (`V_OUT_BUF`)** and `OUT` (`J2.T`) track smoothly and linearly from **`-4.69 V` (full CCW)** to **`+4.69 V` (full CW)**, while **`TP8` (`V_INV_BUF`)** and `INV_OUT` (`J3.T`) track `-OUT`. Return `RV4` to center (`OUT ≈ 0.00 V`).
4. **Zero-Deadzone & Dynamic Envelope Check:**
   - Set `RV1` (`GAIN`) to `100%` CW, `RV2` (`ATK`) to `0%` CCW, `RV3` (`Release`) to `30%`.
   - Inject a **`1 kHz`, `100 mVpp` (`50 mV` peak)** sine wave into `J1` (`IN`): confirm **`TP4` (`V_GAIN`) ≈ `1.00 Vpp`**, **`TP5` (`V_RECT`) ≈ `+0.50 V` peaks**, **`TP6` (`V_ENV_BUF`) ≈ `+0.50 V` DC**, and `OUT` rises to **`~+0.49 V`** (previously `0 V` below `D3`'s `~0.6 V` deadband).
   - Drop amplitude to **`15 mVpp`** (**`TP5` `V_RECT` ≈ `75 mV`**): confirm **`TP6` (`V_ENV_BUF`)**, `OUT`, and `D4` (`LED`) still track cleanly without deadband truncation.
   - Increase input to `2 Vpp` and burst/gate the tone: verify on **`TP6` (`V_ENV_BUF`)** that `ATK` (`A50k`) smoothly slows rising edges (`0.15 ms`–`50 ms`) and `Release` (`A1M`) smoothly scales falling tails (`10 ms`–`835 ms` `τ`) with zero probe loading on `C2` and zero level droop across fast vs. slow `Release` settings.
