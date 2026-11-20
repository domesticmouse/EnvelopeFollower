# Envelope Follower Circuit Review & Recommended Improvements

Detailed engineering review of [`EnvelopeFollower.md`](./EnvelopeFollower.md) and [`EnvelopeFollower.webp`](./EnvelopeFollower.webp), identifying circuit design flaws, component/stability risks, Eurorack interoperability gaps, and calculation discrepancies in the documentation.

---

## Executive Summary

The original 6-op-amp circuit is functionally sound as a basic DIY sketch, but a stage-by-stage analysis reveals **several significant analog design issues** and **two factual calculation/wiring errors in `EnvelopeFollower.md`**:

1. **Severe output clipping & gain modulation (`U1D`, `RV4`)**: `U1D` amplifies `ENV_NODE` by `2.25×` to `2.52×`, clipping `OUT` at the `+12V` rail once `ENV_NODE` exceeds `~4.2–4.7 V`, while `RV4` (`OFFSET`) shifts envelope gain by `12%` across its rotation and exhibits a strongly S-curved taper.
2. **Unbuffered peak diode (`D3`) & missing attack current limiter (`RV2`)**: `D3` sits outside any op-amp feedback loop (`~0.65 V` dead-zone and thermal drift), and dialing `ATK` (`RV2`) to `0 Ω` shorts `U1C` directly into `C2` (`1 µF`).
3. **Release-dependent amplitude droop (`R9`)**: `R9` (`1 kΩ`) forms a resistive divider with `R10` (`10 kΩ`) + `RV3`, dropping `ENV_NODE` amplitude by `9.1%` (`-0.83 dB`) at minimum `Release`.
4. **Low input impedance (`Z_in ≈ 9.9 kΩ`) & miscalculated $f_c$**: `R2` (`10 kΩ`) terminates at `U1A` virtual ground, pulling $Z_{\text{in}}$ down to `9.9 kΩ` (10× below the `100 kΩ` Eurorack standard) and raising the actual input high-pass cutoff from the documented `0.034 Hz` to **`3.42 Hz`**.
5. **LED idle glow & low peak brightness (`U2B`, `D4`, `R21`–`R23`)**: The `-2.79 V` cathode bias leaves standard red/yellow/green LEDs glowing dimly at idle (`~23–32 µA`) while capping `+10 V` peak current at `~0.33–0.37 mA`.
6. **Missing Eurorack power protection & local IC decoupling**: No reverse-polarity/overcurrent protection on `J4` and no `100 nF` ceramic bypass caps at `U1`/`U2`.
7. **Reversed `OFFSET` pot rotation note**: `EnvelopeFollower.md` (Section 6.3) states `Pin 1 -> OFF_TOP, Pin 3 -> OFF_BOT` pushes `OUT` negative when turned clockwise, whereas it actually pushes `OUT` **positive**.

> **Key Architectural Insight:** Switching the canonical IC BOM from `1 × TL074 + 1 × TL072` (`Option A`) to **`2 × TL074`** (`Option C`, already listed in `EnvelopeFollower.md`) unifies the IC BOM and frees **2 op-amp sections**—enough to add a true `100 kΩ` input buffer and an active precision peak detector (`D3` inside the op-amp loop) with minimal PCB area impact.

---

## 1. Critical Circuit Flaws & Recommended Fixes

### 1.1 Output Stage Excess Gain, Clipping & `OFFSET`-Dependent Gain Modulation (`U1D`, `RV4`, `R11`–`R15`)

**Current Behavior (`EnvelopeFollower.md` §4 Stage 5):**
- `RV4` (`100 kΩ` `OFFSET` pot) sits between `R11` (`10 kΩ` to `+12V`) and `R12` (`10 kΩ` to `-12V`). Depending on wiper fraction $\alpha \in [0, 1]$, its Thévenin source resistance varies by more than 3×:
  - Ends ($\alpha = 0, 1$): $R_{\text{th}} = 10\text{ k}\Omega \parallel 110\text{ k}\Omega = 9.17\text{ k}\Omega$
  - Center ($\alpha = 0.5$): $R_{\text{th}} = 60\text{ k}\Omega \parallel 60\text{ k}\Omega = 30.00\text{ k}\Omega$
