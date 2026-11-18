# Envelope Follower — Netlist, BOM & KiCad Capture Guide

This reference provides the complete Bill of Materials, 35-net connection list, and manual KiCad capture checklist for the improved Eurorack Envelope Follower based on Hagiwo's original design, updated for modern Texas Instruments **TL074H** quad op-amps (source: [`ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md)).

---

## Integrated Circuit Improvements

1. **Dual TL074H Layout (6 Active Op-Amps Total)**:
    - **U1 (TL074H)**: 4 channels used ($U1A$ Input Gain, $U1B$ Half-Wave Rectifier, $U1C$ Precision Summer, $U1D$ Output Buffer & Offset).
    - **U2 (TL074H)**: 2 channels used ($U2A$ Inverting Output Buffer, $U2B$ LED Driver Buffer).
    - **Unused Channels Terminated ($U2C$, $U2D$)**: Configured as unity-gain followers with non-inverting inputs ($+$) tied to `GND`. This prevents floating inputs, random IC oscillation, and excessive supply current draw.
2. **High-Frequency Power Decoupling**:
    - Added four $100\text{ nF}$ ceramic decoupling capacitors (`C5`–`C8`) placed directly at the $V_{CC+}$ (Pin 4) and $V_{CC-}$ (Pin 11) power pins of each TL074H IC.
3. **Gain Stage Stability**:
    - Added `R_GAIN_MIN` ($1\text{ k}\Omega$) in series with the `GAIN 100k` potentiometer. This prevents shorting the closed-loop feedback path to $0\,\Omega$ at minimum pot travel.
4. **Reverse Polarity Protection**:
    - Added Schottky protection diodes (`D4`, `D5` e.g., `B5819W` / `1N5817`) on the $+12\text{V}$ and $-12\text{V}$ Eurorack supply rails.
5. **Output Short Circuit Protection**:
    - $1\text{ k}\Omega$ series protection resistors (`R16`, `R19`) on both `OUT` and `INV_OUT` jacks.

---

## Comprehensive Netlist Specification

### 1. Full Bill of Materials (BOM)

| Reference | Value / Part | Description / Package | Notes |
| :--- | :--- | :--- | :--- |
| **U1, U2** | **TL074H** | Quad JFET Op-Amp (SOIC-14, TSSOP-14, or DIP-14) | Texas Instruments TL074H (`TL074HIDR`, `C2878713`) |
| **C1** | $4.7\,\mu\text{F}$ | Non-polarized MLCC (`0805`) / Film Capacitor, 25V | AC Input Coupling (`C354262`) |
| **C2** | $1\,\mu\text{F}$ | Ceramic (`0603`) / Film Capacitor, 25V | Envelope Smoothing Cap (`C559769`) |
| **C3, C4** | $4.7\,\mu\text{F}$ | Electrolytic Capacitor (`4x5.4mm`), 50V | Bulk Power Rail Decoupling (`C5246584`) |
| **C5–C8** | $100\text{ nF}$ | Ceramic Capacitor (`0603`), 50V (X7R) | High-Frequency IC Decoupling (`C14663`) |
| **R1** | $1\text{ M}\Omega$ | `0603` 1% Thick Film / 1/4W Metal Film | Input Pulldown (`C22935`) |
| **R2–R7, R10, R11, R12, R13, R14, R15, R17, R18, R20, R22** | $10\text{ k}\Omega$ | `0603` 1% Thick Film / 1/4W Metal Film | Rectifier & Buffer Networks (`C25804`) |
| **R_GAIN_MIN, R9, R16, R19** | $1\text{ k}\Omega$ | `0603` 1% Thick Film / 1/4W Metal Film | Protection & Stability (`C21190`) |
| **R8, R21** | $22\text{ k}\Omega$ | `0603` 1% Thick Film / 1/4W Metal Film | Rectifier & LED Current Limit (`C31850`) |
| **R23** | $33\text{ k}\Omega$ | `0603` 1% Thick Film / 1/4W Metal Film | LED Bias Network (`C4216`) |
| **RV_GAIN** | $100\text{ k}\Omega$ | Potentiometer (Alpha RD901F-40-00D) | Input Gain Control (`Manual THT`) |
| **RV_ATK** | $50\text{ k}\Omega$ | Potentiometer (Alpha RD901F-40-00D) | Attack Time Control (`Manual THT`) |
| **RV_REL** | $1\text{ M}\Omega$ | Potentiometer (Alpha RD901F-40-00D) | Release Time Control (`Manual THT`) |
| **RV_OFFSET** | $100\text{ k}\Omega$ | Potentiometer (Alpha RD901F-40-00D) | DC Offset Adjust (`Manual THT`) |
| **D1, D2, D3** | `1N4148W` | Fast Switching Signal Diode (`SOD-123`) | Precision Rectifier & Peak Charging (`C81598`) |
| **D4, D5** | `B5819W` | Schottky Rectifier Diode (`SOD-123`) | Power Input Reverse Polarity Protection (`C8598`) |
| **LED1** | 3mm LED | Standard Red/Blue/Green LED | Signal Level Indicator (`Manual THT`) |
| **J_IN, J_OUT, J_INV_OUT** | 3.5mm Jack | Thonkiconn (`WQP-PJ398SM`) Switched Mono Jack | Eurorack Audio/CV I/O (`Manual THT`) |
| **J_PWR** | 2x5 Header | 10-pin Eurorack Shrouded Power Header | $\pm 12\text{V}$, GND Power Input (`Manual THT`) |

