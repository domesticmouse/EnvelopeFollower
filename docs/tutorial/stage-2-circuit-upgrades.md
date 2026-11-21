# Stage 2: Sketch Extraction, Analog Critique & Eurorack Protections

Start from [Hagiwo's original post](https://note.com/solder_state/n/n110e9ba066b3?hl=en) and the hand-drawn reference schematic, [`EnvelopeFollower.webp`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.webp):

![Hagiwo's Original Envelope Follower Sketch](../images/EnvelopeFollower.webp)

Download the reference schematic into your project directory and verify that you fetched the raw image rather than an HTML wrapper page before asking your AI agent to inspect it:

```bash
curl -LO https://raw.githubusercontent.com/domesticmouse/EnvelopeFollower/main/EnvelopeFollower.webp
file EnvelopeFollower.webp
```

Confirm `file` reports a valid image (`RIFF ... Web/P image` or `JPEG image data`) rather than `HTML document`.

Rather than jumping straight from a raw sketch to a PCB in a single prompt, breaking the upfront circuit design into focused engineering prompts catches hidden analog bugs and hardens the module for Eurorack power and patching before locking down the JLCPCB BOM, audio walkthrough, test points, and silkscreen DFM rules in [Stage 3](stage-3-bom-and-dfm.md).

---

## Step 2.1: Extracting the Baseline Circuit from the Schematic

First, ask the agent to transcribe every net, component value, and diode orientation from the hand-drawn image into a clean Markdown specification (`EnvelopeFollower.md`).

### AI Agent Prompt

> *"Please review `EnvelopeFollower.webp`. I'd like to extract a Markdown description of the circuit that can be used to build a circuit, and save it to `EnvelopeFollower.md`."*

### Baseline 6-Op-Amp Topology

Reading the sketch left-to-right reveals **6 active op-amp stages** (`1× TL074` + `1× TL072`, `3× TL072`, or `2× TL074`), **23 fixed resistors** (`1× 1M`, `1× 33k`, `2× 22k`, `16× 10k`, `3× 1k`), **4 capacitors**, **4 potentiometers**, **3 signal diodes**, **1 LED**, **3 jacks**, and **1 power header (`J4`)**:

1. **Stage 0 — Power Supply Entry (`J4`, `C3`, `C4`)**: Bipolar $\pm 12\text{ V}$ entry bypassed only by bulk $4.7\,\mu\text{F}$ electrolytics (`C3` on `+12V` to `GND`, `C4` with `+` on `GND` and `-` on `-12V`).
2. **Stage 1 — AC-Coupled Variable-Gain Preamp (`U1A`)**: `J1` (`IN`) passes through non-polarized `C1` ($4.7\,\mu\text{F}$) and `R1` ($1\text{ M}\Omega$ pulldown) into an inverting amplifier (`R2` $= 10\text{ k}\Omega$, feedback rheostat `RV1` $= 100\text{ k}\Omega$, $0\times$ to $-10\times$ gain).
3. **Stages 2 & 3 — Precision Full-Wave Rectifier (`U1B`, `U1C`)**: `U1B` forms an active half-wave rectifier (`R3`, `R6` $= 10\text{ k}\Omega$, `D1`, `D2` $= \text{1N4148}$), summed by `U1C` (`R7` $= 10\text{ k}\Omega$ half-wave leg vs. `R4 + R5` $= 20\text{ k}\Omega$ direct feedforward leg, `R8` $= 22\text{ k}\Omega$ feedback for $+1.1\times |V_{\text{PREAMP\_OUT}}|$).
4. **Stage 4 — Attack / Release Peak Detector (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)**: Passive `1N4148` diode `D3` charges `C2` ($1\,\mu\text{F}$) through `RV2` (`ATK`, $50\text{ k}\Omega$), followed by `R9` ($1\text{ k}\Omega$) into `ENV_NODE`, discharging through `R10` ($10\text{ k}\Omega$) and `RV3` (`Release`, $1\text{ M}\Omega$).
5. **Stage 5 — Offset Summing, `OUT` & `INV_OUT` (`U1D`, `U2A`, `RV4`)**: Non-inverting `ENV_NODE` buffer on `U1D` (`+`) with a $\pm 12\text{ V}$ bias divider (`R11`, `R12` $= 10\text{ k}\Omega$, `RV4` `OFFSET` $= 100\text{ k}\Omega$, `R13`–`R15` $= 10\text{ k}\Omega$) on `U1D` (`-`), driving `J2` (`OUT`) via `R16` ($1\text{ k}\Omega$) and unity-gain inverter `U2A` (`R17` $= \text{R18} = 10\text{ k}\Omega$) driving `J3` (`INV_OUT`) via `R19` ($1\text{ k}\Omega$).
6. **Stage 6 — Pre-Biased LED Driver (`U2B`)**: Unity follower fed via `R20` ($10\text{ k}\Omega$), driving `D4` (`LED`) via `R21` ($22\text{ k}\Omega$) against a cathode bias divider (`R22` $= 10\text{ k}\Omega$ to `GND`, `R23` $= 33\text{ k}\Omega$ to `-12V`, setting a $-2.79\text{ V}$ Thévenin bias).

---

## Step 2.2: Critiquing the Analog Circuit & Fixing Hidden Flaws

Before ordering parts, ask the agent to audit the transcribed circuit for mathematical errors, loading problems, deadzones, and suboptimal component values (`EnvelopeFollowerImprovements.md`).

### AI Agent Prompt

> *"Please review `EnvelopeFollower.md`. Are there improvements that could be made to the circuit? Record the suggested improvements and explanations to `EnvelopeFollowerImprovements.md`."*

### Key Analog Engineering Findings

Switching from `1× TL074 + 1× TL072` (`6` op-amps) to **`2× TL074H`** (`8` op-amps) unifies the IC BOM onto a single line item and frees **2 op-amp sections** (`U2C`, `U2D`) to fix the input impedance and peak-detector deadband directly.

#### 1. Output Stage Excess Gain, Rail Clipping & `OFFSET` Loading (`U1D`, `RV4`, `R11`–`R15`)

In Hagiwo's original schematic, `RV4` ($100\text{ k}\Omega$) sits between `R11`/`R12` ($10\text{ k}\Omega$) and drives `U1D` (`-`) through `R13` ($10\text{ k}\Omega$) alongside `R14` ($10\text{ k}\Omega$ to `GND`) and `R15` ($10\text{ k}\Omega$ feedback). Looking back into the wiper, the divider's Thévenin source resistance $R_{\text{th}}(\alpha)$ shifts more than $3\times$ across rotation—from **$9.17\text{ k}\Omega$** at the ends ($10\text{ k}\Omega \parallel 110\text{ k}\Omega$) to **$30.00\text{ k}\Omega$** at center ($60\text{ k}\Omega \parallel 60\text{ k}\Omega$):

$$
V_{\text{U1D\_OUT}} = \left(2 + \frac{R_{15}}{R_{13} + R_{\text{th}}(\alpha)}\right) V_{\text{ENV\_NODE}} - \left(\frac{R_{15}}{R_{13} + R_{\text{th}}(\alpha)}\right) V_{\text{th}}(\alpha)
$$

- **Consequences**: `U1D` amplifies `ENV_NODE` by **$2.25\times$ (center) to $2.52\times$ (ends)** (`12%` gain shift across knob rotation), clipping `OUT` hard against the $+12\text{ V}$ rail once `ENV_NODE` exceeds just **$+4.17\text{ V}$ to $+4.67\text{ V}$** (less than half the detector's dynamic range), while heavily compressing the `OFFSET` taper near center (`±1.44 V` at 25%/75% travel out of `±5.22 V`). *(The critique also caught a reversed sign in `EnvelopeFollower.md`'s pot-rotation note: with `Pin 1 = +V` and `Pin 3 = -V`, turning `RV4` clockwise already pushes `OUT` **positive** because `U1D` inverts `OFF_WIPER`.)*
- **Fix (Remove `R14` + 10× Impedance Scaling)**: **Delete `R14`** to drop the unnecessary $2\times$ base gain floor, scale `RV4` down to **`B10k` (Linear)** with **`R11 = R12 = 1 kΩ`** (cutting wiper impedance $10\times$ to $0.92\text{ k}\Omega \le R_{\text{th}} \le 3.00\text{ k}\Omega$, spanning `±9.63 V` on protected `±11.55 V` rails), and set **`R13 = 18 kΩ`** with **`R15 = 10 kΩ`**. Envelope gain settles to **$1.476\times\text{--}1.529\times$** (just **`3.5%`** variation across rotation), headroom climbs to **`ENV_NODE ≈ +7.5 V`**, and DC offset sweeps nearly linearly across **`±5.09 V`** (`CW = +OUT`).

#### 2. Unbuffered Peak Diode `D3`, Attack Current Spike & `R9` Release Droop (`U2C`, `D3`, `RV2`, `R9`)

Hagiwo's passive peak detector suffers from three compounding flaws:

1. **`~0.65 V` Diode Deadzone**: Passive `D3` (`1N4148`) sits outside any op-amp loop, erasing low-level tails below $\approx 0.65\text{ V}$ and drifting `-2 mV/°C`.
2. **Zero-Ohm Attack Current Spike**: Dialing `RV2` (`ATK`) fully CCW (`0 Ω`) shorts `U1C` directly into `C2` (`1 µF`), slamming the op-amp into short-circuit current limiting on every transient.
3. **`9.1%` (`-0.83 dB`) Release-Dependent Amplitude Droop**: `R9` (`1 kΩ`) placed between `ENV_CAP` and `ENV_NODE` forms a voltage divider with `R10` (`10 kΩ`) + `RV3` (`1 MΩ`), dropping `ENV_NODE` to `10 / 11 = 90.9%` whenever `Release` is dialed to minimum.

- **Fix**:
  - **Active Zero-Deadzone Peak Detector (`U2C`)**: Wrap low-leakage silicon diode **`D3` (`1N4148WS`, `< 25 nA` reverse leakage)** inside `U2C`'s feedback loop (`U2C+` = `RECT_OUT`, `U2C_OUT` $\rightarrow$ `D3.A`, `D3.K` (`ATK_IN`) $\rightarrow$ `U2C-`), cutting the deadzone below **`5 mV`** without sacrificing slow-release hold time (unlike Schottky diodes, whose $\mu\text{A}$–$\text{mA}$ reverse leakage drains `C2`).
  - **Attack Surge Limiter (`R_ATK_MIN = 470 Ω`)**: Insert `470 Ω` in series with `RV2` (`A50k`), capping peak surge current at `~21 mA` while yielding $\tau_{\text{atk}} \approx 0.47\text{--}50.5\text{ ms}$ with `C2 = 1 µF`.
  - **Delete `R9` & Add `R_ENV_PROT` (`10 kΩ`)**: Connect `C2` directly to `ENV_NODE` (`0%` release droop, $\tau_{\text{rel}} = 10\text{ ms--}1.01\text{ s}$ with `R10 = 10 kΩ` + `RV3 = A1M`) and add `R_ENV_PROT` (`10 kΩ`) directly in front of `U1D+` (matching `R20 = 10 kΩ` on `U2B+`) so `C2` cannot dump charge into `U1D` during a rail brownout.

#### 3. Low Input Impedance (`9.9 kΩ`), `f_c` Error & Dedicated Input Buffer (`U2D`)

Because `R2` (`10 kΩ`) terminates at `U1A`'s virtual ground, Hagiwo's input impedance is only $Z_{\text{in}} = R_1 \parallel R_2 = 9.90\text{ k}\Omega$ ($10\times$ heavier than the `100 kΩ` Eurorack standard), which also shifts the input high-pass cutoff from the naive $0.034\text{ Hz}$ (`1 MΩ` × `4.7 µF`) up to **$3.42\text{ Hz}$**. Leaving `J1` Tip-Normal ungrounded also invites `50/60 Hz` hum when unpatched.

- **Fix**: Dedicate **`U2D`** as a unity-gain non-inverting input buffer after `R_IN_PROT` (`1 kΩ`), `C1` (`1 µF` PET film), and `R1` (`100 kΩ` to `GND`), raising input impedance to **$Z_{\text{in}} = 101\text{ k}\Omega$** with $f_c = 1.58\text{ Hz}$. Wire `J1.TN → GND` unconditionally and add **`D_IN` (`BAV99`)** rail clamps plus `R_IN_BUF` (`1 kΩ`) ahead of `U2D+`.

#### 4. In-Loop Precision LED Current Sink (`U2B`, `D4`, `D_LED_CLAMP`, `R_LED`)

The original $-2.79\text{ V}$ cathode pre-bias divider (`R22 = 10 kΩ`, `R23 = 33 kΩ`) leaves red/yellow/green LEDs glowing dimly at `0 V` silence (`23–32 µA`) while limiting `+10 V` peak current to only `~0.36 mA`.

- **Fix**: Delete `R21`, `R22`, and `R23`, and place `D4` (`3 mm` LED) **inside `U2B`'s negative-feedback loop**, with `D4.K` (`LED_K`) tied to `U2B-` and **`R_LED = 2.2 kΩ`** to `GND`. Op-amp feedback enforces $I_{\text{LED}} = V_{\text{ENV\_NODE}} / 2.2\text{ k}\Omega$ (**`0.00 mA` true dark idle**, up to **`~4.5 mA`** linear peak drive) independent of LED color or $V_f$. Place **`D_LED_CLAMP` (`1N4148WS`)** anti-parallel across `D4` (`Anode = LED_K`, `Cathode = U2B_OUT`) so negative offset/noise clamps at `-0.65 V` instead of subjecting `D4` to `-12 V` reverse breakdown.

#### 5. Rectifier Symmetry, Capacitor Dielectrics, In-Loop Output Feedback & Pot Tapers

- **`0.1%`-Matched `1.000×` Rectifier (`R3`–`R8B`, `D1_D2`)**: Because `U1C` subtracts $1/20\text{ k}\Omega$ from $1/10\text{ k}\Omega$ (`2× − 1×` cancellation), resistor errors magnify $\sim 3\times$ (`44.3%` asymmetry with 5% parts; `8.16%` even with 1% parts). Using **`7 × 10 kΩ ±0.1%` (`25 ppm/°C`)** thin-film resistors (`R4 + R5 = 20 kΩ` feedforward and `R8A + R8B = 20 kΩ` feedback, consolidating onto one reel) locks unity gain $V_{\text{RECT\_OUT}} = +1.000\,|V_{\text{PREAMP\_OUT}}|$ with **`≤ 0.80%`** worst-case half-cycle error, while swapping `D1`/`D2` to a **`BAT54S` (`D1_D2`)** dual Schottky saves `~0.35 V` of negative swing headroom at `U1B_OUT`.
- **Non-Polarized PET Film Caps (`C1`, `C2 = 1 µF 100 V`)**: Avoids Class-2 MLCC (`X7R`/`X5R`) piezoelectric microphonics and `30–60%` DC-bias capacitance loss on `C2` (`ENV_NODE`).
- **Preamp HF Roll-Off (`C_HF = 47 pF` `C0G/NP0`) & In-Loop Output Feedback (`C_OUT1`, `C_OUT2 = 100 pF` `C0G/NP0`)**: `C_HF` across `U1A` sets $f_c \ge 36.9\text{ kHz}$ against pot-wiring capacitance; taking `R15`/`R18` DC feedback from the output clamp midpoints (`OUT_CLAMP`, `INV_OUT_CLAMP`) with local `100 pF` `C0G` HF caps halves DC output impedance to `470 Ω` and achieves **`0.00%` tracking mismatch** between `OUT` and `INV_OUT`.
- **Potentiometer Tapers**: **`A100k`** (`GAIN`), **`A50k`** (`ATK`), and **`A1M`** (`Release`) Audio/Log tapers spread musical adjustment cleanly across knob rotation, while **`B10k`** (`OFFSET`) stays Linear for a centered `0 V` midpoint.

---

## Step 2.3: Adding Eurorack Hardware Protections

Next, harden the design against reverse-plugged ribbon cables, noisy digital power buses, floating/shorted inputs, broken pot wires, and output-to-output patch clashes.

### AI Agent Prompt

> *"Please review `EnvelopeFollower.md` and `EnvelopeFollowerImprovements.md`. Can you please add appropriate protections for a Eurorack circuit? Reverse-polarity protection for power supply, local decoupling caps for ICs, gain floor limiting, output protection, and unused op-amp termination. Update `EnvelopeFollowerImprovements.md`."*

### Five Production Protections

1. **Reverse-Polarity Protection & RC Bus Filtering (`J4`, `D_PWR_P`, `D_PWR_N`, `R_PWR_P`, `R_PWR_N`, `C3`, `C4`)**:
   - Use a **shrouded, keyed `2×5` (`2.54 mm`) IDC header (`J4`)** (`Pins 1–2 = -12V_IN` marked `RED STRIPE / -12V`, `Pins 3–8 = GND`, `Pins 9–10 = +12V_IN`).
   - Insert series **`B5819W` (`40 V / 1 A` Schottky, `SOD-123`)** diodes (`D_PWR_P` anode on `+12V_IN`; **`D_PWR_N` cathode on `-12V_IN`**, reversed for negative-rail current flow), followed by **`10 Ω` `250 mW` (`1206`)** damping resistors (`R_PWR_P`, `R_PWR_N`) into **`22 µF` `50 V`** SMD electrolytic bulk caps (`C3`, `C4` — **`C4` `+` on `GND`**, `4.2×` voltage derating). At `~15 mA` nominal draw, internal rails sit at **`≈ ±11.55 V`** while the `10 Ω / 22 µF` RC filter rolls off bus switching noise above **`723 Hz`** and damps hot-plug inrush.
2. **Local IC Decoupling (`C_DEC1`–`C_DEC4` = `100 nF` `50 V` `X7R` `0603`)**:
   - Placed within **`< 3–5 mm`** of `U1` and `U2` supply pins (`Pin 4` $+12\text{ V}$, `Pin 11` $-12\text{ V}$) with direct low-inductance vias to `GND` to prevent high-frequency oscillation and rail bounce during fast rectifier/peak switching.
3. **Gain-Floor Limiting & Open-Wiper Fail-Safe (`R_GAIN_MIN`, `R_GAIN_FAIL`, `C_HF`)**:
   - Place **`R_GAIN_MIN = 1 kΩ`** in series with `RV1` (`A100k`) so minimum gain stops at **`-0.10×` (`-20 dB`)** instead of shorting `U1A_OUT` to `U1A_INV` at `0 Ω`.
   - Place **`R_GAIN_FAIL = 1 MΩ`** directly on the PCB in parallel with `R_GAIN_MIN + RV1` alongside `C_HF` (`47 pF` `C0G`): normal gain spans **`-0.10×` to `-9.17×` (`+19.25 dB`)**, while a broken panel-pot wire stays bounded at `-100×` instead of slamming `U1A` open-loop.
4. **Output Short-Circuit, Rail-Clash & ESD Clamping (`R16A/B`, `R19A/B`, `D_OUT`, `D_INV_OUT`)**:
   - Replace single `1 kΩ` output resistors with split **`470 Ω + 470 Ω` `0.5 W` (`1210`)** clash-rated resistors (`R16A`/`R16B` on `OUT`, `R19A`/`R19B` on `INV_OUT`). During a continuous `22.5 V` opposite-rail output-to-output clash (`23.9 mA`), each resistor dissipates `0.269 W` (`1.86×` continuous margin inside `0.5 W`).
   - Connect **`BAV99` (`SOT-23`)** dual series switching diodes (`D_OUT` on `OUT_CLAMP`, `D_INV_OUT` on `INV_OUT_CLAMP`, plus `D_IN` on `IN_AC`) with `Pin 1 = -12V`, `Pin 2 = +12V`, and `Pin 3 = COM` so external ESD strikes and `> ±12 V` transients are current-limited by `R16B`/`R19B` and shunted cleanly into the bypassed rails. Leave output jack normal pins (`J2.TN`, `J3.TN`) **`NC`**.
5. **Op-Amp Channel Utilization & Unused Termination (`U2C`, `U2D`)**:
   - Never leave spare op-amp inputs floating or tied in open loop. In this improved build, **all 8 channels** across `2× TL074H` are actively used (`U2C` active peak detector, `U2D` `100 kΩ` input buffer); any build leaving spare sections must wire them as unity-gain followers referenced to `GND` (`+` to `GND`, `-` tied to `OUT`).

---

## Step 2.4: Optional Feature Exploration — What Else Can Antigravity Suggest?

When you ask an open-ended circuit review prompt like Step 2.2 (*"Are there improvements that could be made to the circuit?"*), Antigravity does not stop at fixing analog bugs—it also proposes **optional musical and functional enhancements** tailored to a Eurorack modular environment.

For example, while generating `EnvelopeFollowerImprovements.md`, the agent noted that input capacitor `C1` blocks sub-audio control voltages and suggested adding a panel-mounted **AC / DC Input Coupling Switch (`SW1`)** in parallel across `C1` (as well as an optional Gate/Trigger threshold comparator, input pad switch, and center-detent `OFFSET` pot). When asked to elaborate on the `AC / DC` switch idea, Antigravity generated a complete engineering feasibility analysis showing how a single SPST toggle switch converts the module into a **DC-coupled precision full-wave CV rectifier ($2\times$ LFO frequency doubler), asymmetric unipolar slew limiter / Gate-to-AR envelope generator, and dual-output polarizer/offset shaper**—while catching a critical design interaction with inter-stage AC coupling and op-amp input offset voltage ($V_{\text{os}}$).

!!! tip "Explore the Optional DC-Coupled CV & Slew Direction"
    We keep the main tutorial flow ([Stage 3](stage-3-bom-and-dfm.md) through [Stage 7](stage-7-manufacturing.md)) focused on the core 8-control envelope follower (`4` pots, `3` jacks, `1` LED) so the baseline 6 HP layout stays simple. If you want to see the full engineering analysis Antigravity generated—or incorporate `SW1` into your own build—read **[Optional Direction: DC-Coupled CV / LFO Slew & Precision Rectification Mode](optional-dc-coupled-mode.md)**.
