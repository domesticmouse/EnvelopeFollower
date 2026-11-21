# Envelope Follower — Circuit Review & Suggested Improvements

Review of [EnvelopeFollower.md](./EnvelopeFollower.md) (cross-checked against [EnvelopeFollower.webp](./EnvelopeFollower.webp)).

The baseline circuit is a functional Eurorack analog envelope follower (`±12 V`, 6 op-amp channels), and several practical notes (local decoupling, reverse-polarity protection, pot tapers) are already acknowledged in `EnvelopeFollower.md`. However, detailed analysis reveals **Eurorack safety and protection omissions** (no schematic/BOM reverse-polarity power protection, no local IC decoupling caps, no input-stage gain floor limiting on `GAIN`, insufficient fault wattage and missing ESD/overvoltage clamps on `OUT`/`INV_OUT`, and no termination rule for unused op-amps when consolidating to `2× TL074`), **signal-path defects** (unwanted clipping, diode deadband, current-limiting saturation on fast attack, `OFFSET`-dependent gain modulation, poor rail rejection, weak LED drive), **Eurorack interface limitations**, and **four technical errors in `EnvelopeFollower.md`** (reversed `ATK`/`Release` pot wiring, reversed `GAIN` taper recommendation, an incorrect divider ratio, and an output jack switch-contact hazard).

---

## Summary Priority Matrix

| # | Area / Component(s) | Severity | Core Issue | Recommended Fix |
|---|---|---|---|---|
| 1 | `J4`, `D5`, `D6`, `C3`, `C4` | **High** | Power reverse-polarity protection is absent from schematic/BOM/netlist; `4.7 µF` bulk caps are undersized | Use shrouded 2×5 IDC header `J4` with series `40 V` Schottky diodes (`D5`, `D6`: `1N5819`/`SS14`) or PTC+shunt clamps; raise `C3`/`C4` to `22–47 µF` (`≥ 35 V`) |
| 2 | `U1`, `U2`, `C5`–`C8` | **High** | Local IC decoupling capacitors are absent from schematic/BOM/netlist, risking high-frequency oscillation | Add `4× 100 nF` (`50 V` X7R) bypass caps (`C5`–`C8`) within `≤ 5 mm` of `U1` and `U2` `Vcc+`/`Vcc-` pins to `GND` |
| 3 | `U1A`, `R2`, `RV1` (`GAIN`), `R24` | **High** | `RV1` reaches `0 Ω` feedback, causing a `0×` (`-∞ dB`) dead zone, `0 Ω` wiper strap across `U1A`, and wiper-lift pops | Add series gain-floor resistor `R24` (`4.7 kΩ` for `0.47×` floor or `10 kΩ` for `1.0×` floor at `R2 = 10 kΩ`; `47–100 kΩ` if scaled to `100 kΩ`) |
| 4 | `J2`, `J3`, `R16`, `R19`, `D7`, `D8` | **High** | `1 kΩ` `0603`/`0805`/`0.25 W` output resistors overheat (`0.44–0.58 W`) on opposing-rail patch faults; no output ESD/OV clamps; `TN` hazard | Upgrade `R16`/`R19` (`1 kΩ`) to `≥ 0.5 W`; add `BAT54S`/`BAV99` clamps (`D7`, `D8`) at `V_OUT_PRE`/`V_INV_PRE`; leave `J2.TN`/`J3.TN` `NC` |
| 5 | `U2C`, `U2D` (spare op-amps) | **High** | Consolidating to `2× TL074` leaves up to 2 spare op-amps unaddressed; floating pins oscillate and inject die/rail noise | Terminate every unallocated channel as a `GND`-referenced unity-gain follower (`+` to `GND`, `-` tied to `Out`, `Out` unloaded) |
| 6 | `U1C`, `D3`, `RV2` (`ATK`), `R25` | **High** | `0 Ω` min `ATK` shorts `U1C` into `1 µF` (`C2`), causing current-limiting spikes & capacitive instability | Add `R25` (`220 Ω–470 Ω`, `330 Ω` nominal) min attack resistor in series with `RV2` |
| 7 | `RV2`, `RV3`, `RV1` (`ATK`, `Release`, `GAIN`) | **High (Doc/Wiring)** | `EnvelopeFollower.md` wires `RV2`/`RV3` backwards (`CW = shorter time`) and suggests `C100K` for `RV1` | Swap outer pot terminals on `RV2` & `RV3` (`Pin 1` to signal, `Pins 2+3` to cap/GND); use `A100K` (or `B100K`) for `RV1` |
| 8 | `U1D`, `RV4` (`OFFSET`), `R11`–`R15` | **High** | `U1D` gain (`2.25×–2.52×`) clips early above `~4.2 V`, shifts `+12%` with `OFFSET`, and couples `±12 V` noise | Lower `U1D` gain (`1.0×–1.5×`) and buffer `RV4` wiper using spare `U2C` (or lower divider impedance + raise `R13`) |
| 9 | `D3` (`1N4148`) | **Medium–High** | `D3` outside feedback loop causes `~0.6 V` deadband, current-dependent peak error, and thermal drift | Replace with Schottky (`BAT54`/`BAT85`/`1N5711`) or move into an active clamped super-diode peak-detector loop |
| 10 | `R9`, `R10` (`ENV_NODE`) | **Medium (Circuit + Doc)** | `R9` (`1 kΩ`) + `R10` (`10 kΩ`) attenuate `ENV_NODE` by `9.1%` at min release (doc miscalculates as `11/12`) | Move series isolation resistor solely to `U1D +` input (matching `R20`), or drop `R9` from discharge path |
| 11 | `J1`, `C1`, `R1`, `R2` (`IN`), `D9` | **Medium** | `~9.9 kΩ` input impedance loads passive/Eurorack sources; `4.7 µF` non-polarized `C1` is bulky/microphonic; no ESD clamp | Scale `R2` to `100 kΩ` (`RV1 = 470 kΩ`/`1 MΩ`, `R24 = 47–100 kΩ`, `10–22 pF` comp cap) and `C1` to `470 nF–1 µF` film; add `D9` clamp |
| 12 | `U2B`, `D4`, `R21`–`R23` (`LED`) | **Medium** | `0.17–0.34 mA` LED drive is very dim for standard LEDs yet leaks `~37 µA` idle glow on red LEDs | Use active feedback LED current driver (`D4` + `R_sense` + anti-parallel `1N4148`), or tune `R21` down to `2.2–4.7 kΩ` |
| 13 | `C2` (`1 µF`) | **Medium** | Allowing X7R MLCC causes `30–60%` DC-bias capacitance loss and microphonic false triggers | Specify polyester/polypropylene film (`1 µF`, `50 V`) only (no MLCC) |
| 14 | `U1`, `U2`, `R8` | **Low–Medium** | Mixed IC BOM (`TL074`+`TL072`), `1.1×` rectifier gain (`R8 = 22 kΩ`), early `U1B` clipping | Consolidate to `2× TL074` (terminate unused channels per §1.5), use `20 kΩ` (`2× 10 kΩ`) for `R8`, consider `TL074H` |

