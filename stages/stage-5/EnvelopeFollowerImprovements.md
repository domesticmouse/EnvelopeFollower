# Envelope Follower — Circuit Review & Suggested Improvements

Review of the circuit documented in [`EnvelopeFollower.md`](./EnvelopeFollower.md) (derived from [`EnvelopeFollower.webp`](./EnvelopeFollower.webp)).

Overall, the baseline design is a clean, buildable analog full-wave envelope follower, and `EnvelopeFollower.md` accurately captures the hand-drawn schematic (`D1`/`D2`/`D3` polarities, op-amp pinouts, and net connectivity all match `EnvelopeFollower.webp`). However, electrical analysis reveals several **missing Eurorack hardware protections, practical reliability risks, severe control/gain interactions, non-ideal passive losses, and documentation inaccuracies** that should be addressed before committing the design to a PCB or Eurorack module.

---

## 1. Prioritized Summary of Suggested Improvements

| ID | Priority | Stage / Refs | Issue in Baseline Design | Recommended Improvement |
|---|---|---|---|---|
| **IMP-01** | **Critical** | Power (`U1`, `U2`, `J4`, `C3`, `C4`) | No reverse-polarity power protection; no local `100 nF` IC decoupling caps; `4.7 µF` bulk caps lack voltage rating | Add keyed `2×5` IDC header (`J4`), series `40 V` Schottky reverse-polarity diodes (`1N5819`/`SS14`, `D4`/`D5`) upstream of `C3`/`C4` (or PTC + shunt clamp), `4× 100 nF / 50 V` local bypass caps (`C5`–`C8`) at `U1`/`U2` power pins, and `22–47 µF / ≥35 V` bulk electrolytics |
| **IMP-02** | **Critical** | Stage 4 (`R9`, `D3`, `RV2`, `C2`, `R10`, `RV3`) | `R9` (`1 kΩ`) is placed *after* `C2` instead of *before* it (`U1C` shorts into `1 µF` at `ATK = 0 Ω`; `R9`/`R10` causes `9.1%` release-dependent sag); `ATK` (`50 kΩ`) vs `R10` (`10 kΩ`) causes up to **`83.6%` DC/peak attenuation** | Move `R9` (`220–470 Ω` or `1 kΩ`) *before* `C2` in series with `D3`/`RV2`; re-scale `C2`/`RV2`/`R10` (so `R10 ≫ R_ATK_max`) or isolate attack/release with an active buffered detector |
| **IMP-03** | **High** | Stage 4 (`D3`, `C2`) | `D3` (`1N4148`) sits outside `U1C`'s feedback loop (`~0.6 V` dead zone); `EnvelopeFollower.md` §7.3 allows X7R ceramic for `C2` (up to `30–60%` DC-bias capacitance drop) | Place `D3` inside an active precision peak-detector loop (using a spare op-amp from `2× TL074` + inter-stage AC coupling), and mandate **film (`MKS2`/polypropylene) or C0G/NP0** for `C2` |
| **IMP-04** | **High** | Stage 1 (`J1`, `C1`, `R1`, `R2`, `RV1`, `U1A`) | Low `9.9 kΩ` input impedance loads sources; `RV1` drops to `0 Ω` feedback (`0×` dead-mute gain floor & shorted feedback compensation); floating `IN_TIP`; `0–27.7×` gain clips `±5 V` signals above `~10%` travel; high-K MLCC distortion on `C1` | Add **gain floor limiting resistor `R_gain_min`** (`4.7 kΩ` for `0.47×` floor or `10 kΩ` for `1.0×` floor) in series with `RV1`, raise `Z_in` to `100 kΩ`, shrink `C1` to `470 nF–1 µF` film, ground `J1` normal pin, use `A100K` pot, add `15 pF` comp cap across `R_gain_min + RV1`, and add `1 kΩ + BAV99` input clamp |
| **IMP-05** | **High** | Stages 5–6 (`U1D`, `U2A`, `RV4`, `R11`–`R19`, `J2`, `J3`) | `RV4` wiper impedance shifts output gain by `12%`; `OFFSET` CW turns `OUT` negative; `±12 V` ripple couples to outputs; `2.25×` gain halves `C2` headroom; `R16`/`R19` lack output-to-output power margin & ESD/over-voltage clamps | Buffer `RV4` (or use inverting summer), swap `RV4` lugs so CW = positive, decouple `OFFSET` (`10 µF + 100 nF`), lower Stage 5 gain to `1.0×`, and add **Eurorack output protection** (`1 kΩ ≥ 0.5 W` or `2× 499 Ω / 0.25 W` series resistors, `BAT54S`/`BAV99` rail clamps behind `R_out`, and `NC` jack normal pins) |
| **IMP-06** | **High** | Stage 7 (`U2B`, `R21`–`R23`, `LED1`) | At unclipped `OUT` max (`V_env = 4.67 V`), `I_LED` is only `0.15–0.19 mA` (very dim), yet `-2.79 V` cathode bias causes `~33 µA` idle glow on red LEDs and wastes `-12 V` current | Rewire `U2B` as an active transconductance LED driver (`I_LED = V_env / R_set`) with an anti-parallel `1N4148` clamp diode across `LED1`, eliminating `R22` and `R23` |
| **IMP-07** | **Medium** | Stages 2–3 (`U1B`, `U1C`, `R3`–`R8`) | Half-wave subtraction makes FWR symmetry highly sensitive to resistor tolerance (`±8%` at 1%, `±44%` at 5%), generating `1× f_in` ripple; `U1A` `11× V_os` reaches rectifier | Use matched `1%` or `0.1%` resistors for `R3`–`R7`; add inter-stage AC coupling (`1 µF` + `100 kΩ`) before `R3`/`R4` if using an active deadband-free peak detector |
| **IMP-08** | **Medium** | Stage 4 (`RV2`, `RV3`), IC BOM & Spare Channels | Linear `B1M` `Release` pot squeezes `11–100 ms` into the bottom `9%` of rotation; `1× TL074 + 1× TL072` splits IC BOM with zero spares; any spare `TL074` channels risk oscillation/saturation if left floating | Use audio/log `A1M` (`Release`) and `A50K` (`ATK`); consolidate ICs to **`2× TL074`**; **terminate any unused op-amp channels (`U2C`/`U2D`)** as `GND`-biased unity-gain followers (`+` to `GND`, `-` to `OUT`) |
| **IMP-09** | **Low / Optional** | Functional & Eurorack Extensions | 1st-order decay passes heavy `100 Hz` ripple on bass signals at fast `Release`; no AC/DC switch or Gate output | Add optional 2nd-order `30–40 Hz` Sallen-Key smoothing filter, AC/DC coupling toggle, and optional Gate/Trigger comparator output |

