# How the Improved Eurorack Envelope Follower Works

A stage-by-stage guide for learning audio electronics, based on [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md) and [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md).

---

## What Is an Envelope Follower?

An audio signal—a guitar note, a drum hit, or a synthesizer bassline—is an **alternating current (AC)** voltage that swings rapidly above and below `0 V` dozens to thousands of times every second. If you plug that raw audio straight into a synth filter's cutoff CV input, the filter just wobbles back and forth at audio speed instead of opening smoothly with the loudness of the sound.

An **envelope follower** turns that fast, bipolar audio wiggle into a **slow, smooth control voltage (CV)** that traces the sound's *loudness contour* (its **amplitude envelope**):

1. **Strip away unwanted DC** and buffer the jack so the module doesn't weigh down whatever plugged into it (`Stage 1A`).
2. **Boost or pad the signal** to a healthy working voltage (`Stage 1B`).
3. **Flip the negative half-cycles upward** so negative swings count just as much as positive swings (`Stages 2 & 3`).
4. **Capture the peaks and smooth the motion** with adjustable Attack (how fast it rises) and Release (how slowly it fades) (`Stage 4`).
5. **Shift and buffer the final CV** into normal (`OUT`) and inverted (`INV_OUT`) outputs (`Stage 5`), while driving an indicator LED cleanly (`Stage 6`).

```
  MAIN AUDIO-TO-CV SIGNAL ARC
  ===========================
  Audio IN (J1)
     │  (AC, ±V, e.g. ±1 V riding on stray DC)
     ▼
  [Stage 1A: Input Clamp + AC Coupling + Buffer (C1, R1, D_IN, U2D)]
     │  (Pure AC centered at 0 V; 101 kΩ load to source)
     ▼
  [Stage 1B: Inverting Gain Preamp (U1A, RV1 GAIN)]
     │  (Scaled AC: -0.10× to -9.17×)
     ▼
  [Stages 2 & 3: Precision Full-Wave Rectifier (U1B, D1_D2, U1C)]
     │  (Pulsating positive humps: +1.000 × |PREAMP_OUT|)
     ▼
  [Stage 4: Active Peak Detector + Attack/Release (U2C, D3, RV2, C2, RV3)]
     │  (Smooth positive envelope voltage ENV_NODE: 0 V to ~+10 V)
     ├──────────────────────────────────────────────────────┐
     ▼                                                      ▼
  [Stage 5: Offset Summer + Protected Outputs]    [Stage 6: LED Sink]
   U1D (+ RV4 OFFSET) ──► J2 (OUT)                 U2B + D4 ──► Glows
   U2A (Inverter)     ──► J3 (INV_OUT)             proportional to ENV_NODE

  SUPPORTING INFRASTRUCTURE
  =========================
  [Stage 0: J4 Power Entry → B5819W Reverse-Polarity Protection → 10 Ω / 22 µF Filter → 100 nF IC Bypass]
```

Every single one of the **8 op-amp sections** inside the two `TL074HIDR` quad op-amp chips (`U1A`–`U1D` and `U2A`–`U2D`) has a dedicated job—there are zero spare or wasted sections.

---

## Part I: Following the Audio Signal Path

To make the voltages concrete as we walk through the circuit, imagine plugging in a **±1.0 V peak sine wave** that happens to have a stray **+0.5 V DC offset** on it (so it swings between `-0.5 V` and `+1.5 V`), with `GAIN` set to **`-2.0×`**, `OFFSET` centered (`0 V`), fast `ATK`, and medium `Release`.

---

### Stage 1A — Input Protection, AC Coupling & Buffering (`J1`, `C1`, `R1`, `D_IN`, `U2D`)

**Goal:** Mute unpatched hum, block DC offsets, survive static shocks, and present a standard `100 kΩ`-class Eurorack input impedance.

#### 1. The Normalled Jack (`J1`)
`J1` is a switched `3.5 mm` mono jack (`WQP-PJ398SM`). When nothing is plugged in, its internal **Tip-Normal (`TN`)** contact touches `Tip`, shorting `J1.T` directly to **`GND`**.
- **Why this matters:** Without `J1.TN → GND`, the input wire acts like an antenna picking up `50/60 Hz` mains hum, which the preamp could amplify by nearly `10×` and falsely trigger the envelope and LED. Inserting a patch cable physically lifts `TN` off `Tip`, letting the external signal enter.

#### 2. AC Coupling (`R_IN_PROT`, `C1`, `R1`)
From `J1.T`, the signal enters `R_IN_PROT` (`1 kΩ`), passes through **`C1` (`1 µF` PET film)** onto node `IN_AC`, and sees **`R1` (`100 kΩ`)** tied to `GND`.
- **How a capacitor blocks DC:** A capacitor passes changing voltages (AC) while blocking steady voltages (DC). `C1` and `R_IN_PROT + R1` form a **first-order RC high-pass filter** whose `-3 dB` corner frequency is:
  $$f_c = \frac{1}{2\pi (R_{\text{IN\_PROT}} + R_1)\,C_1} = \frac{1}{2\pi \cdot 101\,\text{k}\Omega \cdot 1\,\mu\text{F}} \approx 1.58\text{ Hz}$$