---

## 1. Eurorack Protections & Critical Circuit Improvements

### 1.1 Power Supply Reverse-Polarity Protection (`J4`, `D5`, `D6`, `C3`, `C4`)
* **Current behavior:** `EnvelopeFollower.md` (§3.1) leaves reverse-polarity protection out of the schematic, BOM, and netlist, relying on raw `+12V in` / `-12V in` inputs with `4.7 µF` electrolytics (`C3`, `C4`).
* **Why this is a hazard in Eurorack:**
  * Unshrouded `2×5` headers or mis-crimped third-party ribbon cables allow plugging the power cable in 180° backwards, swapping `+12V_IN` and `-12V_IN` across `GND` (pins 3–8). Without protection, reversed rails immediately destroy `U1`, `U2`, and polarized electrolytics `C3`/`C4`.
  * `4.7 µF` (`C3`, `C4`) provides minimal bulk energy storage on noisy Eurorack buses shared with digital modules.
* **Recommended implementation (incorporate into canonical schematic, BOM, and netlist):**
  1. **Shrouded Keyed Eurorack Header (`J4`):** Specify a **10-pin (`2×5`, 2.54 mm pitch) shrouded/keyed box header** following Doepfer A-100 pinout:
     * Pins 1–2: `-12V_IN` (print an explicit **`-12V / RED`** stripe bar on PCB silkscreen)
     * Pins 3–8: `GND`
     * Pins 9–10: `+12V_IN`
  2. **Primary Method — Series `40 V` Schottky Diodes (`D5`, `D6`):**
     * Add **`1N5819`** (`DO-41` THT) or **`SS14`** (`SMA` SMD) / **`1N5819WS`** (`SOD-323` SMD) — rated **`≥ 40 V` $V_{\text{RRM}}$, `1 A`**:
       * **`D5` (`+12 V` rail):** Anode (`Pin 2`) $\rightarrow$ `+12V_IN` (`J4.9–10`), Cathode (`Pin 1`) $\rightarrow$ protected **`+12V`** rail.
       * **`D6` (`-12 V` rail):** Anode (`Pin 2`) $\rightarrow$ protected **`-12V`** rail, Cathode (`Pin 1`) $\rightarrow$ `-12V_IN` (`J4.1–2`).
     * **Why `≥ 40 V` $V_{\text{RRM}}$ is mandatory:** During a reversed cable plug-in or hot swap against charged bulk caps, a diode can see up to `24 V` (`|+12 V - (-12 V)|`) reverse bias; `40 V` parts (`1N5819`/`SS14`/`1N5819WS`) provide `> 1.6×` derating margin (avoid `20 V` `1N5817`).
     * **Drop & headroom check:** At this module's `~8–15 mA` operating draw, `D5`/`D6` drop only **`~0.28–0.35 V`**, giving protected rails of **`±11.65 V`** (`TL074` still swings `±10.1 V`, and `TL074H` swings `±11.45 V`) while drawing **`0 mA`** with zero bus short if plugged in backwards.
  3. **Zero-Drop Alternative — Resettable PTC Fuses + Shunt Clamps:**
     * Place **`50 mA–100 mA` hold PTC fuses** (`F1`, `F2`, `≥ 30 V`, optionally paired with `10 Ω` flameproof surge resistors) in series with `+12V_IN` and `-12V_IN`, followed by reverse-biased shunt Schottky diodes **`D5`/`D6` (`1N5819`/`SS14`) to `GND`** (`+12V` rail: `K` to `+12V`, `A` to `GND`; `-12V` rail: `A` to `-12V`, `K` to `GND`).
     * *Trade-off:* Avoids the `0.35 V` diode drop, **but** draws a brief high-current short on the rack PSU (`~100–300 ms` trip time) and allows `~0.35–0.5 V` transient reverse polarity during a fault. Series `40 V` Schottky diodes (`D5`, `D6`) are cleaner and preferred for this low-current analog module.
  4. **Bulk Filtering Upgrade (`C3`, `C4`):**
     * Increase `C3` and `C4` from `4.7 µF` to **`22 µF – 47 µF` (`≥ 35 V` radial electrolytic)** placed immediately downstream of `D5`/`D6` near `J4`:
       * `C3`: **`+` to `+12V`**, **`-` to `GND`**
       * `C4`: **`+` to `GND`**, **`-` to `-12V`**

### 1.2 Local Decoupling Capacitors for ICs (`C5`–`C8`, `U1`, `U2`)
* **Current behavior:** `EnvelopeFollower.md` (§3.1, §5.3) mentions `100 nF` decoupling only as an optional build note and omits them from the schematic, BOM, and netlist.
* **Why this is critical:** Relying solely on distant `C3`/`C4` bulk electrolytics leaves trace inductance on the `±12V` supply rails. When `U1C` charges `C2` (`1 µF`) during fast attacks or `U1D`/`U2A` drive cable capacitance, supply impedance spikes can trigger ultrasonic op-amp oscillation and cross-channel coupling.
* **Recommended implementation:**
  * Add **`4× 100 nF` (`0.1 µF`) `50 V` `X7R` ceramic MLCC capacitors** (`C5`–`C8`, minimum `≥ 25 V` rated for `12 V` rail derating — do **not** use `16 V` parts; `0603`/`0805` SMD or `5 mm` radial THT):
    * **`C5`**: `+12V` to `GND` directly at **`U1` `Vcc+` (`Pin 4`)**
    * **`C6`**: `-12V` to `GND` directly at **`U1` `Vcc-` (`Pin 11`)**
    * **`C7`**: `+12V` to `GND` directly at **`U2` `Vcc+`** (**`Pin 4`** if `2× TL074`, or **`Pin 8`** if `TL072`)
    * **`C8`**: `-12V` to `GND` directly at **`U2` `Vcc-`** (**`Pin 11`** if `2× TL074`, or **`Pin 4`** if `TL072`)
  * *(If building with `3× TL072`, add `6× 100 nF` — one `+12V` and one `-12V` bypass cap per IC.)*
* **PCB layout rule:** Place `C5`–`C8` within **`≤ 3–5 mm`** of each IC's power pins, routing supply traces through the capacitor pads into the IC pins and returning the ground pads directly to the `GND` plane via short wide traces or dedicated vias.