---

## 2. Detailed Circuit Improvements & Engineering Rationale

### 2.1 Power Supply, Decoupling, IC Consolidation & Unused Op-Amp Termination (`J4`, `C3`, `C4`, `U1`, `U2`)

1. **Add Mandatory Local `100 nF` Ceramic Decoupling Capacitors (`C5`–`C8`)** *(Critical)*
   - **Issue:** `EnvelopeFollower.webp` shows only the two bulk `4.7 µF` rail capacitors (`C3`, `C4`) near `J4`. As noted in `EnvelopeFollower.md` §7.1, there are no local high-frequency decoupling capacitors at `U1` or `U2`. Because `TL07x` has a relatively fast `~13 V/µs` slew rate and `U1C` drives current pulses into `C2` (`1 µF`), trace inductance on `±12V` causes local rail droop, ground bounce, and potential high-frequency op-amp oscillation.
   - **Fix:** Place **`4× 100 nF` (`50 V` `X7R` or `C0G`)** ceramic bypass capacitors (`0603`/`0805` or THT) within **`< 3–5 mm`** of each IC's power pins with short wide traces and dedicated vias directly to the `GND` plane (`50 V` rating minimizes DC-bias derating at `12 V` and provides surge margin for hot-plugging):
     - **`U1` (`TL074`, DIP-14/SOIC-14):** **`C5`** (`100 nF`) from **Pin 4 (`+12V`)** to `GND`; **`C6`** (`100 nF`) from **Pin 11 (`-12V`)** to `GND`.
     - **`U2` (if `TL072` baseline, DIP-8/SOIC-8):** **`C7`** (`100 nF`) from **Pin 8 (`+12V`)** to `GND`; **`C8`** (`100 nF`) from **Pin 4 (`-12V`)** to `GND`.
     - **`U2` (if consolidated to `TL074`, DIP-14/SOIC-14):** **`C7`** (`100 nF`) from **Pin 4 (`+12V`)** to `GND`; **`C8`** (`100 nF`) from **Pin 11 (`-12V`)** to `GND`.

2. **Add Reverse-Polarity Power Protection on `J4` + Upgrade Bulk Capacitance (`D4`, `D5`, `C3`, `C4`)** *(Critical)*
   - **Issue:** `J4` connects `+12V in` and `-12V in` straight to `U1`, `U2`, `C3`, and `C4`. Reversing an unkeyed Eurorack power cable swaps `+12 V` and `-12 V`, immediately destroying `TL074`/`TL072` and violently reverse-biasing `C3`/`C4`. Furthermore, `4.7 µF` provides minimal energy storage and ripple filtering.
   - **Fix (Recommended Series Schottky Topology):**
     - Use a **keyed/shrouded `2×5`-pin Doepfer A-100 Eurorack IDC header (`J4`)**: pins 1–2 = `-12V_in` (red stripe), pins 3–8 = `GND`, pins 9–10 = `+12V_in`.
     - Add **series Schottky diodes (`D4`, `D5`: `1N5819` THT or `SS14`/`B140` SMD, `40 V / 1 A`)**:
       - **`D4`** on `+12V`: **Anode** to `J4.+12V_in`, **Cathode** to protected `+12V` rail.
       - **`D5`** on `-12V`: **Cathode** to `J4.-12V_in`, **Anode** to protected `-12V` rail.
       - *Voltage Rating Check:* Do **not** use `20 V` `1N5817` diodes—on a reversed cable or hot-plug against charged rails, reverse voltage across `D4`/`D5` can approach `24 V` (`+12 V` to `-12 V`), so `≥ 30–40 V` reverse rating is mandatory.
     - **Critical Placement Rule:** Connect `C3`, `C4`, `C5`–`C8`, and all IC/bias circuitry **downstream** of `D4`/`D5` on the protected `+12V`/`-12V` rails (never on raw `J4` pins) so a reversed cable draws **zero fault current** and never reverse-biases `C3`/`C4`. Forward drop is only `~0.25–0.35 V` at `< 20 mA` (`±11.65–11.75 V`, negligible headroom impact).
     - *Optional Post-Diode RC Filter:* If additional PSU ripple rejection is desired, insert `10 Ω` (`0.25 W`) series resistors *after* `D4`/`D5` before `C3`/`C4` (`f_c = 339 Hz` with `47 µF`; `< 0.2 V` drop at normal load, and never exposed to `12 V` fault voltage).
     - *Alternative (Zero Static Drop — PTC + Shunt Clamps):* Place **`100–200 mA` (`≥ 30 V`) resettable PTC polyfuses** (e.g., `MF-MSMF010`) in series with `+12V_in`/`-12V_in`, followed by reverse-biased **`1N5819`/`SS14` shunt clamp diodes** (`+12V` cathode / `GND` anode; `GND` cathode / `-12V` anode). **Warning:** Never pair a standard `1/4 W` `10 Ω` resistor with shunt clamp diodes—under a reversed `12 V` rail, `P = 12² / 10 = 14.4 W` burns out the resistor immediately; note also that PTC + shunt clamps momentarily draw heavy fault current from the Eurorack bus PSU until the PTC trips.
     - **Upgrade Bulk Capacitors (`C3`, `C4`):** Replace `4.7 µF` (unrated) with **`22 µF–47 µF, ≥ 35 V`** (preferably `50 V`) aluminum electrolytics downstream of `D4`/`D5` near `J4` (`C3`: `+` to `+12V`, `-` to `GND`; `C4`: `+` to `GND`, `-` to `-12V`).

