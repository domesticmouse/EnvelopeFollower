# Envelope Follower (Improved Eurorack Revision) — Audio Electronics Guide

This guide explains how the Eurorack Envelope Follower specified in [EnvelopeFollowerImproved.md](./EnvelopeFollowerImproved.md) and [EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md) works, written for anyone learning audio electronics. Rather than just listing component values, we will trace the **audio signal path** from the input jack all the way to the outputs and front-panel LED—explaining *why* each resistor, capacitor, diode, and op-amp is there—and then cover the supporting **power-handling**, **component-selection**, and **PCB layout** architecture behind it.

---

## What Does an Envelope Follower Do?

An audio waveform (like a snare hit, guitar strum, or bassline) swings rapidly above and below `0 V` hundreds or thousands of times per second. If you simply plug an audio waveform into a filter's cutoff CV input or a VCA, it tries to wobble at audio rates rather than tracking the instrument's overall loudness.

An **envelope follower** solves this by extracting the *amplitude contour* (the "volume shadow") of an incoming signal:

```text
  Audio In (AC, symmetric around 0 V)
       /\      /\    /\
  ────/──\────/──\──/──\────  0 V   (rapid positive & negative swings)
          \  /    \/    \  /
           \/            \/

             │  Rectify (flip negative half upward) + Smooth (Attack / Release)
             ▼

  Envelope Out (Slowly varying positive DC voltage)
       .──────────.
      /            \____
  ───/──────────────────\───  0 V   (tracks loudness contour cleanly)
```

In a **Eurorack modular synthesizer**, typical signal conventions look like this:
- **Audio & Bipolar Modulation (`IN`):** Commonly `±5 V` (`10 Vpp`) for oscillators/audio, up to `±10 V` (`20 Vpp`) for hot modulation sources, and as quiet as tens of millivolts for unamplified pickups or decaying reverb tails.
- **Unipolar Envelope Output (`OUT`):** Typically `0 V` (silence) up to `+10 V` (peak loudness), shiftable via `OFFSET` into bipolar `±5 V`-style modulation.
- **Impedance Convention ("Bridging"):** Eurorack inputs aim for `~100 kΩ` input impedance and `1 kΩ` output impedance. Because `1 kΩ` is roughly `100×` smaller than `100 kΩ`, patching modules together wastes less than `1%` of signal voltage (`Voltage Divider Rule`).

### Big-Picture Architecture

The entire circuit runs on `2 × TL074H` quad op-amps (`8` active op-amp sections, `0` unused spares) powered from the Eurorack `±12 V` bus. Following the signal left-to-right shows the five main stages:

```text
  [ IN (J1) ] ──▶ Stage 1: Protection, AC Coupling & GAIN (D9, C1, RV1, U1A)
                       │  V_GAIN
                       ▼
                  Stage 2: 1.00x Precision Full-Wave Rectifier (U1B, U1C, D1, D2)
                       │  V_RECT = |V_GAIN|
                       ▼
                  Stage 3: Zero-Deadzone Peak Detector, ATK/REL & Buffer (U2C, D3, D5, RV2, C2, RV3, U2D)
                       │  V_ENV_BUF (0 to +10 V smooth DC envelope)
                       ├──────────────────────────────────────────┐
                       ▼                                          ▼
                  Stage 4: OFFSET & Outputs                  Stage 5: Linear LED Driver
                   ├─ U1D (0.975x Diff + RV4) ──▶ [ OUT (J2) ]     U2B + R27 ──▶ [ LED (D4) ]
                   └─ U2A (-1.00x Inverter)  ──▶ [ INV_OUT (J3) ]

  Supporting Foundation: Stage 6 — ±12 V Power Entry, Reverse Polarity, Filtering & Decoupling
                          (J4, D7, D8, R28, R29, C3–C8)
```

---

## Part I — The Main Arc: Following the Audio Signal Path

---

### Stage 1: Input Conditioning, Protection & Variable `GAIN`
**Components:** `J1`, `R1` (`10 kΩ`), `D9` (`BAT54S`), `C1` (`1 µF` film), `RV1` (`A100k`), `R2` (`4.7 kΩ`), `R3` (`1 MΩ`), `U1A`, `R4` (`10 kΩ`), `R5` (`100 kΩ`), `C9` (`22 pF`)

```text
   J1 (IN Jack)
    ├─ TN ──▶ GND               (Silences unplugged jack)
    └─ Tip ──▶ [R1: 10k] ──┬──▶ [C1: 1uF 63V Film] ──▶ RV1.3 (CW: A100k)
                           │                             │
                      [D9: BAT54S]                 RV1.2 (Wiper) ──┬──▶ U1A (+) Pin 3
                      Pin 2 → +12V_PROT                  │         │
                      Pin 1 → -12V_PROT            RV1.1 (CCW)   [R3: 1M]
                                                         │         │
                                                    [R2: 4.7k]    GND
                                                         │
                                                        GND

   U1A (+) Pin 3 ──────────────▶ ┌─(+)───┐
                                 │  U1A  ├───▶ V_GAIN (Pin 1)
   GND ──[R4: 10k]──┬──────────▶ └─(-)───┘          │
                    │                               │
                    └──────[R5: 100k || C9: 22pF]───┘
```

#### 1. Jack Normalization (`J1.TN → GND`)
Eurorack `3.5 mm` jacks (`WQP-PJ398SM`) include a built-in mechanical switch pin (`TN`, Tip-Normal) that touches the `Tip` contact whenever **no cable is plugged in**, and lifts open when a plug is inserted. Connecting `J1.TN` directly to `GND` shorts the input cleanly to `0 V` when unplugged. Without this, an open input trace acts like a tiny antenna for `50/60 Hz` mains hum—which the `11×` amplifier downstream would faithfully turn into a phantom envelope.

#### 2. Protecting the Input *Ahead* of the Capacitor (`R1`, `D9`)
Someone patching in the dark might accidentally plug a hot `+15 V` or static-charged cable into `IN`. `R1` (`10 kΩ`) and `D9` (`BAT54S`, a dual Schottky diode array in one tiny `SOT-23` package) form an overvoltage/ESD clamp:
- Pin `1` (Anode) connects to `-12V_PROT`; Pin `2` (Cathode) connects to `+12V_PROT`; Pin `3` (the midpoint between the two diodes) sits on node `IN_CLAMP`.
- During normal audio (`±10 V`), neither diode conducts because the signal stays inside the `±11.6 V` rails. If an external transient spikes past `+11.9 V` or below `-11.9 V`, `D9` conducts and safely steers excess energy into the power rails, while `R1` (`10 kΩ`) limits even a sustained `±24 V` fault to roughly `(24 V - 11.9 V) / 10 kΩ ≈ 1.2 mA` (`14.4 mW` in `R1`).

