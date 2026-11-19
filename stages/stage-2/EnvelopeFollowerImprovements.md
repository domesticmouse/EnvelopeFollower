# Envelope Follower — Circuit Review & Suggested Improvements

> **Reviewed Files:** [`EnvelopeFollower.md`](./EnvelopeFollower.md) and [`EnvelopeFollower.webp`](./EnvelopeFollower.webp)  
> **Scope:** Electrical performance, signal integrity, potentiometer ergonomics, power-supply protection, Eurorack standards compliance, and BOM/IC optimization. Reference designators (`R1`–`R23`, `C1`–`C4`, `D1`–`D4`, `RV1`–`RV4`, `U1`–`U2`, `J1`–`J3`) and net names follow `EnvelopeFollower.md`.

---

## Summary of Findings

The existing circuit is a solid, functional dual-rail (`±12 V`) Eurorack envelope follower, and `EnvelopeFollower.md` captures the schematic accurately. However, circuit analysis reveals several **analog design bottlenecks** (a `~0.6 V` peak-detector dead zone, an `84%` attack/release voltage-divider collapse, severe `OFFSET` pot nonlinearity with premature rail clipping, and an LED that glows continuously at `0 V` idle) alongside missing **Eurorack protections** (power reverse-polarity protection, per-IC decoupling capacitors, preamp gain floor limiting, output overvoltage/thermal protection, and explicit unused op-amp termination).

| Priority | Stage / Refs | Issue | Impact | Recommended Fix |
|---|---|---|---|---|
| **High** | Peak Detector (`D3`, `U1C`) | `D3` sits outside op-amp feedback | `~0.5–0.7 V` dead zone, thermal drift (`-2 mV/°C`), compressed quiet signals | Move `D3` inside a precision peak-detector feedback loop (`2x TL074` Option B) |
| **High** | Attack/Release (`RV2`, `R9`, `R10`, `RV3`, `C2`) | `RV2` (`50k`) + `R9+R10` (`11k`) form static divider; `ATK = 0 Ω` drives `1 µF` directly | Up to **84% amplitude loss** at high Attack + min Release; `R9` adds ~9% sag; op-amp current-limiting at `ATK = 0` | Remove `R9` from signal path; add `R_atk_min` (`220–470 Ω`); re-scale `R_rel,min > R_atk,max` or separate Peak + AR slew |
| **High** | Offset & Buffer (`U1D`, `RV4`, `R11`–`R15`) | `100k` pot loaded by `10k` (`R13`); `R14` sets `2.25x–2.52x` variable gain | Severe S-curve knob feel; `12%` gain shift with `OFFSET`; clips at `+10.5 V` when `ENV_RAW > ~4.2 V`; inverted knob direction | Re-architect as unity `ENV_RAW` buffer + inverting summer (`1.0x` constant gain, `RV4 = 10k`, `R13 = 20k`), or buffer `OFFSET` |
| **High** | LED Driver (`U2B`, `D4`, `R21`–`R23`) | `-2.79 V` cathode bias + `22k` anode resistor | High-efficiency LEDs glow continuously (`~30–40 µA`) at `0 V` silence; only `~0.36 mA` at `+10 V`; color-dependent | Use `U2B` as closed-loop op-amp LED current sink (`D4` in feedback + `R_set` to `GND` + clamp diode) |
| **Medium** | Input Preamp (`J1`, `C1`, `R1`, `R2`, `RV1`) | `10 kΩ` input Z; `R1` on op-amp side of `C1`; `RV1 = 0 Ω` mutes (`A_v = 0`); no clamp or HF cap | Loads passive/1k Eurorack sources (~9% loss); jack floats when unplugged; `0 Ω` dead mute/wiper drop; `TL07x` phase-reversal risk | Raise `R2` to `100 kΩ` (`RV1 = A1M`); add `R_gain_min` (`10 kΩ` for `0.1x` floor, or `100 kΩ` for `1x`) + `10 pF`; move `R1` to `IN_JACK` (`+ TN` to `GND`); add `1N4148` clamps on `U1A.IN-` |
| **Medium** | Rectifier (`U1B`, `U1C`, `R3`–`R8`) | `R8 = 22k` vs `20k` (`1.1x`); `U1B` clips at `>+9.8 V`; 5% E12 symmetry risk | Positive-peak folding near `+10 V`; half-wave ripple if resistors mismatch | Use `20k` 1% (or scale `U1B` to `-0.5x`) for exact `1.0x` gain and full negative headroom; add `10–22 pF` across `R8` |
| **Medium** | Controls (`RV1`–`RV4`) | Linear tapers assumed / unspecified | `GAIN`, `ATK`, and `Release` bunch useful settings into lowest 10–20% of travel | Use **Audio/Log (`A`)** taper for `GAIN`, `ATK`, `Release`; **Linear (`B`)** (optionally center-detent) for `OFFSET` |
| **Essential** | Power & Decoupling (`J_PWR`, `C3`, `C4`, `U1`, `U2`) | No reverse-polarity protection, no `100 nF` bypass caps, small `4.7 µF` bulk caps | Risk of IC/electrolytic destruction on backward cable; HF oscillation and rail coupling | Add shrouded `2x5` header + series `1N5817` Schottkys (`+` optional `10 Ω` RC); add `100 nF` ceramic (`≥25 V`) per IC rail pin; raise `C3`/`C4` to `10–47 µF ≥25 V` |
| **Essential** | Output Protection (`J2`, `J3`, `R16`, `R19`) | Unspecified `1k` wattage; no rail clamping against back-fed overvoltage or ESD | Opposite-rail shorts (`~0.51 W`) overheat `1/8–1/4 W` resistors; `>±12 V` faults/ESD hit op-amp outputs | Rate `R16`/`R19` (`1 kΩ`) at **`≥ 0.5 W`**; add **`BAV99`** (or paired `1N4148`) rail clamps on op-amp side + `22–100 pF` FB cap; leave `TN` open |
| **Essential** | Unused Stages & BOM (`U1`, `U2`, `C2`) | Unused stages in 6/7-stage `2x TL074` builds not fully specified; `C2` MLCC DC-bias loss | Floating op-amps rail/oscillate and inject noise; MLCC `C2` loses capacity under `10 V` | Terminate any unused stages as unity followers (`IN+ → GND`, `IN- ↔ OUT`); use film `C2`; consolidate on `2x TL074(H)` |

