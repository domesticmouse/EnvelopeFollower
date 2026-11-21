# Envelope Follower — Circuit Review & Suggested Improvements

Review of the circuit documented in [EnvelopeFollower.md](./EnvelopeFollower.md) (derived from [EnvelopeFollower.webp](./EnvelopeFollower.webp)).

All reference designators (`U1A`–`U1D`, `U2A`–`U2B`, `R1`–`R23`, `C1`–`C4`, `D1`–`D4`, `RV1`–`RV4`, `J1`–`J4`) and net names (`IN_TIP`, `IN_AC`, `IN_SUM`, `V_GAIN`, `RECT_MID`, `V_RECT`, `ENV_CAP`, `ENV_RAW`, `V_OUT_BUF`, `LED_BIAS`, etc.) follow [EnvelopeFollower.md](./EnvelopeFollower.md).

---

## Executive Summary & Prioritized Improvements

The original circuit in [EnvelopeFollower.md](./EnvelopeFollower.md) is fundamentally sound—a classic AC-coupled inverting input stage, 2-op-amp precision full-wave rectifier, passive attack/release envelope detector, DC-offsetting output buffer with `-1×` inverse output, and negatively biased LED buffer. However, detailed analysis reveals several electrical interactions, headroom bottlenecks, pot-taper/usability issues, and hardware reliability gaps.

| Priority | Area / Components | Issue Found | Recommended Fix |
|---|---|---|---|
| **High** | **Output Stage (`U1D`, `RV4`, `R11`–`R15`)** | Excessive `2.25×`–`2.52×` gain clips `OUT`/`INV_OUT` above `ENV_RAW ≈ 4.6 V`; `RV4` (`100 kΩ`) modulates gain by `+12%` and produces severe S-curve offset crowding (`72%` of sweep in outer `25%` of travel); CW rotation shifts `OUT` negative. | Reduce `U1D` gain toward `1×` (matching `0–10 V` detector range); scale `RV4` to `10 kΩ` feeding `100 kΩ` summing resistors (or buffer `RV4`) to eliminate gain coupling and nonlinearity; reverse `RV4` wiring polarity. |
| **High** | **Peak Detector (`D3`, `U1C`, `C2`)** | Peak diode `D3` (`1N4148`) sits outside `U1C`'s feedback loop, creating a `~0.6 V` deadband, temperature drift (`~-2 mV/°C`), and current-dependent peak error. | Place `D3` inside an active precision peak-detector op-amp loop (with anti-saturation clamp diode) or use matched-diode `V_f` compensation. |
| **High** | **Envelope Detector (`R9`, `RV2`, `R10`, `RV3`, `C2`)** | Tapping `ENV_RAW` after `R9` (`1 kΩ`) drops amplitude by `9.1%` at fast `Release`; `ATK` (`50 kΩ`) + `R9+R10` (`11 kΩ`) creates up to `82%` divider loss; linear `1 MΩ` `Release` pot cramps `11–100 ms` into `0–9%` rotation; `0 Ω` `ATK` slams `U1C` into `1 µF`. | Tap `U1D +` and `LED` directly at `C2` (`ENV_CAP`); add `100 Ω`–`220 Ω` series protection on `RV2`; switch `RV3` to an `A1M` audio/log taper (+ parallel safety resistor); specify film (`MKS`/`MKP`) rather than X7R ceramic for `C2`; optionally decouple Attack and Release actively. |
| **High** | **LED Driver (`R20`–`R23`, `U2B`, `D4`)** | Effective `29.67 kΩ` impedance limits LED current to `~0.17 mA` at `+5 V` (`~0.34 mA` at `+10 V`); `-2.79 V` cathode bias causes `~32 µA` idle glow on red/amber/yellow LEDs (`V_f ≈ 1.8–2.1 V`). | Use either re-scaled bias resistors (`R21 = 1 kΩ`, `R22 = 2.2 kΩ`, `R23 = 15 kΩ` → `~3 mA` max, `0 mA` idle for all colors) or an op-amp constant-current sink driver (`0–5 mA` linear, `V_f`-independent). |
| **Medium** | **Input Stage (`J1`, `C1`, `R1`, `R2`, `RV1`, `U1A`)** | Low `~9.9 kΩ` input impedance loads passive attenuators/pickups; linear `RV1` feedback rheostat gives poor gain taper, `0×` dead-zone / `0 Ω` feedback short (no gain floor), open-wiper rail-slam risk, and stray capacitance; floating `J1` tip invites hum. | Ground `J1` normalled switch pin (`TN`); add `R_floor` + `1 MΩ` open-wiper resistor + `22 pF` compensation cap—or better, use `47 kΩ + A50k` log input attenuator with `R_floor = 2.2 kΩ` (`Z_in ≈ 97 kΩ`, `C1 = 1 µF ≥ 50 V` film) into fixed `+21×` `U1A` (`0.47×–10.8×` gain, `BAT54S` input clamp). |
| **High** | **Power & Decoupling (`J4`, `C3`–`C8`, `D_rev+`, `D_rev-`)** | No reverse-polarity protection on `J4` (cables plugged backward destroy `U1`/`U2`); no local `100 nF` IC decoupling drawn; small `4.7 µF` bulk caps. | Use shrouded keyed `2×5` Eurorack header (`J4`) + series `1N5819` reverse-polarity Schottky diodes upstream of `22–47 µF` (`35 V`) bulk caps `C3`/`C4`; place `100 nF` (`50 V` X7R) local decoupling caps `C5`–`C8` directly at `U1`/`U2` supply pins. |
| **High** | **Output & Jack Protection (`J1`–`J3`, `R16`, `R19`, `BAT54S`)** | Cross-patching `OUT`/`INV_OUT` (`-10.5 V`) into `+12 V` dissipates `~0.51 W` in `1 kΩ` `R16`/`R19` (exceeding `0603`/`1/4 W` ratings); no ESD/overvoltage clamps on jacks; risk of miswiring output jack `TN` pins to `GND`. | Upgrade `R16`/`R19` (`1 kΩ`) to `0.5 W` (or `2 × 470 Ω` `1/4 W` series); add `BAT54S` rail clamps on circuit side of `R16`/`R19` and at `U1A +`; ground `J1.TN` only and leave `J2.TN`/`J3.TN` `NC`. |
| **Medium** | **Unused Op-Amp Termination (`TL074` spares)** | Unaddressed in baseline review; leaving spare op-amps floating (e.g., if consolidating Path A onto `2 × TL074`) causes oscillation, rail saturation, and crosstalk. | Terminate every unused op-amp unit as a `GND`-referenced unity-gain voltage follower (`+` input tied to `GND`, `-` input tied to `OUT`; never leave floating or tie both inputs to `GND`). |
| **Low** | **Precision Rectifier (`U1B`, `U1C`, `R3`–`R8`)** | `R8 = 22 kΩ` (`+1.1×`) clips `U1C` slightly before `U1A` (`~9.5 V`); `U1B` sinks `2 mA` through `D2`, clipping positive `V_GAIN` peaks slightly earlier than negative peaks. | Change `R8` to `20 kΩ` (`10 kΩ + 10 kΩ`, matching `R5 + R6` BOM) for exact `1.00×` gain; optionally scale `R3`–`R8` to `22 kΩ` / `44 kΩ` to halve `U1B` sink current and improve peak symmetry. |