**Why put `D9` *before* `C1` instead of right at `U1A +`?**  
This is a classic precision-audio design trick. Schottky diodes like `BAT54S` have tiny reverse leakage current (`≤ 2 µA`). If `D9` were wired directly to `U1A +` (after `C1`), any imbalance between the upper and lower diode leakage flowing across the `~100 kΩ` gain pot could create tens or hundreds of millivolts of DC offset—which `U1A` would amplify `11×` right into a false baseline glow on the LED! By placing `D9` **ahead of `C1`**, any diode leakage drains harmlessly to ground through `R1` and the plugged-in cable (or `J1.TN`), while `C1` blocks any tiny DC voltage from ever reaching `U1A`.

#### 3. Blocking Incoming DC (`C1 = 1 µF 63 V` Box Film)
Some synth modules output audio riding on a DC bias (e.g., an oscillator swinging `0 V` to `+5 V` instead of `-2.5 V` to `+2.5 V`). If DC reached the rectifier, it would register as continuous volume even during silence. `C1` (`1 µF`) acts as a **high-pass filter** against `IN`'s resistance (`Z_in ≈ 113 kΩ` nominal, ranging `~105–115 kΩ` with pot position):

$$f_c = \frac{1}{2\pi R C_1} = \frac{1}{2\pi (113\,\text{k}\Omega)(1\,\mu\text{F})} \approx \mathbf{1.41\,\text{Hz}}$$

Anything above `~1.4 Hz`—including deep sub-bass (`20 Hz`) and audio-rate modulation—passes unattenuated, while steady DC (`0 Hz`) is blocked.

`C1` is a **metallized polyester (`PET`) box film capacitor (`63 V`)**, not a ceramic or electrolytic cap, because:
1. Input signals can swing both positive and negative (bipolar), whereas polarized electrolytics expect one polarity.
2. High-capacitance `X7R` ceramic capacitors are **piezoelectric**—tapping the front panel or bumping a jack physically generates tiny voltage spikes across an X7R cap, injecting fake hits into the envelope follower.