---

## 1. High-Impact Analog Performance Improvements

### 1.1 Eliminate the `~0.6 V` Peak-Detector Dead Zone (`D3`)
* **Current Circuit:** `D3` (`1N4148`) sits outside `U1C`'s feedback loop (`RECT_OUT` → `D3` → `RV2` → `C2`).
* **Problem:** `D3` imposes a forward voltage drop of $V_F \approx 0.5\text{–}0.7\,\text{V}$ (which also drifts at $\approx -2\,\text{mV}/^\circ\text{C}$). Rectified signals below $\sim 0.55\,\text{V}$ produce **zero** envelope output, and quiet transients near threshold suffer nonlinear compression unless `GAIN` is turned high enough to clip louder peaks.
* **Improvement:** Place `D3` inside the feedback loop of a dedicated **precision peak-detector op-amp** (`U_pk`) between `RECT_OUT` and `PEAK_DET`:
  * `U_pk.IN+` ← `RECT_OUT`
  * `U_pk.OUT` → `D3.A`
  * `D3.K` (`PEAK_DET`) → `U_pk.IN-` (and onward to `R_atk_min` + `RV2` → `C2`)
* **Why This Works & Trade-Offs to Watch:**
  * When `RECT_OUT > V_C2`, feedback forces `PEAK_DET` to equal `RECT_OUT` within $V_{\text{os}}$ ($\sim 1\text{–}3\,\text{mV}$), removing the `0.6 V` dead zone while preserving true RC attack timing (`RV2` remains *outside* the feedback loop so the op-amp does not slam to the rail to override `ATK`).
  * When `RECT_OUT < V_C2`, `D3` reverse-biases and `U_pk.OUT` rests at `Vcc-` (`~ -10.5 V`); recovery at `TL07x` slew rate (`13 V/µs`) takes `~1.5 µs`, negligible at audio rates. *(Do not add a direct clamp diode from `PEAK_DET` to `U_pk.OUT` without isolation, as that would discharge `C2` into `U_pk.OUT`.)*
  * **Important Interaction with `U1A` DC Offset:** Currently, `D3`'s `0.6 V` drop masks `U1A`'s input offset voltage ($V_{\text{os}} \approx \pm 3\text{ mV typ}, \pm 6\text{–}10\text{ mV max}$), which `U1A` amplifies by $(1 + R_{\text{RV1}}/R_2) = 11\times$ (`±33 mV` typ, up to `±110 mV`) at max `GAIN`. Once `D3`'s dead zone is removed, `U1A`'s offset is rectified into a small idle floor at high `GAIN`. Mitigate this either by using lower-offset op-amps (`TL074H` has `1 mV` typ `V_os`; `OPA4172` has `0.2 mV`), or by AC-coupling `PREAMP_OUT` into `R3`/`R4` (e.g., `10 µF` non-polarized cap into `6.67 kΩ` → $f_c \approx 2.4\,\text{Hz}$, noting AC coupling can shift baseline on strongly asymmetric waveforms).

---

### 1.2 Fix `ATK`/`Release` Voltage-Divider Collapse, `R9` Attenuation, and `ATK = 0 Ω` Shorting
* **Current Circuit:** `PEAK_DET` → `RV2` (`0–50 kΩ`) → `ENV_CAP` (`C2 = 1 µF`) → `R9` (`1 kΩ`) → `ENV_RAW` → `R10` (`10 kΩ`) + `RV3` (`0–1 MΩ`) → `GND`.
* **Problems:**
  1. **Up to 84% amplitude collapse:** Because `C2` charges through `RV2` while continuously discharging to `GND` through `R9 + R10 + RV3`, they act as a resistive divider whenever `D3` conducts. At maximum `ATK` (`50 kΩ`) and minimum `Release` (`RV3 = 0 Ω`, `11 kΩ` to `GND`), `ENV_RAW` is clamped to at most:
     $$V_{\text{ENV\_RAW,max}} = V_{\text{PEAK\_DET}} \cdot \frac{10\,\text{k}\Omega}{50\,\text{k}\Omega + 1\,\text{k}\Omega + 10\,\text{k}\Omega} \approx 0.164\,V_{\text{PEAK\_DET}}\quad (-15.7\,\text{dB})$$
  2. **Unnecessary gain sag from `R9` (`1 kΩ`):** Placing `R9` *before* `ENV_RAW` creates a `10k / 11k` (`0.909x`) divider at minimum release vs `0.999x` at maximum release, causing envelope amplitude to shift by ~9% as `Release` is adjusted.
  3. **Capacitive overload at `ATK = 0 Ω`:** With `RV2` turned fully down (`0 Ω`), `U1C` (or `U_pk`) drives `C2 = 1 µF` directly through `D3`, hitting op-amp short-circuit current limiting (`~20–30 mA`), collapsing output swing, and risking oscillation if `D3` is inside a feedback loop.
