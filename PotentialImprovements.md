# Potential Improvements: DC-Coupled CV / LFO Slew & Precision Rectification Mode

*(Standalone engineering note originally drafted against Hagiwo's baseline RefDes [`EnvelopeFollower.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/EnvelopeFollower.md) and [`EnvelopeFollowerImprovements.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/EnvelopeFollowerImprovements.md) Section 2.7: "Optional Eurorack Feature Enhancements". Also mirrored locally under `./reference/`.)*

> **Note for ENV / SKEW builders:** The finalized `6 HP` module in `reference/` already incorporates DC-coupled slew input (`J2` `SLEW IN`), active skew limiting, `TL074HIDR`, `SMOOTH`, and `FAST/SLOW`. See [`site/src/content/tutorial/optional/ac-dc-input-coupling.mdx`](site/src/content/tutorial/optional/ac-dc-input-coupling.mdx) ([live Optional AC/DC Mode page](https://domesticmouse.github.io/EnvelopeFollower/optional/ac-dc-input-coupling/)) for how this `AC / DC` bypass translates onto the updated `SW3` / `C7` schematic alongside [`reference/DesignSpec.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/DesignSpec.md) and the [Base Circuit & Review specs (`/specs/`) on the `ENV / SKEW` Companion Site](https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/specs/).

---

## 1. Concept Overview

In Hagiwo's baseline circuit ([`EnvelopeFollower.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/EnvelopeFollower.md)), input jack `J1` (`IN`) feeds the inverting preamp `U1A` exclusively through AC-coupling capacitor `C1` (`4.7 µF` baseline; `470 nF–1 µF` in the high-`Z_in` upgrade). With `R1 || R2 = 9.90 kΩ` (or `100 kΩ` upgraded), `C1` forms a `1.6–3.4 Hz` high-pass filter:

- **Advantage for audio:** Strips any DC offset from audio signals so silence sits strictly at `0 V` entering the precision full-wave rectifier (`U1B`, `U1C`).
- **Limitation for CV / LFO sources:** Sub-audio modulation (slow LFOs, stepped sequencer CVs, gates/triggers, or static DC voltages) decays back toward `0 V` across `C1` instead of being tracked accurately.

Adding a panel-mounted **AC / DC Input Coupling Switch (`SW1`, SPST)** directly in parallel across `C1` (`J1.Tip` / post-protection input node to `AC_IN`) lets the user short out `C1` on demand, converting the module from a dedicated audio envelope follower into a **DC-coupled precision full-wave CV rectifier, asymmetric unipolar slew limiter, and bipolar offset/inverter processor**.

---

## 2. How Each Downstream Stage Behaves in `DC` Mode (`SW1` Closed)

When `SW1` bypasses `C1`, DC and low-frequency control voltages (`-10 V` to `+10 V`, scaled by `GAIN` pot `RV1`) flow unmodified into the signal chain:

### 2.1 Precision Full-Wave CV Rectification ("Absolute Value" / LFO Frequency Doubler)
- **Mechanism:** `U1B` (`D1`, `D2`, `R3`, `R6`) and `U1C` (`R4`, `R5`, `R7`, `R8`) compute $V_{\text{FWR\_OUT}} = k \cdot |V_{\text{PREAMP\_OUT}}|$ (where $k = 1.1\times$ baseline, or $1.0\times$ with `R8 = 20 kΩ`).
- **With fast `ATK` & `Release` (both fully CCW):**
  - Bipolar LFOs (triangle, sine, ramp) centered around `0 V` fold their negative half-cycle upward cleanly with **no `0.6 V` diode deadzone** at zero crossings.
  - A symmetric triangle or sine LFO emerges as a **unipolar rectified wave at `2×` the input frequency** (classic octave-up LFO / analog wave-folder behavior).
  - Unipolar positive or negative CV inputs pass through as strictly positive magnitude $|V_{\text{in}}|$.

### 2.2 Asymmetric Unipolar Slew Limiter / Gate-to-AR Envelope Generator
- **Mechanism:** Stage 4 charges `C2` (`ENV_CAP`) via `D3` + `RV2` (`ATK`) and discharges `C2` to `GND` via `R10` + `RV3` (`Release`). Because `D3` only conducts when $V_{\text{FWR\_OUT}} > V_{C2}$ (or $V_{C2} + V_f$ if passive), rise and fall times are governed independently:
  - **Rising CV / Audio Gate → Attack Slew:** Patching a `0 to +5 V` or `0 to +10 V` gate/trigger into `IN` charges `C2` at the `ATK` rate while the gate is high, then decays exponentially at the `Release` rate once the gate returns to `0 V`—turning the module into a standalone **Attack–Release (AR) envelope generator**.
  - **Stepped CV Portamento / Lag Processing:** Patching unipolar stepped CV (e.g., `0 to +5 V` sequencer or quantized random voltages) smooths upward voltage jumps via `ATK` and downward steps via `Release` (unipolar portamento; note that bipolar inputs will be full-wave rectified first unless `U1B`/`U1C` are also bypassed).

### 2.3 Simultaneous Polarizer, Gain & Dual Offset Shaper (`OUT` + `INV_OUT`)
- `GAIN` (`RV1`) sets the overall CV scaling (`0.47×–10.47×` with gain-floor limiting), `OFFSET` (`RV4`) shifts the resulting unipolar rectified/slewed CV upward or downward (`±5.2 V` baseline or `±10 V` upgraded), and Stage 5 / Stage 6 output both **`OUT`** and **`INV_OUT`** (`-OUT`) simultaneously for parallel positive and ducking/inverted modulation patches.
- `LED1` continues tracking the pre-offset envelope/CV level cleanly.

---

## 3. Critical Design Constraints When Implementing `SW1` (`AC / DC`)

To prevent subtle DC errors or signal blockage when `SW1` is added alongside the upgrades in [`EnvelopeFollowerImprovements.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/8ad81d0/EnvelopeFollowerImprovements.md), account for the following three interactions:

1. **Inter-Stage AC Coupling Conflict (`IMP-07` / Section 2.3.2):**
   - Section 2.3.2 recommends adding a second `1 µF + 100 kΩ` AC-coupling network *between* `PREAMP_OUT` and the rectifier (`R3`/`R4`) to block `U1A`'s amplified input offset voltage (`11 × V_os`) when using an active zero-deadzone peak detector (`D3` inside an op-amp feedback loop).
   - **Conflict:** If that inter-stage capacitor remains permanently in series, closing `SW1` across `C1` alone will **still block DC** at `U1B`/`U1C`.
   - **Solution Options:**
     - **Option A (Preferred with low-offset op-amps):** Use **`TL074H`** (`V_os ≈ 1 mV` typ., `±11 mV` max at `10×` gain) or **`OPA4172`** (`V_os ≈ 0.2 mV` typ.) and **omit the inter-stage AC-coupling capacitor**, leaving only `C1` to bypass via a single **SPST** `AC/DC` switch.
     - **Option B (If keeping inter-stage AC coupling with standard `TL074`):** Use a **DPST / DPDT** toggle switch for `SW1` so one pole shorts `C1` and the second pole simultaneously shorts the inter-stage coupling capacitor in `DC` mode.

2. **Input `1 MΩ` Pulldown Loading (`R1`):**
   - In `DC` mode, `C1` is shorted, so `J1.Tip` connects straight into the `R1 || R2` node (`9.90 kΩ` in the baseline inverting topology, or `100 kΩ` if using the Stage 1 high-`Z_in` buffer/divider upgrade). Upgrading Stage 1 input impedance to **`100 kΩ`** ensures `DC` mode never loads external passive CV attenuators or `1 kΩ`-output LFOs (`< 1%` droop instead of `-9.1%`).

3. **Unplugged Switch-Ground Behavior (`J1` Normal Pin):**
   - With `J1`'s switched normal pin grounded (`IMP-04`), unplugging `J1` in `DC` mode safely grounds `R2` (`0 V` reference) with zero hum or offset drift, and switching from `AC` to `DC` while unpatched causes no transient pop if `C1` has already discharged through `R1` (`1 MΩ` to `GND`).

---

## 4. Implementation Checklist (If Added to PCB / Panel)

| Item | Specification / Placement | Notes |
|---|---|---|
| **Switch (`SW1`)** | Panel-mount SPST ON-ON (or SPDT with one throw `NC`) | Connects directly across `C1` pads (`C1.1` ↔ `C1.2`). Use DPST if an inter-stage coupling cap is present. |
| **Panel Silkscreen** | Top: `AC`, Bottom: `DC` (or `AUDIO` / `CV`) | Place near `J1` (`IN`) jack on the 3U front panel. |
| **Recommended Companion Upgrades** | `TL074H` (low `V_os`), `100 kΩ` `Z_in`, active peak detector (`U2C`/`U2D`) | Eliminates `0.6 V` diode deadzone on low-amplitude LFOs (`±1 V` to `±5 V`) and removes DC offset error without a second blocking capacitor. |