#### 4. High-Impedance Attenuator, Gain Floor & Audio Taper (`RV1`, `R2`, `R3`)
Instead of putting the `GAIN` potentiometer in the op-amp's feedback loop (which loads the input down to `~10 kΩ` and risks opening the op-amp's feedback loop if the wiper scratches), this design uses a **passive input voltage divider followed by a fixed `+11×` gain stage**:
- **High Input Impedance:** Looking into `J1.Tip`, the signal sees `R1` (`10 kΩ`) + `RV1` (`100 kΩ`) + `R2` (`4.7 kΩ`) with `R3` (`1 MΩ`) in parallel with the lower tap—roughly **`105–115 kΩ`** (`~113 kΩ` nominal). That matches the Eurorack `100 kΩ` standard and keeps impedance almost flat across the knob sweep.
- **Why `A100k` (Audio / Logarithmic Taper)?** Human ears—and decibel gain scales—are logarithmic. A linear pot packs most useful audio adjustments into the first `15%` of knob travel. An `A`-taper (`~15%` resistance at 12 o'clock) spreads moderate `±5 V` audio gains smoothly around the center of the knob while leaving higher gain for quiet mic/guitar/line signals in the upper half.
- **Why `R2` (`4.7 kΩ` Gain Floor)?** If the bottom of `RV1` (`Pin 1`, `CCW`) went straight to `GND`, turning `GAIN` down to zero would mute the module completely (`0×` dead zone). Adding `R2 = 4.7 kΩ` below `RV1` ensures that even at `0%` CCW, `4.7 / (10 + 100 + 4.7) ≈ 4.1%` of the input signal still reaches `U1A`. Multiplied by `U1A`'s `+11×` gain, that produces a **`+0.45×` (`-6.9 dB`) gain floor**. Hot `±10 V` (`20 Vpp`) Eurorack signals shrink to `±4.5 V` at `V_GAIN`—completely clean and unclipped—while never dropping into a silent dead spot.
- **Why `R3` (`1 MΩ` Open-Wiper Safety)?** Potentiometer wipers are mechanical sliding contacts. If dirt causes `RV1`'s wiper (`Pin 2`) to bounce open for a millisecond, `U1A +` would float and slam to the power rail. `R3` (`1 MΩ` to `GND`) is big enough not to noticeably load the `100 kΩ` divider (`~1%` effect), yet anchors `U1A +` firmly to `0 V` if the wiper lifts.

#### 5. Fixed `+11.0×` Non-Inverting Amplifier (`U1A`, `R4`, `R5`, `C9`)
`U1A` is wired in the classic **non-inverting op-amp configuration**. Using the golden rules of an ideal op-amp with negative feedback:
1. Almost zero current enters `Pin 3` (`+`) or `Pin 2` (`-`) (`TL074H` draws picoamps).
2. Negative feedback drives `V_GAIN` until `Pin 2` (`-`) equals `Pin 3` (`+`).

Because `R4` (`10 kΩ`) and `R5` (`100 kΩ`) form a voltage divider from `V_GAIN` down to `GND`, the voltage at `Pin 2` is $V_{\text{GAIN}} \cdot \frac{R_4}{R_4 + R_5}$. Setting that equal to $V_{\text{WIPER}}$ gives:

$$A_{v,\text{U1A}} = 1 + \frac{R_5}{R_4} = 1 + \frac{100\,\text{k}\Omega}{10\,\text{k}\Omega} = \mathbf{+11.0\times}$$

Combined with the input divider (`R1`, `RV1`, `R2`, `R3`):
- **`0%` CCW (Floor):** $\approx \mathbf{+0.45\times}$ (`-7.0 dB`) — tames `±10 V` signals to `±4.5 V`.
- **`50%` (12 o'clock, `A100k` ~15%):** $\approx \mathbf{+1.86\times\text{–}+1.89\times}$ (`+5.4 dB`) — ideal for standard `±5 V` synth signals.
- **`100%` CW (Max):** $\approx \mathbf{+9.95\times\text{–}+10.04\times}$ (`+20.0 dB`) — boosts quiet `100 mVpp` line/tail signals to `1.0 Vpp`.

Two subtle details complete Stage 1:
- **`C9` (`22 pF` C0G ceramic across `R5`):** At ultrasonic frequencies, op-amps lose phase margin and can ring or pick up radio interference. `C9` acts like a gentle bypass around `R5` above $f_{-3\text{dB}} = \frac{1}{2\pi (100\,\text{k}\Omega)(22\,\text{pF})} \approx \mathbf{72.3\,\text{kHz}}$, stabilizing `U1A` without touching audible frequencies (`20 Hz–20 kHz`). `C0G` (`NP0`) ceramic is chosen because its capacitance never shifts with voltage or audio vibration.
- **`TL074H` Phase-Reversal Immunity:** Classic `TL074` op-amps famously invert their output polarity ("phase reversal") if driven below about `-8 V` on their input pins. The modern **`TL074H`** (`TL074HIDR`) is immune to phase reversal and operates cleanly across `[-11.6 V, +9.6 V]` at normal levels (`V(U1A +)` stays within `±1 V` whenever `V_GAIN` is unclipped).

---

### Stage 2: Precision `1.00×` Full-Wave Rectifier
**Components:** `U1B`, `U1C`, `R6` (`10 kΩ`), `R7` (`10 kΩ`), `R8` (`20 kΩ`), `R9` (`10 kΩ`), `R10` (`20 kΩ`), `D1` (`1N4148WS`), `D2` (`1N4148WS`)

```text
                                ┌──[D1: K◀──A]──┐
                                │               │
  V_GAIN ──┬──[R6: 10k]──┬──────┴──▶ ┌─(-)───┐  │
           │             │           │  U1B  ├──┴── RECT_OP_OUT (Pin 7)
           │             │   GND ──▶ └─(+)───┘       │
           │             │                       [D2: K]
           │             │                           │ (A)
           │             └──────────[R7: 10k]────────┴── RECT_MID ──[R9: 10k]──┐
           │                                                                   │
           └────────────────────────[R8: 20k]──────────────────────────────────┼──▶ ┌─(-)───┐
                                                                               │    │  U1C  ├──▶ V_RECT (Pin 8)
                                                                       GND ────┼──▶ └─(+)───┘        │
                                                                               │                     │
                                                                               └─────[R10: 20k]──────┘
```

#### Why Not Just Use a Diode Bridge?
A plain silicon diode (`1N4148`) won't turn on until forward voltage reaches `~0.6 V`. If you put a passive diode directly in an audio signal path, anything quieter than `±0.6 V` disappears completely, and medium signals lose `0.6 V` of accuracy.

A **2-op-amp precision full-wave rectifier** puts the diodes *inside* an op-amp's feedback loop. Because an op-amp has huge open-loop gain (`> 100,000×`), it gladly jumps its own output by `±0.6 V` instantly so the circuit *outside* behaves like an ideal `0 V`-drop diode.

Let's trace both halves of an audio wave:

#### Case A: Positive Half-Cycle (`V_GAIN > 0`)
1. `V_GAIN > 0` pushes current rightward through `R6` (`10 kΩ`) into `U1B -` (`Pin 6`, held at **`0 V` virtual ground** because `U1B +` is grounded).
2. To keep `Pin 6` at `0 V`, `U1B OUT` (`Pin 7`) swings **negative**.
3. That negative output reverse-biases `D1` (`OFF`, open circuit) and forward-biases `D2` (`ON`).
4. Now feedback closes through `D2` and `R7` (`10 kΩ`). Since `R6 = R7 = 10 kΩ`, `U1B` pulls `RECT_MID` to exact **`-V_GAIN`** (while `U1B OUT` sits `~0.6 V` lower at `-V_GAIN - 0.6 V` to pay `D2`'s diode toll!).
5. Next, `U1C` acts as an **inverting summing amplifier** (`Pin 9` is also at `0 V` virtual ground):
   - From `V_GAIN` via `R8` (`20 kΩ`): $I_8 = +\frac{V_{\text{GAIN}}}{20\,\text{k}\Omega}$
   - From `RECT_MID` (`-V_GAIN`) via `R9` (`10 kΩ`): $I_9 = -\frac{V_{\text{GAIN}}}{10\,\text{k}\Omega}$
   - Total current entering `U1C -`: $I_{\text{sum}} = +\frac{V_{\text{GAIN}}}{20\,\text{k}\Omega} - \frac{2\,V_{\text{GAIN}}}{20\,\text{k}\Omega} = -\frac{V_{\text{GAIN}}}{20\,\text{k}\Omega}$
   - `R10` (`20 kΩ`) must supply the opposite current from `V_RECT`, so:

$$V_{\text{RECT}} = -R_{10} \cdot I_{\text{sum}} = -20\,\text{k}\Omega \cdot \left(-\frac{V_{\text{GAIN}}}{20\,\text{k}\Omega}\right) = \mathbf{+1.00\,V_{\text{GAIN}}}$$

#### Case B: Negative Half-Cycle (`V_GAIN < 0`)
1. `V_GAIN < 0` pulls current leftward *out* of `U1B -` (`Pin 6`) through `R6`.
2. `U1B OUT` (`Pin 7`) swings **positive** (`~+0.6 V`).
3. That forward-biases `D1` (`ON`)—shorting `U1B` into a simple `0 V` follower—and reverse-biases `D2` (`OFF`).
4. Because `D2` is disconnected and `U1C -` (`Pin 9`) is at `0 V` virtual ground, no current flows through `R7` or `R9`, so **`RECT_MID = 0 V`**.
5. Now `U1C` sees only the `V_GAIN` branch through `R8` (`20 kΩ`) and inverts it via `R10` (`20 kΩ`):

$$V_{\text{RECT}} = -\frac{R_{10}}{R_8} V_{\text{GAIN}} = -\frac{20\,\text{k}\Omega}{20\,\text{k}\Omega} V_{\text{GAIN}} = \mathbf{-V_{\text{GAIN}} = +|V_{\text{GAIN}}|}$$

#### Result: Exact `1.00×` Absolute Value
Regardless of input polarity, `V_RECT = +1.00 · |V_GAIN| ≥ 0`. Notice why `R8` and `R10` are both `20 kΩ` (`1%`): matching `R8 = R10 = 20 kΩ` and `R9 = 10 kΩ` gives exact `1.00×` unity rectification so `U1C` never clips earlier than `U1A`, preserving full `~10.5 V` headroom.

---

### Stage 3: Active Zero-Deadzone Peak Detector, Attack/Release & Buffer
**Components:** `U2C`, `U2D`, `D3` (`1N4148WS`), `D5` (`1N4148WS`), `R11` (`200 kΩ`), `C10` (`100 pF` C0G), `R12` (`150 Ω`), `RV2` (`A50k`), `C2` (`1 µF` film), `R13` (`10 kΩ`), `RV3` (`A1M`), `R14` (`4.7 MΩ`)

```text
  V_RECT ──────▶ ┌─(+)───┐
                 │  U2C  ├──────────┬───────────▶ [D3: A──▶K] ──[R12: 150R]──[RV2: A50k ATK]──┬──▶ ENV_CAP ──▶ ┌─(+)───┐
         ┌──────▶└─(-)───┘          │                                                         │                │  U2D  ├───┬──▶ V_ENV_BUF
         │         │                │                                                  [C2: 1uF Film]      ┌─▶ └─(-)───┘   │
         │         ├──[D5: A──▶K]───┤  (Anti-saturation clamp)                                │            └─────────────┘
         │         │                │                                                    [R13: 10k]                      │
         │         └─[C10: 100pF]───┘  (Loop compensation)                                    │                          │
         │                                                                          [RV3: A1M || R14: 4.7M]              │
         │                                                                                    │                          │
         │                                                                                   GND                         │
         └───────────────────────────────────────────[R11: 200k]─────────────────────────────────────────────────────────┘
```

This is the core of the module—turning the `2×`-frequency pulsating humps at `V_RECT` into a clean, musical envelope voltage (`V_ENV_BUF`).

#### 1. Why Put the Peak Diode `D3` *Inside* an Op-Amp Loop? (`U2C` + `U2D`)
In basic textbook envelope followers, `V_RECT` simply feeds a diode `D3` straight into `C2`. That passive diode creates a `~0.6 V` deadband—any audio signal producing less than `0.6 V` peak never even charges `C2`, killing quiet tails and drifting by `~-2 mV/°C` with temperature.

Here, **`U2C`** and **`U2D`** team up to erase that deadzone completely:
- `U2C` acts as a high-speed comparator/driver: its `+` input (`Pin 10`) watches `V_RECT`, and its `-` input (`Pin 9`) watches the *actual stored voltage* on `C2` (`V_ENV_BUF`, via `R11 = 200 kΩ`).
- Whenever `V_RECT` rises **even a couple of millivolts above** `V(C2)`, `U2C`'s output (`Pin 8`) shoots positive (`up toward +10.5 V`), easily paying `D3`'s `~0.6 V` forward drop and pushing charge into `C2` through `R12` + `RV2`.
- The instant `V(C2)` reaches `V_RECT`, `U2C` stops pushing more charge. Even a `75 mV` (`15 mVpp` at full `GAIN`) quiet tail charges `C2` accurately to `75 mV` with **`0 mV` diode deadzone**.

#### 2. Attack (`R12`, `RV2 = A50k`, `C2 = 1 µF`)
When `V_RECT > V(C2)`, charging current flows through `D3` → `R12` (`150 Ω`) → `RV2` (`A50k` `ATK` pot) → `C2` (`1 µF`):
- **Time Constant Span:** $\tau_{\text{atk}} = R_{\text{atk}} C_2$, giving **`0.15 ms`** at `0%` CCW (`150 Ω`) up to **`50.15 ms`** at `100%` CW (`50.15 kΩ`), with `~7.7 ms` at 12 o'clock thanks to the **`A50k` audio/log taper** (which gives fine control over snappy `0.2–8 ms` drum/pluck transients).
- **Why `R12 = 150 Ω`?** Without `R12`, turning `ATK` to `0 Ω` would make `U2C` try to slam a discharged `1 µF` capacitor straight to `+10 V` in nanoseconds, hitting current limits and risking ringing. `150 Ω` caps surge current safely while still delivering a crisp `0.15 ms` instant attack.
- **Active Slewing Behavior:** Because `U2C` drives `D3`'s anode near `+10.5 V` whenever `V_RECT > V(C2)`, charging acts as a fast active slew toward `+10.5 V` (`I_chg ≈ (10.5 V - V(C2)) / R_atk`) that stops cleanly at `V(C2) = V_RECT`—making transients snap cleanly up to target.

#### 3. Release (`R13`, `RV3 = A1M`, `R14 = 4.7 MΩ`, `C2 = 1 µF`)
When `V_RECT` falls below `V(C2)`, `U2C OUT` drops below `V(C2)`, **reverse-biasing `D3` (`OFF`)**. `C2` cannot discharge backward into `U2C`, so its stored voltage decays exponentially to `GND` through `R13` (`10 kΩ`) + (`RV3 || R14`):
- **`0%` CCW (`RV3 = 0 Ω`):** $\tau_{\text{rel}} = 10\,\text{k}\Omega \times 1\,\mu\text{F} = \mathbf{10.0\,\text{ms}}$ (fast, tracks low-frequency bass/CV ripple).
- **`50%` (12 o'clock, `A1M` ~15% = `150 kΩ || 4.7 MΩ`):** $\tau_{\text{rel}} \approx \mathbf{155\,\text{ms}}$ (natural musical decay).
- **`100%` CW (`1 MΩ || 4.7 MΩ = 825 kΩ`):** $\tau_{\text{rel}} \approx \mathbf{835\,\text{ms}}$ (long `~2.5 s` decay to 5% remaining voltage).

Notice the two protection details on `RV2` and `RV3`:
- Both pots are wired as **fail-safe rheostats** (`Wiper` tied to `CW`): if the wiper hops off the carbon track briefly, the connection stays intact at maximum resistance (`50 kΩ` / `1 MΩ`) rather than going open-circuit.
- **`R14` (`4.7 MΩ`) parallels `RV3` (`A1M`):** Even if an external pot lug wire breaks, `R14` ensures `C2` still bleeds smoothly instead of latching the envelope output stuck high forever.

#### 4. Three Hidden Engineering Heroes in Stage 3
Beginners often glance at a schematic and wonder what tiny extra components like `U2D`, `D5`, and `C10`/`R11` are doing. Each one solves a real-world analog pitfall:

1. **Dedicated Unity Buffer (`U2D`):**  
   If `Stage 4` (`OFFSET` `100 kΩ` divider) or `Stage 5` (`LED` `10 kΩ` divider) tapped `C2` (`ENV_CAP`) directly, they would constantly drain `C2`, wrecking long `Release` times and creating voltage-divider droop at fast `Release` settings. Wiring **`U2D`** (`Pin 12` `+` to `ENV_CAP`, `Pin 13` `-` tied to `Pin 14` `OUT`) creates a `~1 pA` impedance wall: `C2` never notices downstream loads, so `Release` never drops peak output voltage (`0%` release tap droop).
2. **Anti-Saturation Clamp (`D5 = 1N4148WS`):**  
   During `Release`, `V_RECT < V(C2)`, so `U2C`'s `-` input is higher than its `+` input. Without `D5`, `U2C` would slam its output all the way to `-11.6 V`. On the next drum transient, `U2C` would have to climb `~12–22 V` out of saturation before `D3` could even turn on! **`D5`** (Anode to `PEAK_INV`, Cathode to `PEAK_OP_OUT`) closes a negative clamp loop during decay, holding `U2C OUT` gently at `V_RECT - 0.55 V`—allowing **`~55 ns`** wake-up (`20 V/µs` slew) when the next peak arrives.
3. **Loop Compensation (`R11 = 200 kΩ`, `C10 = 100 pF` C0G) & Film Dielectric (`C2`):**  
   Putting a variable `RC` delay (`R12 + RV2` into `C2 = 1 µF`) *inside* `U2C`'s feedback loop introduces a low-frequency phase lag (`3.17 Hz–1.06 kHz`) that would normally make `U2C` ring or oscillate. **`C10` (`100 pF` C0G)** directly bridges `U2C OUT` to `U2C -`, working with **`R11` (`200 kΩ`)** to bypass the slow capacitor loop above `f_z = 1 / (2π · 200 kΩ · 100 pF) = 7.96 kHz`. This guarantees **`> 70°` phase margin** across every setting of the `ATK` knob. Meanwhile, making **`C2` a `1 µF 63 V` box film capacitor** guarantees zero voltage-dependent capacitance loss and zero knock-induced piezoelectric spikes.

---

### Stage 4: Output Buffering, Linear `OFFSET`, Polarity Inversion & Jack Protection
**Components:** `U1D`, `R15`–`R20`, `RV4` (`B10k`), `U2A`, `R22` (`10 kΩ`), `R23` (`10 kΩ`), `D10` (`BAT54S`), `D11` (`BAT54S`), `R21` (`1 kΩ 1 W`), `R24` (`1 kΩ 1 W`), `J2`, `J3`

```text
  V_ENV_BUF ──[R15: 100k]──┬──────────▶ ┌─(+)───┐
                           │            │  U1D  ├──┬──▶ V_OUT_BUF ──┬──[D10: BAT54S]──▶ ±12V_PROT
                      [R16: 100k]   ┌─▶ └─(-)───┘  │                │
                           │        │              │          [R21: 1k 1W 2512] ──▶ J2.Tip (OUT, TN=NC)
                          GND       ├──[R20: 100k]─┘
                                    │
                               [R19: 100k]
                                    │
  +12V_PROT ──[R17: 6.8k]── RV4.1 (CCW) ── RV4.2 (Wiper)
  -12V_PROT ──[R18: 6.8k]── RV4.3 (CW)     [RV4 = B10k Linear]

  V_OUT_BUF ──[R22: 10k]───┬──────────▶ ┌─(-)───┐
                           │            │  U2A  ├──┬──▶ V_INV_BUF ──┬──[D11: BAT54S]──▶ ±12V_PROT
                           │    GND ──▶ └─(+)───┘  │                │
                           │                       │          [R24: 1k 1W 2512] ──▶ J3.Tip (INV_OUT, TN=NC)
                           └──────[R23: 10k]───────┘
```

#### 1. Subtracting/Adding DC `OFFSET` Without Clipping (`U1D`, `RV4`, `R15`–`R20`)
An envelope naturally runs from `0 V` to `+10 V`. Sometimes you want it shifted downward (`-4.7 V` to `+5.3 V`) to modulate a filter symmetrically around center pitch, or lifted slightly above `0 V`.

`U1D` is wired as a **unity-ish (`0.975×`) difference amplifier**:
- **Non-inverting leg (`U1D +`):** `R15` (`100 kΩ`) and `R16` (`100 kΩ`) divide `V_ENV_BUF` cleanly in half: $V_+ = 0.500\,V_{\text{ENV\_BUF}}$.
- **Offset voltage source (`RV4`):** `RV4` (`B10k`, **`10 kΩ` linear taper**—linear because center position should represent `0.00 V` offset cleanly!) sits between `R17` (`6.8 kΩ` to `+12V_PROT`) on `Pin 1` (`CCW`) and `R18` (`6.8 kΩ` to `-12V_PROT`) on `Pin 3` (`CW`).
  - With `±11.6 V` rails, the unloaded wiper voltage $V_{\text{th}}$ sweeps linearly from **`+4.92 V` (full CCW)** through **`0.00 V` (center)** to **`-4.92 V` (full CW)**.
  - Its Thevenin source resistance `R_pot,th` is only `4.84 kΩ` (at extremes) to `5.90 kΩ` (at center).
- **Inverting leg (`U1D -`):** `R19` (`100 kΩ`) connects the `OFFSET` wiper to `U1D -`, and `R20` (`100 kΩ`) provides feedback from `V_OUT_BUF`.

Notice the beauty of **impedance scaling** (`10 kΩ` pot driving `100 kΩ` summing resistor):
$$V_{\text{OUT\_BUF}} = \frac{1}{2}\left(1 + \frac{100\,\text{k}\Omega}{100\,\text{k}\Omega + R_{\text{pot,th}}}\right)V_{\text{ENV\_BUF}} - \left(\frac{100\,\text{k}\Omega}{100\,\text{k}\Omega + R_{\text{pot,th}}}\right)V_{\text{th}}$$
- Because `R_pot,th` (`4.84–5.90 kΩ`) is `~18×` smaller than `R19` (`100 kΩ`), adjusting `OFFSET` changes envelope gain by only **`±0.25%`** (`0.972×` at center to `0.977×` at extremes)!
- Keeping gain at **`~0.975×`** (rather than `2×+`) means the full `0–10 V` detector output maps cleanly onto `0–9.75 V` at `OUT` with **zero premature clipping** below the `~10.5 V` rail ceiling.
- Because `V_th` feeds the *inverting* input (`-` sign in the equation), wiring `Pin 1` (`CCW`) toward `+12V_PROT` and `Pin 3` (`CW`) toward `-12V_PROT` flips the polarity neatly so **turning `OFFSET` clockwise shifts `OUT` positive** (`-4.69 V` CCW to `+4.69 V` CW, with `< 1%` linearity error).

#### 2. Inverted Output (`U2A`, `R22`, `R23`)
`U2A` takes `V_OUT_BUF` through `R22` (`10 kΩ`) into its inverting input (`Pin 2`, with `Pin 3` `+` grounded) and feeds back through `R23` (`10 kΩ`):

$$V_{\text{INV\_BUF}} = -\frac{R_{23}}{R_{22}}\,V_{\text{OUT\_BUF}} = \mathbf{-1.00\,V_{\text{OUT\_BUF}}}$$

In modular patching, `INV_OUT` is a classic **sidechain ducking** output: as a kick drum hits and `OUT` rises from `0 V` to `+8 V`, `INV_OUT` drops from `0 V` to `-8 V` (or `+5 V` down to `-3 V` with `OFFSET` turned up), automatically turning down a synth pad's VCA or closing a filter in rhythm.

#### 3. Surviving Real-World Patching Mistakes (`D10`, `D11`, `R21`, `R24`, `J2`, `J3`)
Eurorack users routinely hot-plug patch cables and occasionally patch two module outputs together by mistake:
- **Cable Capacitance Isolation (`R21`, `R24` = `1 kΩ`):** Long patch cords add `100–300 pF` of capacitance directly on an op-amp's output, which can cause high-frequency oscillation. Placing `1 kΩ` in series isolates the cable from `U1D` and `U2A`, while forming only a `~1%` voltage divider into standard `100 kΩ` Eurorack inputs.
- **Why `1 W 2512` Resistors (`R21`, `R24`)?** If `OUT` is sitting at `-10.5 V` and someone accidentally patches it straight into another module's `+12 V` output, `22.5 V` sits across `R21`: $P = \frac{(22.5\,\text{V})^2}{1000\,\Omega} = \mathbf{0.506\,\text{W}}$. Tiny `0603` (`0.1 W`) or even `1/4 W` (`0.25 W`) resistors would burn up under a sustained patch error. Upgrading `R21` and `R24` to **`1 W` `2512`** resistors keeps worst-case continuous fault heat at just `51%` of rated capacity.
- **Why `D10` and `D11` (`BAT54S`) Sit *Behind* `R21`/`R24`:** Placing the ESD/rail clamp diodes on the **op-amp side** (`V_OUT_BUF`, `V_INV_BUF`) instead of directly on the jack tips means `R21`/`R24` (`1 kΩ`) limits any external `> +12 V` fault or ESD zap before it hits `BAT54S` (`+15 V` fault injects just `~3 mA`, easily absorbed by the module's normal supply current).
- **Output Jack Switches (`J2.TN = NC`, `J3.TN = NC`):** Unlike the input jack (`J1.TN → GND`), output jacks leave `TN` completely **unconnected (`NC`)**. Grounding an output jack's switch pin would short `OUT` to `GND` through `R21` whenever no cable is plugged in!

---

### Stage 5: Visual Metering — Constant-Current LED Driver
**Components:** `U2B`, `R25` (`10 kΩ`), `R26` (`10 kΩ`), `R27` (`1 kΩ`), `D4` (`3 mm` LED), `D6` (`1N4148WS`)

```text
  V_ENV_BUF ──[R25: 10k]──┬──▶ ┌─(+)───┐
                          │    │  U2B  ├──▶ V_LED_DRV
                     [R26: 10k]└─(-)───┘        │
                          │       ▲        [D4: 3mm LED (A→K)] || [D6: 1N4148WS (K←A)]
                         GND      │             │
                                  └─────────────┴── LED_SENSE ──[R27: 1k]──▶ GND
```

#### Why Not Just Drive the LED Through a Resistor?
A standard `3 mm` LED has a turn-on threshold (`V_f`): `~1.8 V` for red, `~2.0–2.2 V` for green/yellow, and `~3.0–3.4 V` for blue/white. If you drive an LED from `V_ENV_BUF` through a plain resistor, the LED stays completely dark during the bottom `2–3 V` of every envelope, and swapping green for red completely changes brightness.

#### How Constant-Current Feedback Solves It (`0.50 mA/V`)
1. `R25` (`10 kΩ`) and `R26` (`10 kΩ`) halve `V_ENV_BUF` onto `U2B +` (`Pin 5`): $V_+ = 0.500\,V_{\text{ENV\_BUF}}$ (`0 V` to `+5 V` for a `0–10 V` envelope).
2. **`D4` (`3 mm` LED) sits *inside* `U2B`'s negative feedback loop** (`Pin 7` `OUT` → `D4` Anode → `D4` Cathode → `Pin 6` `-` `LED_SENSE` → `R27 = 1 kΩ` to `GND`).
3. Because `U2B` always adjusts its output until `V(LED_SENSE) = V_+`, the voltage across `R27` is locked to exact `0.500 · V_ENV_BUF`. By Ohm's law, all current flowing through `R27` had to come down through `D4`:

$$I_{\text{LED}} = \frac{0.500 \cdot V_{\text{ENV\_BUF}}}{1\,\text{k}\Omega} = \mathbf{0.50\,\text{mA/V} \cdot V_{\text{ENV\_BUF}}}$$

- **At `0.00 V` idle:** **`0.00 mA`** (dead dark—zero bleed current).
- **At `+50 mV` quiet envelope:** `0.025 mA` (starts glowing smoothly right above `~20 mV`).
- **At `+5.0 V`:** **`2.50 mA`** (crisp studio brightness).
- **At `+10.0 V`:** **`5.00 mA`** (bright full-scale peak).
- **Color-independent:** Whether you solder a `1.8 V` red LED or a `3.4 V` white/blue LED, `U2B` simply raises `V_LED_DRV` (`Pin 7`) by the needed `V_f` while keeping current locked to `0.50 mA/V`.
- **Reverse Clamp (`D6 = 1N4148WS`):** Placed antiparallel across `D4` (`A` at `LED_SENSE`, `K` at `V_LED_DRV`), `D6` clamps any tiny negative op-amp offset (`V_OS`) to `≤ 0.6 V` reverse voltage so `D4` is never reverse-stressed.

---

## Part II — Supporting Systems: Power, Components & Physical Architecture

---

### Section 6: Power Supply Handling, Protection & Decoupling
**Components:** `J4` (`2×5` shrouded IDC header), `D7`, `D8` (`1N5819WS`), `R28`, `R29` (`10 Ω`), `C3`, `C4` (`47 µF 35 V` electrolytic), `C5`–`C8` (`100 nF 50 V` X7R)

```text
  J4 (2x5 Shrouded IDC)
   ├─ Pins 9, 10 (+12V_IN) ──▶ [D7: 1N5819WS (A→K)] ──▶ [R28: 10R] ──┬──▶ +12V_PROT (+11.6 V)
   │                                                                 ├── [C3: 47uF 35V (+ to rail)]
   │                                                                 └── [C5, C7: 100nF] (at U1.4, U2.4)
   ├─ Pins 3–8 (GND) ────────────────────────────────────────────────────▶ Solid Ground Plane
   │
   └─ Pins 1, 2 (-12V_IN)  ◀── [D8: 1N5819WS (K◀─A)] ◀── [R29: 10R] ◀──┬── -12V_PROT (-11.6 V)
     (Red Stripe)                                                    ├── [C4: 47uF 35V (+ to GND!)]
                                                                     └── [C6, C8: 100nF] (at U1.11, U2.11)
```

#### 1. Doepfer A-100 Power Connector (`J4`)
`J4` is a **shrouded, keyed `2×5` (`2.54 mm`) IDC header** mounted on the rear (`B.Cu`) following the Eurorack standard:
- **Pins `1, 2`:** `-12V_IN` (marked by the red stripe on Eurorack ribbon cables).
- **Pins `3–8`:** `GND` (all 6 pins bonded solidly to the PCB ground plane for a quiet analog `0 V` reference).
- **Pins `9, 10`:** `+12V_IN`.

#### 2. Series Schottky Reverse-Polarity Protection (`D7`, `D8`)
Even with a keyed shrouded header, unkeyed DIY ribbon cables can still be forced on backward. **`D7` and `D8`** (`1N5819WS`, `40 V, 1 A` Schottky diodes) sit in series with both incoming power rails:
- **`D7` (`+12 V` rail):** Anode (`A`) to `+12V_IN`, Cathode (`K`) downstream toward `+12V_PROT`. Passes positive current cleanly, blocks reversed `-12 V`.
- **`D8` (`-12 V` rail):** **Reversed orientation!** Cathode (`K`) to `-12V_IN`, Anode (`A`) downstream toward `-12V_PROT`. Because current on the negative rail flows *out* of the circuit back toward `-12V_IN`, `D8` conducts cleanly under normal `-12 V` operation and blocks reversed `+12 V`.

Why **Schottky** diodes instead of standard `1N400x` silicon diodes? At the module's `~7.5 mA` idle (`~12.5 mA` max LED) draw, a `1N5819WS` drops only **`~0.28 V`** (versus `~0.7 V` for regular diodes), preserving maximum op-amp headroom—and if plugged in backward, they draw **`0 mA`** indefinitely with zero overheating.

#### 3. RC Rail Filtering & Bulk Reservoirs (`R28`, `R29`, `C3`, `C4`)
Downstream of `D7`/`D8` (so the electrolytic caps are also protected against reverse polarity!), `R28` (`10 Ω`) and `R29` (`10 Ω`) feed two `47 µF 35 V` bulk aluminum electrolytic capacitors (`C3`, `C4`):
- **Low-Pass Supply Filter:** Each `10 Ω` + `47 µF` pair forms a **`339 Hz` RC filter** ($f_c = \frac{1}{2\pi \cdot 10\,\Omega \cdot 47\,\mu\text{F}}$) that smooths hot-plug inductive inrush spikes and rejects high-frequency switching-PSU buzz coming from neighboring digital Eurorack modules.
- **Protected Rail Voltage:** At `~12.5 mA` peak draw, `D7`/`D8` (`~0.28 V`) plus `R28`/`R29` (`12.5 mA × 10 Ω ≈ 0.12 V`) drop `~0.4 V` total per rail, establishing clean **`±11.6 V`** internal rails (`+12V_PROT`, `-12V_PROT`).
- **Negative-Rail Electrolytic Polarity (`C4`):** A classic beginner pitfall! Polarized capacitors require their `+` terminal to be more positive than their `-` terminal. On `C3` (`+12 V` rail), `+` goes to `+12V_PROT` and `-` goes to `GND`. On `C4` (`-12 V` rail), **`GND` (`0 V`) is higher than `-11.6 V`**, so **`C4 +` goes to `GND` and `C4 -` goes to `-12V_PROT`!**

#### 4. Local High-Frequency Decoupling (`C5`–`C8`)
Large `47 µF` electrolytic capacitors (`C3`, `C4`) have internal inductance that makes them slow above tens of kilohertz. When `U2C` fires a sharp peak pulse into `C2` or `U2B` steps LED current, the op-amps need tiny, ultra-fast energy reservoirs right beside their power pins.

Four **`100 nF` (`50 V` X7R `0603`)** ceramic bypass capacitors (`C5`–`C8`) sit **`< 5 mm`** from `U1` (`Pin 4` `+12V_PROT`, `Pin 11` `-12V_PROT`) and `U2` (`Pin 4`, `Pin 11`) straight to `GND` via immediate stitching vias—keeping high-speed `TL074H` op-amps completely free of supply-rail bounce and HF oscillation.

---

### Section 7: Op-Amp Architecture, Component Choices & PCB Split

#### 1. Zero-Spare `2 × TL074H` Allocation (`8` Active Units)
Every single op-amp channel inside `U1` and `U2` (`TL074HIDR`, `SOIC-14`) has a dedicated job—leaving `0` floating spare op-amps (floating op-amps can oscillate and inject noise into active audio stages):

| IC / Unit | Pins (`+`, `-`, `OUT`) | Stage & Role |
|---|---|---|
| **`U1A`** | `3`, `2`, `1` | Stage 1: Fixed `+11.0×` input amplifier (`+0.45×` to `+10.04×` overall) |
| **`U1B`** | `5`, `6`, `7` | Stage 2: Precision full-wave rectifier half-wave switch |
| **`U1C`** | `10`, `9`, `8` | Stage 2: Precision `1.00×` rectifier summer (`V_RECT = +\|V_GAIN\|`) |
| **`U1D`** | `12`, `13`, `14` | Stage 4: `0.975×` difference amplifier & `OFFSET` mixer (`V_OUT_BUF`) |
| **`U2A`** | `3`, `2`, `1` | Stage 4: `-1.00×` inverting output stage (`V_INV_BUF`) |
| **`U2B`** | `5`, `6`, `7` | Stage 5: `0.50 mA/V` constant-current LED driver (`D4`) |
| **`U2C`** | `10`, `9`, `8` | Stage 3: Active zero-deadzone peak detector (`D3`, `D5`, `C10`, `R11`) |
| **`U2D`** | `12`, `13`, `14` | Stage 3: Dedicated `+1×` unity buffer isolating `C2` (`V_ENV_BUF`) |

*(Both ICs share Pin `4` = `+12V_PROT` and Pin `11` = `-12V_PROT`.)*

#### 2. Why Four Different Capacitor Types Appear in One Circuit
For learners, reading the BOM ([EnvelopeFollowerBOM.md](./EnvelopeFollowerBOM.md)) reveals why engineers pick different capacitor dielectrics for different jobs:

| Capacitors | Type & Spec | Why This Type Is Chosen Here |
|---|---|---|
| `C1`, `C2` | **`1 µF 63 V` Box Film (`PET`, `P=5mm`)** | Zero piezoelectric microphonics, non-polarized, stable capacitance vs. voltage—essential for the input AC-coupling filter (`C1`) and timing integrator (`C2`). |
| `C9`, `C10` | **`22 pF`, `100 pF 50 V C0G` (`0603`)** | Class-1 `C0G` (`NP0`) ceramic has zero distortion, zero microphonics, and tight `±5%` stability—ideal inside op-amp feedback loops. |
| `C5`–`C8` | **`100 nF 50 V X7R` (`0603`)** | Compact, cheap Class-2 ceramic with low high-frequency impedance—ideal for `±12 V` DC rail decoupling right at IC pins (never put `X7R` in an audio path like `C1`/`C2`!). |
| `C3`, `C4` | **`47 µF 35 V` Aluminum Electrolytic** | High bulk capacitance per dollar for `339 Hz` power-rail filtering (`35 V` rating gives `3×` safety margin over `12 V` rails). |

#### 3. Physical Sandwich & Manufacturing Partition (`60` Total Parts)
To keep assembly straightforward and low-cost (compatible with **JLCPCB Economic single-sided PCBA**):
- **`B.Cu` Rear SMT (`49` parts, `20` BOM lines):** Both `TL074H` ICs, all `10` SMD diodes (`D1`–`D3`, `D5`–`D11`), all `29` resistors (`R1`–`R29`), and `8` SMD capacitors (`C3`–`C10`) sit strictly on the back copper layer (`B.Cu`). `15` lines are JLCPCB **Basic** (`$0` feeder fees), `1` (`R14 = 4.7 MΩ`) is **Preferred Extended** (`$0` feeder fee), and only `4` lines (`U1`/`U2`, `D9`–`D11`, `R21`/`R24`, `C3`/`C4`) incur Extended feeder fees (`$12.00` total order setup, `~$0.88` raw SMD parts/board).
- **`B.Cu` Rear Manual THT (`3` parts):** `J4` (`2×5` IDC power header) and the `9.5 mm`-tall `C1`/`C2` box film caps mount on the rear side and get hand-soldered later so they don't collide with the front panel.
- **`F.Cu` Front Panel THT (`8` parts):** Only panel-facing controls—`J1`–`J3` jacks, `RV1`–`RV4` 9 mm vertical potentiometers (`A100k`, `A50k`, `A1M`, `B10k`), and `D4` (`3 mm` LED)—mount on the front (`F.Cu`), bolted to the `3U` Eurorack panel before soldering so the panel carries all mechanical stress instead of the solder joints.

---

## Part III — Practical Learner's Reference

---

### Section 8: Signal Walkthrough & Control Cheat-Sheet

#### Follow-the-Voltage Examples (With `RV4` `OFFSET` Centered at `0.00 V`)

| Test Scenario | `RV1` (`GAIN`) | `V(IN_WIPER)` | `V_GAIN` (`U1.1`) | `V_RECT` (`U1.8`) | `V_ENV_BUF` (`U2.14`) | `OUT` (`J2.T`) | `INV_OUT` (`J3.T`) | `I_LED` (`D4`) |
|---|---|---|---|---|---|---|---|---|
| **Unplugged Idle** (`J1` empty) | Any | `0.00 V` | `0.00 V` | `0.00 V` | `0.00 V` | `0.00 V` | `0.00 V` | **`0.00 mA` (Dark)** |
| **Quiet Tail** (`100 mVpp` / `50 mV` pk) | `100%` CW (`~10×`) | `±45 mV` pk | `±0.50 V` pk | `+0.50 V` pk | `+0.50 V` DC | `+0.49 V` | `-0.49 V` | `0.25 mA` (Soft glow) |
| **Standard Synth Audio** (`±5 V` / `10 Vpp`) | `50%` (`~1.89×`) | `±0.86 V` pk | `±9.45 V` pk | `+9.45 V` pk | `+9.45 V` DC | `+9.19 V` | `-9.19 V` | `4.73 mA` (Bright) |
| **Hot Modular LFO** (`±10 V` / `20 Vpp`) | `0%` CCW (`+0.45×`) | `±0.41 V` pk | `±4.50 V` pk | `+4.50 V` pk | `+4.50 V` DC | `+4.37 V` | `-4.37 V` | `2.25 mA` (Mid-bright) |

*(Note: At full `OFFSET` sweep with `0 V` input, `OUT` smoothly tracks from **`-4.69 V` (CCW)** to **`+4.69 V` (CW)** and `INV_OUT` tracks opposite, while `D4` always indicates the true positive `0–10 V` envelope amplitude prior to `OFFSET`.)*

#### How Every Front-Panel Knob Shapes the Envelope

| Control | Taper / Part | Sweep Range | Musical Effect |
|---|---|---|---|
| **`GAIN` (`RV1`)** | `A100k` (Log) | `+0.45×` to `+10.04×` (`-7 dB` to `+20 dB`) | Scales input sensitivity; CCW keeps `±10 V` signals unclipped, 12 o'clock fits `±5 V` audio, CW boosts quiet acoustic/mic sources. |
| **`ATK` (`RV2`)** | `A50k` (Log) | `0.15 ms` to `50.15 ms` (`τ`) | Sets how fast the envelope rises on transients: CCW grabs instantaneous drum snaps; CW rounds off clicks and turns bursts into smooth swells. |
| **`Release` (`RV3`)** | `A1M` (Log) | `10.0 ms` to `835 ms` (`τ`) | Sets how fast the envelope decays after silence: CCW tracks fast staccato rhythms (or creates audio-rate harmonic ripple); CW holds lush, slow tails. |
| **`OFFSET` (`RV4`)** | `B10k` (Linear) | `-4.69 V` (CCW) to `+4.69 V` (CW) | Shifts `OUT` up or down in DC voltage (and `INV_OUT` opposite), turning `0–10 V` unipolar envelopes into bipolar modulation or setting a threshold bias. |