---

## 1. Detailed Stage-by-Stage Improvements

### 1.1 Output Stage: Excessive Gain, Gain–Offset Coupling & Nonlinear Pot Taper (`U1D`, `RV4`, `R11`–`R15`)

#### Issues Observed
1. **Premature Rail Clipping (`2.25×`–`2.52×` Output Gain):**
   `U1A` and `U1C` (`TL074` on `±12 V`) operate up to `~±10.5 V`. After `D3` (`~0.6 V`), `ENV_CAP` / `ENV_RAW` can already swing cleanly from `0 V` to `~+9.9 V` (and the `LED` buffer `U2B` tracks all the way to `+9.9 V`). However, `U1D` amplifies `ENV_RAW` by `2.25×` at `OFFSET` center (and `2.52×` at the extremes):
   - Any `ENV_RAW` above **`~4.6 V`** drives `V_OUT_BUF` past `+10.5 V` (`4.6 V × 2.25 = 10.35 V`), hard-clipping both `OUT` (`J2`) and `INV_OUT` (`J3`).
   - Meanwhile, the indicator `LED` (`U2B`) keeps getting brighter between `4.6 V` and `9.9 V`, misleading the user into thinking the output is still tracking dynamics when `OUT` and `INV_OUT` are actually flat-topped at the rail.
2. **Offset Control Modulates Envelope Gain (`+12%` Shift):**
   Because `RV4` (`100 kΩ`) sits between `R11` (`10 kΩ` to `+12V`) and `R12` (`10 kΩ` to `-12V`), its Thevenin source resistance `R_pot,th` varies by more than `3×`: from **`30.0 kΩ`** at center (`50%`) down to **`9.17 kΩ`** at both extremes (`0%` and `100%`). Feeding this directly into `R13` (`10 kΩ`) makes `R_off = 10 kΩ + R_pot,th` vary from `40.0 kΩ` to `19.17 kΩ`, changing the non-inverting gain on `U1D` (`2 + 10k / R_off`) from **`2.25×` (center) to `2.52×` (extremes)**. Adjusting `OFFSET` unintentionally scales the envelope amplitude by `~12%`.
3. **Severe S-Curve Offset Nonlinearity (`72%` of Travel in Outer `25%`):**
   Using the exact equation in [EnvelopeFollower.md](./EnvelopeFollower.md) Section 4.5, at `75%` pot rotation (`V_th = +5 V`), `R_top = 35 kΩ` and `R_bot = 85 kΩ`, giving `R_pot,th = 24.79 kΩ` and `R_off = 34.79 kΩ`. Thus:
   - From `50%` to `75%` rotation, `OUT` shifts by only `-5 V × (10k / 34.79k) = -1.44 V` (**`27.6%`** of the `-5.22 V` swing).
   - Over the last `25%` (`75%` to `100%`), `OUT` jumps by **`-3.78 V` (`72.4%`** of the swing).
   This makes zeroing or fine-tuning small DC offsets near the ends of the knob awkward and nonlinear.
4. **Inverted `OFFSET` Rotation Polarity:**
   Because `RV4` drives `U1D`'s inverting input (`-`), a standard wiring with `+12V` at the CW end shifts `OUT` **negative** as you turn clockwise.

#### Recommended Improvements
- **Option A — Zero-Extra-Op-Amp Resistor Scaling (keeps 6 op-amps total):**
  1. Remove `R14` (which forced `U1D` gain `≥ 2×`), increase `R13` to **`100 kΩ`**, and set `R15` to **`47 kΩ`** (or **`33 kΩ`**) so `U1D` gain drops from `2.25×` to **`1.46×`** (or **`1.33×`**), extending unclipped `ENV_CAP` headroom from `4.6 V` up to **`7.2 V`–`7.9 V`** without loading `C2` (`ENV_CAP` still sees only `U1D +`).
  2. Replace `RV4` (`100 kΩ`) with a **`10 kΩ`** linear pot (`R_pot,th ≤ 3.0 kΩ`) and `R11 = R12 = 1 kΩ` (`V_th = ±10 V`, `R_pot,th = 0.92–3.00 kΩ`). With `R13 = 100 kΩ` and `R15 = 47 kΩ`:
     - Output gain varies only from **`1.456×` to `1.466×`** (**`0.66%`** variation vs `12%`).
     - Offset sweeps smoothly over **`±4.66 V`** with **`< 2%`** linearity error (vs `72%` crowding).
  3. Wire `RV4` Pin `1` (`CCW`) to `R11` (`+12V`) and Pin `3` (`CW`) to `R12` (`-12V`)—and optionally use a **center-detent** pot—so turning `OFFSET` clockwise shifts `OUT` positive (`INV_OUT` negative).
- **Option B — Buffered `1×` Difference Amplifier (ideal, used in `2 × TL074` revision in Section 2):**
  Once `C2` (`ENV_CAP`) is buffered by a unity-gain op-amp, `U1D` can be wired as a **unity-gain (`~0.97–1.00×`) difference amplifier** (`100 kΩ` resistors on `+` and feedback inputs, `RV4 = 10 kΩ` with `R11 = R12 = 6.8 kΩ` giving `±5.08 V` unloaded / `±4.85 V` loaded offset, or a buffered `RV4`):
  $$V_{\text{OUT\_BUF}} = V_{\text{ENV}} - V_{\text{OFFSET}}$$
  This maps the full `0–10 V` envelope range onto `0–10 V` at `OUT` with **zero clipping below `10 V`**, **zero gain-offset interaction**, and linear offset control.

---

### 1.2 Peak-Charging Diode `D3` Outside Op-Amp Feedback (`U1C`, `D3`)