* **Improvements:**
  1. **Remove `R9` from the signal path:** Connect `ENV_CAP` (`C2`) directly to `ENV_RAW`, and place the full minimum release resistance (`R10 = 10 kΩ` or `12 kΩ`) purely in the `Release` branch to `GND`.
  2. **Add minimum attack resistance (`R_atk_min`):** Insert a **`220 Ω`–`470 Ω`** resistor in series with `RV2` (`ATK`). This limits peak charging current into `C2` to `<25 mA`, stabilizes `U_pk`/`U1C`, and still yields a snappy `0.22–0.47 ms` minimum attack.
  3. **Mitigate or eliminate the `ATK`/`Release` divider:**
     * *Simple passive scaling:* Because the steady-state divider ceiling $\frac{R_{\text{rel}}}{R_{\text{atk}} + R_{\text{rel}}} = \frac{\tau_{\text{rel}}}{\tau_{\text{atk}} + \tau_{\text{rel}}}$ depends only on time-constant ratio, keep $\tau_{\text{rel,min}} \ge 2\text{–}4\times \tau_{\text{atk,max}}$ where possible (e.g., `C2 = 470 nF`, `RV2 = A20k` [`~0.16–9.6 ms`], `R10 = 47 kΩ` [`22 ms` min release], `RV3 = A2M` [`0.96 s` max]), reducing worst-case divider loss from `84%` to `~30%`.
     * *Architectural alternative (if long Attack + short Release with full amplitude is needed):* Use a fast precision peak-hold stage (holding peak across audio cycles) buffered into an **independent Attack/Release slew limiter** (diode-steered charging/discharging to the buffered peak rather than to `GND`).

---

### 1.3 Fix `OFFSET` Pot Nonlinearity, Gain Modulation (`2.25x–2.52x`), Clipping, and Polarity (`U1D`)
* **Current Circuit:** `RV4` (`100 kΩ`) sits between `+12V` via `R11` (`10 kΩ`) and `-12V` via `R12` (`10 kΩ`), feeding `R13` (`10 kΩ`) into `U1D.IN-` alongside `R14` (`10 kΩ` to `GND`) and `R15` (`10 kΩ` feedback). `U1D.IN+` receives `ENV_RAW`.
* **Problems:**
  1. **Severe S-curve pot loading:** At `ENV_RAW = 0 V`, `U1D.IN-` is at `0 V` virtual ground, loading the `100 kΩ` wiper with `10 kΩ` (`R13`). Moving `OFFSET` from center (`50%`) to `75%` only changes `OUT` from `0 V` to `-1.44 V` (`28%` of span), while the last quarter (`75%` to `100%`) jumps from `-1.44 V` to `-5.22 V` (`72%` of span).
  2. **Gain changes with `OFFSET` knob position:** `RV4`'s Thevenin source impedance varies from `30 kΩ` (center) to `9.17 kΩ` (ends), shifting `U1D`'s non-inverting gain for `ENV_RAW` from **`2.25x` (center) to `2.52x` (extremes)** — a **12% sensitivity shift**.
  3. **Premature rail clipping & LED mismatch:** Because `U1D` amplifies `ENV_RAW` by `2.25x–2.52x`, `U1D` saturates at `~+10.5 V` as soon as `ENV_RAW` exceeds `~4.2–4.7 V` (or `~2.0 V` with `+5 V` offset), while the `LED` (driven by `ENV_RAW`) still reads below half scale.
  4. **Counter-intuitive knob direction:** Because `RV4` feeds `U1D.IN-`, turning the wiper toward the `+12V` end drives `OUT` **negative**.