- Because `OFF_WIPER` feeds `U1D-` through `R13` (`10 kΩ`) alongside `R14` (`10 kΩ` to `GND`) and `R15` (`10 kΩ` feedback), `U1D` exhibits three coupled problems:
  1. **Premature rail clipping**: `U1D` amplifies `ENV_NODE` by $2.25\times$ (center) to $2.52\times$ (ends). Because `RECT_OUT` reaches `~+10.5 V` and `ENV_NODE` reaches `~+9.8 V`, `U1D` tries to swing to `+22 V` and **clips hard against the `+12V` rail (`~+10.5 V`) once `ENV_NODE` exceeds just `+4.17 V` to `+4.67 V`** (less than half of the detector's dynamic range). Positive `OFFSET` reduces available envelope headroom even further.
  2. **Gain modulation with `OFFSET`**: Adjusting `OFFSET` shifts the envelope signal gain by **`12%`** (`2.25×` at center vs. `2.52×` at the extremes).
  3. **Heavily compressed center taper**: Because $R_{\text{th}}$ triples at mid-travel, the DC shift at `OUT` is non-linear: at $\alpha = 0.25$ / $0.75$ (halfway from center to an end), `OUT` shifts by only **`±1.44 V`** (`27.5%` of its `±5.22 V` full-scale shift).

**Recommended Improvements:**
- **Option A — Zero extra op-amps (keep 6 op-amps, non-inverting `U1D`, linearize `RV4`)**:
  - Keep `U1D` non-inverting (`U1D+` presents `~10¹² Ω` to `ENV_NODE` so `C2` release timing is undisturbed, leaving `U2B` dedicated to the LED driver in §2.2), and make three component changes:
    1. **Remove `R14` (`10 kΩ` to `GND`)**: Eliminates the unnecessary `2×` base gain floor, reducing envelope gain to $1 + \frac{R_{15}}{R_{13} + R_{\text{th}}(\alpha)}$.
    2. **Scale `RV4` down 10× (`RV4 = 10 kΩ`, `R11 = R12 = 1 kΩ`)**: Preserves the exact `±10.00 V` span while cutting wiper source resistance 10× to $R_{\text{th}} \in [0.92\text{ k}\Omega, 3.00\text{ k}\Omega]$.
    3. **Set `R13 = 18 kΩ` (or `22 kΩ`) with `R15 = 10 kΩ`**:
       - With `R13 = 18 kΩ`: `OFFSET` spans **`±5.29 V`** (`±2.44 V` at 25%/75% travel—nearly linear!), and envelope gain drops to **`1.48×` (center) to `1.53×` (ends)** (only **`3.5%`** variation instead of `12%`, raising the `OUT` clip threshold to `ENV_NODE ≈ +6.9 V`).
       - With `R13 = 22 kΩ`: `OFFSET` spans **`±4.36 V`** (`±2.04 V` at 25%/75%), and envelope gain drops to **`1.40×` to `1.44×`** (**`2.6%`** variation, raising clip threshold to `ENV_NODE ≈ +7.3 V`).
- **Option B — Using `2 × TL074` (8 op-amps total: buffered `ENV_NODE` + inverting summer)**:
  - Use a unity-gain voltage follower (`U_ENV_BUF`) to buffer `ENV_NODE` without loading `C2`, then reconfigure `U1D` as an **inverting summing amplifier** driving `INV_OUT` (`R_env = 10 kΩ` from `U_ENV_BUF_OUT`, `R15 = 10 kΩ` feedback, **remove `R14`**, `RV4 = 10 kΩ` + `R11 = R12 = 1 kΩ` via `R13 = 20 kΩ` for `±4.78 V` offset), and invert `U1D_OUT` at `-1.0×` via `U2A` (`R17 = R18 = 10 kΩ`) to produce `OUT`.
  - Because `U1D-` is a virtual ground, envelope gain is locked at **`+1.00×`** (`0` to `~+10 V` full-scale without clipping `U1D` early) with **0.0% gain modulation** across the entire `OFFSET` sweep. (Optionally add a dedicated follower on `RV4` wiper for 100% offset linearity.)

---

### 1.2 Unbuffered Peak Diode `D3` Deadband & Missing Attack Surge Resistor (`U1C`, `D3`, `RV2`, `C2`)

**Current Behavior (`EnvelopeFollower.md` §4 Stage 4):**
- **~0.65 V Dead-Zone**: `D3` (`1N4148`) sits outside `U1C`'s feedback loop. `C2` (`ENV_CAP`) cannot charge until `RECT_OUT` exceeds `D3`'s forward voltage (`~0.55–0.70 V`, drifting `-2 mV/°C`). Quiet audio tails and low-level signals below `~0.5 V` vanish abruptly, and `C2` lags below the true peak voltage (`~0.7–0.85 V` error during fast surges).
- **Op-Amp Output Current Surge at `ATK = 0 Ω`**: When `RV2` (`ATK`, `50 kΩ` rheostat) is dialed fully CCW (`0 Ω`), `U1C` drives `C2` (`1 µF` to `GND`) directly through `D3`. Fast transients slam `U1C` into short-circuit current limiting (`~20–40 mA`), injecting sharp current spikes into the `±12V` rails and `GND` and risking capacitive-load ringing.

**Recommended Improvements:**
- **Always add a minimum attack series resistor (`R_atk_min = 220 Ω` to `470 Ω`)** in series with `RV2` (`ATK`), analogous to `R10` on `Release`. At `220 Ω` with `1 µF`, minimum attack time constant is `0.22 ms` (still perceptually instantaneous for audio transients) while capping peak op-amp charging current and damping ringing.
- **Precision fix (recommended, using 1 spare op-amp in `2 × TL074`)**: Wrap `D3` (`1N4148`) inside a dedicated precision peak-detector op-amp (`U_PK+` = `RECT_OUT`, `U_PK_OUT` → `D3.A`, `D3.K` (`ATK_IN`) → `U_PK-`, then `ATK_IN` → `R_atk_min` + `RV2` → `ENV_CAP`).
  - Why keep `1N4148` inside an op-amp loop rather than substituting a power Schottky diode? A power Schottky (`1N5819`) has up to `1 mA` reverse leakage at `25 °C` (`10 mA` hot), which would discharge `C2` faster than the `1 MΩ` `Release` pot. Even a small-signal Schottky (`BAT85`) has up to `2 µA` reverse leakage at `25 V` (comparable to the `10 µA` discharge current of `10 V / 1 MΩ`), whereas `1N4148` leaks `< 25 nA` and achieves `< 5 mV` dead-zone inside an op-amp loop.
  - *(6-op-amp fallback)*: If strictly limited to 6 op-amps, swapping `D3` to a low-leakage small-signal Schottky (`BAT85` or `1N5711`, $V_f \approx 0.24\text{–}0.32\text{ V}$) halves the dead-zone at the cost of slight temperature-dependent leakage at maximum `1 MΩ` `Release`.

---

### 1.3 `R9` (`1 kΩ`) Causes a `9.1%` `Release`-Dependent Amplitude Droop (`ENV_CAP` / `ENV_NODE`)

**Current Behavior (`EnvelopeFollower.md` §4 Stage 4):**
- `R9` (`1 kΩ`) sits between `C2` (`ENV_CAP`) and `ENV_NODE`, where `R10` (`10 kΩ`) + `RV3` (`1 MΩ`) pull down to `GND`.
- `R9` and `R10 + RV3` form a voltage divider:
  - At `RV3 = 1 MΩ`: $V_{\text{ENV\_NODE}} / V_{\text{ENV\_CAP}} = \frac{1010}{1011} = 0.999$
  - At `RV3 = 0 Ω`: $V_{\text{ENV\_NODE}} / V_{\text{ENV\_CAP}} = \frac{10}{11} = 0.909$ (`-0.83 dB`)
- Turning `Release` down to minimum drops the module's output amplitude by **`9.1%`**, and `R9` provides no meaningful protection because `U1D+` and `U2B+` are internal nodes (not external jacks) and `U2B+` already has `R20` (`10 kΩ`).

**Recommended Improvement:**
- **Remove `R9` (`1 kΩ`)** by connecting `ENV_CAP` directly to `ENV_NODE` (and change `R10` to `11 kΩ` if keeping an `11 ms` minimum release, or keep `10 kΩ` for `10 ms`).
- Add a **`10 kΩ` series protection resistor** directly in front of `U1D+` (matching `R20` on `U2B+`)—or buffer `ENV_NODE` once with a follower—so `C2` cannot dump current into `U1D`'s input pin if `+12V` collapses while `C2` is charged to `+10 V`.

---

### 1.4 Low Input Impedance (`Z_in ≈ 9.9 kΩ`) & Mandatory Grounding of `J1` Normal Switch (`J1`, `C1`, `R1`, `R2`, `U1A`)

**Current Behavior (`EnvelopeFollower.md` §4 Stage 1 & §6.5):**
- `U1A` is an inverting amplifier with its `+` pin grounded, so `U1A_INV` is a virtual ground. Thus, above a few hertz, `J1` sees $Z_{\text{in}} = R_1 \parallel R_2 = 1\text{ M}\Omega \parallel 10\text{ k}\Omega = 9.90\text{ k}\Omega$.
- Standard Eurorack inputs are **`100 kΩ`** (and instrument/piezo inputs are `≥ 470 kΩ–1 MΩ`). A `9.9 kΩ` input loads a typical `1 kΩ` Eurorack output down by `9.2%` (`-0.84 dB`) and severely attenuates/muffles passive instruments.
- Leaving `J1` Tip-Normal unconnected (listed as optional in §6.5) leaves `C1.1` floating when unpatched, allowing `U1A` (at up to `10×` / `+20 dB` gain) to amplify ambient 50/60 Hz hum and falsely trigger the envelope/LED.

**Recommended Improvements:**
- **Raise `Z_in` to `100 kΩ` (or higher)**:
  - **Preferred (`2 × TL074`)**: Place a unity-gain non-inverting input buffer (`U_IN`) after `C1`, with `R1 = 100 kΩ` bias to `GND` (keeping `R2 = 10 kΩ` and `RV1 = 100 kΩ` low-noise).
  - **6-op-amp option A**: Place `RV1` (`100 kΩ` audio taper) *ahead* of `U1A` as an input attenuator feeding a fixed `+10×` (`+11×`) non-inverting amplifier (`U1A`). This gives a constant `100 kΩ` input impedance and avoids `1 MΩ` feedback noise/rolloff, though an unprotected `TL074` non-inverting input must be protected against `< -10 V` negative signals to prevent `TL07x` common-mode phase reversal.
  - **6-op-amp option B**: Scale `R2 = 100 kΩ` and `RV1 = 1 MΩ` (with `47 pF` feedback cap; trade-off: higher resistor thermal noise and susceptibility to hum at the panel pot).
- **Make grounding `J1` Tip-Normal mandatory** in the schematic/PCB so unpatched noise is shorted cleanly to `GND`.
- **Add input ESD / overvoltage clamping**: Place dual clamping diodes (`1N4148` or `BAT54S`) from `IN_AC` (or after a `1 kΩ` series protection resistor at `J1`) to `+12V` and `-12V` to clamp hot-plug transients and ESD spikes.

---

### 1.5 Power Entry Protection & Local IC Decoupling (`J4`, `C3`, `C4`, `U1`, `U2`)

**Current Behavior (`EnvelopeFollower.md` §4 Stage 0 & §6.2, §6.5):**
- `J4` connects `+12V` and `-12V` directly to `U1`, `U2`, `C3`, and `C4` with **no reverse-polarity protection, no series current limiting, and no local `100 nF` IC decoupling capacitors**.
- `C3` and `C4` (`4.7 µF`) are modest for Eurorack bulk decoupling and §3.2 lists `16 V` as an acceptable minimum voltage rating.

**Recommended Improvements:**
- **Reverse-polarity & overcurrent protection**:
  - Use a **shrouded, keyed 10-pin (`2×5`) Eurorack IDC header** for `J4` (clearly silkscreened `-12V` stripe).
  - Add either **series Schottky diodes** (`1N5819` / `SS14` in series with `+12V` and `-12V` before `C3`/`C4`—blocks reversed power completely with zero fuse trip, trading ~`0.35 V` headroom), OR **`10 Ω` 1/4 W resistors / 100 mA PTC polyfuses + reverse-biased shunt diodes** (`1N4001` / `1N5819` to `GND`, which clamps reversed rails and preserves full `±12 V` headroom while also providing RC supply filtering with `C3`/`C4`).
- **Mandatory local IC decoupling**: Add **`100 nF` (X7R, `≥ 25 V` / `50 V`) ceramic capacitors** as close as physically possible to every IC's `V+` and `V-` pins to `GND` (2 per IC = 4 caps total) to suppress `TL07x` rail bounce, channel crosstalk, and HF oscillation.
- **Upgrade bulk caps `C3`/`C4`**: Increase from `4.7 µF` to **`10 µF–47 µF` (e.g., `22 µF`) rated `≥ 25 V` (preferably `35 V`)**. Do **not** use `16 V` electrolytics on `±12 V` rails—16 V leaves inadequate derating margin against supply tolerances and Eurorack hot-plug inductive overshoot.

---

## 2. Signal Integrity, Component Selection & Usability Improvements

### 2.1 Precision Rectifier Matching, Headroom & Symmetry (`U1B`, `U1C`, `R3`–`R8`, `D1`, `D2`)

- **High tolerance sensitivity (`2× − 1×` cancellation)**: During positive `PREAMP_OUT`, `U1C` sums $+\frac{V}{R_4+R_5}$ (`1/20 kΩ`) against $-\frac{V}{R_7}\frac{R_6}{R_3}$ (`1/10 kΩ`). Because it subtracts `1/20k` from `1/10k` to leave `1/20k`, **resistor errors are amplified roughly 3×**:
  - With `5%` resistors, worst-case half-cycle gain asymmetry reaches **`44.3%`**.
  - Even with standard `1%` resistors, worst-case half-cycle asymmetry reaches **`8.16%`**, leaking fundamental-frequency ripple (`50/100 Hz`) into the envelope detector.
  - **Fix**: Specify **`0.1%` (or hand-matched `1%`) metal-film resistors** for `R3`–`R7` (dropping worst-case asymmetry to `0.80%`). Replace `R4 + R5` (`10 kΩ + 10 kΩ`) with a single `0.1%` `20 kΩ` resistor if convenient, and change `R8` from `22 kΩ` (`1.1×` gain) to **`20 kΩ`** for exact **`1.0×`** unity gain (preventing `U1C` from hitting `+10.5 V` rail saturation before `U1A`).
- **`U1B` negative swing margin**: At `PREAMP_OUT = +10 V`, `RECT_HW = -10 V`, forcing `U1B_OUT` down to `-10 V - V_f(D2) ≈ -10.65 V` while sinking `2 mA` (`R6 || R7 = 5 kΩ`). On `±12 V` rails, `TL074` clips near `-10 V` to `-10.5 V`, causing asymmetric clipping at extreme peaks. Using small-signal Schottky diodes (`BAT85`) for `D1`/`D2` saves `~0.35 V` of headroom and halves zero-crossing deadband (note: `D1`/`D2` operate inside low-impedance op-amp nodes, so `BAT85`'s `~µA` leakage causes no timing error here, unlike `D3`).

### 2.2 LED Driver Idle Glow & Low Peak Current (`U2B`, `D4`, `R21`–`R23`)

**Current Behavior:**
- `R22` (`10 kΩ` to `GND`) and `R23` (`33 kΩ` to `-12V`) set a `-2.79 V` Thévenin bias (`R_th = 7.67 kΩ`) on `D4` cathode, with `R21 = 22 kΩ` (`29.67 kΩ` total loop impedance):
  - **Red LED ($V_f \approx 1.85\text{ V}$)**: Draws **`31.7 µA` at `0 V` idle** (visibly glowing in dim rooms) and only **`0.369 mA` at `+10 V` peak**.
  - **Yellow/Green LED ($V_f \approx 2.1\text{ V}$)**: Draws **`23.3 µA` at `0 V` idle** and **`0.360 mA` at `+10 V`**.
  - **Blue/White LED ($V_f \approx 3.0\text{ V}$)**: Stays off at idle, peaking at **`0.330 mA`**.

**Recommended Improvement (In-Loop Precision LED Current Sink):**
- Delete `R22` (`10 kΩ`) and `R23` (`33 kΩ`), and place LED `D4` **inside `U2B`'s feedback loop**:
  - `U2B_OUT` → `D4.A`; `D4.K` → `U2B-` and **`R_led` (`2.2 kΩ` to `4.7 kΩ`) to `GND`**.
  - **Crucial safeguard**: Add a **`1N4148` anti-parallel clamp diode across `D4`** (Anode at `D4.K` / `U2B-`, Cathode at `D4.A` / `U2B_OUT`). If offset/noise ever pulls `U2B+` slightly negative, this clamps `U2B_OUT` at `-0.65 V` so the LED is never subjected to `-12 V` reverse breakdown (typical LED $V_{R,\max} \approx 5\text{ V}$).
- **Benefits**: Guaranteed **`0.00 mA` idle current** for **any LED color/forward voltage**, linear brightness proportional to envelope voltage (`0–4.5 mA` with `2.2 kΩ`), and independence from `-12V` supply drift. *(Note: In a 6-op-amp build, `U2B` gently saturates above `ENV_NODE ≈ +8.5 V` without affecting `ENV_NODE`; in an 8-op-amp build with a dedicated `ENV_CAP` buffer, dividing `U2B_OUT` by 2 into `U2D` with `R_led = 1 kΩ` keeps the LED linear all the way to `+10 V` even for a `3.2 V` blue LED.)*

### 2.3 Capacitor Dielectrics & Physical Sizing (`C1`, `C2`)

- **Do not use Class-2 MLCCs (X7R/X5R/Y5V) for `C2` (`1 µF`)**: Section 3.2 mentions `MLCC` as an option for `C2`. Class-2 MLCCs suffer from **piezoelectric microphonics** (tapping panel pots creates CV spikes) and **DC-bias capacitance loss** (losing 30–60% of nominal capacitance at `+10 V`, causing Attack and Release times to shrink dramatically on loud signals). Specify a **polyester/polypropylene film capacitor** (`1 µF`, e.g., 5 mm box film).
- **Shrink `C1` (`4.7 µF`) once `Z_in` is raised to `100 kΩ`**: A `4.7 µF` non-polarized film capacitor is physically large and costly. At `Z_in = 100 kΩ`, a compact **`1 µF` film** (`f_c = 1.59 Hz`) or **`470 nF` film** (`f_c = 3.39 Hz`) preserves the same low-frequency response in a standard 5 mm footprint without using bipolar electrolytics.

### 2.4 Preamp HF Compensation & Potentiometer Taper Selection (`RV1`, `RV2`, `RV3`)

- **Add `22 pF–47 pF` (`C0G/NP0`) feedback compensation across `RV1`**: Panel wiring to `RV1` adds stray capacitance at `U1A_INV` (`pin 2`). At `100 kΩ` gain, a small parallel feedback capacitor rolls off ultrasonic gain above `~34–72 kHz`, preventing peaking, RF pickup, and oscillation.
- **Potentiometer tapers (`A` vs. `B`)**:
  - **`RV1` (`GAIN`)**: Use a **`100 kΩ` audio/logarithmic (`A` taper)** pot. With a linear `100 kΩ` pot, unity gain (`1×`, `10 kΩ`) occurs at just **10% rotation**, crowding all normal Eurorack attenuation/unity levels into the bottom sliver while 90% of travel drives `±5 V` audio into hard rail clipping.
  - **`RV2` (`ATK`) & `RV3` (`Release`)**: Use **audio/log (`A` taper)** pots (especially for `RV3 = 1 MΩ`), giving fine control in the musical `10–200 ms` range.
- **Attack/Release interaction**: In any single-capacitor diode-RC detector driven by unsmoothed rectified AC, `RV2` (`ATK`) and `R10 + RV3` (`Release`) act as a voltage divider whenever $\tau_{\text{atk}} \gtrsim \tau_{\text{rel}}$. At `ATK = 50 kΩ` and `Release = 0 Ω` (`10 kΩ`), peak output drops to **`10k / (50k + 10k) = 16.7%` (`-15.6 dB`)**. Either increase `R10` (`22 kΩ–47 kΩ` if `22–47 ms` min release is acceptable), use `A`-taper pots to keep `RV3` away from low resistance in normal use, or split into a fast peak-hold (`Release`) stage followed by a buffered `ATK` slew stage if full-amplitude slow-attack + ultra-fast-release is required.

### 2.5 Output Load Accuracy (`R16`, `R19`)

- `R16` and `R19` (`1 kΩ`) sit outside the op-amp feedback loops, which safely protects against output shorts and cable capacitance, but causes a **`1%` voltage drop into `100 kΩ`** and a **`9.1%` drop into `10 kΩ`** (e.g., if patched into a second unit of this exact circuit!).
- **Optional precision CV enhancement**: Put `R16` / `R19` (`1 kΩ` or `470 Ω`) **inside the DC feedback loop** (taking a `10 kΩ` DC feedback resistor from the jack side of `R16`/`R19` back to the op-amp `-` pin, plus a `100 pF` local HF compensation cap directly from the op-amp output pin to `-`). This yields **zero DC load error** while retaining short-circuit and capacitive-load stability.

### 2.6 Optimal Allocation of `2 × TL074` (`Option C`, 8 Op-Amps)

Migrating from `1 × TL074 + 1 × TL072` (`Option A`, 6 op-amps) to `2 × TL074` (`Option C`, 8 op-amps) unifies the IC BOM and gives **2 spare op-amps** that can be assigned in either of two clean configurations:

1. **Allocation 1 (Inverting Input Preamp Preserved)**:
   - Spare #1: **`100 kΩ` unity-gain input buffer** before `R2` (`10 kΩ`) (eliminates `9.9 kΩ` loading without increasing preamp resistor noise or phase-reversal risk).
   - Spare #2: **Active precision peak detector** (`D3` inside loop) feeding `R_atk_min` + `RV2` → `C2`.
   - Combine with §1.1 Option A (`R14` removed, `RV4 = 10 kΩ`, `R13 = 18–22 kΩ`, `< 3.5%` gain variation) and §2.2 (in-loop LED driver on `U2B`).
2. **Allocation 2 (Exact `1.0×` Output Gain & `0%` Offset Interaction)**:
   - Use §1.4 6-op-amp option A (`RV1` as `100 kΩ` input attenuator into clamped non-inverting `+11×` `U1A`, `Z_in = 100 kΩ`).
   - Spare #1: **Active precision peak detector** (`D3` inside loop).
   - Spare #2: **`ENV_NODE` unity buffer** feeding `U1D` as an inverting `1.0×` summer (§1.1 Option B) while `U2B` remains dedicated to the in-loop LED driver (§2.2).

Any op-amp section still left unused in a build must be terminated as a unity-gain follower (`+` to `GND`, `-` to `OUT`), never left with floating inputs.

---

## 3. Discrepancies & Corrections Found in `EnvelopeFollower.md`

| Section / Line | Stated in `EnvelopeFollower.md` | Actual Circuit Behavior / Correction |
|---|---|---|
| **§1 Table (L15) & §4 Stage 1 (L137)** | Input AC-coupling high-pass cutoff $f_c \approx 0.034\text{ Hz}$ (calculated from `C1 = 4.7 µF` and `R1 = 1 MΩ`). | Because `R2` (`10 kΩ`) connects to `U1A`'s inverting virtual ground (`0 V`), `C1` sees $R_1 \parallel R_2 = 9.90\text{ k}\Omega$. The actual cutoff is **$f_c = \frac{1}{2\pi \cdot 4.7\,\mu\text{F} \cdot 9.90\,\text{k}\Omega} \approx 3.42\text{ Hz}$** (100× higher). |
| **§6.3 Pot Rotation (L221)** | *"RV4 (OFFSET): Pin 1 -> OFF_TOP, Pin 3 -> OFF_BOT makes clockwise push OUT more negative (or swap Pin 1/Pin 3 if you want clockwise to push OUT more positive)."* | **Sign reversed.** `OFF_TOP` is `+10 V` and `OFF_BOT` is `-10 V`. Turning CW moves wiper Pin 2 toward Pin 3 (`-10 V`), and because `U1D` **inverts** `OFF_WIPER`, turning CW pushes `OUT` **more positive (`+5.22 V`)**. The current netlist already yields intuitive `CW = +OUT` behavior; swapping Pins 1 and 3 would invert it. |
| **§4 Stage 4 (L152)** | Notes $\tau_{\text{rel,min}} = 11\text{ ms}$ from `(1 kΩ + 10 kΩ) · 1 µF`. | Omits that `R9` (`1 kΩ`) + `R10` (`10 kΩ`) attenuate `ENV_NODE` by `10/11` (`-9.1%`) relative to `ENV_CAP` when `Release` is at minimum. |
| **§3.2 Cap Voltage (L103–104)** | Lists `(minimum 16 V)` for `C3`/`C4` on `±12 V` rails. | Tighten minimum rating to **`≥ 25 V`** (`35 V` recommended) to provide standard ≥2× voltage derating margin. |

---

## 4. Optional Eurorack Feature Enhancements (Scope Extensions)

If expanding the module beyond a strict 1:1 fix of the original schematic:
1. **Gate / Trigger Extractor Output**: Compare `ENV_NODE` against an adjustable threshold pot (e.g., `0–8 V`) with slight positive hysteresis (`~100–200 mV`) to generate a clean `0/+10 V` Gate/Trigger output for triggering ADSRs or clock dividers from audio transients.
2. **AC / DC Input Coupling Switch**: A front-panel toggle (or jumper) bypassing `C1` allows the module to follow sub-3 Hz CVs and slow LFOs accurately while keeping AC-coupling available for DC-biased audio.
3. **Input Pad / Gain Range Switch**: A `1×` / `10×` range switch or pad prevents `±10 V` modular signals from saturating `U1A` while preserving `+20 dB` (or `+26 dB`) gain for quiet guitar/line inputs.
4. **Center-Detent `OFFSET` Pot & Bi-Color `OUT` LED**: A center-detent `10 kΩ` (`B`-taper) pot makes zero-offset easy to find by touch; a bi-color LED on `OUT` (or keeping single LED on `ENV_NODE`) visualizes bipolar offset shifts.