#### Issues Observed
In Stage 3, `D3` (`1N4148`) sits **outside** `U1C`'s feedback loop (`U1C OUT → D3 → RV2`). Consequently:
1. **Deadband Threshold (`~0.6 V`):** Rectified peaks below `~0.6 V` (`|V_GAIN| < 0.55 V`) cannot forward-bias `D3`, producing `0 V` envelope output and truncating quiet musical tails.
2. **Amplitude- & Rate-Dependent Error:** Because `V_f` of a `1N4148` varies logarithmically with current (`~0.45 V` at `10 µA` trickle vs `~0.75 V` at `10 mA` fast attack) and drifts at `~-2 mV/°C`, peak accuracy shifts with `ATK` setting and temperature. With `U1D`'s `2.25×` gain, a `0.6 V` diode drop translates into a `~1.35 V` error at `OUT`.

*(Note: You cannot simply move `R8` across `D3` inside `U1C`'s feedback loop, because when `V_RECT` drops, `C2` would discharge through `RV2` and `R8` into `U1C`'s `0 V` virtual ground, destroying `Release` time.)*

#### Recommended Improvements
- **Option A — Active Precision Peak Detector (used in `2 × TL074` revision):**
  Insert a dedicated op-amp (`U_peak`) after `U1C`:
  - `V_RECT` → `U_peak +`.
  - `U_peak OUT` → `D3` (`A → K`) → `RV2` (`ATK`) → `C2` (`ENV_CAP`).
  - `C2` (`ENV_CAP`) → unity-gain JFET buffer (`U_buf`) → `10 kΩ` → `U_peak -`.
  - Add an anti-saturation clamp diode `D_clamp` (`1N4148`, `A` at `U_peak -`, `K` at `U_peak OUT`) so when `V_RECT < V(C2)`, `U_peak OUT` clamps at `V_RECT - 0.6 V` rather than slamming to `-10.5 V`.
  - **Result:** `0 mV` diode deadband—signals down to a few millivolts track cleanly.
  - **Tradeoff to note:** When `RV2 > 0`, `U_peak` drives `RV2` at full rail (`~+10.5 V`) until `V(C2) = V_RECT`, making attack a **constant-target slew** (faster for low-amplitude signals) rather than a true exponential RC curve toward `V_RECT`. Alternatively, keep a fast `0 Ω` peak-hold stage (`C_hold` + `Release`) followed by `U_buf` and a post-buffer `RV2` (`ATK`) low-pass RC filter (zero amplitude loss and zero diode deadband, with the natural constraint `τ_rel,eff ≥ τ_atk`).
- **Option B — Matched-Diode `V_f` Pre-Bias (if keeping passive RC exponential attack):**
  Place a matched `1N4148` in the feedback path of a pre-bias unity buffer before `D3` (with a small `~0.2–0.5 mA` pull-down bias resistor from its `-` input to `-12 V`) so its output rides at `V_RECT + V_f`, canceling `D3`'s `~0.6 V` drop to within `~30–50 mV` while preserving pure passive exponential `RC` charging.

---

### 1.3 Envelope Detector: `R9` Tap Error, Attack/Release Interaction, Taper & `C2` Dielectric (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)

#### Issues Observed
1. **`R9` (`1 kΩ`) Causes a `9.1%` Amplitude Drop at Fast `Release`:**
   In [EnvelopeFollower.md](./EnvelopeFollower.md), `U1D +` and `R20` (`LED`) tap the `ENV_RAW` node **after** `R9` (`1 kΩ`), while `C2` sits before `R9`. As `RV3` (`Release`) is turned down from `1 MΩ` to `0 Ω`, `R9` (`1 kΩ`) and `R10` (`10 kΩ`) form a voltage divider:
   $$\frac{V_{\text{ENV\_RAW}}}{V_{\text{ENV\_CAP}}} = \frac{10\,\text{k}\Omega + R_{\text{REL}}}{1\,\text{k}\Omega + 10\,\text{k}\Omega + R_{\text{REL}}} \xrightarrow{R_{\text{REL}}=0} \frac{10\,\text{k}\Omega}{11\,\text{k}\Omega} = 0.909\;(-9.1\%)$$
   Turning `Release` down changes the peak output level even when `C2` charges to the exact same voltage.
2. **Severe Attack / Release Amplitude Interaction (`-14.9 dB` Loss):**
   When `ATK` (`RV2`) is set high (`50 kΩ`) and `Release` (`RV3`) is near minimum (`0 Ω`, leaving `R9 + R10 = 11 kΩ`), `RV2` and `R9 + R10` form a voltage divider during charging:
   $$\frac{11\,\text{k}\Omega}{50\,\text{k}\Omega + 11\,\text{k}\Omega} = 0.180\;(-14.9\text{ dB})$$
   Up to **82%** of the envelope peak voltage is lost (further compounded by `R9` to `0.164`).
3. **Zero Minimum Series Resistance on `ATK` (`RV2 = 0 Ω`):**
   At `0%` `ATK`, `D3` connects directly to `C2` (`1 µF`). `U1C` sees a capacitive short on fast transients, driving `U1C` into output current limit (`~25 mA`) and risking ringing.
4. **Linear `1 MΩ` `Release` Potentiometer (`RV3`) Cramps Fast Decays:**
   With `R_min = 11 kΩ` and a linear `1 MΩ` pot (`C2 = 1 µF`):
   - `0%` = `11 ms`, `9%` = `101 ms`, `50%` = `511 ms`, `100%` = `1011 ms`.
   Over **`90%` of the knob travel** spans just `101 ms` to `1.01 s`, squeezing the entire percussive `11 ms–100 ms` range into the bottom `9%` of rotation. Also, if `RV3`'s wiper momentarily loses contact, `C2` has no discharge path to `GND` and holds voltage indefinitely.
5. **`C2` (`1 µF`) Dielectric Choice:**
   [EnvelopeFollower.md](./EnvelopeFollower.md) (Sections 3.4 and 6.1) lists "Film or C0G/X7R ceramic" as suitable for `C2`. **X7R ceramic** `1 µF` MLCCs exhibit severe DC bias derating (often losing `30–70%` capacitance by `+10 V`), piezoelectric microphonics (panel knocks inject false transients directly into `U1D`), and voltage-dependent distortion of the exponential release tail.