### 2. Net Connection List (35 Nets)

```text
NET +12V_RAW
    J_PWR Pin 9, Pin 10
    D4 Anode

NET -12V_RAW
    J_PWR Pin 1, Pin 2
    D5 Cathode

NET +12V
    D4 Cathode
    U1 Pin 4 (V+)
    U2 Pin 4 (V+)
    C3 Pin 1 (+)
    C5 Pin 1
    C7 Pin 1
    R11 Pin 1

NET -12V
    D5 Anode
    U1 Pin 11 (V-)
    U2 Pin 11 (V-)
    C4 Pin 2 (-)
    C6 Pin 1
    C8 Pin 1
    R12 Pin 2
    R23 Pin 2

NET GND
    J_PWR Pins 3, 4, 5, 6, 7, 8
    J_IN Sleeve
    J_OUT Sleeve
    J_INV_OUT Sleeve
    R1 Pin 2
    U1 Pin 3 (U1A +), Pin 5 (U1B +), Pin 10 (U1C +)
    U2 Pin 3 (U2A +), Pin 10 (U2C +), Pin 12 (U2D +)
    C2 Pin 2 (-)
    C3 Pin 2 (-)
    C4 Pin 1 (+)
    C5 Pin 2, C6 Pin 2, C7 Pin 2, C8 Pin 2
    RV_REL Pin 1 & Wiper Pin 2
    R14 Pin 2
    R22 Pin 1

NET SIGNAL_IN
    J_IN Tip
    C1 Pin 1

NET AC_IN
    C1 Pin 2
    R1 Pin 1
    R2 Pin 1

NET GAIN_FB_IN
    R2 Pin 2
    U1 Pin 2 (U1A -)
    RV_GAIN Pin 1

NET GAIN_FB_MID
    RV_GAIN Wiper Pin 2 / Pin 3
    R_GAIN_MIN Pin 1

NET OUT_GAIN
    U1 Pin 1 (U1A Out)
    R_GAIN_MIN Pin 2
    R3 Pin 1
    R5 Pin 1

NET HALF_WAVE_IN
    R3 Pin 2
    U1 Pin 6 (U1B -)
    D1 Cathode
    R4 Pin 1

NET HALF_WAVE_OP_OUT
    U1 Pin 7 (U1B Out)
    D1 Anode
    D2 Anode

NET HALF_WAVE_NODE
    D2 Cathode
    R4 Pin 2
    R7 Pin 1

NET SUM_TOP_MID
    R5 Pin 2
    R6 Pin 1

NET SUM_IN
    R6 Pin 2
    R7 Pin 2
    U1 Pin 9 (U1C -)
    R8 Pin 1

NET RECT_OUT
    U1 Pin 8 (U1C Out)
    R8 Pin 2
    D3 Anode

NET ATK_IN
    D3 Cathode
    RV_ATK Pin 1

NET ENV_FILT
    RV_ATK Wiper Pin 2 / Pin 3
    C2 Pin 1 (+)
    R9 Pin 1

NET LED_IN
    R9 Pin 2
    R10 Pin 1
    U1 Pin 12 (U1D +)
    R20 Pin 1

NET REL_NODE
    R10 Pin 2
    RV_REL Pin 3

NET OFFSET_HI
    R11 Pin 2
    RV_OFFSET Pin 3

NET OFFSET_LO
    R12 Pin 1
    RV_OFFSET Pin 1

NET OFFSET_WIPER
    RV_OFFSET Wiper Pin 2
    R13 Pin 1

NET OFFSET_SUM_IN
    R13 Pin 2
    R14 Pin 1
    U1 Pin 13 (U1D -)
    R15 Pin 1

NET OUT_BUF_NODE
    U1 Pin 14 (U1D Out)
    R15 Pin 2
    R16 Pin 1
    R17 Pin 1

NET SIGNAL_OUT
    R16 Pin 2
    J_OUT Tip

NET INV_SUM_IN
    R17 Pin 2
    U2 Pin 2 (U2A -)
    R18 Pin 1

NET INV_BUF_NODE
    U2 Pin 1 (U2A Out)
    R18 Pin 2
    R19 Pin 1

NET SIGNAL_INV_OUT
    R19 Pin 2
    J_INV_OUT Tip

NET LED_BUF_IN
    R20 Pin 2
    U2 Pin 5 (U2B +)

NET LED_DRV
    U2 Pin 6 (U2B -)
    U2 Pin 7 (U2B Out)
    R21 Pin 1

NET LED_ANODE
    R21 Pin 2
    LED1 Anode

NET LED_CATHODE
    LED1 Cathode
    R22 Pin 2
    R23 Pin 1

NET U2C_TERM
    U2 Pin 8 (U2C Out)
    U2 Pin 9 (U2C -)

NET U2D_TERM
    U2 Pin 14 (U2D Out)
    U2 Pin 13 (U2D -)
```