- **In our example:** The stray `+0.5 V` DC offset stops on the left side of `C1`, while audio frequencies (even `20 Hz` sub-bass, over `12×` above `1.58 Hz`) pass cleanly through to `IN_AC` as a pure **`±1.0 V` wave centered at `0 V`**.
- **Why `C1` is non-polarized PET film (`100 V`):** Audio swings both positive and negative, which would reverse-bias a standard polarized electrolytic. Class-2 ceramic caps (`X7R`) are also avoided here so tapping the panel cannot inject piezoelectric clicks (and to keep `C1` and `C2` as one shared BOM line).

#### 3. ESD & Overvoltage Clamping (`D_IN`, `R_IN_BUF`)
`D_IN` (`BAV99`) is a tiny `SOT-23` package containing **two switching diodes in series** connected between `-12V` (`Pin 1`), `IN_AC` (`Pin 3`), and `+12V` (`Pin 2`).
- Under normal `±10 V` signals, both diodes sit reverse-biased and invisible (`< 25 nA` leakage).
- If static electricity (ESD) or a hot-plug spike tries to yank `IN_AC` above `+12.3 V` or below `-12.3 V`, one of `D_IN`'s diodes turns on and dumps the excess current safely into the locally bypassed `±12V` rails, while `R_IN_PROT` (`1 kΩ`) limits the surge current.
- `R_IN_BUF` (`1 kΩ`) sits right in front of `U2D+` (`U2.12`) as a second current limiter protecting the op-amp's internal input diodes during extreme faults.

#### 4. The `101 kΩ` Input Buffer (`U2D`)
`U2D` is wired as a **unity-gain voltage follower**: its `-` input (`U2.13`) connects straight to its output (`U2.14` = `IN_BUF`). An op-amp with negative feedback adjusts its output to keep its `+` and `-` inputs equal, so:
$$V_{\text{IN\_BUF}} = V_{\text{IN\_AC}}$$
- **Why spend an op-amp just to multiply by `1`?** Without `U2D`, `C1`/`R1` would connect straight to `R2` (`10 kΩ`) at the inverting preamp's virtual ground (`0 V`), dragging the module's input impedance down to `10 kΩ` (`10×` heavier than the Eurorack `100 kΩ` standard) and shifting `f_c` up by `10×`! Because `U2D` is a FET-input `TL074H` (`~1 pA` input bias current), `C1` and `R1` see virtually infinite impedance on `U2.12`. Thus the source jack sees **`Z_in = R_IN_PROT + R1 = 101 kΩ`**, while `U2D`'s low-impedance output drives `R2` (`10 kΩ`) effortlessly.

---

### Stage 1B — Protected Inverting Preamp (`U1A`, `R2`, `RV1`, `R_GAIN_MIN`, `R_GAIN_FAIL`, `C_HF`)

**Goal:** Scale quiet line/instrument inputs up or pad hot `±10 V` Eurorack signals down cleanly.

`U1A` (`U1.3` `+` grounded, `U1.2` `-` = `U1A_INV`) is a classic **inverting amplifier**:
- Because `U1A+` is `0 V`, negative feedback holds `U1A_INV` at **`0 V` (a "virtual ground")**.
- Input voltage `V_IN_BUF` pushes a current $I_{\text{in}} = V_{\text{IN\_BUF}} / R_2$ through `R2` (`10 kΩ`). Since the op-amp input takes negligible current, that same current must flow through the feedback network $Z_f$ to `PREAMP_OUT` (`U1.1`), forcing:
  $$V_{\text{PREAMP\_OUT}} = -V_{\text{IN\_BUF}} \cdot \frac{Z_f}{R_2}$$
- **Why inverting doesn't hurt:** Flipping the waveform upside-down (`-`) makes no difference to an envelope follower because Stage 2/3 immediately takes the absolute value! Using an inverting stage also keeps `U1A`'s input pins fixed at `0 V`, avoiding common-mode distortion on large swings.

#### Smart Details in `U1A`'s Feedback Loop
| Component | Value | What It Teaches & Why It's There |
|---|---|---|
| **`R_GAIN_MIN`** | `1 kΩ` | Sits in series with `RV1` (`GAIN`). Prevents dialing `RV1` fully CCW from shorting `U1A_OUT` to `U1A_INV` through `0 Ω`, and creates a **`-0.10×` (`-20 dB`) gain floor** so hot `±10 V` synth oscillators can be attenuated to `±1 V` instead of clipping. |
| **`RV1`** | `A100k` | Wired as a 2-terminal **variable resistor (rheostat)** (`1` = `GAIN_POT_1`, `2+3` tied to `PREAMP_OUT`). Using an **audio (`A`) taper** spreads unity gain (`1×` at `10 kΩ`) smoothly up the dial instead of cramming attenuation and unity into the bottom 10% of rotation. |
| **`R_GAIN_FAIL`** | `1 MΩ` | Mounted on the PCB in parallel with `R_GAIN_MIN + RV1`. At normal settings (`1 kΩ–101 kΩ`), `1 MΩ` barely nudges max gain to **`-9.17×` (`+19.25 dB`)** (`101 kΩ || 1 MΩ = 91.7 kΩ`). If a panel-pot wire breaks, `R_GAIN_FAIL` keeps feedback closed at `-100×` instead of letting `U1A` go open-loop and slam into the rails. |
| **`C_HF`** | `47 pF` `C0G` | Wires running to a front-panel pot add stray capacitance on `U1A_INV`, which can make op-amps ring or oscillate at ultrasonic frequencies. `C_HF` gently rolls off gain above $f_c = \frac{1}{2\pi \cdot 91.7\,\text{k}\Omega \cdot 47\,\text{pF}} \approx 36.9\text{ kHz}$ at max gain—well above audible sound, while killing RF/oscillation. |