#### Recommended Improvements
1. **Tap `U1D +` and `LED` directly at `C2` (`ENV_CAP`),** removing `R9` (`1 kΩ`) from the `Release` series path (adjusting `R10` to `10 kΩ` or `11 kΩ` directly from `C2` to `RV3`). This immediately eliminates the `9.1%` release-dependent amplitude shift.
2. **Add a `100 Ω`–`220 Ω` series safety resistor in series with `RV2` (`ATK`):** Protects `U1C` from capacitive current spikes and ringing while keeping minimum attack `≤ 0.22 ms`.
3. **Use an audio/logarithmic taper (`A1M`) for `RV3` (`Release`),** spreading fast `10–150 ms` releases across the first half of the knob and `150 ms–1 s` tails across the upper half. Add a **`4.7 MΩ` safety resistor** in parallel with `RV3` (effective max `τ_rel ≈ 835 ms`, or use `A2M || 2.2 MΩ` for `~1.05 s`) so an open wiper never latches the envelope high.
4. **Specify a `1 µF` film capacitor (polyester/polypropylene, e.g., WIMA MKS2/MKP2, `≥ 50 V`) for `C2`**—do not use X7R ceramic or standard polarized electrolytics.
5. **Decouple Attack and Release (optional upgrade):**
   Either use a fast peak-hold stage (`C_hold` + `Release`) → unity buffer → `RV2` (`ATK`) + `C_atk` low-pass (zero amplitude loss, `τ_rel,eff ≥ τ_atk`), or a classic 2-op-amp diode-steering active slew limiter (`D_atk`/`D_rel` separating charge and discharge currents completely).

---

### 1.4 LED Indicator: Dim Output, Idle Glow on Red/Yellow LEDs & Bias Loss (`R20`–`R23`, `U2B`, `D4`)

#### Issues Observed
1. **Very Low LED Current (`~0.17 mA` at `+5 V`, `~0.34 mA` at `+10 V`):**
   From [EnvelopeFollower.md](./EnvelopeFollower.md) Section 4.6, `V_bias = -2.79 V` (`R22 = 10 kΩ`, `R23 = 33 kΩ`) has a Thevenin source resistance `R_th = 7.67 kΩ`, giving `29.67 kΩ` total series resistance with `R21 = 22 kΩ`. For a `2.8 V` green/blue LED, `I_LED` is only **`0.17 mA` at `+5 V`** and **`0.34 mA` at `+10 V`**—far dimmer than standard `2–5 mA` studio panel indicators unless narrow-angle ultra-bright LEDs are fitted.
2. **Idle Glow on Red, Amber, Orange, and Yellow LEDs:**
   Because the cathode rests at `-2.79 V` while `U2B OUT` rests at `0 V`, `2.79 V` appears across `D4` at idle. Any red/orange/yellow LED (`V_f ≈ 1.8–2.1 V`) conducts **`~30 µA`** continuously at `0 V` and never turns completely dark (worsening to hundreds of microamps if `R21` is simply lowered to increase brightness).
3. **Continuous Negative-Rail Drain:**
   `R22 + R23` (`43 kΩ`) draws `0.28 mA` from `-12V` continuously, and `R20` (`10 kΩ`) on `U2B +` provides no practical benefit for an internal node.

#### Recommended Improvements
- **Option A — Re-Scaled Passive Bias (zero extra components, zero load on `C2`):**
  Change `R21 = 1 kΩ`, `R22 = 2.2 kΩ` (to `GND`), and `R23 = 15 kΩ` (to `-12V`), removing `R20` (`0 Ω` jumper):
  - `V_bias = -12 V × (2.2k / 17.2k) = -1.53 V` (`< 1.8 V`, so **completely OFF `0 mA` at `0 V` for red, yellow, green, blue, and white LEDs**).
  - Total effective impedance drops from `29.67 kΩ` to `R21 + (2.2k || 15k) = 2.92 kΩ`, increasing LED current nearly `10×` to **`~1.3–1.6 mA` at `+5 V`** and **`~3.0–3.3 mA` at `+10 V`**.
- **Option B — Precision Op-Amp Constant-Current Sink Driver (ideal when fed from buffered `C2` in `2 × TL074` revision):**
  *(Important: do not place a resistive divider directly on unbuffered `C2` (`ENV_CAP`), as it would discharge `C2` and shorten `Release`!)*
  Drive `U2B +` (or `U2D +`) from the buffered envelope via a `10 kΩ / 10 kΩ` divider (`0 V` to `+5 V` for `0–10 V` envelope), place `D4` (`LED`) from op-amp output (`A`) to `-` input (`K`), add a `1 kΩ` sense resistor from `-` input (`D4.K`) to `GND`, and place an antiparallel `1N4148` clamp across `D4` (`A` to `-`, `K` to output):
  - $$I_{\text{LED}} = \frac{0.5 \cdot V_{\text{ENV}}}{1\,\text{k}\Omega} = 0.5\,\text{mA/V} \cdot V_{\text{ENV}} \quad (0\text{ mA at }0\text{ V},\; 5.0\text{ mA at }+10\text{ V})$$
  - Exact **`0 mA` off state** at `0 V`, turns on at `< 20 mV`, linear brightness **completely independent of LED color or `V_f`**, and eliminates `R22`/`R23` `-12V` static drain.

---

### 1.5 Input Stage: Impedance, `GAIN` Taper/Stability, Gain Floor Limiting & Jack Normalization (`J1`, `C1`, `R1`, `R2`, `RV1`, `U1A`)

#### Issues Observed
1. **Low Input Impedance (`~9.9 kΩ` vs `100 kΩ` Eurorack Standard):**
   `R2` (`10 kΩ`) terminates into `U1A`'s virtual ground, giving `Z_in = 1 MΩ || 10 kΩ ≈ 9.90 kΩ`. Standard Eurorack inputs are `100 kΩ` (or `1 MΩ` for instruments). A `~9.9 kΩ` load drops signal level noticeably when patched from passive attenuators (`10k–50k` pots), vintage synths, or guitar pickups.
2. **`GAIN` Potentiometer (`RV1`) Used as Feedback Rheostat:**
   - **Poor control taper:** Linear `0–100 kΩ` gives `|A_v| = R_GAIN / 10 kΩ`. Unity gain (`1×`) occurs at `10%` rotation (`10 kΩ`), while the entire top `50%` of knob travel covers only `+14 dB` to `+20 dB` (`5×` to `10×`). Typical Eurorack signals (`5–10 Vpp`) cluster below `20%` rotation.
   - **Open-wiper failure mode:** If `RV1` wiper momentarily lifts, `U1A` loses feedback (`A_OL > 10⁵`) and slams to `±10.5 V`, creating a loud false envelope spike.
   - **Summing-node capacitance:** Wiring panel pot `RV1` directly to `U1A -` (`IN_SUM`) adds stray capacitance at the inverting node, reducing phase margin at high gain.