3. **Consolidate Op-Amp ICs to `2× TL074` & Terminate Unused Op-Amp Channels** *(Medium)*
   - **IC Consolidation:** Using `1× TL074 + 1× TL072` splits the IC BOM into two line items while leaving zero spare channels to fix Stage 4 (`D3` deadband) or Stage 5 (`OFFSET` loading). Switching to **`2× TL074`** consolidates the IC BOM to one part number at virtually identical cost and provides **2 extra op-amp channels (`U2C`, `U2D`)**—enough for an **active precision peak detector** (IMP-03) and an **`OFFSET` wiper buffer** (IMP-05). For lower DC offset (`~1 mV` typ vs `3–10 mV`), rail-to-rail output (`±11.8 V` vs `±10.5 V`), and immunity to classic JFET phase reversal near `-12 V`, consider pin-compatible **`TL074H`** or **`OPA4172`**.
   - **Mandatory Unused Op-Amp Termination (`U2C`, `U2D`):**
     - Whenever `2× TL074` leaves spare channels unused (e.g., both `U2C` and `U2D` if building the baseline 6-stage schematic without active upgrades, or `U2D` if only one spare channel is consumed by an upgrade such as §2.5.1 Option B), **never leave inputs floating or outputs tied to rails/GND**.
     - Wire every unused `TL074` channel as a **unity-gain voltage follower biased to `GND` (`0 V`, exact mid-rail of `±12 V`)**:
       - **If `U2C` is unused:** Connect **Pin 10 (`+` input) → `GND`**; connect **Pin 9 (`-` input) → Pin 8 (`OUT`)**; leave Pin 8 connected *only* to Pin 9 (no external load).
       - **If `U2D` is unused:** Connect **Pin 12 (`+` input) → `GND`**; connect **Pin 13 (`-` input) → Pin 14 (`OUT`)**; leave Pin 14 connected *only* to Pin 13 (no external load).
     - **Common Termination Errors to Avoid:**
       - *Floating inputs:* High-Z JFET inputs pick up hum/switching fields and oscillate rail-to-rail, injecting noise onto `±12 V`.
       - *Tying both `+` and `-` to `GND` (open-loop):* `TL074`'s `±3–10 mV` `V_os` is multiplied by open-loop gain (`~200,000`), slamming the output into `±10.5 V` saturation and increasing thermal/quiescent stress.
       - *Tying `+` to `-12 V` (`V-`):* Violates classic `TL074` lower input common-mode limit (`~V- + 4 V = -8 V`), causing phase reversal and excess supply current.
       - *Tying `OUT` to `GND` or `±12 V`:* Directly shorts the op-amp output stage (`~25 mA` fault current).

---

### 2.2 Stage 1 — Input Impedance, Coupling, Gain Floor Limiting, Gain Range & Input Protection (`J1`, `C1`, `R1`, `R2`, `RV1`, `U1A`)

1. **Raise Input Impedance from `9.9 kΩ` to `100 kΩ` Standard** *(High)*
   - **Issue:** `U1A` is wired as an inverting amplifier with `R2 = 10 kΩ` to virtual ground, setting passband input impedance to `Z_in = R1 || R2 = 1 MΩ || 10 kΩ = 9.90 kΩ`. This is `10×` lower than the `100 kΩ` Eurorack standard and heavily loads passive attenuators/mixers, guitar pickups, piezos, and high-Z vintage synths. Even a module with a `1 kΩ` output resistor loses `9.1%` (`-0.83 dB`) into `9.9 kΩ`.
   - **Fix (Two Clean Options):**
     - **Option A (Pre-buffer or non-inverting preamp with input level pot):** Route `J1` (`IN`) → `C1` (`1 µF` film) → `RV1` (`A100K` wired as an input voltage divider to `GND`, giving a constant **`100 kΩ` `Z_in`**) → `U1A` (`+`), configured as a fixed non-inverting gain stage (e.g., `1 + 91 kΩ / 10 kΩ = 10.1×`, or `1 + 39 kΩ / 10 kΩ = 4.9×` for Eurorack levels). Because `C1` blocks DC and `U1A(+)` draws picoamps, `RV1` carries zero DC bias current (scratch-free), and a wiper lift safely defaults to `0 V` if a `1 MΩ` bleed resistor ties `U1A(+)` to `GND`.
     - **Option B (Unity input buffer):** If keeping the inverting `U1A` topology (`R2 = 10 kΩ`, `RV1` in feedback), insert a non-inverting unity-gain buffer (`100 kΩ` bias resistor `R1` to `GND`) right after `C1`.
   - **Secondary Benefit on `C1`:** Raising `Z_in` from `9.9 kΩ` to `100 kΩ` lets `C1` shrink from `4.7 µF` to **`470 nF`** (`f_c = 3.39 Hz`) or **`1 µF`** (`f_c = 1.59 Hz`), allowing compact, low-distortion polyester/polypropylene film caps instead of bulky `4.7 µF` film parts or microphonic high-K MLCCs.

2. **Avoid High-K MLCCs (`X5R`/`X7R`) on `C1` & Ground `J1` Normal Pin** *(High)*
   - **Issue:**
     - `EnvelopeFollower.md` §2.1 lists `MLCC` as acceptable for `C1` (`4.7 µF`). High-capacitance Class-II MLCCs (`X5R`/`X7R`) exhibit strong voltage-coefficient harmonic distortion and piezoelectric microphonics—knocking the front panel or PCB can trigger false envelopes. Use a **film capacitor** (`470 nF–1 µF` with `100 kΩ` `Z_in`, or `4.7 µF` film/nichicon-MUSE bipolar if keeping `10 kΩ`).
     - `J1` is a 2-terminal jack (`IN_TIP` floats before `C1` when unplugged). At high `GAIN`, an open `IN_TIP` acts as a 50/60 Hz capacitive antenna coupled across `C1`, causing hum and false `LED1`/`OUT` chatter.
   - **Fix:** Use a 3-pin switched jack (e.g., Thonkiconn `WQP-PJ398SM`) for `J1` with its **switched normal pin connected to `GND`**, muting `IN_TIP` whenever no cable is patched.