---

## Manual KiCad Schematic Capture Steps

If capturing the schematic manually in KiCad instead of generating it via SKiDL in [Stage 3](../tutorial/stage-3-skidl.md):

### Step 1: Project Setup & Symbol Libraries
- [ ] Open KiCad and create a new project: `EnvelopeFollower.kicad_pro`.
- [ ] Open Schematic Editor (`EnvelopeFollower.kicad_sch`).
- [ ] Place power symbols: `+12V`, `-12V`, and `GND`.

### Step 2: Component Placement & Op-Amp Allocation
- [ ] Place **U1** as `TL074` (4 units: U1A, U1B, U1C, U1D + Power unit U1_Power).
- [ ] Place **U2** as `TL074` (4 units: U2A, U2B, U2C, U2D + Power unit U2_Power).
- [ ] Terminate unused op-amps:
    - Wire U2C Pin 9 ($-$) to U2C Pin 8 ($\text{Out}$); wire U2C Pin 10 ($+$) to `GND`.
    - Wire U2D Pin 13 ($-$) to U2D Pin 14 ($\text{Out}$); wire U2D Pin 12 ($+$) to `GND`.

### Step 3: Input & Gain Stage Capture
- [ ] Wire `J_IN` (3.5mm jack) $\to$ `C1` ($4.7\,\mu\text{F}$) $\to$ `R1` ($1\text{ M}\Omega$ to GND) and `R2` ($10\text{ k}\Omega$).
- [ ] Connect `R2` to U1A Pin 2 ($-$). Wire U1A Pin 3 ($+$) to `GND`.
- [ ] Connect U1A Pin 2 to `RV_GAIN` Pin 1. Wire `RV_GAIN` wiper to `R_GAIN_MIN` ($1\text{ k}\Omega$), and `R_GAIN_MIN` to U1A Pin 1 ($\text{Out}$).

### Step 4: Precision Rectifier Capture
- [ ] **Half-Wave Rectifier (U1B)**:
    - Wire U1A Pin 1 via `R3` ($10\text{ k}\Omega$) to U1B Pin 6 ($-$).
    - Wire U1B Pin 5 ($+$) to `GND`.
    - Connect 1N4148 Diode `D1` Cathode to Pin 6 ($-$), Anode to Pin 7 ($\text{Out}$).
    - Connect 1N4148 Diode `D2` Anode to Pin 7 ($\text{Out}$), Cathode to `R4` ($10\text{ k}\Omega$).
    - Loop `R4` back to Pin 6 ($-$).