3. **Zero Minimum Gain Floor / `0 Ω` Feedback Short:**
   - In the baseline inverting topology, turning `RV1` (`GAIN`) all the way down (`0 Ω`) shorts `U1A` output directly to `U1A -` (`IN_SUM`) through the panel pot wiper and drops gain to **`0×` (`-∞ dB`)**, creating an unresponsive dead zone across the lower end of the knob (compounded by `D3`'s `~0.6 V` threshold).
   - Likewise, in a grounded `47 kΩ + A50k` input attenuator, turning `RV1` fully CCW shorts `U1A +` directly to `GND` (`0×` gain). Unless full mute at `0%` is specifically desired, a Eurorack envelope follower benefits from a deterministic non-zero **minimum gain floor** (while also protecting `TL07x` against common-mode floor phase reversal).
4. **Floating Input Jack & Unprotected Input (`J1`, `C1`):**
   Leaving a switched jack's normalled pin (`TN`) floating allows `C1` (`4.7 µF`) to pick up ambient `50/60 Hz` hum/noise when no cable is inserted, amplified up to `10×` by `U1A`. Additionally, `C1` lacks a specified `≥ 50 V` DC-blocking rating and `U1A` has no ESD/overvoltage rail clamping against external patch faults.

#### Recommended Improvements
- **Minimal Fix (keeps inverting `U1A`):**
  1. Connect `J1`'s normalled switch pin (`TN`) to `GND` so an unplugged jack shorts the input cleanly to ground.
  2. **Gain floor & ceiling limiting:** Insert a **`4.7 kΩ` gain-floor resistor (`R_floor`)** in series with `RV1` (`U1A -` ↔ `R_floor` ↔ `RV1` ↔ `U1A OUT`), setting a minimum gain floor of **`0.47×` (`-6.6 dB`)** and maximum **`10.47×`**—preventing a `0 Ω` feedback short and keeping standard `±5 V`–`±10 V` Eurorack signals active without clipping `U1A` at `±10 V` peaks (use `10 kΩ` if a `1.0×` unity floor is preferred for `±5 V` line/audio signals). Place a **`1 MΩ` safety resistor** (open-wiper gain ceiling) and **`22 pF` compensation capacitor** (HF rolloff) in parallel across `R_floor + RV1`.
  3. Optionally switch `RV1` to an audio/log taper (`A100k`) so low gains occupy more knob travel.
- **Better Fix (`Z_in ≈ 97 kΩ`, Log Taper, Gain Floor Limiting, No Extra Op-Amp):**
  Replace the inverting input stage with an **input attenuator with gain-floor limiting into a fixed `+21×` non-inverting amplifier**:
  - `J1.Tip` → `C1` (`1 µF` film, `≥ 50 V` / `63 V`, giving `f_c ≈ 1.65 Hz`—smaller and cheaper than `4.7 µF`) → `R_in1` (`47 kΩ`) → `RV1` (`A50k` log pot) → **`R_floor` (`2.2 kΩ`)** → `GND` (connected to `RV1` Pin `1` `CCW`).
  - `RV1` wiper → `U1A +`, with a **`1 MΩ` pull-down to `GND`** (open-wiper ceiling safety) and **`BAT54S` rail-clamp diode array** (`Pin 1 A` → `-12V_PROT`, `Pin 2 K` → `+12V_PROT`, `Pin 3 COM` → `U1A +`; `R_in1 = 47 kΩ` limits even `±24 V` transient fault current to `< 0.26 mA`).
  - `U1A` set to fixed non-inverting gain `1 + 200 kΩ / 10 kΩ = +21×` (with `22 pF` across `200 kΩ` for HF gain limiting).
  - **Gain Floor & Headroom Performance:**
    - **Minimum Gain Floor (`0%` CCW):** `R_floor = 2.2 kΩ` sets `|A_v,min| = (2.2k || 1M) / (47k + 50k + 2.2k) × 21 =` **`+0.465×`** (`-6.65 dB`), ensuring even hot `±10 V` (`20 Vpp`) Eurorack signals stay safely below `U1A` clipping (`±4.65 V`) while eliminating the silent dead zone at minimum `GAIN`. *(For a `~1.0×` unity floor, use `R_floor = 4.7 kΩ` → `+0.97×` to `+11.0×`, or `4.7 kΩ` with `180 kΩ / 10 kΩ` = `+19×` for `+0.87×` to `+9.97×`; only omit `R_floor` if full `0×` mute at CCW is explicitly desired.)*
    - **Maximum Gain (`100%` CW):** **`+10.78×`** (`+20.65 dB`) with nearly constant `Z_in ≈ 96.6 kΩ`.
    - **Common-Mode Floor Safety for `TL074`:** At `±12 V` peak input and full CW gain, `U1A +` reaches at most `±6.16 V`—safely above `TL07x`'s `-8 V` negative common-mode floor so **`TL074` cannot undergo phase reversal** (the rectifier takes `|V_GAIN|`, so removing `U1A`'s sign inversion does not alter circuit polarity).
- **Optional Enhancement:** Add an `AC / DC` bypass switch across `C1` if sub-3 Hz CV tracking is desired.

---

### 1.6 Precision Full-Wave Rectifier: Gain Scaling & Saturation Symmetry (`U1B`, `U1C`, `R3`–`R8`)

#### Issues Observed
1. **Unnecessary `+1.1×` Gain (`R8 = 22 kΩ`):**
   `V_RECT = +1.1 · |V_GAIN|` causes `U1C` to clip against `+10.5 V` when `|V_GAIN|` reaches `~9.55 V`, slightly before `U1A` clips, and introduces a non-integer `1.1×` factor while adding `22 kΩ` to the BOM.
2. **Asymmetric Load Current on `U1B`:**
   When `V_GAIN > 0`, `U1B OUT` sits at `-V_GAIN - V_f(D2)` (`~-10.65 V` at `V_GAIN = +10 V`) while sinking `I(R4) + I(R7) = V_GAIN / 5 kΩ` (`2.0 mA`). Because `TL07x` output swing droops under heavier load, positive `V_GAIN` peaks clip ~`0.5–1 V` earlier than negative `V_GAIN` peaks (`U1B` stays at `+0.6 V` during `V_GAIN < 0`).