* **Improvements:**
  * **Option A (Minimal 6-op-amp fix keeping `1x TL074 + 1x TL072` and keeping `U2B` as LED driver):**
    * Remove `R14` (`10 kΩ` to `GND`).
    * Change `RV4` from `100 kΩ` to **`10 kΩ` (`B10k`)**, reduce `R11 = R12 = 1 kΩ` (`±10 V` end limits), and scale `R13 = 100 kΩ`, `R15 = 47 kΩ`.
    * **Result:** `RV4` source impedance is only `0.92–3.0 kΩ` against `100 kΩ`: pot loading bow drops from `>70%` to **`<3%`**, `ENV_RAW` gain stabilizes at **`1.46x` with `<0.7%` variation** (`±4.7 V` offset range), and headroom expands substantially before clipping. Swap `+12V`/`-12V` connections on `RV4` so CW rotation increases `OUT` positively.
  * **Option B (Optimal `2x TL074` 8-op-amp architecture — exact `1.00x` gain & zero interaction):**
    * Buffer `ENV_RAW` with a unity-gain follower (`U2A` → `ENV_RAW_BUF`), sum `ENV_RAW_BUF` (`10 kΩ`) and `OFFSET` (`RV4 = 10 kΩ`, `R11=R12=1 kΩ`, `R13 = 20 kΩ`) in an **inverting summer (`U2C`)** with `10 kΩ` feedback to create **`INV_OUT`** (`-1.00x * ENV_RAW - 0.5 * V_OFF`), and invert with **`U2D`** (`10 kΩ / 10 kΩ`) to create **`OUT`** (`+1.00x * ENV_RAW + 0.5 * V_OFF`).
    * **Result:** Exact **`1.00x` (`0–10 V`) headroom**, **`0.00%` gain dependence** on `OFFSET` position, smooth offset response (`±4.8 V` with `R11=R12=1 kΩ`, or `±5.0 V` with `R13 = 19.1 kΩ` / `R11=R12=470 Ω`), and `+12V` on CW (`Pin 3`) naturally increases `OUT` positively while `INV_OUT` moves negatively.

---

### 1.4 Fix LED Quiescent Glow at `0 V`, Low Drive Current, and Color Sensitivity (`U2B`, `D4`)
* **Current Circuit:** `U2B` voltage follower drives `D4` (`LED`) via `R21 = 22 kΩ`, with cathode pre-biased at `-2.79 V` (`7.67 kΩ` Thevenin) by `R22` (`10 kΩ` to `GND`) and `R23` (`33 kΩ` to `-12V`).
* **Problems:**
  1. **LED stays lit in silence:** At `ENV_RAW = 0 V`, `U2B_OUT = 0 V`, placing **`+2.79 V`** across `R21 + D4 + 7.67 kΩ`. For standard red, yellow, or green LEDs ($V_F \approx 1.6\text{–}2.0\,\text{V}$ at µA currents), this drives **`~30–40 µA` continuously at `0 V`** — clearly visible on the **high-efficiency/ultrabright LEDs** required by `R21 = 22 kΩ` (which only supplies `~0.36 mA` at `+10 V`).
  2. **Strong LED color sensitivity:** Switching to a blue/white LED ($V_F \approx 2.8\text{–}3.0\,\text{V}$) changes both turn-on threshold and brightness dramatically, while standard low-efficiency red/green LEDs appear very dim at `0.36 mA`.
* **Improvement:** Convert `U2B` into a **closed-loop op-amp LED current sink/driver** (delete `R21`, `R22`, `R23`):
  * Connect `U2B.IN+` ← `ENV_RAW` (or `ENV_RAW_BUF`).
  * Connect `U2B.OUT` → `D4.A` (`LED` anode), and `D4.K` (`LED` cathode) → `U2B.IN-`.
  * Connect **`R_set`** from `U2B.IN-` to `GND`: use **`2.2 kΩ`** for standard LEDs (`0–4.5 mA` across `0–10 V`) or **`4.7 kΩ`** for ultrabright LEDs (`0–2.1 mA`).
  * Add an **anti-parallel clamp diode (`1N4148`)** across `D4` (anode to `U2B.IN-`, cathode to `U2B.OUT`) and a **`100 pF`** feedback capacitor from `U2B.OUT` to `U2B.IN-` to keep the loop closed and prevent reverse-voltage breakdown if `U2B.IN+` ever sits slightly negative due to input offset.
  * *(Optional anti-offset polish:)* Add a **`1 MΩ` pull-up** from `U2B.IN-` to `+12 V` (`12 µA` bias). With `R_set = 2.2 kΩ`, `D4` remains strictly **0.00 mA** until `ENV_RAW > +26 mV`, guaranteeing zero idle glow even under worst-case `±10 mV` `TL07x` input offset voltage, while still eliminating the `~1.8–3.0 V` LED dead zone and removing `-12 V` bias bleed.

---

## 2. Medium-Impact Signal-Path & Headroom Improvements

### 2.1 Raise Input Impedance to `100 kΩ`, Relocate `R1`, Add Gain Floor, and Prevent `TL07x` Phase Reversal (`U1A`)
* **Current Circuit:** `J1` → `C1` (`4.7 µF`) → `IN_AC` (`R1 = 1 MΩ` to `GND`, `R2 = 10 kΩ` to `U1A.IN-`), `RV1 = 100 kΩ` feedback.
* **Problems:**
  1. **Low `~9.9 kΩ` input impedance:** Standard Eurorack input impedance is **`100 kΩ`**. A `10 kΩ` input loads down `1 kΩ` module outputs by `~9%` and severely attenuates passive attenuators, dynamic mics, contact mics, or instrument pickups.
  2. **`R1` is on the wrong side of `C1`:** Because `U1A.IN-` is a virtual ground, `IN_AC` is already pulled to `0 V` via `R2 = 10 kΩ` (`1 MΩ || 10 kΩ` is redundant). Meanwhile, `IN_JACK` has no DC path to `GND` when `J1` is unpatched, allowing `C1` to hold charge and create patch-in thumps.
  3. **`0 Ω` minimum feedback / no gain floor:** At full CCW (`RV1 = 0 Ω`), gain drops to `A_v = 0` (`-∞ dB` dead mute), `U1A.OUT` shorts directly to `U1A.IN-` across wiper end-stop resistance (causing erratic dropout near the stop), and any parallel feedback compensation capacitor is shorted out.
  4. **`TL07x` phase-reversal hazard:** If `RV1` is at `100 kΩ` (`10x` gain) and a hot Eurorack input drives `V_in < -11 V`, `U1A.OUT` clips at `+10.5 V` and `U1A.IN-` is pulled below `-9 V` — violating `TL07x` common-mode limits (`Vcc- + 3..4 V`) and triggering **output phase inversion** (output abruptly snapping to `-10.5 V`).
  5. **Linear gain taper & HF stability:** With `RV1 = 100 kΩ` linear over `10 kΩ`, gains from `0x` to `1x` sit in the bottom `10%` of rotation; high-gain feedback also benefits from minor HF roll-off.