### 1.3 Gain Floor Limiting on Input Stage (`U1A`, `R2`, `RV1`, `R24`)
* **Current behavior:** `RV1` (`100 kΩ` `GAIN` pot wired as a rheostat) is the sole feedback impedance across `U1A` (`-` pin 2 to `Out` pin 1). At the counter-clockwise (CCW) stop (`RV1 = 0 Ω`), closed-loop gain drops to $A_{v1} = -0\,\Omega / 10\,\text{k}\Omega = 0\times$ (`-∞ dB`).
* **Why this is a problem:**
  1. **Unusable `0×` dead zone:** At and near the CCW stop, `0×` gain combined with `D3`'s forward drop (`~0.3–0.6 V`) leaves the bottom portion of the `GAIN` knob completely dead, making the module appear unresponsive even with healthy Eurorack signals patched in.
  2. **`0 Ω` feedback strap & wiper-bounce jumps:** At `RV1 = 0 Ω`, `U1A` output drives the inverting summing node directly through a mechanical wiper at `0 Ω` while sinking/sourcing the entire input current (`V_in / R2`). Momentary wiper lift/scratchiness near the stop opens feedback from `0 Ω` to `100 kΩ`, causing abrupt `+20 dB` gain spikes/clicks. It also shorts any parallel feedback compensation capacitor (`C_comp`) to `0 Ω`.
* **Recommended implementation:** Add a fixed **gain-floor resistor (`R24`)** in series with `RV1` (`GAIN`) on the inverting-input side (`U1A_IN_M`, `U1A` pin 2 $\rightarrow$ `R24` $\rightarrow$ `RV1.1`; `RV1.2 + RV1.3` $\rightarrow$ `V_AMP`, `U1A` pin 1) to isolate pot/wire stray capacitance from the sensitive summing junction:
  $$A_{v1,\min} = -\frac{R_{24}}{R_2}, \qquad A_{v1,\max} = -\frac{R_{24} + R_{V1}}{R_2}$$
  * **Original `R2 = 10 kΩ`, `RV1 = 100 kΩ` stage:**
    * **`R24 = 4.7 kΩ` (1%):** Establishes a **`0.47×` (`-6.56 dB`)** minimum gain floor (`0.47×` to `10.47×`). Hot `±10 V` (`20 Vpp`) Eurorack signals attenuate safely to `4.7 V` peak before `U1C`/`U1D` (preventing downstream rail clipping even at `1.5×` `U1D` gain), while standard `±5 V` audio (`2.35 V` rectified, `~3.5 V` out) still triggers cleanly above threshold.
    * *Alternative **`R24 = 10 kΩ` (1%):** Sets a **`1.00×` (`0 dB`)** unity gain floor (`1.0×` to `11.0×`) and reuses the `10 kΩ` BOM value (best when `U1D` gain is set to `1.0×` or inputs stay within `±5 V`–`±8 V`).*
  * **Scaled `100 kΩ` input-impedance stage (§3.2 Option A: `R2 = 100 kΩ`, `RV1 = 470 kΩ` or `1 MΩ`):**
    * Scale proportionally to **`R24 = 47 kΩ`** (`0.47×` floor) or **`100 kΩ`** (`1.0×` unity floor).
    * Place the optional ultrasonic compensation cap **`C_comp` (`10 pF–22 pF` `C0G` for `1 MΩ`, or `22 pF–47 pF` `C0G` for `470 kΩ`/`100 kΩ`)** across the *entire* feedback branch (`U1A -` to `U1A Out`, spanning `R24 + RV1`) so `C_comp` never gets shorted at `0 Ω` and keeps $-3\text{ dB}$ roll-off above audio (`~15.9 kHz` at `1 MΩ + 10 pF`; `~33.9 kHz` at `100 kΩ + 47 pF`).
  * *(If true `0×` mute is ever desired at full CCW, implement it as a passive input attenuator before a fixed-gain stage rather than running an op-amp feedback rheostat down to `0 Ω`.)*

### 1.4 Output Protection (`OUT` / `J2`, `INV_OUT` / `J3`, `R16`, `R19`, `D7`, `D8`)
* **Current behavior:** `U1D.14` (`V_OUT_PRE`) and `U2A.1` (`V_INV_PRE`) drive `J2.Tip` (`OUT_TIP`) and `J3.Tip` (`INV_OUT_TIP`) through `R16 = 1 kΩ` and `R19 = 1 kΩ` (`1/4 W` THT or `0603`/`0805` SMD in `EnvelopeFollower.md`), with no ESD/overvoltage clamps and ambiguous switched-jack symbols in `EnvelopeFollower.webp`.
* **Why this is inadequate for Eurorack:**
  1. **Output-to-output patch fault overheating:** If `OUT` driven to `+10.5 V` is accidentally patched to another Eurorack module driving `-10.5 V` to `-12 V` (a common patching mistake), `R16` or `R19` (`1 kΩ`) sees `21–24 V` continuously and dissipates:
     $$P_{\text{fault}} = \frac{(21\text{–}24\,\text{V})^2}{1000\,\Omega} = 0.44\text{–}0.58\,\text{W}$$
     This exceeds `0603` (`0.1 W`), `0805` (`0.125 W`), and `1/4 W` (`0.25 W`) resistor ratings by `2×–5×`.
  2. **Unclamped ESD & external overvoltage transients:** Human-body ESD strikes (`±8–15 kV`) or hot-plugged inductive/high-voltage transients on panel jacks pass straight across `R16`/`R19` into `U1D` and `U2A` outputs without external clamping.
  3. **Switched-jack `TN` shorting hazard:** Wiring `J2.TN` or `J3.TN` to `GND` (as drawn in `EnvelopeFollower.webp`) continuously shorts `R16`/`R19` to `GND` whenever unplugged.