#### Recommended Improvements
1. Change `R8` from `22 kΩ` to **`20 kΩ`** (or two **`10 kΩ` `1%` resistors in series**, matching `R5 + R6` and reusing the existing `10 kΩ` BOM line!) for exact **`1.00×`** rectifier gain and symmetric headroom.
2. Optionally scale `R3, R4, R6–R8` up from `10 kΩ / 20 kΩ` to **`22 kΩ / 44 kΩ`** (e.g., `22 kΩ` for `R3`, `R4`, `R5`, `R6`, `R7`, and `R8` as `22 kΩ + 22 kΩ`), halving `U1B` peak sink current to `~0.9 mA` for cleaner saturation symmetry while preserving `1%` matching.

---

### 1.7 Eurorack Circuit Protections: Power Supply, IC Decoupling, Output Protection & Unused Op-Amp Termination (`J1`–`J4`, `C3`–`C8`, `D_rev+`, `D_rev-`, `BAT54S`, `R16`, `R19`, `U1`, `U2`)

While [EnvelopeFollower.md](./EnvelopeFollower.md) (Sections 3.1 and 6.1) mentions local `100 nF` decoupling, reverse-polarity protection, and terminating unused units in Option C as high-level Build Notes, a production-ready Eurorack module requires concrete component-level protections across power entry, IC supply rails, external I/O jacks, and spare op-amp units.

#### 1.7.1 Power Supply Reverse-Polarity Protection & Bulk Filtering (`J4`, `D_rev+`, `D_rev-`, `C3`, `C4`)
- **Issues Observed:**
  - The baseline schematic shows bare `+12V in`, `GND`, and `-12V in` ports with no reverse-polarity protection—inserting an unkeyed ribbon cable backward destroys `U1`, `U2`, and reverse-biases `C3`/`C4` immediately.
  - `4.7 µF` bulk capacitors (`C3`, `C4`) are light for noisy Eurorack bus boards shared with digital modules.
- **Recommended Implementation:**
  1. **Shrouded Keyed Eurorack Header (`J4`):** Use a **shrouded, keyed `2×5` (10-pin) IDC header** following the Doepfer A-100 pinout: Pins `1–2` = `-12V` (red stripe), Pins `3–8` = `GND` (all 6 pins tied solidly to the PCB ground plane), Pins `9–10` = `+12V`.
  2. **Series Schottky Reverse-Polarity Diodes (`D_rev+`, `D_rev-`):** Place **`1N5819`** (THT, or `SS14` / `B5819W` SMD) series diodes upstream of `C3` and `C4`:
     - **`+12V` rail (`D_rev+`):** Anode (`A`) to `J4` pins `9–10` (`+12V in`); Cathode (`K`) to protected `+12V_PROT` rail.
     - **`-12V` rail (`D_rev-`):** Cathode (`K`) to `J4` pins `1–2` (`-12V in`); Anode (`A`) to protected `-12V_PROT` rail. *(Observe opposite orientation on the negative rail so normal `-12 V` conducts cleanly while reversed `+12 V` blocks.)*
     - **Voltage Drop & Headroom:** At `~10–15 mA` module draw, `1N5819` drops `~0.25–0.32 V` (`V_rail ≈ ±11.7 V`), leaving `~±10.2–10.5 V` `TL07x` output swing and keeping Path A/B offset (`±4.54 V` / `±4.73 V`) and Path A LED bias (`-1.50 V`) within spec, with **zero standby fault dissipation** if plugged in backward indefinitely. *(Optionally add `10 Ω` `1/4 W` / `0805` series resistors or ferrite beads after `D_rev+`/`D_rev-` into `C3`/`C4` to damp hot-plug ringing and switching-PSU ripple; `10 Ω` adds `0.15 V` drop at `15 mA`, leaving `±11.55 V`. Avoid `10 Ω` fusible + `1N4004` shunt clamps unless zero steady-state drop is essential, as reversed cables force `~1.2 A` / `14.4 W` through the `10 Ω` resistor until it opens.)*
  3. **Protected Bulk Capacitors (`C3`, `C4`):** Place **`22 µF` or `47 µF` (`≥ 35 V`, low-ESR aluminum electrolytic)** **downstream** of `D_rev+`/`D_rev-` so they are also reverse-polarity protected (`C3 +` to `+12V_PROT`, `C3 -` to `GND`; `C4 +` to `GND`, `C4 -` to `-12V_PROT`).

#### 1.7.2 Local IC Decoupling Capacitors (`C5`–`C8`)
- **Issue Observed:** No local high-frequency ceramic bypass capacitors are present on the baseline schematic; long bus traces to `U1` and `U2` invite op-amp HF oscillation and supply rail bounce during `C2` peak-charging transients and LED current steps.
- **Recommended Implementation:**
  Place **`100 nF` (`0.1 µF`, `50 V` X7R ceramic**, `0603`/`0805` SMD or radial THT) directly across the supply pins of **every op-amp package** (`< 5 mm` trace length, short return to `GND`):
  - **`U1` (`TL074`, DIP-14 / SOIC-14):** `C5` from Pin `4` (`+12V_PROT`) to `GND`; `C6` from Pin `11` (`-12V_PROT`) to `GND`.
  - **`U2` (`TL072` in Path A, DIP-8 / SOIC-8):** `C7` from Pin `8` (`+12V_PROT`) to `GND`; `C8` from Pin `4` (`-12V_PROT`) to `GND`.
  - **`U2` (`TL074` in Path B or BOM-consolidated Path A):** `C7` from Pin `4` (`+12V_PROT`) to `GND`; `C8` from Pin `11` (`-12V_PROT`) to `GND`.

#### 1.7.3 Output & Input Jack Protection (`J1`–`J3`, `R16`, `R19`, `BAT54S`)
- **Issues Observed:**
  1. **Output Resistor Overload Under Cross-Patching (`R16`, `R19`):** `1 kΩ` series resistors protect `U1D`/`U2A`/`U2C` on short to `GND` (`10.5² / 1000 = 0.11 W`), but patching `OUT` at `-10.5 V` directly into another module's `+10.5 V` or `+12 V` output (`21–22.5 V` difference) dissipates **`0.44–0.51 W`** continuously, scorching `0603`/`0805` SMD or `1/4 W` resistors.
  2. **No ESD / Overvoltage Clamping:** External `8 kV` ESD strikes or hot-patched voltages beyond `±12 V` hit op-amp pins directly.
  3. **Output Jack Switch Miswiring Risk:** Grounding a switched jack's normalled pin (`TN`) is required on `J1` (`IN`), but mistakenly grounding `J2.TN` or `J3.TN` shorts `OUT` / `INV_OUT` to `GND` through `1 kΩ` whenever unplugged.
