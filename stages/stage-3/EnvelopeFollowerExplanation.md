# How the Eurorack Envelope Follower Circuit Works

> **Companion Reference:** [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md) (circuit spec & netlist) and [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md) (verified parts list)  
> **Target Audience:** Audio electronics learners and DIY Eurorack builders  
> **Hardware Platform:** Dual `±12 V` Eurorack module using `2× TL074H` quad op-amps (`8` active op-amp stages, `59` total parts)

---

## 1. The Big Picture: What an Envelope Follower Does

An **envelope follower** listens to an oscillating AC audio signal—whose voltage swings smoothly above and below `0 V` thousands of times per second—and extracts its **overall loudness contour** as a slowly changing **positive DC control voltage (CV)** (`0 V` to `+10 V`). You can then patch that CV into a filter cutoff, VCA, or oscillator pitch so the loudness of one sound (like a drum loop, voice, or guitar) dynamically shapes another sound.

Think of the circuit as a six-step assembly line from left to right:

```text
  Bipolar Audio       Scaled AC         Positive Pulses     Smoothed CV          Bipolar Offset & Outputs
  (~±5 V / ±10 V)     (0.1x–10.1x)      (|V|, both halves)  (0 to +10 V)         (+5.15 V max shift)

  [J1 IN] ──► [1. AC Couple & Preamp] ──► [2. Full-Wave Rectifier] ──► [3. Peak Detector] ──► [4. Attack / Release]
                   (U1A)                       (U1B + U1C)                 (U2C + D3)            (RV2, C2, RV3)
                                                                                                       │
                                                                                                  [5. Buffer]
                                                                                                     (U2D)
                                                                                                  ┌────┴────┐
                                                                                                  ▼         ▼
                                                                                      [6a. LED Sink]   [6b. Offset & Outputs]
                                                                                       (U2B + D4)       (U2A → INV_OUT, U1D → OUT)
```

### Key Audio Electronics Concepts Used Throughout
1. **Virtual Ground (Inverting Op-Amp Principle):** Many stages here (`U1A`, `U1B`, `U1C`, `U2A`, `U1D`) tie the op-amp's non-inverting input (`IN+`) to `GND` (`0 V`). Whenever negative feedback is working, the op-amp adjusts its output to keep its inverting input (`IN-`) at **`0 V` too**—without drawing current into `IN-` (`~1 pA` on `TL074H`). Because `IN-` sits at `0 V` without being wired directly to ground, engineers call it a **virtual ground**. It lets us set gain purely with resistor ratios and mix multiple signals cleanly without them interfering with each other.
2. **Dual-Rail `±12 V` Power:** Eurorack synthesizers use both `+12 V` and `-12 V` around a `0 V` `GND` reference. Having a negative rail allows audio signals to swing cleanly below `0 V` without needing artificial mid-rail bias voltages, and allows `OFFSET` (`RV4`) and `INV_OUT` (`J3`) to swing negative as well as positive.

---

## 2. Main Arc: Following the Audio Signal Path

Let's trace an incoming audio signal—say a drum hit or synth bassline—from the input jack all the way to the CV outputs and indicator LED.

---

### Stage 1: Input Jack, Ground Reference & DC Blocking (`J1`, `R1`, `C1`)

**Nets:** `IN_JACK` → `IN_AC`  
**Components:** `J1` (`WQP-PJ398SM`), `R1` (`1 MΩ`), `C1` (`10 µF 50 V X7R`)

```text
  J1.T ──┬── [R1 1 MΩ] ──► GND
         │
        [C1 10 µF 50 V] ──► IN_AC ──► [R2 10 kΩ] ──► U1A.IN-
         ▲
  J1.TN ─┴─► GND (shorts IN_JACK to 0 V when unplugged)
```

#### What Happens Here
1. **Quiet When Unplugged (`J1.TN` & `R1`):** `J1` is a switched `3.5 mm` mono jack. When no cable is inserted, its internal tip-normalled switch (`TN`) connects `IN_JACK` directly to `GND`, keeping the module dead silent instead of picking up hum on an open wire. When a cable plugs in, `TN` opens and **`R1` (`1 MΩ` to `GND`)** gives any plugged-in source a permanent DC return path to ground so `C1` cannot store a stray static charge that would cause a loud "thump" at patch-in.
2. **DC Blocking (`C1`):** Real-world Eurorack patches sometimes carry steady DC offsets (for example, an LFO biased at `+5 V` or a synth voice with slight DC drift). Because an envelope follower measures *amplitude*, any steady DC offset would falsely look like a loud continuous signal. **Capacitor `C1` blocks DC while letting AC audio pass freely.**

#### Why These Exact Values & Parts?
* **High-Pass Cutoff & Ceramic DC-Bias Effect (`C1 = 10 µF 50 V X7R`):** `C1` and the preamp's input resistor `R2` (`10 kΩ`) form a high-pass filter with cutoff frequency:
  $$f_c = \frac{1}{2\pi R_2 C_1}$$
  At `0 V` DC bias (`10 µF` into `10 kΩ`), $f_c \approx 1.59\text{ Hz}$. However, **`X7R` ceramic capacitors lose significant capacitance when a steady DC voltage sits across them** (a property called *DC bias derating*). Choosing a `10 µF` capacitor rated for `50 V` in a `1206` package ensures that even if an external module applies a worst-case `12 V` DC offset on `J1`, `C1` retains at least `4.7 µF` of effective capacitance, keeping $f_c \le 3.4\text{ Hz}$—still well below the `20 Hz` bottom of human hearing.
