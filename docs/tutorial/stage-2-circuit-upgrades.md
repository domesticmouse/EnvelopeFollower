# Stage 2: Interpreting Hagiwo's Sketch & Designing Production Upgrades

Start from the original hand-drawn reference schematic, [`EnvelopeFollower.webp`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.webp):

![Hagiwo's Original Envelope Follower Sketch](../images/EnvelopeFollower.webp)

## AI Agent Prompt

> *"Inspect `EnvelopeFollower.webp`. Trace every node and component in Hagiwo's Envelope Follower schematic, adapt the design for modern Texas Instruments `TL074H` quad op-amps (`SOIC-14`), apply Eurorack production safeguards (reverse-polarity protection, local decoupling, gain floor limiting, output protection, and unused op-amp termination), and write a complete BOM, 35-net connection list, and KiCad capture checklist to `ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md`."*

## Signal Flow: 6 Functional Blocks

Reading the sketch left-to-right and top-to-bottom breaks the analog circuit into six clean stages:

1. **Power Entry, Protection & Decoupling (`J_PWR`, `D4`–`D5`, `C3`–`C8`)**:
   Eurorack $\pm 12\text{V}$ and `GND` enter via a 2×5 shrouded 10-pin IDC header (`J_PWR`: Pins 1–2 `-12V_RAW`, Pins 3–8 `GND`, Pins 9–10 `+12V_RAW`) before feeding dual `TL074H` ICs (`U1`, `U2` Pin 4 $= +12\text{V}$, Pin 11 $= -12\text{V}$).
2. **AC Input Coupling & Gain Stage (`U1A`)**:
   `J_IN` passes through a non-polarized $4.7\,\mu\text{F}$ coupling capacitor (`C1`) with a $1\text{ M}\Omega$ input pulldown (`R1`) into an inverting amplifier (`U1A`, $R_2 = 10\text{ k}\Omega$ input, `RV_GAIN` $= 100\text{ k}\Omega$ feedback).
3. **Precision Full-Wave Rectifier (`U1B`, `U1C`)**:
   `U1B` forms an active half-wave stage (`R3`, `R4` $= 10\text{ k}\Omega$, `D1`, `D2` = 1N4148), while `U1C` sums the half-wave path (`R7` $= 10\text{ k}\Omega$) against the direct signal (`R5 + R6` $= 20\text{ k}\Omega$ total) through `R8` $= 22\text{ k}\Omega$. Because the half-wave leg has twice the admittance of the direct leg ($\frac{1}{10\text{ k}\Omega}$ vs. $\frac{1}{20\text{ k}\Omega}$), `U1C` flips only one polarity to produce full-wave rectification with a clean $1.1\times$ summing gain ($\frac{22\text{ k}\Omega}{20\text{ k}\Omega}$).
4. **Peak Detector & Attack/Release Timing (`D3`, `RV_ATK`, `C2`, `RV_REL`)**:
   `D3` (1N4148) charges the $1\,\mu\text{F}$ smoothing capacitor `C2` through `RV_ATK` ($50\text{ k}\Omega$ attack pot) and discharges through `R9` ($1\text{ k}\Omega$), `R10` ($10\text{ k}\Omega$), and `RV_REL` ($1\text{ M}\Omega$ release pot).
5. **Output Amplifier & DC Offset Stage (`U1D`)**:
   `U1D` buffers the envelope on Pin 12 ($+$) while summing a bipolar DC bias divider (`R11`, `R12` $= 10\text{ k}\Omega$ across $\pm 12\text{V}$ feeding `RV_OFFSET` $100\text{ k}\Omega$ and `R13`–`R15` $10\text{ k}\Omega$) on Pin 13 ($-$), driving `J_OUT` through `R16` ($1\text{ k}\Omega$).
6. **Inverted Output & Pre-Biased LED Driver (`U2A`, `U2B`, `U2C`, `U2D`)**:
   `U2A` provides a unity-gain inverted envelope (`R17 = R18 = 10k`, driving `J_INV_OUT` through `R19` $= 1\text{ k}\Omega$). `U2B` buffers the envelope via `R20` ($10\text{ k}\Omega$) and drives `LED1` through `R21` ($22\text{ k}\Omega$) against a negative-biased cathode divider (`R22` $= 10\text{ k}\Omega$ to `GND`, `R23` $= 33\text{ k}\Omega$ to $-12\text{V}$), letting the LED respond smoothly near $0\text{V}$.

## Five Production Upgrades Over the Original Sketch

Hagiwo's sketch uses minimal parts for breadboard simplicity (`TL074 or TL072`). Translating it into a reliable SMT PCB in the [Netlist, BOM & Capture Guide](../reference/netlist-and-bom.md) ([`ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md)) adds five essential safeguards:

1. **Unused Op-Amp Termination (`U2C`, `U2D`)**: With 6 active op-amps across two `TL074H` packages (8 channels total), two channels remain spare. Leaving op-amp pins floating risks high-frequency oscillation and excess current draw. Both `U2C` (Pins 8–10) and `U2D` (Pins 12–14) are wired as unity-gain followers with their non-inverting inputs ($+$) tied to `GND`.
2. **Gain Floor Resistor (`R_GAIN_MIN` $= 1\text{ k}\Omega$)**: Placed in series with `RV_GAIN` ($100\text{ k}\Omega$) so turning the gain knob fully counter-clockwise never shorts `U1A`'s feedback loop to $0\,\Omega$, avoiding wiper-contact dead spots and op-amp capacitive loading.
3. **High-Frequency IC Decoupling (`C5`–`C8` $= 100\text{ nF}$)**: Four `0603` X7R ceramic capacitors sit directly beside Pins 4 ($+12\text{V}$) and 11 ($-12\text{V}$) of `U1` and `U2`, complementing the two bulk $4.7\,\mu\text{F}$ electrolytics (`C3`, `C4`).
4. **Reverse-Polarity Protection (`D4`, `D5` = `B5819W`)**: Series `SOD-123` Schottky diodes on `+12V_RAW` and `-12V_RAW` protect the `TL074H` rails if a keyed/unkeyed Eurorack power cable is plugged in backwards.
5. **Non-Polarized MLCC Input Coupling (`C1`) & Output Isolation (`R16`, `R19`)**: `C1` uses a $4.7\,\mu\text{F}$ 25V X7R `0805` MLCC for clean bipolar AC coupling without electrolytic reverse-biasing, and $1\text{ k}\Omega$ series resistors (`R16`, `R19`) protect `U1D` and `U2A` against short-circuited patch cables.