- **Recommended Implementation:**
  1. **Fault-Rated `1 kΩ` Output Build-Out Resistors (`R16`, `R19`):** Keep `1 kΩ` series output resistance (which also isolates `100–300 pF` Eurorack patch cable capacitance from the op-amp output to prevent oscillation), but specify **`0.5 W` (`1/2 W`) metal-film THT**, **`1206`/`2512` surge-rated SMD**, or **`2 × 470 Ω` (`1/4 W` / `0805`) in series (`940 Ω`)**.
  2. **ESD & Overvoltage Rail Clamps (`BAT54S`, SOT-23):** Use dual series Schottky arrays (`BAT54S`: Pin `1` `A` → `-12V_PROT`, Pin `2` `K` → `+12V_PROT`, Pin `3` `COM` → protected signal node):
     - **On `OUT` (`J2`) and `INV_OUT` (`J3`):** Place `BAT54S` **behind current-limiting resistance**—specifically on the **op-amp side (`V_OUT_BUF` / `V_INV_BUF`)** of `R16`/`R19` (or at the midpoint of a split `820 Ω` op-amp-side + `180 Ω` jack-side network). *Why:* Because `D_rev+` blocks reverse flow back into the Eurorack PSU bus, placing `BAT54S` directly on raw `J2.Tip` without series impedance allows an external `>+15 V` DC fault to burn `BAT54S` and lift `+12V_PROT`. With `1 kΩ` `R16`/`R19` ahead of `BAT54S`, `+15 V` injects only `3 mA` (safely sunk by the module's `~10–15 mA` quiescent current) and `+24 V` injects `12 mA`. *(Optionally add `15 V` Zener / TVS rail clamps across `+12V_PROT`–`GND` and `GND`–`-12V_PROT` if sustaining `>20 V` external faults.)*
     - **On `IN` (`J1`):** Place `BAT54S` (`Pin 3 COM`) at `U1A +` downstream of `C1` (`1 µF ≥ 50 V` film) and `R_in1` (`47 kΩ`); `R_in1` limits even `±24 V` transient faults to `0.25 mA`.
  3. **Jack Switch Normalization:** Ground `J1.TN → GND` (unplugged input quieted to `0 V`), and leave **`J2.TN` and `J3.TN` unconnected (`NC`)**.

#### 1.7.4 Unused Op-Amp Termination (`TL074` Spare Units)
- **When Applicable:** Any build using `2 × TL074` with the 6-op-amp circuit (such as Path A consolidated onto a single IC BOM, baseline Option C in [EnvelopeFollower.md](./EnvelopeFollower.md), or single-output variants omitting `INV_OUT` or `LED`). *(Path B uses all `8` op-amps across `2 × TL074`, leaving `0` unused units.)*
- **Recommended Implementation (Dual `±12 V` Supply):**
  Configure every unused unit as a **unity-gain voltage follower referenced to `GND`** (`0 V` mid-supply, well inside `TL07x`'s `[-8 V, +12 V]` common-mode range):
  - Tie the **non-inverting input (`+`) directly to `GND`**.
  - Tie the **inverting input (`-`) directly to that unit's output (`OUT`)**.
  - **Exact `TL074` Pin Mapping for Path A on `2 × TL074` (`U2C` & `U2D` unused):**
    - **`U2C`:** Pin `10` (`+`) → `GND`; Pin `9` (`-`) ↔ Pin `8` (`OUT`).
    - **`U2D`:** Pin `12` (`+`) → `GND`; Pin `13` (`-`) ↔ Pin `14` (`OUT`).
  - **What to Avoid:** Never leave unused `TL07x` pins floating (parasitic oscillation and rail chatter inject noise through shared supply/substrate), never tie both `+` and `-` directly to `GND` without feedback (input offset `V_OS` saturates the output to `±10.5 V`), and never tie `+` to `-12V` (violates `TL07x` negative common-mode limit and triggers phase reversal).

---

## 2. Two Concrete Implementation Paths

Depending on whether you want to keep the 6-op-amp topology (`1 × TL074 + 1 × TL072`, or `2 × TL074` with 2 terminated spares) or use `2 × TL074` (`8` op-amps, **same 2-IC count**) to unlock full active precision, here are the two recommended upgrade paths:

### Path A: Minimal Revision (6 Active Op-Amps: `1 × TL074 + 1 × TL072`, or `2 × TL074` BOM-Consolidated)
Fixes the biggest usability, gain-clipping, LED, impedance, and Eurorack protection flaws with **zero extra active stages**:
1. **Input & Gain Floor (`U1A`):** Ground `J1.TN`; `C1 = 1 µF` film (`≥ 50 V`) → `47 kΩ` → `RV1` (`A50k` log pot) → **`R_floor = 2.2 kΩ` to `GND`** (`RV1` Pin `1` `CCW`); `RV1` wiper → `U1A +` (`1 MΩ` pull-down to `GND` + `BAT54S` clamp to `±12V_PROT`); `U1A` fixed `+21×` non-inverting (`200 kΩ || 22 pF` fb, `10 kΩ` to `GND`). (`Z_in ≈ 96.6 kΩ`, **`+0.47×` gain floor to `+10.8×` max**, no `TL07x` phase reversal).
2. **Rectifier (`U1B`, `U1C`):** Change `R8` to `20 kΩ` (`10k + 10k` `1%`) for `1.00×` gain.
3. **Envelope (`RV2`, `C2`, `RV3`):** Add `150 Ω` in series with `RV2` (`ATK`); remove `R9` from the `Release` branch and connect `U1D +` and `U2B +` directly to `C2` (`1 µF` film, not X7R); use `A1M` log pot (`|| 4.7 MΩ` safety resistor) for `RV3` (`Release`).
4. **Output & Output Protection (`U1D`, `RV4`, `J2`, `J3`):** Omit `R14`; use `RV4 = 10 kΩ` linear (`R11 = R12 = 1 kΩ`, wired CW=`-12V_PROT` / CCW=`+12V_PROT` so CW = positive `OUT`), `R13 = 100 kΩ`, `R15 = 47 kΩ` (`1.46×` gain, `< 0.7%` gain-offset coupling, `±4.54 V` smooth linear offset at `±11.7 V` rails). Rate `R16`/`R19` (`1 kΩ`) at **`0.5 W`** (or `2 × 470 Ω` `1/4 W` series), add **`BAT54S`** clamps at `V_OUT_BUF` / `V_INV_BUF`, and leave `J2.TN` / `J3.TN` **`NC`**.
5. **LED (`U2B`, `D4`):** Jumper `R20 = 0 Ω`; set `R21 = 1 kΩ`, `R22 = 2.2 kΩ`, `R23 = 15 kΩ` (`-1.50 V` bias, `0 mA` idle for all LED colors, `~3 mA` at `+10 V`).
6. **Power & Local Decoupling (`J4`, `C3`–`C8`):** Shrouded keyed `2×5` IDC header `J4` (`1–2: -12V`, `3–8: GND`, `9–10: +12V`), series `1N5819` reverse-polarity diodes (`D_rev+` `A→K`, `D_rev-` `K→A`), downstream `22–47 µF` (`35 V`) bulk caps `C3`/`C4`, and **`4 × 100 nF` (`50 V` X7R) local decoupling caps `C5`–`C8`** directly at `U1` (`4`/`11`) and `U2` (`8`/`4` for `TL072`, or `4`/`11` for `TL074`).
7. **Unused Op-Amp Termination (if built with `2 × TL074`):** Wire `U2C` (`Pin 10 → GND`, `9 ↔ 8`) and `U2D` (`Pin 12 → GND`, `13 ↔ 14`) as unity-gain followers.

### Path B: Full Precision Revision (`2 × TL074` = 8 Op-Amps, Same 2-IC Count)
Uses all `8` op-amp units (`0` spare units) to eliminate `D3`'s diode deadband and completely isolate `C2`, `OFFSET`, and `LED`, with full Eurorack protections built in:
- `U1A`: High-Z input gain stage (`Z_in ≈ 96.6 kΩ`, `C1 = 1 µF ≥ 50 V` film, `J1.TN → GND`, `47 kΩ` + `A50k` log attenuator + **`R_floor = 2.2 kΩ`** + `1 MΩ` pull-down + `BAT54S` clamp + fixed `+21×` gain → **`+0.47×`–`+10.8×`**).
- `U1B`, `U1C`: `1.00×` precision full-wave rectifier (`R8 = 20 kΩ`).
- `U1D`: **Active precision peak detector** (`D3` inside feedback loop + `1N4148` anti-saturation clamp, `0 V` diode deadband, `150 Ω` min attack resistor).
- `U2A`: **Dedicated unity-gain `C2` buffer** (`ENV_CAP` unloaded by anything except `R10 + RV3`).
- `U2B`: **Near-unity (`~0.97×`) difference/offset stage** (`100 kΩ` summing resistors and `RV4 = 10 kΩ`, `R11 = R12 = 6.8 kΩ` for `±4.73 V` loaded linear offset at `±11.7 V` rails and `< 0.5%` gain shift—or `95.3 kΩ` inverting leg resistor for exact `1.00×` gain; `0–10 V` completely unclipped).
- `U2C`: `-1.00×` inverted output (`INV_OUT`).
- `U2D`: **Precision constant-current LED driver** (`10k/10k` divider on `U2D +` fed from `U2A`, `D4` in feedback with `1 kΩ` sense resistor to `GND` + antiparallel `1N4148` clamp → exact `0 mA` off at `0 V` and linear `0–5 mA` for any LED color).
- **Outputs (`J2`, `J3`):** `R16`, `R19` = `1 kΩ` **`0.5 W`** (or `2 × 470 Ω` `1/4 W` series), **`BAT54S`** ESD/rail clamps on `V_OUT_BUF` (`U2B OUT`) and `V_INV_BUF` (`U2C OUT`), `J2.TN` / `J3.TN` left **`NC`**.
- **Power & Decoupling (`J4`, `C3`–`C8`):** Shrouded `2×5` `J4`, series **`1N5819`** reverse-polarity diodes (`D_rev+`, `D_rev-`), `22–47 µF` (`35 V`) bulk caps `C3`/`C4` downstream, and **`4 × 100 nF` (`50 V` X7R)** decoupling caps `C5`–`C8` right at `U1` (`4`/`11`) and `U2` (`4`/`11`).
- **Unused Op-Amp Note:** All `8` sections are active (`0` unused units); if building a stripped variant (e.g., omitting `INV_OUT` or `LED`), terminate any spare unit(s) as `GND`-referenced unity-gain followers (`+` → `GND`, `-` ↔ `OUT`).

---

## 3. Eurorack Protection Summary Checklist

| Protection Area | Component(s) | Value / Rating | Placement & Connections |
|---|---|---|---|
| **Power Reverse Polarity** | `J4`, `D_rev+`, `D_rev-` | Shrouded `2×5` IDC; `2 × 1N5819` (or `SS14`) | `J4` (`1–2: -12V`, `3–8: GND`, `9–10: +12V`); `D_rev+` (`A` to `J4 +12V`, `K` to `+12V_PROT`); `D_rev-` (`K` to `J4 -12V`, `A` to `-12V_PROT`) |
| **Bulk Rail Filtering** | `C3`, `C4` | `22–47 µF`, `≥ 35 V` low-ESR electrolytic | Downstream of `D_rev+`/`D_rev-` (`C3 +` to `+12V_PROT`, `C4 +` to `GND`, `C4 -` to `-12V_PROT`) |
| **Local IC Decoupling** | `C5`–`C8` | `4 × 100 nF`, `50 V` X7R ceramic | `< 5 mm` from supply pins to `GND`: `U1` (`4`, `11`), `U2` (`8`/`4` for `TL072` or `4`/`11` for `TL074`) |
| **Gain Floor & Input Clamp** | `R_floor`, `R_pd`, `C1`, `D_in` | `2.2 kΩ` (or `4.7 kΩ` inv.); `1 MΩ`; `1 µF ≥ 50 V` film; `BAT54S` | `R_floor` at `RV1` CCW-to-`GND` (`+0.47×` min floor; or series with `RV1` in inv. mode); `D_in` (`1:-12V_PROT`, `2:+12V_PROT`, `3:U1A+`); `J1.TN → GND` |
| **Output Fault & ESD Clamp** | `R16`, `R19`, `D_out1`, `D_out2` | `1 kΩ`, `0.5 W` (or `2 × 470 Ω 1/4 W`); `2 × BAT54S` | `R16`/`R19` in series to `J2.Tip`/`J3.Tip`; `D_out1`/`D_out2` `Pin 3` at op-amp side (`V_OUT_BUF`, `V_INV_BUF`), `1:-12V_PROT`, `2:+12V_PROT`; `J2.TN`/`J3.TN = NC` |
| **Unused Op-Amp Termination** | Spare `TL074` units (if any) | Direct traces (no extra parts) | Unity-gain follower: `+` input → `GND`, `-` input ↔ `OUT` (e.g., `U2C`: `10→GND`, `9↔8`; `U2D`: `12→GND`, `13↔14`) |