* **Input Impedance Trade-Off (`10 kΩ` vs. `100 kΩ`):** Because `U1A.IN-` (`PREAMP_INV`) is a virtual ground (`0 V`), the audio input sees `R1` (`1 MΩ`) in parallel with `R2` (`10 kΩ`) ≈ **`10 kΩ`** input impedance. Standard Eurorack modules usually present `100 kΩ` inputs. With a `10 kΩ` input, a typical Eurorack module with a `1 kΩ` output resistor loses about `9%` of its amplitude (`10k / 11k = 0.909`, easily compensated by `GAIN`), though very high-impedance passive sources (like unbuffered guitar pickups or contact mics) will be attenuated more heavily. Raising input impedance to `100 kΩ` would simply require scaling `R2` to `100 kΩ` and `RV1` to `A1M`.

---

### Stage 2: Variable-Gain Inverting Preamp (`U1A`, `R2`, `R26`, `RV1`, `C9`, `D5`, `D6`)

**Nets:** `IN_AC` → `PREAMP_INV` → `PREAMP_OUT`  
**Op-Amp:** `U1A` (`TL074H`, pins `3=IN+`, `2=IN-`, `1=OUT`)

```text
                       ┌─────── [C9 47 pF NP0] ───────┐
                       │                              │
  IN_AC ── [R2 10 kΩ] ─┼─► U1A.IN- (2)   U1A.OUT (1) ─┴─► PREAMP_OUT
                       │    ▲                         │
                       ├── [R26 1 kΩ] ── [RV1 A100k] ─┘
                       │
                   [D5 / D6 1N4148W] (anti-parallel) ──► GND
```

#### What Happens Here
Modular audio and line-level instruments vary wildly—from `±0.5 V` guitar/line signals up to `±10 V` Eurorack oscillators. `U1A` scales the input cleanly into the `±10 V` working range of the rectifier.

Because `U1A` is an **inverting amplifier**, its gain is simply the negative ratio of the feedback branch (`R26 + RV1`) to the input resistor (`R2`):
$$A_v = -\frac{R_{26} + R_{\text{RV1}}}{R_2} = -\frac{1\,\text{k}\Omega + R_{\text{RV1}}}{10\,\text{k}\Omega}$$

* **`RV1` fully CCW (`0 Ω`):** $A_v = -1\,\text{k}\Omega / 10\,\text{k}\Omega = \mathbf{-0.10\times}$ (`-20 dB` attenuation—great for taming hot `±10 V` drums or modular voices without muting).
* **`RV1` fully CW (`100 kΩ`):** $A_v = -(1\,\text{k}\Omega + 100\,\text{k}\Omega) / 10\,\text{k}\Omega = \mathbf{-10.10\times}$ (`+20 dB` boost—enough to lift quiet `±1 V` signals up to `±10 V`).

*(Does the `-` sign inversion matter for an envelope follower? Not at all! The very next stage rectifies both positive and negative peaks equally.)*

#### Why These Design Details Matter
* **Minimum-Gain Resistor (`R26 = 1 kΩ`):** If `RV1` went straight from `U1A.IN-` to `U1A.OUT` with no series resistor, turning `GAIN` all the way down (`0 Ω`) would mute the circuit completely (`A_v = 0`), short out feedback capacitor `C9`, and risk crackling dropouts at the pot's mechanical end-stop. `R26` guarantees a clean `-0.10x` minimum floor.
* **Audio Taper Pot (`RV1 = A100k`):** Human loudness and gain ratios are logarithmic (decibels), not linear. Using an **Audio/Log (`A`) taper** pot wired so resistance grows from `L1` (CCW) to `W+L2` (CW) puts `0.1x–1.1x` in the lower half of the knob and `1.1x–10.1x` in the upper half, instead of cramming everything below `1x` into the first `10%` of rotation. Notice also that `W` (wiper) is tied to `L2` (CW): if the wiper ever momentarily lifts off the resistive track, resistance simply jumps to `101 kΩ` instead of going open-loop and slamming `U1A` to the rails.
* **Ultrasonic Stability (`C9 = 47 pF NP0`):** Placing a tiny `47 pF` capacitor across the entire feedback branch (`R26 + RV1`) rolls off gain above audio frequencies:
  $$f_c = \frac{1}{2\pi (101\,\text{k}\Omega)(47\,\text{pF})} \approx \mathbf{33.5\,\text{kHz}} \text{ (at max gain)}$$
  This keeps radio-frequency interference and op-amp phase shift from turning `U1A` into an accidental ultrasonic oscillator, while leaving `20 Hz–20 kHz` audio flat.
* **Anti-Parallel Clamps (`D5`, `D6 = 1N4148W`):** In normal linear operation, `PREAMP_INV` sits at `0 V` virtual ground, so `D5` and `D6` have `0 V` across them and do nothing (`< 1 nA` leakage). If you crank `GAIN` up on a massive input signal until `U1A.OUT` hits its `±11.4 V` supply limits, negative feedback breaks down and `IN-` tries to swing far away from `0 V`. `D5` and `D6` clamp `U1A.IN-` safely within `±0.65 V` of `GND`, protecting the op-amp inputs from overdrive (on top of `TL074H` already being phase-reversal-free).

---

### Stage 3: Precision Full-Wave Rectifier (`U1B`, `D1`, `D2`, `R3`–`R8B`, `U1C`, `C10`)

**Nets:** `PREAMP_OUT` → `RECT_INV` / `U1B_OUT` / `HALF_WAVE` / `RECT_FF_MID` → `SUM_INV` → `RECT_OUT`  
**Op-Amps:** `U1B` (`TL074H`, pins `5=IN+`, `6=IN-`, `7=OUT`), `U1C` (`TL074H`, pins `10=IN+`, `9=IN-`, `8=OUT`)

```text
  PREAMP_OUT ──┬── [R4 20k] ── [R5 20k] (40k feedforward) ──────────────┐
               │                                                        ▼
               └── [R3 20k] ──┬──► U1B.IN- (6)                     SUM_INV ──► U1C.IN- (9)
                              │       U1B.OUT (7) ─► U1B_OUT            ▲          │
                              │          │   │                          │     [R8A 20k + R8B 20k]
                         [R6 10k]     D1(A) D2(K)                       │        || [C10 15 pF]
                              │       D1(K)  │                          │          ▼
                              └──► HALF_WAVE ┴─────── [R7 10k] ─────────┴─────► RECT_OUT (U1C.OUT 8)
```