- [ ] **Summing Stage (U1C)**:
    - Wire U1A Pin 1 via `R5` ($10\text{ k}\Omega$) in series with `R6` ($10\text{ k}\Omega$) to U1C Pin 9 ($-$).
    - Wire node after `D2` Cathode via `R7` ($10\text{ k}\Omega$) to U1C Pin 9 ($-$).
    - Connect U1C Pin 10 ($+$) to `GND`.
    - Wire feedback resistor `R8` ($22\text{ k}\Omega$) between U1C Pin 9 ($-$) and Pin 8 ($\text{Out}$).

### Step 5: Peak Detector & Buffer Stage Capture
- [ ] Connect U1C Pin 8 ($\text{Out}$) via Diode `D3` (Anode at U1C Pin 8, Cathode to `RV_ATK` Pin 1).
- [ ] Wire `RV_ATK` wiper to `C2` ($1\,\mu\text{F}$ cap to GND) and `R9` ($1\text{ k}\Omega$).
- [ ] Connect `R9` to `R10` ($10\text{ k}\Omega$), `RV_REL` ($1\text{ M}\Omega$ pot to GND), U1D Pin 12 ($+$), and `R20` ($10\text{ k}\Omega$).
- [ ] Wire Offset network: $+12\text{V} \to \text{R11} (10\text{ k}\Omega) \to \text{RV\_OFFSET} (100\text{ k}\Omega) \to \text{R12} (10\text{ k}\Omega) \to -12\text{V}$. Wire wiper via `R13` ($10\text{ k}\Omega$) to U1D Pin 13 ($-$) with `R14` ($10\text{ k}\Omega$) to GND and `R15` ($10\text{ k}\Omega$) feedback.
- [ ] Wire U1D Pin 14 ($\text{Out}$) via `R16` ($1\text{ k}\Omega$) to `J_OUT` Tip.

### Step 6: Inverted Output & LED Driver Capture
- [ ] Wire U1D Pin 14 via `R17` ($10\text{ k}\Omega$) to U2A Pin 2 ($-$). Connect U2A Pin 3 ($+$) to `GND`. Wire `R18` ($10\text{ k}\Omega$) feedback and output resistor `R19` ($1\text{ k}\Omega$) to `J_INV_OUT` Tip.
- [ ] Connect `R20` to U2B Pin 5 ($+$). Wire U2B Pin 6 ($-$) directly to Pin 7 ($\text{Out}$). Connect Pin 7 via `R21` ($22\text{ k}\Omega$) to `LED1` Anode.
- [ ] Wire `LED1` Cathode to `R22` ($10\text{ k}\Omega$ to GND) and `R23` ($33\text{ k}\Omega$ to $-12\text{V}$).

### Step 7: Power Decoupling & Protection Capture
- [ ] Place `J_PWR` (2x5 Shrouded Header).
- [ ] Connect `+12V_RAW` through Schottky diode `D4` to `+12V`.
- [ ] Connect `-12V_RAW` through Schottky diode `D5` to `-12V`.
- [ ] Place bulk electrolytic caps `C3` ($4.7\,\mu\text{F}$ $+12\text{V}$ to GND) and `C4` ($4.7\,\mu\text{F}$ $-12\text{V}$ to GND).
- [ ] Place high-frequency decoupling caps `C5`, `C6` next to U1 Power Unit, and `C7`, `C8` next to U2 Power Unit.

### Step 8: ERC & PCB Preparation
- [ ] Run Electrical Rules Check (**ERC**). Resolve any unconnected pin warnings or power flag errors (`PWR_FLAG` on `+12V`, `-12V`, `GND` if required).
- [ ] Assign Footprints (`SOIC-14_3.9x8.7mm_P1.27mm` for TL074H, `0603`/`0805` SMD passives, and `SOD-123` diodes).
- [ ] Save schematic, export Netlist, and proceed to PCB Layout!