* **Recommended implementation:**
  1. **Upgrade `R16` and `R19` (`1 kΩ`) Power Rating to `≥ 0.5 W`:**
     * Use **`1/2 W` metal-film THT**, **`1210`/`2010` SMD (`0.5 W`–`0.75 W`)**, or **`2× 510 Ω` (`0805`/`1206`, `0.25 W` each) in series** (or `2× 2 kΩ` `0.25 W` in parallel) to survive continuous output-to-opposing-rail patching indefinitely while preserving standard `1 kΩ` Eurorack output impedance (`1%` accuracy into `100 kΩ` inputs) and capacitive cable isolation (`~1–2 nF`).
     * *(Optional stabilization: add `47 pF–100 pF` `C0G` feedback caps across `R15` and `R18`.)*
  2. **Add Dual Output Clamping Diodes (`D7`, `D8`: `BAT54S` or `BAV99`, SOT-23):**
     * Place one dual series-diode package on the **op-amp side** of each `1 kΩ` series resistor (`D7` on `V_OUT_PRE`, `D8` on `V_INV_PRE`):
       * **Pin 1 (`A1`) $\rightarrow$ `-12V`**
       * **Pin 2 (`K2`) $\rightarrow$ `+12V`**
       * **Pin 3 (`COM`) $\rightarrow$ `V_OUT_PRE` (`U1D.14`/`R16.1`)** for `D7`; **`V_INV_PRE` (`U2A.1`/`R19.1`)** for `D8`.
     * *Why op-amp side of `R16`/`R19`:* `R16`/`R19` (`1 kΩ`) limits ESD and external overvoltage fault current into the clamping diodes (`(24 - 12)/1k = 12 mA`), while normal `±10.5 V` signals remain inside the `±11.65 V` rails so the diodes stay reverse-biased with zero signal distortion.
     * *Component notes:* **`BAV99`** (`70 V / 215 mA`, `~1.5 pF`, `< 2.5 µA` leakage) or **`BAT54S`** (`30 V / 200 mA` Schottky, lower clamping `Vf`) both work well. **KiCad schematic caution:** KiCad's built-in `Diode:BAV99` symbol labels pins `1/3` as `"K"` and `2` as `"A"`, even though electrical connections are `1 = A1`, `2 = K2`, `3 = COM` — verify footprint pin numbers `1/2/3` (`Pin 1 -> -12V`, `Pin 2 -> +12V`, `Pin 3 -> signal`)! *(If sustained `> +20 V` DC faults on both outputs simultaneously must be absorbed without lifting the `D5`-blocked `+12V` rail, place bidirectional `15 V` TVS diodes such as `SMAJ15CA` / `PESD15VL1BA` from `OUT_TIP`/`INV_OUT_TIP` to `GND` instead of, or in addition to, rail clamps.)*
  3. **Switched-Jack Normalled Pins (`TN`):**
     * Explicitly leave **`J2.TN` (`OUT`)** and **`J3.TN` (`INV_OUT`)** **unconnected (`NC`)**; tie `TN` to `GND` **only** on **`J1` (`IN`)**.

### 1.5 Unused Op-Amp Termination (`U2C`, `U2D` / Any Spare Channel)
* **Where unused channels occur:** Consolidating from `TL074 + TL072` to **`2× TL074`** (§3.5) provides 8 op-amp channels for a 6-channel baseline circuit, leaving **`U2C` and `U2D`** spare (or leaving **`U2D`** spare if `U2C` is used to buffer `OFFSET` per §1.7). Any build using `1× TL074 + 2× TL072` also leaves 2 channels unused.
* **Why floating or wrongly tied pins fail:**
  * Leaving unused op-amp inputs floating (`NC`) lets high-Z JFET/CMOS inputs drift into noise pickup, rail banging, or MHz oscillation, adding `2–5 mA` of excess supply current, switching spikes on `±12V`, and thermal/substrate crosstalk into active stages (`U2A`, `U2B`).
  * **Common mistake to avoid:** Do **NOT** tie both `+` and `-` inputs to `GND` with `Out` floating. Because `TL074` has `±1–10 mV` input offset voltage ($V_{\text{os}}$), open-loop gain drives the output continuously into `+10.5 V` or `-10.5 V` saturation.
* **Proper `±12 V` Dual-Supply Termination (Unity-Gain Voltage Follower to `GND`):**
  * On a symmetric `±12 V` supply, `GND` (`0 V`) sits at exact mid-supply inside `TL074`/`TL074H`'s linear common-mode and output swing range. Configure every unused channel as a **unity-gain follower with `+` tied to `GND` and `-` tied directly to `Out`** (with `Out` driving no external load):
    * **`TL074` `U2C` (if unused):** `Pin 10 (+)` $\rightarrow$ `GND`; `Pin 9 (-)` $\rightarrow$ `Pin 8 (Out)`.
    * **`TL074` `U2D` (if unused):** `Pin 12 (+)` $\rightarrow$ `GND`; `Pin 13 (-)` $\rightarrow$ `Pin 14 (Out)`.
    * **`TL072` spare channel `U*B` (if applicable):** `Pin 5 (+)` $\rightarrow$ `GND`; `Pin 6 (-)` $\rightarrow$ `Pin 7 (Out)`.
  * *(Rule for partial adoption: If `U2C` is repurposed—for example, as the `OFFSET` unity buffer in §1.7—`U2D` must still be terminated via `Pin 12 -> GND`, `Pin 13 -> Pin 14`.)*

### 1.6 Add a Minimum Attack Current-Limiting Resistor in Series with `RV2` (`ATK`, `R25`)
* **Current behavior:** In §3.4 (`U1C Out` $\rightarrow$ `D3` $\rightarrow$ `RV2` $\rightarrow$ `C2`), when `RV2` (`ATK`) is turned to minimum (`0 Ω`), `U1C` drives `C2` (`1 µF` to `GND`) directly through `D3` (`1N4148`).
* **Why this is a problem:**
  1. **Op-amp short-circuit saturation & supply spikes:** During a fast input transient with `C2 = 0 V`, `U1C` immediately hits its internal short-circuit current limit (`~25–40 mA` for `TL074`) rather than achieving a true `0 ms` attack. That current surge draws sharp pulses from the `+12 V` rail into `GND`, injecting clicks/ripple into the `OFFSET` divider and audio stages.
  2. **Capacitive load instability:** While `D3` conducts, `U1C` sees a near-pure `1 µF` capacitive load to ground, eroding phase margin and risking high-frequency ringing or oscillation on `V_FWR`.
* **Suggested improvement:** Insert a fixed **`R25` (`220 Ω` to `470 Ω`, `330 Ω` nominal)** in series between `D3` cathode (`ATK_IN`) and `RV2.1` (`ATK`).
  * With `330 Ω`, minimum $\tau_{\text{atk}} = 330\,\Omega \times 1\,\mu\text{F} = 0.33\text{ ms}$ (still virtually instantaneous for audio/CV transients), while peak charging current is bounded below `~30 mA` (or `~20 mA` with `470 Ω`), keeping `U1C` inside linear drive and stable against capacitive oscillation.