- **In our example:** With `GAIN` set to `-2.0×`, `IN_BUF` (`±1.0 V`) becomes **`PREAMP_OUT = ∓2.0 V`** (a `±2.0 V` sine wave, inverted).

---

### Stages 2 & 3 — `0.1%`-Matched Precision Full-Wave Rectifier (`U1B`, `D1_D2`, `U1C`, `R3`–`R8B`)

**Goal:** Compute the exact absolute value $V_{\text{RECT\_OUT}} = +1.000\,|V_{\text{PREAMP\_OUT}}|$ without losing quiet signals inside diode voltage drops.

If you tried to rectify audio using a passive diode bridge (`1N4148`), nothing below `~0.65 V` would conduct at all. Placing diodes **inside an op-amp's feedback loop** lets the op-amp's huge open-loop gain automatically compensate for the diode drop.

This circuit uses the classic **two-op-amp inverting half-wave rectifier (`U1B`) + summing amplifier (`U1C`)** topology:

```
                   ┌── [R4 10k 0.1%] ── [R5 10k 0.1%] (20 kΩ feedforward) ──┐
                   │                                                        ▼
PREAMP_OUT ────────┴──► [R3 10k 0.1%] ──► [U1B / D1_D2 / R6] ──► [R7 10k 0.1%] ──► [U1C (R8A+R8B = 20 kΩ)] ──► RECT_OUT
```

#### How Both Half-Cycles Work
`D1_D2` is a `BAT54S` dual series Schottky diode (`Pin 1 = RECT_HW`, `Pin 2 = U1B_INV`, `Pin 3 = U1B_OUT`), providing two diodes: **`D2` (`RECT_HW → U1B_OUT`)** and **`D1` (`U1B_OUT → U1B_INV`)**. `U1B+` (`U1.5`) and `U1C+` (`U1.10`) are both tied to `GND`.

1. **Positive Half-Cycle (`PREAMP_OUT > 0`, e.g. `+2.0 V`):**
   - Current flows into `U1B_INV` through `R3` (`10 kΩ`), pushing `U1B_OUT` **negative**.
   - `D1` (`U1B_OUT → U1B_INV`) is reverse-biased (**OFF**); `D2` (`RECT_HW → U1B_OUT`) conducts (**ON**), closing `U1B`'s feedback loop through `R6` (`10 kΩ`).
   - Thus `U1B` acts as a unity-gain inverter: **`RECT_HW = -PREAMP_OUT = -2.0 V`**.
   - Now `U1C` sums two currents into `U1C_INV` (`0 V` virtual ground):
     - Feedforward branch (`R4 + R5 = 20 kΩ`): $+\frac{2.0\text{ V}}{20\,\text{k}\Omega} = +0.10\text{ mA}$
     - Rectified branch (`R7 = 10 kΩ`): $-\frac{2.0\text{ V}}{10\,\text{k}\Omega} = -0.20\text{ mA}$
     - Net input current = $-0.10\text{ mA}$, flowing out through `R8A + R8B = 20 kΩ` to give:
       $$V_{\text{RECT\_OUT}} = -(-0.10\text{ mA}) \cdot 20\,\text{k}\Omega = \mathbf{+2.0\text{ V}}$$

2. **Negative Half-Cycle (`PREAMP_OUT < 0`, e.g. `-2.0 V`):**
   - Current pulls out of `U1B_INV` through `R3`, pushing `U1B_OUT` **positive**.
   - `D1` turns **ON** immediately near `+0.3 V`, clamping `U1B_OUT` so `U1B` stays active in linear feedback and never wastes time recovering from positive rail saturation!
   - `D2` is reverse-biased (**OFF**), disconnecting `U1B_OUT` from `RECT_HW`. With `R6` tied to `U1B_INV` (`0 V`) and `R7` tied to `U1C_INV` (`0 V`), **`RECT_HW = 0 V`** (zero current through `R7`).
   - `U1C` receives **only** the feedforward current ($-2.0\text{ V} / 20\,\text{k}\Omega = -0.10\text{ mA}$), inverting it across `R8A + R8B = 20 kΩ` to give:
     $$V_{\text{RECT\_OUT}} = -(-0.10\text{ mA}) \cdot 20\,\text{k}\Omega = \mathbf{+2.0\text{ V}}$$