#### Why Not Just Use a Simple Diode Bridge?
A plain silicon diode needs `~0.65 V` forward voltage before it turns on, erasing quiet musical detail and distorting waveforms near `0 V`. Instead, this circuit uses a **precision op-amp full-wave rectifier** that turns *both* positive and negative halves of `PREAMP_OUT` into strictly positive voltages (`RECT_OUT = +1.00 × |PREAMP_OUT|`) with zero diode drop.

#### How the Two Half-Cycles Work
Notice how the signal splits into **two paths** that meet at `U1C`'s virtual ground (`SUM_INV`):
1. A **feedforward path** (`R4 + R5 = 40 kΩ`) straight from `PREAMP_OUT` to `U1C`.
2. A **half-wave rectifier path** through `U1B` (`R3 = 20 kΩ`, `R6 = 10 kΩ`) and `R7 = 10 kΩ` into `U1C`.

Let's follow both polarities of $V_{\text{pre}} = V(\text{PREAMP\_OUT})$:

* **When $V_{\text{pre}} > 0$ (positive half-cycle at `PREAMP_OUT`):**
  1. Positive voltage pushes current through `R3` (`20 kΩ`) into `U1B.IN-`, making `U1B.OUT` swing **negative**.
  2. `D1` (cathode at `0 V`, anode negative) turns **OFF**. `D2` (cathode negative) turns **ON**.
  3. Negative feedback closes through `D2` and `R6` (`10 kΩ`), forcing node `HALF_WAVE` to:
     $$V_{\text{HALF\_WAVE}} = -V_{\text{pre}} \cdot \frac{R_6}{R_3} = -V_{\text{pre}} \cdot \frac{10\,\text{k}\Omega}{20\,\text{k}\Omega} = \mathbf{-0.5\,V_{\text{pre}}}$$
     *(Because `D2` is inside `U1B`'s feedback loop, `U1B` automatically drops `U1B_OUT` an extra `~0.65 V` lower so `HALF_WAVE` lands at the exact `-0.5x` voltage without diode loss!)*
  4. Now look at the currents entering `U1C.IN-` (`SUM_INV`, `0 V` virtual ground):
     $$I_{\text{sum}} = \underbrace{\frac{V_{\text{pre}}}{40\,\text{k}\Omega}}_{\text{feedforward }(R_4+R_5)} + \underbrace{\frac{-0.5\,V_{\text{pre}}}{10\,\text{k}\Omega}}_{\text{half-wave }(R_7)} = \frac{V_{\text{pre}}}{40\,\text{k}\Omega} - \frac{2\,V_{\text{pre}}}{40\,\text{k}\Omega} = -\frac{V_{\text{pre}}}{40\,\text{k}\Omega}$$
  5. `U1C` pushes that current back through `R8A + R8B` (`40 kΩ`), producing:
     $$V_{\text{RECT\_OUT}} = -I_{\text{sum}} \cdot 40\,\text{k}\Omega = \mathbf{+1.00\,V_{\text{pre}}}$$

* **When $V_{\text{pre}} < 0$ (negative half-cycle at `PREAMP_OUT`):**
  1. Negative voltage pulls current out of `U1B.IN-`, making `U1B.OUT` swing **positive**.
  2. `D1` turns **ON**, clamping `U1B.OUT` cleanly at `~+0.65 V` (preventing `U1B` from saturating against `+12 V` so it recovers fast at zero crossings!).
  3. `D2` is **reverse-biased (OFF)**, disconnecting `U1B.OUT` from `HALF_WAVE`. With `D2` off, `R6` and `R7` simply tie `HALF_WAVE` to two `0 V` virtual grounds, so $V_{\text{HALF\_WAVE}} = \mathbf{0\,\text{V}}$ (zero current through `R7`).
  4. Now `U1C` sees **only** the negative feedforward current through `R4 + R5` (`40 kΩ`), which `U1C` inverts back to positive:
     $$V_{\text{RECT\_OUT}} = -V_{\text{pre}} \cdot \frac{40\,\text{k}\Omega}{40\,\text{k}\Omega} = \mathbf{+1.00\,|V_{\text{pre}}|}$$

```text
  PREAMP_OUT:    ╭─╮       ╭─╮       ╭─╮
                 ╯ ╰─╮   ╭─╯ ╰─╮   ╭─╯ ╰─  (+10 V to -10 V AC)
                     ╰───╯     ╰───╯

  HALF_WAVE:     ────╮   ╭─────╮   ╭─────  (0 V and -5 V, -0.5x inverted halves)
                     ╰───╯     ╰───╯

  RECT_OUT:      ╭─╮ ╭───╮ ╭─╮ ╭───╮ ╭─╮   (0 V to +10 V, exact 1.00x |PREAMP_OUT|)
                 ╯ ╰─╯   ╰─╯ ╰─╯   ╰─╯ ╰─
```

#### Why These Design Details Matter
* **Why Scale `U1B` to `-0.5x`?** If `U1B` ran at `-1.0x`, a `+10.5 V` signal at `PREAMP_OUT` would require `HALF_WAVE = -10.5 V` and `U1B_OUT = -11.2 V` (due to `D2`'s drop), squeezing right up against the `-11.6 V` negative rail. Running `U1B` at `-0.5x` keeps `U1B_OUT` well within `-6.2 V` even at maximum amplitude, giving huge headroom!
* **Why `1%` Resistors (`10 kΩ` and `20 kΩ` Series Pairs)?** Because positive and negative half-cycles travel different resistor paths, loose `5%` resistors would make positive peaks taller than negative peaks, injecting steady hum/ripple into the envelope. Using `1%` `0603` resistors keeps both halves matched, and pairing `20 kΩ + 20 kΩ` for `40 kΩ` (`R4+R5` and `R8A+R8B`) achieves exact `1.00x` unity gain while reusing the existing `20 kΩ` BOM line.
* **`C10 = 15 pF NP0` Across `R8A + R8B`:** Damps high-frequency switching glitches (`f_c ≈ 265 kHz`) as `D1` and `D2` hand off conduction at every zero crossing.

---

### Stage 4: Active Zero-Deadzone Peak Detector (`U2C`, `D3`)

**Nets:** `RECT_OUT` → `U2C_OUT` / `PEAK_DET`  
**Op-Amp:** `U2C` (`TL074H`, pins `10=IN+`, `9=IN-`, `8=OUT`), **Diode:** `D3` (`1N4148W`)

```text
  RECT_OUT ──► U2C.IN+ (10)
               U2C.OUT (8) ──► [D3 A→K] ──┬──► PEAK_DET ──► [R28 470 Ω] ──► [RV2 ATK] ──► ENV_RAW
                                          │
                                      U2C.IN- (9)
```

#### What Happens Here
At `RECT_OUT`, the signal is all positive—but it still plunges back down to `0 V` twice every audio cycle! We need a **one-way valve** that charges our smoothing capacitor on audio peaks, then blocks the capacitor from discharging backward into `U1C` during waveform valleys.

If you just put a diode (`D3`) directly in series without an op-amp, `D3` throws away the bottom `~0.65 V` of every signal (and drifts `-2 mV/°C` with temperature). Quiet passages vanish completely.

Instead, **`U2C` places `D3` inside its negative-feedback loop**:
* **When `RECT_OUT` is higher than `PEAK_DET` (rising wave / attack):** `U2C` drives its output up to `V(RECT_OUT) + 0.65 V`, forward-biasing `D3` so that `PEAK_DET` equals `RECT_OUT` within `U2C`'s tiny `~1 mV` input offset voltage. The `0.65 V` diode deadzone completely disappears!
* **When `RECT_OUT` falls below `ENV_RAW` (between audio cycles / decay):** `U2C.IN-` (`PEAK_DET`, pulled to `ENV_RAW` through `R28 + RV2`) is now higher than `U2C.IN+` (`RECT_OUT`). `U2C.OUT` swings down to its negative rail (`~-11.4 V`), reverse-biasing `D3` OFF. Now `C2` cannot discharge backward into `U1C` or `U2C`, and can only decay smoothly through the `Release` path!
* **Fast Recovery:** When the next audio peak rises above `ENV_RAW`, `TL074H`'s fast `20 V/µs` slew rate swings `U2C.OUT` from `-11.4 V` back up to conduction in about `~1.1 µs`—negligible even for `20 kHz` audio.

*(Why is `R28 + RV2` outside `U2C`'s feedback loop instead of inside it? If the attack resistor sat inside the loop, `U2C` would simply slam harder against `+12 V` to overcome the resistor and charge `C2` instantly anyway, defeating the `ATK` knob!)*

---

### Stage 5: Attack & Release RC Envelope Filter (`R28`, `RV2`, `C2`, `R10`, `RV3`)

**Nets:** `PEAK_DET` → `ATK_MIN` → `ENV_RAW` → `REL_MID` → `GND`

```text
  PEAK_DET ── [R28 470 Ω] ── [RV2 A50k (ATK)] ──┬──► ENV_RAW ──► U2D.IN+ (12)
                                                │
                                         ┌──────┴──────┐
                                    [C2 1 µF]     [R10 47 kΩ]
                                     WIMA Film         │
                                         │       [RV3 A1M (Release)]
                                        GND            │
                                                      GND
```

#### How `C2` Smooths Peaks into an Envelope
Capacitor `C2` (`1 µF`) acts as a tiny voltage reservoir:
* **Attack (Charging `C2`):** Whenever `PEAK_DET > ENV_RAW`, current flows from `U2C` through `D3`, `R28`, and `RV2` (`ATK`) to charge `C2`. The RC time constant $\tau_{\text{atk}} = (R_{28} + R_{\text{RV2}}) \cdot C_2$ determines how fast `ENV_RAW` climbs (`1τ` reaches `63.2%` of a step; `~5τ` settles fully):
  * **Minimum (`RV2 = 0 Ω`):** $470\,\Omega \times 1\,\mu\text{F} = \mathbf{0.47\,\text{ms}}$ (snappy transient tracking).
  * **Maximum (`RV2 = 50 kΩ`):** $50.47\,\text{k}\Omega \times 1\,\mu\text{F} = \mathbf{50.5\,\text{ms}}$ (soft, slow swell).
* **Release (Discharging `C2`):** When the audio stops or drops below `ENV_RAW`, `D3` blocks backward flow, so `C2` drains gently to `GND` through `R10` and `RV3` (`Release`). The decay time constant $\tau_{\text{rel}} = (R_{10} + R_{\text{RV3}}) \cdot C_2$ sets how long it takes to fall to `36.8%`:
  * **Minimum (`RV3 = 0 Ω`):** $47\,\text{k}\Omega \times 1\,\mu\text{F} = \mathbf{47\,\text{ms}}$ (fast, syllabic/percussive decay).
  * **Maximum (`RV3 = 1 MΩ`):** $1.047\,\text{M}\Omega \times 1\,\mu\text{F} = \mathbf{1.05\,\text{s}}$ (long, smooth sustain tail).

#### Three Key Design Choices in This Stage
1. **`R28 = 470 Ω` Attack Floor:** If `RV2` were allowed to hit `0 Ω`, a sudden `+10.5 V` step would try to dump massive current straight into an empty `1 µF` capacitor, slamming `U2C` into its `26 mA` short-circuit current limit and risking oscillation. `470 Ω` caps peak charging current at $10.5\,\text{V} / 470\,\Omega \approx \mathbf{22.3\,\text{mA}}$ (safely under `26 mA`) while still keeping a sub-millisecond `0.47 ms` attack.
2. **Why `C2` Must Be a Film Capacitor (`WIMA MKS2` `1 µF 63 V` THT):** High-capacitance ceramic capacitors (`X7R`/`X5R`) would fail miserably here for three reasons:
   * They lose **`50–80%`** of their capacitance under a `10 V` DC envelope, making `ATK`/`Release` speed up unpredictably on loud notes.
   * They are piezoelectric ("microphonic")—tapping the front panel generates phantom voltage spikes directly on `ENV_RAW`!
   * They have higher dielectric absorption and leakage during `1 s` releases.
   Because JLCPCB stocks no `1 µF` SMD film capacitors, `C2` is specified as a through-hole **WIMA `MKS2` metallized polyester film** capacitor mounted manually on the rear (`B.Cu`) so its `10.0 mm` body stays clear of the `10.5 mm` front-panel standoff.
3. **The Passive Attack/Release Divider Trade-Off (`R10 = 47 kΩ`):** Because `C2` continuously discharges through `R10 + RV3` *even while charging* through `R28 + RV2`, the two resistances form a voltage divider during sustained tones:
   $$V_{\text{max}} \le V_{\text{peak}} \cdot \frac{R_{\text{rel}}}{R_{\text{atk}} + R_{\text{rel}}}$$
   With `R10 = 47 kΩ`:
   * For typical attacks (`ATK ≤ 10 ms`, i.e., `R_atk ≤ 10.47 kΩ`) even at minimum release, loss is **`≤ 18%`** (and practically `0%` once `Release` is turned up even partway).
   * At the extreme corner case (`ATK = max 50.47 kΩ` *and* `Release = min 47 kΩ`), the steady-state divider ceiling drops by **`51.8%`** (`47k / 97.47k = 0.482x`). That's inherent to passive single-capacitor attack/release networks, and a big improvement over `R10 = 10 kΩ` (`84%` loss). Both `RV2` (`A50k`) and `RV3` (`A1M`) use **Audio/Log (`A`)** pots so millisecond adjustments spread out evenly across the knob.

---

### Stage 6: `ENV_RAW` Unity Buffer (`U2D`) & Linear LED Current Sink (`U2B`, `D4`, `D7`, `C13`, `R29`, `R30`)

**Nets:** `ENV_RAW` → `ENV_RAW_BUF` → `LED_A` / `LED_K`  
**Op-Amps:** `U2D` (`TL074H`, pins `12=IN+`, `13=IN-`, `14=OUT`), `U2B` (`TL074H`, pins `5=IN+`, `6=IN-`, `7=OUT`)

```text
                                                      +12V_PROT
                                                          │
  ENV_RAW ──► U2D.IN+ (12)                           [R30 1 MΩ]
              U2D.OUT (14) ──┬──► ENV_RAW_BUF             │
                  │          ├──► R14 (to Offset Summer)  │
              U2D.IN- (13) ──┴──► U2B.IN+ (5)             │
                                  U2B.OUT (7) ──┬── [D4 LED A→K] ──┬──► LED_K
                                                ├── [D7 1N4148W K←A]┤     │
                                                └── [C13 100 pF] ───┘  U2B.IN- (6)
                                                                          │
                                                                     [R29 2.2 kΩ]
                                                                          │
                                                                         GND
```

#### Why `U2D` Buffer Is Essential
Imagine connecting the `10 kΩ` offset resistor (`R14`) straight to `C2`! A `10 kΩ` load would drain `C2` in `10 ms`, completely ruining the `1.05 s` `Release` knob! **`U2D` is a unity-gain voltage follower (`A_v = +1.00x`)** whose `1 pA` JFET-like input draws virtually zero current from `C2`, while its low-impedance output (`ENV_RAW_BUF`) easily drives both the LED driver (`U2B`) and the output offset mixer (`U2A`).

#### How the Closed-Loop LED Current Sink (`U2B`) Works
A beginner might drive an LED straight through a resistor from `ENV_RAW_BUF`—but an LED doesn't turn on until `~1.8 V` (red) or `~3.0 V` (green/blue), leaving low envelopes invisible! Instead, `U2B` drives **`D4` inside its feedback loop** as a **voltage-controlled current sink**:
* **Above `+25 mV` (`D4` ON):** `U2B` forces `U2B.IN-` (`LED_K`) to match `U2B.IN+` (`ENV_RAW_BUF`). Since `LED_K` connects to `GND` through **`R29` (`2.2 kΩ`)**, the voltage across `R29` equals `ENV_RAW_BUF`, forcing a rock-steady current through the LED:
  $$I_{\text{LED}} \approx \frac{V_{\text{ENV\_RAW\_BUF}} - 25\,\text{mV}}{2.2\,\text{k}\Omega}$$
  That produces **`0.455 mA` per volt**—linear from near `0 V` up to **`~4.53 mA` at `+10 V`**, completely independent of LED color or forward voltage! *(Note: Because `U2B.OUT` must sit one LED drop `V_F` above `ENV_RAW_BUF`, on the `+11.55 V` protected rail `U2B.OUT` smoothly saturates near `+11.4 V` once `ENV_RAW_BUF` exceeds `~9.4–9.6 V` for standard LEDs or `~8.4 V` for high-`V_F` emerald-green LEDs—harmlessly capping peak brightness slightly early without affecting `ENV_RAW_BUF`.)*
* **In Silence (`0 V` Idle) — `R30` & `D7`:** **`R30` (`1 MΩ` to `+12V_PROT`)** injects `~11.55 µA` into `LED_K`, lifting `LED_K`'s idle threshold to **`+25 mV`** (`11.55 µA × 2.2 kΩ`). When `ENV_RAW_BUF ≤ +25 mV`, `U2B.OUT` swings slightly negative (`~-0.65 V`), turning `D4` completely OFF (**`0.00 mA`**, zero faint idle glow even on tiny `TL074H` input offsets), while **`D7` (`1N4148W`, anti-parallel across `D4`)** conducts those `11.55 µA` into `U2B.OUT` to keep the feedback loop closed and cap reverse voltage across `D4` at a safe `0.65 V`.
* **Compensation (`C13 = 100 pF NP0`):** Bridges `LED_A` and `LED_K` directly around the diodes to keep `U2B` stable across the `D7 ↔ D4` handoff. *(If using an ultrabright `500–1000 mcd` LED like LCSC `C99761`, swap `R29` to `4.7 kΩ` to keep max current at a comfortable `2.1 mA`.)*

---

### Stage 7: Bipolar Offset Mixer, Double Inversion & Protected Outputs (`RV4`, `U2A`, `U1D`, `D8`, `D9`, `R16`, `R19`, `J2`, `J3`)

**Nets:** `ENV_RAW_BUF` + `OFF_WIPER` → `SUM_OFF_INV` → `INV_DRV` → `INV_OUT_JACK` (`J3`) and `OUT_INV` → `ENV_OUT` → `OUT_JACK` (`J2`)  
**Op-Amps:** `U2A` (`TL074H`, pins `3=IN+`, `2=IN-`, `1=OUT`), `U1D` (`TL074H`, pins `12=IN+`, `13=IN-`, `14=OUT`)

```text
  +12V_PROT ── [R11 470 Ω] ──► RV4.L2 (CW)
                               RV4.W (B10k) ── [R13 20 kΩ] ──┐
  -12V_PROT ── [R12 470 Ω] ──► RV4.L1 (CCW)                  ▼
                                                        SUM_OFF_INV ──► U2A.IN- (2)
  ENV_RAW_BUF ─────────────────────────────── [R14 10 kΩ] ───┘             │  [R18 10k || C11 47pF]
                                                                           ▼
                                         ┌──── [D9 BAV99 ±12V] ◄─────── INV_DRV (U2A.OUT 1)
                                         │                                 │
                                    [R19 1k 1W]                       [R17 10 kΩ]
                                         │                                 ▼
                                    J3 INV_OUT                         OUT_INV ──► U1D.IN- (13)
                                                                                      │ [R15 10k || C12 47pF]
                                         ┌──── [D8 BAV99 ±12V] ◄────────────────── ENV_OUT (U1D.OUT 14)
                                         │
                                    [R16 1k 1W]
                                         │
                                      J2 OUT
```

#### How `OFFSET` Works Without Changing Gain
* **Bipolar Voltage Divider (`R11`, `R12`, `RV4`):** `RV4` (`B10k`, linear taper—center detent recommended) spans between `+12V_PROT` (via `R11 = 470 Ω` on `L2`/CW) and `-12V_PROT` (via `R12 = 470 Ω` on `L1`/CCW). Unloaded, the wiper (`OFF_WIPER`) sweeps linearly from **`-10.60 V` (CCW) to `+10.56 V` (CW)** (`0 V` at center). Because `RV4` is `10 kΩ` and feeds `R13 = 20 kΩ` (a relatively light load, `20 kΩ` vs. `≤ 2.7 kΩ` wiper source impedance), knob linearity suffers **`< 3.3%` loading bow**.
* **Inverting Summer (`U2A`):** `U2A.IN-` (`SUM_OFF_INV`) is a `0 V` virtual ground, so `ENV_RAW_BUF` (`R14 = 10 kΩ`) and `OFF_WIPER` (`R13 = 20 kΩ`) sum independently with **`0.00%` gain interaction**:
  $$V_{\text{INV\_DRV}} = -\frac{10\,\text{k}\Omega}{10\,\text{k}\Omega}\,V_{\text{ENV\_RAW\_BUF}} - \frac{10\,\text{k}\Omega}{20\,\text{k}\Omega}\,V_{\text{OFF\_WIPER}} = \mathbf{-1.00\,V_{\text{ENV\_RAW\_BUF}} - 0.50\,V_{\text{OFF\_WIPER}}}$$
  That feeds **`J3` (`INV_OUT`)** directly—producing a `0 to -10 V` inverted envelope shifted by `∓5.15 V` (`OFFSET`).
* **Unity Output Inverter (`U1D`):** `U1D` flips `INV_DRV` one more time (`R17 = 10 kΩ`, `R15 = 10 kΩ`, `A_v = -1.00x`):
  $$V_{\text{ENV\_OUT}} = \mathbf{+1.00\,V_{\text{ENV\_RAW\_BUF}} + 0.50\,V_{\text{OFF\_WIPER}}}$$
  Two inversions cancel out! Turning `OFFSET` **clockwise** shifts `OUT` (`J2`) **positively** (`0` to `+5.15 V`), turning **counter-clockwise** shifts `OUT` **negatively** (`0` to `-5.15 V`, letting an envelope dip below zero for bipolar modulation), and `OUT` retains exact `1.00x` (`0–10 V`) headroom. *(Note: Combining a `+10 V` peak with `+5.15 V` offset adds up to `+15.15 V`, which naturally clips cleanly at the op-amp's `~±11.4 V` supply swing limit.)*
* **HF Compensation (`C11`, `C12 = 47 pF NP0`):** Paired across `R18` and `R15` (`10 kΩ` each, $f_c \approx 339\text{ kHz}$) to preserve stability.

#### Output Protection (`D8`, `D9`, `R16`, `R19`, `J2`, `J3`)
Eurorack patch cables frequently get plugged into the wrong jack—or accidentally hot-plugged from output to output!
* **`1 kΩ 1 W` Fault Resistors (`R16`, `R19` in `2512` SMD):** Sitting *outside* the op-amp feedback loops, these isolate long patch-cable capacitance (so `U1D` and `U2A` don't oscillate) and limit fault current. If you accidentally patch `+11.4 V` from `OUT` straight into `-12 V` (`23.4 V` across `1 kΩ`), current is limited to `23.4 mA` and the resistor dissipates $23.4^2 / 1000 = \mathbf{0.55\,\text{W}}$—which would scorch a standard `0.1 W` (`0603`) or `0.25 W` resistor, but runs comfortably at `55%` of our `1.0 W` `2512` rating!
* **`BAV99` Rail Clamps (`D8`, `D9`):** Each `SOT-23` dual series diode connects its midpoint (`Pin 3`) to the op-amp output (`ENV_OUT` or `INV_DRV`), `Pin 1` (`A1`) to `-12V_PROT`, and `Pin 2` (`K2`) to `+12V_PROT`. During normal `±11.4 V` output swings they stay reverse-biased and invisible. If static electricity (ESD) or an external `> ±12 V` fault hits `J2.T` or `J3.T`, `R16`/`R19` limits current while `BAV99` shunts the surge safely into the power rails instead of frying `U1D` or `U2A`. (`J2.TN` and `J3.TN` are left unconnected—`NC`—unlike the input jack!)

---

## 3. Supporting Section: Power Handling, Protection & Decoupling

**Nets:** `±12Vin` → `±12V_DIODE` → `±12V_PROT` and `GND`  
**Components:** `J_PWR`, `D10`, `D11`, `R24`, `R25`, `C3`, `C4`, `C5`–`C8`

```text
  J_PWR (2x5 Shrouded IDC)
    Pins 9,10 (+12Vin) ──► [D10 B5819W A→K] ──► [R24 10 Ω 1206] ──┬──► +12V_PROT
                                                                  ├──► C3 (22µF 35V) ──► GND
                                                                  └──► U1.4 (+ C5 100nF), U2.4 (+ C7 100nF)

    Pins 3–8  (GND) ───────────────────────────────────────────────────► GND

    Pins 1,2  (-12Vin) ◄── [D11 B5819W K←A] ◄── [R25 10 Ω 1206] ◄──┬── -12V_PROT
                                                                  ├──► C4 (22µF 35V) ──► GND
                                                                  └──► U1.11 (+ C6 100nF), U2.11 (+ C8 100nF)
```

### How Eurorack Power Is Kept Clean and Safe
1. **Standard `2×5` Keyed IDC Header (`J_PWR`):** Pins `1–2` carry `-12Vin` (the red stripe on standard Eurorack ribbon cables), pins `3–8` are `GND`, and pins `9–10` carry `+12Vin`. The shrouded, keyed housing physically prevents backwards insertion with keyed cables.
2. **Series Schottky Reverse-Polarity Protection (`D10`, `D11 = B5819W`):** Even with a keyed header, unkeyed DIY cables can still get plugged in backwards. Placing `40 V 1 A` Schottky diodes *in series* on both rails blocks reverse current completely with zero fault stress—unlike shunt diodes across the rails, which rely on shorting out your power supply! And because `C3`, `C4`, and all ICs sit **downstream** of `D10`/`D11`, polarized electrolytic capacitors can never be reverse-biased. Note `C4`'s orientation on `-12V_PROT`: `C4.+` goes to `GND` (`0 V`) and `C4.-` goes to `-12V_PROT` (`-11.6 V`) so `0 V` is always more positive than `-11.6 V`.
3. **RC Supply Filtering & Surge Limiting (`R24`, `R25 = 10 Ω 1206` + `C3`, `C4 = 22 µF 35 V`):** Together, each `10 Ω` resistor and `22 µF` electrolytic capacitor form a **`723 Hz` low-pass filter** ($f_c = 1 / (2\pi \cdot 10 \cdot 22\mu)$) that attenuates high-frequency switching noise from Eurorack power supplies and tames hot-plug inrush current.
4. **Rail Headroom & Power Budget:**
   * Normal draw: `2× TL074H` quiescent (`~7.5 mA`) + `RV4` divider (`~2.1 mA`) + `D4` LED at `+10 V` (`~4.5 mA`) = **`~14 mA` max on `+12V`** and **`~10 mA` on `-12V`** (with transient `C2` attack spikes up to `~22.3 mA`).
   * Voltage drop: `B5819W` drops `~0.30 V` + `10 Ω` `R24`/`R25` drops `~0.10–0.15 V`, leaving **`+11.55 V / -11.60 V`** nominal on `±12V_PROT`—more than enough for full `±10 V` signals with `TL074H`.
5. **Local IC Decoupling (`C5`–`C8 = 100 nF 50 V X7R 0603`):** Large `22 µF` electrolytics react too slowly to nanoseconds-fast switching currents (like `D1`/`D2` zero crossings). Four `100 nF` ceramic capacitors sit physically within millimeters of `U1` and `U2`'s supply pins (`Pin 4` `+12V_PROT` to `GND`, and `Pin 11` `-12V_PROT` to `GND`), acting as ultra-fast local charge reservoirs so op-amp stages never corrupt each other through shared power traces.

---

## 4. Supporting Section: Op-Amp Selection, Capacitor Dielectrics & Construction

### Why `2× TL074H` (`TL074HIDR`) Instead of Classic `TL074` + `TL072`?
1. **Zero Spare/Floating Op-Amps (`8/8` Stages Used):** All `8` op-amps across `U1` and `U2` are put to work, eliminating a separate `TL072` BOM line item and leaving zero unused stages to terminate.
2. **Superior Voltage Headroom (`0 V` Positive CM Range & `~115 mV` Output Swing):** Classic `TL07x` outputs stall `~1.5 V` short of the rails (`~+10.0 V` max on `+11.55 V`). By contrast, TI's modern `TL074H` common-mode range reaches all the way up to **`VCC+`** (`0 V` headroom—vital for `U2C`, `U2D`, and `U2B` running from `0 V` to `+10.5 V`), and its output swings within **`~115 mV` of `VCC+`** and **`~105 mV` of `VCC-`** (`~±11.4 V` on our protected rails).
3. **Low Input Offset (`1 mV` typ) & No Phase Reversal:** Crucial because removing `D3`'s `0.65 V` deadzone exposes `U1A`'s DC offset (`11.1×` noise gain at max `GAIN`), and `TL074H` won't latch/invert if severely overdriven.
4. **Speed (`20 V/µs` slew, `5.25 MHz` GBW, `1 pA` input bias):** Recovers `U2C` from `-11.4 V` in ~`1.1 µs` and keeps `C2` leakage negligible during `1 s` releases.

### Capacitor Dielectrics at a Glance
| RefDes | Value | Dielectric | Why This Type? |
|---|---|---|---|
| `C9`–`C13` | `15 pF`, `47 pF`, `100 pF` | **`NP0` (`C0G`)** Ceramic (`0603`) | Zero voltage drift, zero microphonics, tight `±5%` tolerance—ideal for op-amp feedback stability. |
| `C5`–`C8` | `100 nF 50 V` | **`X7R`** Ceramic (`0603`) | Compact, low-inductance high-frequency supply bypassing right at IC pins. |
| `C1` | `10 µF 50 V` | **`X7R`** Ceramic (`1206`) | High capacitance in SMD (`10 µF` rated `50 V` ensures `≥ 4.7 µF` effective even under `12 V` DC bias). |
| `C3`, `C4` | `22 µF 35 V` | **Aluminum Electrolytic** (`5×5.4 mm`) | High bulk capacitance per dollar for power-rail ripple smoothing (`35 V` rated for `12 V` rails). |
| `C2` | `1 µF 63 V` | **Metallized Polyester Film** (`WIMA MKS2`, THT) | Immune to DC-bias capacitance collapse, microphonics, and leakage during `1 s` envelope releases. |

### Assembly Split (`49` SMD + `10` Manual THT)
* **JLCPCB Economic SMT (`49` components / `19` BOM lines):** Both `TL074HIDR` ICs, all diodes (`D1`–`D3`, `D5`–`D11`), all resistors (`R1`–`R8B`, `R10`–`R19`, `R24`–`R26`, `R28`–`R30`), and caps `C1`, `C3`–`C13`. *(All `49` SMD components and optional `DNP` `RH-5001` test points are live-verified in [`EnvelopeFollowerBOM.md`](./EnvelopeFollowerBOM.md).)*
* **Manual Through-Hole (`10` parts):**
  * **Front (`F.Cu`) at `10.5 mm` panel standoff:** `J1`–`J3` (`WQP-PJ398SM` jacks), `RV1`–`RV4` (`9 mm` pots: `A100k`, `A50k`, `A1M`, `B10k`), and `D4` (`3 mm` LED).
  * **Rear (`B.Cu`):** `J_PWR` (`2×5` shrouded IDC header, pin 1 red stripe = `-12Vin`) and `C2` (`1 µF` WIMA `MKS2` film cap, `10.0 mm` tall—mounted on the rear to clear the `10.5 mm` front panel).

---

## 5. Quick Reference: Controls, Signal Benchmarks & Build Checks

### Panel Controls & Jacks
| Control / Jack | RefDes | Spec / Range | Function & Musical Feel |
|---|---|---|---|
| **`IN`** | `J1` | `3.5 mm` mono (`TN → GND`), `10 kΩ` Z | Audio/CV input (quiet when unpatched; blocks external DC). |
| **`GAIN`** | `RV1` | `A100k` (Audio/Log), `-0.10x` to `-10.10x` | Input scaling from `-20 dB` attenuation up to `+20 dB` boost. |
| **`ATK`** | `RV2` | `A50k` (Audio/Log), `0.47–50.5 ms` | Rising response time (`R28 = 470 Ω` prevents `0 Ω` shorting). |
| **`Release`** | `RV3` | `A1M` (Audio/Log), `47 ms–1.05 s` | Falling decay time (`R10 = 47 kΩ` minimizes divider sag). |
| **`OFFSET`** | `RV4` | `B10k` (Linear, center detent), `±5.15 V` | Shifts `OUT` positively CW (`-5.15 V` to `+5.15 V`) with `0%` gain shift. |
| **`LED`** | `D4` | `3 mm` THT (`0–4.53 mA` linear) | Tracks raw pre-offset envelope (`0.00 mA` below `+25 mV` silence). |
| **`OUT`** | `J2` | `3.5 mm` mono (`TN` open), `1 kΩ` out Z | Positive envelope + offset (`+1.00 × ENV_RAW + OFFSET`). |
| **`INV_OUT`** | `J3` | `3.5 mm` mono (`TN` open), `1 kΩ` out Z | Inverted envelope + inverted offset (`-1.00 × ENV_RAW - OFFSET`). |

### Bench Verification Benchmarks (`1 kHz` `±5 V` Sine Input, `GAIN ≈ 1.0x`, `OFFSET` Centered)
1. **Rails:** `+12V_PROT ≈ +11.55 V`, `-12V_PROT ≈ -11.60 V`.
2. **Silence (`J1` unpatched):** `ENV_RAW` near `0 V` (`< 25 mV`), `D4` completely dark (`0.00 mA`), `OUT` and `INV_OUT` near `0 V`.
3. **Active Signal (`±5 V` sine scaled to `±5 V` at `PREAMP_OUT`):**
   * `HALF_WAVE`: `0 V` and `-2.5 V` half-waves.
   * `RECT_OUT`: `0 V` to `+5.0 V` full-wave pulses (`100%` symmetry).
   * `ENV_RAW` / `ENV_RAW_BUF`: steady `~+5.0 V` DC (with slight ripple depending on `Release`).
   * `OUT`: `~+5.0 V`; `INV_OUT`: `~-5.0 V`; `D4` glows smoothly (`~2.26 mA` with `2.2 kΩ` `R29`).
4. **Full CW `OFFSET`:** `OUT` rises by `+5.15 V` (`~+10.15 V`); `INV_OUT` drops to `~-10.15 V` (and clips cleanly around `±11.4 V` if combined with a `+10 V` envelope).