### 1.7 Fix Output Stage Over-Gain (`2.25×–2.52×`), `OFFSET` Gain Modulation, & Poor Rail PSRR (`U1D`, `RV4`)
* **Current behavior:** `U1D` is wired as a non-inverting summing/gain stage with `R15 = 10 kΩ`, `R14 = 10 kΩ`, `R13 = 10 kΩ` fed by `RV4` (`100 kΩ` `OFFSET` across `R11 = 10 kΩ` to `+12 V` and `R12 = 10 kΩ` to `-12 V`). As `EnvelopeFollower.md` §3.5 derives, `U1D` has an envelope gain of `2.25×` at center (`R_th = 30 kΩ`) and `2.52×` at the extremes (`R_th = 9.17 kΩ`), with `±5.22 V` offset.
* **Why this is a problem:**
  1. **Severe early output clipping & LED mismatch:** Because `U1A` already provides up to `10×` gain and `U1C` adds `1.1×`, `U1D`'s `2.25×–2.52×` gain causes `OUT` and `INV_OUT` to hard-clip at `±10.5 V` (`TL07x` rail limit) whenever `ENV_NODE` exceeds just **`~4.2–4.6 V`** (with `OFFSET = 0 V`). Meanwhile, `U2B` (`LED`) taps `ENV_NODE` (which spans `0–10 V`), so `OUT` can be flat-topped in clipping while the `LED` still shows mid-scale headroom and keeps brightening.
  2. **Unintended `+12%` gain shift from the `OFFSET` knob:** Because `R13` (`10 kΩ`) is comparable to `RV4`'s wiper Thevenin impedance (`9.17 kΩ` to `30 kΩ`), turning `OFFSET` away from center increases signal gain from `2.25×` to `2.52×` (`+1.0 dB`) and warps the `OFFSET` knob response into an S-curve.
  3. **Direct `±12 V` power-rail noise coupling:** Because `OFFSET` derives its `±10 V` span straight from raw `±12 V` rails, power supply ripple, bus droop, or digital-module noise on `±12 V` feeds through `R11`/`RV4`/`R12`/`R13` to `OUT` and `INV_OUT` (up to `~0.48×` rail transfer at offset extremes).
* **Suggested improvements:**
  * **Drop `U1D` signal gain to `1.4×–1.5×` (or `1.0×`):** Remove `R14` (`10 kΩ` to `GND`) and set `R15 = 10 kΩ`, `R13 = 20 kΩ` (or `22 kΩ`). With a `±10 V` offset tap, signal gain drops to `1 + 10/20 = 1.50×` (allowing `ENV_NODE` up to `+7.0 V` before `U1D` reaches `+10.5 V`), while preserving the `±5.0 V` offset span (`∓10 V × 10/20`).
  * **Decouple `OFFSET` impedance from `U1D` gain:**
    * *Best fix (if consolidating to `2× TL074`, see §3.5):* Use spare op-amp **`U2C`** as a unity-gain voltage follower on `RV4` wiper (`OFFSET_WIPER` $\rightarrow$ `U2C.10 (+)`; `U2C.9 (-)` $\rightarrow$ `U2C.8 (Out)` $\rightarrow$ `R13`). That gives `0 Ω` source impedance into `R13`, eliminating the `12%` gain modulation and making `OFFSET` completely linear (remember to terminate remaining spare `U2D` per §1.5).
    * *Zero-IC-change alternative:* Lower the offset divider to `RV4 = 10 kΩ` and `R11 = R12 = 1 kΩ` (`R_th = 0.92–3.00 kΩ`) with `R14` removed and `R13 = 22 kΩ`, `R15 = 10 kΩ`. Gain becomes `1.40×` (center) to `1.436×` (ends) — reducing gain variation from `12%` down to `2.6%` — with a `±4.36 V` offset span (at `~2 mA` divider draw).
  * **Improve `OFFSET` rail rejection (optional):** Add small RC supply filtering (`100 Ω` + `10 µF`) or `±5.1 V` Zener / `LM4040-5.0` shunt references (with `R13 = R15 = 10 kΩ`, `R14` omitted, `RV4` buffered) so `OFFSET` stays rock-steady regardless of Eurorack `±12 V` supply tolerance, Schottky drop (`D5`/`D6`), or bus sag.

### 1.8 Eliminate or Reduce the `~0.6 V` Deadband Caused by `D3` (`1N4148`)
* **Current behavior:** `D3` sits outside `U1C`'s feedback loop (`U1C Out` $\rightarrow$ `D3` $\rightarrow$ `RV2` $\rightarrow$ `C2`).
* **Why this is a problem:**
  1. Signals whose rectified level $1.1\,|V_{\text{AMP}}|$ falls below `~0.6 V` produce **zero envelope voltage** (quiet passages and decay tails chop off prematurely unless `GAIN` is cranked high).
  2. $V_F$ of `1N4148` varies logarithmically with charging current (`~0.45 V` at microamp slow-attack currents vs. `~0.7 V` at milliamp fast-attack currents) and drifts at `-2 mV/°C`, causing peak amplitude to shift when adjusting `ATK`.
* **Suggested improvements:**
  * **Drop-in component upgrade:** Replace `D3` (`1N4148`) with a low-leakage **Schottky diode** such as **`BAT54` / `BAT85` / `1N5711`** ($V_F \approx 0.25\text{–}0.30\text{ V}$ at typical envelope currents), cutting the deadband roughly in half with no circuit topology changes. *(Verify reverse leakage at elevated temperature: `1N5711` / `BAT54` room-temp leakage is typically `< 0.1–1 µA`, negligible compared to `Release` discharge except at multi-second holds.)*
  * **Active super-diode peak detector (if using `2× TL074`, §3.5):** Use a spare op-amp (`U2D`) with `D3` inside the feedback loop plus a second clamp diode (`D_clamp`, anode to `U2D -`, cathode to `U2D Out`), with feedback taken from a buffer on `ENV_CAP`. The clamp diode prevents negative-rail saturation when `V_FWR < V_ENV`, eliminating the `0.6 V` threshold completely. *(Note: if `RV2` (`ATK`) is placed inside the active loop after `D3`, `U2D` drives to `+10.5 V` during attack, producing a faster, slew-linear attack rather than pure exponential RC charging; alternatively, keep a `~100 pF` local compensation cap across `D_clamp` for stability.)*

---

## 2. Errors & Inconsistencies Identified in `EnvelopeFollower.md`

The following issues are present in the text, BOM, or netlist of `EnvelopeFollower.md` itself and should be corrected before PCB layout or assembly:

1. **Reversed `ATK` (`RV2`) and `Release` (`RV3`) Potentiometer Wiring (§2.2, §3.4, §4):**
   * **What `EnvelopeFollower.md` specifies:**
     * `RV2` (`ATK`, line 172 & lines 226–227): *"Wire **Pin 1 (CCW) + Pin 2 (Wiper)** to `ENV_CAP` (`C2`/`R9`) and **Pin 3 (CW)** to `D3` cathode if you want **clockwise rotation = longer/slower attack time**."*
     * `RV3` (`Release`, line 179 & lines 215, 229): *"Connect **Pin 3 (CW)** to `R10`, and tie **Pin 1 (CCW) + Pin 2 (Wiper)** to `GND` so turning `Release` **clockwise increases decay/release time**."*
   * **Why it is backwards:** Under standard potentiometer pinout (`Pin 1 = CCW`, `Pin 2 = Wiper`, `Pin 3 = CW`), tying `Pin 1` to `Pin 2` puts the active resistance between `Pin 2` and `Pin 3` ($R_{23}$). At full **CCW**, the wiper sits at `Pin 1` so $R_{23} = R_{\text{total}}$ (**maximum** time constant); turning **CW** moves the wiper toward `Pin 3`, so $R_{23} \rightarrow 0\,\Omega$ (**minimum** time constant). Both halves of the parenthetical note on line 172 are also swapped.
   * **Correction:** For **CW = longer time**, wire **`Pin 1 (CCW)` to the upstream side** (`R25`/`D3.K` for `RV2`, `R10.2` for `RV3`) and tie **`Pin 2 (Wiper) + Pin 3 (CW)`** to the downstream side (`ENV_CAP` for `RV2`, `GND` for `RV3`). With `RV3` wired this way (`Pin 1` to `R10`, `Pins 2+3` to `GND`), an **`A1M` (audio/log)** taper pot actually expands the short `11 ms–150 ms` release range cleanly across the first half of rotation (`~10–15%` at 50%).

2. **Reversed Taper Recommendation for `GAIN` (`RV1`, §5.4 line 252):**
   * **What `EnvelopeFollower.md` specifies:** Recommends `B100K` (Linear) or `C100K` (Reverse-Log) with `Pin 1 (CCW)` to `U1A -` and `Pins 2+3` to `U1A Out`.
   * **Why `C100K` is backwards here:** With `Pin 1` to `-` and `Pins 2+3` to `Out`, resistance increases from `0 Ω` (CCW) to `100 kΩ` (CW). A reverse-log (`C100K`) pot reaches `~85%` (`85 kΩ`, gain `8.5×`) at 50% rotation, crowding nearly the entire `0×–8.5×` span into the bottom half of the knob.
   * **Correction:** Recommend **`A100K` (Audio/Log)** (which gives `~1.0–1.5×` gain around mid-rotation and smooth resolution over the critical `0.47×–3×` Eurorack range) or `B100K` (Linear).

3. **Divider Math Typo on `R9` / `R10` (§3.4 line 178):**
   * **What `EnvelopeFollower.md` states:** *"At minimum release (`0 Ω`), `R9` (`1 kΩ`) and `R10` (`10 kΩ`) form a slight `11 / 12 ≈ 0.917` divider on the envelope voltage."*
   * **Correction:** `R9` (`1 kΩ`) is the top series resistor (`ENV_CAP` $\rightarrow$ `ENV_NODE`) and `R10` (`10 kΩ`) is the bottom shunt resistor (`ENV_NODE` $\rightarrow$ `GND`). The actual unloaded divider ratio at `RV3 = 0 Ω` is:
     $$\frac{R_{10}}{R_9 + R_{10}} = \frac{10\,\text{k}\Omega}{1\,\text{k}\Omega + 10\,\text{k}\Omega} = \frac{10}{11} \approx 0.9091 \quad (-9.09\% \text{ attenuation})$$

4. **Switched-Jack Symbol Hazard on Outputs (`OUT`, `INV_OUT`) in `EnvelopeFollower.webp` vs. §2.2/§4:**
   * **Observation:** The source image `EnvelopeFollower.webp` draws identical tip-switched jack symbols with the normalled switch contact tied to `GND` on `IN`, `OUT`, and `INV_OUT`. While `EnvelopeFollower.md` safely maps only `Tip` and `Sleeve` on `J1`–`J3`, builders referencing `EnvelopeFollower.webp` with 3-pin Thonkiconn jacks (`WQP-PJ398SM`, pins `T`, `TN`, `S`) risk wiring `TN` to `GND` on `OUT`/`INV_OUT`. That shorts `R16`/`R19` (`1 kΩ`) to ground whenever unplugged, continuously sinking/sourcing up to `~10 mA` when `OFFSET != 0 V` and causing load-step transients when patching.
   * **Correction:** Explicitly document in §2.2/§5 to **leave `TN` unconnected (NC) on `OUT` (`J2`) and `INV_OUT` (`J3`)**, while tying `TN` to `GND` on `IN` (`J1`) to quiet the input when unpatched.

---

## 3. Moderate Performance, Eurorack Compatibility, & BOM Improvements

### 3.1 Eliminate the `R9` (`1 kΩ`) / `R10` (`10 kΩ`) Amplitude Drop at Short Release
* **Current behavior:** `C2` (`ENV_CAP`) passes through `R9` (`1 kΩ`) *before* branching to `R10`/`Release`, `U1D +`, and `R20` (`LED`). Consequently, turning `Release` to minimum drops the entire envelope amplitude at `ENV_NODE` by `9.1%` (`10/11`), making perceived output level depend on the `Release` knob position.
* **Suggested improvement:** Tap `R10` + `RV3` directly at `ENV_CAP` (`C2`) so there is no series divider ahead of `R10` (optionally raise `R10` to `11 kΩ` to preserve the `11 ms` minimum time constant). Place `R9` (`1 kΩ`–`10 kΩ`, matching `R20`) **solely** in series with `U1D +` (between `ENV_CAP` and `U1D.12`) so `U1D +` still gets current-limiting protection if `C2` discharges during power-off, with **zero** DC attenuation into `U1D`'s high-Z JFET input.

### 3.2 Raise Input Impedance to Eurorack Standard (`100 kΩ`), Downsize `C1`, & Add Input ESD Clamping
* **Current behavior:** `R2 = 10 kΩ` to `U1A` virtual ground yields $Z_{\text{in}} = R_1 \parallel R_2 \approx 9.9\text{ k}\Omega$ AC, requiring a large `4.7 µF` non-polarized input capacitor `C1` ($f_c \approx 3.42\text{ Hz}$). Also, `J1` has no ESD/overvoltage clamping beyond `C1`/`R2`.
* **Why this is a problem:**
  * Standard Eurorack audio/CV inputs are **`100 kΩ`**. A `9.9 kΩ` input drops `~9%` amplitude from a `1 kΩ`-output module (worse if passively multed) and severely loads high-impedance sources (electric guitars, passive piezo pickups, passive attenuators).
  * A `4.7 µF` film capacitor is bulky and expensive, whereas a `4.7 µF` MLCC introduces microphonics and voltage-dependent capacitance distortion, and a bipolar electrolytic adds leakage/ESR.