Whether `PREAMP_OUT` is `+2.0 V` or `-2.0 V`, **`RECT_OUT` outputs `+2.0 V`**—a clean, strictly positive full-wave rectified waveform!

#### Two Precision Engineering Upgrades Here
- **Why `7 × 10 kΩ ±0.1%` (`25 ppm/°C`) resistors (`R3`–`R8B`):** Look back at the positive half-cycle math: `U1C` subtracts $2\times$ (`R7`) from $1\times$ (`R4+R5`) to leave $1\times$. Because of this `2× - 1×` cancellation, resistor tolerances get magnified roughly **3×**! Ordinary `5%` parts can produce `44.3%` asymmetry between positive and negative half-cycles, and even `1%` parts allow `8.16%` mismatch—leaking fundamental audio ripple into the envelope detector. Switching to `±0.1%` thin-film parts slashes worst-case mismatch to **`≤ 0.80%`**, and building the two `20 kΩ` paths (`R4+R5`, `R8A+R8B`) out of pairs of the same `10 kΩ ±0.1%` reel ensures matched temperature drift while avoiding an extra `$3.00` JLCPCB Extended feeder line.
- **Why `BAT54S` Schottky (`D1_D2`) instead of `1N4148`:** When `PREAMP_OUT = +10 V`, `RECT_HW` sits at `-10 V`, forcing `U1B_OUT` down to `-10 V - V_f(D2)` while sinking `2 mA` (`R6 || R7 = 5 kΩ`). A `1N4148` (`~0.65 V` drop) pushes `U1B_OUT` to `-10.65 V`, dangerously close to clipping on `±11.55 V` internal rails; `BAT54S` (`~0.3 V` drop) buys back `~0.35 V` of crucial negative headroom.

---

### Stage 4 — Active Zero-Deadzone Peak Detector & Attack/Release (`U2C`, `D3`, `R_ATK_MIN`, `RV2`, `C2`, `R10`, `RV3`)

**Goal:** Turn the fast pulsating `RECT_OUT` bumps into a smooth DC envelope with independent Attack and Release times, even for very quiet signals.

#### 1. Active Zero-Deadzone Peak Detector (`U2C` + `D3`)
In a simple passive peak detector (`RECT_OUT → D3 → C2`), nothing charges `C2` until `RECT_OUT` exceeds `D3`'s `~0.65 V` turn-on threshold—erasing quiet reverb tails and shifting the voltage downward by `~0.7 V` with temperature drift.

Here, **`U2C` wraps `D3` (`1N4148WS`) inside its negative feedback loop**:
- `U2C+` (`U2.10`) monitors `RECT_OUT`.
- `U2C_OUT` (`U2.8`) drives `D3.A`, and `D3.K` (`ATK_IN`) feeds back to `U2C-` (`U2.9`).
- **When `RECT_OUT` rises above `ATK_IN`:** `U2C` drives `U2C_OUT` higher by whatever `~0.65 V` drop `D3` needs so **`ATK_IN = RECT_OUT` down to `< 5 mV`**! Even tiny `50 mV` signals pass cleanly.
- **When `RECT_OUT` dips between audio crests:** `U2C+` falls below `U2C-` (which floats at `ENV_NODE`), so `U2C_OUT` swings negative to the `-11.55 V` rail, immediately **reverse-biasing `D3`**. Charge on `C2` is trapped and cannot flow backward into `U1C` or `U2C`.
- **Why keep silicon `1N4148WS` for `D3` instead of a Schottky?** Now that `U2C`'s loop erases `D3`'s forward drop, we want the **lowest possible reverse leakage** so `C2` doesn't drain backward during slow `1 s` releases. `1N4148WS` leaks `< 25 nA` (versus `µA`–`mA` for Schottky diodes, especially when warm).

#### 2. Attack & Release Time Constants (`C2 = 1 µF` PET Film)
From `ATK_IN`, charging and discharging happen around the hold capacitor **`C2` (`1 µF` PET film to `GND`)** at node `ENV_NODE`:

- **Attack Path (`R_ATK_MIN + RV2`):**
  - `R_ATK_MIN` (`470 Ω`) + `RV2` (`A50k` audio-taper rheostat) connect `ATK_IN` to `ENV_NODE`.
  - Time constant: $\tau_{\text{atk}} = (470\,\Omega + R_{\text{RV2}}) \cdot 1\,\mu\text{F} \approx \mathbf{0.47\text{ ms to }50.5\text{ ms}}$.
  - **Why `R_ATK_MIN = 470 Ω`?** Without it, dialing `ATK` fully CCW (`0 Ω`) shorts `U2C` directly into an empty `1 µF` capacitor on fast transients, slamming `U2C` into current limit (`26 mA+`), spiking the power rails, and risking ringing. `470 Ω` caps `10 V` surge current at `~21 mA` while still sounding instantaneous (`0.47 ms`).