* **Improvements:**
  * Change **`R2` to `100 kΩ`** and **`RV1` to `A1M`** (audio/log taper) for Eurorack-standard `100 kΩ` input impedance.
  * Add **`R_gain_min`** in series with `RV1` to set a non-zero **gain floor** (`10 kΩ` for **`0.1x–10.1x`** to tame hot `±10 V` signals without muting, or `100 kΩ` for **`1.0x–11.0x`** unity floor; see **Section 3.3**).
  * Use **`1 µF` film (`≥ 50 V`)** for `C1` ($f_c = 1.6\,\text{Hz}$ into `100 kΩ`, smaller and more accurate than `4.7 µF`) or keep `4.7 µF` ($f_c = 0.34\,\text{Hz}$).
  * Move **`R1` (`100 kΩ`–`1 MΩ`) to the jack side (`IN_JACK` to `GND`)** and wire `J1`'s tip-normalled (`TN`) contact to `GND` so unpatched inputs are quiet and `C1` stays discharged.
  * Add **`10 pF`** ceramic across the full feedback branch (`R_gain_min + RV1`, from `U1A.IN-` to `U1A.OUT`, `f_c ≈ 15.8 kHz` at `10x` gain) for ultrasonic/RF stability.
  * Add **anti-parallel `1N4148` clamp diodes from `U1A.IN-` to `GND`** (invisible at `0 V` virtual ground during linear operation, clamping `U1A.IN-` within `±0.6 V` during saturation to completely prevent `TL07x` phase inversion), and/or use **`TL074H` / `TL072H`** (phase-reversal-free).

---

### 2.2 Correct Rectifier Gain (`1.1x` → `1.0x`), `U1B` Negative Headroom, and Symmetry (`U1B`, `U1C`)
* **Current Circuit:** `R3 = R6 = R7 = 10 kΩ`, `R4 + R5 = 20 kΩ`, `R8 = 22 kΩ` (`+1.10x` gain).
* **Problems:**
  1. **`U1B` negative saturation clipping on `+10 V` peaks:** When `PREAMP_OUT = +10.5 V`, `HALF_WAVE` must reach `-10.5 V`, forcing `U1B_OUT` to `-10.5 V - 0.7 V (D2) = -11.2 V`. Under its `5 kΩ` (`R6 || R7`) load, a standard `TL07x` on `±12 V` clips around `-10.3 V` to `-10.5 V`, causing `HALF_WAVE` to stall around `-9.8 V` and **folding/distorting `RECT_OUT` downward** at maximum amplitude.
  2. **Unintended `1.1x` gain & E12 tolerance sensitivity:** `R8 = 22 kΩ` causes `U1C` to clip slightly before `U1A` (`1.1 * 10.5 V > 10.5 V`). Additionally, because positive and negative half-cycles traverse different resistor ratios, `5%` resistors can create noticeable half-wave asymmetry and fundamental-frequency ripple.
* **Improvements:**
  * Use **1% metal film resistors** across `U1B` and `U1C` for clean half-wave symmetry.
  * Replace `R4 + R5` (`10k + 10k`) and `R8` (`22k`) with **`20 kΩ` 1%** (E24) for exact **`1.00x`** unity gain and lower part count (or if restricted strictly to E12 `10k` values, set `R4 = 10 kΩ`, `R7 = 10 kΩ || 10 kΩ = 5 kΩ`, `R8 = 10 kΩ`).
  * To eliminate `U1B` negative saturation on `±12 V` rails: either use **`TL074H`** (output swings within `~0.1–0.5 V` of rails), **or scale `U1B` to `-0.5x` gain** (`R3 = 20 kΩ`, `R6 = 10 kΩ`, `R7 = 10 kΩ`, `R_ff = 40 kΩ` [`20k + 20k`], `R8 = 40 kΩ` [`20k + 20k`]), which keeps `U1B_OUT` within `-5.95 V` even at `+10.5 V` `PREAMP_OUT` while maintaining exact `1.00x` gain and light `5 kΩ` loading.
  * Add **`10–22 pF`** across `R8` (`U1C` feedback) to damp zero-crossing switching glitches from `D1`/`D2`.

---