3. **Add Gain Floor Limiting (`R_gain_min`) & Tame Excessive Max Gain (`0–27.7×`)** *(High)*
   - **Issue (No Gain Floor Limit on `RV1`):** In the baseline inverting preamp (`U1A`), `RV1` (`100 kΩ`) connects directly between `PREAMP_SUM` (`U1A-`) and `PREAMP_OUT`, allowing feedback resistance `R_f` to drop to **`0 Ω` (`0×` dead mute)** at full CCW. This causes three issues:
     1. Turning `GAIN` to minimum completely silences the module (`0 V` output even with `±5 V`–`±10 V` Eurorack inputs), creating a dead zone at low knob angles (compounded by `D3`'s `0.6 V` threshold if passive).
     2. At `0 Ω`, `U1A`'s summing node (`PREAMP_SUM`) is shorted directly to `PREAMP_OUT` across only the potentiometer's erratic mechanical end-stop/wiper resistance (`~10–500 Ω`), bypassing any parallel feedback compensation capacitor across `RV1` and tying panel-wiring capacitance directly across the op-amp.
     3. Unlike `Release` (`R10 = 10 kΩ`) and corrected `ATK` (`R9`), Stage 1 lacks a deterministic minimum-resistance floor resistor.
   - **Fix (Gain Floor Limiting):**
     - **Inverting Topology (Baseline / Option B):** Insert a fixed series resistor **`R_gain_min` (`R24`)** in series with `RV1` (`PREAMP_SUM` → `R_gain_min` → `RV1` → `PREAMP_OUT`), and place the `15 pF` stability cap across the combined **`R_gain_min + RV1`** network so compensation remains active across the full knob sweep:
       - **`R_gain_min = 4.7 kΩ` (General Eurorack default):** Sets **`0.47×` to `10.47×`** preamp gain (`Noise Gain = 1.47×–11.47×`; `15 pF` pole = `2.26 MHz` at min, `101 kHz` at max). A `0.47×` floor keeps hot `±10 V` Eurorack oscillators/LFOs unclipped through `U1A` and `U1C` (`0.47 × 1.1 = 0.52×` before `OUT`), while preventing `0×` mute and keeping `≥ 4.7 kΩ` around `U1A`.
       - **`R_gain_min = 10 kΩ` (Unity-floor option for `±5 V` audio):** Sets **`1.00×` to `11.00×`** preamp gain (`Noise Gain = 2.00×–12.00×`; `15 pF` pole = `1.06 MHz` at min, `96.5 kHz` at max), guaranteeing at least unity gain at minimum rotation.
     - **Non-Inverting + Input Divider Option (Option A):** The fixed op-amp stage (`1 + R_f / R_g`) already maintains a safe `≥ 1×` feedback floor; to also prevent `0×` output mute at CCW, insert a bottom floor resistor `R_div_min` (e.g., `10 kΩ`) between `RV1` Pin 1 (CCW) and `GND` (giving a `1/11 = 0.091×` attenuation floor × `4.9×–10.1×` stage gain = `0.45×–0.92×` minimum system gain). Omit `R_div_min` only if deliberate `0×` mute at CCW is desired.
   - **Issue (Excessive Max Gain `0–27.7×`):** Total gain `OUT / |V_in|` spans up to `27.7×` (`0–10×` preamp × `1.1×` FWR × `2.25–2.52×` output). For standard `10 Vpp` (`±5 V`) Eurorack audio, `U1D` (`OUT`) clips at `+10.5 V` once `V_env = 4.67 V` (`V_preamp ≈ 4.8 V`), which happens at **`R_GAIN ≈ 9.6 kΩ` (`< 10%` rotation of a linear `B100K` pot!)**, and `U1A` clips at `21%` rotation. Thus `80–90%` of a linear `GAIN` knob is permanently clipped on modular signals.
   - **Fix (Max Gain & Taper):**
     - Reduce Stage 5 (`U1D`) excess gain from `2.25–2.52×` down to **`1.0×`** (see IMP-05), raising the unclipped threshold to `|V_in| = 5 V → 2×` preamp gain (`20%` linear).
     - Use an **audio/logarithmic (`A100K`) potentiometer** for `RV1` (`GAIN`) so `0.47×–2×` occupies the lower half of rotation for hot Eurorack signals while `2×–10.5×` occupies the upper half for quiet line/guitar sources.

4. **Add Feedback Compensation (`15 pF` C0G) & Input ESD / Over-Voltage Clamping** *(Medium / High)*
   - **Issue:** `PREAMP_SUM` (`U1A-`) sees up to `100+ kΩ` feedback (`R_gain_min + RV1`). With panel-mounted pot wiring or PCB stray capacitance (`~10 pF` on `U1A-`), the feedback pole (`~150 kHz`) erodes phase margin against `TL074`'s `3 MHz` GBW, risking ultrasonic peaking or oscillation at high `GAIN`. Also, hot-plugged cables, `±15 V` gear, or ESD transients pass straight across `C1` into `U1A`.
   - **Fix:**
     - Add a **`15 pF` (`10–22 pF`) C0G/NP0** capacitor across **`R_gain_min + RV1`** (`f_p ≈ 96.5–101.3 kHz` at max gain, `-0.17` to `-0.18 dB` at `20 kHz`) to guarantee stability across all knob positions.
     - Add a **`1 kΩ` series current-limiting resistor** at `J1.Tip` followed by **dual rail-clamp diodes (`BAV99` `70 V` low-leakage silicon, or `BAS70-04` `70 V` Schottky)** to `+12V` and `-12V` **before `C1`** (limiting external over-voltage/ESD surge currents while avoiding warm `BAT54S` Schottky reverse-leakage drift across high-Z `100 kΩ`/`1 MΩ` nodes after `C1`, and preventing negative swings below `-8 V` from triggering `TL07x` phase reversal in non-inverting Option A).

---

### 2.3 Stages 2 & 3 — Precision Full-Wave Rectifier Accuracy & DC Offset Hygiene (`U1B`, `U1C`, `R3`–`R8`)

1. **Match `R3`–`R7` Tolerances to Prevent Asymmetric Half-Wave Ripple** *(Medium)*
   - **Issue:** In the inverting-summing FWR, positive half-cycles compute `V_fwr(+) = R8 · (R6/(R3·R7) - 1/(R4+R5)) · V_preamp`, whereas negative half-cycles compute `V_fwr(-) = R8 / (R4+R5) · |V_preamp|`. Because the positive path subtracts `1/20 kΩ` from `1/10 kΩ`, tolerance errors on `R3`, `R6`, and `R7` carry **`2×` sensitivity**:
     - With **`1%` resistors**, worst-case positive vs. negative half-wave gain mismatch is **`+8.16% / -7.84%`**.
     - With **`5%` resistors**, worst-case mismatch reaches **`+44.3% / -36.3%`**.
     - Asymmetric half-waves inject fundamental-frequency (`1× f_in`) ripple into `C2` instead of cancelling it to `2× f_in`, doubling low-frequency ripple.
   - **Fix:** Use **`0.1%` thin-film resistors** (or hand-matched `1%` resistors from the same tape reel) for `R3, R4, R5, R6, R7`. Optionally replace `R4 + R5` (`10 kΩ + 10 kΩ`) with a single `20.0 kΩ` resistor (and set `R8 = 20.0 kΩ` if exact `1.00×` FWR gain is preferred over `1.10×`).

2. **Add Inter-Stage AC Coupling (`1 µF` + `100 kΩ`) Before the Rectifier When Removing `D3` Deadband** *(Medium)*
   - **Issue:** `TL074` has a typical `V_os` of `3 mV` and a maximum of **`10 mV`**. At max `GAIN` (`100 kΩ / 10 kΩ`), `U1A`'s non-inverting noise gain is `1 + 100k/10k = 11×`, producing up to **`±110 mV`** DC offset at `PREAMP_OUT`—which, combined with `U1B` (`2 × V_os`) and `U1C` (`4.3 × V_os`) offsets, reaches **`~186 mV` worst-case DC error at `FWR_OUT`**. In the baseline circuit, `D3`'s `~0.6 V` forward drop accidentally hides this offset. **If you upgrade Stage 4 to an active deadband-free peak detector without blocking `U1A`'s DC offset, `OUT` will exhibit a permanent false baseline offset of up to `~0.42 V` (`2.25 × 186 mV`) that shifts as `GAIN` is turned!**
   - **Fix:** Insert a **`1 µF` film capacitor + `100 kΩ` resistor to `GND`** (`f_c = 1.59 Hz`) between `PREAMP_OUT` and the rectifier inputs (`R3`/`R4`), or use low-offset op-amps (`TL074H` / `OPA4172`), before removing `D3`'s deadband. *(Skip the inter-stage capacitor only if DC-coupled CV envelope following is explicitly desired alongside precision low-offset op-amps.)*

---

### 2.4 Stage 4 — Attack / Release Detector & Peak Diode Redesign (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)

1. **Move `R9` (`1 kΩ`) *Before* `C2` (`ENV_CAP`) to Stop `U1C` Current Spikes & `9.1%` Amplitude Sag** *(Critical)*
   - **Issue:** In `EnvelopeFollower.webp`, `R9` (`1 kΩ`) is placed *after* `C2` (between `ENV_CAP` and `ENV_NODE`), leaving **zero series resistance** between `D3` and `C2` when `RV2` (`ATK`) is at `0 Ω`:
     1. `U1C` sees `C2` (`1 µF`) as a dead capacitive short during attack peaks, hitting `TL074` short-circuit current limit (`~20–40 mA`), causing `±12 V` rail glitches, and destroying `U1C`'s phase margin.
     2. Meanwhile, `R9` (`1 kΩ`) forms a voltage divider with `R10 + RV3` (`10 kΩ` min to `1.01 MΩ` max), attenuating `ENV_NODE` to **`90.9%` (`-9.1%`)** at minimum `Release` (`0 Ω`) vs `99.9%` at max `Release`.
   - **Fix:** Move `R9` (reduced to **`220 Ω–470 Ω`** for `< 0.5 ms` min attack, or kept at `1 kΩ` for `1 ms` min attack) **between `D3.K` / `RV2` and `ENV_CAP` (`C2`)**, and connect `ENV_CAP` directly to `ENV_NODE` (`R10`, `U1D+`, `R20`). This limits `U1C` peak current (`≤ 25 mA` at `470 Ω`, `≤ 12 mA` at `1 kΩ`), stabilizes `U1C`, and eliminates the `9.1%` release-dependent amplitude sag.

2. **Eliminate the `83.6%` `ATK` vs. `Release` Divider Attenuation** *(Critical)*
   - **Issue:** Because `R10 + RV3` (`10 kΩ` min) remains permanently in parallel with `C2` while `RV2` (`0–50 kΩ`) charges `C2`, `RV2` and `R9 + R10 + RV3` form a severe voltage divider whenever `ATK` is turned up and `Release` is turned down:
     - At `ATK = 50 kΩ`, `Release = 0 Ω` (`11 kΩ` total shunt): steady-state divider at `ENV_CAP` is `11k / 61k = 0.180`, and with `R9`/`R10` (`0.909`) at `ENV_NODE`, total DC transfer drops to **`0.164` (`-15.7 dB`, an `83.6%` voltage loss!)**, while effective `τ_atk` collapses from `50 ms` to `(50k || 11k) × 1 µF = 9.02 ms`.
     - Even at `ATK = 50 kΩ`, `Release = 100 kΩ` (`10%` pot rotation), `ENV_NODE` loses **`31.7%`** of DC amplitude (and even more on AC peaks).
   - **Fix (Two Approaches):**
     - **Drop-In Passive Re-Scaling (Keeps Exact RC Topology):** Move `R9 = 470 Ω` before `C2` and ensure `R10 ≫ RV2_max` (e.g., `C2 = 470 nF` film, `RV2 = 10 kΩ` -> `τ_atk = 0.22–4.9 ms`; `R10 = 47 kΩ`, `RV3 = 1 MΩ` -> `τ_rel = 22.1–492 ms`, raising worst-case divider from `16.4%` to **`81.8%`**; or `C2 = 1 µF`, `RV2 = 25 kΩ`, `R10 = 100 kΩ` -> `τ_atk = 0.47–25.5 ms`, `τ_rel = 100–1100 ms`, worst-case `79.7%`).
     - **Active Op-Amp Slew/Peak Isolation (Best Performance):** Use a dedicated op-amp peak detector/slew limiter with separate attack and release diode paths (`D_atk` charges via `RV2`, `D_rel` discharges via `RV3`), completely eliminating attack/release interaction (`100%` peak transfer at all knob settings). *(Note: an op-amp slew limiter produces linear rather than exponential release unless gated back to `GND`.)*

3. **Put `D3` Inside an Active Feedback Loop (Eliminate `0.6 V` Deadband) & Fix `C2` Dielectric Spec** *(High)*
   - **Issue:**
     - `D3` (`1N4148`) outside `U1C`'s loop causes a **`~0.6 V` dead zone** (`-2 mV/°C` thermal drift, nonlinear low-level tracking). Replacing `D3` directly with a power Schottky (`1N5819`) is a **trap**: `1N5819` reverse leakage (`50–500+ µA`) is larger than `C2`'s `1 MΩ` release current (`~5–10 µA`), destroying long release decays! Even small-signal Schottkys (`BAT54`) leak `~1–2 µA` when warm inside a synth case.
     - `EnvelopeFollower.md` §7.3 permits **`X7R` ceramic** for `C2` (`1 µF`). Under `5–10 V` DC envelope voltage, compact `X7R` MLCCs suffer **`30–60%` capacitance loss (DC bias derating)**, making `Release` up to `2×` faster at high signal levels than at low levels, plus piezo microphonics.
   - **Fix:**
     - **Active Precision Peak Detector (using 1 spare op-amp from `2× TL074`):** Drive `U_det(+)` from `FWR_OUT`, connect `U_det` output → `D3` (`1N4148`, anode to `U_det` out) → `R9_pre` (`470 Ω`) → `RV2` → `C2`; feed back from a unity-buffered copy of `C2` (e.g., `U_env_buf` output) through `10 kΩ` to `U_det(-)`; and place an anti-saturation clamp diode `D_clamp` (`1N4148`, anode at `U_det(-)`, cathode at `U_det` output). This eliminates the `0.6 V` diode drop, keeps `U_det` out of negative rail saturation, and preserves `1N4148`'s `< 25 nA` low reverse leakage on `C2`. *(Pair with inter-stage AC coupling from §2.3.2 / IMP-07.)*
     - **Capacitor Type for `C2`:** Mandate a **polyester/polypropylene box film capacitor** (e.g., WIMA `MKS2` / `FKP2`, `50–63 V`) or `C0G/NP0` ceramic—**do not use `X7R`/`X5R` MLCCs**. Keep PCB pads around `ENV_CAP` / `ENV_NODE` clean of flux residue to prevent parallel leakage at `1 MΩ`.

4. **Change `RV3` (`Release`) & `RV2` (`ATK`) to Audio/Log Taper (`A1M`, `A50K`)** *(Medium)*
   - **Issue:** With a linear `B1M` pot on `RV3` (`1 µF`, `R10 = 10 kΩ`), `0%` = `11 ms`, `10%` = `111 ms`, and `100%` = `1011 ms`. All snappy percussive release times (`11–100 ms`) are crammed into the **bottom `9%` of knob rotation**.
   - **Fix:** Specify an **audio/logarithmic (`A1M`) potentiometer** for `RV3` (`Release`) and optionally `A50K` for `RV2` (`ATK`), verifying CW/CCW lug wiring (`Short Pin 2+3` or `Pin 1+2` depending on taper direction) so fast times expand smoothly across the lower half of knob travel.

5. **Optional 2nd-Order Ripple Filter (`30–40 Hz`)** *(Low / Optional)*
   - **Issue:** With `50 Hz` bass audio (`100 Hz` full-wave pulses, `10 ms` period) and fast `Release` (`11 ms`), a 1st-order RC detector drops by `1 - e^(-10/11) ≈ 60%` between half-cycles, outputting massive `100 Hz` audio ripple instead of a smooth CV.
   - **Fix:** Adding a buffered 2nd-order Sallen-Key low-pass filter (`f_c ≈ 30–40 Hz`) after `ENV_NODE` gives `-12 dB/oct` ripple rejection while preserving fast transient response.

---

### 2.5 Stages 5 & 6 — Output Stage Gain, `OFFSET` Isolation, Polarity & Rail Ripple (`U1D`, `U2A`, `R11`–`R19`, `RV4`)

1. **Decouple `OFFSET` (`RV4`) Impedance from Envelope Signal Gain (`12%` Gain Shift)** *(High)*
   - **Issue:** `RV4` (`100 kΩ`) feeds `R13` (`10 kΩ`) directly into `U1D(-)`. As `RV4` sweeps from center (`R_pot_th = 30.0 kΩ`) to either end (`9.17 kΩ`), `U1D`'s envelope gain shifts by **`12%`** (`2.25×` at center → `2.52×` at ends).
   - **Fix (Two Clean Options):**
     - **Option A (Spare Op-Amp Buffer from `2× TL074`):** Insert a unity-gain follower (`U_off_buf`) between `RV4` wiper and `R13`. `U1D` then sees a constant source resistance regardless of knob angle.
     - **Option B (Zero Extra Op-Amps — Reorder Stages 5 & 6 into Inverting Virtual-Ground Summing):** Let `U1D` be a unity buffer on `ENV_NODE` (`+1.000×`), feed that buffered signal and `RV4` wiper (via `R13`) into `U2A`'s **virtual-ground inverting summer** to produce `INV_OUT`, and invert `INV_OUT` through a second unity inverter to produce `OUT`. Because `U2A(-)` is a virtual ground, **`RV4` wiper impedance has `0%` effect on envelope signal gain** (using `RV4 = 10 kΩ` + `R11 = R12 = 1 kΩ` keeps offset tracking linear within `< 3%` as well).

2. **Lower Output Stage Gain from `2.25–2.52×` to `1.0×`** *(High)*
   - **Issue:** Multiplying `V_env` by `2.25–2.52×` in `U1D` forces `OUT` into `TL074` saturation (`+10.5 V`) when `V_env` is only **`4.17–4.67 V`**. This wastes over half of `U1C`/`C2`'s `0–10 V` headroom, doubles the relative severity of `D3`'s `0.6 V` deadband (`0.6 / 4.67 = 12.8%`), and starves `LED1` (which taps `ENV_NODE` pre-`U1D`).
   - **Fix:** With buffered `OFFSET`, remove `R14` and configure Stage 5 for **`1.0×` envelope gain** (e.g., via the inverting summer + unity inverter above, or a `10 kΩ / 10 kΩ` balanced difference/summing network), letting `C2` operate across a clean `0–10 V` swing while keeping `GAIN` in Stage 1 (`U1A`) / Stage 3 (`U1C`).

3. **Fix `OFFSET` Knob Polarity (`CW = Positive OUT`) & Reject `±12 V` PSU Ripple** *(High)*
   - **Issue:**
     - As wired in `EnvelopeFollower.md` §5, turning `RV4` **clockwise shifts `OUT` negative (`-5.22 V`)**, which is counter-intuitive.
     - `RV4` sits directly across `±12 V` (`R11`/`R12`), giving poor power-supply ripple rejection: `50 mVpp` switching noise on `+12 V` alone injects `6.25 mVpp` (at center) up to `23.9 mVpp` (at the `+12 V` end) directly onto `OUT` and `INV_OUT` (and rail voltage asymmetry shifts `0 V` center).
   - **Fix:**
     - Swap `RV4.1` and `RV4.3` (or use an even number of inversions as in Option B above) so **clockwise = positive `OUT`**. Consider a **center-detent `B100K`** pot so `0 V` offset is easy to locate by feel (and tune `R11`/`R12` for `±5 V` if bipolar centering of `0–10 V` is preferred, or `±10 V` for full-range CV ducking).
     - Add **`10 µF` + `100 nF` decoupling** from `OFFSET_WIPER` to `GND` (and/or RC-filter `OFFSET_TOP` and `OFFSET_BOT` via `100 Ω` + `10 µF` to `GND`) to strip `±12 V` PSU noise from the CV outputs.

4. **Eurorack Output Protection (`R16`, `R19`, Clamp Diodes & Jack Normal Pins)** *(High)*
   - **Short-Circuit & Capacitive-Load Isolation:** Retain **`R16 = R19 = 1 kΩ`** (standard Eurorack output impedance) rather than dropping blindly to `470 Ω`. At `±10.5 V`, `1 kΩ` limits short-to-`GND` current to `10.5 mA` (safely inside `TL07x` continuous short-circuit limits), isolates `U1D`/`U2A` from capacitive patch cables, and incurs only `-0.99%` drop into `100 kΩ` inputs. If zero voltage droop into legacy `10 kΩ` inputs (`-9.09%` loss at `1 kΩ`) is desired, place `1 kΩ` **inside the op-amp feedback loop** (`U_out` → `1 kΩ` → `J_tip`, `10 kΩ` DC feedback from `J_tip`, `47 pF` direct high-frequency feedback from `U_out` to `-`) instead of reducing series fault impedance (`470 Ω` drives `47.9 mA` and `1.08 W` under opposite-rail faults).
   - **Power Rating for Output-to-Output Faults:** In Eurorack patching, another module's output (`+12 V` or `+10.5 V`) is frequently patched accidentally into `OUT` (`J2`) or `INV_OUT` (`J3`) while our output sits at `-10.5 V`. Across `1 kΩ`, `ΔV = 21–22.5 V` (`21–22.5 mA`) dissipates **`0.44–0.51 W` continuously**—overheating standard `0603` (`0.1 W`), `0805` (`0.125 W`), or `1/4 W` (`0.25 W`) parts. Specify **`R16`, `R19` ≥ 0.5 W** (e.g., `1206`/`2010` surge-rated SMD or `0.5 W` THT), or implement each `1 kΩ` output leg as **`2× 499 Ω` (`0.25 W` each) in series** (sharing fault dissipation while providing a natural midpoint for clamp diodes).
   - **ESD & External Over-Voltage Clamping:** Add dual rail-clamp diodes (**`BAT54S`** `30 V` Schottky—preferred on low-Z outputs because its `~0.35 V` clamp engages before `U1D`/`U2A` internal ESD diodes—or **`BAS70-04` / `BAV99` `70 V`** for wider reverse margin across the `24 V` rail span) at **`ENV_OUT` and `INV_OUT_RAW` behind `R16`/`R19`** (or at the midpoint of split `499 Ω + 499 Ω` output resistors), clamping to `+12V` and `-12V`. Having `≥ 499 Ω–1 kΩ` in front of the clamp diodes limits external `+48 V` phantom or `±8 kV` ESD transients safely (`< 36 mA` into `1 kΩ` at `+48 V`) and protects `U1D` (Pin 14) / `U2A` (Pin 1) even when unpowered.
   - **Switched Jack Normal Pin Safety (`J2`, `J3`):** If using 3-pin switched jacks (e.g., `WQP-PJ398SM`) for `J2` (`OUT`) and `J3` (`INV_OUT`), leave their switched **normal pins strictly No-Connect (`NC`)** (never grounded, which shorts `OUT`/`INV_OUT` through `1 kΩ` when unplugged).

---

### 2.6 Stage 7 — Active `LED1` Transconductance Driver (`U2B`, `R20`–`R23`, `LED1`)

- **Issue in Baseline Design:**
  - The passive `-2.79 V` cathode bias (`R22 = 10 kΩ`, `R23 = 33 kΩ`) + `R21 = 22 kΩ` yields `R_total = 29.67 kΩ`.
  - When `OUT` reaches unclipped saturation (`+10.5 V`, corresponding to `V_env = 4.67 V`), `LED1` receives only **`0.191 mA`** (Red, `1.8 V`) or **`0.150 mA`** (Blue/White, `3.0 V`)—extremely dim under normal lighting (the `0.34–0.37 mA` value in `EnvelopeFollower.md` §4.6 assumes `V_env = 10 V`, where `OUT` is heavily clipped).
  - Worse, at **`V_env = 0 V` (idle)**, a standard `1.8 V` red LED passes **`~33 µA`** (`~40 µA` at low-current `V_f ≈ 1.6 V`), causing a **faint permanent glow even with no signal**, while `R22`+`R23` constantly bleeds `0.28 mA` from `-12 V` and couples `-12 V` rail variations into LED brightness.
- **Fix — Rewire `U2B` as an Active Voltage-to-Current (`V-to-I`) LED Driver:**
  - Connect `ENV_NODE` → `U2B(+)` (retain `R20 = 10 kΩ` optionally as input protection).
  - Connect `U2B` output → `LED1` **Anode**.
  - Connect `LED1` **Cathode** → `U2B(-)` AND a single current-setting resistor **`R_set`** (`1.5 kΩ` or `2.2 kΩ`) to **`GND`**.
  - Connect a **`1N4148` protection diode (`D_led_prot`)** anti-parallel across `LED1` (**Anode** to `U2B(-)`, **Cathode** to `U2B` output) so any slight negative offset (`V_env < 0`) clamps reverse voltage across `LED1` to `-0.6 V` instead of slamming `U2B` to `-12 V` and exceeding typical `5 V` LED reverse-breakdown ratings.
  - **Result:**
    - `I_LED = V_env / R_set` (`0.00 mA` at `0 V` — **zero idle glow**; with `R_set = 1.5 kΩ`, `3.11 mA` at `4.67 V` and `6.67 mA` at `10 V`).
    - Completely **independent of LED forward voltage `V_f`** (works equally well with red, yellow, green, blue, or white LEDs).
    - Eliminates `R22`, `R23`, and `-12 V` quiescent divider bleed.

---

### 2.7 Optional Eurorack Feature Enhancements

- **AC / DC Input Coupling Switch:** Adding a panel SPST switch in parallel with `C1` lets users toggle between AC-coupled audio envelope following (`f_c ≈ 1.6–3.4 Hz`) and DC-coupled CV/LFO slew-or-rectification duties.
- **Gate / Trigger Extractor Output:** Comparing `ENV_NODE` against a fixed (`~0.5–1 V`) or variable `THRESHOLD` voltage (with hysteresis, e.g., `100 kΩ` / `10 MΩ`) yields a clean `0/+10 V` (or `0/+5 V`) **Gate output** whenever audio is present.

---

## 3. Eurorack Hardware Protection Summary

The table below consolidates all recommended Eurorack electrical protections (extending the baseline reference designators from [`EnvelopeFollower.md`](./EnvelopeFollower.md) cleanly from `R24`/`C5`/`D4` onward):

| Protection Domain | Added / Modified Components | Pin-to-Pin / Net Wiring | Fault / Failure Mode Mitigated |
|---|---|---|---|
| **Reverse-Polarity Power Supply** | Keyed `2×5` IDC `J4`; `D4`, `D5` (`1N5819` / `SS14`, `40 V / 1 A`); `C3`, `C4` (`22–47 µF, ≥ 35 V`) | `D4`: `J4.+12V_in (A)` → `+12V (K)`<br>`D5`: `-12V (A)` → `J4.-12V_in (K)`<br>`C3`/`C4` and all ICs sit **downstream** of `D4`/`D5` *(or PTC + shunt clamp alternative)* | Swapped `±12 V` cable destroys `U1`/`U2` and explodes `C3`/`C4`; `40 V` rating handles `24 V` rail-to-rail reverse bias |
| **Local IC Decoupling** | `C5`, `C6`, `C7`, `C8` (`4× 100 nF, 50 V X7R/C0G`) | `U1`: `C5` (`Pin 4 → GND`), `C6` (`Pin 11 → GND`)<br>`U2 (TL072)`: `C7` (`Pin 8 → GND`), `C8` (`Pin 4 → GND`)<br>`U2 (TL074)`: `C7` (`Pin 4 → GND`), `C8` (`Pin 11 → GND`) | Rail droop, ground bounce, and high-frequency `TL07x` oscillation during `C2` charging pulses (`< 3–5 mm` from pins) |
| **Gain Floor Limiting** *(+ Input ESD)* | `R24` / `R_gain_min` (`4.7 kΩ` or `10 kΩ`); `15 pF` C0G comp; *(Input: `R25 = 1 kΩ`, `D6 = BAV99`/`BAS70-04`, `J1` normal → `GND`)* | `PREAMP_SUM` → `R24` → `RV1` → `PREAMP_OUT` (`15 pF` across `R24 + RV1`); *(Input: `J1.Tip` → `R25` → `D6` clamp to `±12V` → `C1`)* | Eliminates `0×` dead-mute & `0 Ω` feedback short across pot hop-off resistance (`0.47×` or `1.0×` min gain); stops ESD & floating-jack hum |
| **Output Protection** | `R16`, `R19` (`1 kΩ ≥ 0.5 W` or `2× 499 Ω / 0.25 W`); `D7`, `D8` (`BAT54S` / `BAS70-04` / `BAV99`); `J2`/`J3` switched jacks | `ENV_OUT` (`D7` to `±12V`) → `R16` → `J2.Tip`<br>`INV_OUT_RAW` (`D8` to `±12V`) → `R19` → `J3.Tip`<br>`J2`/`J3` normal pins strictly `NC` | Short-to-`GND` (`≤ 10.5 mA`), capacitive-cable oscillation, continuous opposite-rail output-to-output patching (`~0.5 W`), `±8 kV` ESD, `+48 V` / unpowered back-feed |
| **Unused Op-Amp Termination** | Any spare `TL074` channels (`U2C`, `U2D` when consolidating to `2× TL074`) | `U2C`: `Pin 10 (+) → GND`, `Pin 9 (-) → Pin 8 (OUT)`<br>`U2D`: `Pin 12 (+) → GND`, `Pin 13 (-) → Pin 14 (OUT)` | Floating-input rail-banging, open-loop `V_os` saturation, `-12 V` common-mode phase reversal, and output short-circuiting |

---

## 4. Minor Analytical Gaps Noted in `EnvelopeFollower.md`

While reviewing [`EnvelopeFollower.md`](./EnvelopeFollower.md) against [`EnvelopeFollower.webp`](./EnvelopeFollower.webp), the following documentation points were found to be slightly incomplete or optimistic:

1. **Line 19 (`Total Gain: 0× to ~27.7×`):** Omits the `9.1%` (`0.909×`) attenuation across `R9`/`R10` when `Release = 0 Ω`, `D3`'s `~0.6 V` forward threshold subtraction prior to `U1D`, and the `ATK`/`Release` divider loss (down to `0.164×` at `ATK = 50 kΩ`, `Release = 0 Ω`).
2. **Line 153 (`adjustable from 0 (mute) to -10`):** Reflects the unprotected `0 Ω` feedback path when `RV1` is at CCW (`0×` gain floor), without a minimum feedback series resistor (`R_gain_min`) to bound minimum gain and keep feedback compensation active.
3. **Line 184 (`τ_atk ≈ R_ATK × 1 µF = < 1 ms to 50 ms`):** Neglects the parallel discharge path `(R9 + R10 + R_REL)`. At `Release = 0 Ω` and `ATK = 50 kΩ`, effective `τ_atk` is `(50 kΩ || 11 kΩ) × 1 µF = 9.02 ms` and peak voltage is capped at `16.4%` of `V_fwr - V_f`.
4. **Line 215 (`At V_env = +10 V, I_LED ≈ 0.34–0.37 mA`):** Because `U1D` (`2.25–2.52×`) clips `OUT` at `+10.5 V` when `V_env` reaches `4.17–4.67 V`, normal unclipped operation limits `I_LED` to **`0.15–0.19 mA`** (with `~33 µA` idle bleed at `0 V` on low-`V_f` red LEDs).
5. **Line 286 (`C2`: "film or C0G/X7R ceramic"):** Should specifically **exclude `X7R`** for `C2`, since DC-bias capacitance derating (`30–60%` loss at `5–10 V`) distorts release decay linearity.