- **Release Path (`R10 + RV3`):**
  - `R10` (`10 kΩ`) + `RV3` (`A1M` audio-taper rheostat) discharge `C2` (`ENV_NODE`) to `GND`.
  - Time constant: $\tau_{\text{rel}} = (10\,\text{k}\Omega + R_{\text{RV3}}) \cdot 1\,\mu\text{F} = \mathbf{10\text{ ms to }1.01\text{ s}}$.
  - **Why the original `R9` (`1 kΩ`) was deleted:** Putting a `1 kΩ` series resistor between `C2` and `ENV_NODE` created a voltage divider against `R10` (`10 kΩ`) whenever `Release` was turned all the way down, dropping output amplitude by `9.1%` (`10 / 11`). Removing `R9` gives **0% release-dependent droop**.
- **Why `C2` MUST be PET film (`1 µF 100 V`):** Never use `X7R`/`X5R` MLCCs for an envelope hold capacitor! Class-2 ceramics are **piezoelectric** (bumping the module or turning knobs generates CV spikes) and suffer **DC-bias capacitance loss** (losing 30–60% of their capacitance at `+10 V`, causing Attack and Release times to shrink as signals get louder). Film is rock-steady and microphonic-free.
- **Audio-electronics quirk to know (`ATK` vs. `Release` interaction):** Because charging (`RV2`) and discharging (`R10 + RV3`) meet at the same `ENV_NODE` pin, dialing a *slow Attack* (`50 ms`) together with an *ultra-fast Release* (`10 ms`) makes `RV2` (`50.5 kΩ`) and `R10` (`10 kΩ`) act as a resistive divider (`10k / 60.5k ≈ 16.5%` peak!), limiting maximum envelope voltage. Keeping `Release` comfortably longer than `Attack` (which `A`-taper pots naturally encourage) gives full-amplitude tracking.

- **In our example:** With fast `ATK` and `100 ms` `Release`, `ENV_NODE` charges quickly to **`+2.0 V`** and holds steadily between the `RECT_OUT` humps.

---

### Stage 5 — Linearized `OFFSET`, In-Loop Output Buffers & Clash Protection (`U1D`, `RV4`, `U2A`, `J2`, `J3`)

**Goal:** Combine `ENV_NODE` with a smooth bipolar `OFFSET` knob, produce both normal (`OUT`) and inverted (`INV_OUT`) CV outputs, and survive Eurorack cable abuse.

#### 1. `U1D` Non-Inverting Envelope Buffer + Linearized `OFFSET` Summer
First, `R_ENV_PROT` (`10 kΩ`) protects `U1D+` (`U1.12`) from `C2`'s stored charge if module power drops out while `C2` sits at `+10 V`. Under normal power, `U1D+` draws `~1 pA`, so `R_ENV_PROT` introduces zero voltage drop.

Meanwhile, the **`OFFSET` circuit (`RV4`, `R11`–`R13`, `R15`)** works by **superposition**:
- `RV4` (`B10k` linear pot) sits between `R11` (`1 kΩ` to `+11.55 V`) and `R12` (`1 kΩ` to `-11.55 V`), spanning `±9.63 V` ($\pm 11.55\text{ V} \cdot \frac{5}{6}$).
- `OFF_WIPER` (`RV4.2`) feeds `U1D-` (`U1.13`) through **`R13 = 18 kΩ`**, with feedback **`R15 = 10 kΩ`** from `OUT_CLAMP`.