### 2.3 Specify Potentiometer Tapers (`RV1`–`RV4`)
* **Problem:** Linear pots (`B` taper) on `GAIN` (`0–10x`), `ATK` (`0–50 ms`), and `Release` (`10 ms–1.01 s`) crowd almost all useful musical adjustments into the lowest 10–20% of rotation (e.g., `Release` hits `110 ms` by 10% rotation and only varies `2x` across the entire top half of the knob).
* **Improvement:**
  * `RV1` (`GAIN`), `RV2` (`ATK`), `RV3` (`Release`): Specify **Audio / Logarithmic (`A` taper)** potentiometers wired so resistance increases clockwise (Pin 1 = CCW, Pins 2+3 = CW+Wiper).
  * `RV4` (`OFFSET`): Specify **Linear (`B` taper)**, ideally with a **center detent** for repeatable `0 V` offset.

---

## 3. Eurorack Circuit Protections, Power & Hardware Compliance

### 3.1 Power Supply Reverse-Polarity Protection & Header (`J_PWR`)
* **Standard `2x5` Shrouded Header:** Replace the raw terminal flags (`+12Vin`, `GND`, `-12Vin`) with a shrouded, keyed **`2x5` (10-pin) Eurorack IDC header** (Pins 1–2 `-12Vin` [red stripe], Pins 3–8 `GND`, Pins 9–10 `+12Vin`).
* **Series Schottky Reverse-Polarity Diodes (`1N5817` / `1N5819` THT or `SS14` / `B5819W` SMD, `≥ 20–40 V`, `1 A`):**
  * `+12V` rail: `J_PWR (+12Vin)` → **Anode**, **Cathode** → protected `+12V_PROT` bus.
  * `-12V` rail: `J_PWR (-12Vin)` → **Cathode**, **Anode** → protected `-12V_PROT` bus.
  * **Why series Schottkys:** Unlike shunt-only clamp diodes (which short the rack PSU if unfused), series Schottkys cleanly block reverse current with zero fault stress, dropping only `~0.25–0.35 V` at module draw (`~10–20 mA`, leaving `±11.65–11.75 V`). Place `C3`, `C4`, and all IC rails **downstream** of these diodes so polarized electrolytics are never reverse-biased.
* **Optional Surge Limiting / R-C Rail Filtering (`10 Ω` or PTC):**
  * Adding **`10 Ω` (`1/4 W`, or fusible) resistors** in series between the Schottky diodes and `C3`/`C4` creates a `~340–720 Hz` R-C filter (with `22–47 µF`) that attenuates Eurorack PSU switching ripple and limits hot-plug inrush current (total rail drop `~0.4–0.5 V`, leaving `~±11.5 V`, still exceeding `±10 V` output swing with `TL074H`). Alternatively, **`100–200 mA` resettable PTC polyfuses** can be used for sustained fault current limiting.

### 3.2 Local IC Decoupling & Bulk Power Filtering (`U1`, `U2`, `C3`, `C4`)
* **Per-IC Ceramic Decoupling (`100 nF`):** Place **`100 nF` (`0.1 µF`) `X7R` or `C0G/NP0` ceramic capacitors rated `≥ 25 V` (preferably `50 V`)** physically within a few millimeters of the power pins of **every** op-amp IC (`4` caps for a 2-IC build; `6` caps if using `3x TL072`), with short, low-inductance traces to `GND`:
  * One `100 nF` from `V+` (`+12V_PROT`) to `GND` and one `100 nF` from `V-` (`-12V_PROT`) to `GND` per package.
  * **Pin mapping:** For `TL074` (`U1`, and `U2` in `2x TL074` builds): **Pin 4 (`V+`) → `GND`**, **Pin 11 (`V-`) → `GND`**. For `TL072` (if used): **Pin 8 (`V+`) → `GND`**, **Pin 4 (`V-`) → `GND`**.
  * Prevents high-frequency op-amp oscillation, rectifier switching transients (`D1`/`D2`), and inter-stage rail coupling.
* **Bulk Electrolytic Upgrades (`C3`, `C4`):** Increase `C3`, `C4` from `4.7 µF` to **`10 µF`–`47 µF` (`≥ 25 V` or `35 V` rated)** right at `J_PWR` downstream of the reverse-polarity diodes (`C3.+` to `+12V_PROT`, `C3.-` to `GND`; `C4.+` to `GND`, `C4.-` to `-12V_PROT`).

### 3.3 Preamp Gain Floor Limiting & Input Protection (`U1A`, `RV1`, `J1`, `C1`)
* **Add Minimum-Gain Series Resistor (`R_gain_min`):** Insert a fixed resistor **`R_gain_min`** in series with `RV1` (`GAIN`) between `PREAMP_INV` (`U1A.IN-`) and `PREAMP_OUT` (`U1A.OUT`), placing the `10 pF` HF compensation capacitor across the entire `R_gain_min + RV1` branch:
  * Prevents `RV1 = 0 Ω` from muting the module to `A_v = 0` (`-∞ dB`), eliminates wiper end-stop contact-resistance dropouts/crackle near full CCW, and keeps non-zero feedback impedance across the `10 pF` compensation cap.
  * **Recommended Floor Values (choose per gain-range preference):**
    * **`0.1x` (`-20 dB`) attenuating floor (recommended Eurorack default):** **`R_gain_min = 10 kΩ`** with revised `R2 = 100 kΩ` / `RV1 = A1M` (**`0.1x` to `10.1x`**; or **`1 kΩ`** on original `R2 = 10 kΩ` / `RV1 = 100 kΩ`). Allows hot `±10 V` Eurorack signals to be scaled down cleanly without muting.
    * **`1.0x` (`0 dB`) unity floor (boost-only alternative):** **`R_gain_min = 100 kΩ`** with `R2 = 100 kΩ` / `RV1 = A1M` (**`1.0x` to `11.0x`**; or **`10 kΩ`** on original `10 kΩ` / `100 kΩ`). Guarantees gain never drops below unity, though `±10 V` inputs cannot be attenuated prior to `OFFSET` summing.