* **Suggested improvements:**
  * **Option A (Keep inverting `U1A` topology — immune to TL07x phase reversal):** Scale `R2` from `10 kΩ` to **`100 kΩ`** ($Z_{\text{in}} = 1\,\text{M}\Omega \parallel 100\,\text{k}\Omega = 90.9\,\text{k}\Omega$, or increase `R1` to `2.2 MΩ` for `95.7 kΩ`), scale `C1` down to **`470 nF` (`fc = 3.72 Hz`) or `1 µF` (`fc = 1.75 Hz`) polyester/polypropylene film (`≥ 50 V`)**, and scale `RV1` (`GAIN`) to **`470 kΩ` or `1 MΩ`** (`A500K` / `A1M`) with matching gain-floor resistor **`R24 = 47 kΩ` or `100 kΩ`** (§1.3). Add a **`10 pF–22 pF` (`1 MΩ` pot) or `22 pF–47 pF` (`470 kΩ` pot) `C0G` feedback capacitor** across `R24 + RV1` (`U1A -` to `U1A Out`) to prevent ultrasonic peaking without rolling off audio transients.
    * *Important advantage:* Keeping `U1A` inverting holds both inputs at `0 V` virtual ground, making `U1A` **immune to `TL07x` input phase reversal** even if `-12 V` is patched into `IN`.
  * **Option B (Add a dedicated input buffer if consolidating to `2× TL074`):** Put `C1` (`1 µF` film) $\rightarrow$ `R1` (`100 kΩ` to `GND`) $\rightarrow$ `10 kΩ` series resistor + dual clamp (`BAT54S`/`BAV99` to `±12 V`) into a unity buffer (using `TL074H` or clamping within `[-8 V, +12 V]`), then feed the original `R2 = 10 kΩ`, `RV1 = 100 kΩ`, `R24 = 4.7 kΩ–10 kΩ` `U1A` gain stage. That gives exact `100 kΩ` input impedance while keeping `RV1` at common `100 kΩ`. *(Remember to terminate any remaining spare channel per §1.5.)*
  * **Input ESD / hot-plug protection (`R26`, `D9`):** Add a small series surge resistor **`R26` (`100 Ω–1 kΩ`, `≥ 0.25 W`)** between `J1.Tip` and `C1` (or rely on `C1` + `100 kΩ` `R2`) and a **`BAT54S` / `BAV99` clamp (`D9`)** (`Pin 1 -> -12V`, `Pin 2 -> +12V`, `Pin 3 -> AC_IN` after `C1`/`R26` or buffer input resistor) to shunt ESD and hot-plug voltage surges safely to the decoupled rails.

### 3.3 Improve the `LED` Level Indicator Driver (`U2B`, `D4`, `R21`–`R23`)
* **Current behavior:** `U2B` buffers `ENV_NODE` (`0` to `+10 V`) through `R21 = 22 kΩ` into `D4`, whose cathode is pre-biased to `-2.79 V` (`R22 = 10 kΩ`, `R23 = 33 kΩ`, $R_{\text{th,K}} = 7.67\text{ k}\Omega$, total resistance `29.67 kΩ`).
* **Why this is a problem:**
  * LED current is tiny: only **`~0.17 mA` at `+5 V`** and **`~0.34 mA` at `+10 V`** for a green/blue LED ($V_F \approx 2.8\text{ V}$). Standard diffused LEDs are barely visible under studio/stage lighting at `< 0.5 mA`.
  * Conversely, because `-2.79 V` exceeds the turn-on voltage of red/amber LEDs ($V_F \approx 1.7\text{–}1.9\text{ V}$), a high-efficiency red LED draws **`~37 µA` continuously at `0 V` idle**, producing a faint permanent glow even with no signal!
  * `R22` + `R23` also continuously draw `0.28 mA` from `-12 V` even when idle.
* **Suggested improvements:**
  * **Best fix — Linear Feedback LED Current Driver (`0 mA` idle, color-independent):** Remove `R22` and `R23`, place `D4` inside `U2B`'s feedback loop (`U2B Out` $\rightarrow$ `D4` Anode; `D4` Cathode $\rightarrow$ `U2B -` and `R_sense = 2.2 kΩ–3.3 kΩ` to `GND`), and add a **`1N4148` anti-parallel clamp diode across `D4`** (anode to `D4.K`, cathode to `D4.A`).
    * At `ENV_NODE = 0 V`: `I_LED = 0.00 mA` (completely dark at idle for *any* LED color—red, green, blue, or white).
    * For `ENV_NODE > 0 V`: `U2B` automatically compensates `D4`'s exact $V_F$, driving linear current $I_{\text{LED}} = V_{\text{ENV}} / R_{\text{sense}}$ (`~1.5–2.3 mA` at `+5 V` with `2.2–3.3 kΩ`).
    * The anti-parallel `1N4148` prevents `U2B` input offset (`±3–10 mV`) from driving `U2B Out` to `-10.5 V` and exceeding the LED's typical `5 V` reverse-voltage rating ($V_R$).
  * **Minimal-change fix (keep original topology):** Lower `R21` from `22 kΩ` to **`2.2 kΩ–4.7 kΩ`** (increasing peak current to `~1–2 mA`) and adjust `R23` (`33 kΩ` for green/blue/white $V_F \approx 2.8\text{ V}$, or `47 kΩ–56 kΩ` for red/amber $V_F \approx 1.8\text{–}2.0\text{ V}$ so idle glow disappears).

### 3.4 Specify Non-MLCC Film Capacitor for `C2` (`1 µF`)
* **Current behavior:** BOM allows `"Film or X7R MLCC (drawn unpolarized; ≥ 25 V)"` for `C2` (`1 µF` envelope timing cap).
* **Why this is a problem:** Compact X7R MLCCs lose **`30%–60%` of effective capacitance at `10 V` DC bias**, making attack/release times change dynamically with signal amplitude. MLCCs are also piezoelectric (microphonic), so tapping the panel or turning adjacent pots can inject spurious spikes straight onto `ENV_CAP`.
* **Suggested improvement:** Require a **polyester or polypropylene film capacitor** (e.g., WIMA MKS2 `1 µF`, `50 V`/`63 V`) for `C2` (and `C1`).

### 3.5 Consolidate Op-Amps (`2× TL074`), Consider `TL074H`, & Match Rectifier Gain (`R8 = 20 kΩ`)
* **BOM consolidation & 2 free op-amps (`2× TL074` vs `TL074 + TL072`):**
  * Replacing `1× TL074` + `1× TL072` with **`2× TL074`** keeps the same 2-IC package count, eliminates one IC SKU from the BOM, and yields **two spare op-amps** (`U2C`, `U2D`) at negligible cost — which directly solves `OFFSET` buffering (§1.7) and either active peak detection (§1.8) or input buffering (§3.2). **Any remaining unallocated channel (`U2C`/`U2D`) must be terminated per §1.5** (`+` to `GND`, `-` to `Out`).