Let's see how each input affects `OUT_CLAMP`:
1. **Envelope Gain (with `OFFSET` at `0 V`):** Because `R14` (`10 kΩ` to `GND` in the original design) was removed, `U1D` acts as a non-inverting amplifier with feedback `R15` (`10 kΩ`) and ground resistance `R13 + R_th(α)` (where the `B10k` pot's Thévenin resistance $R_{\text{th}}(\alpha)$ varies cleanly from `0.92 kΩ` at the ends to `3.00 kΩ` at center):
   $$A_{v,\text{env}}(\alpha) = 1 + \frac{R_{15}}{R_{13} + R_{\text{th}}(\alpha)} = \mathbf{1.476\times\text{ (center) to }1.529\times\text{ (ends)}}$$
   - That's only **`3.5%` gain variation** across the entire `OFFSET` sweep (down from `12%` in the original circuit!) and lets `ENV_NODE` climb all the way to **`~+7.5 V`** (`~+11.1 V` at `OUT_CLAMP`) before touching the `+11.55 V` internal rail (versus clipping at `+4.2 V` in the original `2.5×` design!).
2. **DC Offset Shift (with `ENV_NODE = 0 V`):** `U1D` acts as an inverting amplifier for `V_th`:
   $$V_{\text{OUT, offset}} = -V_{\text{th}}(\alpha) \cdot \frac{R_{15}}{R_{13} + R_{\text{th}}(\alpha)}$$
   At the ends ($V_{\text{th}} = \pm 9.63\text{ V}$, $R_{\text{th}} = 0.92\text{ k}\Omega$), `OUT` shifts smoothly over **`±5.09 V`**.
   - **Pot rotation intuition:** `RV4.1` (CCW) = `+9.63 V`, `RV4.3` (CW) = `-9.63 V`. Turning `OFFSET` **clockwise** moves the wiper toward `-9.63 V`, and because `U1D` **inverts** `OFF_WIPER`, turning **CW pushes `OUT` positive** (`-5.09 V → +5.09 V`).

#### 2. `U2A` Inverting Output (`INV_OUT`)
`OUT_CLAMP` also feeds `U2A` (`U2.3` `+` tied to `GND`; `R17 = 10 kΩ` input; `R18 = 10 kΩ` feedback from `INV_OUT_CLAMP`), creating an exact **`-1.000×` mirror**:
$$V_{\text{INV\_OUT}} = -V_{\text{OUT}}$$
Why include `INV_OUT`? In Eurorack, sending `INV_OUT` (plus a positive `OFFSET`) to a filter or VCA creates instant **sidechain ducking** (kick drum goes in → other synth voices dip down cleanly).

#### 3. Split `0.5 W` Clash Resistors, Midpoint Clamps & In-Loop Feedback
Look closely at the output wiring of both `OUT` (`J2`) and `INV_OUT` (`J3`):
- `U1D_OUT` → **`R16A` (`470 Ω`, `0.5 W` `1210`)** → `OUT_CLAMP` (**`D_OUT` `BAV99` to `±12V`**, plus **`R15` `10 kΩ` feedback** and **`R17` `10 kΩ` to `U2A`**) → **`R16B` (`470 Ω`, `0.5 W` `1210`)** → `J2.T` (`OUT`). (`U2A` mirrors this identically with `R19A/B`, `D_INV_OUT`, `R18`, and `C_OUT2`.)
- **Three clever engineering tricks work together here:**
  1. **Surviving Output-to-Output Clashes:** If you accidentally patch `OUT` (at `+10.5 V`) straight into another module's output driving `-12 V`, `~22.5 V` drops across `R16A + R16B = 940 Ω` (`23.9 mA`). Each `470 Ω` resistor dissipates $I^2 R \approx \mathbf{0.269\text{ W}}$—which would cook standard `1/8 W` (`0603`) or `1/4 W` resistors! Specifying **`1210` `0.5 W`** resistors gives a **`1.86×` continuous thermal margin**.
  2. **Midpoint ESD Protection:** Any ESD zap or `> ±12 V` spike at `J2.T` is limited by `R16B` (`470 Ω`) and shunted by `D_OUT` (`BAV99`) into the `±12V` rails before reaching `U1D` or `U2A`.
  3. **In-Loop DC Feedback + Local HF Compensation (`C_OUT1`/`C_OUT2`):** Taking `R15` (`10 kΩ`) and `R17` (`10 kΩ`) from `OUT_CLAMP` (after `R16A`) puts `R16A` *inside* `U1D`'s DC loop—cutting DC output impedance at `J2.T` in half (`470 Ω` from `R16B` alone, instead of `940 Ω`) and giving **`0.00%` tracking mismatch** between `OUT_CLAMP` and `INV_OUT_CLAMP`. Because cable capacitance at `OUT_CLAMP` could shift feedback phase at MHz frequencies, **`C_OUT1` and `C_OUT2` (`100 pF` `C0G`)** bypass high frequencies directly from each op-amp's output pin back to its `-` pin, keeping the loop unconditionally stable.
- Both output Tip-Normal pins (`J2.TN`, `J3.TN`) are left **`NC`** (unconnected) so an unpatched jack never shorts an op-amp output to ground.

- **In our example:** With `ENV_NODE = +2.0 V` and `OFFSET = 0 V`, **`OUT` reads `≈ +2.95 V`** (`1.476 × 2.0 V`) and **`INV_OUT` reads `≈ -2.95 V`**.

---

## Part II: Supporting Subsystems

### 1. Stage 6 — In-Loop Precision LED Current Sink (`U2B`, `R20`, `D4`, `D_LED_CLAMP`, `R_LED`)

**Goal:** Show envelope intensity clearly on a front-panel `3 mm` LED with zero dim glow at idle and uniform brightness regardless of LED color.

In the original sketch, `D4`'s cathode was pulled down to `-2.79 V`, causing red/green/yellow LEDs to glow dimly even at `0 V` idle while capping peak current at `~0.36 mA`. The improved circuit solves this cleanly using **`U2B` as a voltage-controlled current sink**:

1. `ENV_NODE` enters `U2B+` (`U2.5`) via `R20` (`10 kΩ`, protecting `U2B+` from `C2` during power-down).
2. `U2B_OUT` (`U2.7`) drives the LED anode (`D4.A`).
3. The LED cathode (`D4.K` = `LED_K`) feeds **`U2B-` (`U2.6`)** and drops to `GND` through **`R_LED` (`2.2 kΩ`)**.

- **Why this works for *any* LED color:** Negative feedback forces `LED_K` to match `ENV_NODE`, so `U2B_OUT` automatically rises to `V_ENV + V_f(LED)`—whether `D4` is a `1.8 V` red LED or a `3.0 V` blue LED! By Ohm's law, LED current is strictly:
  $$I_{\text{LED}} = \frac{V_{\text{ENV\_NODE}}}{R_{\text{LED}}} = \frac{V_{\text{ENV\_NODE}}}{2.2\,\text{k}\Omega}$$
  - **At `0 V` idle:** $I_{\text{LED}} = \mathbf{0.00\text{ mA}}$ (completely dark!).
  - **In our example (`ENV_NODE = +2.0 V`):** $I_{\text{LED}} = 2.0\text{ V} / 2.2\,\text{k}\Omega \approx \mathbf{0.91\text{ mA}}$ (and rises linearly up to **`~4.5 mA`** at high levels; at extreme `> +8.5–9.5 V` peaks `U2B_OUT` gently runs out of headroom near `+11.55 V` without affecting `ENV_NODE` or `OUT`).
- **Why `D_LED_CLAMP` (`1N4148WS`) sits backwards across `D4`:** LEDs can only withstand about `5 V` in reverse before breaking down. If op-amp offset (`±1 mV`) or noise ever pulls `U2B+` slightly below `0 V` at idle, `D4` shuts off, opening the feedback loop and slamming `U2B_OUT` down to `-11.55 V` across the reversed LED! **`D_LED_CLAMP` (anti-parallel across `D4`)** turns on at `-0.65 V`, harmlessly closing the loop and protecting `D4`.

---

### 2. Stage 0 — Eurorack Power Entry, Reverse-Polarity Protection & Decoupling (`J4`, `D_PWR_P/N`, `R_PWR_P/N`, `C3`, `C4`, `C_DEC1`–`C_DEC4`)

Eurorack uses a **`2×5` (`10-pin`) shrouded, keyed `2.54 mm` IDC header (`J4`)** carrying dual bipolar rails relative to `GND`:
- **Pins `1–2`:** `-12V_IN` *(marked `RED STRIPE / -12V` on the PCB silkscreen)*
- **Pins `3–8`:** `GND`
- **Pins `9–10`:** `+12V_IN`

#### Reverse-Polarity Schottky Diodes (`D_PWR_P`, `D_PWR_N`)
Even with a shrouded header, DIY ribbon cables sometimes get crimped backwards or pushed onto pins shifted by one row. Two **`B5819W` (`40 V / 1 A`) Schottky diodes** guard the rails with zero fault current:
- **`D_PWR_P` (`+12V` rail):** Anode at `J4.9–10` (`+12V_IN`), Cathode toward `+12V_PROT`. Blocks negative voltage on `+12V_IN`.
- **`D_PWR_N` (`-12V` rail):** **Reversed!** Cathode at `J4.1–2` (`-12V_IN`), Anode toward `-12V_PROT`. Why? Because conventional current flows *out of `GND` through the op-amps and back into the `-12V` supply*. Under normal power, `-12V_PROT` (`-11.55 V`) is slightly more positive than `-12V_IN` (`-12.0 V`), so `D_PWR_N` conducts normally. If someone applies `+12 V` to pins `1–2`, `D_PWR_N` blocks it completely.

#### RC Rail Filtering (`R_PWR_P/N` + `C3/C4`) & Rail Voltage
Right after the diodes sit **`R_PWR_P` and `R_PWR_N` (`10 Ω`, `1206` `250 mW`)** feeding bulk electrolytic capacitors **`C3` and `C4` (`22 µF`, `50 V`)**:
- Together they form a **`723 Hz` supply low-pass filter** ($f_c = \frac{1}{2\pi \cdot 10\,\Omega \cdot 22\,\mu\text{F}}$) that softens hot-plug inrush spikes and rejects power-bus whine from neighboring digital modules.
- At `~15 mA` nominal current draw, `B5819W` (`~0.30 V`) + `10 Ω × 15 mA` (`0.15 V`) drops `~0.45 V`, leaving clean **`±11.55 V` internal rails**.
- **Critical electrolytic polarity check:** On `C3` (`+12V`), `+` goes to `+12V` and `-` goes to `GND`. On **`C4` (`-12V`), `+` goes to `GND` and `-` goes to `-12V`**—because `0 V` (`GND`) is `11.55 V` *more positive* than `-11.55 V`! Both use `50 V` ratings (`4.2×` margin above `12 V`).

#### Local High-Frequency IC Decoupling (`C_DEC1`–`C_DEC4`)
Why add four tiny **`100 nF` (`50 V` `X7R` `0603`)** ceramic caps right next to `U1` (`pins 4 & 11`) and `U2` (`pins 4 & 11`) when `C3`/`C4` are already `22 µF`?
- Large electrolytic capacitors have noticeable internal inductance and resistance at megahertz speeds, and long PCB traces add even more inductance. Because `TL074H` has a `5.25 MHz` gain-bandwidth product and `20 V/µs` slew rate, fast switching edges inside `U1`/`U2` would bounce the local supply pins and risk oscillation without a tiny ceramic bypass placed **`< 3–5 mm`** from each power pin to the ground plane.

---

### 3. Decoding the BOM: Why Each Component Class Was Chosen

One of the best ways to learn practical electronics is looking at [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md) and asking *why* four different diode types, three resistor grades, and four capacitor dielectrics appear on one small board:

- **2 × `TL074HIDR` (`SOIC-14`, `C2878713`):** Standardizing on two quad op-amps instead of `1 × TL074 + 1 × TL072` keeps the IC BOM to a single line item (`$0.51` total for both chips) while providing 8 sections (`20 V/µs` slew rate, `5.25 MHz` GBWP, `1 pA` input bias, short-circuit protection, internal RF immunity).
- **Four Specialized Diodes:**
  - `B5819W` (`SOD-123`, `C8598`) — `40 V / 1 A` power Schottky for low-loss `±12V` polarity protection.
  - `BAT54S` (`SOT-23`, `C47546`) — dual `30 V / 200 mA` signal Schottky saving negative swing margin in `U1B`.
  - `1N4148WS` (`SOD-323`, `C2128`) — `100 V` low-leakage (`< 25 nA`) silicon switching diode for `D3` (peak hold) and `D_LED_CLAMP`.
  - `BAV99` (`SOT-23`, `C2500`) — dual `100 V` series clamp diode guarding `IN`, `OUT`, and `INV_OUT`.
- **Three Resistor Grades:**
  - `0603 1%` Basic thick-film (`C21190`, `C25804`, etc.) — pennies each for general biasing and gain paths.
  - `0603 0.1% 25 ppm/°C` thin-film (`C95204`) — 7 matched `10 kΩ` parts for the `1.000×` rectifier so half-cycle mismatch stays `≤ 0.80%`.
  - `1210 0.5 W` (`C333193`) & `1206 0.25 W` (`C17903`) — larger packages rated for thermal dissipation during output rail clashes and power inrush.
- **Four Capacitor Dielectrics:**
  - `C0G / NP0` (`47 pF` `C1671`, `100 pF` `C14858`) — ultra-stable Class I ceramic for op-amp feedback stability (`C_HF`, `C_OUT1`, `C_OUT2`).
  - `X7R 50 V` (`100 nF` `C14663`) — compact Class II ceramic for local IC bypass (`50 V` rating limits DC-bias loss on `12 V` rails).
  - `50 V` Aluminum Electrolytic (`22 µF` `C2836438`) — high-capacitance bulk rail smoothing.
  - `100 V` PET Box Film (`1 µF` `C125397`, THT) — zero microphonics, zero DC-bias capacitance collapse, and low leakage for `C1` (audio coupling) and `C2` (envelope hold).
- **Manufacturing Split (JLCPCB Economic PCBA + Hand Soldering):** All **49 SMT components (`19` BOM lines, `$1.05` parts + `$15.00` Extended feeder fees)** sit on `F.Cu` so JLCPCB populates the board in a single Economic SMT pass. The **11 THT parts**—front-panel `J1`–`J3`, `RV1`–`RV4`, and `D4` on `F.Cu`, plus `J4` and the `11 mm`-tall `C1`/`C2` film caps on `B.Cu` (clearing the `~10.5 mm` panel standoff)—are soldered later.

---

### 4. Quick Panel & Patch Reference

| Control / Jack | Type / Range | Turn Clockwise / Behavior | Practical Patch Tip |
|---|---|---|---|
| **`IN` (`J1`)** | `3.5 mm` mono (`Z_in = 101 kΩ`, `f_c = 1.58 Hz`) | Grounded via `TN` when unplugged | Accepts Eurorack audio, drums, vocals (via preamp), or raw instruments |
| **`GAIN` (`RV1`)** | `A100k` (`-0.10×` to `-9.17×`) | **CW increases gain** (`-20 dB` to `+19.25 dB`) | Turn CCW (`-20 dB`) to tame hot `±10 V` modular oscillators; turn CW for quiet pickups/line signals |
| **`ATK` (`RV2`)** | `A50k` (`0.47 ms` to `50.5 ms`) | **CW slows attack** | Full CCW snaps cleanly to drum transients; `15–50 ms` softens clicks into smooth swells |
| **`Release` (`RV3`)** | `A1M` (`10 ms` to `1.01 s`) | **CW lengthens release** | Fast (`10–30 ms`) tracks rapid rhythms or creates audio-rate modulation; slow (`0.3–1 s`) sustains smooth pads |
| **`OFFSET` (`RV4`)** | `B10k` (`±5.09 V` linear) | **CW pushes `OUT` more positive** | Center (`0 V`) for standard `0 → +V` envelopes; turn CW + use `INV_OUT` for `+5 V → 0 V` sidechain ducking |
| **`OUT` (`J2`)** | `~1.48× ENV_NODE ± 5.09 V` (rail-limited near `±11.5 V`) | Positive-going envelope (`470 Ω` DC out, `BAV99` + `0.5 W` clash protected) | Patch to a VCF Cutoff or VCA CV input for auto-wah / dynamic brightness |
| **`INV_OUT` (`J3`)** | `-V_OUT` | Inverted envelope (`0.00%` tracking error vs. `OUT_CLAMP`) | Patch to another voice's VCA CV (with positive `OFFSET`) so louder beats duck background pads |
| **`LED` (`D4`)** | `3 mm` indicator | `0.00 mA` idle; `0–4.5 mA` linear brightness | Visual feedback of `ENV_NODE` before `OFFSET` is added |