* **Open-Track Fail-Safe & Input Clamping:** Keep `RV1.W` tied to `RV1.L2` so normal wiper lift defaults to max pot resistance (`10x`) rather than open-loop saturation (optionally add a `2.2–4.7 MΩ` resistor directly from `PREAMP_INV` to `PREAMP_OUT` for broken-track fail-safe). Pair with anti-parallel **`1N4148` clamps** on `U1A.IN-` to `GND` (preventing `TL07x` phase inversion/overdrive) and rate `C1` at **`≥ 50 V` film** to safely block external DC voltages on `J1`.

### 3.4 Output Protection (`J2` `OUT`, `J3` `INV_OUT`, `R16`, `R19`)
* **Thermal Power Rating for `R16` & `R19` (`1 kΩ`):** Specify **`1 kΩ ≥ 0.5 W` (`1/2 W`)** through-hole (or `2x 470 Ω 1/4 W` in series / `2x 2 kΩ 1/4 W` in parallel / `1206`–`2010` power SMD). While `1 kΩ` limits short-to-GND current to `~10–12 mA`, patching an output at `+10.5–11.5 V` into `-12 V` (or an opposite-polarity low-impedance driver) places `~22.5 V` across `1 kΩ`, dissipating **`~0.51 W`** — enough to scorch `1/8 W` (`0603`/`0805`) or `1/4 W` resistors.
* **External Overvoltage & ESD Rail Clamps (`BAV99` or paired `1N4148`s):** On both `OUT` and `INV_OUT`, connect a dual series diode clamp (**`BAV99`** SOT-23 or two `1N4148`s per output: anode to `-12V_PROT`, common midpoint to the op-amp output node *behind* `R16`/`R19`, cathode to `+12V_PROT`):
  * Remains reverse-biased and transparent across normal `±10–11.5 V` swings (`< 10 nA` leakage). Use `BAV99`/`1N4148` (`V_f ≈ 0.65 V`) rather than low-`V_f` Schottkys (`BAT54S`) so rail-to-rail `TL074H` outputs never forward-bias the clamps.
  * When external overvoltages (`>±12 V`) or ESD transients hit `J2.T`/`J3.T`, `R16`/`R19` (`1 kΩ`) limits fault current while `BAV99` shunts excess voltage safely to the rails before back-feeding the op-amp output silicon. *(Optional split-resistor variant: `220 Ω` jack-side → `BAV99` midpoint → `820 Ω` op-amp-side clamps fast ESD spikes before they reach the IC output pin.)*
* **Capacitive Load Stability & Jack Normalization:** Keep `R16`/`R19` outside the op-amp feedback loop to isolate long Eurorack patch-cable capacitance, include **`22–100 pF`** HF compensation across the output op-amp feedback resistors (`R15`, `R18`, or `U2C`/`U2D` `10 kΩ`), and leave `TN` **unconnected** on `J2` and `J3`.

### 3.5 Unused Op-Amp Termination
* **When Unused Stages Occur:** The full 8-stage Option B (`2x TL074(H)`, Section 4) uses all 8 stages (`0` unused). However, building the original 6-stage circuit or Option A with `2x TL074(H)` leaves **2 unused stages (`U2C`, `U2D`)**, and a 7-stage partial build leaves **1 unused stage (`U2D`)**.
* **Required Unity-Follower Termination:** Never leave unused op-amp inputs floating (causes rail saturation, excess quiescent current, and HF oscillation that couples into active stages), never short `IN+` directly to `IN-`, and never ground `OUT`. Because dual `±12 V` supplies place `GND` (`0 V`) squarely within `TL07x` and `TL074H` common-mode range, terminate each unused op-amp as a **unity-gain follower tied to `GND`**:
  * Wire **`IN+` → `GND`**, **`IN-` ↔ `OUT`**, and leave **`OUT` unconnected** to any external load.
  * **Exact `TL074` (`DIP-14`/`SOIC-14`) pin connections:**
    * Unused `U2C`: **Pin 10 (`IN+`) → `GND`**, **Pin 9 (`IN-`) ↔ Pin 8 (`OUT`)**.
    * Unused `U2D`: **Pin 12 (`IN+`) → `GND`**, **Pin 13 (`IN-`) ↔ Pin 14 (`OUT`)**.
    * *(If one half of a `TL072` is ever unused: **Pin 5 (`IN+`) → `GND`**, **Pin 6 (`IN-`) ↔ Pin 7 (`OUT`)**.)*
  * Ensure `U2` still receives `±12V_PROT` supply rails and local `100 nF` decoupling caps.