* **Modern drop-in op-amp upgrade (`TL074H` / `TL072H`):**
  * Standard `TL074`/`TL072` clips around `±10.5 V` on `±12 V` rails (`±10.1 V` behind series Schottky diodes) and suffers **phase reversal** if inputs drop below `~ -8 V`. Pin-compatible `TL074H` (TI CMOS JFET-replacement) offers rail-to-rail output (`±11.8 V`, recovering full headroom even with `D5`/`D6` drops and on `U1B` where `U1B_OUT = -V1 - V_D2` normally clips `~0.65 V` early!), zero phase reversal, lower input offset (`±1 mV` vs `±3–10 mV`), and `20 V/µs` slew rate.
* **Exact unity rectifier gain (`R8 = 20 kΩ` instead of `22 kΩ`):**
  * Using `22 kΩ` for `R8` creates an arbitrary `1.1×` gain (`V_FWR = +1.1·|V_AMP|`) and adds a separate `22 kΩ` BOM line. Replacing `R8` with **`20 kΩ` (or two `10 kΩ` 1% resistors in series**, matching `R6 + R7`) gives exact `1.00×` full-wave rectification (`V_FWR = |V_AMP|`), better matching/thermal tracking across `10 kΩ` resistors, and `10%` more headroom before `U1C` clips.

---

## 4. Eurorack Protection Delta Summary (BOM & Net Changes)

Summary of all protection additions and component upgrades relative to [EnvelopeFollower.md](./EnvelopeFollower.md):

| Ref | Protection Function | Recommended Value / Part | Package / Rating | Exact Net / Pin Connection |
|---|---|---|---|---|
| `J4` | Keyed Eurorack Power | `Conn_02x05_Odd_Even` shrouded IDC | `2.54 mm`, `≥ 1 A` | `1–2` = `-12V_IN` (`RED`), `3–8` = `GND`, `9–10` = `+12V_IN` |
| `D5` | `+12V` Reverse Polarity | `1N5819` / `SS14` / `1N5819WS` | `≥ 40 V`, `1 A` Schottky | `A (2)` $\rightarrow$ `+12V_IN`; `K (1)` $\rightarrow$ `+12V` |
| `D6` | `-12V` Reverse Polarity | `1N5819` / `SS14` / `1N5819WS` | `≥ 40 V`, `1 A` Schottky | `A (2)` $\rightarrow$ `-12V`; `K (1)` $\rightarrow$ `-12V_IN` |
| `C3`, `C4` | Bulk Rail Filtering | `22 µF–47 µF` electrolytic (upgrade from `4.7 µF`) | `≥ 35 V` | `C3`: `+` to `+12V`, `-` to `GND`; `C4`: `+` to `GND`, `-` to `-12V` |
| `C5`, `C6` | `U1` Local Decoupling | `100 nF` `X7R` MLCC (`2×`) | `50 V` (`≥ 25 V`) | `C5`: `U1.4 (+12V)`–`GND`; `C6`: `U1.11 (-12V)`–`GND` (`≤ 5 mm` to IC) |
| `C7`, `C8` | `U2` Local Decoupling | `100 nF` `X7R` MLCC (`2×`) | `50 V` (`≥ 25 V`) | `C7`: `U2.4` (`TL074`) / `U2.8` (`TL072`)–`GND`; `C8`: `U2.11` / `U2.4`–`GND` |
| `R24` | Gain Floor Limiting | `4.7 kΩ` (or `10 kΩ`) 1% *(scale `47–100 kΩ` if `R2 = 100 kΩ`)* | `0.1–0.25 W`, 1% | Series between `U1A -` (`U1A_IN_M`, pin 2) and `RV1.1` (`GAIN`) |
| `R25` | Attack Peak Current Limit | `330 Ω` (`220–470 Ω`) | `0.25 W`, 1% | Series between `D3.K` (`ATK_IN`) and `RV2.1` (`ATK`) |
| `R16`, `R19` | Output Short / Patch Fault | `1 kΩ` (upgrade wattage from `1/4 W` / `0603`) | **`≥ 0.5 W`** (`1/2 W` THT or `1210` SMD) | `R16`: `V_OUT_PRE`–`OUT_TIP`; `R19`: `V_INV_PRE`–`INV_OUT_TIP` |
| `D7`, `D8` | Output ESD / OV Clamp | `BAT54S` or `BAV99` (`2×` SOT-23) | `30–70 V`, `200 mA` | `Pin 1 (A1)` $\rightarrow$ `-12V`, `Pin 2 (K2)` $\rightarrow$ `+12V`, `Pin 3 (COM)` $\rightarrow$ `V_OUT_PRE` / `V_INV_PRE` |
| `D9` *(opt.)* | Input ESD / Surge Clamp | `BAT54S` or `BAV99` (+ `R26 = 100 Ω–1 kΩ` pre-`C1`) | `30–70 V`, `200 mA` | `Pin 1 (A1)` $\rightarrow$ `-12V`, `Pin 2 (K2)` $\rightarrow$ `+12V`, `Pin 3 (COM)` $\rightarrow$ `AC_IN` |
| `J1`–`J3` | Switched-Jack `TN` Safety | `WQP-PJ398SM` (`T`, `TN`, `S`) | 3.5 mm mono | `J1.TN` (`IN`) $\rightarrow$ `GND`; **`J2.TN` (`OUT`) & `J3.TN` (`INV_OUT`) $\rightarrow$ `NC`** |
| `U2C`, `U2D` | Unused Op-Amp Termination | Any unallocated `TL074` (`U2`) channels | Unity follower to `GND` | `U2C`: `10->GND, 9->8`; `U2D`: `12->GND, 13->14` *(for `TL072` spare: `5->GND, 6->7`)* |

---

## 5. Optional Functional Enhancements (Scope Expansion)

These additions are not flaws in the original design, but significantly expand Eurorack utility if panel space permits:

1. **AC / DC Input Coupling Switch (Bypass `C1`):** Adding an SPDT switch across `C1` (with `R1` adjusted appropriately) lets the module track ultra-slow LFOs, envelopes, or act as a precision full-wave rectifier / slew limiter for DC-coupled CV signals, while still switching to AC coupling (`~1.7–3.4 Hz`) for audio.
2. **Gate / Trigger Output with Threshold (Comparator):** Adding a comparator (or Schmitt trigger with a `THRESHOLD` pot or fixed `~1 V` threshold + hysteresis) driven from `ENV_NODE` provides a synchronized Gate output whenever an incoming audio transient exceeds threshold—one of the most requested companion outputs on Eurorack envelope followers (like the Doepfer A-119).
3. **Output Level / Attenuverter or `0–5 V` / `0–8 V` Scaling:** Including an output attenuator (or calibrating max `U1D` gain to `1.0×–1.5×`) makes it easier to drive `0–5 V` CV destinations without slamming into `±10.5 V` rail clipping.