### 3.6 Component Dielectrics, BOM Consolidation & Input Jack Normalization
1. **Specify Film Dielectric for `C2` (`1 µF` / `470 nF`):** Explicitly specify a **polyester/polypropylene film capacitor** (e.g., WIMA MKS2) for `C2`, and avoid high-K MLCCs (`X7R`/`X5R`), which lose `50–80%` of capacitance under `10 V` DC bias and introduce piezoelectric microphonics and higher leakage during `1 s` releases.
2. **Consolidate BOM to `2x TL074` (or `2x TL074H`):** Replacing `1x TL074 + 1x TL072` with **`2x TL074` (or `2x TL074H`)** keeps the **exact same 2-IC package count**, eliminates a unique BOM line item, and yields the two extra op-amp stages needed for the **precision peak detector** and **exact-`1.0x` `OFFSET` buffer/summer** (or safely terminated per Section 3.5 in 6/7-stage builds).
3. **Switched Input Jack Normalization (`J1`):** Wire `J1` (`IN`) tip-normalled switch pin (`TN`) to `GND` so an unpatched module has zero floating hum/noise pickup; leave `TN` unconnected on `OUT` (`J2`) and `INV_OUT` (`J3`).

---

## 4. Recommended Revised Architecture (`2x TL074H` Optimal Build)

Using two quad op-amps (`2x TL074` or `2x TL074H`, same 2-IC count as the original `TL074 + TL072`) implements all major analog fixes and Eurorack protections cleanly:

```text
POWER:  [J_PWR 2x5] ─► [1N5817 + opt 10Ω] ─► [C3/C4 22–47µF ≥25V] ─► ±12V_PROT
                                                                        ├─► U1 (Pin4/11 + 2x 100nF → GND)
                                                                        └─► U2 (Pin4/11 + 2x 100nF → GND)

SIGNAL: IN (J1, TN→GND) ──┬── [R1 1M→GND]
                          └── [C1 1µF ≥50V film] ── [R2 100k] ──► [U1A Preamp: (R_gain_min 10k + RV1 A1M) || 10pF, 1N4148 clamps on IN-]
                                                                      │
                                 ┌── [R4+R5 40k (20k+20k) 1%] ────────┼── [R3 20k 1%] ──► [U1B -0.5x HWR: D1, D2, R6 10k 1%]
                                 │                                                               │
                                 └────────────────────────► [U1C Summer: R7 10k 1%, R8 40k 1% || 15pF] ◄┘
                                                                      │
                                                                 [RECT_OUT]
                                                                      │
                                                                      ▼
                                                        [U1D Precision Peak Detector]
                                                         (D3 inside feedback loop)
                                                                      │
                                                         [R_atk_min 330Ω] + [RV2 A20k]
                                                                      │
                                                            ┌─────────┴──────────┐
                                                        [C2 470nF film]    [R10 47k + RV3 A2M] ──► GND
                                                            │
                                                        [ENV_RAW]
                                                            │
                                                  [U2A Unity Buffer]
                                                            │
                                                      [ENV_RAW_BUF]
                                              ┌─────────────┴─────────────┐
                                              ▼                           ▼
                                [U2B LED Current Sink]      [U2C Inverting Summer (-1.0x || 47pF)] ◄── [RV4 B10k + R11/R12 1k → R13 20k]
                                 (D4 in FB, R_set 2.2k,            │
                                  1N4148 clamp, 100pF)             ├──► [BAV99 clamps ±12V] ─► [R19 1k ≥0.5W] ─► INV_OUT (J3, TN open)
                                                                   ▼
                                                     [U2D Unity Inverter (+1.0x || 47pF)] ─► [BAV99 clamps ±12V] ─► [R16 1k ≥0.5W] ─► OUT (J2, TN open)
```

*(Note: All 8 op-amp stages are active above; if building a 6- or 7-stage variant with `2x TL074`, tie unused `U2C`/`U2D` stages as unity-gain followers per Section 3.5.)*

### Key Gains Over the Original Circuit
* **Zero dead zone:** Responds linearly to quiet signals down to millivolts (`D3` inside `U1D` feedback).
* **Full `0–10 V` CV range with independent `OFFSET`:** `OUT` and `INV_OUT` maintain an exact `1.00x` (`±4.8 V` offset) scale without clipping early or shifting sensitivity when `OFFSET` is turned.
* **Clean `ATK`/`Release` behavior:** Worst-case divider drop reduced from `84%` to `~30%` (with `R_atk_min` protecting the op-amp at `ATK = 0`), zero `R9` sag, and musical log pot response.
* **Crisp LED indicator:** Completely off (`0.00 mA`) in silence, linearly tracks `ENV_RAW` regardless of LED color.
* **Full Eurorack protection & compliance:** Shrouded `2x5` power header with series Schottky reverse-polarity protection, `100 nF` local IC decoupling per rail pin, `100 kΩ` input Z with `R_gain_min` gain floor limiting and phase-reversal clamps, `1 kΩ ≥ 0.5 W` + `BAV99` output protection, and documented unused op-amp termination.
